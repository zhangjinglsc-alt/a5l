#!/usr/bin/env python3
"""
US_SIM_001 美股实时监控系统 v3.0
- WebSocket实时监控 (零API消耗)
- WebSocket超时后秒级Finnhub REST API回退
- 每15分钟持久化到交易计划文档
- 多层级互为保障

Chief配置: 15分钟更新 + WebSocket实时监控 + 秒级Finnhub回退
"""

import sys
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional

sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from finnhub_websocket import FinnhubWebSocketClient
from unified_data_source_manager import UnifiedDataSourceManager


class USSim001HybridMonitor:
    """
    US_SIM_001 混合监控模式
    
    监控策略:
    1. WebSocket实时流 (主数据源，零API消耗，毫秒级延迟)
    2. WebSocket超时 → 秒级Finnhub REST API回退 (1秒间隔)
    3. 所有API失效 → 本地缓存兜底
    4. 每15分钟持久化到交易计划文档
    """
    
    # 配置参数
    WEBSOCKET_TIMEOUT = 10  # WebSocket超时时间(秒)
    FINNHUB_POLL_INTERVAL = 1  # Finnhub轮询间隔(秒)
    PERSIST_INTERVAL = 15 * 60  # 持久化间隔(15分钟)
    ALERT_CHECK_INTERVAL = 5  # 预警检查间隔(秒)
    
    def __init__(self):
        # WebSocket客户端
        self.ws_client = FinnhubWebSocketClient()
        self.ws_connected = False
        self.ws_last_data_time = None
        
        # REST API数据源 (WebSocket超时后使用)
        self.data_manager = UnifiedDataSourceManager(enable_cache=True)
        
        # 当前价格缓存
        self.current_prices = {}
        self.price_last_update = {}
        
        # 从配置文件加载持仓
        self.portfolio = self._load_portfolio()
        self.watchlist = ['AAPL', 'TSLA', 'AVGO', 'MRVL', 'MSFT', 'GOOGL']
        
        # 预警记录
        self.alerts_triggered = set()
        
        # 运行状态
        self.running = False
        self.monitor_mode = 'websocket'  # websocket / finnhub / cache
        
    def _load_portfolio(self) -> Dict:
        """从配置文件加载持仓"""
        config_file = '/workspace/projects/workspace/data/simulation/US_SIM_001.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config.get('positions', {})
        
        # 默认持仓
        return {
            'NVDA': {'quantity': 100, 'cost_basis': 198.48},
            'INTC': {'quantity': 92, 'cost_basis': 108.64},
            'WDC': {'quantity': 10, 'cost_basis': 473.80},
            'AMD': {'quantity': 50, 'cost_basis': 142.12}
        }
    
    def _save_portfolio(self):
        """保存当前价格到配置文件"""
        config_file = '/workspace/projects/workspace/data/simulation/US_SIM_001.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # 更新当前价格
            for symbol, pos in config.get('positions', {}).items():
                if symbol in self.current_prices:
                    pos['current_price'] = self.current_prices[symbol]
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
    
    def start(self):
        """启动混合监控"""
        print("="*70)
        print("🇺🇸 US_SIM_001 美股实时监控系统 v3.0")
        print("="*70)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("📊 监控模式:")
        print("   1️⃣ WebSocket实时流 (主)")
        print("   2️⃣ WebSocket超时 → Finnhub REST API (1秒级)")
        print("   3️⃣ 所有API失效 → 本地缓存兜底")
        print("   4️⃣ 每15分钟持久化到交易计划文档")
        print()
        
        # 显示持仓
        print("📊 当前持仓:")
        for symbol, data in self.portfolio.items():
            print(f"   {symbol}: {data['quantity']}股 @ ${data['cost_basis']:.2f}")
        print()
        
        # 启动WebSocket
        self._start_websocket()
        
        # 启动监控线程
        self.running = True
        threads = [
            threading.Thread(target=self._websocket_health_monitor, name="WS-Monitor"),
            threading.Thread(target=self._finnhub_fallback_monitor, name="Finnhub-Fallback"),
            threading.Thread(target=self._alert_monitor, name="Alert-Monitor"),
            threading.Thread(target=self._persist_monitor, name="Persist-Monitor"),
        ]
        
        for t in threads:
            t.daemon = True
            t.start()
        
        print("✅ 混合监控系统已启动！")
        print("   按 Ctrl+C 停止")
        print()
        
        # 主循环
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n   用户停止监控")
        finally:
            self.stop()
    
    def _start_websocket(self):
        """启动WebSocket连接"""
        try:
            # 添加价格回调
            self.ws_client.add_price_callback(self._ws_price_handler)
            
            # 连接WebSocket
            self.ws_client.connect()
            time.sleep(3)
            
            # 订阅所有股票
            all_symbols = list(self.portfolio.keys()) + self.watchlist
            for symbol in all_symbols:
                self.ws_client.subscribe(symbol)
                time.sleep(0.3)
            
            self.ws_connected = True
            self.ws_last_data_time = datetime.now()
            self.monitor_mode = 'websocket'
            print("   🟢 WebSocket连接成功")
            
        except Exception as e:
            print(f"   🔴 WebSocket连接失败: {e}")
            self.ws_connected = False
            self.monitor_mode = 'finnhub'
    
    def _ws_price_handler(self, symbol, price):
        """WebSocket价格回调"""
        self.current_prices[symbol] = price
        self.price_last_update[symbol] = datetime.now()
        self.ws_last_data_time = datetime.now()
        
        # 持仓股显示盈亏
        if symbol in self.portfolio:
            self._show_position_update(symbol, price, 'WebSocket')
    
    def _websocket_health_monitor(self):
        """WebSocket健康监控线程"""
        while self.running:
            time.sleep(5)  # 每5秒检查一次
            
            if not self.ws_connected:
                continue
            
            # 检查WebSocket是否超时
            if self.ws_last_data_time:
                elapsed = (datetime.now() - self.ws_last_data_time).total_seconds()
                
                if elapsed > self.WEBSOCKET_TIMEOUT:
                    if self.monitor_mode == 'websocket':
                        print(f"\n   ⚠️ WebSocket超时 ({elapsed:.0f}秒)，切换到Finnhub REST API...")
                        self.monitor_mode = 'finnhub'
    
    def _finnhub_fallback_monitor(self):
        """Finnhub REST API回退监控线程 (秒级)"""
        while self.running:
            try:
                # 仅在WebSocket模式下休眠
                if self.monitor_mode == 'websocket':
                    time.sleep(1)
                    continue
                
                # 获取所有需要监控的股票
                all_symbols = list(self.portfolio.keys()) + self.watchlist
                
                for symbol in all_symbols:
                    if not self.running:
                        break
                    
                    try:
                        # 使用统一数据源管理器 (优先Finnhub，自动限流)
                        price_data = self.data_manager.get_price(symbol)
                        
                        if price_data and price_data.current > 0:
                            price = price_data.current
                            source = price_data.source
                            
                            # 更新价格
                            self.current_prices[symbol] = price
                            self.price_last_update[symbol] = datetime.now()
                            
                            # 持仓股显示
                            if symbol in self.portfolio:
                                cached = "(缓存)" if price_data.is_cached else ""
                                self._show_position_update(symbol, price, f'{source}{cached}')
                        
                    except Exception as e:
                        print(f"      ❌ {symbol}: 获取失败 - {e}")
                    
                    # 秒级间隔 (1秒)
                    time.sleep(self.FINNHUB_POLL_INTERVAL)
                
                # 检查WebSocket是否恢复
                if self.monitor_mode == 'finnhub' and self.ws_connected:
                    if self.ws_last_data_time:
                        elapsed = (datetime.now() - self.ws_last_data_time).total_seconds()
                        if elapsed < 5:  # WebSocket恢复
                            print(f"\n   🟢 WebSocket恢复，切换回实时流...")
                            self.monitor_mode = 'websocket'
                
            except Exception as e:
                print(f"   ⚠️ Finnhub监控异常: {e}")
                time.sleep(5)
    
    def _alert_monitor(self):
        """预警监控线程"""
        while self.running:
            try:
                # 检查持仓预警
                for symbol, pos in self.portfolio.items():
                    if symbol in self.current_prices:
                        price = self.current_prices[symbol]
                        cost = pos['cost_basis']
                        pnl_pct = ((price - cost) / cost) * 100
                        
                        self._check_alerts(symbol, price, pnl_pct)
                
                time.sleep(self.ALERT_CHECK_INTERVAL)
                
            except Exception as e:
                print(f"   ⚠️ 预警监控异常: {e}")
                time.sleep(5)
    
    def _persist_monitor(self):
        """持久化监控线程 (每15分钟)"""
        last_persist = datetime.now()
        
        while self.running:
            try:
                elapsed = (datetime.now() - last_persist).total_seconds()
                
                if elapsed >= self.PERSIST_INTERVAL:
                    print(f"\n   💾 执行15分钟数据持久化...")
                    self._persist_to_trading_plan()
                    self._save_portfolio()
                    last_persist = datetime.now()
                    print(f"   ✅ 持久化完成，下次: {(last_persist + timedelta(seconds=self.PERSIST_INTERVAL)).strftime('%H:%M:%S')}")
                
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                print(f"   ⚠️ 持久化异常: {e}")
                time.sleep(60)
    
    def _show_position_update(self, symbol: str, price: float, source: str):
        """显示持仓更新"""
        if symbol not in self.portfolio:
            return
        
        pos = self.portfolio[symbol]
        shares = pos['quantity']
        cost = pos['cost_basis']
        
        pnl = (price - cost) * shares
        pnl_pct = ((price - cost) / cost) * 100
        
        emoji = "🟢" if pnl > 0 else "🔴"
        now = datetime.now().strftime('%H:%M:%S')
        
        print(f"   {emoji} [{now}] {symbol}: ${price:.2f} | "
              f"盈亏: ${pnl:,.2f} ({pnl_pct:+.2f}%) | 来源: {source}")
    
    def _check_alerts(self, symbol: str, price: float, pnl_pct: float):
        """检查预警"""
        # 止损 -8%
        if pnl_pct <= -8:
            alert_key = f"{symbol}_stop_loss"
            if alert_key not in self.alerts_triggered:
                self.alerts_triggered.add(alert_key)
                print(f"\n   🚨🚨🚨 {symbol} 触发止损! 亏损 {pnl_pct:.2f}% 🚨🚨🚨")
                print(f"        建议立即平仓!")
        
        # 止盈 +15%
        elif pnl_pct >= 15:
            alert_key = f"{symbol}_take_profit"
            if alert_key not in self.alerts_triggered:
                self.alerts_triggered.add(alert_key)
                print(f"\n   🎉🎉🎉 {symbol} 触发止盈! 盈利 {pnl_pct:.2f}% 🎉🎉🎉")
                print(f"        建议考虑减仓或平仓!")
    
    def _persist_to_trading_plan(self):
        """持久化到交易计划文档"""
        try:
            # 调用更新脚本
            import subprocess
            result = subprocess.run(
                ['python3', '/workspace/projects/workspace/data/simulation/update_trading_plan_docs.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("   ✅ 交易计划文档已更新")
            else:
                print(f"   ⚠️ 交易计划文档更新: {result.stderr}")
        except Exception as e:
            print(f"   ⚠️ 持久化失败: {e}")
    
    def print_summary(self):
        """打印持仓摘要"""
        print("\n" + "="*70)
        print(f"📊 US_SIM_001 持仓摘要 [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"   监控模式: {self.monitor_mode.upper()}")
        print("="*70)
        
        total_pnl = 0
        total_value = 0
        total_cost = 0
        
        for symbol, pos in self.portfolio.items():
            current_price = self.current_prices.get(symbol, pos.get('current_price', pos['cost_basis']))
            shares = pos['quantity']
            cost = pos['cost_basis']
            
            pnl = (current_price - cost) * shares
            value = current_price * shares
            cost_value = cost * shares
            pnl_pct = ((current_price - cost) / cost) * 100
            
            total_pnl += pnl
            total_value += value
            total_cost += cost_value
            
            emoji = "🟢" if pnl > 0 else "🔴"
            print(f"   {emoji} {symbol}: {shares}股 @ ${current_price:.2f} | "
                  f"盈亏: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
        
        total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
        emoji_total = "🟢" if total_pnl > 0 else "🔴"
        print("-"*70)
        print(f"   {emoji_total} 总计: 市值 ${total_value:,.2f} | "
              f"盈亏: ${total_pnl:,.2f} ({total_pnl_pct:+.2f}%)")
        print("="*70)
    
    def stop(self):
        """停止监控"""
        self.running = False
        if self.ws_client:
            self.ws_client.disconnect()
        print("\n   ✅ 监控系统已停止")


import json

if __name__ == '__main__':
    monitor = USSim001HybridMonitor()
    monitor.start()
