#!/usr/bin/env python3
"""
A5L Backtest Analysis & Visualization
回测结果分析与可视化
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

class BacktestAnalyzer:
    """回测结果分析器"""
    
    def __init__(self, results_dir: str = None):
        self.workspace = "/workspace/projects/workspace"
        self.results_dir = results_dir or f"{self.workspace}/data/backtest_results"
        
    def analyze_result(self, result_file: str) -> dict:
        """分析单个回测结果"""
        with open(result_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        analysis = {
            'strategy_name': result['strategy_name'],
            'period': f"{result['start_date']} - {result['end_date']}",
            'profitability': self._analyze_profitability(result),
            'risk': self._analyze_risk(result),
            'trading': self._analyze_trading(result),
            'score': self._calculate_score(result)
        }
        
        return analysis
    
    def _analyze_profitability(self, result: dict) -> dict:
        """盈利能力分析"""
        return {
            'total_return': result['total_return_pct'],
            'annual_return': result['annual_return'],
            'sharpe_ratio': result['sharpe_ratio'],
            'profit_score': min(result['sharpe_ratio'] * 20, 100)  # 夏普比率评分
        }
    
    def _analyze_risk(self, result: dict) -> dict:
        """风险分析"""
        return {
            'max_drawdown': result['max_drawdown_pct'],
            'volatility': result['volatility'],
            'risk_score': max(0, 100 - result['max_drawdown_pct'] * 2)  # 回撤评分
        }
    
    def _analyze_trading(self, result: dict) -> dict:
        """交易分析"""
        return {
            'total_trades': result['total_trades'],
            'win_rate': result['win_rate'],
            'profit_factor': result['profit_factor'],
            'trading_score': result['win_rate'] * result['profit_factor'] / 10
        }
    
    def _calculate_score(self, result: dict) -> float:
        """计算综合评分"""
        # 权重: 收益40% + 风险30% + 交易30%
        profit_score = min(result['sharpe_ratio'] * 20, 100) * 0.4
        risk_score = max(0, 100 - result['max_drawdown_pct'] * 2) * 0.3
        trading_score = result['win_rate'] * result['profit_factor'] / 10 * 0.3
        
        return profit_score + risk_score + trading_score
    
    def compare_strategies(self, result_files: list) -> pd.DataFrame:
        """对比多个策略"""
        comparisons = []
        
        for file in result_files:
            analysis = self.analyze_result(file)
            comparisons.append({
                '策略名称': analysis['strategy_name'],
                '时间范围': analysis['period'],
                '总收益': f"{analysis['profitability']['total_return']:.2f}%",
                '年化收益': f"{analysis['profitability']['annual_return']:.2f}%",
                '夏普比率': f"{analysis['profitability']['sharpe_ratio']:.2f}",
                '最大回撤': f"{analysis['risk']['max_drawdown']:.2f}%",
                '胜率': f"{analysis['trading']['win_rate']:.2f}%",
                '盈亏比': f"{analysis['trading']['profit_factor']:.2f}",
                '综合评分': f"{analysis['score']:.2f}"
            })
        
        return pd.DataFrame(comparisons)
    
    def generate_html_report(self, result_file: str, output_file: str = None):
        """生成HTML可视化报告"""
        with open(result_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        # 生成权益曲线数据
        equity_data = result.get('equity_curve', [])
        dates = [e['date'] for e in equity_data]
        values = [e['total_value'] for e in equity_data]
        
        # 计算回撤曲线
        peak = values[0]
        drawdowns = []
        for v in values:
            if v > peak:
                peak = v
            drawdowns.append((peak - v) / peak * 100)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>回测报告 - {result['strategy_name']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
        .positive {{ color: #22c55e; }}
        .negative {{ color: #ef4444; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .trades-table {{ background: white; padding: 20px; border-radius: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 回测报告: {result['strategy_name']}</h1>
            <p>时间范围: {result['start_date']} - {result['end_date']}</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value {'positive' if result['total_return_pct'] > 0 else 'negative'}">
                    {result['total_return_pct']:.2f}%
                </div>
                <div class="metric-label">总收益率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result['annual_return']:.2f}%</div>
                <div class="metric-label">年化收益</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result['sharpe_ratio']:.2f}</div>
                <div class="metric-label">夏普比率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value negative">{result['max_drawdown_pct']:.2f}%</div>
                <div class="metric-label">最大回撤</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result['win_rate']:.2f}%</div>
                <div class="metric-label">胜率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result['profit_factor']:.2f}</div>
                <div class="metric-label">盈亏比</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result['total_trades']}</div>
                <div class="metric-label">交易次数</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{result['volatility']:.2f}%</div>
                <div class="metric-label">波动率</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📈 权益曲线</h2>
            <canvas id="equityChart" height="100"></canvas>
        </div>
        
        <div class="chart-container">
            <h2>📉 回撤曲线</h2>
            <canvas id="drawdownChart" height="100"></canvas>
        </div>
    </div>
    
    <script>
        // 权益曲线
        new Chart(document.getElementById('equityChart'), {{
            type: 'line',
            data: {{
                labels: {dates},
                datasets: [{{
                    label: '总资产',
                    data: {values},
                    borderColor: 'rgb(99, 102, 241)',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ beginAtZero: false }} }}
            }}
        }});
        
        // 回撤曲线
        new Chart(document.getElementById('drawdownChart'), {{
            type: 'line',
            data: {{
                labels: {dates},
                datasets: [{{
                    label: '回撤率(%)',
                    data: {drawdowns},
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ y: {{ beginAtZero: true, max: 50 }} }}
            }}
        }});
    </script>
</body>
</html>
"""
        
        if output_file is None:
            output_file = result_file.replace('.json', '.html')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML报告已生成: {output_file}")
        return output_file


if __name__ == "__main__":
    analyzer = BacktestAnalyzer()
    
    # 列出所有回测结果
    results_dir = Path("/workspace/projects/workspace/data/backtest_results")
    if results_dir.exists():
        result_files = list(results_dir.glob("*.json"))
        print(f"📊 找到 {len(result_files)} 个回测结果\n")
        
        for f in result_files:
            analysis = analyzer.analyze_result(f)
            print(f"\n📈 {analysis['strategy_name']}")
            print(f"   综合评分: {analysis['score']:.2f}")
            print(f"   年化收益: {analysis['profitability']['annual_return']:.2f}%")
            print(f"   最大回撤: {analysis['risk']['max_drawdown']:.2f}%")
            print(f"   胜率: {analysis['trading']['win_rate']:.2f}%")
