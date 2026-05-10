#!/usr/bin/env python3
"""
多股票组合轮动策略 - Portfolio Rotation Strategy
核心逻辑：
1. 监控股票池（50-100只）
2. 每天选出最强动量股票（突破信号+趋势评分）
3. 最多同时持有5只，每只20%仓位
4. 每周轮动，淘汰弱势股，纳入强势股
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

class PortfolioRotationStrategy:
    """组合轮动策略"""
    
    def __init__(self, initial_capital=1000000, max_positions=5):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.max_positions = max_positions  # 最多持有5只
        self.positions = {}  # {code: position_dict}
        self.trades = []
        self.daily_stats = []
        self.stock_pool = []  # 股票池
        self.stock_data_cache = {}  # 数据缓存
        
    def build_stock_pool(self):
        """构建股票池 - 沪深300成分股"""
        # 使用常见大盘股作为测试池
        self.stock_pool = [
            '000001.SZ', '000002.SZ', '000063.SZ', '000066.SZ', '000100.SZ',
            '000333.SZ', '000338.SZ', '000568.SZ', '000651.SZ', '000725.SZ',
            '000768.SZ', '000858.SZ', '000895.SZ', '002001.SZ', '002007.SZ',
            '002024.SZ', '002027.SZ', '002142.SZ', '002230.SZ', '002236.SZ',
            '002271.SZ', '002304.SZ', '002352.SZ', '002415.SZ', '002460.SZ',
            '002475.SZ', '002594.SZ', '002714.SZ', '002812.SZ', '300003.SZ',
            '300014.SZ', '300015.SZ', '300033.SZ', '300059.SZ', '300122.SZ',
            '300124.SZ', '300274.SZ', '300408.SZ', '300413.SZ', '300433.SZ',
            '300498.SZ', '300750.SZ', '600000.SH', '600009.SH', '600016.SH',
            '600028.SH', '600030.SH', '600031.SH', '600036.SH', '600048.SH',
            '600050.SH', '600104.SH', '600196.SH', '600276.SH', '600309.SH',
            '600346.SH', '600406.SH', '600436.SH', '600438.SH', '600519.SH',
            '600585.SH', '600588.SH', '600600.SH', '600690.SH', '600745.SH',
            '600809.SH', '600837.SH', '600887.SH', '600893.SH', '600900.SH',
            '601012.SH', '601066.SH', '601088.SH', '601100.SH', '601111.SH',
            '601138.SH', '601166.SH', '601211.SH', '601288.SH', '601318.SH',
            '601336.SH', '601398.SH', '601601.SH', '601628.SH', '601668.SH',
            '601688.SH', '601766.SH', '601857.SH', '601888.SH', '601899.SH',
            '601919.SH', '601933.SH', '601988.SH', '601995.SH', '603259.SH',
            '603288.SH', '603501.SH', '603986.SH', '605117.SH', '688111.SH',
            '688599.SH'
        ]
        return self.stock_pool
    
    def get_stock_data(self, code, start_date, end_date):
        """获取股票数据"""
        cache_key = f"{code}_{start_date}_{end_date}"
        if cache_key in self.stock_data_cache:
            return self.stock_data_cache[cache_key]
        
        cache_file = Path(f"/tmp/portfolio_{code}_{start_date}_{end_date}.csv")
        if cache_file.exists():
            df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            self.stock_data_cache[cache_key] = df
            return df
        
        if TUSHARE_AVAILABLE:
            try:
                pro = ts.pro_api()
                df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
                if not df.empty:
                    df = df.sort_values('trade_date')
                    df.set_index('trade_date', inplace=True)
                    df.index = pd.to_datetime(df.index)
                    df.to_csv(cache_file)
                    self.stock_data_cache[cache_key] = df
                    return df
            except:
                pass
        return None
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        
        # 均线
        for period in [5, 10, 20, 60]:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        
        # 涨跌幅
        df['change_pct'] = df['close'].pct_change() * 100
        
        # 20日新高
        df['high_20'] = df['high'].rolling(window=20).max()
        df['breakout'] = df['close'] >= df['high_20'].shift(1) * 0.98
        
        # 成交量
        df['volume_ma20'] = df['vol'].rolling(window=20).mean()
        df['volume_ratio'] = df['vol'] / df['volume_ma20']
        
        # 趋势评分
        df['trend_score'] = (
            (df['close'] > df['ma5']).astype(int) +
            (df['close'] > df['ma10']).astype(int) +
            (df['close'] > df['ma20']).astype(int) +
            (df['close'] > df['ma60']).astype(int)
        )
        
        # 动量得分 (0-100)
        df['momentum_score'] = (
            df['trend_score'] * 20 +
            df['change_pct'].clip(-10, 10) * 2 +
            (df['volume_ratio'] - 1).clip(0, 5) * 5
        ).clip(0, 100)
        
        return df
    
    def scan_stocks(self, date, lookback_days=60):
        """扫描股票池，返回当前信号股票"""
        signals = []
        
        start_date = (pd.to_datetime(date) - timedelta(days=lookback_days)).strftime('%Y%m%d')
        end_date = date.strftime('%Y%m%d')
        
        for code in self.stock_pool:
            df = self.get_stock_data(code, start_date, end_date)
            if df is None or len(df) < 20:
                continue
            
            df = self.calculate_indicators(df)
            
            if len(df) < 1:
                continue
            
            row = df.iloc[-1]
            
            # 突破信号条件
            is_breakout = (
                row['breakout'] and  # 创20日新高
                row['change_pct'] > 3 and  # 涨3%以上
                row['volume_ratio'] > 1.5 and  # 放量
                row['close'] > row['ma20'] and  # 20日线上
                row['trend_score'] >= 3  # 趋势强势
            )
            
            if is_breakout:
                signals.append({
                    'code': code,
                    'price': row['close'],
                    'change_pct': row['change_pct'],
                    'volume_ratio': row['volume_ratio'],
                    'trend_score': row['trend_score'],
                    'momentum_score': row['momentum_score'],
                    'ma20': row['ma20']
                })
        
        # 按动量得分排序
        signals = sorted(signals, key=lambda x: x['momentum_score'], reverse=True)
        return signals
    
    def should_sell(self, code, current_price, current_date):
        """检查是否应该卖出"""
        if code not in self.positions:
            return False, ''
        
        pos = self.positions[code]
        
        # 止损 -8%
        if current_price <= pos['entry_price'] * 0.92:
            return True, '止损'
        
        # 移动止盈：盈利>30%后回撤10%
        if pos['high_since_entry'] >= pos['entry_price'] * 1.30:
            if current_price <= pos['high_since_entry'] * 0.90:
                return True, '移动止盈'
        
        # 持仓超过60天强制检查
        holding_days = (current_date - pos['entry_date']).days
        if holding_days > 60:
            # 获取最新数据检查趋势
            df = self.get_stock_data(code, 
                (current_date - timedelta(days=30)).strftime('%Y%m%d'),
                current_date.strftime('%Y%m%d'))
            if df is not None and len(df) > 0:
                df = self.calculate_indicators(df)
                last = df.iloc[-1]
                if current_price < last['ma10'] * 0.98:
                    return True, '趋势转弱'
        
        return False, ''
    
    def run_backtest(self, start_date, end_date):
        """运行回测"""
        print(f"\n{'='*70}")
        print(f"🚀 组合轮动策略回测")
        print(f"📅 {start_date} ~ {end_date}")
        print(f"💰 初始资金: ¥{self.initial_capital:,.0f}")
        print(f"📊 股票池: {len(self.build_stock_pool())}只")
        print(f"{'='*70}")
        
        # 生成交易日列表
        date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # 工作日
        
        for i, date in enumerate(date_range):
            date_str = date.strftime('%Y%m%d')
            
            # 更新持仓市值和检查卖出
            positions_to_sell = []
            total_position_value = 0
            
            for code in list(self.positions.keys()):
                df = self.get_stock_data(code,
                    (date - timedelta(days=5)).strftime('%Y%m%d'),
                    date_str)
                
                if df is not None and len(df) > 0:
                    current_price = df.iloc[-1]['close']
                    pos = self.positions[code]
                    
                    # 更新最高价
                    if current_price > pos['high_since_entry']:
                        pos['high_since_entry'] = current_price
                    
                    # 检查卖出
                    should_exit, exit_reason = self.should_sell(code, current_price, date)
                    if should_exit:
                        positions_to_sell.append((code, current_price, exit_reason))
                    else:
                        total_position_value += pos['shares'] * current_price
            
            # 执行卖出
            for code, price, reason in positions_to_sell:
                pos = self.positions[code]
                shares = pos['shares']
                proceeds = shares * price * 0.9995
                pnl = proceeds - pos['cost_basis']
                pnl_pct = pnl / pos['cost_basis'] * 100
                holding_days = (date - pos['entry_date']).days
                
                self.cash += proceeds
                del self.positions[code]
                
                self.trades.append({
                    'date': date_str,
                    'action': 'SELL',
                    'code': code,
                    'price': price,
                    'shares': shares,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'holding_days': holding_days,
                    'reason': reason
                })
                
                emoji = "🚀" if pnl_pct > 20 else ("✅" if pnl > 0 else "❌")
                print(f"📉 SELL {date_str} {code} ¥{price:.2f} [{reason}] {emoji} {pnl_pct:+.1f}% ({holding_days}天)")
            
            # 每周一扫描新机会（或空仓时）
            if date.weekday() == 0 or len(self.positions) < self.max_positions:
                available_slots = self.max_positions - len(self.positions)
                
                if available_slots > 0 and self.cash > self.initial_capital * 0.2:
                    signals = self.scan_stocks(date)
                    
                    # 过滤已持有的
                    signals = [s for s in signals if s['code'] not in self.positions]
                    
                    # 取前N个信号
                    for signal in signals[:available_slots]:
                        code = signal['code']
                        price = signal['price']
                        
                        # 每只仓位20%
                        position_value = self.initial_capital * 0.20
                        shares = int(position_value / price / 100) * 100
                        
                        if shares > 0:
                            cost = shares * price * 1.0005
                            if cost <= self.cash * 0.95:  # 留点余地
                                self.cash -= cost
                                self.positions[code] = {
                                    'shares': shares,
                                    'cost_basis': cost,
                                    'entry_price': price,
                                    'high_since_entry': price,
                                    'entry_date': date
                                }
                                
                                self.trades.append({
                                    'date': date_str,
                                    'action': 'BUY',
                                    'code': code,
                                    'price': price,
                                    'shares': shares,
                                    'momentum_score': signal['momentum_score']
                                })
                                
                                print(f"📈 BUY  {date_str} {code} ¥{price:.2f} x{shares} (动量{signal['momentum_score']:.0f})")
            
            # 记录每日统计
            total_value = self.cash + total_position_value
            self.daily_stats.append({
                'date': date,
                'cash': self.cash,
                'position_value': total_position_value,
                'total_value': total_value,
                'positions_count': len(self.positions)
            })
            
            # 每月输出一次状态
            if i % 22 == 0 and i > 0:
                print(f"   [{date_str}] 总资产: ¥{total_value:,.0f} (+{(total_value/self.initial_capital-1)*100:+.1f}%) 持仓{len(self.positions)}只")
        
        return self.generate_report(start_date, end_date)
    
    def generate_report(self, start_date, end_date):
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
        completed_trades = [t for t in self.trades if t['action'] == 'SELL']
        
        if completed_trades:
            winning_trades = [t for t in completed_trades if t['pnl'] > 0]
            big_wins = [t for t in winning_trades if t['pnl_pct'] > 20]
            
            win_rate = len(winning_trades) / len(completed_trades)
            avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['pnl'] for t in completed_trades if t['pnl'] <= 0]) if [t for t in completed_trades if t['pnl'] <= 0] else 0
            avg_holding = np.mean([t['holding_days'] for t in completed_trades])
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        else:
            win_rate = avg_win = avg_loss = avg_holding = profit_factor = 0
            winning_trades = big_wins = []
        
        # 最大回撤
        cummax = df_stats['total_value'].cummax()
        drawdown = (df_stats['total_value'] - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 夏普比率
        daily_returns = df_stats['total_value'].pct_change().dropna()
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        
        # 年化波动率
        volatility = np.std(daily_returns) * np.sqrt(252) * 100
        
        report = {
            'strategy': '组合轮动策略',
            'start_date': start_date,
            'end_date': end_date,
            'years': years,
            'initial_capital': initial,
            'final_capital': final,
            'total_return_pct': total_return * 100,
            'annual_return_pct': annual_return * 100,
            'volatility_pct': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_drawdown * 100,
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'big_wins': len(big_wins),
            'win_rate': win_rate * 100,
            'profit_factor': profit_factor,
            'avg_holding_days': avg_holding,
            'max_positions': self.max_positions,
            'stock_pool_size': len(self.stock_pool)
        }
        
        print(f"\n{'='*70}")
        print(f"📊 组合轮动策略回测报告 ({years:.1f}年)")
        print(f"{'='*70}")
        print(f"初始资金: ¥{initial:,.0f}")
        print(f"最终资金: ¥{final:,.0f}")
        print(f"总收益率: {total_return*100:+.2f}%")
        print(f"年化收益率: {annual_return*100:+.2f}%")
        print(f"年化波动率: {volatility:.1f}%")
        print(f"夏普比率: {sharpe:.2f}")
        print(f"最大回撤: {max_drawdown*100:.1f}%")
        print(f"\n交易统计:")
        print(f"  总交易: {len(completed_trades)}次")
        print(f"  盈利次数: {len(winning_trades)}次 (胜率{win_rate*100:.0f}%)")
        print(f"  大赚(>20%): {len(big_wins)}次")
        print(f"  盈亏比: {profit_factor:.1f}")
        print(f"  平均持仓: {avg_holding:.0f}天")
        print(f"\n组合配置:")
        print(f"  股票池: {len(self.stock_pool)}只")
        print(f"  最大持仓: {self.max_positions}只")
        print(f"  单只仓位: 20%")
        
        return report


if __name__ == '__main__':
    # 运行10年回测
    strategy = PortfolioRotationStrategy(initial_capital=1000000, max_positions=5)
    
    result = strategy.run_backtest('2015-01-01', '2024-12-31')
    
    if result:
        # 保存结果
        output = '/workspace/projects/workspace/data/backtest_results/portfolio_rotation_10year.json'
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 结果已保存: {output}")
