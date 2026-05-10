#!/usr/bin/env python3
"""
长期回测引擎 - 支持10-15年历史数据
目标：验证策略在更长周期内的稳定性
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False

class LongTermBacktestEngine:
    """长期回测引擎 - 10-15年"""
    
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.trades = []
        self.daily_stats = []
        
    def get_stock_data(self, code, start_date, end_date):
        """获取股票历史数据（支持15年）"""
        cache_file = Path(f"/tmp/lt_stock_data_{code}_{start_date}_{end_date}.csv")
        if cache_file.exists():
            df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            print(f"  📂 从缓存加载: {code} ({len(df)}条数据)")
            return df
        
        if TUSHARE_AVAILABLE:
            try:
                pro = ts.pro_api()
                df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
                if not df.empty:
                    df = df.sort_values('trade_date')
                    df.set_index('trade_date', inplace=True)
                    df.index = pd.to_datetime(df.index)
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    df.to_csv(cache_file)
                    print(f"  ✅ 获取数据: {code} ({len(df)}条, {start_date}~{end_date})")
                    return df
            except Exception as e:
                print(f"  ❌ 获取{code}失败: {e}")
        
        return None
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        
        # 多周期均线
        for period in [5, 10, 20, 60, 120, 250]:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        
        # 长期趋势（年线）
        df['long_trend'] = np.where(df['close'] > df['ma250'], 1, -1)
        df['mid_trend'] = np.where(df['close'] > df['ma60'], 1, 
                                   np.where(df['close'] < df['ma60'] * 0.95, -1, 0))
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # 波动率
        df['volatility'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
        
        # 成交量
        df['volume_ma20'] = df['vol'].rolling(window=20).mean()
        df['volume_ratio'] = df['vol'] / df['volume_ma20']
        
        return df
    
    def trend_following_strategy(self, df, i):
        """
        趋势跟随策略 - 长期版本
        只在年线之上操作 + 中期趋势确认
        """
        if i < 250:
            return 'HOLD'
        
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        # 长期过滤：只在年线之上
        if row['long_trend'] != 1:
            return 'HOLD'
        
        # 买入：中期金叉 + 放量 + RSI不过热
        buy_signal = (
            row['mid_trend'] == 1 and
            prev_row['ma5'] <= prev_row['ma10'] and
            row['ma5'] > row['ma10'] and
            row['volume_ratio'] > 1.0 and
            35 < row['rsi'] < 70
        )
        
        # 卖出：中期转弱 或 RSI超买
        sell_signal = (
            row['mid_trend'] == -1 or
            row['rsi'] > 75 or
            (prev_row['macd'] >= prev_row['macd_signal'] and 
             row['macd'] < row['macd_signal'])
        )
        
        if buy_signal:
            return 'BUY'
        elif sell_signal:
            return 'SELL'
        return 'HOLD'
    
    def run_backtest(self, code, start_date, end_date, strategy_name='趋势跟随_年线过滤'):
        """运行回测"""
        print(f"\n{'='*70}")
        print(f"📈 长期回测: {code}")
        print(f"📅 周期: {start_date} ~ {end_date}")
        print(f"🎯 策略: {strategy_name}")
        print(f"{'='*70}")
        
        df = self.get_stock_data(code, start_date, end_date)
        if df is None or df.empty:
            print(f"❌ 无法获取{code}数据")
            return None
        
        df = self.calculate_indicators(df)
        df = df.dropna()
        
        if len(df) < 250:
            print(f"❌ 数据不足: {len(df)}条（需要至少250日）")
            return None
        
        code_clean = code.replace('.SZ', '').replace('.SH', '')
        years = len(df) / 252
        print(f"📊 数据年份: ~{years:.1f}年 | 总交易日: {len(df)}天")
        
        for i in range(len(df)):
            date = df.index[i]
            price = df.iloc[i]['close']
            high = df.iloc[i]['high']
            
            signal = self.trend_following_strategy(df, i)
            
            # 持仓止损检查
            if code_clean in self.positions:
                pos = self.positions[code_clean]
                
                if high > pos['high_since_entry']:
                    pos['high_since_entry'] = high
                
                # 移动止损：最高点回撤12%
                trailing_stop = pos['high_since_entry'] * 0.88
                hard_stop = pos['cost_basis'] * 0.90
                stop_price = max(trailing_stop, hard_stop)
                
                # 止盈：盈利20%后回撤8%止盈
                if price >= pos['entry_price'] * 1.20:
                    stop_price = max(stop_price, pos['high_since_entry'] * 0.92)
                
                if price <= stop_price:
                    signal = 'SELL_STOP'
            
            # 执行交易
            if signal == 'BUY' and code_clean not in self.positions:
                volatility = df.iloc[i]['volatility'] if not pd.isna(df.iloc[i]['volatility']) else 0.02
                position_pct = min(0.5, 0.25 / (volatility * 12 + 0.01))
                position_pct = max(0.15, min(0.5, position_pct))
                
                invest_amount = self.cash * position_pct
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
                            'entry_date': date,
                            'stop_price': price * 0.90
                        }
                        self.trades.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'action': 'BUY',
                            'code': code,
                            'price': price,
                            'shares': shares,
                            'amount': cost,
                            'cash_after': self.cash
                        })
            
            elif signal.startswith('SELL') and code_clean in self.positions:
                pos = self.positions[code_clean]
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
                    'amount': proceeds,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'holding_days': holding_days,
                    'cash_after': self.cash
                })
            
            # 每日统计
            position_value = sum(pos['shares'] * price for c, pos in self.positions.items())
            total_value = self.cash + position_value
            self.daily_stats.append({
                'date': date,
                'close': price,
                'cash': self.cash,
                'position_value': position_value,
                'total_value': total_value,
                'positions_count': len(self.positions)
            })
        
        return self.generate_report(code, years)
    
    def generate_report(self, code, years):
        """生成回测报告"""
        if not self.daily_stats:
            return None
        
        df_stats = pd.DataFrame(self.daily_stats)
        
        initial = self.initial_capital
        final = df_stats['total_value'].iloc[-1]
        total_return = (final - initial) / initial
        annual_return = (1 + total_return) ** (1/years) - 1 if total_return > -1 else -1
        
        # 交易统计
        completed_trades = []
        entry = None
        for t in self.trades:
            if t['action'] == 'BUY':
                entry = t
            elif t['action'] == 'SELL' and entry:
                completed_trades.append({
                    'pnl': t.get('pnl', 0),
                    'pnl_pct': t.get('pnl_pct', 0),
                    'holding_days': t.get('holding_days', 0)
                })
                entry = None
        
        if completed_trades:
            winning_trades = [t for t in completed_trades if t['pnl'] > 0]
            win_rate = len(winning_trades) / len(completed_trades)
            avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
            losing_trades = [t for t in completed_trades if t['pnl'] <= 0]
            avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
            avg_holding = np.mean([t['holding_days'] for t in completed_trades])
        else:
            win_rate = avg_win = avg_loss = avg_holding = 0
            winning_trades = losing_trades = []
        
        # 年度收益
        df_stats['year'] = df_stats['date'].dt.year
        annual_returns = {}
        for year in df_stats['year'].unique():
            year_data = df_stats[df_stats['year'] == year]
            if len(year_data) > 1:
                year_return = (year_data['total_value'].iloc[-1] / year_data['total_value'].iloc[0]) - 1
                annual_returns[str(year)] = year_return * 100
        
        # 最大回撤
        cummax = df_stats['total_value'].cummax()
        drawdown = (df_stats['total_value'] - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 夏普比率
        daily_returns = df_stats['total_value'].pct_change().dropna()
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        
        report = {
            'code': code,
            'strategy_name': '趋势跟随_年线过滤',
            'years': years,
            'initial_capital': initial,
            'final_capital': final,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'annual_return': annual_return,
            'annual_return_pct': annual_return * 100,
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_holding_days': avg_holding,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'sharpe_ratio': sharpe,
            'annual_returns': annual_returns,
            'trades': self.trades
        }
        
        print(f"\n{'='*70}")
        print(f"📊 {code} 长期回测报告 ({years:.1f}年)")
        print(f"{'='*70}")
        print(f"初始资金: ¥{initial:,.0f}")
        print(f"最终资金: ¥{final:,.0f}")
        print(f"总收益: {total_return*100:+.2f}%")
        print(f"年化收益: {annual_return*100:+.2f}%")
        print(f"总交易: {len(completed_trades)}次 | 胜率: {win_rate*100:.1f}%")
        print(f"平均持仓: {avg_holding:.0f}天")
        print(f"最大回撤: {max_drawdown*100:.1f}%")
        print(f"夏普比率: {sharpe:.2f}")
        print(f"\n年度收益:")
        for year, ret in sorted(annual_returns.items()):
            bar = "█" * int(abs(ret) / 2)
            print(f"  {year}: {ret:+.1f}% {bar}")
        
        return report


def run_15_year_backtest():
    """运行15年回测（2009-2024）"""
    print("\n" + "="*70)
    print("🚀 启动15年长期回测 (2009-2024)")
    print("="*70)
    
    # 15年回测标的
    test_stocks = [
        ('000001.SZ', '2009-01-01', '2024-12-31'),  # 平安银行 - 15年
        ('000858.SZ', '2009-01-01', '2024-12-31'),  # 五粮液 - 15年
        ('600519.SH', '2009-01-01', '2024-12-31'),  # 茅台 - 15年
        ('600036.SH', '2009-01-01', '2024-12-31'),  # 招商银行 - 15年
    ]
    
    all_results = []
    
    for code, start, end in test_stocks:
        engine = LongTermBacktestEngine(initial_capital=1000000)
        result = engine.run_backtest(code, start, end)
        if result:
            all_results.append(result)
    
    # 汇总
    print("\n" + "="*70)
    print("📊 15年回测汇总统计")
    print("="*70)
    
    if all_results:
        total_returns = [r['total_return_pct'] for r in all_results]
        annual_returns = [r['annual_return_pct'] for r in all_results]
        win_rates = [r['win_rate'] * 100 for r in all_results]
        drawdowns = [r['max_drawdown_pct'] for r in all_results]
        
        print(f"\n股票数量: {len(all_results)}只")
        print(f"回测周期: 15年 (2009-2024)")
        print(f"平均总收益: {np.mean(total_returns):+.2f}%")
        print(f"平均年化收益: {np.mean(annual_returns):+.2f}%")
        print(f"平均胜率: {np.mean(win_rates):.1f}%")
        print(f"平均最大回撤: {np.mean(drawdowns):.1f}%")
        print(f"最佳收益: {max(total_returns):+.2f}%")
        print(f"最差收益: {min(total_returns):+.2f}%")
        
        # 保存结果
        output_file = '/workspace/projects/workspace/data/backtest_results/15_year_longterm_results.json'
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 完整结果已保存: {output_file}")
        
        return all_results
    
    return None


if __name__ == '__main__':
    # 执行15年回测
    results = run_15_year_backtest()
    
    if results:
        print("\n✅ 15年长期回测完成!")
    else:
        print("\n⚠️ 回测未能完成")
