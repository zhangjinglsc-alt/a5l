#!/usr/bin/env python3
"""
实际组合轮动回测 - 快速版（10只股票×5年）
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False

print("🚀 开始实际组合轮动回测...\n")

# 股票池
stocks = ['000001.SZ', '000858.SZ', '600519.SH', '600036.SH', '000066.SZ',
          '000333.SZ', '002594.SZ', '601318.SH', '600900.SH', '300750.SZ']

initial_capital = 1000000
cash = initial_capital
positions = {}  # {code: {shares, cost, entry, high, date}}
trades = []
daily_stats = []

data_cache = {}

def get_data(code, start, end):
    """获取数据"""
    key = f"{code}_{start}_{end}"
    if key in data_cache:
        return data_cache[key]
    if TUSHARE_AVAILABLE:
        try:
            pro = ts.pro_api()
            df = pro.daily(ts_code=code, start_date=start, end_date=end)
            if not df.empty:
                df = df.sort_values('trade_date')
                df.set_index('trade_date', inplace=True)
                df.index = pd.to_datetime(df.index)
                df['ma10'] = df['close'].rolling(10).mean()
                df['ma20'] = df['close'].rolling(20).mean()
                df['change_pct'] = df['close'].pct_change() * 100
                df['high_20'] = df['high'].rolling(20).max()
                df['vol_ma20'] = df['vol'].rolling(20).mean()
                data_cache[key] = df
                return df
        except Exception as e:
            print(f"  获取{code}失败: {e}")
    return None

def scan_signals(date):
    """扫描信号"""
    signals = []
    start = (date - timedelta(days=40)).strftime('%Y%m%d')
    end = date.strftime('%Y%m%d')
    
    for code in stocks:
        df = get_data(code, start, end)
        if df is None or len(df) < 20:
            continue
        row = df.iloc[-1]
        
        # 突破信号
        if (row['close'] >= row['high_20'] * 0.98 and 
            row['change_pct'] > 3 and
            row['vol'] > row['vol_ma20'] * 1.5 and
            row['close'] > row['ma20']):
            signals.append({
                'code': code, 
                'price': row['close'], 
                'change': row['change_pct'],
                'score': row['change_pct'] * row['vol'] / row['vol_ma20']
            })
    
    return sorted(signals, key=lambda x: x['score'], reverse=True)

# 回测周期：2020-2024（5年）
dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='W-MON')
max_positions = 5

print(f"📅 回测周期: 2020-01-01 ~ 2024-12-31 ({len(dates)}周)")
print(f"📊 股票池: {len(stocks)}只")
print(f"💰 初始资金: ¥{initial_capital:,.0f}\n")

for i, date in enumerate(dates):
    date_str = date.strftime('%Y%m%d')
    
    # 检查卖出
    for code in list(positions.keys()):
        df = get_data(code, (date-timedelta(days=5)).strftime('%Y%m%d'), date_str)
        if df is None or len(df) == 0:
            continue
        
        price = df.iloc[-1]['close']
        pos = positions[code]
        
        if price > pos['high']:
            pos['high'] = price
        
        # 卖出条件
        sell = False
        reason = ''
        
        if price <= pos['entry'] * 0.92:
            sell, reason = True, '止损'
        elif pos['high'] >= pos['entry'] * 1.30 and price <= pos['high'] * 0.90:
            sell, reason = True, '止盈'
        elif (date - pos['date']).days > 30:
            if price < df.iloc[-1]['ma10'] * 0.98:
                sell, reason = True, '趋势转弱'
        
        if sell:
            proceeds = price * pos['shares'] * 0.9995
            pnl = proceeds - pos['cost']
            pnl_pct = pnl / pos['cost'] * 100
            days = (date - pos['date']).days
            cash += proceeds
            del positions[code]
            trades.append({'date': date_str, 'code': code, 'pnl': pnl, 'pnl_pct': pnl_pct})
            emoji = "🚀" if pnl_pct > 20 else ("✅" if pnl > 0 else "❌")
            print(f"📉 {date_str} SELL {code} ¥{price:.1f} [{reason}] {emoji} {pnl_pct:+.1f}% ({days}天)")
    
    # 买入
    slots = max_positions - len(positions)
    if slots > 0 and cash > initial_capital * 0.2:
        signals = scan_signals(date)
        signals = [s for s in signals if s['code'] not in positions]
        
        for sig in signals[:slots]:
            code, price = sig['code'], sig['price']
            shares = int(initial_capital * 0.20 / price / 100) * 100
            if shares > 0:
                cost = shares * price * 1.0005
                if cost <= cash * 0.95:
                    cash -= cost
                    positions[code] = {'shares': shares, 'cost': cost, 'entry': price, 'high': price, 'date': date}
                    print(f"📈 {date_str} BUY  {code} ¥{price:.1f} x{shares} (涨{sig['change']:.1f}%)")
    
    # 统计
    pos_value = 0
    for code in positions:
        df = get_data(code, (date-timedelta(days=2)).strftime('%Y%m%d'), date_str)
        if df is not None and len(df) > 0:
            pos_value += positions[code]['shares'] * df.iloc[-1]['close']
    
    total = cash + pos_value
    daily_stats.append({'date': date, 'total': total, 'pos': len(positions)})
    
    # 每月输出
    if i % 4 == 0 and i > 0:
        print(f"   [{date_str}] 总资产: ¥{total:,.0f} ({(total/initial_capital-1)*100:+.1f}%) 持仓{len(positions)}只")

# 报告
df = pd.DataFrame(daily_stats)
final = df['total'].iloc[-1]
total_ret = (final - initial_capital) / initial_capital
years = 5
annual = (final / initial_capital) ** (1/years) - 1

wins = [t for t in trades if t['pnl'] > 0]
big_wins = [t for t in wins if t['pnl_pct'] > 20]
win_rate = len(wins) / len(trades) if trades else 0

cummax = df['total'].cummax()
max_dd = ((df['total'] - cummax) / cummax).min()

print(f"\n{'='*60}")
print(f"📊 实际组合轮动回测结果 (5年)")
print(f"{'='*60}")
print(f"初始资金: ¥{initial_capital:,.0f}")
print(f"最终资金: ¥{final:,.0f}")
print(f"总收益率: {total_ret*100:+.1f}%")
print(f"年化收益率: {annual*100:+.1f}%")
print(f"交易次数: {len(trades)}次")
print(f"胜率: {win_rate*100:.0f}%")
print(f"大赚(>20%): {len(big_wins)}次")
print(f"最大回撤: {max_dd*100:.1f}%")
print(f"{'='*60}")

# 保存
result = {
    'strategy': '组合轮动-实际回测',
    'period': '2020-2024',
    'stocks': stocks,
    'initial': initial_capital,
    'final': final,
    'total_return': total_ret * 100,
    'annual_return': annual * 100,
    'trades': len(trades),
    'win_rate': win_rate * 100,
    'big_wins': len(big_wins),
    'max_drawdown': max_dd * 100
}

Path('/workspace/projects/workspace/data/backtest_results').mkdir(parents=True, exist_ok=True)
with open('/workspace/projects/workspace/data/backtest_results/actual_portfolio_5year.json', 'w') as f:
    json.dump(result, f, indent=2)

print("\n💾 结果已保存到: actual_portfolio_5year.json")
