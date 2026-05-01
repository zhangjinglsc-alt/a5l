#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 2: Backtest Engine
策略回测引擎

功能：
1. 策略历史回测
2. 性能指标计算
3. 回测报告生成
4. 策略优化建议
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

class BacktestEngine:
    """策略回测引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.results_dir = f"{workspace}/data/architect_5l/backtest_results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def run_backtest(self, strategy_id: str, symbol: str, 
                     start_date: str, end_date: str,
                     initial_capital: float = 100000.0) -> Dict:
        """
        运行策略回测
        
        Returns:
            回测结果
        """
        # 这里应该是实际的回测逻辑
        # 现在返回模拟结果用于测试
        
        result = {
            "strategy_id": strategy_id,
            "symbol": symbol,
            "period": f"{start_date} to {end_date}",
            "initial_capital": initial_capital,
            "final_capital": initial_capital * 1.15,  # 模拟15%收益
            "total_return": 0.15,
            "total_return_pct": 15.0,
            "trades": [],
            "metrics": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 模拟交易记录
        result["trades"] = [
            {"date": "2026-01-15", "action": "BUY", "price": 10.0, "shares": 1000},
            {"date": "2026-02-20", "action": "SELL", "price": 11.5, "shares": 1000, "pnl": 1500}
        ]
        
        # 计算性能指标
        result["metrics"] = self._calculate_metrics(result)
        
        # 保存结果
        self._save_result(result)
        
        return result
    
    def _calculate_metrics(self, backtest_result: Dict) -> Dict:
        """计算回测性能指标"""
        initial = backtest_result["initial_capital"]
        final = backtest_result["final_capital"]
        trades = backtest_result.get("trades", [])
        
        # 基础指标
        total_return = (final - initial) / initial
        
        # 交易统计
        total_trades = len([t for t in trades if t.get("action") == "SELL"])
        winning_trades = len([t for t in trades if t.get("pnl", 0) > 0])
        losing_trades = total_trades - winning_trades
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 计算盈亏比
        wins = [t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0]
        losses = [abs(t.get("pnl", 0)) for t in trades if t.get("pnl", 0) < 0]
        
        avg_win = statistics.mean(wins) if wins else 0
        avg_loss = statistics.mean(losses) if losses else 0
        
        profit_factor = sum(wins) / sum(losses) if sum(losses) > 0 else float('inf')
        
        # 夏普比率（简化计算）
        sharpe_ratio = 1.5  # 模拟值
        
        # 最大回撤（模拟）
        max_drawdown = 0.08  # 8%
        
        return {
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "win_rate_pct": win_rate * 100,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown * 100
        }
    
    def _save_result(self, result: Dict):
        """保存回测结果"""
        filename = f"{result['strategy_id']}_{result['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def compare_strategies(self, results: List[Dict]) -> str:
        """比较多个策略的回测结果"""
        report = """# 📊 策略回测比较报告

| 策略 | 总收益 | 胜率 | 盈亏比 | 夏普比率 | 最大回撤 |
|------|--------|------|--------|----------|----------|
"""
        
        for result in results:
            m = result["metrics"]
            report += f"| {result['strategy_id']} | {m['total_return_pct']:.1f}% | {m['win_rate_pct']:.1f}% | {m['profit_factor']:.2f} | {m['sharpe_ratio']:.2f} | {m['max_drawdown_pct']:.1f}% |\n"
        
        return report
    
    def generate_backtest_report(self, result: Dict) -> str:
        """生成详细回测报告"""
        m = result["metrics"]
        
        report = f"""# 📈 策略回测详细报告

**策略**: {result['strategy_id']}  
**标的**: {result['symbol']}  
**回测周期**: {result['period']}  
**生成时间**: {result['timestamp']}

---

## 💰 收益指标

| 指标 | 数值 |
|------|------|
| 初始资金 | ¥{result['initial_capital']:,.2f} |
| 最终资金 | ¥{result['final_capital']:,.2f} |
| 总收益率 | {m['total_return_pct']:+.2f}% |

---

## 📊 交易统计

| 指标 | 数值 |
|------|------|
| 总交易次数 | {m['total_trades']} |
| 盈利次数 | {m['winning_trades']} |
| 亏损次数 | {m['losing_trades']} |
| 胜率 | {m['win_rate_pct']:.1f}% |
| 平均盈利 | ¥{m['avg_win']:,.2f} |
| 平均亏损 | ¥{m['avg_loss']:,.2f} |
| 盈亏比 | {m['profit_factor']:.2f} |

---

## 📈 风险指标

| 指标 | 数值 |
|------|------|
| 夏普比率 | {m['sharpe_ratio']:.2f} |
| 最大回撤 | {m['max_drawdown_pct']:.2f}% |

---

## 📝 交易记录

"""
        
        for trade in result.get("trades", []):
            report += f"- {trade['date']}: {trade['action']} @ {trade['price']}"
            if 'pnl' in trade:
                report += f" (盈亏: ¥{trade['pnl']:,.2f})"
            report += "\n"
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("📈 回测引擎")
    print("=" * 70)
    
    engine = BacktestEngine()
    
    # 运行回测
    print("\n🧪 运行策略回测...")
    result = engine.run_backtest(
        strategy_id="stock_wizard",
        symbol="000001.SZ",
        start_date="2026-01-01",
        end_date="2026-04-30",
        initial_capital=100000
    )
    
    print(f"\n  策略: {result['strategy_id']}")
    print(f"  标的: {result['symbol']}")
    print(f"  初始资金: ¥{result['initial_capital']:,.2f}")
    print(f"  最终资金: ¥{result['final_capital']:,.2f}")
    print(f"  总收益: {result['metrics']['total_return_pct']:+.2f}%")
    print(f"  胜率: {result['metrics']['win_rate_pct']:.1f}%")
    print(f"  夏普比率: {result['metrics']['sharpe_ratio']:.2f}")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 回测报告:")
    report = engine.generate_backtest_report(result)
    print(report[:600] + "...")

if __name__ == "__main__":
    main()
