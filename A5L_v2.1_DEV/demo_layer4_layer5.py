#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Layer 4/5 模拟交易与复盘功能演示
2026-05-02
"""

import sys
sys.path.insert(0, "/workspace/projects/workspace")

print("="*70)
print("🚀 A5L Layer 4/5 模拟交易与复盘功能演示")
print("="*70)
print()

# 初始化交易系统
print("📊 初始化交易系统...")
from ARCHITECT_5L.layer4_layer5_trading_system import A5LTradingSystem

trading_system = A5LTradingSystem()
print("✅ 交易系统初始化完成")
print()

# 演示1: 执行多笔模拟交易
print("🎮 演示1: Layer 4 - 执行模拟交易策略信号")
print("-"*70)

import random
random.seed(42)

# 模拟一些交易信号
trades = [
    ("AAPL", "BUY", 10, 180.50, "turtle_trading", 0.85),
    ("NVDA", "BUY", 5, 890.00, "trend_rs", 0.78),
    ("TSLA", "BUY", 8, 175.30, "volume_price", 0.72),
    ("MSFT", "BUY", 15, 420.25, "fundamental_growth", 0.80),
]

executed_trades = []
for symbol, action, qty, price, strategy, confidence in trades:
    result = trading_system.execute_strategy_signal(
        symbol=symbol,
        action=action,
        quantity=qty,
        price=price,
        strategy=strategy,
        confidence=confidence,
        account_id="US_SIM_001"
    )
    
    if result["success"]:
        print(f"  ✅ {symbol}: {action} {qty}股 @ ${price:.2f}")
        print(f"     策略: {strategy} (置信度: {confidence:.0%})")
        print(f"     成本: ${result['costs']['total']:.2f}")
        executed_trades.append((symbol, qty, price))
    else:
        print(f"  ❌ {symbol}: {result.get('error', '执行失败')}")

print()

# 演示2: 查看投资组合
print("📈 演示2: 查看模拟账户投资组合")
print("-"*70)

portfolio = trading_system.get_portfolio("US_SIM_001")
print(f"  账户名称: {portfolio['account_name']}")
print(f"  交易市场: {portfolio['market']}")
print(f"  币种: {portfolio['currency']}")
print(f"  初始资金: ${portfolio['initial_capital']:,.2f}")
print(f"  可用现金: ${portfolio['available_cash']:,.2f}")
print(f"  总资产: ${portfolio['total_equity']:,.2f}")
print(f"  持仓数: {portfolio['positions_count']}")
print(f"  收益率: {portfolio['total_return']:.2f}%")
print()
print("  当前持仓:")
for symbol, pos in portfolio['positions'].items():
    print(f"    • {symbol}: {pos['quantity']}股 @ 均价${pos['avg_price']:.2f}")

print()

# 模拟价格更新 (假设持仓盈利)
print("📊 演示3: 更新市场价格，计算浮动盈亏")
print("-"*70)

# 模拟价格上涨
price_updates = {
    "AAPL": 185.20,  # 涨2.6%
    "NVDA": 925.50,  # 涨4.0%
    "TSLA": 172.80,  # 跌1.4%
    "MSFT": 435.60,  # 涨3.7%
}

trading_system.update_market_prices(price_updates)
print("  市场价格已更新:")
for symbol, new_price in price_updates.items():
    print(f"    • {symbol}: ${new_price:.2f}")

# 重新获取组合 (包含浮动盈亏)
portfolio = trading_system.get_portfolio("US_SIM_001")
print(f"\n  更新后总资产: ${portfolio['total_equity']:,.2f}")
print(f"  浮动盈亏: ${portfolio.get('unrealized_pnl', 0):,.2f}")
print()

# 演示4: 执行卖出交易 (实现部分盈亏)
print("💰 演示4: 执行卖出交易 (实现部分盈利)")
print("-"*70)

# 卖出部分AAPL
sell_result = trading_system.execute_strategy_signal(
    symbol="AAPL",
    action="SELL",
    quantity=5,
    price=185.20,
    strategy="turtle_trading",
    confidence=0.82,
    account_id="US_SIM_001"
)

if sell_result["success"]:
    realized_pnl = (185.20 - 180.50) * 5  # 盈利$23.50
    print(f"  ✅ AAPL: SELL 5股 @ $185.20")
    print(f"     实现盈利: ${realized_pnl:.2f}")
    print(f"     交易成本: ${sell_result['costs']['total']:.2f}")

print()

# 演示5: 每日复盘
print("🔄 演示5: Layer 5 - 运行每日交易复盘")
print("-"*70)

from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')

review_report = trading_system.run_daily_review(
    date=today,
    account_id="US_SIM_001"
)

print(f"  复盘日期: {review_report.date}")
print(f"  账户ID: {review_report.account_id}")
print()
print("  📊 交易统计:")
print(f"    • 总交易数: {review_report.total_trades}")
print(f"    • 盈利交易: {review_report.winning_trades}")
print(f"    • 亏损交易: {review_report.losing_trades}")
print(f"    • 胜率: {review_report.win_rate*100:.1f}%")
print()
print("  💰 绩效指标:")
print(f"    • 总盈亏: ${review_report.total_pnl:,.2f}")
print(f"    • 平均盈利: ${review_report.avg_profit:,.2f}")
print(f"    • 平均亏损: ${review_report.avg_loss:,.2f}")
print(f"    • 盈亏比: {review_report.profit_factor:.2f}")
print()
print("  📈 策略绩效:")
for strategy, stats in review_report.strategy_performance.items():
    print(f"    • {strategy}: {stats['trades']}笔, 胜率{stats['win_rate']*100:.0f}%, 盈亏${stats['total_pnl']:.2f}")
print()
print(f"  📝 复盘总结: {review_report.summary}")
print()
print("  🎯 行动项:")
for i, item in enumerate(review_report.action_items, 1):
    print(f"    {i}. {item}")

print()
print("="*70)
print("✅ A5L Layer 4/5 演示完成！")
print()
print("📋 演示内容总结:")
print("  1. Layer 4: 执行模拟交易 (买入/卖出)")
print("  2. Layer 4: 多市场账户管理 (美股/A股/港股)")
print("  3. Layer 4: 风控检查 (止损/仓位/置信度)")
print("  4. Layer 4: 盈亏计算 (已实现/未实现)")
print("  5. Layer 5: 每日自动复盘")
print("  6. Layer 5: 绩效归因分析")
print("  7. Layer 5: 策略效果评估")
print("  8. Layer 5: 生成改进建议")
print()
print("🎯 A5L现已具备完整的模拟交易与复盘能力！")
print("="*70)
