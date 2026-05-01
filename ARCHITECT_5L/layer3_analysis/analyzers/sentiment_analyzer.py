#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 3: Sentiment Analyzer
非结构化分析层 - 情绪分析器

功能：
1. 文本情绪分析
2. 风险点识别
3. 机会点识别
4. 情绪趋势跟踪

原则：诚实第一，所有结论必须有数据支撑
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class SentimentAnalyzer:
    """情绪分析器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        
        # 情绪词典（简化版，实际应该使用更复杂的NLP模型）
        self.sentiment_dict = self._load_sentiment_dict()
        
        # 风险关键词
        self.risk_keywords = [
            "亏损", "下滑", "下降", "不及预期", "预警", "风险", "违规",
            "调查", "处罚", "减持", "解禁", "退市", "st", "爆雷",
            "loss", "decline", " Investigation", "penalty", "risk"
        ]
        
        # 机会关键词
        self.opportunity_keywords = [
            "增长", "提升", "突破", "订单", "合同", "中标", "扩产",
            "涨价", "超预期", "利好", "政策支持", "龙头", "优势",
            "growth", "breakthrough", "contract", "expansion", "beat"
        ]
    
    def _load_sentiment_dict(self) -> Dict:
        """加载情绪词典"""
        return {
            "positive": [
                "增长", "上涨", "利好", "突破", "超预期", "强劲", "优势",
                "订单", "中标", "扩产", "涨价", "龙头", "领先", "创新",
                "growth", "surge", "breakthrough", "strong", "beat", "leader"
            ],
            "negative": [
                "亏损", "下滑", "下降", "不及预期", "风险", "减持",
                "解禁", "调查", "处罚", "违规", "退市", "爆雷",
                "loss", "decline", " Investigation", "penalty", "risk", "warn"
            ],
            "neutral": [
                "公告", "报告", "说明", "回复", "披露", "显示",
                "announcement", "report", "disclosure", "state"
            ]
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        分析文本情绪
        
        Args:
            text: 待分析文本
        
        Returns:
            情绪分析结果
        """
        if not text:
            return {
                "score": 0.0,
                "label": "neutral",
                "confidence": 0.0,
                "keywords": []
            }
        
        text_lower = text.lower()
        
        # 统计关键词
        positive_count = sum(1 for word in self.sentiment_dict["positive"] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_dict["negative"] if word in text_lower)
        
        # 计算情绪得分 (-1 到 1)
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
            label = "neutral"
            confidence = 0.5
        else:
            score = (positive_count - negative_count) / total
            
            if score > 0.3:
                label = "positive"
            elif score < -0.3:
                label = "negative"
            else:
                label = "neutral"
            
            confidence = min(abs(score) + 0.3, 1.0)
        
        # 提取关键词
        keywords = []
        for word in self.sentiment_dict["positive"] + self.sentiment_dict["negative"]:
            if word in text_lower:
                keywords.append(word)
        
        return {
            "score": round(score, 2),
            "label": label,
            "confidence": round(confidence, 2),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "keywords": list(set(keywords))[:10]  # 最多10个关键词
        }
    
    def identify_risks(self, text: str, title: str = "") -> List[Dict]:
        """
        识别风险点
        
        原则：所有风险必须有明确证据，不夸大
        """
        risks = []
        text_combined = f"{title} {text}".lower()
        
        # 检查风险关键词
        for keyword in self.risk_keywords:
            if keyword in text_combined:
                # 找到关键词上下文
                idx = text_combined.find(keyword)
                start = max(0, idx - 30)
                end = min(len(text_combined), idx + 30)
                context = text_combined[start:end]
                
                risks.append({
                    "keyword": keyword,
                    "context": context,
                    "severity": self._assess_severity(keyword, context),
                    "evidence": f"文本中出现'{keyword}'"
                })
        
        # 去重
        seen = set()
        unique_risks = []
        for risk in risks:
            if risk["keyword"] not in seen:
                seen.add(risk["keyword"])
                unique_risks.append(risk)
        
        return unique_risks
    
    def identify_opportunities(self, text: str, title: str = "") -> List[Dict]:
        """
        识别机会点
        
        原则：所有机会必须有数据支撑，不臆测
        """
        opportunities = []
        text_combined = f"{title} {text}".lower()
        
        # 检查机会关键词
        for keyword in self.opportunity_keywords:
            if keyword in text_combined:
                idx = text_combined.find(keyword)
                start = max(0, idx - 30)
                end = min(len(text_combined), idx + 30)
                context = text_combined[start:end]
                
                opportunities.append({
                    "keyword": keyword,
                    "context": context,
                    "confidence": self._assess_opportunity_confidence(keyword, context),
                    "evidence": f"文本中出现'{keyword}'"
                })
        
        # 去重
        seen = set()
        unique_opps = []
        for opp in opportunities:
            if opp["keyword"] not in seen:
                seen.add(opp["keyword"])
                unique_opps.append(opp)
        
        return unique_opps
    
    def _assess_severity(self, keyword: str, context: str) -> str:
        """评估风险严重程度"""
        high_severity = ["退市", "爆雷", "st", "违规", "处罚", "调查"]
        medium_severity = ["亏损", "下滑", "减持", "解禁"]
        
        if any(s in keyword for s in high_severity):
            return "high"
        elif any(s in keyword for s in medium_severity):
            return "medium"
        else:
            return "low"
    
    def _assess_opportunity_confidence(self, keyword: str, context: str) -> str:
        """评估机会可信度"""
        high_conf = ["中标", "合同", "订单", "扩产", "超预期"]
        medium_conf = ["增长", "提升", "突破", "龙头"]
        
        if any(c in keyword for c in high_conf):
            return "high"
        elif any(c in keyword for c in medium_conf):
            return "medium"
        else:
            return "low"
    
    def analyze_sector_sentiment(self, sector: str, info_list: List[Dict]) -> Dict:
        """
        分析板块情绪
        
        原则：基于多个信息源的综合判断
        """
        if not info_list:
            return {
                "sector": sector,
                "sentiment": "neutral",
                "score": 0.0,
                "info_count": 0,
                "note": "无足够信息"
            }
        
        scores = []
        positive_count = 0
        negative_count = 0
        
        for info in info_list:
            sentiment = self.analyze_sentiment(info.content if hasattr(info, 'content') else info.get("content", ""))
            scores.append(sentiment["score"])
            
            if sentiment["label"] == "positive":
                positive_count += 1
            elif sentiment["label"] == "negative":
                negative_count += 1
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score > 0.2:
            overall = "positive"
        elif avg_score < -0.2:
            overall = "negative"
        else:
            overall = "neutral"
        
        return {
            "sector": sector,
            "sentiment": overall,
            "score": round(avg_score, 2),
            "info_count": len(info_list),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "confidence": min(abs(avg_score) + 0.3, 1.0)
        }

def main():
    """演示"""
    print("=" * 70)
    print("🎭 情绪分析器 (Layer 3)")
    print("=" * 70)
    
    analyzer = SentimentAnalyzer()
    
    # 测试文本1 - 正面
    text1 = "公司2026年第一季度业绩超预期，营业收入同比增长30%，净利润增长25%，获得大额订单。"
    print("\n📝 测试文本1（正面）:")
    print(f"  {text1}")
    result1 = analyzer.analyze_sentiment(text1)
    print(f"  情绪: {result1['label']} (得分: {result1['score']})")
    print(f"  置信度: {result1['confidence']}")
    print(f"  关键词: {result1['keywords']}")
    
    # 测试文本2 - 负面
    text2 = "公司一季度出现亏损，业绩不及预期，面临调查风险，大股东计划减持。"
    print("\n📝 测试文本2（负面）:")
    print(f"  {text2}")
    result2 = analyzer.analyze_sentiment(text2)
    print(f"  情绪: {result2['label']} (得分: {result2['score']})")
    print(f"  置信度: {result2['confidence']}")
    print(f"  关键词: {result2['keywords']}")
    
    # 风险识别
    print("\n⚠️ 风险识别:")
    risks = analyzer.identify_risks(text2)
    for risk in risks:
        print(f"  [{risk['severity'].upper()}] {risk['keyword']}: {risk['context'][:50]}...")
    
    # 机会识别
    print("\n✅ 机会识别:")
    opps = analyzer.identify_opportunities(text1)
    for opp in opps:
        print(f"  [{opp['confidence'].upper()}] {opp['keyword']}: {opp['context'][:50]}...")

if __name__ == "__main__":
    main()
