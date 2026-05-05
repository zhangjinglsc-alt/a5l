#!/usr/bin/env python3
"""
US_SIM_001 美股实时监控系统 - 持续运行版
后台持续监控美股持仓和关注股票
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from finnhub_websocket import FinnhubWebSocketClient
from datetime import datetime
import json
import time


class USSim001PersistentMonitor:
    """US_SIM_001 持续实时监控系统"""
    
    def __init__(self):
        self.ws_client = FinnhubWebSocketClient()
        self.portfolio = {
            'NVDA': {'shares': 100, 'cost': 945.00},
        }
        self.watchlist = ['AAPL', 'TSLA', 'AVGO', 'MRVL']
        self.price_history = {}
        self.alerts = []
        self.running = False
        
    def start(self):
        """启动持续监控"""
        print("="*70)
        print("🇺🇸 US_SIM_001 美股实时监控系统 - 持续运行版")
        print("="*70)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 显示持仓
        print("📊 当前持仓:")
        for symbol, data in self.portfolio.items():
            print(f"   {symbol}: {data['shares']}股 @ ${data['cost']:.2f}")
        print()
        
        # 添加价格回调
        self.ws_client.add_price_callback(self._price_handler)
        
        # 连接WebSocket
        self.ws_client.connect()
        time.sleep(3)
        
        # 订阅所有股票
        all_symbols = list(self.portfolio.keys()) + self.watchlist
        for symbol in all_symbols:
            self.ws_client.subscribe(symbol)
            time.sleep(0.3)
        
        print()
        print("✅ 实时监控已启动！将持续运行...")
        print("   按 Ctrl+C 停止")
        print()
        
        self.running = True
        
        try:
            # 持续运行，每分钟打印一次摘要
            counter = 0
            while self.running:
                time.sleep(1)
                counter += 1
                
                # 每60秒打印持仓摘要
                if counter % 60 == 0:
                    self._print_summary()
                    
        except KeyboardInterrupt:
            print("\n   用户停止监控")
        finally:
            self.stop()
    
    def _price_handler(self, symbol, price):
        """价格变动处理"""
        # 保存历史
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append({
            'time': datetime.now().isoformat(),
            'price': price
        })
        
        # 限制历史记录
        if len(self.price_history[symbol]) > 50:
            self.price_history[symbol] = self.price_history[symbol][-50:]
        
        # 持仓股显示盈亏
        if symbol in self.portfolio:
            self._show_position(symbol, price)
    
    def _show_position(self, symbol, price):
        """显示持仓状况"""
        position = self.portfolio[symbol]
        shares = position['shares']
        cost = position['cost']
        
        pnl = (price - cost) * shares
        pnl_pct = ((price - cost) / cost) * 100
        
        emoji = "🟢" if pnl > 0 else "🔴"
        status = "盈利" if pnl > 0 else "亏损"
        
        print(f"   {emoji} [{datetime.now().strftime('%H:%M:%S')}] {symbol}: ${price:.2f} | "
              f"{status}: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
        
        # 检查预警
        self._check_alerts(symbol, price, pnl_pct)
    
    def _check_alerts(self, symbol, price, pnl_pct):
        """检查预警"""
        # 止损 -8%
        if pnl_pct <= -8 and f"{symbol}_stop_loss" not in self.alerts:
            self.alerts.append(f"{symbol}_stop_loss")
            print(f"   ⚠️  🚨 {symbol} 触发止损! 亏损 {pnl_pct:.2f}%")
        
        # 止盈 +15%
        elif pnl_pct >= 15 and f"{symbol}_take_profit" not in self.alerts:
            self.alerts.append(f"{symbol}_take_profit")
            print(f"   🎯 🎉 {symbol} 触发止盈! 盈利 {pnl_pct:.2f}%")
    
    def _print_summary(self):
        """打印持仓摘要"""
        print()
        print("="*70)
        print(f"📊 US_SIM_001 持仓摘要 [{datetime.now().strftime('%H:%M:%S')}]")
        print("="*70)
        
        total_pnl = 0
        total_value = 0
        
        for symbol, data in self.portfolio.items():
            current_price = self.ws_client.get_last_price(symbol)
            if current_price:
                shares = data['shares']
                cost = data['cost']
                pnl = (current_price - cost) * shares
                value = current_price * shares
                pnl_pct = ((current_price - cost) / cost) * 100
                
                emoji = "🟢" if pnl > 0 else "🔴"
                print(f"   {emoji} {symbol}: {shares}股 @ ${current_price:.2f} | "
                      f"盈亏: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
                
                total_pnl += pnl
                total_value += value
        
        print()
        print(f"   💰 总持仓价值: ${total_value:,.2f}")
        print(f"   📈 总盈亏: ${total_pnl:,.2f}")
        print("="*70)
        print()
    
    def stop(self):
        """停止监控"""
        print()
        print("🛑 停止US_SIM_001实时监控...")
        self.running = False
        self.ws_client.disconnect()
        
        # 保存价格历史
        history_file = f"/workspace/projects/workspace/data/simulation/US_SIM_001_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.price_history, f, indent=2)
            print(f"   价格历史已保存: {history_file}")
        except:
            pass
        
        print("✅ 监控已停止")


if __name__ == '__main__':
    monitor = USSim001PersistentMonitor()
    monitor.start()
