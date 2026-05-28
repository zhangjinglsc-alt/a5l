#!/usr/bin/env python3
"""
2026-05-27 美股交易计划执行脚本
"""
import sys
sys.path.insert(0, '/workspace/projects/workspace/data/simulation')
from a5l_unified_trader import us_buy, portfolio_all, report_all

print("📅 2026-05-27 美股交易计划执行")
print("="*50)

# 1. 执行日内T+0交易
print("\n1. 执行日内交易订单:")
# 买入$10,000 NVDA 做T+0，逻辑：英伟达AI龙头，日内波动大，适合高抛低吸
us_buy('NVDA', 10000, "日内T+0交易：英伟达AI龙头，今日半导体板块预计走强，博取1-2%日内收益")

# 买入$10,000 TSLA 做T+0，逻辑：特斯拉近期波动放大，新能源+机器人概念，日内交易机会充足
us_buy('TSLA', 10000, "日内T+0交易：特斯拉波动充足，今日新能源车板块催化，博取日内收益")

# 2. 打印当前持仓
print("\n2. 当前美股持仓:")
portfolio_all()

# 3. 打印交易报告
print("\n3. 今日交易记录:")
report_all()

print("\n✅ 今日美股交易计划执行完成")
print("📝 所有交易决策已记录到系统")
