#!/usr/bin/env python3
"""
Finnhub WebSocket实时数据流 - A5L美股实时监控
实时接收美股报价、交易数据
"""

import os
import sys
import json
import websocket
import threading
import time
from datetime import datetime
from typing import Callable, List, Dict

sys.path.insert(0, '/workspace/projects/workspace')

# WebSocket回调函数类型
PriceCallback = Callable[[str, float], None]
TradeCallback = Callable[[str, Dict], None]


class FinnhubWebSocketClient:
    """Finnhub WebSocket客户端 - 实时美股数据"""
    
    def __init__(self, api_key: str = None):
        """
        初始化WebSocket客户端
        
        Args:
            api_key: Finnhub API Key
        """
        self.api_key = api_key or self._load_api_key()
        self.ws = None
        self.subscribed_symbols = set()
        self.price_callbacks: List[PriceCallback] = []
        self.trade_callbacks: List[TradeCallback] = []
        self.is_connected = False
        self.last_prices: Dict[str, float] = {}
        self.reconnect_attempts = 0
        self.max_reconnect = 5
        
    def _load_api_key(self) -> str:
        """加载API Key"""
        config_path = '/workspace/projects/workspace/config/finnhub_config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get('api_key')
        return os.environ.get('FINNHUB_API_KEY')
    
    def on_message(self, ws, message):
        """处理收到的消息"""
        try:
            data = json.loads(message)
            
            # 处理交易数据
            if 'data' in data:
                for item in data['data']:
                    symbol = item.get('s')
                    price = item.get('p')
                    timestamp = item.get('t')
                    volume = item.get('v')
                    
                    if symbol and price:
                        # 更新最新价格
                        self.last_prices[symbol] = price
                        
                        # 触发回调
                        for callback in self.price_callbacks:
                            try:
                                callback(symbol, price)
                            except Exception as e:
                                print(f"   价格回调错误: {e}")
                        
                        for callback in self.trade_callbacks:
                            try:
                                callback(symbol, item)
                            except Exception as e:
                                print(f"   交易回调错误: {e}")
                        
                        # 打印实时数据 (调试用)
                        # print(f"   [{datetime.now().strftime('%H:%M:%S')}] {symbol}: ${price:.2f}")
            
            # 处理心跳
            elif 'type' in data and data['type'] == 'ping':
                ws.send(json.dumps({'type': 'pong'}))
                
        except Exception as e:
            print(f"   消息处理错误: {e}")
    
    def on_error(self, ws, error):
        """处理错误"""
        print(f"❌ WebSocket错误: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """连接关闭"""
        print(f"⚠️ WebSocket连接关闭: {close_status_code} - {close_msg}")
        self.is_connected = False
        
        # 自动重连
        if self.reconnect_attempts < self.max_reconnect:
            self.reconnect_attempts += 1
            print(f"   {5}秒后尝试重连 ({self.reconnect_attempts}/{self.max_reconnect})...")
            time.sleep(5)
            self.connect()
    
    def on_open(self, ws):
        """连接建立"""
        print("✅ WebSocket连接成功！")
        self.is_connected = True
        self.reconnect_attempts = 0
        
        # 重新订阅之前的股票
        for symbol in self.subscribed_symbols:
            self.subscribe(symbol)
    
    def connect(self):
        """建立WebSocket连接"""
        ws_url = f"wss://ws.finnhub.io?token={self.api_key}"
        
        print(f"🔗 连接Finnhub WebSocket...")
        
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # 在后台线程运行
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
    
    def subscribe(self, symbol: str):
        """
        订阅股票实时数据
        
        Args:
            symbol: 股票代码 (如 'AAPL', 'NVDA')
        """
        symbol = symbol.upper()
        self.subscribed_symbols.add(symbol)
        
        if self.is_connected and self.ws:
            self.ws.send(json.dumps({'type': 'subscribe', 'symbol': symbol}))
            print(f"   📈 已订阅: {symbol}")
        else:
            print(f"   ⏳ 等待连接后订阅: {symbol}")
    
    def unsubscribe(self, symbol: str):
        """取消订阅"""
        symbol = symbol.upper()
        self.subscribed_symbols.discard(symbol)
        
        if self.is_connected and self.ws:
            self.ws.send(json.dumps({'type': 'unsubscribe', 'symbol': symbol}))
            print(f"   📉 已取消订阅: {symbol}")
    
    def add_price_callback(self, callback: PriceCallback):
        """添加价格回调函数"""
        self.price_callbacks.append(callback)
    
    def add_trade_callback(self, callback: TradeCallback):
        """添加交易回调函数"""
        self.trade_callbacks.append(callback)
    
    def get_last_price(self, symbol: str) -> float:
        """获取最新价格"""
        return self.last_prices.get(symbol.upper())
    
    def disconnect(self):
        """断开连接"""
        if self.ws:
            self.ws.close()
        self.is_connected = False
        print("✅ WebSocket连接已断开")
    
    def is_running(self) -> bool:
        """检查是否运行中"""
        return self.is_connected


# ==================== 快捷使用方式 ====================

_ws_client = None

def get_ws_client() -> FinnhubWebSocketClient:
    """获取WebSocket客户端实例 (单例)"""
    global _ws_client
    if _ws_client is None:
        _ws_client = FinnhubWebSocketClient()
    return _ws_client


def start_realtime_monitor(symbols: List[str], price_handler: Callable = None):
    """
    启动实时监控
    
    Args:
        symbols: 要监控的股票列表
        price_handler: 价格变化处理函数
    """
    client = get_ws_client()
    
    # 添加默认的价格处理
    if price_handler:
        client.add_price_callback(price_handler)
    else:
        def default_handler(symbol, price):
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] {symbol}: ${price:.2f}")
        client.add_price_callback(default_handler)
    
    # 连接并订阅
    client.connect()
    
    # 等待连接建立
    time.sleep(2)
    
    # 订阅股票
    for symbol in symbols:
        client.subscribe(symbol)
    
    return client


def monitor_us_portfolio(portfolio: Dict[str, float]):
    """
    监控美股持仓组合
    
    Args:
        portfolio: 持仓字典 {symbol: shares}
    """
    symbols = list(portfolio.keys())
    
    def portfolio_handler(symbol, price):
        shares = portfolio.get(symbol, 0)
        value = price * shares
        print(f"   💼 {symbol}: ${price:.2f} × {shares} = ${value:,.2f}")
    
    return start_realtime_monitor(symbols, portfolio_handler)


# ==================== 测试 ====================

if __name__ == '__main__':
    print("="*70)
    print("🚀 Finnhub WebSocket实时数据流测试")
    print("="*70)
    
    # 测试1: 连接并订阅
    print("\n测试1: 连接并订阅NVDA/AAPL")
    client = FinnhubWebSocketClient()
    
    # 添加价格回调
    def my_handler(symbol, price):
        print(f"   💰 [{datetime.now().strftime('%H:%M:%S')}] {symbol}: ${price:.2f}")
    
    client.add_price_callback(my_handler)
    
    # 连接
    client.connect()
    
    # 等待连接
    time.sleep(3)
    
    # 订阅股票
    client.subscribe('NVDA')
    client.subscribe('AAPL')
    client.subscribe('TSLA')
    
    print("\n   实时监控中... (按Ctrl+C停止)")
    
    try:
        # 运行30秒
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n   用户停止")
    
    # 断开连接
    client.disconnect()
    
    print("\n✅ 测试完成！")
