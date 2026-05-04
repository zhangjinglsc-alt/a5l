#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 8: 多策略并行引擎
Multi-Strategy Parallel Engine with dynamic weighting
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

class StrategyType(Enum):
    """策略类型"""
    CANSLIM = "canslim"           # 成长股策略
    TURTLE = "turtle"             # 海龟交易
    TREND_RS = "trend_rs"         # 趋势+相对强度
    VOLUME_PRICE = "volume_price" # 量价分析
    FUNDAMENTAL = "fundamental"   # 基本面增长
    YANGGUAN = "yangguan"         # 阳关大道
    BUFFETT = "buffett"           # 价值投资

@dataclass
class StrategySignal:
    """策略信号"""
    strategy: StrategyType
    symbol: str
    action: str  # buy/sell/hold
    confidence: float  # 0-1
    position_size: float  # 建议仓位 0-1
    reasoning: str
    timestamp: str
    expected_return: float  # 预期收益率
    risk_score: float  # 风险评分 0-1

@dataclass
class StrategyPerformance:
    """策略表现"""
    strategy: StrategyType
    total_trades: int
    win_rate: float
    avg_return: float
    sharpe_ratio: float
    max_drawdown: float
    current_weight: float
    last_updated: str

class MultiStrategyEngine:
    """多策略并行引擎"""
    
    def __init__(self):
        self.strategies = list(StrategyType)
        self.weights = {s: 1.0 / len(self.strategies) for s in self.strategies}
        self.signals = []
        self.performance = self._init_performance()
        self.conflict_resolver = StrategyConflictResolver()
        
    def _init_performance(self) -> Dict[StrategyType, StrategyPerformance]:
        """初始化策略表现"""
        return {
            s: StrategyPerformance(
                strategy=s,
                total_trades=random.randint(10, 100),
                win_rate=random.uniform(0.45, 0.65),
                avg_return=random.uniform(-0.02, 0.08),
                sharpe_ratio=random.uniform(0.5, 2.0),
                max_drawdown=random.uniform(0.05, 0.25),
                current_weight=1.0 / len(self.strategies),
                last_updated=datetime.now().isoformat()
            )
            for s in self.strategies
        }
    
    def generate_signals(self, symbol: str, market_data: Dict) -> List[StrategySignal]:
        """
        生成所有策略的信号
        
        每个策略独立分析，生成自己的交易信号
        """
        signals = []
        
        for strategy in self.strategies:
            signal = self._run_strategy(strategy, symbol, market_data)
            if signal:
                signals.append(signal)
        
        self.signals.extend(signals)
        return signals
    
    def _run_strategy(self, strategy: StrategyType, symbol: str,
                     market_data: Dict) -> Optional[StrategySignal]:
        """运行单个策略"""
        
        # 模拟不同策略的决策逻辑
        if strategy == StrategyType.CANSLIM:
            return self._canslim_strategy(symbol, market_data)
        elif strategy == StrategyType.TURTLE:
            return self._turtle_strategy(symbol, market_data)
        elif strategy == StrategyType.TREND_RS:
            return self._trend_rs_strategy(symbol, market_data)
        elif strategy == StrategyType.VOLUME_PRICE:
            return self._volume_price_strategy(symbol, market_data)
        elif strategy == StrategyType.FUNDAMENTAL:
            return self._fundamental_strategy(symbol, market_data)
        elif strategy == StrategyType.YANGGUAN:
            return self._yangguan_strategy(symbol, market_data)
        elif strategy == StrategyType.BUFFETT:
            return self._buffett_strategy(symbol, market_data)
        
        return None
    
    def _canslim_strategy(self, symbol: str, data: Dict) -> StrategySignal:
        """CANSLIM成长股策略"""
        # 简化的CANSLIM逻辑
        score = (
            data.get("eps_growth", 0) * 0.2 +
            data.get("sales_growth", 0) * 0.2 +
            data.get("rs_rating", 50) / 100 * 0.2 +
            (1 if data.get("new_product", False) else 0) * 0.2 +
            (1 if data.get("institutional_demand", False) else 0) * 0.2
        )
        
        action = "buy" if score > 0.6 else "hold" if score > 0.4 else "sell"
        
        return StrategySignal(
            strategy=StrategyType.CANSLIM,
            symbol=symbol,
            action=action,
            confidence=min(0.95, score),
            position_size=score * 0.3,
            reasoning=f"CANSLIM综合评分: {score:.2f}",
            timestamp=datetime.now().isoformat(),
            expected_return=random.uniform(0.05, 0.15),
            risk_score=0.6
        )
    
    def _turtle_strategy(self, symbol: str, data: Dict) -> StrategySignal:
        """海龟交易策略 (20/55日突破)"""
        price = data.get("price", 100)
        ma20 = data.get("ma20", price * 0.95)
        ma55 = data.get("ma55", price * 0.90)
        
        if price > ma20 and price > ma55:
            action = "buy"
            confidence = 0.7
        elif price < ma20 and price < ma55:
            action = "sell"
            confidence = 0.7
        else:
            action = "hold"
            confidence = 0.5
        
        return StrategySignal(
            strategy=StrategyType.TURTLE,
            symbol=symbol,
            action=action,
            confidence=confidence,
            position_size=0.2 if action == "buy" else 0,
            reasoning=f"20日: {ma20:.2f}, 55日: {ma55:.2f}, 当前: {price:.2f}",
            timestamp=datetime.now().isoformat(),
            expected_return=random.uniform(0.03, 0.10),
            risk_score=0.5
        )
    
    def _trend_rs_strategy(self, symbol: str, data: Dict) -> StrategySignal:
        """趋势+相对强度策略"""
        trend = data.get("trend", "sideways")
        rs = data.get("rs_rating", 50)
        
        if trend == "up" and rs > 70:
            action = "buy"
            confidence = rs / 100
        elif trend == "down" and rs < 30:
            action = "sell"
            confidence = (100 - rs) / 100
        else:
            action = "hold"
            confidence = 0.5
        
        return StrategySignal(
            strategy=StrategyType.TREND_RS,
            symbol=symbol,
            action=action,
            confidence=confidence,
            position_size=(rs - 50) / 100 * 0.25,
            reasoning=f"趋势: {trend}, RS: {rs}",
            timestamp=datetime.now().isoformat(),
            expected_return=random.uniform(0.04, 0.12),
            risk_score=0.55
        )
    
    def _volume_price_strategy(self, symbol: str, data: Dict) -> StrategySignal:
        """量价分析策略"""
        volume_ratio = data.get("volume_ratio", 1.0)
        price_change = data.get("price_change", 0)
        
        # 量价齐升 = 买入信号
        if volume_ratio > 1.5 and price_change > 0.02:
            action = "buy"
            confidence = min(0.9, volume_ratio * 0.3 + price_change * 10)
        # 量价背离 = 卖出信号
        elif volume_ratio > 1.5 and price_change < -0.02:
            action = "sell"
            confidence = min(0.9, volume_ratio * 0.3 + abs(price_change) * 10)
        else:
            action = "hold"
            confidence = 0.5
        
        return StrategySignal(
            strategy=StrategyType.VOLUME_PRICE,
            symbol=symbol,
            action=action,
            confidence=confidence,
            position_size=volume_ratio * 0.1,
            reasoning=f"量比: {volume_ratio:.2f}, 涨跌: {price_change:+.2%}",
            timestamp=datetime.now().isoformat(),
            expected_return=random.uniform(0.02, 0.08),
            risk_score=0.65
        )
    
    def _fundamental_strategy(self, symbol: str, data: Dict) -> StrategySignal:
        """基本面增长策略"""
        pe = data.get("pe", 20)
        growth = data.get("revenue_growth", 0.1)
        roe = data.get("roe", 0.1)
        
        # PEG估值
        peg = pe / (growth * 100) if growth > 0 else 999
        
        if peg < 1.0 and roe > 0.15:
            action = "buy"
            confidence = 0.8
        elif peg > 2.0:
            action = "sell"
            confidence = 0.7
        else:
            action = "hold"
            confidence = 0.5
        
        return StrategySignal(
            strategy=StrategyType.FUNDAMENTAL,
            symbol=symbol,
            action=action,
            confidence=confidence,
            position_size=(0.15 - peg * 0.05) if peg < 2 else 0,
            reasoning=f"PE: {pe:.1f}, 增长: {growth:.1%}, ROE: {roe:.1%}, PEG: {peg:.2f}",
            timestamp=datetime.now().isoformat(),
            expected_return=random.uniform(0.05, 0.12),
            risk_score=0.4
        )
    
    def _yangguan_strategy(self, symbol: str, data: Dict) -> StrategySignal:
        """阳关大道超短策略"""
        volume_spike = data.get("volume_spike", False)
        price_breakout = data.get("price_breakout", False)
        
        if volume_spike and price_breakout:
            action = "buy"
            confidence = 0.85
        else:
            action = "hold"
            confidence = 0.4
        
        return StrategySignal(
            strategy=StrategyType.YANGGUAN,
            symbol=symbol,
            action=action,
            confidence=confidence,
            position_size=0.15 if action == "buy" else 0,
            reasoning="量价齐升突破" if action == "buy" else "无明确信号",
            timestamp=datetime.now().isoformat(),
            expected_return=random.uniform(0.02, 0.05),
            risk_score=0.75
        )
    
    def _buffett_strategy(self, symbol: str, data: Dict) -> StrategySignal:
        """巴菲特价值投资"""
        margin_of_safety = data.get("margin_of_safety", 0)
        moat_score = data.get("moat_score", 5)
        
        if margin_of_safety > 0.3 and moat_score >= 7:
            action = "buy"
            confidence = min(0.9, margin_of_safety + moat_score / 10)
        elif margin_of_safety < 0:
            action = "sell"
            confidence = 0.7
        else:
            action = "hold"
            confidence = 0.5
        
        return StrategySignal(
            strategy=StrategyType.BUFFETT,
            symbol=symbol,
            action=action,
            confidence=confidence,
            position_size=margin_of_safety * 0.25,
            reasoning=f"安全边际: {margin_of_safety:.1%}, 护城河: {moat_score}/10",
            timestamp=datetime.now().isoformat(),
            expected_return=random.uniform(0.08, 0.15),
            risk_score=0.3
        )
    
    def aggregate_signals(self, symbol: str) -> Dict:
        """
        聚合多策略信号
        
        使用加权投票机制，考虑各策略当前表现权重
        """
        # 获取该股票的所有信号
        symbol_signals = [s for s in self.signals if s.symbol == symbol]
        
        if not symbol_signals:
            return {"action": "hold", "confidence": 0, "reasoning": "无信号"}
        
        # 按动作分类
        buy_signals = [s for s in symbol_signals if s.action == "buy"]
        sell_signals = [s for s in symbol_signals if s.action == "sell"]
        hold_signals = [s for s in symbol_signals if s.action == "hold"]
        
        # 计算加权得分
        def weighted_score(signals):
            return sum(s.confidence * self.weights[s.strategy] for s in signals)
        
        buy_score = weighted_score(buy_signals)
        sell_score = weighted_score(sell_signals)
        hold_score = weighted_score(hold_signals)
        
        # 决策
        scores = {"buy": buy_score, "sell": sell_score, "hold": hold_score}
        final_action = max(scores, key=scores.get)
        final_confidence = scores[final_action]
        
        # 检测冲突
        conflicts = self.conflict_resolver.detect_conflicts(symbol_signals)
        
        return {
            "symbol": symbol,
            "action": final_action,
            "confidence": final_confidence,
            "scores": scores,
            "supporting_signals": len([s for s in symbol_signals if s.action == final_action]),
            "conflicts": conflicts,
            "timestamp": datetime.now().isoformat()
        }
    
    def update_weights(self, performance_data: Dict):
        """根据表现动态调整策略权重"""
        # 基于夏普比率和胜率调整权重
        total_score = 0
        scores = {}
        
        for strategy in self.strategies:
            perf = self.performance[strategy]
            score = perf.sharpe_ratio * 0.6 + perf.win_rate * 0.4
            scores[strategy] = max(0.1, score)  # 最小权重0.1
            total_score += scores[strategy]
        
        # 归一化
        for strategy in self.strategies:
            self.weights[strategy] = scores[strategy] / total_score
            self.performance[strategy].current_weight = self.weights[strategy]
            self.performance[strategy].last_updated = datetime.now().isoformat()
    
    def get_strategy_summary(self) -> Dict:
        """获取策略汇总"""
        return {
            "strategies": [s.value for s in self.strategies],
            "weights": {k.value: f"{v:.1%}" for k, v in self.weights.items()},
            "performance": {
                k.value: {
                    "win_rate": f"{v.win_rate:.1%}",
                    "sharpe": f"{v.sharpe_ratio:.2f}",
                    "max_dd": f"{v.max_drawdown:.1%}"
                }
                for k, v in self.performance.items()
            },
            "total_signals": len(self.signals)
        }


class StrategyConflictResolver:
    """策略冲突解决器"""
    
    def detect_conflicts(self, signals: List[StrategySignal]) -> List[Dict]:
        """检测策略冲突"""
        conflicts = []
        
        # 检查多空冲突
        buy_strategies = [s for s in signals if s.action == "buy"]
        sell_strategies = [s for s in signals if s.action == "sell"]
        
        if buy_strategies and sell_strategies:
            conflicts.append({
                "type": "long_short_conflict",
                "description": f"{len(buy_strategies)}个策略看多 vs {len(sell_strategies)}个策略看空",
                "severity": "high" if len(buy_strategies) > 0 and len(sell_strategies) > 0 else "medium"
            })
        
        # 检查仓位建议冲突
        position_sizes = [s.position_size for s in signals if s.action == "buy"]
        if position_sizes and max(position_sizes) - min(position_sizes) > 0.2:
            conflicts.append({
                "type": "position_size_conflict",
                "description": f"仓位建议差异大: {min(position_sizes):.1%} - {max(position_sizes):.1%}",
                "severity": "medium"
            })
        
        return conflicts


def demo():
    """多策略并行引擎演示"""
    print("=" * 70)
    print("⚡ A5L Week 8: 多策略并行引擎演示")
    print("=" * 70)
    
    engine = MultiStrategyEngine()
    
    # 模拟市场数据
    market_data = {
        "price": 19.82,
        "ma20": 19.50,
        "ma55": 18.80,
        "volume_ratio": 1.8,
        "price_change": 0.03,
        "eps_growth": 0.25,
        "sales_growth": 0.30,
        "rs_rating": 75,
        "pe": 18,
        "roe": 0.18,
        "revenue_growth": 0.25,
        "margin_of_safety": 0.25,
        "moat_score": 7,
        "trend": "up",
        "volume_spike": True,
        "price_breakout": True,
        "new_product": True,
        "institutional_demand": True
    }
    
    # 演示1: 生成所有策略信号
    print("\n【演示1: 七大策略并行分析 - 中国长城(000066)】")
    print("-" * 70)
    
    signals = engine.generate_signals("000066", market_data)
    
    for signal in signals:
        emoji = {"buy": "📈", "sell": "📉", "hold": "➡️"}[signal.action]
        print(f"{emoji} {signal.strategy.value:12s}: {signal.action.upper():4s} "
              f"(置信度: {signal.confidence:.1%}, 仓位: {signal.position_size:.1%})")
        print(f"   理由: {signal.reasoning[:50]}...")
    
    # 演示2: 信号聚合
    print("\n【演示2: 多策略信号聚合】")
    print("-" * 70)
    
    aggregated = engine.aggregate_signals("000066")
    
    print(f"最终决策: {aggregated['action'].upper()}")
    print(f"综合置信度: {aggregated['confidence']:.2f}")
    print(f"支持策略数: {aggregated['supporting_signals']}/7")
    print(f"各方向得分:")
    for action, score in aggregated['scores'].items():
        print(f"   {action}: {score:.2f}")
    
    if aggregated['conflicts']:
        print(f"\n⚠️ 检测到冲突:")
        for conflict in aggregated['conflicts']:
            print(f"   • {conflict['type']}: {conflict['description']}")
    
    # 演示3: 策略表现与权重
    print("\n【演示3: 策略权重动态分配】")
    print("-" * 70)
    
    summary = engine.get_strategy_summary()
    
    print("当前权重分配:")
    for strategy, weight in summary['weights'].items():
        perf = summary['performance'][strategy]
        print(f"   {strategy:12s}: {weight:>5} (胜率{perf['win_rate']}, 夏普{perf['sharpe']})")
    
    # 演示4: 动态权重调整
    print("\n【演示4: 权重动态调整】")
    print("-" * 70)
    
    print("更新前权重:")
    for s, w in engine.weights.items():
        print(f"   {s.value}: {w:.1%}")
    
    engine.update_weights({})  # 模拟更新
    
    print("\n更新后权重 (基于表现):")
    for s, w in engine.weights.items():
        print(f"   {s.value}: {w:.1%}")
    
    print("\n" + "=" * 70)
    print("✅ 多策略并行引擎演示完成!")
    print("=" * 70)
    print("\n💡 生产环境增强:")
    print("   • 真实策略回测数据")
    print("   • 实时权重自适应调整")
    print("   • 策略相关性分析")
    print("   • 动态策略组合优化")


if __name__ == "__main__":
    demo()
