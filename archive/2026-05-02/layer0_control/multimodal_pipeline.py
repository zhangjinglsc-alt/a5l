#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L 多模态信息处理链路 (Multi-Modal Information Processing)

支持的信息类型:
- 文本信息 (Text)
- 图片信息 (Image) - 截图、图表、照片
- 公众号文章 (WeChat Article)
- 研报文档 (Research Report)
- PDF文件 (PDF)
- 网页内容 (Web Content)

5步闭环处理所有类型信息
"""

import json
import hashlib
import base64
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

sys.path.insert(0, "/workspace/projects/workspace")

class InfoType(Enum):
    """信息类型"""
    TEXT = "text"                    # 纯文本
    IMAGE = "image"                  # 图片
    WECHAT_ARTICLE = "wechat"        # 公众号文章
    RESEARCH_REPORT = "report"       # 研报
    PDF = "pdf"                      # PDF文件
    WEB = "web"                      # 网页内容
    MIXED = "mixed"                  # 混合内容

class InfoReliabilityLevel(Enum):
    """信息可靠性等级"""
    VERIFIED = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    UNVERIFIED = 1

@dataclass
class MultiModalContent:
    """多模态内容"""
    content_type: InfoType
    raw_data: Any                    # 原始数据
    text_content: str = ""           # 提取的文本
    metadata: Dict = field(default_factory=dict)
    extracted_entities: List[str] = field(default_factory=list)
    ocr_text: str = ""               # OCR识别文本(图片用)
    summary: str = ""                # 内容摘要

@dataclass
class InformationPacket:
    """信息包"""
    packet_id: str
    content: MultiModalContent       # 多模态内容
    source: str
    timestamp: str
    context: Dict = field(default_factory=dict)
    
    # 第2步: 复查结果
    reliability_level: Optional[InfoReliabilityLevel] = None
    reliability_score: float = 0.0
    verification_notes: List[str] = field(default_factory=list)
    
    # 第3步: 分析结果
    skill_analysis: Dict = field(default_factory=dict)
    kiwi_findings: List[Dict] = field(default_factory=list)
    cross_references: List[Dict] = field(default_factory=list)
    
    # 第4步: 理解输出
    understanding: str = ""
    key_insights: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    
    # 第5步: 归档状态
    archived_to_kiwi: bool = False
    strategy_updated: bool = False
    archive_location: str = ""

class ContentExtractor:
    """
    多模态内容提取器
    从不同类型信息中提取结构化内容
    """
    
    @staticmethod
    def extract_from_image(image_path: str) -> MultiModalContent:
        """
        从图片提取内容
        - OCR识别文字
        - 图表识别
        - 图像理解
        """
        print(f"  🖼️  图片内容提取: {image_path}")
        
        # 模拟OCR和图像理解
        ocr_result = ContentExtractor._simulate_ocr(image_path)
        chart_data = ContentExtractor._simulate_chart_analysis(image_path)
        
        return MultiModalContent(
            content_type=InfoType.IMAGE,
            raw_data=image_path,
            text_content=ocr_result["text"],
            ocr_text=ocr_result["text"],
            summary=ocr_result["summary"],
            metadata={
                "image_type": ocr_result["type"],
                "chart_data": chart_data,
                "dimensions": ocr_result.get("dimensions", {})
            },
            extracted_entities=ocr_result["entities"]
        )
    
    @staticmethod
    def extract_from_wechat(url: str) -> MultiModalContent:
        """
        从公众号文章提取内容
        - 标题、作者、发布时间
        - 正文内容
        - 图片和图表
        """
        print(f"  📱 公众号文章提取: {url}")
        
        # 模拟公众号解析
        article = ContentExtractor._simulate_wechat_parse(url)
        
        return MultiModalContent(
            content_type=InfoType.WECHAT_ARTICLE,
            raw_data=url,
            text_content=article["content"],
            summary=article["summary"],
            metadata={
                "title": article["title"],
                "author": article["author"],
                "publish_time": article["publish_time"],
                "read_count": article.get("read_count", 0),
                "like_count": article.get("like_count", 0)
            },
            extracted_entities=article["entities"]
        )
    
    @staticmethod
    def extract_from_report(file_path: str) -> MultiModalContent:
        """
        从研报提取内容
        - 标题、机构、分析师
        - 投资评级、目标价
        - 核心观点
        - 财务数据
        """
        print(f"  📊 研报提取: {file_path}")
        
        # 模拟研报解析
        report = ContentExtractor._simulate_report_parse(file_path)
        
        return MultiModalContent(
            content_type=InfoType.RESEARCH_REPORT,
            raw_data=file_path,
            text_content=report["content"],
            summary=report["summary"],
            metadata={
                "title": report["title"],
                "institution": report["institution"],
                "analysts": report["analysts"],
                "rating": report["rating"],
                "target_price": report["target_price"],
                "publish_date": report["publish_date"],
                "stock_code": report["stock_code"]
            },
            extracted_entities=report["entities"]
        )
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> MultiModalContent:
        """
        从PDF提取内容
        - 文本提取
        - 表格识别
        - 结构解析
        """
        print(f"  📄 PDF提取: {file_path}")
        
        # 模拟PDF解析
        pdf_content = ContentExtractor._simulate_pdf_parse(file_path)
        
        return MultiModalContent(
            content_type=InfoType.PDF,
            raw_data=file_path,
            text_content=pdf_content["text"],
            summary=pdf_content["summary"],
            metadata={
                "page_count": pdf_content["pages"],
                "has_tables": pdf_content["has_tables"],
                "title": pdf_content.get("title", "")
            },
            extracted_entities=pdf_content["entities"]
        )
    
    @staticmethod
    def extract_from_web(url: str) -> MultiModalContent:
        """
        从网页提取内容
        - 标题、正文
        - 发布时间
        - 关键信息
        """
        print(f"  🌐 网页提取: {url}")
        
        # 模拟网页抓取
        web_content = ContentExtractor._simulate_web_scrape(url)
        
        return MultiModalContent(
            content_type=InfoType.WEB,
            raw_data=url,
            text_content=web_content["content"],
            summary=web_content["summary"],
            metadata={
                "title": web_content["title"],
                "site": web_content["site"],
                "publish_time": web_content.get("publish_time"),
            },
            extracted_entities=web_content["entities"]
        )
    
    @staticmethod
    def extract_from_text(text: str) -> MultiModalContent:
        """从纯文本提取内容"""
        return MultiModalContent(
            content_type=InfoType.TEXT,
            raw_data=text,
            text_content=text,
            summary=text[:200] + "..." if len(text) > 200 else text,
            metadata={"char_count": len(text)}
        )
    
    # ============ 模拟方法 ============
    
    @staticmethod
    def _simulate_ocr(image_path: str) -> Dict:
        """模拟OCR识别"""
        # 根据文件名模拟不同类型
        if "chart" in image_path.lower():
            return {
                "text": "股价走势图 2026年1-4月 最高价: 58元 最低价: 42元 当前价: 52元",
                "summary": "股价走势图，显示2026年1-4月股价波动区间42-58元",
                "type": "chart",
                "entities": ["股价", "2026年"],
                "dimensions": {"width": 800, "height": 600}
            }
        elif "report" in image_path.lower():
            return {
                "text": "研报摘要：买入评级 目标价65元 当前PE 25倍",
                "summary": "研报截图，显示买入评级和目标价65元",
                "type": "document_snippet",
                "entities": ["买入", "目标价", "PE"]
            }
        else:
            return {
                "text": "图片中的文字内容...",
                "summary": "图片内容识别",
                "type": "general",
                "entities": []
            }
    
    @staticmethod
    def _simulate_chart_analysis(image_path: str) -> Dict:
        """模拟图表分析"""
        if "chart" in image_path.lower():
            return {
                "chart_type": "line",
                "trend": "upward",
                "key_points": [
                    {"date": "2026-01", "value": 45},
                    {"date": "2026-04", "value": 52}
                ]
            }
        return {}
    
    @staticmethod
    def _simulate_wechat_parse(url: str) -> Dict:
        """模拟公众号解析"""
        return {
            "title": "深度解析：新能源行业投资机会",
            "author": "财经观察",
            "publish_time": "2026-05-01",
            "content": "新能源行业正在迎来新的发展机遇..." + "详细分析内容...",
            "summary": "新能源行业投资分析，看好宁德时代、比亚迪等龙头企业",
            "read_count": 10000,
            "like_count": 500,
            "entities": ["新能源", "宁德时代", "比亚迪"]
        }
    
    @staticmethod
    def _simulate_report_parse(file_path: str) -> Dict:
        """模拟研报解析"""
        return {
            "title": "宁德时代(300750)深度报告：全球龙头地位稳固",
            "institution": "中信证券",
            "analysts": ["张明", "李华"],
            "rating": "买入",
            "target_price": 280.0,
            "current_price": 220.0,
            "publish_date": "2026-05-01",
            "stock_code": "300750.SZ",
            "content": "投资要点：1. 全球动力电池龙头..." + "详细研报内容...",
            "summary": "维持买入评级，目标价280元，看好公司全球龙头地位",
            "entities": ["宁德时代", "300750", "动力电池"]
        }
    
    @staticmethod
    def _simulate_pdf_parse(file_path: str) -> Dict:
        """模拟PDF解析"""
        return {
            "title": "2026年Q1财报",
            "pages": 25,
            "text": "财务数据..." + "管理层讨论...",
            "summary": "Q1财报PDF，包含财务数据和管理层讨论",
            "has_tables": True,
            "entities": ["营收", "净利润", "毛利率"]
        }
    
    @staticmethod
    def _simulate_web_scrape(url: str) -> Dict:
        """模拟网页抓取"""
        return {
            "title": "今日股市行情",
            "site": "新浪财经",
            "content": "今日A股市场..." + "板块表现...",
            "summary": "今日股市行情综述",
            "publish_time": "2026-05-02",
            "entities": ["A股", "上证指数"]
        }

class MultiModalInformationPipeline:
    """
    多模态信息处理链路
    处理文本、图片、公众号、研报、PDF等所有信息类型
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.processing_history = []
        self.extractor = ContentExtractor()
        
        # 初始化KIWI集成
        self.kiwi_integration = None
        self._init_kiwi()
    
    def _init_kiwi(self):
        """初始化KIWI"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer10_kiwi_integration")
            from kiwi_integration import KIWIIntegration
            self.kiwi_integration = KIWIIntegration(self.workspace)
        except Exception as e:
            print(f"⚠️ KIWI初始化失败: {e}")
    
    def process(self, input_data: Union[str, Dict], source: str, 
                input_type: InfoType = None, context: Dict = None) -> InformationPacket:
        """
        主入口: 处理任意类型信息
        
        Args:
            input_data: 输入数据(文本字符串、图片路径、URL等)
            source: 信息来源
            input_type: 信息类型(自动检测 if None)
            context: 上下文
            
        Returns:
            处理后的信息包
        """
        # 生成packet_id
        packet_id = hashlib.md5(f"{str(input_data)}{datetime.now()}".encode()).hexdigest()[:12]
        
        print(f"\n{'='*70}")
        print(f"🔄 多模态信息处理链路启动 | Packet: {packet_id}")
        print(f"{'='*70}")
        
        # 第1步: 内容提取(包含类型检测)
        content = self._step1_extract(input_data, input_type)
        
        # 创建信息包
        packet = InformationPacket(
            packet_id=packet_id,
            content=content,
            source=source,
            timestamp=datetime.now().isoformat(),
            context=context or {}
        )
        
        # 第2-5步: 统一处理
        packet = self._step2_verify(packet)
        packet = self._step3_analyze(packet)
        packet = self._step4_output(packet)
        packet = self._step5_archive(packet)
        
        # 记录历史
        self.processing_history.append(packet)
        
        print(f"\n✅ 多模态信息处理完成 | Packet: {packet_id}")
        print(f"{'='*70}\n")
        
        return packet
    
    def _step1_extract(self, input_data: Union[str, Dict], 
                       input_type: InfoType = None) -> MultiModalContent:
        """
        第1步: 内容提取和类型检测
        """
        print(f"\n📖 Step 1: 内容提取")
        print("-"*70)
        
        # 自动检测类型
        if input_type is None:
            input_type = self._detect_type(input_data)
        
        print(f"  信息类型: {input_type.value}")
        
        # 根据类型提取内容
        if input_type == InfoType.IMAGE:
            content = self.extractor.extract_from_image(input_data)
        elif input_type == InfoType.WECHAT_ARTICLE:
            content = self.extractor.extract_from_wechat(input_data)
        elif input_type == InfoType.RESEARCH_REPORT:
            content = self.extractor.extract_from_report(input_data)
        elif input_type == InfoType.PDF:
            content = self.extractor.extract_from_pdf(input_data)
        elif input_type == InfoType.WEB:
            content = self.extractor.extract_from_web(input_data)
        else:
            content = self.extractor.extract_from_text(input_data)
        
        print(f"  提取文本长度: {len(content.text_content)} 字符")
        print(f"  内容摘要: {content.summary[:50]}...")
        
        return content
    
    def _detect_type(self, input_data: Union[str, Dict]) -> InfoType:
        """自动检测信息类型"""
        if isinstance(input_data, str):
            # 图片文件
            if any(input_data.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                return InfoType.IMAGE
            # PDF文件
            elif input_data.lower().endswith('.pdf'):
                return InfoType.PDF
            # URL检测
            elif input_data.startswith('http'):
                if 'mp.weixin.qq.com' in input_data:
                    return InfoType.WECHAT_ARTICLE
                else:
                    return InfoType.WEB
            # 研报文件路径
            elif 'report' in input_data.lower() or '研报' in input_data:
                return InfoType.RESEARCH_REPORT
        
        return InfoType.TEXT
    
    def _step2_verify(self, packet: InformationPacket) -> InformationPacket:
        """第2步: 复查确认可靠性"""
        print(f"\n🔍 Step 2: 复查确认可靠性")
        print("-"*70)
        
        source = packet.source
        content_type = packet.content.content_type
        
        # 来源可信度评估(根据类型调整)
        source_credibility = {
            "官方公告": 5,
            "交易所": 5,
            "顶级券商研报": 5,
            "Wind": 4,
            "Bloomberg": 4,
            "财新": 4,
            "知名公众号": 3.5,
            "一般公众号": 3,
            "财经媒体": 3,
            "社交媒体": 2,
            "未知": 1
        }
        
        base_credibility = source_credibility.get(source, 2)
        
        # 类型加权
        type_multiplier = {
            InfoType.RESEARCH_REPORT: 1.2,  # 研报更可信
            InfoType.PDF: 1.1,
            InfoType.WECHAT_ARTICLE: 0.9,
            InfoType.IMAGE: 0.8,            # 图片需要额外验证
            InfoType.WEB: 0.9,
            InfoType.TEXT: 1.0
        }
        
        base_credibility *= type_multiplier.get(content_type, 1.0)
        
        # 内容质量检查
        quality_checks = []
        text_content = packet.content.text_content
        
        # 检查是否有具体数据
        if any(c.isdigit() for c in text_content):
            quality_checks.append("✅ 包含具体数据")
            base_credibility += 0.5
        
        # 检查是否有实体
        if packet.content.extracted_entities:
            quality_checks.append(f"✅ 识别到实体: {', '.join(packet.content.extracted_entities[:3])}")
            base_credibility += 0.3
        
        # 图片额外检查
        if content_type == InfoType.IMAGE:
            if packet.content.metadata.get("image_type") == "chart":
                quality_checks.append("✅ 识别为图表类型")
                base_credibility += 0.5
            elif packet.content.metadata.get("image_type") == "document_snippet":
                quality_checks.append("✅ 识别为文档片段")
                base_credibility += 0.3
        
        # 确定可靠性等级
        if base_credibility >= 4.5:
            level = InfoReliabilityLevel.VERIFIED
        elif base_credibility >= 3.5:
            level = InfoReliabilityLevel.HIGH
        elif base_credibility >= 2.5:
            level = InfoReliabilityLevel.MEDIUM
        elif base_credibility >= 1.5:
            level = InfoReliabilityLevel.LOW
        else:
            level = InfoReliabilityLevel.UNVERIFIED
        
        packet.reliability_level = level
        packet.reliability_score = min(base_credibility / 5.0, 1.0)
        packet.verification_notes = quality_checks
        
        print(f"  来源: {source}")
        print(f"  信息类型: {content_type.value}")
        print(f"  可靠性等级: {level.name}")
        print(f"  可靠性评分: {packet.reliability_score:.1%}")
        print(f"  质量检查:")
        for note in quality_checks:
            print(f"    {note}")
        
        return packet
    
    def _step3_analyze(self, packet: InformationPacket) -> InformationPacket:
        """第3步: SKILL分析 + KIWI调阅"""
        print(f"\n🧠 Step 3: SKILL分析 + KIWI调阅")
        print("-"*70)
        
        # 低可靠性信息简化处理
        if packet.reliability_level in [InfoReliabilityLevel.LOW, InfoReliabilityLevel.UNVERIFIED]:
            print(f"  ⚠️ 信息可靠性较低({packet.reliability_level.name})，简化分析")
            packet.skill_analysis = {"status": "simplified_due_to_low_reliability"}
            return packet
        
        # 提取关键词
        text = packet.content.text_content
        keywords = self._extract_keywords(text)
        
        # 根据信息类型进行特定分析
        analysis_result = {
            "info_type": packet.content.content_type.value,
            "key_entities": packet.content.extracted_entities,
            "keywords": keywords[:10],
            "sentiment": self._analyze_sentiment(text),
        }
        
        # 研报特殊分析
        if packet.content.content_type == InfoType.RESEARCH_REPORT:
            metadata = packet.content.metadata
            analysis_result["report_analysis"] = {
                "institution": metadata.get("institution"),
                "rating": metadata.get("rating"),
                "target_price": metadata.get("target_price"),
                "current_price": metadata.get("current_price"),
                "upside": (metadata.get("target_price", 0) / metadata.get("current_price", 1) - 1) * 100 if metadata.get("current_price") else None
            }
        
        # 图片特殊分析
        if packet.content.content_type == InfoType.IMAGE:
            chart_data = packet.content.metadata.get("chart_data", {})
            if chart_data:
                analysis_result["chart_analysis"] = chart_data
        
        packet.skill_analysis = analysis_result
        
        print(f"  实体识别: {', '.join(analysis_result['key_entities'][:3]) if analysis_result['key_entities'] else '无'}")
        print(f"  情感倾向: {analysis_result['sentiment']}")
        
        if "report_analysis" in analysis_result:
            ra = analysis_result["report_analysis"]
            print(f"  研报评级: {ra['rating']}")
            print(f"  目标价: {ra['target_price']}")
            if ra['upside']:
                print(f"  上涨空间: {ra['upside']:.1f}%")
        
        # KIWI调阅
        if self.kiwi_integration and keywords:
            print(f"\n  🔍 KIWI知识调阅:")
            try:
                kiwi_results = self.kiwi_integration.search_knowledge(keywords[0])
                packet.kiwi_findings = [
                    {"title": doc.title, "url": doc.url}
                    for doc in kiwi_results.documents[:3]
                ]
                print(f"    找到 {len(packet.kiwi_findings)} 篇相关文档")
                for finding in packet.kiwi_findings[:2]:
                    print(f"    📄 {finding['title'][:40]}...")
            except Exception as e:
                print(f"    ⚠️ KIWI调阅失败: {e}")
        
        return packet
    
    def _step4_output(self, packet: InformationPacket) -> InformationPacket:
        """第4步: 输出理解结果"""
        print(f"\n📤 Step 4: 输出理解结果")
        print("-"*70)
        
        understanding_parts = []
        content = packet.content
        
        # 基本信息
        understanding_parts.append(f"【信息类型】{content.content_type.value}")
        understanding_parts.append(f"【信息来源】{packet.source}")
        understanding_parts.append(f"【可靠性】{packet.reliability_level.name} ({packet.reliability_score:.0%})")
        
        # 内容摘要
        understanding_parts.append(f"【内容摘要】{content.summary}")
        
        # 类型特定信息
        if content.content_type == InfoType.RESEARCH_REPORT:
            metadata = content.metadata
            understanding_parts.append(f"【研报信息】{metadata.get('institution')} | 评级: {metadata.get('rating')} | 目标价: {metadata.get('target_price')}元")
        elif content.content_type == InfoType.IMAGE:
            img_type = content.metadata.get("image_type", "general")
            understanding_parts.append(f"【图片类型】{img_type}")
            if content.ocr_text:
                understanding_parts.append(f"【OCR识别】{content.ocr_text[:50]}...")
        elif content.content_type == InfoType.WECHAT_ARTICLE:
            metadata = content.metadata
            understanding_parts.append(f"【文章信息】{metadata.get('title')} | 作者: {metadata.get('author')}")
        
        # 分析结果
        if packet.skill_analysis:
            analysis = packet.skill_analysis
            if "sentiment" in analysis:
                understanding_parts.append(f"【情感倾向】{analysis['sentiment']}")
            
            # 关键洞察
            insights = []
            if packet.reliability_score > 0.8:
                insights.append("高可靠信息，可直接用于决策")
            if packet.kiwi_findings:
                insights.append(f"KIWI中找到 {len(packet.kiwi_findings)} 篇相关文档")
            if content.content_type == InfoType.RESEARCH_REPORT:
                ra = analysis.get("report_analysis", {})
                if ra.get("upside") and ra["upside"] > 20:
                    insights.append(f"研报看好，上涨空间{ra['upside']:.0f}%")
            
            packet.key_insights = insights
            if insights:
                understanding_parts.append(f"【关键洞察】{'; '.join(insights)}")
        
        # 行动建议
        actions = self._generate_actions(packet)
        packet.action_items = actions
        if actions:
            understanding_parts.append(f"【建议行动】{'; '.join(actions)}")
        
        packet.understanding = "\n".join(understanding_parts)
        print(packet.understanding)
        
        return packet
    
    def _step5_archive(self, packet: InformationPacket) -> InformationPacket:
        """第5步: 归档总结"""
        print(f"\n💾 Step 5: 归档总结")
        print("-"*70)
        
        # 归档逻辑
        if packet.reliability_score >= 0.6:
            packet.archived_to_kiwi = True
            packet.archive_location = f"kiwi://processed/{datetime.now().strftime('%Y%m%d')}/{packet.packet_id}"
            print(f"  ✅ 已归档到KIWI: {packet.archive_location}")
        else:
            print(f"  ⚠️ 可靠性不足，仅本地存档")
        
        # 策略更新
        if packet.content.content_type == InfoType.RESEARCH_REPORT and packet.reliability_score > 0.8:
            packet.strategy_updated = True
            print(f"  📊 建议更新策略参数(基于高可靠研报)")
        
        print(f"  处理闭环: 完成")
        
        return packet
    
    # ============ 辅助方法 ============
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        common_words = ["的", "了", "是", "在", "和", "与", "对", "为", "将", "等"]
        words = [w for w in text.split() if len(w) > 2 and w not in common_words]
        return list(set(words))[:10]
    
    def _analyze_sentiment(self, text: str) -> str:
        """情感分析"""
        positive = ["涨", "利好", "增长", "突破", "强劲", "优秀", "买入", "推荐", "看好"]
        negative = ["跌", "利空", "下降", "跌破", "疲软", "亏损", "卖出", "回避", "看空"]
        
        p_count = sum(1 for w in positive if w in text)
        n_count = sum(1 for w in negative if w in text)
        
        if p_count > n_count:
            return "偏多"
        elif n_count > p_count:
            return "偏空"
        return "中性"
    
    def _generate_actions(self, packet: InformationPacket) -> List[str]:
        """生成行动建议"""
        actions = []
        
        if packet.reliability_score >= 0.8:
            actions.append("纳入决策参考")
        
        if packet.kiwi_findings:
            actions.append("查阅KIWI相关文档")
        
        # 研报特定建议
        if packet.content.content_type == InfoType.RESEARCH_REPORT:
            analysis = packet.skill_analysis.get("report_analysis", {})
            if analysis.get("rating") == "买入":
                actions.append("关注买入机会")
        
        return actions

def demo():
    """演示多模态信息处理"""
    print("="*70)
    print("🔄 多模态信息处理链路演示")
    print("   支持: 文本 | 图片 | 公众号 | 研报 | PDF")
    print("="*70)
    
    pipeline = MultiModalInformationPipeline()
    
    # 测试场景1: 研报
    print("\n" + "="*70)
    print("📋 场景1: 研报文件")
    print("="*70)
    packet1 = pipeline.process(
        input_data="/path/to/宁德时代深度报告_中信证券.pdf",
        source="顶级券商研报",
        input_type=InfoType.RESEARCH_REPORT
    )
    
    # 测试场景2: 图片(图表)
    print("\n" + "="*70)
    print("📋 场景2: 图片(股价走势图)")
    print("="*70)
    packet2 = pipeline.process(
        input_data="/workspace/projects/media/inbound/stock_chart_2026.jpg",
        source="自研图表",
        input_type=InfoType.IMAGE
    )
    
    # 测试场景3: 公众号文章
    print("\n" + "="*70)
    print("📋 场景3: 公众号文章")
    print("="*70)
    packet3 = pipeline.process(
        input_data="https://mp.weixin.qq.com/s/xxx",
        source="知名公众号",
        input_type=InfoType.WECHAT_ARTICLE
    )
    
    # 汇总
    print("\n" + "="*70)
    print("📊 处理汇总")
    print("="*70)
    print(f"  总共处理: {len(pipeline.processing_history)} 条信息")
    for i, p in enumerate(pipeline.processing_history, 1):
        print(f"  {i}. [{p.content.content_type.value}] {p.source} - {p.reliability_level.name}")
    
    print("\n" + "="*70)
    print("✅ 多模态信息处理链路演示完成！")
    print("="*70)

if __name__ == "__main__":
    demo()
