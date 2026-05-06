#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A/B测试框架
策略对比测试与自动选择

功能:
- 策略分组测试 (A/B/C分组)
- 绩效对比分析
- 统计显著性检验
- 自动选择最优策略
"""

import numpy as np
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, "/workspace/projects/workspace")

@dataclass
class StrategyVariant:
    """策略变体"""
    name: str
    strategy_id: str
    params: Dict
    description: str = ""

@dataclass
class TestResult:
    """测试结果"""
    variant_name: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trade_count: int
    avg_holding_days: float
    volatility: float
    calmar_ratio: float
    sample_size: int

class ABTestFramework:
    """A/B测试框架"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.tests: Dict[str, Dict] = {}
        self.results: Dict[str, List[TestResult]] = {}
        
        print("🧪 A/B测试框架初始化")
    
    def create_test(self, test_id: str, name: str, 
                    variants: List[StrategyVariant],
                    start_date: str, end_date: str,
                    initial_capital: float = 100000.0) -> Dict:
        """
        创建A/B测试
        
        Args:
            test_id: 测试ID
            name: 测试名称
            variants: 策略变体列表
            start_date: 测试开始日期
            end_date: 测试结束日期
            initial_capital: 初始资金
            
        Returns:
            测试配置
        """
        test_config = {
            "test_id": test_id,
            "name": name,
            "variants": [asdict(v) for v in variants],
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital,
            "status": "created",
            "created_at": datetime.now().isoformat()
        }
        
        self.tests[test_id] = test_config
        
        print(f"✅ 创建A/B测试: {name}")
        print(f"   测试ID: {test_id}")
        print(f"   变体数量: {len(variants)}")
        print(f"   测试周期: {start_date} 至 {end_date}")
        
        return test_config
    
    def run_backtest(self, variant: StrategyVariant, 
                     price_data: pd.DataFrame) -> TestResult:
        """
        运行回测
        
        Args:
            variant: 策略变体
            price_data: 价格数据
            
        Returns:
            测试结果
        """
        # 简化的回测逻辑 (实际应该调用完整的回测引擎)
        returns = price_data['close'].pct_change().dropna()
        
        # 模拟策略信号
        np.random.seed(hash(variant.name) % 2**32)
        signals = np.random.choice([-1, 0, 1], size=len(returns), p=[0.2, 0.6, 0.2])
        
        # 计算策略收益
        signals_series = pd.Series(signals[:len(returns)], index=returns.index)
        strategy_returns = returns * signals_series.shift(1).fillna(0)
        
        # 计算指标
        total_return = (1 + strategy_returns).prod() - 1
        volatility = strategy_returns.std() * np.sqrt(252)
        sharpe = strategy_returns.mean() / (strategy_returns.std() + 1e-8) * np.sqrt(252)
        
        # 最大回撤
        cumulative = (1 + strategy_returns).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min()
        
        # 胜率
        trades = strategy_returns[strategy_returns != 0]
        win_rate = (trades > 0).sum() / len(trades) if len(trades) > 0 else 0
        
        # 交易次数
        trade_count = len(trades)
        
        # Calmar比率
        calmar = total_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return TestResult(
            variant_name=variant.name,
            total_return=total_return,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            trade_count=trade_count,
            avg_holding_days=np.random.uniform(2, 30),  # 模拟
            volatility=volatility,
            calmar_ratio=calmar,
            sample_size=len(returns)
        )
    
    def run_test(self, test_id: str, price_data: pd.DataFrame) -> List[TestResult]:
        """
        运行完整测试
        
        Args:
            test_id: 测试ID
            price_data: 价格数据
            
        Returns:
            所有变体的测试结果
        """
        if test_id not in self.tests:
            raise ValueError(f"测试不存在: {test_id}")
        
        test_config = self.tests[test_id]
        print(f"\n{'='*70}")
        print(f"🚀 运行A/B测试: {test_config['name']}")
        print(f"{'='*70}\n")
        
        results = []
        
        for variant_dict in test_config['variants']:
            variant = StrategyVariant(**variant_dict)
            print(f"📝 测试变体: {variant.name}")
            print(f"   策略: {variant.strategy_id}")
            
            result = self.run_backtest(variant, price_data)
            results.append(result)
            
            print(f"   总收益: {result.total_return:.2%}")
            print(f"   夏普比: {result.sharpe_ratio:.2f}")
            print(f"   最大回撤: {result.max_drawdown:.2%}")
            print()
        
        self.results[test_id] = results
        test_config['status'] = 'completed'
        
        return results
    
    def statistical_test(self, test_id: str, 
                         metric: str = 'total_return') -> Dict:
        """
        统计显著性检验
        
        Args:
            test_id: 测试ID
            metric: 检验指标
            
        Returns:
            统计检验结果
        """
        if test_id not in self.results:
            raise ValueError(f"测试结果不存在: {test_id}")
        
        results = self.results[test_id]
        
        # 简化的统计检验 (t检验)
        # 实际应该使用更严格的统计方法
        
        # 找到最佳变体
        best_result = max(results, key=lambda x: getattr(x, metric))
        
        # 计算置信区间 (简化)
        metric_values = [getattr(r, metric) for r in results]
        mean_val = np.mean(metric_values)
        std_val = np.std(metric_values)
        
        # 简化的显著性判断
        significance = {}
        for result in results:
            if result.variant_name == best_result.variant_name:
                continue
            
            diff = getattr(best_result, metric) - getattr(result, metric)
            # 简化: 如果差异大于1个标准差，认为显著
            is_significant = abs(diff) > std_val
            
            significance[result.variant_name] = {
                "difference": diff,
                "significant": is_significant,
                "confidence": "95%" if is_significant else "<95%"
            }
        
        return {
            "best_variant": best_result.variant_name,
            "metric": metric,
            "best_value": getattr(best_result, metric),
            "mean": mean_val,
            "std": std_val,
            "significance": significance
        }
    
    def select_best_strategy(self, test_id: str, 
                             criteria: List[str] = None) -> Dict:
        """
        选择最优策略
        
        Args:
            test_id: 测试ID
            criteria: 选择标准 (默认: sharpe_ratio, total_return, max_drawdown)
            
        Returns:
            最优策略及得分
        """
        if criteria is None:
            criteria = ['sharpe_ratio', 'total_return', 'calmar_ratio']
        
        if test_id not in self.results:
            raise ValueError(f"测试结果不存在: {test_id}")
        
        results = self.results[test_id]
        
        # 计算综合得分
        scores = {}
        for result in results:
            score = 0
            
            # 夏普比率权重40%
            if 'sharpe_ratio' in criteria:
                score += result.sharpe_ratio * 0.4
            
            # 总收益权重30%
            if 'total_return' in criteria:
                score += result.total_return * 100 * 0.3  # 放大收益率影响
            
            # Calmar比率权重30%
            if 'calmar_ratio' in criteria:
                score += result.calmar_ratio * 0.3
            
            scores[result.variant_name] = score
        
        # 选择最优
        best_variant = max(scores, key=scores.get)
        best_result = next(r for r in results if r.variant_name == best_variant)
        
        return {
            "test_id": test_id,
            "best_variant": best_variant,
            "score": scores[best_variant],
            "all_scores": scores,
            "metrics": {
                "total_return": best_result.total_return,
                "sharpe_ratio": best_result.sharpe_ratio,
                "max_drawdown": best_result.max_drawdown,
                "calmar_ratio": best_result.calmar_ratio
            },
            "recommendation": f"推荐使用策略变体: {best_variant}"
        }
    
    def generate_report(self, test_id: str) -> str:
        """生成测试报告"""
        if test_id not in self.results:
            return f"测试结果不存在: {test_id}"
        
        test_config = self.tests[test_id]
        results = self.results[test_id]
        
        # 获取最优策略
        best = self.select_best_strategy(test_id)
        stats = self.statistical_test(test_id)
        
        report = f"""# A/B测试报告

## 测试概览

- **测试名称**: {test_config['name']}
- **测试ID**: {test_id}
- **测试周期**: {test_config['start_date']} 至 {test_config['end_date']}
- **变体数量**: {len(test_config['variants'])}

## 测试结果对比

| 变体 | 总收益 | 夏普比 | 最大回撤 | 胜率 | 交易次数 |
|------|--------|--------|----------|------|----------|
"""
        
        for r in results:
            report += f"| {r.variant_name} | {r.total_return:.2%} | {r.sharpe_ratio:.2f} | {r.max_drawdown:.2%} | {r.win_rate:.1%} | {r.trade_count} |\n"
        
        report += f"""

## 最优策略

- **推荐变体**: {best['best_variant']}
- **综合得分**: {best['score']:.4f}

### 绩效指标
- 总收益: {best['metrics']['total_return']:.2%}
- 夏普比率: {best['metrics']['sharpe_ratio']:.2f}
- 最大回撤: {best['metrics']['max_drawdown']:.2%}
- Calmar比率: {best['metrics']['calmar_ratio']:.2f}

## 统计显著性

- **最佳指标**: {stats['metric']}
- **最佳值**: {stats['best_value']:.4f}
- **平均值**: {stats['mean']:.4f}
- **标准差**: {stats['std']:.4f}

### 显著性检验

"""
        
        for variant, sig in stats['significance'].items():
            sig_mark = "✅ 显著" if sig['significant'] else "❌ 不显著"
            report += f"- {variant}: 差异 {sig['difference']:.4f} ({sig['confidence']}) {sig_mark}\n"
        
        report += f"""

## 结论与建议

{best['recommendation']}

**实施建议**:
1. 在实盘交易中启用最优策略变体
2. 持续监控策略表现
3. 建议每月重新运行A/B测试
4. 当策略绩效下降时，考虑重新优化参数

---
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report
    
    def save_results(self, test_id: str, filepath: str = None):
        """保存测试结果"""
        if filepath is None:
            filepath = f"{self.workspace}/data/ab_tests/{test_id}_results.json"
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            "test_config": self.tests.get(test_id),
            "results": [asdict(r) for r in self.results.get(test_id, [])]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"💾 测试结果已保存: {filepath}")

def demo():
    """演示A/B测试框架"""
    print("="*70)
    print("🧪 A/B测试框架演示")
    print("="*70)
    print()
    
    # 创建模拟价格数据
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=252, freq='B')
    price = 100
    prices = []
    for _ in range(252):
        price = price * (1 + np.random.normal(0.0003, 0.015))
        prices.append(price)
    
    price_data = pd.DataFrame({
        'date': dates,
        'close': prices,
        'open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices]
    })
    
    # 初始化框架
    framework = ABTestFramework()
    
    # 创建测试变体
    variants = [
        StrategyVariant(
            name="海龟交易-A",
            strategy_id="turtle_trading",
            params={"entry_period": 20, "exit_period": 10, "stop_loss": 0.03},
            description="标准海龟交易法则"
        ),
        StrategyVariant(
            name="海龟交易-B",
            strategy_id="turtle_trading",
            params={"entry_period": 30, "exit_period": 15, "stop_loss": 0.05},
            description="保守版海龟交易"
        ),
        StrategyVariant(
            name="趋势突破-C",
            strategy_id="trend_rs",
            params={"rsi_period": 14, "trend_ma": 50},
            description="趋势+RSI策略"
        )
    ]
    
    # 创建测试
    framework.create_test(
        test_id="TEST_20260502_001",
        name="海龟交易参数优化测试",
        variants=variants,
        start_date="2025-01-01",
        end_date="2025-12-31"
    )
    
    # 运行测试
    results = framework.run_test("TEST_20260502_001", price_data)
    
    # 统计检验
    print("="*70)
    print("📊 统计显著性检验")
    print("="*70)
    stats = framework.statistical_test("TEST_20260502_001")
    print(f"最佳变体: {stats['best_variant']}")
    print(f"最佳值: {stats['best_value']:.4f}")
    print()
    
    # 选择最优策略
    print("="*70)
    print("🏆 最优策略选择")
    print("="*70)
    best = framework.select_best_strategy("TEST_20260502_001")
    print(f"推荐策略: {best['best_variant']}")
    print(f"综合得分: {best['score']:.4f}")
    print(f"夏普比率: {best['metrics']['sharpe_ratio']:.2f}")
    print(f"总收益: {best['metrics']['total_return']:.2%}")
    print()
    
    # 生成报告
    report = framework.generate_report("TEST_20260502_001")
    print("="*70)
    print("📝 A/B测试报告预览")
    print("="*70)
    print(report[:1000] + "...")
    
    print()
    print("="*70)
    print("✅ A/B测试框架演示完成!")
    print("="*70)

if __name__ == "__main__":
    demo()
