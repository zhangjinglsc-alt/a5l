#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 6: AI增强决策引擎
AI-Enhanced Decision Engine with LLM signal boosting
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SignalEnhancement:
    """信号增强结果"""
    original_confidence: float
    enhanced_confidence: float
    enhancement_factor: float
    reasoning: str
    sentiment_score: float
    news_impact: str
    risk_adjustment: float

class AIEnhancementEngine:
    """AI增强决策引擎"""
    
    def __init__(self):
        self.sentiment_threshold = 0.3
        self.news_weight = 0.2
        self.sentiment_weight = 0.15
        self.technical_weight = 0.65
        
    def analyze_sentiment(self, symbol: str, text_data: List[str]) -> Dict:
        """情绪分析"""
        # 模拟情绪分析
        positive_keywords = ["增长", "突破", "利好", "强劲", "超预期", "买入", "上涨"]
        negative_keywords = ["下跌", "利空", "疲软", "不及预期", "卖出", "风险", "衰退"]
        
        sentiment_score = 0.0
        keyword_matches = []
        
        for text in text_data:
            text_lower = text.lower()
            pos_count = sum(1 for kw in positive_keywords if kw in text_lower)
            neg_count = sum(1 for kw in negative_keywords if kw in text_lower)
            
            sentiment_score += (pos_count - neg_count) * 0.1
            
            if pos_count > 0:
                keyword_matches.extend([kw for kw in positive_keywords if kw in text_lower])
            if neg_count > 0:
                keyword_matches.extend([kw for kw in negative_keywords if kw in text_lower])
        
        # 归一化到 -1 到 1
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        return {
            "score": sentiment_score,
            "label": "positive" if sentiment_score > 0.3 else "negative" if sentiment_score < -0.3 else "neutral",
            "keywords": list(set(keyword_matches)),
            "confidence": min(1.0, abs(sentiment_score) + 0.5)
        }
    
    def analyze_news_impact(self, symbol: str, news_items: List[Dict]) -> Dict:
        """新闻事件影响分析"""
        impact_score = 0.0
        high_impact_events = []
        
        for news in news_items:
            impact = news.get("impact", "medium")
            sentiment = news.get("sentiment", "neutral")
            
            if impact == "high":
                multiplier = 0.3
                high_impact_events.append(news.get("title", "Unknown"))
            elif impact == "medium":
                multiplier = 0.15
            else:
                multiplier = 0.05
            
            if sentiment == "positive":
                impact_score += multiplier
            elif sentiment == "negative":
                impact_score -= multiplier
        
        return {
            "impact_score": max(-1.0, min(1.0, impact_score)),
            "high_impact_events": high_impact_events[:3],  # Top 3
            "news_count": len(news_items)
        }
    
    def enhance_signal(self, symbol: str, original_signal: Dict,
                      market_data: Dict, news_data: List[Dict],
                      sentiment_data: List[str]) -> SignalEnhancement:
        """增强交易信号"""
        
        original_confidence = original_signal.get("confidence", 0.5)
        original_direction = original_signal.get("direction", "neutral")
        
        # 1. 情绪分析
        sentiment = self.analyze_sentiment(symbol, sentiment_data)
        sentiment_score = sentiment["score"]
        
        # 2. 新闻影响分析
        news_analysis = self.analyze_news_impact(symbol, news_data)
        news_impact_score = news_analysis["impact_score"]
        
        # 3. 技术面调整
        technical_factor = self._calculate_technical_factor(market_data)
        
        # 4. 计算增强置信度
        # 原始置信度 * 技术权重 + 情绪 * 情绪权重 + 新闻 * 新闻权重
        enhancement = (
            original_confidence * self.technical_weight +
            abs(sentiment_score) * self.sentiment_weight * (1 if sentiment_score > 0 and original_direction == "bullish" else -1) +
            abs(news_impact_score) * self.news_weight * (1 if news_impact_score > 0 and original_direction == "bullish" else -1)
        )
        
        # 调整置信度 (保持原始方向)
        if original_direction == "bullish":
            enhanced_confidence = min(0.95, original_confidence + enhancement * 0.1)
        elif original_direction == "bearish":
            enhanced_confidence = min(0.95, original_confidence + enhancement * 0.1)
        else:
            enhanced_confidence = original_confidence
        
        # 5. 风险调整
        risk_adjustment = self._calculate_risk_adjustment(market_data)
        enhanced_confidence *= risk_adjustment
        
        enhancement_factor = (enhanced_confidence - original_confidence) / original_confidence if original_confidence > 0 else 0
        
        # 生成推理
        reasoning = self._generate_reasoning(
            original_signal, sentiment, news_analysis, technical_factor
        )
        
        return SignalEnhancement(
            original_confidence=original_confidence,
            enhanced_confidence=enhanced_confidence,
            enhancement_factor=enhancement_factor,
            reasoning=reasoning,
            sentiment_score=sentiment_score,
            news_impact=", ".join(news_analysis["high_impact_events"]) if news_analysis["high_impact_events"] else "无重大事件",
            risk_adjustment=risk_adjustment
        )
    
    def _calculate_technical_factor(self, market_data: Dict) -> float:
        """计算技术面因子"""
        trend = market_data.get("trend", "neutral")
        rsi = market_data.get("rsi", 50)
        volume_ratio = market_data.get("volume_ratio", 1.0)
        
        factor = 0.0
        
        # 趋势贡献
        if trend == "uptrend":
            factor += 0.2
        elif trend == "downtrend":
            factor -= 0.2
        
        # RSI贡献
        if rsi > 70:
            factor -= 0.1  # 超买
        elif rsi < 30:
            factor += 0.1  # 超卖
        
        # 成交量贡献
        if volume_ratio > 1.5:
            factor += 0.1  # 放量
        
        return factor
    
    def _calculate_risk_adjustment(self, market_data: Dict) -> float:
        """计算风险调整因子"""
        volatility = market_data.get("volatility", 0.2)
        beta = market_data.get("beta", 1.0)
        
        # 高波动性降低置信度
        vol_adjustment = 1.0 - (volatility - 0.2) * 0.5
        
        # 高Beta调整
        beta_adjustment = 1.0 - abs(beta - 1.0) * 0.1
        
        return max(0.5, min(1.1, vol_adjustment * beta_adjustment))
    
    def _generate_reasoning(self, original_signal: Dict, sentiment: Dict,
                           news_analysis: Dict, technical_factor: float) -> str:
        """生成增强推理"""
        reasoning_parts = []
        
        # 原始信号
        reasoning_parts.append(f"原始信号置信度: {original_signal.get('confidence', 0.5):.1%}")
        
        # 情绪贡献
        if abs(sentiment['score']) > 0.3:
            direction = "正面" if sentiment['score'] > 0 else "负面"
            reasoning_parts.append(f"市场情绪{direction} (得分: {sentiment['score']:+.2f})")
        
        # 新闻贡献
        if news_analysis['high_impact_events']:
            reasoning_parts.append(f"重大新闻事件: {len(news_analysis['high_impact_events'])}条")
        
        # 技术面
        if technical_factor > 0.1:
            reasoning_parts.append("技术面支持 (趋势向上)")
        elif technical_factor < -0.1:
            reasoning_parts.append("技术面压力 (趋势向下)")
        
        return "; ".join(reasoning_parts)


def demo():
    """AI增强演示"""
    print("=" * 70)
    print("🤖 A5L Week 6: AI增强决策引擎演示")
    print("=" * 70)
    
    engine = AIEnhancementEngine()
    
    # 测试场景1: NVDA
    print("\n【场景1: NVDA - AI芯片龙头】")
    print("-" * 70)
    
    original_signal = {
        "symbol": "NVDA",
        "direction": "bullish",
        "confidence": 0.75,
        "source": "technical_analysis"
    }
    
    market_data = {
        "trend": "uptrend",
        "rsi": 65,
        "volume_ratio": 1.8,
        "volatility": 0.25,
        "beta": 1.5
    }
    
    news_data = [
        {"title": "NVDA发布新一代AI芯片", "impact": "high", "sentiment": "positive"},
        {"title": "数据中心需求强劲", "impact": "medium", "sentiment": "positive"},
        {"title": "竞品发布新芯片", "impact": "low", "sentiment": "neutral"}
    ]
    
    sentiment_data = [
        "NVDA业绩超预期，AI芯片需求强劲",
        "分析师上调目标价，看好AI前景",
        "机构投资者增持NVDA"
    ]
    
    result = engine.enhance_signal("NVDA", original_signal, market_data, news_data, sentiment_data)
    
    print(f"原始置信度: {result.original_confidence:.1%}")
    print(f"增强后置信度: {result.enhanced_confidence:.1%}")
    print(f"增强因子: {result.enhancement_factor:+.1%}")
    print(f"情绪得分: {result.sentiment_score:+.2f}")
    print(f"新闻影响: {result.news_impact}")
    print(f"风险调整: {result.risk_adjustment:.2f}")
    print(f"推理: {result.reasoning}")
    
    # 测试场景2: TSLA
    print("\n【场景2: TSLA - 波动较大】")
    print("-" * 70)
    
    original_signal = {
        "symbol": "TSLA",
        "direction": "bearish",
        "confidence": 0.60,
        "source": "technical_analysis"
    }
    
    market_data = {
        "trend": "downtrend",
        "rsi": 35,
        "volume_ratio": 1.2,
        "volatility": 0.45,  # 高波动
        "beta": 2.0  # 高Beta
    }
    
    news_data = [
        {"title": "TSLA销量不及预期", "impact": "high", "sentiment": "negative"},
        {"title": "竞争加剧，价格战持续", "impact": "medium", "sentiment": "negative"}
    ]
    
    sentiment_data = [
        "TSLA股价下跌，市场担忧竞争",
        "电动车销量增长放缓",
        "分析师下调评级"
    ]
    
    result = engine.enhance_signal("TSLA", original_signal, market_data, news_data, sentiment_data)
    
    print(f"原始置信度: {result.original_confidence:.1%}")
    print(f"增强后置信度: {result.enhanced_confidence:.1%}")
    print(f"增强因子: {result.enhancement_factor:+.1%}")
    print(f"情绪得分: {result.sentiment_score:+.2f}")
    print(f"新闻影响: {result.news_impact}")
    print(f"风险调整: {result.risk_adjustment:.2f} (高波动降低置信度)")
    print(f"推理: {result.reasoning}")
    
    print("\n" + "=" * 70)
    print("✅ AI增强决策引擎演示完成!")
    print("=" * 70)


if __name__ == "__main__":
    demo()
