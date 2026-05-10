#!/usr/bin/env python3
"""
组合轮动策略 - 快速验证版（20只股票池）
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

class QuickPortfolioStrategy:
    def __init__(self, initial_capital=1000000, max_positions=5):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.max_positions = max_positions
        self.positions = {}
        self.trades = []
        self.daily_stats = []
        # 小股票池，快速测试
        self.stock_pool = [
            '000001.SZ', '000858.SZ', '000333.SZ', '002594.SZ', '600519.SH',
            '600036.SH', '600900.SH', '601318.SH', '601888.SH', '300750.SZ',
            '000066.SZ', '002230.SZ', '600276.SH', '601012.SH', '603259.SH',
            '300122.SZ', '002142.SZ', '600031.SH', '300274.SZ', '601166.SH'
        ]
        self.data_cache = {}
    
    def get_data(self, code, start, end):
        cache_key = f"{code}_{start}_{end}"
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        if TUSHARE_AVAILABLE:
            try:
                pro = ts.pro_api()
                df = pro.daily(ts_code=code, start_date=start, end_date=end)
                if not df.empty:
                    df = df.sort_values('trade_date')
                    df.set_index('trade_date', inplace=True)
                    df.index = pd.to_datetime(df.index)
                    self.data_cache[cache_key] = df
                    return df
            except:
                pass
        return None
    
    def calc_indicators(self, df):
        df = df.copy()
        for p in [5, 10, 20, 60]:
            df[f'ma{p}'] = df['close'].rolling(window=p).mean()
        df['change_pct'] = df['close'].pct_change() * 100
        df['high_20'] = df['high'].rolling(window=20).max()
        df['breakout'] = df['close'] >= df['high_20'].shift(1) * 0.98
        df['vol_ma20'] = df['vol'].rolling(window=20).mean()
        df['vol_ratio'] = df['vol'] / df['vol_ma20']
        df['trend_score'] = (
            (df['close'] > df['ma5']).astype(int) +
            (df['close'] > df['ma10']).astype(int) +
            (df['close'] > df['ma20']).astype(int)
        )
        return df
    
    def scan(self, date):
        signals = []
        start = (date - timedelta(days=60)).strftime('%Y%m%d')
        end = date.strftime('%Y%m%d')
        
        for code in self.stock_pool:
            df = self.get_data(code, start, end)
            if df is None or len(df) < 20:
                continue
            df = self.calc_indicators(df)
            row = df.iloc[-1]
            
            if (row['breakout'] and row['change_pct'] > 3 and 
                row['vol_ratio'] > 1.5 and row['close'] > row['ma20'] and
                row['trend_score'] >= 3):
                signals.append({
                    'code': code, 'price': row['close'], 
                    'change': row['change_pct'], 'vol': row['vol_ratio'],
                    'trend': row['trend_score']
                })
        
        return sorted(signals, key=lambda x: x['change'] * x['vol'], reverse=True)
    
    def should_sell(self, code, price, date):
        if code not in self.positions:
            return False, ''
        pos = self.positions[code]
        
        if price <= pos['entry'] * 0.92:
            return True, '止损'
        if pos['high'] >= pos['entry'] * 1.30 and price <= pos['high'] * 0.90:
            return True, '止盈'
        
        # 持仓超30天检查趋势
        days = (date - pos['date']).days
        if days > 30:
            df = self.get_data(code, (date - timedelta(days=10)).strftime('%Y%m%d'),
                              date.strftime('%Y%m%d'))
            if df is not None and len(df) > 0:
                df = self.calc_indicators(df)
                if price < df.iloc[-1]['ma10'] * 0.98:
                    return True, '趋势转弱'
        
        return False, ''
    
    def run(self, start_date, end_date):
        print(f"\n{'='*60}")
        print(f"🚀 组合轮动策略 (20只股票池)")
        print(f"📅 {start_date} ~ {end_date}")
        print(f"💰 初始: ¥{self.initial_capital:,.0f} | 最大{self.max_positions}只")
        print(f"{'='*60}\n")
        
        dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')  # 每周一
        
        for date in dates:
            date_str = date.strftime('%Y%m%d')
            
            # 检查卖出
            for code in list(self.positions.keys()):
                df = self.get_data(code, (date - timedelta(days=5)).strftime('%Y%m%d'), date_str)
                if df is None or len(df) == 0:
                    continue
                
                price = df.iloc[-1]['close']
                pos = self.positions[code]
                if price > pos['high']:
                    pos['high'] = price
                
                sell, reason = self.should_sell(code, price, date)
                if sell:
                    pnl = price * pos['shares'] * 0.9995 - pos['cost']
                    pnl_pct = pnl / pos['cost'] * 100
                    days = (date - pos['date']).days
                    self.cash += price * pos['shares'] * 0.9995
                    del self.positions[code]
                    self.trades.append({'date': date_str, 'code': code, 'pnl': pnl, 'pnl_pct': pnl_pct})
                    emoji = "🚀" if pnl_pct > 20 else ("✅" if pnl > 0 else "❌")
                    print(f"📉 {date_str} SELL {code} ¥{price:.1f} [{reason}] {emoji} {pnl_pct:+.1f}% ({days}天)")
            
            # 买入新信号
            slots = self.max_positions - len(self.positions)
            if slots > 0 and self.cash > self.initial_capital * 0.2:
                signals = self.scan(date)
                signals = [s for s in signals if s['code'] not in self.positions]
                
                for sig in signals[:slots]:
                    code, price = sig['code'], sig['price']
                    shares = int(self.initial_capital * 0.20 / price / 100) * 100
                    if shares > 0:
                        cost = shares * price * 1.0005
                        if cost <= self.cash * 0.95:
                            self.cash -= cost
                            self.positions[code] = {
                                'shares': shares, 'cost': cost, 'entry': price,
                                'high': price, 'date': date
                            }
                            print(f"📈 {date_str} BUY  {code} ¥{price:.1f} x{shares} (涨{sig['change']:.1f}%)")
            
            # 统计
            pos_value = 0
            for code in self.positions:
                df = self.get_data(code, (date - timedelta(days=2)).strftime('%Y%m%d'), date_str)
                if df is not None and len(df) > 0:
                    pos_value += self.positions[code]['shares'] * df.iloc[-1]['close']
            
            total = self.cash + pos_value
            self.daily_stats.append({'date': date, 'total': total, 'pos': len(self.positions)})
        
        return self.report(start_date, end_date)
    
    def report(self, start, end):
        df = pd.DataFrame(self.daily_stats)
        initial, final = self.initial_capital, df['total'].iloc[-1]
        total_ret = (final - initial) / initial
        years = (pd.to_datetime(end) - pd.to_datetime(start)).days / 365
        annual = (1 + total_ret) ** (1/years) - 1 if total_ret > -1 else -1
        
        trades = self.trades
        wins = [t for t in trades if t['pnl'] > 0]
        big_wins = [t for t in wins if t['pnl_pct'] > 20]
        win_rate = len(wins) / len(trades) if trades else 0
        
        cummax = df['total'].cummax()
        max_dd = ((df['total'] - cummax) / cummax).min()
        
        print(f"\n{'='*60}")
        print(f"📊 组合轮动策略结果 ({years:.1f}年)")
        print(f"{'='*60}")
        print(f"总收益: {total_ret*100:+.1f}% | 年化: {annual*100:+.1f}%")
        print(f"交易: {len(trades)}次 | 胜率: {win_rate*100:.0f}% | 大赚: {len(big_wins)}次")
        print(f"最大回撤: {max_dd*100:.1f}%")
        print(f"最终资产: ¥{final:,.0f}")
        
        return {
            'total_return': total_ret * 100, 'annual': annual * 100,
            'trades': len(trades), 'win_rate': win_rate * 100,
            'max_dd': max_dd * 100, 'final': final
        }


if __name__ == '__main__':
    strategy = QuickPortfolioStrategy()
    result = strategy.run('2015-01-01', '2024-12-31')
    
    if result:
        with open('/workspace/projects/workspace/data/backtest_results/quick_portfolio_10y.json', 'w') as f:
            json.dump(result, f)
        print(f"\n💾 结果已保存")
