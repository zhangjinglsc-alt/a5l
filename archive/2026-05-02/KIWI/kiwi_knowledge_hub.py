#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIWI 知识沉淀中心 (KIWI Knowledge Hub)
A5L的内部图书馆 - 承载所有知识，支持决策

核心理念:
- 所有信息自动归档到KIWI
- 知识结构化、可检索、可复用
- 与A5L五层架构深度集成
- 支持多维度知识关联

功能模块:
1. 知识采集器 - 自动收集和整理信息
2. 知识组织器 - 结构化存储和分类
3. 知识检索器 - 智能搜索和推荐
4. 知识连接器 - 建立知识间关联
5. 知识沉淀器 - 长期积累和复利
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import re

sys.path.insert(0, "/workspace/projects/workspace")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeType(Enum):
    """知识类型"""
    MARKET_DATA = "market_data"           # 市场数据
    RESEARCH_REPORT = "research_report"   # 研报
    NEWS = "news"                         # 新闻
    STRATEGY = "strategy"                 # 策略
    TRADE_RECORD = "trade_record"         # 交易记录
    ANALYSIS = "analysis"                 # 分析
    INSIGHT = "insight"                   # 洞察
    DECISION = "decision"                 # 决策
    LESSON = "lesson"                     # 教训/经验
    CONCEPT = "concept"                   # 概念/理论

@dataclass
class KnowledgeNode:
    """知识节点"""
    node_id: str
    title: str
    content: str
    knowledge_type: KnowledgeType
    source: str
    timestamp: str
    tags: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)  # 关联实体(股票代码等)
    reliability: float = 0.0  # 可信度 0-1
    importance: float = 0.5   # 重要性 0-1
    usage_count: int = 0      # 使用次数
    related_nodes: List[str] = field(default_factory=list)  # 关联节点ID
    metadata: Dict = field(default_factory=dict)

@dataclass
class KnowledgeQuery:
    """知识查询"""
    query_id: str
    query_text: str
    query_type: str  # keyword, semantic, entity, time
    results: List[KnowledgeNode] = field(default_factory=list)
    timestamp: str = ""

class KIWIKnowledgeHub:
    """
    📚 KIWI知识沉淀中心
    A5L的内部图书馆
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.kiwi_dir = f"{workspace}/KIWI"
        self.knowledge_graph: Dict[str, KnowledgeNode] = {}
        self.entity_index: Dict[str, Set[str]] = {}  # 实体 -> 节点ID集合
        self.tag_index: Dict[str, Set[str]] = {}     # 标签 -> 节点ID集合
        self.time_index: Dict[str, List[str]] = {}   # 日期 -> 节点ID列表
        self.usage_stats: Dict = {}
        
        # 确保目录存在
        os.makedirs(self.kiwi_dir, exist_ok=True)
        os.makedirs(f"{self.kiwi_dir}/nodes", exist_ok=True)
        os.makedirs(f"{self.kiwi_dir}/indices", exist_ok=True)
        os.makedirs(f"{self.kiwi_dir}/exports", exist_ok=True)
        
        # 加载已有知识
        self._load_existing_knowledge()
        
        logger.info("📚 KIWI知识沉淀中心初始化完成")
        logger.info(f"   知识节点数: {len(self.knowledge_graph)}")
    
    def _load_existing_knowledge(self):
        """加载已有知识"""
        nodes_dir = f"{self.kiwi_dir}/nodes"
        if os.path.exists(nodes_dir):
            for filename in os.listdir(nodes_dir):
                if filename.endswith('.json'):
                    try:
                        with open(f"{nodes_dir}/{filename}", 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            node = KnowledgeNode(**data)
                            self.knowledge_graph[node.node_id] = node
                            self._update_indices(node)
                    except Exception as e:
                        logger.warning(f"加载知识节点失败 {filename}: {e}")
    
    def _update_indices(self, node: KnowledgeNode):
        """更新索引"""
        # 实体索引
        for entity in node.entities:
            if entity not in self.entity_index:
                self.entity_index[entity] = set()
            self.entity_index[entity].add(node.node_id)
        
        # 标签索引
        for tag in node.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(node.node_id)
        
        # 时间索引
        date_key = node.timestamp[:10]  # YYYY-MM-DD
        if date_key not in self.time_index:
            self.time_index[date_key] = []
        self.time_index[date_key].append(node.node_id)
    
    def add_knowledge(self, title: str, content: str, 
                      knowledge_type: KnowledgeType,
                      source: str,
                      entities: List[str] = None,
                      tags: List[str] = None,
                      reliability: float = 0.5,
                      importance: float = 0.5,
                      metadata: Dict = None) -> str:
        """
        添加知识到KIWI
        
        这是知识沉淀的核心入口
        """
        # 生成节点ID
        content_hash = hashlib.md5(f"{title}{content}{datetime.now()}".encode()).hexdigest()[:12]
        node_id = f"KN-{knowledge_type.value}-{content_hash}"
        
        # 自动提取实体(如果未提供)
        if entities is None:
            entities = self._extract_entities(content)
        
        # 自动打标签(如果未提供)
        if tags is None:
            tags = self._auto_tag(content, knowledge_type)
        
        # 创建知识节点
        node = KnowledgeNode(
            node_id=node_id,
            title=title,
            content=content,
            knowledge_type=knowledge_type,
            source=source,
            timestamp=datetime.now().isoformat(),
            tags=tags,
            entities=entities,
            reliability=reliability,
            importance=importance,
            metadata=metadata or {}
        )
        
        # 保存到内存
        self.knowledge_graph[node_id] = node
        self._update_indices(node)
        
        # 持久化到文件
        self._save_node(node)
        
        # 建立知识关联
        self._connect_related_knowledge(node)
        
        logger.info(f"📚 知识已沉淀: [{knowledge_type.value}] {title[:30]}... (ID: {node_id})")
        
        return node_id
    
    def _extract_entities(self, content: str) -> List[str]:
        """从内容中提取实体"""
        entities = []
        
        # 提取股票代码 (6位数字)
        stock_codes = re.findall(r'\b(\d{6})\b', content)
        entities.extend([f"{code}.SZ" if code.startswith(('0', '3')) else f"{code}.SH" 
                        for code in stock_codes])
        
        # 提取公司名 (简单匹配)
        company_patterns = [
            r'(宁德时代|比亚迪|茅台|腾讯|阿里|字节|华为)',
            r'(中芯国际|长电科技|韦尔股份|海康威视)'
        ]
        for pattern in company_patterns:
            matches = re.findall(pattern, content)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _auto_tag(self, content: str, knowledge_type: KnowledgeType) -> List[str]:
        """自动打标签"""
        tags = [knowledge_type.value]
        
        # 根据内容关键词打标签
        keyword_tags = {
            "新能源": ["新能源", "电动车", "光伏", "锂电"],
            "半导体": ["半导体", "芯片", "晶圆", "光刻"],
            "AI": ["AI", "人工智能", "大模型", "算法"],
            "医药": ["医药", "医疗", "药品", "疫苗"],
            "金融": ["银行", "保险", "券商", "金融"]
        }
        
        for tag, keywords in keyword_tags.items():
            if any(kw in content for kw in keywords):
                tags.append(tag)
        
        return tags
    
    def _save_node(self, node: KnowledgeNode):
        """保存节点到文件"""
        filepath = f"{self.kiwi_dir}/nodes/{node.node_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(node), f, ensure_ascii=False, indent=2)
    
    def _connect_related_knowledge(self, new_node: KnowledgeNode):
        """建立知识关联"""
        # 查找相关节点
        related = []
        
        # 基于实体关联
        for entity in new_node.entities:
            if entity in self.entity_index:
                for node_id in self.entity_index[entity]:
                    if node_id != new_node.node_id:
                        related.append(node_id)
        
        # 基于标签关联
        for tag in new_node.tags:
            if tag in self.tag_index:
                for node_id in self.tag_index[tag]:
                    if node_id != new_node.node_id and node_id not in related:
                        related.append(node_id)
        
        # 更新新节点的关联
        new_node.related_nodes = related[:10]  # 最多关联10个
        
        # 双向关联
        for node_id in related[:10]:
            if node_id in self.knowledge_graph:
                node = self.knowledge_graph[node_id]
                if new_node.node_id not in node.related_nodes:
                    node.related_nodes.append(new_node.node_id)
                    node.related_nodes = node.related_nodes[:10]
                    self._save_node(node)
        
        # 保存更新后的新节点
        self._save_node(new_node)
    
    def query_knowledge(self, query: str, 
                        query_type: str = "semantic",
                        filters: Dict = None,
                        limit: int = 10) -> List[KnowledgeNode]:
        """
        查询知识
        
        Args:
            query: 查询内容
            query_type: keyword/semantic/entity/time
            filters: 过滤条件
            limit: 返回数量
        """
        results = []
        
        if query_type == "keyword":
            # 关键词搜索
            for node in self.knowledge_graph.values():
                if query.lower() in node.title.lower() or query.lower() in node.content.lower():
                    results.append(node)
        
        elif query_type == "entity":
            # 实体搜索
            if query in self.entity_index:
                for node_id in self.entity_index[query]:
                    if node_id in self.knowledge_graph:
                        results.append(self.knowledge_graph[node_id])
        
        elif query_type == "tag":
            # 标签搜索
            if query in self.tag_index:
                for node_id in self.tag_index[query]:
                    if node_id in self.knowledge_graph:
                        results.append(self.knowledge_graph[node_id])
        
        elif query_type == "time":
            # 时间范围搜索
            if query in self.time_index:
                for node_id in self.time_index[query]:
                    if node_id in self.knowledge_graph:
                        results.append(self.knowledge_graph[node_id])
        
        # 应用过滤
        if filters:
            if "knowledge_type" in filters:
                type_filter = filters["knowledge_type"]
                results = [r for r in results if r.knowledge_type.value == type_filter]
            
            if "min_reliability" in filters:
                min_rel = filters["min_reliability"]
                results = [r for r in results if r.reliability >= min_rel]
        
        # 排序 (重要性 * 可信度)
        results.sort(key=lambda x: (x.importance * x.reliability, x.usage_count), reverse=True)
        
        return results[:limit]
    
    def get_knowledge_by_entity(self, entity: str, limit: int = 20) -> List[KnowledgeNode]:
        """获取与特定实体相关的所有知识"""
        if entity not in self.entity_index:
            return []
        
        results = []
        for node_id in self.entity_index[entity]:
            if node_id in self.knowledge_graph:
                node = self.knowledge_graph[node_id]
                node.usage_count += 1
                results.append(node)
        
        # 按重要性排序
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]
    
    def generate_knowledge_report(self, entity: str = None, 
                                  days: int = 7) -> Dict:
        """
        生成知识报告
        
        用于整合和总结知识
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "summary": {}
        }
        
        if entity:
            # 特定实体的知识报告
            knowledge = self.get_knowledge_by_entity(entity)
            report["entity"] = entity
            report["knowledge_count"] = len(knowledge)
            
            # 按类型分组
            by_type = {}
            for node in knowledge:
                t = node.knowledge_type.value
                if t not in by_type:
                    by_type[t] = []
                by_type[t].append({
                    "title": node.title,
                    "reliability": node.reliability,
                    "importance": node.importance,
                    "timestamp": node.timestamp
                })
            
            report["by_type"] = by_type
            
            # 关键洞察
            high_importance = [n for n in knowledge if n.importance > 0.8]
            report["key_insights"] = [
                {"title": n.title, "content": n.content[:100] + "..."}
                for n in high_importance[:5]
            ]
        
        else:
            # 整体知识统计
            recent_date = (datetime.now() - timedelta(days=days)).isoformat()
            recent_nodes = [
                n for n in self.knowledge_graph.values()
                if n.timestamp > recent_date
            ]
            
            report["total_nodes"] = len(self.knowledge_graph)
            report["recent_nodes"] = len(recent_nodes)
            report["entity_count"] = len(self.entity_index)
            report["tag_count"] = len(self.tag_index)
        
        return report
    
    def export_to_feishu_doc(self, entity: str = None, 
                             title: str = None) -> str:
        """
        导出知识到飞书文档
        
        支持知识的分享和传播
        """
        if title is None:
            title = f"KIWI知识报告-{datetime.now().strftime('%Y%m%d')}"
        
        # 生成Markdown内容
        if entity:
            knowledge = self.get_knowledge_by_entity(entity)
            content = self._generate_entity_markdown(entity, knowledge)
        else:
            content = self._generate_summary_markdown()
        
        # 保存到导出目录
        export_path = f"{self.kiwi_dir}/exports/{title}.md"
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"📚 知识已导出: {export_path}")
        return export_path
    
    def _generate_entity_markdown(self, entity: str, 
                                  knowledge: List[KnowledgeNode]) -> str:
        """生成实体知识Markdown"""
        lines = [
            f"# {entity} - KIWI知识报告",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**知识节点数**: {len(knowledge)}",
            f"",
            "---",
            f"",
            "## 知识概览",
            f""
        ]
        
        # 按类型分组
        by_type = {}
        for node in knowledge:
            t = node.knowledge_type.value
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(node)
        
        for t, nodes in by_type.items():
            lines.append(f"### {t} ({len(nodes)}条)")
            for node in nodes[:5]:  # 每类最多5条
                lines.append(f"- **{node.title}** (可信度: {node.reliability:.0%})")
                lines.append(f"  - {node.content[:80]}...")
            lines.append("")
        
        # 详细内容
        lines.extend(["---", "", "## 详细内容", ""])
        
        for node in knowledge[:20]:  # 最多20条详细
            lines.extend([
                f"### {node.title}",
                f"",
                f"- **类型**: {node.knowledge_type.value}",
                f"- **来源**: {node.source}",
                f"- **可信度**: {node.reliability:.0%}",
                f"- **重要性**: {node.importance:.0%}",
                f"- **时间**: {node.timestamp[:10]}",
                f"",
                f"{node.content}",
                f"",
                "---",
                f""
            ])
        
        return "\n".join(lines)
    
    def _generate_summary_markdown(self) -> str:
        """生成汇总Markdown"""
        lines = [
            f"# KIWI知识库总览",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**知识节点总数**: {len(self.knowledge_graph)}",
            f"**覆盖实体数**: {len(self.entity_index)}",
            f"**标签数**: {len(self.tag_index)}",
            f"",
            "---",
            f"",
            "## 知识分布",
            f""
        ]
        
        # 按类型统计
        by_type = {}
        for node in self.knowledge_graph.values():
            t = node.knowledge_type.value
            if t not in by_type:
                by_type[t] = 0
            by_type[t] += 1
        
        for t, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {t}: {count}条")
        
        lines.extend(["", "---", "", "## 高频实体", ""])
        
        # 高频实体
        entity_counts = [(e, len(ids)) for e, ids in self.entity_index.items()]
        entity_counts.sort(key=lambda x: x[1], reverse=True)
        
        for entity, count in entity_counts[:20]:
            lines.append(f"- {entity}: {count}条知识")
        
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict:
        """获取知识库统计"""
        return {
            "total_nodes": len(self.knowledge_graph),
            "entity_count": len(self.entity_index),
            "tag_count": len(self.tag_index),
            "date_range": {
                "earliest": min((n.timestamp for n in self.knowledge_graph.values()), default=""),
                "latest": max((n.timestamp for n in self.knowledge_graph.values()), default="")
            },
            "by_type": self._count_by_type(),
            "storage_size_mb": self._calculate_storage_size()
        }
    
    def _count_by_type(self) -> Dict:
        """按类型统计"""
        counts = {}
        for node in self.knowledge_graph.values():
            t = node.knowledge_type.value
            counts[t] = counts.get(t, 0) + 1
        return counts
    
    def _calculate_storage_size(self) -> float:
        """计算存储大小"""
        total_size = 0
        nodes_dir = f"{self.kiwi_dir}/nodes"
        if os.path.exists(nodes_dir):
            for filename in os.listdir(nodes_dir):
                filepath = f"{nodes_dir}/{filename}"
                total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)  # MB

def demo():
    """演示KIWI知识沉淀"""
    print("="*70)
    print("📚 KIWI知识沉淀中心演示")
    print("="*70)
    print()
    
    kiwi = KIWIKnowledgeHub()
    
    # 演示1: 添加研报知识
    print("演示1: 添加研报知识")
    print("-"*70)
    
    node_id1 = kiwi.add_knowledge(
        title="宁德时代2026年一季报点评",
        content="宁德时代发布2026年一季报，营收同比增长45%，净利润增长38%。" \
                "动力电池出货量全球第一，市场份额继续提升。毛利率稳定在25%左右。",
        knowledge_type=KnowledgeType.RESEARCH_REPORT,
        source="中信证券研报",
        entities=["300750.SZ", "宁德时代"],
        tags=["新能源", "锂电", "财报"],
        reliability=0.9,
        importance=0.85
    )
    print(f"✅ 知识已添加: {node_id1}")
    print()
    
    # 演示2: 添加交易记录
    print("演示2: 添加交易记录")
    print("-"*70)
    
    node_id2 = kiwi.add_knowledge(
        title="买入宁德时代100股",
        content="基于研报分析，买入宁德时代100股，成本价215元。" \
                "理由：Q1业绩超预期，毛利率稳定，市场份额提升。",
        knowledge_type=KnowledgeType.TRADE_RECORD,
        source="交易记录",
        entities=["300750.SZ"],
        tags=["交易", "买入", "新能源"],
        reliability=1.0,
        importance=0.7
    )
    print(f"✅ 知识已添加: {node_id2}")
    print()
    
    # 演示3: 查询知识
    print("演示3: 查询宁德时代相关知识")
    print("-"*70)
    
    results = kiwi.query_knowledge("宁德时代", query_type="keyword")
    print(f"找到 {len(results)} 条相关知识:")
    for node in results:
        print(f"  - [{node.knowledge_type.value}] {node.title} (可信度: {node.reliability:.0%})")
    print()
    
    # 演示4: 实体关联
    print("演示4: 获取300750.SZ的所有知识")
    print("-"*70)
    
    entity_knowledge = kiwi.get_knowledge_by_entity("300750.SZ")
    print(f"实体 300750.SZ 关联 {len(entity_knowledge)} 条知识:")
    for node in entity_knowledge:
        print(f"  - {node.title}")
    print()
    
    # 演示5: 生成报告
    print("演示5: 生成知识报告")
    print("-"*70)
    
    report = kiwi.generate_knowledge_report(entity="300750.SZ")
    print(f"实体: {report['entity']}")
    print(f"知识数量: {report['knowledge_count']}")
    print(f"知识类型: {list(report['by_type'].keys())}")
    print()
    
    # 演示6: 统计信息
    print("演示6: 知识库统计")
    print("-"*70)
    
    stats = kiwi.get_statistics()
    print(f"总节点数: {stats['total_nodes']}")
    print(f"实体数: {stats['entity_count']}")
    print(f"标签数: {stats['tag_count']}")
    print(f"存储大小: {stats['storage_size_mb']:.2f} MB")
    print()
    
    print("="*70)
    print("✅ KIWI知识沉淀演示完成!")
    print("="*70)

if __name__ == "__main__":
    demo()
