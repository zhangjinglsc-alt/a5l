#!/usr/bin/env python3
"""
优化版策略回测 v2 - 提高交易频率
降低趋势过滤门槛 + 增加波段策略 + 多时间框架
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False

class OptimizedBacktestEngine:
    """优化版回测引擎 v2"""
    
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.trades = []
        self.daily_stats = []
        
    def get_stock_data(self, code, start_date, end_date):
        """获取股票历史数据"""
        cache_file = Path(f"/tmp/stock_data_{code}_{start_date}_{end_date}.csv")
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
                    cache_file.parent.mkdir(parents=True, exist_ok=True)
                    df.to_csv(cache_file)
                    return df
            except Exception as e:
                print(f"获取{code}数据失败: {e}")
        
        return None
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        
        # 多周期均线
        for period in [5, 10, 20, 60]:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        
        # 趋势强度（价格与均线偏离度）
        df['trend_strength'] = (df['close'] - df['ma60']) / df['ma60']
        
        # 短期趋势
        df['short_trend'] = np.where(df['close'] > df['ma20'], 1, -1)
        # 中期趋势
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
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # 布林带
        df['boll_mid'] = df['close'].rolling(window=20).mean()
        df['boll_std'] = df['close'].rolling(window=20).std()
        df['boll_up'] = df['boll_mid'] + 2 * df['boll_std']
        df['boll_down'] = df['boll_mid'] - 2 * df['boll_std']
        df['boll_pct'] = (df['close'] - df['boll_down']) / (df['boll_up'] - df['boll_down'])
        
        # 波动率
        df['volatility'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        # 成交量
        df['volume_ma20'] = df['vol'].rolling(window=20).mean()
        df['volume_ratio'] = df['vol'] / df['volume_ma20']
        
        # 动量
        df['momentum_5'] = df['close'].pct_change(5)
        df['momentum_10'] = df['close'].pct_change(10)
        
        return df
    
    def multi_timeframe_strategy(self, df, i):
        """
        多时间框架策略
        结合短期动量 + 中期趋势 + 超卖反弹
        """
        if i < 60:
            return 'HOLD'
        
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        code_clean = None  # 稍后设置
        
        # === 买入条件（满足任一即可）===
        
        # 1. 趋势跟踪型：中期向上 + 短期金叉 + 量能配合
        trend_follow_buy = (
            row['mid_trend'] >= 0 and  # 中期不跌
            row['short_trend'] == 1 and  # 短期向上
            prev_row['ma5'] <= prev_row['ma10'] and
            row['ma5'] > row['ma10'] and  # 金叉
            row['volume_ratio'] > 1.0 and  # 量能略增
            30 < row['rsi'] < 70  # RSI中性区
        )
        
        # 2. 超卖反弹型：中期向上 + 短期超卖 + 布林带下轨反弹
        oversold_bounce_buy = (
            row['mid_trend'] >= 0 and
            row['rsi'] < 35 and  # 超卖
            row['boll_pct'] < 0.2 and  # 接近布林带下轨
            row['close'] > row['open']  # 当日阳线
        )
        
        # 3. MACD金叉型：中期向上 + MACD金叉 + 柱状线转正
        macd_buy = (
            row['mid_trend'] >= 0 and
            prev_row['macd'] <= prev_row['macd_signal'] and
            row['macd'] > row['macd_signal'] and  # MACD金叉
            row['macd_hist'] > 0 and  # 柱状线为正
            row['macd'] > -0.5  # MACD不过低（避免弱势金叉）
        )
        
        # 4. 突破型：创20日新高 + 放量
        breakout_buy = (
            row['close'] > df.iloc[i-20:i]['high'].max() * 0.99 and  # 接近20日高点
            row['volume_ratio'] > 1.3 and  # 明显放量
            row['short_trend'] == 1
        )
        
        buy_signal = trend_follow_buy or oversold_bounce_buy or macd_buy or breakout_buy
        
        # === 卖出条件（满足任一即可）===
        
        # 1. 趋势转弱：中期向下 + 死叉
        trend_weak_sell = (
            row['mid_trend'] == -1 and
            prev_row['ma5'] >= prev_row['ma10'] and
            row['ma5'] < row['ma10']
        )
        
        # 2. 超买型：RSI超买 + 滞涨
        overbought_sell = (
            row['rsi'] > 75 or
            (row['rsi'] > 70 and row['close'] < row['open'])
        )
        
        # 3. MACD死叉
        macd_sell = (
            prev_row['macd'] >= prev_row['macd_signal'] and
            row['macd'] < row['macd_signal'] and
            row['macd_hist'] < 0
        )
        
        # 4. 布林带上轨滞涨
        boll_sell = (
            row['boll_pct'] > 0.9 and
            row['close'] < row['open']  # 上轨附近收阴
        )
        
        sell_signal = trend_weak_sell or overbought_sell or macd_sell or boll_sell
        
        if buy_signal:
            return 'BUY'
        elif sell_signal:
            return 'SELL'
        return 'HOLD'
    
    def run_backtest(self, code, start_date, end_date):
        """运行回测"""
        print(f"\n{'='*60}")
        print(f"回测: {code} | {start_date} ~ {end_date}")
        print(f"策略: 多时间框架组合")
        print(f"{'='*60}")
        
        df = self.get_stock_data(code, start_date, end_date)
        if df is None or df.empty:
            print(f"❌ 无法获取{code}数据")
            return None
        
        df = self.calculate_indicators(df)
        df = df.dropna()
        
        if len(df) < 60:
            print(f"❌ 数据不足: {len(df)}条")
            return None
        
        code_clean = code.replace('.SZ', '').replace('.SH', '')
        
        for i in range(len(df)):
            date = df.index[i]
            price = df.iloc[i]['close']
            high = df.iloc[i]['high']
            
            signal = self.multi_timeframe_strategy(df, i)
            
            # 检查持仓止损止盈
            if code_clean in self.positions:
                pos = self.positions[code_clean]
                
                # 更新最高价
                if high > pos['high_since_entry']:
                    pos['high_since_entry'] = high
                
                # 移动止损：最高点回撤10%
                trailing_stop = pos['high_since_entry'] * 0.90
                # 硬止损：成本价下跌8%
                hard_stop = pos['cost_basis'] * 0.92
                # 取较高者作为止损价
                stop_price = max(trailing_stop, hard_stop)
                
                # 止盈：盈利15%后，回撤5%止盈
                if price >= pos['entry_price'] * 1.15:
                    stop_price = max(stop_price, pos['high_since_entry'] * 0.95)
                
                if price <= stop_price:
                    signal = 'SELL_STOP'
            
            # 执行交易
            if signal.startswith('BUY') and code_clean not in self.positions:
                # 动态仓位：根据波动率和趋势强度调整
                volatility = df.iloc[i]['volatility'] if not pd.isna(df.iloc[i]['volatility']) else 0.02
                trend_strength = abs(df.iloc[i]['trend_strength']) if not pd.isna(df.iloc[i]['trend_strength']) else 0.05
                
                # 波动小+趋势强 = 重仓；波动大+趋势弱 = 轻仓
                position_pct = min(0.4, 0.2 / (volatility * 15 + 0.01)) * (1 + trend_strength * 2)
                position_pct = max(0.1, min(0.4, position_pct))  # 限制在10%-40%
                
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
                            'stop_price': price * 0.92
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
                        print(f"  📈 BUY {date.strftime('%Y-%m-%d')} {code} @ {price:.2f} x{shares} (仓位{position_pct*100:.0f}%)")
            
            elif (signal.startswith('SELL') or signal == 'SELL_STOP') and code_clean in self.positions:
                pos = self.positions[code_clean]
                shares = pos['shares']
                proceeds = shares * price * 0.9995
                pnl = proceeds - pos['cost_basis']
                pnl_pct = pnl / pos['cost_basis'] * 100
                holding_days = (date - pos['entry_date']).days
                
                self.cash += proceeds
                del self.positions[code_clean]
                
                sell_reason = '止损' if signal == 'SELL_STOP' else '信号'
                
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
                    'reason': sell_reason,
                    'cash_after': self.cash
                })
                
                emoji = "✅" if pnl > 0 else "❌"
                print(f"  📉 SELL {date.strftime('%Y-%m-%d')} {code} @ {price:.2f} [{sell_reason}] | {emoji} PnL: {pnl:,.0f} ({pnl_pct:+.2f}%) 持仓{holding_days}天")
            
            # 记录每日统计
            position_value = sum(
                pos['shares'] * price
                for c, pos in self.positions.items()
            )
            total_value = self.cash + position_value
            self.daily_stats.append({
                'date': date,
                'close': price,
                'cash': self.cash,
                'position_value': position_value,
                'total_value': total_value,
                'positions_count': len(self.positions)
            })
        
        return self.generate_report(code)
    
    def generate_report(self, code):
        """生成回测报告"""
        if not self.daily_stats:
            return None
        
        df_stats = pd.DataFrame(self.daily_stats)
        
        initial = self.initial_capital
        final = df_stats['total_value'].iloc[-1]
        total_return = (final - initial) / initial
        
        days = (df_stats['date'].iloc[-1] - df_stats['date'].iloc[0]).days
        years = max(days / 365, 0.01)
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
            avg_loss = np.mean([t['pnl'] for t in completed_trades if t['pnl'] <= 0]) if [t for t in completed_trades if t['pnl'] <= 0] else 0
            avg_holding = np.mean([t['holding_days'] for t in completed_trades])
        else:
            win_rate = avg_win = avg_loss = avg_holding = 0
        
        cummax = df_stats['total_value'].cummax()
        drawdown = (df_stats['total_value'] - cummax) / cummax
        max_drawdown = drawdown.min()
        
        daily_returns = df_stats['total_value'].pct_change().dropna()
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        
        report = {
            'code': code,
            'strategy_name': '多时间框架组合',
            'initial_capital': initial,
            'final_capital': final,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'annual_return': annual_return,
            'annual_return_pct': annual_return * 100,
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades) if completed_trades else 0,
            'losing_trades': len(completed_trades) - len(winning_trades) if completed_trades else 0,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_holding_days': avg_holding,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'sharpe_ratio': sharpe,
            'trades': self.trades
        }
        
        print(f"\n{'='*60}")
        print(f"📊 {code} 回测报告")
        print(f"{'='*60}")
        print(f"初始资金: ¥{initial:,.0f}")
        print(f"最终资金: ¥{final:,.0f}")
        print(f"总收益: {total_return*100:+.2f}%")
        print(f"年化收益: {annual_return*100:+.2f}%")
        print(f"总交易: {len(completed_trades)}次")
        print(f"胜率: {win_rate*100:.1f}%")
        print(f"平均持仓: {avg_holding:.0f}天")
        print(f"最大回撤: {max_drawdown*100:.1f}%")
        print(f"夏普比率: {sharpe:.2f}")
        
        return report


if __name__ == '__main__':
    # 测试更多股票和更长时间
    test_stocks = [
        ('000001.SZ', '2019-01-01', '2024-12-31'),  # 平安银行 - 6年
        ('000858.SZ', '2019-01-01', '2024-12-31'),  # 五粮液 - 6年
        ('600519.SH', '2019-01-01', '2024-12-31'),  # 茅台 - 6年
        ('000333.SZ', '2019-01-01', '2024-12-31'),  # 美的集团
        ('600036.SH', '2019-01-01', '2024-12-31'),  # 招商银行
    ]
    
    all_results = []
    
    for code, start, end in test_stocks:
        engine = OptimizedBacktestEngine(initial_capital=1000000)
        result = engine.run_backtest(code, start, end)
        if result:
            all_results.append(result)
    
    # 汇总统计
    print(f"\n{'='*60}")
    print("📊 多股票汇总统计")
    print(f"{'='*60}")
    
    total_returns = [r['total_return_pct'] for r in all_results]
    win_rates = [r['win_rate'] * 100 for r in all_results]
    drawdowns = [r['max_drawdown_pct'] for r in all_results]
    
    print(f"平均总收益: {np.mean(total_returns):+.2f}%")
    print(f"平均胜率: {np.mean(win_rates):.1f}%")
    print(f"平均最大回撤: {np.mean(drawdowns):.1f}%")
    print(f"最佳股票收益: {max(total_returns):+.2f}%")
    print(f"最差股票收益: {min(total_returns):+.2f}%")
    
    # 保存结果
    output_file = '/workspace/projects/workspace/data/backtest_results/optimized_strategy_v2_results.json'
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 结果已保存: {output_file}")
