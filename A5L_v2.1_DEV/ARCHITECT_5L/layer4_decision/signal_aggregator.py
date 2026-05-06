#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 4: Signal Aggregator
决策信号层 - 信号聚合器

功能：
1. 整合Layer 2策略信号 + Layer 3分析结果
2. 多信号加权聚合
3. 信号冲突解决
4. 置信度评估
"""

import json
import os
import sys
sys.path.insert(0, '/workspace/projects/workspace/ARCHITECT_5L/layer2_strategy')
sys.path.insert(0, '/workspace/projects/workspace/ARCHITECT_5L/layer3_analysis')

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from strategy_engine import StrategyEngine

@dataclass
class AggregatedSignal:
    """聚合后的交易信号"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0-1
    strength: str  # strong, moderate, weak
    sources: List[Dict]  # 信号来源列表
    risk_level: str  # high, medium, low
    timestamp: str
    holding_period: str  # short, medium, long
    expected_return: Optional[float] = None

class SignalAggregator:
    """信号聚合器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.strategy_engine = StrategyEngine(workspace)
        
        # 信号权重配置
        self.source_weights = {
            "strategy": 0.4,      # 策略信号权重
            "sentiment": 0.2,     # 情绪分析权重
            "fundamental": 0.2,   # 基本面权重
            "technical": 0.15,    # 技术面权重
            "risk": 0.05          # 风险信号权重
        }
    
    def aggregate_signals(self, symbol: str, 
                         strategy_signals: List[Dict],
                         analysis_results: Dict) -> AggregatedSignal:
        """
        聚合多个信号源
        
        Args:
            symbol: 股票代码
            strategy_signals: Layer 2策略信号列表
            analysis_results: Layer 3分析结果
        
        Returns:
            聚合后的交易信号
        """
        sources = []
        
        # 处理策略信号
        strategy_confidence = 0
        strategy_action = "HOLD"
        
        for sig in strategy_signals:
            if sig.get("action") == "BUY":
                strategy_confidence += sig.get("confidence", 0)
                strategy_action = "BUY"
            
            sources.append({
                "type": "strategy",
                "name": sig.get("strategy_name", "Unknown"),
                "action": sig.get("action"),
                "confidence": sig.get("confidence", 0),
                "weight": self.source_weights["strategy"]
            })
        
        # 处理情绪分析
        sentiment_score = analysis_results.get("sentiment", {}).get("score", 0)
        sentiment_confidence = analysis_results.get("sentiment", {}).get("confidence", 0.5)
        
        sources.append({
            "type": "sentiment",
            "score": sentiment_score,
            "confidence": sentiment_confidence,
            "weight": self.source_weights["sentiment"]
        })
        
        # 处理风险信号
        risks = analysis_results.get("risks", [])
        risk_penalty = len([r for r in risks if r.get("severity") == "high"]) * 0.2
        
        sources.append({
            "type": "risk",
            "risk_count": len(risks),
            "high_risk_count": len([r for r in risks if r.get("severity") == "high"]),
            "penalty": risk_penalty,
            "weight": self.source_weights["risk"]
        })
        
        # 计算总体置信度
        total_confidence = (
            strategy_confidence * self.source_weights["strategy"] +
            sentiment_confidence * self.source_weights["sentiment"] * (1 if sentiment_score > 0 else 0) +
            max(0, 0.5 - risk_penalty) * self.source_weights["risk"]
        )
        
        # 决定最终动作
        if strategy_action == "BUY" and sentiment_score > 0 and risk_penalty < 0.3:
            final_action = "BUY"
        elif risk_penalty > 0.5:
            final_action = "SELL"
        else:
            final_action = "HOLD"
        
        # 确定信号强度
        if total_confidence > 0.8:
            strength = "strong"
        elif total_confidence > 0.5:
            strength = "moderate"
        else:
            strength = "weak"
        
        # 风险等级
        if risk_penalty > 0.3:
            risk_level = "high"
        elif risk_penalty > 0.1:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return AggregatedSignal(
            symbol=symbol,
            action=final_action,
            confidence=round(total_confidence, 2),
            strength=strength,
            sources=sources,
            risk_level=risk_level,
            timestamp=datetime.now().isoformat(),
            holding_period="medium"  # 默认中等持仓
        )
    
    def generate_signal_report(self, symbol: str) -> str:
        """生成信号聚合报告"""
        # 获取策略信号（简化演示）
        strategy_signals = [
            {"strategy_name": "股票魔法师", "action": "BUY", "confidence": 0.9},
            {"strategy_name": "趋势突破", "action": "BUY", "confidence": 0.75}
        ]
        
        # 模拟分析结果
        analysis_results = {
            "sentiment": {"score": 0.6, "confidence": 0.8},
            "risks": [{"severity": "low"}],
            "opportunities": [{"confidence": "high"}]
        }
        
        signal = self.aggregate_signals(symbol, strategy_signals, analysis_results)
        
        report = f"""# 📊 交易信号聚合报告 - {symbol}

**生成时间**: {signal.timestamp}  
**最终建议**: {"🟢 " + signal.action if signal.action == "BUY" else "🔴 " + signal.action if signal.action == "SELL" else "⚪ " + signal.action}  
**置信度**: {signal.confidence:.0%}  
**信号强度**: {signal.strength.upper()}  
**风险等级**: {signal.risk_level.upper()}

---

## 📡 信号来源

| 来源类型 | 名称/指标 | 信号 | 置信度 | 权重 | 加权贡献 |
|----------|-----------|------|--------|------|----------|
"""
        
        for src in signal.sources:
            if src["type"] == "strategy":
                contribution = src["confidence"] * src["weight"]
                report += f"| 策略 | {src['name']} | {src['action']} | {src['confidence']:.0%} | {src['weight']} | {contribution:.2f} |\n"
            elif src["type"] == "sentiment":
                contribution = src["confidence"] * src["weight"] * (1 if src["score"] > 0 else 0)
                report += f"| 情绪 | 情绪得分 {src['score']:.1f} | {'正面' if src['score'] > 0 else '负面'} | {src['confidence']:.0%} | {src['weight']} | {contribution:.2f} |\n"
            elif src["type"] == "risk":
                contribution = max(0, 0.5 - src.get("penalty", 0)) * src["weight"]
                report += f"| 风险 | 高风险 {src.get('high_risk_count', 0)} 个 | 警告 | - | {src['weight']} | {contribution:.2f} |\n"
        
        report += f"""
---

## 🎯 执行建议

### 交易决策
- **操作**: {signal.action}
- **仓位建议**: 
  - 强信号(>80%): 10%仓位
  - 中信号(50-80%): 5-8%仓位
  - 弱信号(<50%): 观望或小仓位试探
- **当前适用**: {signal.strength}信号，建议{"10%仓位" if signal.strength == "strong" else "5-8%仓位" if signal.strength == "moderate" else "观望"}

### 风险控制
- **风险等级**: {signal.risk_level.upper()}
- **止损设置**: 
  - 高风险: 3%止损
  - 中风险: 5%止损
  - 低风险: 7%止损
- **当前适用**: {signal.risk_level}风险，建议{"3%" if signal.risk_level == "high" else "5%" if signal.risk_level == "medium" else "7%"}止损

---

## ⚠️ 免责声明

本信号基于算法生成，仅供参考，不构成投资建议。股市有风险，投资需谨慎。
"""
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("📊 信号聚合器 (Layer 4)")
    print("=" * 70)
    
    aggregator = SignalAggregator()
    
    # 演示信号聚合
    print("\n🧪 测试信号聚合...")
    
    strategy_signals = [
        {"strategy_name": "股票魔法师", "action": "BUY", "confidence": 0.9},
        {"strategy_name": "趋势突破", "action": "BUY", "confidence": 0.75}
    ]
    
    analysis_results = {
        "sentiment": {"score": 0.6, "confidence": 0.8},
        "risks": [{"severity": "low"}],
    }
    
    signal = aggregator.aggregate_signals("000001.SZ", strategy_signals, analysis_results)
    
    print(f"\n  标的: {signal.symbol}")
    print(f"  动作: {signal.action}")
    print(f"  置信度: {signal.confidence:.0%}")
    print(f"  强度: {signal.strength}")
    print(f"  风险等级: {signal.risk_level}")
    print(f"\n  信号来源: {len(signal.sources)} 个")
    
    for src in signal.sources:
        print(f"    • {src['type']}: confidence={src.get('confidence', 'N/A')}")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 信号聚合报告:")
    report = aggregator.generate_signal_report("000001.SZ")
    print(report[:1000] + "...")

if __name__ == "__main__":
    main()
