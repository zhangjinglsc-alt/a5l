#!/usr/bin/env python3
"""
三版本信号过滤器回测引擎
版本：保守型(Strict) / 平衡型(Balanced) / 激进型(Aggressive)
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

# 从缓存读取数据
def load_cached_data(code, start_date, end_date):
    cache_file = Path(f"/tmp/strategy_data_cache/{code}_{start_date}_{end_date}.csv")
    if cache_file.exists():
        df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        return df
    return None

class ThreeVersionBacktest:
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.results = {}
    
    def buy_signal_strict(self, row, df, i):
        """
        保守型买入条件（必须同时满足）
        1. 涨幅 ≥ 7%
        2. 成交量 ≥ 3倍20日均量
        3. 创60日新高
        4. 股价在20日线上方
        5. 趋势评分 = 4
        6. RSI 40-70
        """
        if i < 60:
            return False
        
        high_60 = df.iloc[i-60:i]['high'].max()
        
        conditions = [
            row['change_pct'] >= 7,
            row['volume_ratio'] >= 3.0,
            row['close'] >= high_60 * 0.98,
            row['close'] > row['ma20'],
            row['trend_score'] == 4,
            40 <= row['rsi'] <= 70
        ]
        
        return all(conditions)
    
    def buy_signal_balanced(self, row, df, i):
        """
        平衡型买入条件（3个核心+2个辅助）
        核心（必须全部满足）：
        1. 涨幅 ≥ 5%
        2. 成交量 ≥ 2.5倍20日均量
        3. 创20日新高
        
        辅助（满足2/3）：
        4. 趋势评分 ≥ 3
        5. 股价 > 20日线
        6. MACD柱状线扩大
        """
        if i < 20:
            return False
        
        # 核心条件
        core = [
            row['change_pct'] >= 5,
            row['volume_ratio'] >= 2.5,
            row['close'] >= row['high_20'] * 0.98
        ]
        
        if not all(core):
            return False
        
        # 辅助条件
        aux = [
            row['trend_score'] >= 3,
            row['close'] > row['ma20'],
            row['macd_hist'] > df.iloc[i-1]['macd_hist'] if i > 0 else False
        ]
        
        return sum(aux) >= 2
    
    def buy_signal_aggressive(self, row, df, i):
        """
        激进型买入条件（满足3/5）
        1. 涨幅 ≥ 3%
        2. 成交量 ≥ 2倍20日均量
        3. 创10日新高
        4. 趋势评分 ≥ 2
        5. RSI 35-75
        """
        if i < 10:
            return False
        
        high_10 = df.iloc[i-10:i]['high'].max()
        
        conditions = [
            row['change_pct'] >= 3,
            row['volume_ratio'] >= 2.0,
            row['close'] >= high_10 * 0.98,
            row['trend_score'] >= 2,
            35 <= row['rsi'] <= 75
        ]
        
        return sum(conditions) >= 3
    
    def run_backtest(self, code, start_date, end_date, version='balanced'):
        """运行单版本回测"""
        df = load_cached_data(code, start_date, end_date)
        if df is None or len(df) < 60:
            return None
        
        cash = self.initial_capital
        position = None
        trades = []
        daily_values = []
        
        # 选择信号函数
        if version == 'strict':
            buy_signal = self.buy_signal_strict
            stop_loss = 0.94  # -6%
            take_profit_trigger = 0.25  # 25%后回撤8%
            take_profit_drop = 0.92
            trend_exit_ma = 15
            max_holding = 45
        elif version == 'balanced':
            buy_signal = self.buy_signal_balanced
            stop_loss = 0.93  # -7%
            take_profit_trigger = 0.20  # 20%后回撤10%
            take_profit_drop = 0.90
            trend_exit_ma = 12
            max_holding = 35
        else:  # aggressive
            buy_signal = self.buy_signal_aggressive
            stop_loss = 0.92  # -8%
            take_profit_trigger = 0.15  # 15%后回撤12%
            take_profit_drop = 0.88
            trend_exit_ma = 10
            max_holding = 25
        
        for i in range(60, len(df)):
            date = df.index[i]
            price = df.iloc[i]['close']
            high = df.iloc[i]['high']
            
            # 检查持仓卖出
            if position:
                # 更新最高价
                if high > position['high']:
                    position['high'] = high
                
                # 止损
                if price <= position['entry'] * stop_loss:
                    pnl = price * position['shares'] * 0.9995 - position['cost']
                    pnl_pct = pnl / position['cost'] * 100
                    days = (date - position['date']).days
                    cash += price * position['shares'] * 0.9995
                    trades.append({'pnl': pnl, 'pnl_pct': pnl_pct, 'days': days, 'reason': '止损'})
                    position = None
                
                # 移动止盈
                elif position['high'] >= position['entry'] * (1 + take_profit_trigger):
                    if price <= position['high'] * take_profit_drop:
                        pnl = price * position['shares'] * 0.9995 - position['cost']
                        pnl_pct = pnl / position['cost'] * 100
                        days = (date - position['date']).days
                        cash += price * position['shares'] * 0.9995
                        trades.append({'pnl': pnl, 'pnl_pct': pnl_pct, 'days': days, 'reason': '止盈'})
                        position = None
                
                # 趋势退出
                elif price < df.iloc[i][f'ma{trend_exit_ma}'] * 0.98:
                    pnl = price * position['shares'] * 0.9995 - position['cost']
                    pnl_pct = pnl / position['cost'] * 100
                    days = (date - position['date']).days
                    cash += price * position['shares'] * 0.9995
                    trades.append({'pnl': pnl, 'pnl_pct': pnl_pct, 'days': days, 'reason': '趋势'})
                    position = None
                
                # 最大持仓时间
                elif (date - position['date']).days > max_holding:
                    pnl = price * position['shares'] * 0.9995 - position['cost']
                    pnl_pct = pnl / position['cost'] * 100
                    days = (date - position['date']).days
                    cash += price * position['shares'] * 0.9995
                    trades.append({'pnl': pnl, 'pnl_pct': pnl_pct, 'days': days, 'reason': '到期'})
                    position = None
            
            # 买入信号
            elif not position and buy_signal(df.iloc[i], df, i):
                shares = int(cash * 0.95 / price / 100) * 100
                if shares > 0:
                    cost = shares * price * 1.0005
                    cash -= cost
                    position = {
                        'shares': shares,
                        'cost': cost,
                        'entry': price,
                        'high': high,
                        'date': date
                    }
            
            # 记录每日价值
            pos_value = position['shares'] * price if position else 0
            daily_values.append({'date': date, 'total': cash + pos_value})
        
        # 计算结果
        if not daily_values:
            return None
        
        final_value = daily_values[-1]['total']
        total_return = (final_value - self.initial_capital) / self.initial_capital
        years = 5
        annual_return = (final_value / self.initial_capital) ** (1/years) - 1
        
        # 交易统计
        if trades:
            wins = [t for t in trades if t['pnl'] > 0]
            big_wins = [t for t in wins if t['pnl_pct'] > 20]
            win_rate = len(wins) / len(trades)
            avg_holding = np.mean([t['days'] for t in trades])
            
            avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
            losses = [t for t in trades if t['pnl'] <= 0]
            avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        else:
            win_rate = big_wins = avg_holding = profit_factor = 0
            wins = []
        
        # 最大回撤
        values = [v['total'] for v in daily_values]
        cummax = np.maximum.accumulate(values)
        drawdowns = [(v - m) / m for v, m in zip(values, cummax)]
        max_drawdown = min(drawdowns) if drawdowns else 0
        
        return {
            'code': code,
            'version': version,
            'final_value': final_value,
            'total_return': total_return * 100,
            'annual_return': annual_return * 100,
            'trades': len(trades),
            'winning_trades': len(wins),
            'big_wins': len(big_wins),
            'win_rate': win_rate * 100,
            'profit_factor': profit_factor,
            'avg_holding': avg_holding,
            'max_drawdown': max_drawdown * 100
        }
    
    def run_all_versions(self, stocks, start_date, end_date):
        """运行所有版本对比"""
        versions = ['strict', 'balanced', 'aggressive']
        results = {v: [] for v in versions}
        
        print("="*70)
        print("🚀 三版本信号过滤器回测对比")
        print(f"📅 {start_date} ~ {end_date}")
        print(f"📊 股票池: {len(stocks)}只")
        print("="*70)
        
        for version in versions:
            print(f"\n{'='*70}")
            print(f"📌 版本: {version.upper()}")
            print(f"{'='*70}")
            
            for code in stocks:
                result = self.run_backtest(code, start_date, end_date, version)
                if result:
                    results[version].append(result)
                    print(f"  {code}: 年化{result['annual_return']:+.1f}% | 胜率{result['win_rate']:.0f}% | 交易{result['trades']}次")
            
            # 版本汇总
            if results[version]:
                avg_annual = np.mean([r['annual_return'] for r in results[version]])
                avg_win_rate = np.mean([r['win_rate'] for r in results[version]])
                avg_trades = np.mean([r['trades'] for r in results[version]])
                avg_pf = np.mean([r['profit_factor'] for r in results[version] if r['profit_factor'] > 0])
                avg_dd = np.mean([r['max_drawdown'] for r in results[version]])
                
                print(f"\n  📊 {version.upper()} 版本汇总:")
                print(f"     平均年化: {avg_annual:+.1f}%")
                print(f"     平均胜率: {avg_win_rate:.0f}%")
                print(f"     平均交易: {avg_trades:.1f}次")
                print(f"     平均盈亏比: {avg_pf:.1f}")
                print(f"     平均最大回撤: {avg_dd:.1f}%")
        
        return results


if __name__ == '__main__':
    stocks = [
        '000001.SZ', '000858.SZ', '600519.SH', '600036.SH', '000066.SZ',
        '000333.SZ', '002594.SZ', '601318.SH', '600900.SH', '300750.SZ'
    ]
    
    engine = ThreeVersionBacktest(initial_capital=1000000)
    results = engine.run_all_versions(stocks, '20200101', '20241231')
    
    # 保存结果
    output_file = '/workspace/projects/workspace/data/backtest_results/three_versions_comparison.json'
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"💾 完整结果已保存: {output_file}")
    print(f"{'='*70}")
