#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研报阅读分析器 (Research Report Analyzer)
Layer 3 增强模块 - 研报深度理解能力

功能:
- 研报PDF/文本解析
- 结构化信息提取 (评级/目标价/核心逻辑)
- 多研报对比分析
- 研报可信度评估
- 与A5L Pipeline集成
"""

import re
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

sys.path.insert(0, "/workspace/projects/workspace")

@dataclass
class ResearchReport:
    """研报数据类"""
    report_id: str
    title: str
    author: str
    institution: str  # 券商/机构
    publish_date: str
    symbol: str  # 股票代码
    stock_name: str
    
    # 核心内容
    rating: str  # 评级 (买入/增持/中性/减持)
    target_price: Optional[float]  # 目标价
    current_price: Optional[float]  # 当前价格 (研报发布时)
    upside_potential: Optional[float]  # 上涨空间
    
    # 分析内容
    investment_highlights: List[str]  # 投资要点
    core_logic: str  # 核心逻辑
    risk_warnings: List[str]  # 风险提示
    financial_forecast: Dict  # 盈利预测
    
    # 元数据
    page_count: int
    word_count: int
    source_url: Optional[str]
    credibility_score: float  # 可信度评分
    
    # 原始文本
    raw_text: str

class ReportPDFParser:
    """研报PDF解析器"""
    
    def __init__(self):
        self.institution_keywords = [
            "中信证券", "中信建投", "中金公司", "国泰君安", "海通证券",
            "华泰证券", "招商证券", "广发证券", "申万宏源", "兴业证券",
            "东方证券", "光大证券", "平安证券", "国信证券", "长江证券"
        ]
    
    def parse_from_text(self, text: str, metadata: Dict = None) -> ResearchReport:
        """
        从文本解析研报
        
        Args:
            text: 研报文本内容
            metadata: 元数据
            
        Returns:
            ResearchReport对象
        """
        if metadata is None:
            metadata = {}
        
        # 生成report_id
        report_id = hashlib.md5(text[:500].encode()).hexdigest()[:12]
        
        # 提取机构
        institution = self._extract_institution(text)
        
        # 提取股票信息
        symbol, stock_name = self._extract_stock_info(text)
        
        # 提取评级
        rating = self._extract_rating(text)
        
        # 提取目标价
        target_price = self._extract_target_price(text)
        current_price = self._extract_current_price(text)
        upside = self._calculate_upside(target_price, current_price)
        
        # 提取投资要点
        highlights = self._extract_investment_highlights(text)
        
        # 提取核心逻辑
        core_logic = self._extract_core_logic(text)
        
        # 提取风险提示
        risks = self._extract_risk_warnings(text)
        
        # 提取盈利预测
        forecast = self._extract_financial_forecast(text)
        
        # 计算可信度
        credibility = self._calculate_credibility(text, institution)
        
        return ResearchReport(
            report_id=report_id,
            title=metadata.get('title', self._extract_title(text)),
            author=metadata.get('author', self._extract_author(text)),
            institution=institution,
            publish_date=metadata.get('publish_date', self._extract_date(text)),
            symbol=symbol,
            stock_name=stock_name,
            rating=rating,
            target_price=target_price,
            current_price=current_price,
            upside_potential=upside,
            investment_highlights=highlights,
            core_logic=core_logic,
            risk_warnings=risks,
            financial_forecast=forecast,
            page_count=metadata.get('page_count', 0),
            word_count=len(text),
            source_url=metadata.get('source_url'),
            credibility_score=credibility,
            raw_text=text[:5000]  # 只保存前5000字符
        )
    
    def _extract_institution(self, text: str) -> str:
        """提取券商/机构名称"""
        for inst in self.institution_keywords:
            if inst in text:
                return inst
        
        # 尝试匹配XX证券研究所
        match = re.search(r'(\w+证券|\w+期货|\w+投行)(?:研究所|研究中心)', text)
        if match:
            return match.group(1)
        
        return "未知机构"
    
    def _extract_stock_info(self, text: str) -> Tuple[str, str]:
        """提取股票代码和名称"""
        # 匹配模式: 股票代码: 600000.SH 股票名称: 浦发银行
        code_match = re.search(r'(?:股票代码|代码)[：:]\s*(\d{6}\.(?:SH|SZ|sh|sz))', text)
        name_match = re.search(r'(?:股票名称|简称)[：:]\s*([\u4e00-\u9fa5]{2,10})', text)
        
        symbol = code_match.group(1).upper() if code_match else ""
        name = name_match.group(1) if name_match else ""
        
        # 如果没找到，尝试从标题提取
        if not symbol:
            code_match2 = re.search(r'(\d{6})[\.\s]*([\u4e00-\u9fa5]+)', text[:200])
            if code_match2:
                symbol = code_match2.group(1)
                name = code_match2.group(2)
        
        return symbol, name
    
    def _extract_rating(self, text: str) -> str:
        """提取评级"""
        rating_patterns = [
            r'评级[：:]\s*(买入|增持|中性|减持|卖出|强烈推荐|推荐)',
            r'投资评级[：:]\s*(买入|增持|中性|减持|卖出)',
            r'(?:维持|给予|上调|下调).{0,5}(买入|增持|中性|减持|卖出)评级',
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "未明确"
    
    def _extract_target_price(self, text: str) -> Optional[float]:
        """提取目标价"""
        # 匹配目标价: XX.XX元
        patterns = [
            r'目标价[：:]\s*(\d+\.?\d*)\s*元',
            r'目标价格[：:]\s*(\d+\.?\d*)',
            r'6-?12个月目标价[：:]\s*(\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_current_price(self, text: str) -> Optional[float]:
        """提取当前价格"""
        patterns = [
            r'当前价[：:]\s*(\d+\.?\d*)',
            r'收盘价[：:]\s*(\d+\.?\d*)',
            r'现价[：:]\s*(\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return None
    
    def _calculate_upside(self, target: Optional[float], current: Optional[float]) -> Optional[float]:
        """计算上涨空间"""
        if target and current and current > 0:
            return (target - current) / current
        return None
    
    def _extract_investment_highlights(self, text: str) -> List[str]:
        """提取投资要点"""
        highlights = []
        
        # 匹配投资要点部分
        pattern = r'投资要点[：:]?(.*?)(?:核心逻辑|盈利预测|风险提示|$)'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            highlights_text = match.group(1)
            # 提取 bullet points
            bullets = re.findall(r'[•·\-\d+\.\、]\s*([^\n]+)', highlights_text)
            highlights = [b.strip() for b in bullets if len(b.strip()) > 5][:5]
        
        return highlights
    
    def _extract_core_logic(self, text: str) -> str:
        """提取核心逻辑"""
        patterns = [
            r'核心逻辑[：:]?(.*?)(?:投资要点|盈利预测|风险提示|$)',
            r'投资逻辑[：:]?(.*?)(?:盈利预测|风险提示|$)',
            r'核心观点[：:]?(.*?)(?:盈利预测|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                logic = match.group(1).strip()
                return logic[:500] if len(logic) > 500 else logic
        
        return "未明确提取"
    
    def _extract_risk_warnings(self, text: str) -> List[str]:
        """提取风险提示"""
        risks = []
        
        pattern = r'风险提示[：:]?(.*?)(?:投资建议|分析师声明|$)'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            risks_text = match.group(1)
            bullets = re.findall(r'[•·\-\d+\.\、]\s*([^\n]+)', risks_text)
            risks = [b.strip() for b in bullets if len(b.strip()) > 5][:5]
        
        return risks
    
    def _extract_financial_forecast(self, text: str) -> Dict:
        """提取盈利预测"""
        forecast = {}
        
        # 尝试提取EPS预测
        eps_pattern = r'EPS.*?([\d\.]+).*?([\d\.]+).*?([\d\.]+)'
        eps_match = re.search(eps_pattern, text)
        if eps_match:
            forecast['eps_current'] = float(eps_match.group(1))
            forecast['eps_next'] = float(eps_match.group(2))
            forecast['eps_following'] = float(eps_match.group(3))
        
        # 尝试提取PE
        pe_pattern = r'PE.*?([\d\.]+)'
        pe_match = re.search(pe_pattern, text)
        if pe_match:
            forecast['pe'] = float(pe_match.group(1))
        
        return forecast
    
    def _extract_title(self, text: str) -> str:
        """提取标题"""
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                return line
        return "未命名研报"
    
    def _extract_author(self, text: str) -> str:
        """提取分析师"""
        pattern = r'(?:分析师|作者)[：:]\s*([\u4e00-\u9fa5]{2,4})'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return "未知"
    
    def _extract_date(self, text: str) -> str:
        """提取发布日期"""
        pattern = r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?'
        match = re.search(pattern, text)
        if match:
            return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
        return datetime.now().strftime('%Y-%m-%d')
    
    def _calculate_credibility(self, text: str, institution: str) -> float:
        """计算可信度评分"""
        score = 0.5  # 基础分
        
        # 知名机构加分
        if institution in self.institution_keywords:
            score += 0.2
        
        # 内容完整性加分
        if "投资要点" in text:
            score += 0.1
        if "风险提示" in text:
            score += 0.1
        if "盈利预测" in text or "EPS" in text:
            score += 0.1
        
        return min(1.0, score)

class ReportAnalyzer:
    """研报分析器"""
    
    def __init__(self):
        self.parser = ReportPDFParser()
    
    def analyze_single_report(self, text: str, metadata: Dict = None) -> Dict:
        """分析单篇研报"""
        report = self.parser.parse_from_text(text, metadata)
        
        # 生成分析摘要
        summary = self._generate_summary(report)
        
        # 投资建议
        recommendation = self._generate_recommendation(report)
        
        return {
            "report": asdict(report),
            "summary": summary,
            "recommendation": recommendation,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def compare_reports(self, reports: List[ResearchReport]) -> Dict:
        """对比多篇研报"""
        if not reports:
            return {}
        
        # 评级分布
        rating_counts = {}
        for r in reports:
            rating_counts[r.rating] = rating_counts.get(r.rating, 0) + 1
        
        # 目标价范围
        target_prices = [r.target_price for r in reports if r.target_price]
        avg_target = sum(target_prices) / len(target_prices) if target_prices else None
        
        # 一致性分析
        consensus = "一致看好" if rating_counts.get('买入', 0) >= len(reports) * 0.6 else "观点分化"
        
        # 机构覆盖
        institutions = list(set([r.institution for r in reports]))
        
        return {
            "report_count": len(reports),
            "rating_distribution": rating_counts,
            "target_price_range": {
                "min": min(target_prices) if target_prices else None,
                "max": max(target_prices) if target_prices else None,
                "avg": avg_target
            },
            "consensus": consensus,
            "covering_institutions": institutions,
            "latest_report": max(reports, key=lambda x: x.publish_date).publish_date if reports else None
        }
    
    def _generate_summary(self, report: ResearchReport) -> str:
        """生成研报摘要"""
        summary = f"""【研报摘要】{report.stock_name} ({report.symbol})

发布机构: {report.institution}
分析师: {report.author}
发布日期: {report.publish_date}
评级: {report.rating}
目标价: {report.target_price}元 (上涨空间: {report.upside_potential:.1%})
可信度: {report.credibility_score:.0%}

核心逻辑:
{report.core_logic[:200]}...

投资要点:
"""
        for i, point in enumerate(report.investment_highlights[:3], 1):
            summary += f"{i}. {point}\n"
        
        return summary
    
    def _generate_recommendation(self, report: ResearchReport) -> Dict:
        """生成投资建议"""
        # 基于评级和上涨空间给出建议
        if report.rating in ['买入', '强烈推荐'] and report.upside_potential and report.upside_potential > 0.2:
            action = "强烈关注"
            confidence = "high"
        elif report.rating in ['买入', '增持'] and report.upside_potential and report.upside_potential > 0.1:
            action = "重点关注"
            confidence = "medium"
        elif report.rating == '中性':
            action = "观望"
            confidence = "low"
        else:
            action = "谨慎"
            confidence = "low"
        
        return {
            "action": action,
            "confidence": confidence,
            "reason": f"机构评级{report.rating}" + (f"，目标价上涨空间{report.upside_potential:.1%}" if report.upside_potential else "")
        }

def demo():
    """演示研报阅读分析器"""
    print("="*70)
    print("📄 研报阅读分析器演示")
    print("="*70)
    print()
    
    # 模拟研报文本
    sample_report = """
宁德时代（300750.SZ）深度研究报告
发布机构: 中信证券研究所
分析师: 王军
发布日期: 2026年5月1日

股票代码: 300750.SZ
股票名称: 宁德时代
当前价: 180.50元
目标价: 250.00元
评级: 买入

投资要点:
• 全球动力电池龙头地位稳固，市占率持续提升
• 技术领先优势明显，研发实力雄厚
• 海外产能加速布局，全球化进程顺利
• 储能业务快速发展，第二增长曲线明确

核心逻辑:
宁德时代作为全球动力电池龙头，在技术、产能、客户等方面均具备显著优势。
随着新能源汽车渗透率持续提升，公司动力电池业务将保持高速增长。
同时，储能业务成为新的增长引擎，公司在该领域同样具备技术和成本优势。
我们预计公司未来三年净利润复合增速将达到30%以上。

盈利预测:
预计2026-2028年EPS分别为8.5元、11.2元、14.0元，对应PE分别为21x、16x、13x。

风险提示:
• 新能源汽车销量不及预期
• 原材料价格大幅波动
• 行业竞争加剧导致毛利率下降
• 海外市场政策风险
    """
    
    # 初始化分析器
    analyzer = ReportAnalyzer()
    
    # 分析单篇研报
    print("📝 分析单篇研报...\n")
    result = analyzer.analyze_single_report(sample_report)
    
    report = result['report']
    print(f"研报标题: {report['title']}")
    print(f"股票: {report['stock_name']} ({report['symbol']})")
    print(f"发布机构: {report['institution']}")
    print(f"分析师: {report['author']}")
    print(f"发布日期: {report['publish_date']}")
    print(f"评级: {report['rating']}")
    print(f"目标价: {report['target_price']}元")
    print(f"当前价: {report['current_price']}元")
    upside = report['upside_potential']
    print(f"上涨空间: {upside:.1%}" if upside else "上涨空间: 未计算")
    print(f"可信度: {report['credibility_score']:.0%}")
    print()
    
    print("投资要点:")
    for i, point in enumerate(report['investment_highlights'], 1):
        print(f"  {i}. {point}")
    print()
    
    print("核心逻辑:")
    print(f"  {report['core_logic'][:150]}...")
    print()
    
    print("风险提示:")
    for i, risk in enumerate(report['risk_warnings'], 1):
        print(f"  {i}. {risk}")
    print()
    
    print("投资建议:")
    rec = result['recommendation']
    print(f"  建议操作: {rec['action']}")
    print(f"  置信度: {rec['confidence']}")
    print(f"  理由: {rec['reason']}")
    
    print()
    print("="*70)
    print("✅ 研报阅读分析器演示完成!")
    print("="*70)
    print()
    print("💡 此模块可集成到A5L的Layer 3，增强市场信息理解能力")

if __name__ == "__main__":
    demo()
