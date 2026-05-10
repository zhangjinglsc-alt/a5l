#!/usr/bin/env python3
"""
强势股突破策略 - 反向工程化实战模式
核心逻辑：学习中国长城4连板的特征
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False

class MomentumBreakoutStrategy:
    """
    动量突破策略
    核心逻辑：
    1. 股价在20日线上方（中期强势）
    2. 当日涨幅>7%或创20日新高（突破信号）
    3. 成交量放大2倍以上（资金确认）
    4. 买入后持有直到趋势转弱（跌破10日线或涨幅>30%后回撤10%）
    """
    
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.trades = []
        self.daily_stats = []
        
    def get_stock_data(self, code, start_date, end_date):
        """获取数据"""
        cache_file = Path(f"/tmp/momentum_{code}_{start_date}_{end_date}.csv")
        if cache_file.exists():
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        if TUSHARE_AVAILABLE:
            try:
                pro = ts.pro_api()
                df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
                if not df.empty:
                    df = df.sort_values('trade_date')
                    df.set_index('trade_date', inplace=True)
                    df.index = pd.to_datetime(df.index)
                    df.to_csv(cache_file)
                    return df
            except Exception as e:
                print(f"  ❌ {code}: {e}")
        return None
    
    def calculate_indicators(self, df):
        """计算指标"""
        df = df.copy()
        
        # 均线
        for period in [5, 10, 20, 60]:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        
        # 涨跌幅
        df['change_pct'] = df['close'].pct_change() * 100
        
        # 20日最高价
        df['high_20'] = df['high'].rolling(window=20).max()
        df['breakout_20'] = df['high'] >= df['high_20'].shift(1) * 0.99
        
        # 成交量
        df['volume_ma20'] = df['vol'].rolling(window=20).mean()
        df['volume_ratio'] = df['vol'] / df['volume_ma20']
        
        # 趋势强度
        df['trend_score'] = (
            (df['close'] > df['ma5']).astype(int) +
            (df['close'] > df['ma10']).astype(int) +
            (df['close'] > df['ma20']).astype(int) +
            (df['close'] > df['ma60']).astype(int)
        )
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        return df
    
    def breakout_signal(self, df, i):
        """
        突破买入信号
        条件：
        1. 涨幅>7% 或 创20日新高
        2. 成交量放大>2倍
        3. 股价在20日线上方
        4. 趋势评分>=3（强势）
        """
        if i < 60:
            return False
        
        row = df.iloc[i]
        
        # 基本条件
        price_above_ma20 = row['close'] > row['ma20']
        volume_surge = row['volume_ratio'] > 2.0
        strong_trend = row['trend_score'] >= 3
        
        # 突破条件（满足任一）
        big_gain = row['change_pct'] > 7  # 单日大涨7%
        new_high_20 = row['breakout_20'] and row['change_pct'] > 3  # 创20日新高且涨3%
        
        return price_above_ma20 and volume_surge and strong_trend and (big_gain or new_high_20)
    
    def should_sell(self, df, i, pos):
        """
        卖出条件
        1. 跌破10日线（趋势转弱）
        2. 盈利>30%后回撤10%（移动止盈）
        3. 亏损>8%（止损）
        """
        row = df.iloc[i]
        current_price = row['close']
        
        # 止损
        if current_price <= pos['entry_price'] * 0.92:
            return True, '止损'
        
        # 跌破10日线
        if current_price < row['ma10'] * 0.98:
            return True, '趋势转弱'
        
        # 移动止盈：盈利>30%后回撤10%
        if pos['high_since_entry'] >= pos['entry_price'] * 1.30:
            if current_price <= pos['high_since_entry'] * 0.90:
                return True, '移动止盈'
        
        return False, ''
    
    def run_backtest(self, code, start_date, end_date):
        """运行回测"""
        print(f"\n{'='*60}")
        print(f"🚀 动量突破回测: {code} ({start_date}~{end_date})")
        print(f"{'='*60}")
        
        df = self.get_stock_data(code, start_date, end_date)
        if df is None or df.empty:
            return None
        
        df = self.calculate_indicators(df)
        df = df.dropna()
        
        if len(df) < 60:
            return None
        
        code_clean = code.replace('.SZ', '').replace('.SH', '')
        years = len(df) / 252
        
        print(f"📊 数据: {years:.1f}年 | {len(df)}个交易日")
        
        for i in range(len(df)):
            date = df.index[i]
            price = df.iloc[i]['close']
            high = df.iloc[i]['high']
            
            # 检查持仓
            if code_clean in self.positions:
                pos = self.positions[code_clean]
                
                # 更新最高价
                if high > pos['high_since_entry']:
                    pos['high_since_entry'] = high
                
                # 检查卖出
                should_exit, exit_reason = self.should_sell(df, i, pos)
                
                if should_exit:
                    shares = pos['shares']
                    proceeds = shares * price * 0.9995
                    pnl = proceeds - pos['cost_basis']
                    pnl_pct = pnl / pos['cost_basis'] * 100
                    holding_days = (date - pos['entry_date']).days
                    
                    self.cash += proceeds
                    del self.positions[code_clean]
                    
                    self.trades.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'action': 'SELL',
                        'code': code,
                        'price': price,
                        'shares': shares,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'holding_days': holding_days,
                        'reason': exit_reason
                    })
                    
                    emoji = "🚀" if pnl_pct > 20 else ("✅" if pnl > 0 else "❌")
                    print(f"  📉 SELL {date.strftime('%Y%m%d')} {code} ¥{price:.2f} [{exit_reason}] {emoji} {pnl_pct:+.1f}% 持仓{holding_days}天")
            
            # 检查买入
            elif code_clean not in self.positions:
                if self.breakout_signal(df, i):
                    # 仓位：固定30%
                    invest_amount = self.cash * 0.30
                    shares = int(invest_amount / price / 100) * 100
                    
                    if shares > 0:
                        cost = shares * price * 1.0005
                        if cost <= self.cash:
                            self.cash -= cost
                            self.positions[code_clean] = {
                                'shares': shares,
                                'cost_basis': cost,
                                'entry_price': price,
                                'high_since_entry': high,
                                'entry_date': date
                            }
                            
                            change_pct = df.iloc[i]['change_pct']
                            print(f"  📈 BUY  {date.strftime('%Y%m%d')} {code} ¥{price:.2f} x{shares} (涨{change_pct:.1f}%)")
            
            # 每日统计
            position_value = sum(pos['shares'] * price for c, pos in self.positions.items())
            total_value = self.cash + position_value
            self.daily_stats.append({
                'date': date,
                'close': price,
                'cash': self.cash,
                'position_value': position_value,
                'total_value': total_value
            })
        
        return self.generate_report(code, years)
    
    def generate_report(self, code, years):
        """生成报告"""
        if not self.daily_stats:
            return None
        
        df_stats = pd.DataFrame(self.daily_stats)
        
        initial = self.initial_capital
        final = df_stats['total_value'].iloc[-1]
        total_return = (final - initial) / initial
        annual_return = (1 + total_return) ** (1/years) - 1 if total_return > -1 else -1
        
        # 交易统计
        completed_trades = [t for t in self.trades if t['action'] == 'SELL']
        
        if completed_trades:
            winning_trades = [t for t in completed_trades if t['pnl'] > 0]
            big_wins = [t for t in winning_trades if t['pnl_pct'] > 20]  # 大赚>20%
            
            win_rate = len(winning_trades) / len(completed_trades)
            avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['pnl'] for t in completed_trades if t['pnl'] <= 0]) if [t for t in completed_trades if t['pnl'] <= 0] else 0
            avg_holding = np.mean([t['holding_days'] for t in completed_trades])
            
            # 盈亏比
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        else:
            win_rate = avg_win = avg_loss = avg_holding = profit_factor = 0
            winning_trades = big_wins = []
        
        # 最大回撤
        cummax = df_stats['total_value'].cummax()
        drawdown = (df_stats['total_value'] - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 夏普
        daily_returns = df_stats['total_value'].pct_change().dropna()
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        
        report = {
            'code': code,
            'strategy': '动量突破',
            'years': years,
            'initial': initial,
            'final': final,
            'total_return_pct': total_return * 100,
            'annual_return_pct': annual_return * 100,
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'big_wins': len(big_wins),
            'win_rate': win_rate * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'avg_holding_days': avg_holding,
            'max_drawdown_pct': max_drawdown * 100,
            'sharpe': sharpe
        }
        
        print(f"\n📊 {code} 回测结果 ({years:.1f}年)")
        print(f"   总收益: {total_return*100:+.1f}% | 年化: {annual_return*100:+.1f}%")
        print(f"   交易: {len(completed_trades)}次 | 胜率: {win_rate*100:.0f}% | 大赚(>20%): {len(big_wins)}次")
        print(f"   盈亏比: {profit_factor:.1f} | 平均持仓: {avg_holding:.0f}天")
        print(f"   最大回撤: {max_drawdown*100:.1f}% | 夏普: {sharpe:.2f}")
        
        return report


if __name__ == '__main__':
    # 测试多周期
    test_cases = [
        # 15年长期
        ('000001.SZ', '2009-01-01', '2024-12-31'),
        ('000858.SZ', '2009-01-01', '2024-12-31'),
        ('600519.SH', '2009-01-01', '2024-12-31'),
        ('600036.SH', '2009-01-01', '2024-12-31'),
        # 近年强势股票
        ('000066.SZ', '2020-01-01', '2024-12-31'),  # 中国长城
    ]
    
    all_results = []
    
    for code, start, end in test_cases:
        engine = MomentumBreakoutStrategy(initial_capital=1000000)
        result = engine.run_backtest(code, start, end)
        if result:
            all_results.append(result)
    
    # 汇总
    print("\n" + "="*60)
    print("📊 动量突破策略汇总")
    print("="*60)
    
    if all_results:
        returns = [r['total_return_pct'] for r in all_results]
        annuals = [r['annual_return_pct'] for r in all_results]
        win_rates = [r['win_rate'] for r in all_results]
        drawdowns = [r['max_drawdown_pct'] for r in all_results]
        
        print(f"\n平均总收益: {np.mean(returns):+.1f}%")
        print(f"平均年化: {np.mean(annuals):+.1f}%")
        print(f"平均胜率: {np.mean(win_rates):.0f}%")
        print(f"平均最大回撤: {np.mean(drawdowns):.1f}%")
        print(f"最佳: {max(returns):+.1f}% | 最差: {min(returns):+.1f}%")
        
        # 保存
        output = '/workspace/projects/workspace/data/backtest_results/momentum_breakout_results.json'
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n💾 已保存: {output}")
