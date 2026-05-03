"""
A5L Knowledge Graph - Entity Extractor
Phase 2: Extract entities from documents

Extracts:
- Stock codes (NVDA, 000066, etc.)
- Industry names (半导体, AI算力, etc.)
- Concepts (国产替代, ChatGPT, etc.)
- Events (美联储议息, 财报季, etc.)
- People (黄仁勋, 巴菲特, etc.)
"""

import re
import json
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from knowledge_graph_core import Entity, create_stock_entity, create_industry_entity, create_concept_entity


@dataclass
class ExtractedEntity:
    """提取出的实体（中间格式）"""
    text: str          # 原文
    type: str          # 实体类型
    normalized: str    # 标准化名称
    confidence: float  # 置信度
    position: Tuple[int, int]  # 在文本中的位置
    properties: Dict   # 额外属性


class StockExtractor:
    """股票代码提取器"""
    
    # 美股代码模式 (1-5个大写字母)
    US_STOCK_PATTERN = re.compile(r'\b[A-Z]{1,5}\b')
    
    # A股代码模式 (6位数字)
    A_STOCK_PATTERN = re.compile(r'\b(6\d{5}|0\d{5}|3\d{5}|8\d{5}|4\d{5})\b')
    
    # 港股代码模式 (1-5位数字)
    HK_STOCK_PATTERN = re.compile(r'\b(\d{1,5})\.HK\b', re.IGNORECASE)
    
    # 常见美股代码白名单（过滤常见缩写）
    COMMON_US_STOCKS = {
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 
        'TSM', 'ASML', 'AMD', 'INTC', 'QCOM', 'AVGO', 'NFLX', 'CRM',
        'BABA', 'JD', 'PDD', 'TCEHY', 'BIDU', 'NIO', 'XPEV', 'LI',
        'TSLA', 'PLTR', 'ABNB', 'UBER', 'LYFT', 'ZM', 'SNOW', 'CRM',
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC',
        'JNJ', 'PFE', 'MRNA', 'BNTX', 'AZN', 'NVS', 'UNH', 'ABBV',
        'WMT', 'COST', 'HD', 'LOW', 'TGT', 'DG', 'DLTR',
        'KO', 'PEP', 'MCD', 'SBUX', 'YUM', 'CMG',
        'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'OXY',
        'BA', 'LMT', 'RTX', 'NOC', 'GD',
        'DIS', 'NFLX', 'CMCSA', 'VZ', 'T', 'TMUS',
        'V', 'MA', 'AXP', 'DFS', 'COF',
        'PG', 'UL', 'CL', 'KMB', 'GIS', 'K',
        'AAPL', 'MSFT', 'NVDA', 'AMD', 'TSLA'
    }
    
    # 常见非股票大写缩写（黑名单）
    NON_STOCK_WORDS = {
        'AI', 'CEO', 'CFO', 'CTO', 'COO', 'USA', 'USD', 'CNY', 'RMB',
        'GDP', 'CPI', 'PPI', 'PMI', 'IPO', 'ETF', 'EPS', 'PE', 'PB',
        'GDP', 'CAGR', 'YOY', 'QOQ', 'FY', 'Q1', 'Q2', 'Q3', 'Q4',
        'IBM', 'API', 'SaaS', 'PaaS', 'IaaS', 'GPU', 'CPU', 'TPU',
        'RAM', 'SSD', 'HDD', 'USB', 'HTTP', 'HTTPS', 'URL', 'HTML',
        'CEO', 'CFO', 'VP', 'SVP', 'EVP', 'MD', 'ED'
    }
    
    def extract(self, text: str) -> List[ExtractedEntity]:
        """从文本中提取股票代码"""
        entities = []
        
        # 提取美股
        for match in self.US_STOCK_PATTERN.finditer(text):
            code = match.group()
            if code in self.COMMON_US_STOCKS and code not in self.NON_STOCK_WORDS:
                entities.append(ExtractedEntity(
                    text=code,
                    type='Stock',
                    normalized=code,
                    confidence=0.95,
                    position=(match.start(), match.end()),
                    properties={'market': 'US', 'code': code}
                ))
            elif code not in self.NON_STOCK_WORDS:
                # 可能是股票，但置信度较低
                entities.append(ExtractedEntity(
                    text=code,
                    type='Stock',
                    normalized=code,
                    confidence=0.6,
                    position=(match.start(), match.end()),
                    properties={'market': 'US', 'code': code, 'unverified': True}
                ))
        
        # 提取A股
        for match in self.A_STOCK_PATTERN.finditer(text):
            code = match.group()
            entities.append(ExtractedEntity(
                text=code,
                type='Stock',
                normalized=code,
                confidence=0.9,
                position=(match.start(), match.end()),
                properties={'market': 'A股', 'code': code}
            ))
        
        # 提取港股
        for match in self.HK_STOCK_PATTERN.finditer(text):
            code = match.group(1)
            entities.append(ExtractedEntity(
                text=match.group(),
                type='Stock',
                normalized=code,
                confidence=0.9,
                position=(match.start(), match.end()),
                properties={'market': '港股', 'code': code}
            ))
        
        return entities


class IndustryExtractor:
    """行业名称提取器"""
    
    # A股行业分类标准
    INDUSTRIES = {
        # 一级行业
        '半导体', '电子', '计算机', '通信', '传媒', '互联网',
        '银行', '保险', '证券', '多元金融',
        '房地产', '建筑装饰', '建筑材料',
        '电力', '公用事业', '环保',
        '煤炭', '石油石化', '有色金属', '钢铁', '基础化工',
        '机械设备', '国防军工', '电力设备', '汽车', '家用电器',
        '食品饮料', '医药生物', '农林牧渔', '商贸零售', '社会服务',
        '纺织服饰', '轻工制造', '美容护理',
        '交通运输', '物流',
        # 细分行业
        'AI算力', '光通信', '存储芯片', '封测', '晶圆代工',
        '新能源汽车', '锂电池', '光伏', '风电', '储能',
        '创新药', 'CXO', '医疗器械', '中药',
        '白酒', '啤酒', '乳制品', '调味品',
        '游戏', '影视', '广告', '出版',
        '信创', '国产替代', '数字经济', '云计算', '大数据',
        '低空经济', '人形机器人', '固态电池'
    }
    
    def extract(self, text: str) -> List[ExtractedEntity]:
        """从文本中提取行业名称"""
        entities = []
        
        for industry in self.INDUSTRIES:
            # 精确匹配
            if industry in text:
                # 找到所有出现位置
                start = 0
                while True:
                    pos = text.find(industry, start)
                    if pos == -1:
                        break
                    entities.append(ExtractedEntity(
                        text=industry,
                        type='Industry',
                        normalized=industry,
                        confidence=0.9,
                        position=(pos, pos + len(industry)),
                        properties={}
                    ))
                    start = pos + 1
        
        return entities


class ConceptExtractor:
    """概念提取器"""
    
    # 热门概念词典
    CONCEPTS = {
        # 技术概念
        'ChatGPT', 'GPT', '大模型', 'AIGC', '生成式AI', 'AGI',
        '人工智能', '机器学习', '深度学习', '神经网络',
        '元宇宙', 'Web3', '区块链', 'NFT', '数字货币',
        '云计算', '边缘计算', '量子计算',
        '5G', '6G', '物联网', '工业互联网',
        # 政策概念
        '国产替代', '自主可控', '信创', '东数西算',
        '碳中和', '碳达峰', '新能源', '绿色金融',
        '共同富裕', '乡村振兴', '一带一路',
        # 市场概念
        '中特估', '高股息', '红利', '核心资产',
        '赛道股', '白马股', '成长股', '价值股',
        '科创板', '创业板', '北交所', '新三板',
        # 事件概念
        '美联储降息', '加息周期', '量化宽松', '缩表',
        '财报季', '业绩超预期', '业绩暴雷',
        '并购重组', '股权激励', '定增', '回购',
        # 其他
        '出海', '全球化', '供应链', '产业链'
    }
    
    def extract(self, text: str) -> List[ExtractedEntity]:
        """从文本中提取概念"""
        entities = []
        
        for concept in self.CONCEPTS:
            if concept in text:
                start = 0
                while True:
                    pos = text.find(concept, start)
                    if pos == -1:
                        break
                    entities.append(ExtractedEntity(
                        text=concept,
                        type='Concept',
                        normalized=concept,
                        confidence=0.85,
                        position=(pos, pos + len(concept)),
                        properties={}
                    ))
                    start = pos + 1
        
        return entities


class EventExtractor:
    """事件提取器"""
    
    # 事件模式
    EVENT_PATTERNS = [
        (re.compile(r'美联储\s*议息\s*会议'), '美联储议息', 0.95),
        (re.compile(r'美联储\s*降息'), '美联储降息', 0.9),
        (re.compile(r'美联储\s*加息'), '美联储加息', 0.9),
        (re.compile(r'央行\s*降准'), '央行降准', 0.9),
        (re.compile(r'央行\s*降息'), '央行降息', 0.9),
        (re.compile(r'财报\s*季'), '财报季', 0.85),
        (re.compile(r'业绩\s*发布'), '业绩发布', 0.85),
        (re.compile(r'业绩\s*预告'), '业绩预告', 0.85),
        (re.compile(r'业绩\s*超预期'), '业绩超预期', 0.8),
        (re.compile(r'业绩\s*暴雷'), '业绩暴雷', 0.8),
        (re.compile(r'重组\s*方案'), '重组方案', 0.85),
        (re.compile(r'并购\s*方案'), '并购方案', 0.85),
        (re.compile(r'定增\s*方案'), '定增方案', 0.85),
        (re.compile(r'股权\s*激励'), '股权激励', 0.85),
        (re.compile(r'回购\s*股份'), '股份回购', 0.85),
        (re.compile(r'分众\s*传媒'), '分众传媒', 0.9),
    ]
    
    def extract(self, text: str) -> List[ExtractedEntity]:
        """从文本中提取事件"""
        entities = []
        
        for pattern, event_name, confidence in self.EVENT_PATTERNS:
            for match in pattern.finditer(text):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    type='Event',
                    normalized=event_name,
                    confidence=confidence,
                    position=(match.start(), match.end()),
                    properties={}
                ))
        
        return entities


class PersonExtractor:
    """人物提取器"""
    
    # 知名人物词典
    PEOPLE = {
        '黄仁勋', 'Jensen Huang', '马斯克', 'Elon Musk',
        '巴菲特', 'Warren Buffett', '芒格', 'Charlie Munger',
        '贝索斯', 'Jeff Bezos', '扎克伯格', 'Mark Zuckerberg',
        '库克', 'Tim Cook', '纳德拉', 'Satya Nadella',
        '任正非', '雷军', '马云', '马化腾', '李彦宏',
        '张一鸣', '王兴', '黄峥', '刘强东',
        '鲍威尔', 'Powell', '耶伦', 'Yellen',
        '特朗普', 'Trump', '拜登', 'Biden',
    }
    
    def extract(self, text: str) -> List[ExtractedEntity]:
        """从文本中提取人物"""
        entities = []
        
        for person in self.PEOPLE:
            if person in text:
                start = 0
                while True:
                    pos = text.find(person, start)
                    if pos == -1:
                        break
                    entities.append(ExtractedEntity(
                        text=person,
                        type='Person',
                        normalized=person,
                        confidence=0.9,
                        position=(pos, pos + len(person)),
                        properties={}
                    ))
                    start = pos + 1
        
        return entities


class EntityExtractor:
    """实体提取器主类"""
    
    def __init__(self):
        self.stock_extractor = StockExtractor()
        self.industry_extractor = IndustryExtractor()
        self.concept_extractor = ConceptExtractor()
        self.event_extractor = EventExtractor()
        self.person_extractor = PersonExtractor()
    
    def extract(self, text: str) -> List[ExtractedEntity]:
        """从文本中提取所有类型的实体"""
        all_entities = []
        
        all_entities.extend(self.stock_extractor.extract(text))
        all_entities.extend(self.industry_extractor.extract(text))
        all_entities.extend(self.concept_extractor.extract(text))
        all_entities.extend(self.event_extractor.extract(text))
        all_entities.extend(self.person_extractor.extract(text))
        
        # 按位置排序
        all_entities.sort(key=lambda x: x.position[0])
        
        return all_entities
    
    def extract_to_entities(self, text: str) -> List[Entity]:
        """提取并转换为Entity对象"""
        extracted = self.extract(text)
        entities = []
        
        for ext in extracted:
            if ext.type == 'Stock':
                entity = create_stock_entity(
                    code=ext.properties.get('code', ext.normalized),
                    name=ext.text,
                    industry=ext.properties.get('industry'),
                    confidence=ext.confidence
                )
            elif ext.type == 'Industry':
                entity = create_industry_entity(name=ext.normalized)
            elif ext.type == 'Concept':
                entity = create_concept_entity(name=ext.normalized)
            else:
                # 其他类型
                entity = Entity(
                    id=f"{ext.type.lower()}_{ext.normalized}",
                    type=ext.type,
                    name=ext.normalized,
                    properties={'original_text': ext.text, 'confidence': ext.confidence}
                )
            
            entities.append(entity)
        
        return entities
    
    def deduplicate(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """实体消歧和去重"""
        seen = {}
        result = []
        
        for entity in entities:
            key = (entity.type, entity.normalized)
            
            if key not in seen:
                seen[key] = entity
                result.append(entity)
            else:
                # 保留置信度更高的
                if entity.confidence > seen[key].confidence:
                    seen[key] = entity
                    # 替换result中的
                    for i, e in enumerate(result):
                        if e.type == entity.type and e.normalized == entity.normalized:
                            result[i] = entity
                            break
        
        return result


# ========== 飞书文档处理 ==========

class FeishuDocumentProcessor:
    """飞书文档处理器"""
    
    def __init__(self, kg=None):
        self.extractor = EntityExtractor()
        self.kg = kg
    
    def process_text(self, text: str, doc_id: str = None, doc_title: str = None) -> Dict:
        """处理文本，提取实体并添加到知识图谱
        
        Returns:
            {
                'doc_id': str,
                'doc_title': str,
                'entities': List[Entity],
                'entity_count': int,
                'by_type': Dict[type, count]
            }
        """
        # 提取实体
        entities = self.extractor.extract_to_entities(text)
        
        # 添加到知识图谱（如果提供）
        if self.kg:
            for entity in entities:
                self.kg.add_entity(entity)
            
            # 添加文档实体
            if doc_id and doc_title:
                doc_entity = Entity(
                    id=f"report_{doc_id}",
                    type='Report',
                    name=doc_title,
                    properties={'doc_id': doc_id}
                )
                self.kg.add_entity(doc_entity)
                
                # 添加提及关系
                from knowledge_graph_core import Relation
                for entity in entities:
                    relation = Relation(
                        id=f"{entity.id}_mentioned_in_{doc_id}",
                        source_id=entity.id,
                        target_id=f"report_{doc_id}",
                        type='mentioned_in'
                    )
                    self.kg.add_relation(relation)
        
        # 统计
        by_type = {}
        for entity in entities:
            by_type[entity.type] = by_type.get(entity.type, 0) + 1
        
        return {
            'doc_id': doc_id,
            'doc_title': doc_title,
            'entities': entities,
            'entity_count': len(entities),
            'by_type': by_type
        }


# ========== 测试代码 ==========

if __name__ == "__main__":
    # 测试文本（高盛周报片段）
    test_text = """
    Goldman Sachs US Equities Weekly - May 1, 2026
    
    AI周期intact但短期需谨慎。半导体板块本周表现强劲，NVDA和AMD领涨。
    美联储降息预期升温，利好科技股。中特估概念持续发酵，中国长城等信创股受关注。
    
    持仓建议：
    - NVIDIA (NVDA): AI算力龙头，长期持有，目标价$1000
    - AMD: 与Intel竞争加剧，观察
    - Tesla (TSLA): 短期调整，中期看好
    
    行业关注：
    - 半导体：受益于AI需求增长
    - 新能源：光伏、储能赛道景气
    - 信创：国产替代主线
    
    风险提示：关注美联储议息会议，波动率上升。
    """
    
    print("=" * 60)
    print("A5L 知识图谱 - 实体提取器测试")
    print("=" * 60)
    
    # 创建提取器
    extractor = EntityExtractor()
    
    # 提取实体
    print("\n1. 提取实体（中间格式）:")
    extracted = extractor.extract(test_text)
    for e in extracted[:10]:  # 只显示前10个
        print(f"  [{e.type}] {e.text} -> {e.normalized} (置信度: {e.confidence:.2f})")
    
    # 转换为Entity对象
    print("\n2. 转换为Entity对象:")
    entities = extractor.extract_to_entities(test_text)
    for e in entities[:5]:
        print(f"  {e.type}: {e.name} (ID: {e.id})")
    
    # 去重测试
    print("\n3. 去重后:")
    extracted_dup = extractor.extract(test_text + " NVDA NVDA NVIDIA")  # 添加重复
    deduped = extractor.deduplicate(extracted_dup)
    print(f"  去重前: {len(extracted_dup)} 个")
    print(f"  去重后: {len(deduped)} 个")
    
    # 飞书文档处理测试
    print("\n4. 飞书文档处理:")
    from knowledge_graph_core import KnowledgeGraph
    kg = KnowledgeGraph()
    processor = FeishuDocumentProcessor(kg)
    
    result = processor.process_text(
        test_text,
        doc_id="gs_20260503",
        doc_title="高盛美股周报_20260503"
    )
    
    print(f"  文档: {result['doc_title']}")
    print(f"  提取实体: {result['entity_count']} 个")
    print(f"  按类型分布: {result['by_type']}")
    
    # 验证知识图谱
    print("\n5. 知识图谱验证:")
    stats = kg.get_stats()
    print(f"  实体总数: {stats['total_entities']}")
    print(f"  关系总数: {stats['total_relations']}")
    
    # 查询NVDA的关联
    kg.load_to_memory()
    related = kg.get_related_entities("stock_NVDA", depth=1)
    print(f"\n  NVDA关联实体: {len(related)} 个")
    for r in related[:3]:
        print(f"    - {r['entity_name']} ({r['relation_type']})")
    
    print("\n" + "=" * 60)
    print("✅ Phase 2 实体提取器测试完成!")
    print("=" * 60)
