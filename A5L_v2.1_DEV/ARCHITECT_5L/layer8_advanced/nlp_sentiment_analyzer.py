#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NLP情感分析器 (NLP Sentiment Analyzer)
P3阶段 - 文本挖掘与情感分析

功能:
- 新闻情感分析
- 财报文本挖掘
- 公告情绪识别
- NER实体提取
"""

import re
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import Counter
import numpy as np

sys.path.insert(0, "/workspace/projects/workspace")

class SentimentAnalyzer:
    """情感分析器"""
    
    # 正面词汇词典
    POSITIVE_WORDS = [
        "增长", "上升", "提高", "增加", "盈利", "利润", "收益", "利好",
        "突破", "创新高", "强劲", "优异", "优秀", "成功", "领先", "第一",
        "超预期", "超预期", "回购", "分红", "扩张", "发展", "创新",
        "合作", "签约", "订单", "增长", "涨价", "热销", "爆款"
    ]
    
    # 负面词汇词典
    NEGATIVE_WORDS = [
        "下降", "下滑", "亏损", "亏损", "损失", "债务", "违约", "利空",
        "跌破", "创新低", "疲软", "不佳", "失败", "落后", "垫底",
        "低于预期", "减持", "裁员", "收缩", "停滞", "违规", "调查",
        "诉讼", "召回", "停产", "滞销", "库存积压"
    ]
    
    # 程度副词
    INTENSIFIERS = {
        "大幅": 2.0,
        "显著": 1.8,
        "明显": 1.5,
        "较": 1.3,
        "略有": 0.8,
        "稍微": 0.6
    }
    
    def __init__(self):
        print("📝 NLP情感分析器初始化")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        分析文本情感
        
        Args:
            text: 待分析文本
            
        Returns:
            情感分析结果
        """
        # 统计正负词汇
        positive_count = 0
        negative_count = 0
        positive_words_found = []
        negative_words_found = []
        
        # 检查正面词汇
        for word in self.POSITIVE_WORDS:
            if word in text:
                count = text.count(word)
                positive_count += count
                positive_words_found.extend([word] * count)
        
        # 检查负面词汇
        for word in self.NEGATIVE_WORDS:
            if word in text:
                count = text.count(word)
                negative_count += count
                negative_words_found.extend([word] * count)
        
        # 检查程度副词
        intensity = 1.0
        for intensifier, factor in self.INTENSIFIERS.items():
            if intensifier in text:
                intensity = max(intensity, factor)
        
        # 计算情感得分 (-1 到 1)
        total_words = positive_count + negative_count
        if total_words == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_count - negative_count) / total_words * intensity
        
        # 情感标签
        if sentiment_score > 0.3:
            sentiment_label = "强烈正面"
        elif sentiment_score > 0.1:
            sentiment_label = "正面"
        elif sentiment_score < -0.3:
            sentiment_label = "强烈负面"
        elif sentiment_score < -0.1:
            sentiment_label = "负面"
        else:
            sentiment_label = "中性"
        
        # 置信度 (基于词汇数量)
        confidence = min(0.95, 0.5 + total_words * 0.05)
        
        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "confidence": confidence,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_words": list(set(positive_words_found)),
            "negative_words": list(set(negative_words_found)),
            "intensity": intensity,
            "text_length": len(text)
        }
    
    def analyze_news(self, title: str, content: str = "") -> Dict:
        """分析新闻情感"""
        full_text = title + " " + content
        result = self.analyze_sentiment(full_text)
        result["type"] = "news"
        result["title"] = title[:50] + "..." if len(title) > 50 else title
        return result
    
    def analyze_earnings_report(self, text: str) -> Dict:
        """分析财报文本"""
        result = self.analyze_sentiment(text)
        
        # 提取关键财务指标 (简化)
        metrics = self._extract_financial_metrics(text)
        result["financial_metrics"] = metrics
        result["type"] = "earnings_report"
        
        return result
    
    def analyze_announcement(self, text: str) -> Dict:
        """分析公告文本"""
        result = self.analyze_sentiment(text)
        
        # 识别公告类型
        announcement_type = self._classify_announcement(text)
        result["announcement_type"] = announcement_type
        result["type"] = "announcement"
        
        return result
    
    def _extract_financial_metrics(self, text: str) -> Dict:
        """提取财务指标"""
        metrics = {}
        
        # 收入/营收
        revenue_match = re.search(r'营收[^\d]*(\d+\.?\d*)[^\d]*亿', text)
        if revenue_match:
            metrics['revenue'] = float(revenue_match.group(1))
        
        # 净利润
        profit_match = re.search(r'净利润[^\d]*(\d+\.?\d*)[^\d]*亿', text)
        if profit_match:
            metrics['net_profit'] = float(profit_match.group(1))
        
        # 增长率
        growth_match = re.search(r'增长[^\d]*(\d+\.?\d*)[^\d]*%', text)
        if growth_match:
            metrics['growth_rate'] = float(growth_match.group(1)) / 100
        
        return metrics
    
    def _classify_announcement(self, text: str) -> str:
        """分类公告类型"""
        if "回购" in text:
            return "股份回购"
        elif "减持" in text:
            return "股东减持"
        elif "分红" in text or "派息" in text:
            return "分红派息"
        elif "增发" in text or "配股" in text:
            return "再融资"
        elif "业绩预告" in text:
            return "业绩预告"
        elif "重大合同" in text:
            return "重大合同"
        else:
            return "其他公告"

class NERExtractor:
    """命名实体提取器"""
    
    def __init__(self):
        print("🏷️ NER实体提取器初始化")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        提取命名实体
        
        Args:
            text: 待分析文本
            
        Returns:
            实体字典
        """
        entities = {
            "companies": [],
            "persons": [],
            "locations": [],
            "products": [],
            "industries": [],
            "dates": []
        }
        
        # 提取公司名 (简化: 匹配XX股份、XX集团等)
        company_pattern = r'([\u4e00-\u9fa5]{2,8}(?:股份|集团|科技|实业|控股|公司))'
        companies = re.findall(company_pattern, text)
        entities["companies"] = list(set(companies))
        
        # 提取人名 (简化: 匹配2-3字人名)
        # 实际应用需要使用专业的人名词典或模型
        
        # 提取日期
        date_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{4}/\d{2}/\d{2})'
        ]
        for pattern in date_patterns:
            dates = re.findall(pattern, text)
            entities["dates"].extend(dates)
        entities["dates"] = list(set(entities["dates"]))
        
        # 提取行业关键词
        industry_keywords = ["半导体", "新能源", "医药", "金融", "地产", "消费", "科技"]
        for keyword in industry_keywords:
            if keyword in text:
                entities["industries"].append(keyword)
        
        return entities

class TopicModeler:
    """主题建模器"""
    
    def __init__(self):
        # 预定义主题关键词
        self.topics = {
            "业绩增长": ["增长", "盈利", "业绩", "利润", "收入", "营收"],
            "技术创新": ["技术", "创新", "研发", "专利", "新产品", "突破"],
            "市场竞争": ["市场", "竞争", "份额", "客户", "订单", "销售"],
            "资本运作": ["融资", "上市", "并购", "重组", "投资", "股权"],
            "风险事件": ["亏损", "违约", "诉讼", "调查", "召回", "风险"],
            "政策影响": ["政策", "监管", "法规", "补贴", "税收", "审批"]
        }
        
        print("🎯 主题建模器初始化")
    
    def identify_topics(self, text: str) -> List[Tuple[str, float]]:
        """
        识别文本主题
        
        Args:
            text: 待分析文本
            
        Returns:
            主题列表 (主题, 得分)
        """
        topic_scores = []
        
        for topic_name, keywords in self.topics.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += text.count(keyword)
            
            # 归一化得分
            if len(keywords) > 0:
                normalized_score = score / len(keywords)
                if normalized_score > 0:
                    topic_scores.append((topic_name, normalized_score))
        
        # 排序
        topic_scores.sort(key=lambda x: x[1], reverse=True)
        
        return topic_scores[:3]  # 返回前3个主题

class NLPAnalyzer:
    """NLP分析器 (整合)"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ner_extractor = NERExtractor()
        self.topic_modeler = TopicModeler()
        
        print("🧠 NLP分析系统初始化")
    
    def comprehensive_analysis(self, text: str, text_type: str = "news") -> Dict:
        """
        综合分析文本
        
        Args:
            text: 待分析文本
            text_type: 文本类型 (news/earnings/announcement)
            
        Returns:
            综合分析结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "text_type": text_type,
            "text_length": len(text)
        }
        
        # 情感分析
        if text_type == "news":
            result["sentiment"] = self.sentiment_analyzer.analyze_news(text[:100], text)
        elif text_type == "earnings":
            result["sentiment"] = self.sentiment_analyzer.analyze_earnings_report(text)
        elif text_type == "announcement":
            result["sentiment"] = self.sentiment_analyzer.analyze_announcement(text)
        else:
            result["sentiment"] = self.sentiment_analyzer.analyze_sentiment(text)
        
        # 实体提取
        result["entities"] = self.ner_extractor.extract_entities(text)
        
        # 主题识别
        result["topics"] = self.topic_modeler.identify_topics(text)
        
        return result
    
    def batch_analyze(self, texts: List[Dict]) -> List[Dict]:
        """
        批量分析
        
        Args:
            texts: 文本列表，每项包含 {'text': ..., 'type': ..., 'metadata': ...}
            
        Returns:
            分析结果列表
        """
        results = []
        for item in texts:
            text = item.get('text', '')
            text_type = item.get('type', 'news')
            
            analysis = self.comprehensive_analysis(text, text_type)
            analysis['metadata'] = item.get('metadata', {})
            
            results.append(analysis)
        
        return results
    
    def generate_summary(self, analyses: List[Dict]) -> str:
        """生成分析摘要"""
        # 统计情感分布
        sentiment_counts = Counter([a['sentiment']['sentiment_label'] for a in analyses])
        
        # 统计主题
        all_topics = []
        for a in analyses:
            all_topics.extend([t[0] for t in a.get('topics', [])])
        topic_counts = Counter(all_topics)
        
        # 统计实体
        all_companies = []
        for a in analyses:
            all_companies.extend(a.get('entities', {}).get('companies', []))
        company_counts = Counter(all_companies)
        
        summary = f"""# NLP分析摘要

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**分析文本数**: {len(analyses)}

## 情感分布

"""
        for sentiment, count in sentiment_counts.most_common():
            pct = count / len(analyses) * 100
            summary += f"- {sentiment}: {count} ({pct:.1f}%)\n"
        
        summary += "\n## 热门主题\n\n"
        for topic, count in topic_counts.most_common(5):
            summary += f"- {topic}: {count}次\n"
        
        summary += "\n## 提及公司\n\n"
        for company, count in company_counts.most_common(10):
            summary += f"- {company}: {count}次\n"
        
        summary += "\n## 关键洞察\n\n"
        
        # 自动洞察
        dominant_sentiment = sentiment_counts.most_common(1)[0][0]
        summary += f"1. 整体情绪偏向: {dominant_sentiment}\n"
        
        if topic_counts:
            top_topic = topic_counts.most_common(1)[0][0]
            summary += f"2. 最受关注主题: {top_topic}\n"
        
        summary += f"3. 平均文本长度: {np.mean([a['text_length'] for a in analyses]):.0f}字\n"
        
        return summary

def demo():
    """演示NLP分析器"""
    print("="*70)
    print("🧠 NLP情感分析器演示")
    print("="*70)
    print()
    
    nlp = NLPAnalyzer()
    
    # 测试文本
    texts = [
        {
            "text": "平安银行发布2026年一季报，营收同比增长15.3%，净利润增长12.8%，业绩表现优异。",
            "type": "earnings",
            "metadata": {"source": "财报", "symbol": "000001.SZ"}
        },
        {
            "text": "贵州茅台宣布大幅提价，终端售价上涨20%，市场反应积极，股价创历史新高。",
            "type": "news",
            "metadata": {"source": "新闻", "symbol": "600519.SH"}
        },
        {
            "text": "某科技公司因财务造假被证监会立案调查，股价连续跌停，投资者损失惨重。",
            "type": "news",
            "metadata": {"source": "新闻", "symbol": "UNKNOWN"}
        },
        {
            "text": "比亚迪发布新款电动车，技术突破显著，订单火爆，有望引领行业发展。",
            "type": "news",
            "metadata": {"source": "新闻", "symbol": "002594.SZ"}
        }
    ]
    
    # 批量分析
    print("📝 批量分析文本...\n")
    results = nlp.batch_analyze(texts)
    
    for i, result in enumerate(results, 1):
        print(f"{'='*70}")
        print(f"文本 {i}: {result['metadata'].get('symbol', 'N/A')}")
        print(f"{'='*70}")
        
        # 情感
        sentiment = result['sentiment']
        print(f"\n情感分析:")
        print(f"   得分: {sentiment['sentiment_score']:+.2f}")
        print(f"   标签: {sentiment['sentiment_label']}")
        print(f"   置信度: {sentiment['confidence']:.1%}")
        
        if sentiment.get('positive_words'):
            print(f"   正面词: {', '.join(sentiment['positive_words'][:5])}")
        if sentiment.get('negative_words'):
            print(f"   负面词: {', '.join(sentiment['negative_words'][:5])}")
        
        # 实体
        entities = result['entities']
        if entities.get('companies'):
            print(f"\n实体识别:")
            print(f"   公司: {', '.join(entities['companies'][:3])}")
        
        # 主题
        topics = result['topics']
        if topics:
            print(f"\n主题识别:")
            for topic, score in topics[:3]:
                print(f"   - {topic}: {score:.2f}")
    
    # 生成摘要
    print(f"\n{'='*70}")
    print("📊 生成分析摘要")
    print(f"{'='*70}\n")
    summary = nlp.generate_summary(results)
    print(summary)
    
    print("="*70)
    print("✅ NLP情感分析器演示完成!")
    print("="*70)

if __name__ == "__main__":
    demo()
