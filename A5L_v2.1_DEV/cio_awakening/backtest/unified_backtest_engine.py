#!/usr/bin/env python3
"""
A5L Unified Backtest Engine v2.0
统一回测引擎 - 支持15年历史数据回测

特性:
1. Tushare真实历史数据
2. 多策略支持
3. 完整性能指标
4. 可视化报告
"""
import tushare as ts
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# 设置Tushare
TUSHARE_TOKEN = "fd24d18cd957a2feb18629058771772d8820c244719d67fca7d7d73b"
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

@dataclass
class Trade:
    """交易记录"""
    date: str
    action: str  # BUY/SELL
    code: str
    price: float
    shares: int
    amount: float
    pnl: float = 0.0
    pnl_pct: float = 0.0

@dataclass
class BacktestResult:
    """回测结果"""
    strategy_name: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    annual_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    volatility: float
    trades: List[Dict]
    equity_curve: List[Dict]

class UnifiedBacktestEngine:
    """统一回测引擎"""
    
    def __init__(self, data_path: str = None):
        self.workspace = "/workspace/projects/workspace"
        self.data_path = data_path or f"{self.workspace}/A5L_v2.1_DEV/cio_awakening/data/historical/1d_price_fresh"
        self.results_dir = f"{self.workspace}/data/backtest_results"
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        
        # 缓存数据
        self.price_cache = {}
        
    def get_stock_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票历史数据 (优先本地，其次Tushare)"""
        cache_key = f"{code}_{start_date}_{end_date}"
        
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]
        
        # 尝试从本地加载
        all_data = []
        for date_file in Path(self.data_path).glob("*.parquet"):
            date_str = date_file.stem
            if start_date <= date_str <= end_date:
                df = pd.read_parquet(date_file)
                stock_df = df[df['code'] == code]
                if not stock_df.empty:
                    all_data.append(stock_df)
        
        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            result = result.sort_values('date')
        else:
            # 从Tushare获取
            result = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
            if result is not None and not result.empty:
                result = result.rename(columns={
                    'ts_code': 'code',
                    'trade_date': 'date'
                })
                result = result.sort_values('date')
        
        self.price_cache[cache_key] = result
        return result
    
    def run_backtest(self, 
                     strategy_func,
                     symbols: List[str],
                     start_date: str,
                     end_date: str,
                     initial_capital: float = 1000000.0,
                     strategy_name: str = "unnamed_strategy") -> BacktestResult:
        """
        运行回测
        
        Args:
            strategy_func: 策略函数 (df, current_date, position) -> action, shares
            symbols: 股票列表
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            initial_capital: 初始资金
            strategy_name: 策略名称
        
        Returns:
            BacktestResult
        """
        print(f"\n{'='*70}")
        print(f"🚀 开始回测: {strategy_name}")
        print(f"📅 时间范围: {start_date} - {end_date}")
        print(f"💰 初始资金: ¥{initial_capital:,.2f}")
        print(f"📊 标的数量: {len(symbols)}")
        print(f"{'='*70}\n")
        
        # 获取交易日历
        trade_dates = self._get_trade_dates(start_date, end_date)
        
        # 初始化
        capital = initial_capital
        positions = {}  # {code: {'shares': x, 'cost': y}}
        trades = []
        equity_curve = []
        
        for i, date in enumerate(trade_dates):
            # 记录权益曲线
            total_value = capital
            for code, pos in positions.items():
                price = self._get_price(code, date)
                if price > 0:
                    total_value += pos['shares'] * price
            
            equity_curve.append({
                'date': date,
                'total_value': total_value,
                'cash': capital,
                'positions_value': total_value - capital
            })
            
            # 对每个股票执行策略
            for code in symbols:
                try:
                    # 获取股票数据到当前日期
                    df = self.get_stock_data(code, start_date, date)
                    if df.empty:
                        continue
                    
                    # 执行策略
                    current_position = positions.get(code, {'shares': 0, 'cost': 0})
                    action, shares = strategy_func(df, date, current_position, capital)
                    
                    # 执行交易
                    if action == "BUY" and shares > 0:
                        price = self._get_price(code, date)
                        cost = shares * price
                        if cost <= capital:
                            capital -= cost
                            if code in positions:
                                positions[code]['shares'] += shares
                                positions[code]['cost'] += cost
                            else:
                                positions[code] = {'shares': shares, 'cost': cost}
                            
                            trades.append(Trade(
                                date=date, action="BUY", code=code,
                                price=price, shares=shares, amount=cost
                            ))
                    
                    elif action == "SELL" and code in positions and positions[code]['shares'] > 0:
                        price = self._get_price(code, date)
                        sell_shares = min(shares, positions[code]['shares'])
                        revenue = sell_shares * price
                        
                        # 计算盈亏
                        avg_cost = positions[code]['cost'] / positions[code]['shares']
                        pnl = (price - avg_cost) * sell_shares
                        pnl_pct = (price - avg_cost) / avg_cost * 100
                        
                        capital += revenue
                        positions[code]['shares'] -= sell_shares
                        positions[code]['cost'] -= avg_cost * sell_shares
                        
                        if positions[code]['shares'] == 0:
                            del positions[code]
                        
                        trades.append(Trade(
                            date=date, action="SELL", code=code,
                            price=price, shares=sell_shares, amount=revenue,
                            pnl=pnl, pnl_pct=pnl_pct
                        ))
                
                except Exception as e:
                    print(f"  ⚠️ {code} {date} 处理失败: {e}")
            
            # 进度显示
            if (i + 1) % 50 == 0:
                print(f"  📊 进度: {i+1}/{len(trade_dates)} 天, 当前净值: ¥{total_value:,.2f}")
        
        # 计算最终市值
        final_value = capital
        for code, pos in positions.items():
            price = self._get_price(code, trade_dates[-1])
            if price > 0:
                final_value += pos['shares'] * price
        
        # 计算性能指标
        metrics = self._calculate_metrics(
            initial_capital, final_value, trades, equity_curve, trade_dates
        )
        
        # 创建结果
        result = BacktestResult(
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_capital=final_value,
            total_return=metrics['total_return'],
            total_return_pct=metrics['total_return_pct'],
            annual_return=metrics['annual_return'],
            total_trades=metrics['total_trades'],
            winning_trades=metrics['winning_trades'],
            losing_trades=metrics['losing_trades'],
            win_rate=metrics['win_rate'],
            avg_win=metrics['avg_win'],
            avg_loss=metrics['avg_loss'],
            profit_factor=metrics['profit_factor'],
            max_drawdown=metrics['max_drawdown'],
            max_drawdown_pct=metrics['max_drawdown_pct'],
            sharpe_ratio=metrics['sharpe_ratio'],
            volatility=metrics['volatility'],
            trades=[asdict(t) for t in trades],
            equity_curve=equity_curve
        )
        
        # 保存结果
        self._save_result(result)
        
        # 打印报告
        self._print_report(result)
        
        return result
    
    def _get_trade_dates(self, start_date: str, end_date: str) -> List[str]:
        """获取交易日历"""
        df = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
        return df[df['is_open'] == 1]['cal_date'].tolist()
    
    def _get_price(self, code: str, date: str) -> float:
        """获取指定日期收盘价"""
        try:
            df = self.get_stock_data(code, date, date)
            if not df.empty:
                return float(df.iloc[0]['close'])
        except:
            pass
        return 0.0
    
    def _calculate_metrics(self, initial: float, final: float, 
                          trades: List[Trade], equity_curve: List[Dict],
                          trade_dates: List[str]) -> Dict:
        """计算性能指标"""
        # 基础收益
        total_return = (final - initial) / initial
        total_return_pct = total_return * 100
        
        # 年化收益
        days = len(trade_dates)
        years = days / 252
        annual_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        
        # 交易统计
        sell_trades = [t for t in trades if t.action == "SELL"]
        total_trades = len(sell_trades)
        winning_trades = len([t for t in sell_trades if t.pnl > 0])
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 盈亏统计
        wins = [t.pnl for t in sell_trades if t.pnl > 0]
        losses = [abs(t.pnl) for t in sell_trades if t.pnl < 0]
        
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        profit_factor = sum(wins) / sum(losses) if sum(losses) > 0 else float('inf')
        
        # 最大回撤
        values = [e['total_value'] for e in equity_curve]
        peak = values[0]
        max_drawdown = 0
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # 夏普比率 (简化)
        returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values))]
        if returns:
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            volatility = np.std(returns) * np.sqrt(252)
        else:
            sharpe_ratio = 0
            volatility = 0
        
        return {
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'annual_return': annual_return * 100,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown * initial,
            'max_drawdown_pct': max_drawdown * 100,
            'sharpe_ratio': sharpe_ratio,
            'volatility': volatility * 100
        }
    
    def _save_result(self, result: BacktestResult):
        """保存回测结果"""
        filename = f"{result.strategy_name}_{result.start_date}_{result.end_date}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 结果已保存: {filepath}")
    
    def _print_report(self, result: BacktestResult):
        """打印回测报告"""
        print(f"\n{'='*70}")
        print(f"📊 回测报告: {result.strategy_name}")
        print(f"{'='*70}")
        print(f"📅 时间范围: {result.start_date} - {result.end_date}")
        print(f"{'='*70}")
        
        print(f"\n💰 收益指标")
        print(f"  初始资金:     ¥{result.initial_capital:>15,.2f}")
        print(f"  最终资金:     ¥{result.final_capital:>15,.2f}")
        print(f"  总收益率:     {result.total_return_pct:>15.2f}%")
        print(f"  年化收益:     {result.annual_return:>15.2f}%")
        
        print(f"\n📈 交易统计")
        print(f"  总交易次数:   {result.total_trades:>15}")
        print(f"  盈利次数:     {result.winning_trades:>15}")
        print(f"  亏损次数:     {result.losing_trades:>15}")
        print(f"  胜率:         {result.win_rate:>15.2f}%")
        print(f"  平均盈利:     ¥{result.avg_win:>15,.2f}")
        print(f"  平均亏损:     ¥{result.avg_loss:>15,.2f}")
        print(f"  盈亏比:       {result.profit_factor:>15.2f}")
        
        print(f"\n⚠️ 风险指标")
        print(f"  最大回撤:     ¥{result.max_drawdown:>15,.2f}")
        print(f"  最大回撤率:   {result.max_drawdown_pct:>15.2f}%")
        print(f"  夏普比率:     {result.sharpe_ratio:>15.2f}")
        print(f"  波动率:       {result.volatility:>15.2f}%")
        
        print(f"\n{'='*70}")


# ==================== 示例策略 ====================

def example_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float) -> Tuple[str, int]:
    """
    示例策略: 双均线交叉
    
    Returns:
        (action, shares) - action: BUY/SELL/HOLD, shares: 交易数量
    """
    if len(df) < 20:
        return "HOLD", 0
    
    # 计算均线
    df = df.copy()
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    
    current = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else current
    
    # 金叉买入
    if current['ma5'] > current['ma20'] and prev['ma5'] <= prev['ma20']:
        if position['shares'] == 0:
            # 全仓买入
            shares = int(capital / current['close'] / 100) * 100
            return "BUY", shares
    
    # 死叉卖出
    elif current['ma5'] < current['ma20'] and prev['ma5'] >= prev['ma20']:
        if position['shares'] > 0:
            return "SELL", position['shares']
    
    return "HOLD", 0


def momentum_strategy(df: pd.DataFrame, date: str, position: Dict, capital: float) -> Tuple[str, int]:
    """
    动量策略: 5日涨幅前10%
    """
    if len(df) < 5:
        return "HOLD", 0
    
    # 计算5日涨幅
    current_price = df.iloc[-1]['close']
    price_5d_ago = df.iloc[-5]['close']
    momentum = (current_price - price_5d_ago) / price_5d_ago
    
    # 动量 > 5% 买入
    if momentum > 0.05 and position['shares'] == 0:
        shares = int(capital / current_price / 100) * 100
        return "BUY", shares
    
    # 动量 < 0 卖出
    elif momentum < 0 and position['shares'] > 0:
        return "SELL", position['shares']
    
    return "HOLD", 0


if __name__ == "__main__":
    # 创建回测引擎
    engine = UnifiedBacktestEngine()
    
    # 运行回测示例
    symbols = ["000001.SZ", "000002.SZ", "600519.SH"]  # 平安银行、万科、茅台
    
    result = engine.run_backtest(
        strategy_func=example_strategy,
        symbols=symbols,
        start_date="20250101",
        end_date="20260508",
        initial_capital=1000000.0,
        strategy_name="双均线策略"
    )
