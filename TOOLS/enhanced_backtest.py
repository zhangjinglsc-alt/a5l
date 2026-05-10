#!/usr/bin/env python3
"""
增强版策略回测 - 多维度改进
结合趋势过滤 + 多因子选股 + 动态止损
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加tushare支持
try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("⚠️ Tushare未安装，使用模拟数据")

class EnhancedBacktestEngine:
    """增强版回测引擎"""
    
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {code: {'shares': x, 'cost': y, 'high_since_entry': z}}
        self.trades = []
        self.daily_stats = []
        
    def get_stock_data(self, code, start_date, end_date):
        """获取股票历史数据"""
        # 尝试从本地加载
        cache_file = Path(f"/tmp/stock_data_{code}_{start_date}_{end_date}.csv")
        if cache_file.exists():
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        # 使用tushare获取数据
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
        
        # 均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        
        # 趋势判断（价格与60日均线关系）
        df['trend'] = np.where(df['close'] > df['ma60'], 1, 
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
        
        # 波动率（20日）
        df['volatility'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
        
        # ATR (平均真实波幅)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        # 成交量指标
        df['volume_ma20'] = df['vol'].rolling(window=20).mean()
        df['volume_ratio'] = df['vol'] / df['volume_ma20']
        
        return df
    
    def trend_filter_strategy(self, df, i):
        """
        趋势过滤策略
        只在上升趋势中做多，下跌趋势中空仓
        """
        if i < 60:  # 需要足够数据
            return 'HOLD'
        
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        # 趋势判断
        trend_up = row['close'] > row['ma60'] and row['ma20'] > row['ma60']
        trend_down = row['close'] < row['ma60'] * 0.97
        
        # 买入信号：趋势向上 + 金叉 + RSI不过热 + 成交量放大
        buy_signal = (
            trend_up and
            prev_row['ma5'] <= prev_row['ma10'] and  # 前一天未金叉
            row['ma5'] > row['ma10'] and  # 当天金叉
            row['rsi'] < 70 and  # RSI不过热
            row['volume_ratio'] > 1.2  # 成交量放大
        )
        
        # 卖出信号：趋势转弱 或 死叉 或 RSI超买
        sell_signal = (
            trend_down or
            (prev_row['ma5'] >= prev_row['ma10'] and row['ma5'] < row['ma10']) or
            row['rsi'] > 80
        )
        
        if buy_signal:
            return 'BUY'
        elif sell_signal:
            return 'SELL'
        return 'HOLD'
    
    def run_backtest(self, code, start_date, end_date, strategy_name='trend_filter'):
        """运行回测"""
        print(f"\n{'='*60}")
        print(f"回测: {code} | {start_date} ~ {end_date}")
        print(f"策略: {strategy_name}")
        print(f"{'='*60}")
        
        # 获取数据
        df = self.get_stock_data(code, start_date, end_date)
        if df is None or df.empty:
            print(f"❌ 无法获取{code}数据")
            return None
        
        # 计算指标
        df = self.calculate_indicators(df)
        df = df.dropna()
        
        if len(df) < 60:
            print(f"❌ 数据不足: {len(df)}条")
            return None
        
        # 回测循环
        for i in range(len(df)):
            date = df.index[i]
            price = df.iloc[i]['close']
            code_clean = code.replace('.SZ', '').replace('.SH', '')
            
            # 获取信号
            signal = self.trend_filter_strategy(df, i)
            
            # 检查持仓止损
            if code_clean in self.positions:
                pos = self.positions[code_clean]
                # 更新最高价
                if price > pos['high_since_entry']:
                    pos['high_since_entry'] = price
                
                # 移动止损：从最高点回撤8%
                trailing_stop_price = pos['high_since_entry'] * 0.92
                # 固定止损：成本价下跌7%
                hard_stop_price = pos['cost'] * 0.93
                stop_price = max(trailing_stop_price, hard_stop_price)
                
                if price <= stop_price:
                    signal = 'SELL'
                    stop_type = 'trailing' if trailing_stop_price > hard_stop_price else 'hard'
            
            # 执行交易
            if signal == 'BUY' and code_clean not in self.positions:
                # 计算仓位（根据波动率调整）
                volatility = df.iloc[i]['volatility'] if not pd.isna(df.iloc[i]['volatility']) else 0.02
                position_size = min(0.3, 0.15 / (volatility * 10 + 0.01))  # 波动越大，仓位越小
                invest_amount = self.cash * position_size
                shares = int(invest_amount / price / 100) * 100  # 整手
                
                if shares > 0:
                    cost = shares * price * 1.0005  # 加佣金
                    if cost <= self.cash:
                        self.cash -= cost
                        self.positions[code_clean] = {
                            'shares': shares,
                            'cost': cost,
                            'entry_price': price,
                            'high_since_entry': price,
                            'entry_date': date
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
                        print(f"  📈 BUY {date.strftime('%Y-%m-%d')} {code} @ {price:.2f} x{shares}")
            
            elif signal == 'SELL' and code_clean in self.positions:
                pos = self.positions[code_clean]
                shares = pos['shares']
                proceeds = shares * price * 0.9995  # 减佣金和印花税
                pnl = proceeds - pos['cost']
                pnl_pct = pnl / pos['cost'] * 100
                
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
                    'cash_after': self.cash
                })
                
                emoji = "✅" if pnl > 0 else "❌"
                print(f"  📉 SELL {date.strftime('%Y-%m-%d')} {code} @ {price:.2f} x{shares} | {emoji} PnL: {pnl:,.0f} ({pnl_pct:+.2f}%)")
            
            # 记录每日统计
            position_value = sum(
                pos['shares'] * df.iloc[i]['close'] 
                for code_key, pos in self.positions.items()
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
        
        return self.generate_report()
    
    def generate_report(self):
        """生成回测报告"""
        if not self.daily_stats:
            return None
        
        df_stats = pd.DataFrame(self.daily_stats)
        
        # 基础指标
        initial = self.initial_capital
        final = df_stats['total_value'].iloc[-1]
        total_return = (final - initial) / initial
        
        # 年化收益
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
                    'holding_days': (pd.to_datetime(t['date']) - pd.to_datetime(entry['date'])).days
                })
                entry = None
        
        if completed_trades:
            winning_trades = [t for t in completed_trades if t['pnl'] > 0]
            win_rate = len(winning_trades) / len(completed_trades)
            avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
            losing_trades = [t for t in completed_trades if t['pnl'] <= 0]
            avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        else:
            win_rate = 0
            avg_win = avg_loss = 0
        
        # 最大回撤
        cummax = df_stats['total_value'].cummax()
        drawdown = (df_stats['total_value'] - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 夏普比率（简化）
        daily_returns = df_stats['total_value'].pct_change().dropna()
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        
        report = {
            'strategy_name': '趋势过滤+动态止损',
            'initial_capital': initial,
            'final_capital': final,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'annual_return': annual_return,
            'annual_return_pct': annual_return * 100,
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades) if completed_trades else 0,
            'losing_trades': len(losing_trades) if completed_trades else 0,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'sharpe_ratio': sharpe,
            'trades': self.trades
        }
        
        # 打印报告
        print(f"\n{'='*60}")
        print("📊 回测报告")
        print(f"{'='*60}")
        print(f"初始资金: ¥{initial:,.0f}")
        print(f"最终资金: ¥{final:,.0f}")
        print(f"总收益: {total_return*100:+.2f}%")
        print(f"年化收益: {annual_return*100:+.2f}%")
        print(f"总交易: {len(completed_trades)}次")
        print(f"胜率: {win_rate*100:.1f}%")
        print(f"最大回撤: {max_drawdown*100:.1f}%")
        print(f"夏普比率: {sharpe:.2f}")
        
        return report


if __name__ == '__main__':
    engine = EnhancedBacktestEngine(initial_capital=1000000)
    
    # 测试多只股票
    test_stocks = [
        ('000001.SZ', '2020-01-01', '2024-01-01'),  # 平安银行
        ('000858.SZ', '2020-01-01', '2024-01-01'),  # 五粮液
        ('600519.SH', '2020-01-01', '2024-01-01'),  # 茅台
    ]
    
    results = []
    for code, start, end in test_stocks:
        result = engine.run_backtest(code, start, end)
        if result:
            results.append(result)
        # 重置资金
        engine.cash = engine.initial_capital
        engine.positions = {}
        engine.trades = []
        engine.daily_stats = []
    
    # 保存结果
    output_file = '/workspace/projects/workspace/data/backtest_results/enhanced_strategy_results.json'
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 结果已保存: {output_file}")
