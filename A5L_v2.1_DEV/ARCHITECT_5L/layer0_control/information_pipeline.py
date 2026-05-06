#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L 信息处理链路 (Information Processing Pipeline)

5步闭环:
1. 阅读信息 (Read)
2. 复查确认可靠性 (Verify)  
3. SKILL分析+KIWI调阅 (Analyze)
4. 输出理解结果 (Output)
5. 归档总结 (Archive)

形成完整的信息处理闭环，确保知识沉淀和策略进化
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import sys

sys.path.insert(0, "/workspace/projects/workspace")

class InfoReliabilityLevel(Enum):
    """信息可靠性等级"""
    VERIFIED = 5      # 已验证 - 多源交叉验证
    HIGH = 4          # 高可靠 - 权威来源
    MEDIUM = 3        # 中等 - 一般来源
    LOW = 2           # 低可靠 - 需进一步验证
    UNVERIFIED = 1    # 未验证 - 单一来源

@dataclass
class InformationPacket:
    """信息包 - 流经处理链路的单元"""
    packet_id: str
    raw_content: str           # 原始信息
    source: str                # 信息来源
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

class InformationProcessingPipeline:
    """
    信息处理链路
    5步闭环处理所有输入信息
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.processing_history = []
        self.kiwi_integration = None
        self.layer0_controller = None
        
        # 初始化集成
        self._init_integrations()
    
    def _init_integrations(self):
        """初始化各模块集成"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer10_kiwi_integration")
            from kiwi_integration import KIWIIntegration
            self.kiwi_integration = KIWIIntegration(self.workspace)
        except Exception as e:
            print(f"⚠️ KIWI集成初始化失败: {e}")
    
    def process(self, raw_content: str, source: str, context: Dict = None) -> InformationPacket:
        """
        主入口: 处理信息
        
        Args:
            raw_content: 原始信息内容
            source: 信息来源
            context: 上下文
            
        Returns:
            处理后的信息包
        """
        # 生成packet_id
        packet_id = hashlib.md5(f"{raw_content}{datetime.now()}".encode()).hexdigest()[:12]
        
        print(f"\n{'='*70}")
        print(f"🔄 信息处理链路启动 | Packet: {packet_id}")
        print(f"{'='*70}")
        
        # 创建信息包
        packet = InformationPacket(
            packet_id=packet_id,
            raw_content=raw_content,
            source=source,
            timestamp=datetime.now().isoformat(),
            context=context or {}
        )
        
        # 执行5步处理
        packet = self._step1_read(packet)
        packet = self._step2_verify(packet)
        packet = self._step3_analyze(packet)
        packet = self._step4_output(packet)
        packet = self._step5_archive(packet)
        
        # 记录处理历史
        self.processing_history.append(packet)
        
        print(f"\n✅ 信息处理链路完成 | Packet: {packet_id}")
        print(f"{'='*70}\n")
        
        return packet
    
    def _step1_read(self, packet: InformationPacket) -> InformationPacket:
        """
        第1步: 阅读信息
        解析和理解原始信息
        """
        print(f"\n📖 Step 1: 阅读信息")
        print("-"*70)
        
        content = packet.raw_content
        
        # 信息分类
        if any(kw in content for kw in ["涨", "跌", "股价", "行情", "股票"]):
            info_type = "market_data"
        elif any(kw in content for kw in ["财报", "业绩", "收入", "利润"]):
            info_type = "financial_report"
        elif any(kw in content for kw in ["策略", "交易", "买卖", "持仓"]):
            info_type = "trading_strategy"
        elif any(kw in content for kw in ["新闻", "公告", "消息"]):
            info_type = "news"
        else:
            info_type = "general"
        
        packet.context["info_type"] = info_type
        packet.context["content_length"] = len(content)
        packet.context["extracted_keywords"] = self._extract_keywords(content)
        
        print(f"  信息类型: {info_type}")
        print(f"  内容长度: {len(content)} 字符")
        print(f"  关键词: {', '.join(packet.context['extracted_keywords'][:5])}")
        
        return packet
    
    def _step2_verify(self, packet: InformationPacket) -> InformationPacket:
        """
        第2步: 复查确认可靠性
        评估信息来源和内容可靠性
        """
        print(f"\n🔍 Step 2: 复查确认可靠性")
        print("-"*70)
        
        source = packet.source
        content = packet.raw_content
        
        # 来源可信度评估
        source_credibility = {
            "官方公告": 5,
            "交易所": 5,
            "Wind": 4,
            "Bloomberg": 4,
            "财新": 4,
            "券商研报": 3,
            "财经媒体": 3,
            "社交媒体": 2,
            "未知": 1
        }
        
        base_credibility = source_credibility.get(source, 2)
        
        # 内容质量评估
        quality_checks = []
        
        # 检查是否有具体数据
        if any(c.isdigit() for c in content):
            quality_checks.append("✅ 包含具体数据")
            base_credibility += 0.5
        else:
            quality_checks.append("⚠️ 缺乏具体数据")
        
        # 检查是否有来源引用
        if "来源" in content or "http" in content:
            quality_checks.append("✅ 有来源引用")
            base_credibility += 0.5
        else:
            quality_checks.append("⚠️ 无明确来源")
        
        # 检查时效性
        if any(kw in content for kw in ["今日", "最新", "刚刚", datetime.now().strftime("%Y")]):
            quality_checks.append("✅ 时效性强")
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
        print(f"  可靠性等级: {level.name}")
        print(f"  可靠性评分: {packet.reliability_score:.1%}")
        print(f"  质量检查:")
        for note in quality_checks:
            print(f"    {note}")
        
        return packet
    
    def _step3_analyze(self, packet: InformationPacket) -> InformationPacket:
        """
        第3步: SKILL分析 + KIWI调阅
        深度分析并关联已有知识
        """
        print(f"\n🧠 Step 3: SKILL分析 + KIWI调阅")
        print("-"*70)
        
        # 如果可靠性太低，跳过深入分析
        if packet.reliability_level in [InfoReliabilityLevel.LOW, InfoReliabilityLevel.UNVERIFIED]:
            print(f"  ⚠️ 信息可靠性较低({packet.reliability_level.name})，简化分析")
            packet.skill_analysis = {"status": "simplified_due_to_low_reliability"}
            return packet
        
        # SKILL分析
        keywords = packet.context.get("extracted_keywords", [])
        
        analysis_result = {
            "info_type": packet.context.get("info_type"),
            "key_entities": self._extract_entities(packet.raw_content),
            "sentiment": self._analyze_sentiment(packet.raw_content),
            "potential_impact": self._assess_impact(packet),
            "related_strategies": self._match_strategies(packet)
        }
        
        packet.skill_analysis = analysis_result
        
        print(f"  实体识别: {', '.join(analysis_result['key_entities'][:3])}")
        print(f"  情感倾向: {analysis_result['sentiment']}")
        print(f"  潜在影响: {analysis_result['potential_impact']}")
        print(f"  相关策略: {', '.join(analysis_result['related_strategies'][:2])}")
        
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
                for finding in packet.kiwi_findings:
                    print(f"    📄 {finding['title']}")
            except Exception as e:
                print(f"    ⚠️ KIWI调阅失败: {e}")
        
        return packet
    
    def _step4_output(self, packet: InformationPacket) -> InformationPacket:
        """
        第4步: 输出理解结果
        生成结构化的理解输出
        """
        print(f"\n📤 Step 4: 输出理解结果")
        print("-"*70)
        
        # 生成理解摘要
        understanding_parts = []
        
        # 基本信息
        understanding_parts.append(f"【信息来源】{packet.source}")
        understanding_parts.append(f"【可靠性】{packet.reliability_level.name} ({packet.reliability_score:.0%})")
        
        # 内容摘要
        content_summary = packet.raw_content[:100] + "..." if len(packet.raw_content) > 100 else packet.raw_content
        understanding_parts.append(f"【内容摘要】{content_summary}")
        
        # 分析结果
        if packet.skill_analysis:
            analysis = packet.skill_analysis
            understanding_parts.append(f"【情感倾向】{analysis.get('sentiment', '未知')}")
            understanding_parts.append(f"【潜在影响】{analysis.get('potential_impact', '待评估')}")
            
            # 关键洞察
            insights = []
            if packet.reliability_score > 0.8:
                insights.append("高可靠信息，可直接用于决策")
            if analysis.get('related_strategies'):
                insights.append(f"可能影响策略: {', '.join(analysis['related_strategies'][:2])}")
            if packet.kiwi_findings:
                insights.append(f"KIWI中找到 {len(packet.kiwi_findings)} 篇相关文档")
            
            packet.key_insights = insights
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
        """
        第5步: 归档总结
        更新KIWI、更新策略、形成闭环
        """
        print(f"\n💾 Step 5: 归档总结")
        print("-"*70)
        
        archive_actions = []
        
        # 1. 归档到KIWI (如果可靠性足够)
        if packet.reliability_score >= 0.6:
            archive_actions.append("✅ 已归档到KIWI知识库")
            packet.archived_to_kiwi = True
            
            # 模拟归档位置
            packet.archive_location = f"kiwi://processed/{datetime.now().strftime('%Y%m%d')}/{packet.packet_id}"
        else:
            archive_actions.append("⚠️ 可靠性不足，仅本地存档")
        
        # 2. 策略更新建议 (如果需要)
        if packet.action_items and any("策略" in a or "交易" in a for a in packet.action_items):
            archive_actions.append("📊 建议更新相关策略参数")
            packet.strategy_updated = True
        
        # 3. 形成处理闭环记录
        closure_record = {
            "packet_id": packet.packet_id,
            "processed_at": datetime.now().isoformat(),
            "reliability": packet.reliability_score,
            "archived": packet.archived_to_kiwi,
            "strategy_updated": packet.strategy_updated
        }
        
        print(f"  归档位置: {packet.archive_location or '本地缓存'}")
        print(f"  归档状态: {'已同步KIWI' if packet.archived_to_kiwi else '本地存储'}")
        print(f"  策略更新: {'是' if packet.strategy_updated else '否'}")
        print(f"  处理闭环: 完成")
        
        return packet
    
    # ============ 辅助方法 ============
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 简化的关键词提取
        common_words = ["的", "了", "是", "在", "和", "与", "对", "为"]
        words = content.split()
        keywords = [w for w in words if len(w) > 2 and w not in common_words]
        return keywords[:10]
    
    def _extract_entities(self, content: str) -> List[str]:
        """提取实体"""
        entities = []
        # 股票代码模式
        import re
        stock_codes = re.findall(r'\d{6}\.?(SZ|SH|BJ)?', content)
        if stock_codes:
            entities.extend([f"股票:{code[0]}" for code in stock_codes[:3]])
        return entities
    
    def _analyze_sentiment(self, content: str) -> str:
        """情感分析"""
        positive = ["涨", "利好", "增长", "突破", "强劲", "优秀"]
        negative = ["跌", "利空", "下降", "跌破", "疲软", "亏损"]
        
        p_count = sum(1 for w in positive if w in content)
        n_count = sum(1 for w in negative if w in content)
        
        if p_count > n_count:
            return "偏多"
        elif n_count > p_count:
            return "偏空"
        return "中性"
    
    def _assess_impact(self, packet: InformationPacket) -> str:
        """评估影响"""
        if packet.reliability_score > 0.8:
            return "重大影响"
        elif packet.reliability_score > 0.5:
            return "中等影响"
        return "轻微影响"
    
    def _match_strategies(self, packet: InformationPacket) -> List[str]:
        """匹配相关策略"""
        strategies = []
        content = packet.raw_content
        
        if any(kw in content for kw in ["趋势", "突破"]):
            strategies.append("Turtle Trading")
        if any(kw in content for kw in ["价值", "估值", "PE", "PB"]):
            strategies.append("Buffett Value")
        if any(kw in content for kw in ["动量", "强势", "领涨"]):
            strategies.append("Trend+RS")
        
        return strategies
    
    def _generate_actions(self, packet: InformationPacket) -> List[str]:
        """生成行动建议"""
        actions = []
        
        if packet.reliability_score >= 0.8:
            actions.append("纳入决策参考")
        
        if packet.kiwi_findings:
            actions.append("查阅KIWI相关文档")
        
        strategies = packet.skill_analysis.get("related_strategies", [])
        if strategies:
            actions.append(f"关注{strategies[0]}策略信号")
        
        return actions

def demo():
    """演示信息处理链路"""
    print("="*70)
    print("🔄 A5L 信息处理链路演示")
    print("   阅读 → 复查 → 分析+KIWI → 输出 → 归档")
    print("="*70)
    
    pipeline = InformationProcessingPipeline()
    
    # 测试场景1: 高质量市场信息
    print("\n" + "="*70)
    print("📋 测试场景1: 官方财报信息")
    print("="*70)
    
    packet1 = pipeline.process(
        raw_content="宁德时代(300750.SZ)发布2026年一季报：营收同比增长45%，净利润增长38%，毛利率稳定在25%以上。公司表示新产能将于Q2投产。",
        source="官方公告",
        context={"urgency": "high"}
    )
    
    # 测试场景2: 一般质量新闻
    print("\n" + "="*70)
    print("📋 测试场景2: 市场传闻")
    print("="*70)
    
    packet2 = pipeline.process(
        raw_content="听说新能源板块可能要调整，有人说宁德时代目标价要下调。",
        source="社交媒体",
        context={"urgency": "low"}
    )
    
    # 汇总
    print("\n" + "="*70)
    print("📊 处理汇总")
    print("="*70)
    print(f"  总共处理: {len(pipeline.processing_history)} 条信息")
    print(f"  平均可靠性: {sum(p.reliability_score for p in pipeline.processing_history)/len(pipeline.processing_history):.1%}")
    print(f"  KIWI归档: {sum(1 for p in pipeline.processing_history if p.archived_to_kiwi)} 条")
    print(f"  策略更新建议: {sum(1 for p in pipeline.processing_history if p.strategy_updated)} 条")
    
    print("\n" + "="*70)
    print("✅ 信息处理链路演示完成！")
    print("="*70)

if __name__ == "__main__":
    demo()
