#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组合归因分析模块
基于Brinson模型的归因分析

支持:
- 选股归因 (Selection Effect)
- 配置归因 (Allocation Effect)  
- 交互归因 (Interaction Effect)
- 行业归因 (Sector Attribution)
"""

import json
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass

sys.path.insert(0, "/workspace/projects/workspace")

@dataclass
class AttributionResult:
    """归因结果"""
    total_return: float
    benchmark_return: float
    excess_return: float
    selection_effect: float
    allocation_effect: float
    interaction_effect: float
    sector_attribution: Dict[str, Dict]
    period: str

class BrinsonAttribution:
    """
    Brinson归因模型
    
    公式:
    - 选股效应 = Σ(w_p - w_b) × (r_p - r_b)
    - 配置效应 = Σ(w_p - w_b) × r_b
    - 交互效应 = Σ(w_p - w_b) × (r_p - r_b)
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        
    def analyze(self,
                portfolio_weights: Dict[str, float],
                portfolio_returns: Dict[str, float],
                benchmark_weights: Dict[str, float],
                benchmark_returns: Dict[str, float],
                period: str = None) -> AttributionResult:
        """
        执行Brinson归因分析
        
        Args:
            portfolio_weights: 组合权重 {标的: 权重}
            portfolio_returns: 组合收益 {标的: 收益}
            benchmark_weights: 基准权重 {标的: 权重}
            benchmark_returns: 基准收益 {标的: 收益}
            period: 分析期间
            
        Returns:
            AttributionResult: 归因结果
        """
        # 对齐数据
        all_assets = set(portfolio_weights.keys()) | set(benchmark_weights.keys())
        
        # 计算各项效应
        selection_effect = 0
        allocation_effect = 0
        interaction_effect = 0
        
        sector_attribution = {}
        
        for asset in all_assets:
            w_p = portfolio_weights.get(asset, 0)
            r_p = portfolio_returns.get(asset, 0)
            w_b = benchmark_weights.get(asset, 0)
            r_b = benchmark_returns.get(asset, 0)
            
            # Brinson公式
            selection_effect += w_b * (r_p - r_b)
            allocation_effect += (w_p - w_b) * r_b
            interaction_effect += (w_p - w_b) * (r_p - r_b)
            
            sector_attribution[asset] = {
                "portfolio_weight": w_p,
                "portfolio_return": r_p,
                "benchmark_weight": w_b,
                "benchmark_return": r_b,
                "selection": w_b * (r_p - r_b),
                "allocation": (w_p - w_b) * r_b,
                "interaction": (w_p - w_b) * (r_p - r_b)
            }
        
        # 计算总收益
        total_return = sum(w * r for w, r in zip(portfolio_weights.values(), portfolio_returns.values()))
        benchmark_return = sum(w * r for w, r in zip(benchmark_weights.values(), benchmark_returns.values()))
        excess_return = total_return - benchmark_return
        
        return AttributionResult(
            total_return=total_return,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            selection_effect=selection_effect,
            allocation_effect=allocation_effect,
            interaction_effect=interaction_effect,
            sector_attribution=sector_attribution,
            period=period or datetime.now().strftime('%Y-%m')
        )
    
    def generate_report(self, result: AttributionResult) -> str:
        """生成归因分析报告"""
        report = f"""# 📊 组合归因分析报告

**分析期间**: {result.period}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 收益概览

| 指标 | 数值 | 说明 |
|------|------|------|
| 组合收益 | {result.total_return:.2%} | 实际收益 |
| 基准收益 | {result.benchmark_return:.2%} | 基准收益 |
| 超额收益 | {result.excess_return:.2%} | 组合 - 基准 |

---

## 🎯 Brinson归因分解

| 归因因子 | 贡献 | 占比 |
|----------|------|------|
| **选股效应** | {result.selection_effect:.2%} | {result.selection_effect/result.excess_return*100 if result.excess_return != 0 else 0:.1f}% |
| **配置效应** | {result.allocation_effect:.2%} | {result.allocation_effect/result.excess_return*100 if result.excess_return != 0 else 0:.1f}% |
| **交互效应** | {result.interaction_effect:.2%} | {result.interaction_effect/result.excess_return*100 if result.excess_return != 0 else 0:.1f}% |
| **超额收益** | {result.excess_return:.2%} | 100% |

---

## 📊 行业/标归因明细

"""
        
        # 添加明细表格
        report += "| 标的 | 组合权重 | 组合收益 | 基准权重 | 基准收益 | 选股 | 配置 | 交互 |\n"
        report += "|------|----------|----------|----------|----------|------|------|------|\n"
        
        sorted_sectors = sorted(
            result.sector_attribution.items(),
            key=lambda x: abs(x[1]['selection'] + x[1]['allocation'] + x[1]['interaction']),
            reverse=True
        )
        
        for asset, data in sorted_sectors[:10]:  # 前10个
            report += f"| {asset} | {data['portfolio_weight']:.1%} | {data['portfolio_return']:.2%} | {data['benchmark_weight']:.1%} | {data['benchmark_return']:.2%} | {data['selection']:.2%} | {data['allocation']:.2%} | {data['interaction']:.2%} |\n"
        
        report += f"""

---

## 💡 关键洞察

1. **选股能力**: {'✅ 优秀' if result.selection_effect > 0 else '⚠️ 需改进'}
   - 选股效应贡献了 {result.selection_effect:.2%} 的超额收益
   
2. **配置能力**: {'✅ 优秀' if result.allocation_effect > 0 else '⚠️ 需改进'}
   - 配置效应贡献了 {result.allocation_effect:.2%} 的超额收益
   
3. **主要贡献来源**: 
   - {max(result.sector_attribution.items(), key=lambda x: x[1]['selection'] + x[1]['allocation'] + x[1]['interaction'])[0]}

---

**ARCHITECT-5L Attribution Engine** | Brinson Model
"""
        return report
    
    def save_report(self, result: AttributionResult, filepath: str = None):
        """保存归因报告"""
        if filepath is None:
            date_str = datetime.now().strftime('%Y%m%d')
            filepath = f"{self.workspace}/data/attribution/attribution_report_{date_str}.md"
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        report = self.generate_report(result)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 归因报告已保存: {filepath}")
        return filepath

class PerformanceAttribution:
    """绩效归因分析 (扩展)"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.brinson = BrinsonAttribution(workspace)
    
    def analyze_portfolio(self, portfolio_id: str = "default") -> AttributionResult:
        """分析实际组合"""
        # 加载组合数据
        portfolio_file = f"{self.workspace}/data/simulated/{portfolio_id}_portfolio.json"
        
        if not os.path.exists(portfolio_file):
            print(f"⚠️ 组合文件不存在: {portfolio_file}")
            return None
        
        with open(portfolio_file, 'r') as f:
            portfolio = json.load(f)
        
        # 构造归因数据 (示例数据)
        positions = portfolio.get("positions", [])
        
        portfolio_weights = {}
        portfolio_returns = {}
        
        total_value = sum(p.get("market_value", 0) for p in positions)
        
        for pos in positions:
            symbol = pos.get("symbol", "UNKNOWN")
            weight = pos.get("market_value", 0) / total_value if total_value > 0 else 0
            # 模拟收益 (实际应从历史数据计算)
            return_pct = pos.get("unrealized_pnl", 0) / pos.get("cost_basis", 1) if pos.get("cost_basis", 0) > 0 else 0
            
            portfolio_weights[symbol] = weight
            portfolio_returns[symbol] = return_pct
        
        # 基准数据 (沪深300示例)
        benchmark_weights = {"000300.SH": 1.0}
        benchmark_returns = {"000300.SH": 0.08}  # 8%年化收益
        
        return self.brinson.analyze(
            portfolio_weights=portfolio_weights,
            portfolio_returns=portfolio_returns,
            benchmark_weights=benchmark_weights,
            benchmark_returns=benchmark_returns,
            period=datetime.now().strftime('%Y-%m')
        )

def demo():
    """演示归因分析"""
    print("="*70)
    print("📊 Brinson归因分析演示")
    print("="*70)
    print()
    
    attribution = BrinsonAttribution()
    
    # 示例数据
    portfolio_weights = {
        "000001.SZ": 0.20,  # 平安银行
        "000858.SZ": 0.15,  # 五粮液
        "002594.SZ": 0.15,  # 比亚迪
        "300750.SZ": 0.20,  # 宁德时代
        "601318.SH": 0.15,  # 中国平安
        "000333.SZ": 0.15,  # 美的集团
    }
    
    portfolio_returns = {
        "000001.SZ": 0.15,
        "000858.SZ": 0.25,
        "002594.SZ": 0.35,
        "300750.SZ": 0.20,
        "601318.SH": -0.05,
        "000333.SZ": 0.10,
    }
    
    # 基准权重 (等权)
    benchmark_weights = {k: 1/6 for k in portfolio_weights.keys()}
    
    # 基准收益
    benchmark_returns = {
        "000001.SZ": 0.10,
        "000858.SZ": 0.20,
        "002594.SZ": 0.30,
        "300750.SZ": 0.18,
        "601318.SH": 0.00,
        "000333.SZ": 0.08,
    }
    
    print("📈 执行Brinson归因分析...")
    print()
    
    result = attribution.analyze(
        portfolio_weights=portfolio_weights,
        portfolio_returns=portfolio_returns,
        benchmark_weights=benchmark_weights,
        benchmark_returns=benchmark_returns,
        period="2026-05"
    )
    
    print(f"组合收益: {result.total_return:.2%}")
    print(f"基准收益: {result.benchmark_return:.2%}")
    print(f"超额收益: {result.excess_return:.2%}")
    print()
    print("归因分解:")
    print(f"  选股效应: {result.selection_effect:.2%}")
    print(f"  配置效应: {result.allocation_effect:.2%}")
    print(f"  交互效应: {result.interaction_effect:.2%}")
    print()
    
    # 生成并保存报告
    report_path = attribution.save_report(result)
    
    print()
    print("="*70)
    print("✅ 归因分析演示完成!")
    print(f"📄 报告: {report_path}")
    print("="*70)

if __name__ == "__main__":
    demo()
