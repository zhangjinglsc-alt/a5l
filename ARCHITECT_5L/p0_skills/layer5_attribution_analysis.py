#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L5 P0: 投资能力归因分析系统
提出者: Chief Investment Officer (顶级投资人)
"""
import logging
import numpy as np
from typing import Dict, List
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AttributionResult:
    stock_selection: float      # 选股能力
    market_timing: float        # 择时能力
    sector_allocation: float    # 行业配置能力
    risk_management: float      # 风险管理能力
    luck_factor: float          # 运气成分
    unexplained: float          # 无法解释部分

class AttributionAnalyzer:
    """能力归因分析器 - P0最高优先级"""
    
    def __init__(self):
        self.benchmark = "CSI300"  # 默认基准
        logger.info("📊 Attribution Analyzer initialized")
    
    def analyze_performance(self, portfolio_returns: List[float],
                           benchmark_returns: List[float],
                           trades: List[Dict]) -> AttributionResult:
        """分析绩效归因"""
        # 计算总收益
        portfolio_total = np.prod([1 + r for r in portfolio_returns]) - 1
        benchmark_total = np.prod([1 + r for r in benchmark_returns]) - 1
        excess_return = portfolio_total - benchmark_total
        
        # 归因分析 (简化版)
        # 实际应使用Brinson模型或多因子模型
        
        # 选股能力 (个股选择带来的超额收益)
        stock_selection = excess_return * 0.4  # 假设40%来自选股
        
        # 择时能力 (仓位调整带来的超额收益)
        market_timing = excess_return * 0.25   # 假设25%来自择时
        
        # 行业配置
        sector_allocation = excess_return * 0.20  # 假设20%来自行业配置
        
        # 风险管理 (风险控制带来的稳定收益)
        portfolio_vol = np.std(portfolio_returns)
        benchmark_vol = np.std(benchmark_returns)
        risk_adjusted = (portfolio_total / portfolio_vol) - (benchmark_total / benchmark_vol)
        risk_management = risk_adjusted * 0.1  # 假设10%来自风险管理
        
        # 运气成分 (随机性)
        luck_factor = excess_return * 0.03    # 假设3%是运气
        
        # 无法解释
        unexplained = excess_return - (stock_selection + market_timing + 
                                      sector_allocation + risk_management + luck_factor)
        
        return AttributionResult(
            stock_selection=stock_selection,
            market_timing=market_timing,
            sector_allocation=sector_allocation,
            risk_management=risk_management,
            luck_factor=luck_factor,
            unexplained=unexplained
        )
    
    def generate_attribution_report(self, result: AttributionResult) -> str:
        """生成归因报告"""
        total = (result.stock_selection + result.market_timing + 
                result.sector_allocation + result.risk_management + 
                result.luck_factor + result.unexplained)
        
        lines = [
            "# 📊 投资能力归因分析报告",
            "",
            "## 归因分解",
            "",
            f"| 能力维度 | 贡献收益 | 占比 |",
            f"|----------|----------|------|",
            f"| 📈 选股能力 | {result.stock_selection:.2%} | {result.stock_selection/total:.1%} |",
            f"| ⏰ 择时能力 | {result.market_timing:.2%} | {result.market_timing/total:.1%} |",
            f"| 🏭 行业配置 | {result.sector_allocation:.2%} | {result.sector_allocation/total:.1%} |",
            f"| 🛡️ 风险管理 | {result.risk_management:.2%} | {result.risk_management/total:.1%} |",
            f"| 🍀 运气成分 | {result.luck_factor:.2%} | {result.luck_factor/total:.1%} |",
            f"| ❓ 无法解释 | {result.unexplained:.2%} | {result.unexplained/total:.1%} |",
            "",
            "## 核心能力识别",
            ""
        ]
        
        # 识别最强能力
        abilities = {
            '选股能力': result.stock_selection,
            '择时能力': result.market_timing,
            '行业配置': result.sector_allocation,
            '风险管理': result.risk_management
        }
        strongest = max(abilities, key=abilities.get)
        
        lines.append(f"**核心优势**: {strongest} (贡献{abilities[strongest]:.2%}超额收益)")
        lines.append("")
        lines.append("## 改进建议")
        lines.append("")
        
        # 找出最弱能力
        weakest = min(abilities, key=abilities.get)
        lines.append(f"- 重点提升: {weakest} 能力")
        lines.append(f"- 保持优势: {strongest} 能力")
        
        return '
'.join(lines)
