#!/usr/bin/env python3
"""
US_SIM_001 美股实时监控系统
实时监控美股持仓和关注股票
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from finnhub_websocket import FinnhubWebSocketClient
from datetime import datetime
import json
import time


class USSim001Monitor:
    """US_SIM_001 实时监控系统"""
    
    def __init__(self):
        self.ws_client = FinnhubWebSocketClient()
        self.portfolio = {
            'NVDA': {'shares': 100, 'cost': 945.00},  # 当前持仓
        }
        self.watchlist = ['AAPL', 'TSLA', 'AVGO', 'MRVL']  # 关注列表
        self.price_history = {}
        self.alerts = []
        
    def start_monitoring(self):
        """启动实时监控"""
        print("="*70)
        print("🇺🇸 US_SIM_001 美股实时监控系统启动")
        print("="*70)
        print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 显示持仓
        print("📊 当前持仓:")
        for symbol, data in self.portfolio.items():
            print(f"   {symbol}: {data['shares']}股 @ ${data['cost']:.2f}")
        print()
        
        # 显示关注列表
        print("👀 关注列表:")
        print(f"   {', '.join(self.watchlist)}")
        print()
        
        # 添加价格回调
        self.ws_client.add_price_callback(self._price_handler)
        
        # 连接WebSocket
        self.ws_client.connect()
        
        # 等待连接
        time.sleep(3)
        
        # 订阅所有股票
        all_symbols = list(self.portfolio.keys()) + self.watchlist
        for symbol in all_symbols:
            self.ws_client.subscribe(symbol)
            time.sleep(0.5)  # 避免过快订阅
        
        print()
        print("✅ 实时监控已启动！")
        print("   📈 价格变动将实时显示")
        print("   💰 持仓盈亏自动计算")
        print("   🔔 止损止盈自动提醒")
        print()
        
    def _price_handler(self, symbol, price):
        """价格变动处理"""
        # 保存历史价格
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append({
            'time': datetime.now().isoformat(),
            'price': price
        })
        
        # 限制历史记录长度
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
        
        # 检查是否是持仓股
        if symbol in self.portfolio:
            self._check_position(symbol, price)
        else:
            # 只显示价格
            print(f"   👀 [{datetime.now().strftime('%H:%M:%S')}] {symbol}: ${price:.2f}")
    
    def _check_position(self, symbol, price):
        """检查持仓状况"""
        position = self.portfolio[symbol]
        shares = position['shares']
        cost = position['cost']
        
        # 计算盈亏
        pnl = (price - cost) * shares
        pnl_pct = ((price - cost) / cost) * 100
        
        # 确定颜色标记
        if pnl > 0:
            emoji = "🟢"
            status = "盈利"
        elif pnl < 0:
            emoji = "🔴"
            status = "亏损"
        else:
            emoji = "⚪"
            status = "持平"
        
        # 打印持仓状态
        print(f"   {emoji} [{datetime.now().strftime('%H:%M:%S')}] {symbol}: ${price:.2f} | "
              f"成本: ${cost:.2f} | {status}: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
        
        # 检查止损止盈
        self._check_alerts(symbol, price, pnl_pct)
    
    def _check_alerts(self, symbol, price, pnl_pct):
        """检查预警条件"""
        # 止损 -8%
        if pnl_pct <= -8:
            if f"{symbol}_stop_loss" not in self.alerts:
                self.alerts.append(f"{symbol}_stop_loss")
                print(f"   ⚠️  🚨 {symbol} 触发止损! 亏损 {pnl_pct:.2f}%")
        
        # 止盈 +15%
        elif pnl_pct >= 15:
            if f"{symbol}_take_profit" not in self.alerts:
                self.alerts.append(f"{symbol}_take_profit")
                print(f"   🎯 🎉 {symbol} 触发止盈! 盈利 {pnl_pct:.2f}%")
        
        # 警告 -5%
        elif pnl_pct <= -5:
            if f"{symbol}_warning" not in self.alerts:
                self.alerts.append(f"{symbol}_warning")
                print(f"   ⚠️  {symbol} 亏损超5%，请注意风险")
    
    def get_portfolio_summary(self):
        """获取持仓摘要"""
        summary = {
            'positions': {},
            'total_pnl': 0,
            'total_value': 0
        }
        
        for symbol, data in self.portfolio.items():
            current_price = self.ws_client.get_last_price(symbol)
            if current_price:
                shares = data['shares']
                cost = data['cost']
                pnl = (current_price - cost) * shares
                value = current_price * shares
                
                summary['positions'][symbol] = {
                    'shares': shares,
                    'cost': cost,
                    'current_price': current_price,
                    'pnl': pnl,
                    'value': value
                }
                
                summary['total_pnl'] += pnl
                summary['total_value'] += value
        
        return summary
    
    def print_summary(self):
        """打印持仓摘要"""
        summary = self.get_portfolio_summary()
        
        print()
        print("="*70)
        print("📊 US_SIM_001 持仓摘要")
        print("="*70)
        
        for symbol, data in summary['positions'].items():
            pnl_pct = ((data['current_price'] - data['cost']) / data['cost']) * 100
            emoji = "🟢" if data['pnl'] > 0 else "🔴" if data['pnl'] < 0 else "⚪"
            
            print(f"   {emoji} {symbol}: {data['shares']}股 | "
                  f"现价: ${data['current_price']:.2f} | "
                  f"成本: ${data['cost']:.2f} | "
                  f"盈亏: ${data['pnl']:,.2f} ({pnl_pct:+.2f}%)")
        
        print()
        print(f"   💰 总持仓价值: ${summary['total_value']:,.2f}")
        print(f"   📈 总盈亏: ${summary['total_pnl']:,.2f}")
        print("="*70)
    
    def run_forever(self):
        """持续运行"""
        try:
            print()
            print("   实时监控运行中... (按Ctrl+C停止)")
            print()
            
            # 每分钟打印一次摘要
            counter = 0
            while True:
                time.sleep(1)
                counter += 1
                
                # 每60秒打印持仓摘要
                if counter % 60 == 0:
                    self.print_summary()
                    
        except KeyboardInterrupt:
            print("\n   用户停止监控")
        finally:
            self.stop()
    
    def stop(self):
        """停止监控"""
        print()
        print("🛑 停止US_SIM_001实时监控...")
        self.ws_client.disconnect()
        
        # 保存价格历史
        history_file = f"/workspace/projects/workspace/data/simulation/US_SIM_001_price_history_{datetime.now().strftime('%Y%m%d')}.json"
        with open(history_file, 'w') as f:
            json.dump(self.price_history, f, indent=2)
        print(f"   价格历史已保存: {history_file}")
        
        print("✅ 监控已停止")


def start_us_sim_monitor():
    """快捷启动US_SIM_001监控"""
    monitor = USSim001Monitor()
    monitor.start_monitoring()
    monitor.run_forever()


if __name__ == '__main__':
    print("="*70)
    print("🇺🇸 US_SIM_001 美股实时监控系统")
    print("="*70)
    print()
    
    monitor = USSim001Monitor()
    monitor.start_monitoring()
    
    # 运行监控 (可以改为run_forever()持续运行)
    print()
    print("   监控运行中... 将持续接收实时数据")
    print("   (本演示运行60秒后自动停止)")
    
    try:
        # 运行60秒
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n   用户中断")
    
    # 打印最终摘要
    monitor.print_summary()
    
    # 停止
    monitor.stop()
