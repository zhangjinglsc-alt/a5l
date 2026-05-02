#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美股模拟交易初始化演示
"""

import sys
sys.path.insert(0, '/workspace/projects/workspace/TOOLS')
from us_sim_trading_engine import USSimTradingEngine

def main():
    engine = USSimTradingEngine()
    
    print("="*60)
    print("🎮 美股模拟交易系统 - 初始化演示")
    print("="*60)
    
    # 模拟几笔交易
    print("\n📊 模拟交易演示:\n")
    
    # 买入 AAPL
    result = engine.execute_buy("AAPL", 10, 180.50, "trend_following", "突破均线")
    if result['success']:
        print(f"✅ 买入 AAPL 10股 @ $180.50")
    
    # 买入 NVDA
    result = engine.execute_buy("NVDA", 5, 890.00, "momentum", "AI芯片强势")
    if result['success']:
        print(f"✅ 买入 NVDA 5股 @ $890.00")
    
    # 买入 TSLA
    result = engine.execute_buy("TSLA", 8, 175.30, "breakout", "放量突破")
    if result['success']:
        print(f"✅ 买入 TSLA 8股 @ $175.30")
    
    print("\n" + "="*60)
    print("📊 交易后账户状态")
    print("="*60)
    
    account = engine.get_account_summary()
    print(f"\n💰 账户概况")
    print(f"   初始资金: ${account['初始资金']:,.2f}")
    print(f"   当前总资产: ${account['总资产']:,.2f}")
    print(f"   可用资金: ${account['可用资金']:,.2f}")
    
    positions = engine.positions['positions']
    print(f"\n📈 当前持仓 ({len(positions)}只)")
    for pos in positions:
        print(f"   {pos['symbol']}: {pos['quantity']}股 | 成本: ${pos['avg_cost']:.2f} | 市值: ${pos['market_value']:,.2f}")
    
    trades = engine.get_trade_stats()
    print(f"\n📊 交易统计")
    print(f"   总交易: {trades['total_trades']}笔")
    print(f"   累计盈亏: ${trades['total_pnl']:+,.2f}")
    
    print("\n" + "="*60)
    print("✅ 演示完成！系统已就绪")
    print("="*60)

if __name__ == "__main__":
    main()
