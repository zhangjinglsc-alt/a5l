"""
A5L Knowledge Graph - Relation Builder
Phase 3: Build relationships between entities

Builds:
- Industry chain relationships (upstream/downstream)
- Correlation relationships (same industry/concept)
- Competition relationships
- Holding/mention relationships
"""

import re
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from knowledge_graph_core import (
    KnowledgeGraph, Entity, Relation,
    create_industry_chain_relation, create_belongs_to_relation
)


@dataclass
class ExtractedRelation:
    """提取出的关系（中间格式）"""
    source_id: str
    target_id: str
    type: str
    confidence: float
    properties: Dict


class IndustryChainBuilder:
    """产业链关系构建器"""
    
    # 产业链定义（上游 -> 下游）
    INDUSTRY_CHAINS = {
        '半导体': {
            'upstream': ['半导体设备', '半导体材料', 'EDA软件'],
            'downstream': ['芯片设计', '晶圆代工', '封测', '电子产品']
        },
        'AI算力': {
            'upstream': ['半导体', '存储芯片', '光通信', '服务器'],
            'downstream': ['云计算', '大模型', 'AI应用', '数据中心']
        },
        '新能源': {
            'upstream': ['锂矿', '钴矿', '稀土', '化工材料'],
            'downstream': ['锂电池', '光伏', '风电', '储能', '新能源汽车']
        },
        '新能源汽车': {
            'upstream': ['锂电池', '电机', '电控', '汽车零部件'],
            'downstream': ['整车制造', '充电桩', '汽车销售', '汽车服务']
        },
        '光通信': {
            'upstream': ['光芯片', '光器件', '光纤光缆'],
            'downstream': ['光模块', '通信设备', '数据中心', '运营商']
        },
        '信创': {
            'upstream': ['芯片', '操作系统', '数据库', '中间件'],
            'downstream': ['办公软件', '行业软件', '系统集成', '云服务']
        },
        '创新药': {
            'upstream': ['CRO', 'CMO', '原料药', '医药中间体'],
            'downstream': ['制剂', '医疗器械', '医药流通', '医疗服务']
        },
        '游戏': {
            'upstream': ['游戏引擎', '美术外包', '音乐音效'],
            'downstream': ['游戏发行', '游戏平台', '电竞', '直播']
        },
        '云计算': {
            'upstream': ['服务器', '存储', '网络设备', 'IDC'],
            'downstream': ['SaaS', 'PaaS', 'IaaS', '云安全']
        }
    }
    
    # 公司与产业链位置映射
    COMPANY_POSITION = {
        # 半导体
        'NVDA': {'industry': '半导体', 'position': '芯片设计'},
        'AMD': {'industry': '半导体', 'position': '芯片设计'},
        'INTC': {'industry': '半导体', 'position': '晶圆代工'},
        'TSM': {'industry': '半导体', 'position': '晶圆代工'},
        'ASML': {'industry': '半导体', 'position': '半导体设备'},
        '中国长城': {'industry': '信创', 'position': '整机'},
        '中芯国际': {'industry': '半导体', 'position': '晶圆代工'},
        # AI算力
        'NVIDIA': {'industry': 'AI算力', 'position': '芯片设计'},
        'AMD': {'industry': 'AI算力', 'position': '芯片设计'},
        # 新能源
        'TSLA': {'industry': '新能源汽车', 'position': '整车制造'},
        '特斯拉': {'industry': '新能源汽车', 'position': '整车制造'},
        '比亚迪': {'industry': '新能源汽车', 'position': '整车制造'},
        '宁德时代': {'industry': '新能源', 'position': '锂电池'},
        # 光通信
        '中际旭创': {'industry': '光通信', 'position': '光模块'},
        '新易盛': {'industry': '光通信', 'position': '光模块'},
    }
    
    def build_from_industry(self, kg: KnowledgeGraph, industry_name: str) -> List[Relation]:
        """基于行业名称构建产业链关系"""
        relations = []
        
        if industry_name not in self.INDUSTRY_CHAINS:
            return relations
        
        chain = self.INDUSTRY_CHAINS[industry_name]
        industry_id = f"industry_{industry_name}"
        
        # 添加上游关系
        for upstream in chain['upstream']:
            upstream_id = f"industry_{upstream}"
            relation = Relation(
                id=f"{upstream_id}_supply_{industry_id}",
                source_id=upstream_id,
                target_id=industry_id,
                type='industry_chain',
                properties={'direction': 'upstream', 'relation': 'supply'}
            )
            if kg.add_relation(relation):
                relations.append(relation)
        
        # 添加下游关系
        for downstream in chain['downstream']:
            downstream_id = f"industry_{downstream}"
            relation = Relation(
                id=f"{industry_id}_supply_{downstream_id}",
                source_id=industry_id,
                target_id=downstream_id,
                type='industry_chain',
                properties={'direction': 'downstream', 'relation': 'supply'}
            )
            if kg.add_relation(relation):
                relations.append(relation)
        
        return relations
    
    def build_for_stock(self, kg: KnowledgeGraph, stock_code: str, stock_name: str) -> List[Relation]:
        """为股票构建产业链关系"""
        relations = []
        
        # 查找公司在产业链中的位置
        key = stock_code if stock_code in self.COMPANY_POSITION else stock_name
        if key not in self.COMPANY_POSITION:
            return relations
        
        info = self.COMPANY_POSITION[key]
        industry = info['industry']
        position = info['position']
        
        stock_id = f"stock_{stock_code}"
        position_id = f"industry_{position}"
        
        # 添加位置关系
        relation = Relation(
            id=f"{stock_id}_position_{position_id}",
            source_id=stock_id,
            target_id=position_id,
            type='industry_position',
            properties={'position': 'participant'}
        )
        if kg.add_relation(relation):
            relations.append(relation)
        
        # 构建所在行业的产业链
        chain_relations = self.build_from_industry(kg, industry)
        relations.extend(chain_relations)
        
        return relations
    
    def extract_from_text(self, text: str) -> List[ExtractedRelation]:
        """从文本中提取产业链关系"""
        relations = []
        
        # 模式：A为B的上游/下游
        upstream_pattern = re.compile(r'(\w+)\s*为?\s*(\w+)\s*的?\s*上游')
        downstream_pattern = re.compile(r'(\w+)\s*为?\s*(\w+)\s*的?\s*下游')
        
        for match in upstream_pattern.finditer(text):
            source = match.group(1)
            target = match.group(2)
            relations.append(ExtractedRelation(
                source_id=f"entity_{source}",
                target_id=f"entity_{target}",
                type='industry_chain',
                confidence=0.8,
                properties={'direction': 'upstream'}
            ))
        
        for match in downstream_pattern.finditer(text):
            source = match.group(1)
            target = match.group(2)
            relations.append(ExtractedRelation(
                source_id=f"entity_{source}",
                target_id=f"entity_{target}",
                type='industry_chain',
                confidence=0.8,
                properties={'direction': 'downstream'}
            ))
        
        return relations


class CorrelationBuilder:
    """关联关系构建器"""
    
    def build_industry_correlation(self, kg: KnowledgeGraph) -> List[Relation]:
        """构建同行业关联"""
        relations = []
        
        # 获取所有行业
        industries = kg.get_entities_by_type('Industry')
        
        for industry in industries:
            # 查找属于该行业的所有股票
            # 这里简化处理，实际应该从关系查询
            pass
        
        return relations
    
    def build_concept_correlation(self, kg: KnowledgeGraph, concept_id: str) -> List[Relation]:
        """构建同概念关联"""
        relations = []
        
        # 获取与概念关联的所有股票
        related = kg.get_related_entities(concept_id, relation_type='correlates_with')
        
        stock_ids = [r['entity_id'] for r in related if r['entity_type'] == 'Stock']
        
        # 两两建立关联（股票间）
        for i, stock1 in enumerate(stock_ids):
            for stock2 in stock_ids[i+1:]:
                relation = Relation(
                    id=f"{stock1}_correlates_{stock2}",
                    source_id=stock1,
                    target_id=stock2,
                    type='stock_correlation',
                    properties={'basis': 'common_concept', 'concept': concept_id}
                )
                if kg.add_relation(relation):
                    relations.append(relation)
        
        return relations
    
    def build_supply_chain(self, kg: KnowledgeGraph, center_stock: str) -> Dict:
        """构建以某股票为中心的供应链"""
        result = {
            'center': center_stock,
            'suppliers': [],
            'customers': [],
            'competitors': []
        }
        
        # 获取直接关联
        related = kg.get_related_entities(center_stock, depth=1)
        
        for r in related:
            if r['relation_type'] == 'industry_chain':
                if r.get('relation_properties', {}).get('direction') == 'upstream':
                    result['suppliers'].append(r)
                else:
                    result['customers'].append(r)
            elif r['relation_type'] == 'competes_with':
                result['competitors'].append(r)
        
        return result


class CompetitionBuilder:
    """竞争关系构建器"""
    
    # 已知竞争关系
    COMPETITION_PAIRS = [
        ('NVDA', 'AMD'),
        ('NVDA', 'INTC'),
        ('AMD', 'INTC'),
        ('AAPL', 'MSFT'),
        ('AAPL', 'GOOGL'),
        ('TSLA', 'NIO'),
        ('TSLA', 'XPEV'),
        ('TSLA', 'LI'),
        ('BABA', 'JD'),
        ('宁德时代', '比亚迪'),
        ('中际旭创', '新易盛'),
    ]
    
    # 竞争关键词
    COMPETITION_KEYWORDS = [
        '竞争', '竞品', '对手', '市场份额', '市占率',
        'versus', 'vs', 'competitor', 'rival'
    ]
    
    def build_known_competition(self, kg: KnowledgeGraph) -> List[Relation]:
        """构建已知的竞争关系"""
        relations = []
        
        for stock1, stock2 in self.COMPETITION_PAIRS:
            id1 = f"stock_{stock1}"
            id2 = f"stock_{stock2}"
            
            # 双向竞争关系
            relation1 = Relation(
                id=f"{id1}_competes_{id2}",
                source_id=id1,
                target_id=id2,
                type='competes_with',
                confidence=0.95
            )
            relation2 = Relation(
                id=f"{id2}_competes_{id1}",
                source_id=id2,
                target_id=id1,
                type='competes_with',
                confidence=0.95
            )
            
            if kg.add_relation(relation1):
                relations.append(relation1)
            if kg.add_relation(relation2):
                relations.append(relation2)
        
        return relations
    
    def extract_from_text(self, text: str) -> List[ExtractedRelation]:
        """从文本中提取竞争关系"""
        relations = []
        
        # 模式：A与B竞争激烈 / A是B的主要竞争对手
        patterns = [
            re.compile(r'(\w+)\s*与\s*(\w+)\s*(?:竞争|较量|对抗)'),
            re.compile(r'(\w+)\s*是?\s*(\w+)\s*的?\s*(?:主要)?\s*(?:竞争对手?|竞品)'),
        ]
        
        for pattern in patterns:
            for match in pattern.finditer(text):
                source = match.group(1)
                target = match.group(2)
                relations.append(ExtractedRelation(
                    source_id=f"stock_{source}",
                    target_id=f"stock_{target}",
                    type='competes_with',
                    confidence=0.7,
                    properties={}
                ))
        
        return relations


class RelationBuilder:
    """关系构建器主类"""
    
    def __init__(self):
        self.industry_builder = IndustryChainBuilder()
        self.correlation_builder = CorrelationBuilder()
        self.competition_builder = CompetitionBuilder()
    
    def build_all_relations(self, kg: KnowledgeGraph) -> Dict[str, int]:
        """构建所有类型的关系"""
        stats = {
            'industry_chain': 0,
            'competition': 0,
            'correlation': 0,
            'total': 0
        }
        
        # 1. 构建已知竞争关系
        competition_relations = self.competition_builder.build_known_competition(kg)
        stats['competition'] = len(competition_relations)
        
        # 2. 构建产业链关系
        # 为所有股票构建产业链关系
        stocks = kg.get_entities_by_type('Stock')
        for stock in stocks:
            relations = self.industry_builder.build_for_stock(
                kg, stock.code or stock.name, stock.name
            )
            stats['industry_chain'] += len(relations)
        
        # 3. 构建概念关联
        concepts = kg.get_entities_by_type('Concept')
        for concept in concepts:
            relations = self.correlation_builder.build_concept_correlation(kg, concept.id)
            stats['correlation'] += len(relations)
        
        stats['total'] = sum(stats.values())
        return stats
    
    def build_from_document(self, kg: KnowledgeGraph, text: str, doc_id: str) -> Dict:
        """从文档中构建关系"""
        relations = []
        
        # 提取产业链关系
        chain_relations = self.industry_builder.extract_from_text(text)
        for r in chain_relations:
            relation = Relation(
                id=f"{r.source_id}_{r.type}_{r.target_id}_{doc_id}",
                source_id=r.source_id,
                target_id=r.target_id,
                type=r.type,
                confidence=r.confidence,
                properties={**r.properties, 'source_doc': doc_id}
            )
            if kg.add_relation(relation):
                relations.append(relation)
        
        # 提取竞争关系
        competition_relations = self.competition_builder.extract_from_text(text)
        for r in competition_relations:
            relation = Relation(
                id=f"{r.source_id}_{r.type}_{r.target_id}_{doc_id}",
                source_id=r.source_id,
                target_id=r.target_id,
                type=r.type,
                confidence=r.confidence,
                properties={'source_doc': doc_id}
            )
            if kg.add_relation(relation):
                relations.append(relation)
        
        return {
            'doc_id': doc_id,
            'relations': relations,
            'count': len(relations)
        }
    
    def analyze_stock_relationships(self, kg: KnowledgeGraph, stock_id: str) -> Dict:
        """分析股票的完整关系网络"""
        kg.load_to_memory()
        
        result = {
            'stock_id': stock_id,
            'industry_chain': self.correlation_builder.build_supply_chain(kg, stock_id),
            'related_concepts': [],
            'competitors': [],
            'mentioned_in': []
        }
        
        # 获取关联概念
        related = kg.get_related_entities(stock_id, relation_type='correlates_with')
        result['related_concepts'] = [
            {'id': r['entity_id'], 'name': r['entity_name']}
            for r in related if r['entity_type'] == 'Concept'
        ]
        
        # 获取竞争对手
        related = kg.get_related_entities(stock_id, relation_type='competes_with')
        result['competitors'] = [
            {'id': r['entity_id'], 'name': r['entity_name']}
            for r in related
        ]
        
        # 获取提及文档
        related = kg.get_related_entities(stock_id, relation_type='mentioned_in')
        result['mentioned_in'] = [
            {'id': r['entity_id'], 'name': r['entity_name']}
            for r in related
        ]
        
        return result


# ========== 测试代码 ==========

if __name__ == "__main__":
    from knowledge_graph_core import KnowledgeGraph, create_stock_entity, create_industry_entity
    from entity_extractor import FeishuDocumentProcessor
    
    print("=" * 60)
    print("A5L 知识图谱 - 关系构建器测试")
    print("=" * 60)
    
    # 创建知识图谱
    kg = KnowledgeGraph()
    
    # 先添加一些测试实体
    print("\n1. 添加测试实体...")
    test_entities = [
        create_stock_entity("NVDA", "NVIDIA", "半导体"),
        create_stock_entity("AMD", "AMD", "半导体"),
        create_stock_entity("INTC", "Intel", "半导体"),
        create_stock_entity("TSLA", "Tesla", "新能源汽车"),
        create_industry_entity("半导体"),
        create_industry_entity("AI算力"),
        create_industry_entity("新能源汽车"),
        create_industry_entity("半导体设备"),
        create_industry_entity("芯片设计"),
    ]
    for entity in test_entities:
        kg.add_entity(entity)
    print(f"  添加了 {len(test_entities)} 个实体")
    
    # 创建关系构建器
    builder = RelationBuilder()
    
    # 构建所有关系
    print("\n2. 构建所有关系...")
    stats = builder.build_all_relations(kg)
    print(f"  产业链关系: {stats['industry_chain']}")
    print(f"  竞争关系: {stats['competition']}")
    print(f"  关联关系: {stats['correlation']}")
    print(f"  总计: {stats['total']}")
    
    # 分析NVDA的关系网络
    print("\n3. 分析NVDA的关系网络...")
    analysis = builder.analyze_stock_relationships(kg, "stock_NVDA")
    print(f"  供应链上游: {len(analysis['industry_chain']['suppliers'])} 个")
    print(f"  供应链下游: {len(analysis['industry_chain']['customers'])} 个")
    print(f"  竞争对手: {len(analysis['competitors'])} 个")
    print(f"  关联概念: {len(analysis['related_concepts'])} 个")
    
    # 获取产业链
    print("\n4. 获取半导体产业链...")
    chain = builder.industry_builder.build_from_industry(kg, "半导体")
    print(f"  构建了 {len(chain)} 个产业链关系")
    
    # 知识图谱统计
    print("\n5. 知识图谱统计...")
    stats = kg.get_stats()
    print(f"  实体总数: {stats['total_entities']}")
    print(f"  关系总数: {stats['total_relations']}")
    print(f"  关系类型: {stats['relation_types']}")
    
    print("\n" + "=" * 60)
    print("✅ Phase 3 关系构建器测试完成!")
    print("=" * 60)
