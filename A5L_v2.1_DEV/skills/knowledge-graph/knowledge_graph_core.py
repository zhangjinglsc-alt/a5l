"""
A5L Knowledge Graph Builder
Layer 2 - Strategy Engine
SQLite + NetworkX Hybrid Architecture

Core modules:
- Entity extraction from documents
- Relationship building
- Graph storage and query
- Visualization
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import networkx as nx
from contextlib import contextmanager


@dataclass
class Entity:
    """知识图谱实体"""
    id: str
    type: str  # Stock, Industry, Concept, Event, Person, Report
    name: str
    code: Optional[str] = None  # 股票代码等
    properties: Dict[str, Any] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Entity':
        return cls(**data)


@dataclass
class Relation:
    """知识图谱关系"""
    id: str
    source_id: str
    target_id: str
    type: str  # belongs_to, industry_chain, competes_with, correlates_with, affected_by, mentioned_in, holds
    properties: Dict[str, Any] = None
    confidence: float = 1.0
    created_at: str = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Relation':
        return cls(**data)


class GraphDatabase:
    """SQLite-based graph storage"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, 'data', 'knowledge_graph.db')
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接上下文"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 实体表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    code TEXT,
                    properties TEXT,  -- JSON格式
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 关系表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS relations (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    properties TEXT,  -- JSON格式
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES entities(id),
                    FOREIGN KEY (target_id) REFERENCES entities(id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(type)')
            
            conn.commit()
    
    # ========== 实体操作 ==========
    
    def add_entity(self, entity: Entity) -> bool:
        """添加实体"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO entities 
                    (id, type, name, code, properties, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entity.id,
                    entity.type,
                    entity.name,
                    entity.code,
                    json.dumps(entity.properties, ensure_ascii=False),
                    entity.created_at,
                    entity.updated_at
                ))
                return True
        except Exception as e:
            print(f"Error adding entity: {e}")
            return False
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM entities WHERE id = ?', (entity_id,))
            row = cursor.fetchone()
            
            if row:
                return Entity(
                    id=row['id'],
                    type=row['type'],
                    name=row['name'],
                    code=row['code'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """按类型获取实体"""
        entities = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM entities WHERE type = ?', (entity_type,))
            for row in cursor.fetchall():
                entities.append(Entity(
                    id=row['id'],
                    type=row['type'],
                    name=row['name'],
                    code=row['code'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
        return entities
    
    def search_entities(self, keyword: str) -> List[Entity]:
        """搜索实体"""
        entities = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM entities 
                WHERE name LIKE ? OR code LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%'))
            for row in cursor.fetchall():
                entities.append(Entity(
                    id=row['id'],
                    type=row['type'],
                    name=row['name'],
                    code=row['code'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
        return entities
    
    def get_all_entities(self) -> List[Entity]:
        """获取所有实体"""
        entities = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM entities')
            for row in cursor.fetchall():
                entities.append(Entity(
                    id=row['id'],
                    type=row['type'],
                    name=row['name'],
                    code=row['code'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
        return entities
    
    # ========== 关系操作 ==========
    
    def add_relation(self, relation: Relation) -> bool:
        """添加关系"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO relations 
                    (id, source_id, target_id, type, properties, confidence, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    relation.id,
                    relation.source_id,
                    relation.target_id,
                    relation.type,
                    json.dumps(relation.properties, ensure_ascii=False),
                    relation.confidence,
                    relation.created_at
                ))
                return True
        except Exception as e:
            print(f"Error adding relation: {e}")
            return False
    
    def get_relations_by_source(self, source_id: str) -> List[Relation]:
        """获取某实体的出边关系"""
        relations = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM relations WHERE source_id = ?', (source_id,))
            for row in cursor.fetchall():
                relations.append(Relation(
                    id=row['id'],
                    source_id=row['source_id'],
                    target_id=row['target_id'],
                    type=row['type'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    confidence=row['confidence'],
                    created_at=row['created_at']
                ))
        return relations
    
    def get_relations_by_target(self, target_id: str) -> List[Relation]:
        """获取某实体的入边关系"""
        relations = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM relations WHERE target_id = ?', (target_id,))
            for row in cursor.fetchall():
                relations.append(Relation(
                    id=row['id'],
                    source_id=row['source_id'],
                    target_id=row['target_id'],
                    type=row['type'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    confidence=row['confidence'],
                    created_at=row['created_at']
                ))
        return relations
    
    def get_all_relations(self) -> List[Relation]:
        """获取所有关系"""
        relations = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM relations')
            for row in cursor.fetchall():
                relations.append(Relation(
                    id=row['id'],
                    source_id=row['source_id'],
                    target_id=row['target_id'],
                    type=row['type'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    confidence=row['confidence'],
                    created_at=row['created_at']
                ))
        return relations
    
    # ========== 统计信息 ==========
    
    def get_stats(self) -> Dict:
        """获取图谱统计信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 实体统计
            cursor.execute('SELECT type, COUNT(*) FROM entities GROUP BY type')
            entity_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 关系统计
            cursor.execute('SELECT type, COUNT(*) FROM relations GROUP BY type')
            relation_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 总数
            cursor.execute('SELECT COUNT(*) FROM entities')
            total_entities = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM relations')
            total_relations = cursor.fetchone()[0]
            
            return {
                'total_entities': total_entities,
                'total_relations': total_relations,
                'entity_types': entity_stats,
                'relation_types': relation_stats
            }


class KnowledgeGraph:
    """知识图谱核心类 - SQLite + NetworkX混合架构"""
    
    def __init__(self, db_path: str = None):
        self.db = GraphDatabase(db_path)
        self.graph = nx.DiGraph()  # 有向图
        self._loaded = False
    
    def load_to_memory(self) -> None:
        """从SQLite加载到NetworkX内存"""
        if self._loaded:
            return
        
        # 清空当前图
        self.graph.clear()
        
        # 加载所有实体
        entities = self.db.get_all_entities()
        for entity in entities:
            self.graph.add_node(
                entity.id,
                type=entity.type,
                name=entity.name,
                code=entity.code,
                properties=entity.properties
            )
        
        # 加载所有关系
        relations = self.db.get_all_relations()
        for relation in relations:
            self.graph.add_edge(
                relation.source_id,
                relation.target_id,
                type=relation.type,
                confidence=relation.confidence,
                properties=relation.properties
            )
        
        self._loaded = True
        print(f"Loaded {len(entities)} entities and {len(relations)} relations to memory")
    
    def save_from_memory(self) -> None:
        """从NetworkX保存到SQLite"""
        # 保存所有实体
        for node_id, data in self.graph.nodes(data=True):
            entity = Entity(
                id=node_id,
                type=data.get('type', 'Unknown'),
                name=data.get('name', node_id),
                code=data.get('code'),
                properties=data.get('properties', {})
            )
            self.db.add_entity(entity)
        
        # 保存所有关系
        for source, target, data in self.graph.edges(data=True):
            relation = Relation(
                id=f"{source}_{target}_{data.get('type', 'related')}",
                source_id=source,
                target_id=target,
                type=data.get('type', 'related'),
                confidence=data.get('confidence', 1.0),
                properties=data.get('properties', {})
            )
            self.db.add_relation(relation)
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """按类型获取实体"""
        return self.db.get_entities_by_type(entity_type)
    
    # ========== 实体操作 ==========
    
    def add_entity(self, entity: Entity) -> bool:
        """添加实体（同时更新内存和数据库）"""
        # 保存到数据库
        if not self.db.add_entity(entity):
            return False
        
        # 更新内存图
        if self._loaded:
            self.graph.add_node(
                entity.id,
                type=entity.type,
                name=entity.name,
                code=entity.code,
                properties=entity.properties
            )
        
        return True
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        return self.db.get_entity(entity_id)
    
    # ========== 关系操作 ==========
    
    def add_relation(self, relation: Relation) -> bool:
        """添加关系（同时更新内存和数据库）"""
        # 保存到数据库
        if not self.db.add_relation(relation):
            return False
        
        # 更新内存图
        if self._loaded:
            self.graph.add_edge(
                relation.source_id,
                relation.target_id,
                type=relation.type,
                confidence=relation.confidence,
                properties=relation.properties
            )
        
        return True
    
    # ========== 查询接口 ==========
    
    def get_related_entities(self, entity_id: str, relation_type: str = None, depth: int = 1) -> List[Dict]:
        """获取关联实体
        
        Args:
            entity_id: 中心实体ID
            relation_type: 关系类型过滤（可选）
            depth: 查询深度（1=直接关联，2=间接关联）
        
        Returns:
            关联实体列表
        """
        if not self._loaded:
            self.load_to_memory()
        
        if entity_id not in self.graph:
            return []
        
        results = []
        
        if depth == 1:
            # 直接关联
            for neighbor in self.graph.neighbors(entity_id):
                edge_data = self.graph.get_edge_data(entity_id, neighbor)
                if relation_type is None or edge_data.get('type') == relation_type:
                    neighbor_data = self.graph.nodes[neighbor]
                    results.append({
                        'entity_id': neighbor,
                        'entity_type': neighbor_data.get('type'),
                        'entity_name': neighbor_data.get('name'),
                        'relation_type': edge_data.get('type'),
                        'relation_properties': edge_data.get('properties', {})
                    })
        
        elif depth == 2:
            # 间接关联（2跳）
            for neighbor1 in self.graph.neighbors(entity_id):
                for neighbor2 in self.graph.neighbors(neighbor1):
                    if neighbor2 != entity_id:
                        edge1 = self.graph.get_edge_data(entity_id, neighbor1)
                        edge2 = self.graph.get_edge_data(neighbor1, neighbor2)
                        neighbor_data = self.graph.nodes[neighbor2]
                        results.append({
                            'entity_id': neighbor2,
                            'entity_type': neighbor_data.get('type'),
                            'entity_name': neighbor_data.get('name'),
                            'path': [
                                {'entity': neighbor1, 'relation': edge1.get('type')},
                                {'entity': neighbor2, 'relation': edge2.get('type')}
                            ]
                        })
        
        return results
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 3) -> List[List[Dict]]:
        """查找两实体间的路径
        
        Args:
            start_id: 起始实体ID
            end_id: 目标实体ID
            max_depth: 最大深度
        
        Returns:
            路径列表，每条路径是节点和边的序列
        """
        if not self._loaded:
            self.load_to_memory()
        
        if start_id not in self.graph or end_id not in self.graph:
            return []
        
        try:
            paths = list(nx.all_simple_paths(
                self.graph, start_id, end_id, cutoff=max_depth
            ))
            
            result = []
            for path in paths:
                path_detail = []
                for i in range(len(path)):
                    node_data = self.graph.nodes[path[i]]
                    path_detail.append({
                        'entity_id': path[i],
                        'entity_name': node_data.get('name'),
                        'entity_type': node_data.get('type')
                    })
                    if i < len(path) - 1:
                        edge_data = self.graph.get_edge_data(path[i], path[i+1])
                        path_detail.append({
                            'relation_type': edge_data.get('type'),
                            'confidence': edge_data.get('confidence', 1.0)
                        })
                result.append(path_detail)
            
            return result
        except nx.NetworkXNoPath:
            return []
    
    def get_industry_chain(self, entity_id: str) -> Dict:
        """获取产业链关系"""
        if not self._loaded:
            self.load_to_memory()
        
        upstream = []  # 上游
        downstream = []  # 下游
        
        # 查找上游（入边，类型为industry_chain且方向为upstream）
        for source, target, data in self.graph.in_edges(entity_id, data=True):
            if data.get('type') == 'industry_chain':
                source_data = self.graph.nodes[source]
                upstream.append({
                    'entity_id': source,
                    'entity_name': source_data.get('name'),
                    'relation': data.get('properties', {}).get('direction', 'supply')
                })
        
        # 查找下游（出边）
        for source, target, data in self.graph.out_edges(entity_id, data=True):
            if data.get('type') == 'industry_chain':
                target_data = self.graph.nodes[target]
                downstream.append({
                    'entity_id': target,
                    'entity_name': target_data.get('name'),
                    'relation': data.get('properties', {}).get('direction', 'supply')
                })
        
        return {
            'center': entity_id,
            'upstream': upstream,
            'downstream': downstream
        }
    
    def get_concept_stocks(self, concept_id: str) -> List[Dict]:
        """获取概念关联的股票"""
        return self.get_related_entities(concept_id, relation_type='correlates_with')
    
    # ========== 统计接口 ==========
    
    def get_stats(self) -> Dict:
        """获取图谱统计信息"""
        return self.db.get_stats()
    
    def get_centrality(self, entity_id: str = None) -> Dict:
        """获取中心性分析（PageRank）"""
        if not self._loaded:
            self.load_to_memory()
        
        if len(self.graph) == 0:
            return {}
        
        pagerank = nx.pagerank(self.graph)
        
        if entity_id:
            return {entity_id: pagerank.get(entity_id, 0)}
        
        # 返回Top 10
        sorted_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        return {k: v for k, v in sorted_pr[:10]}


# ========== 便捷函数 ==========

def create_stock_entity(code: str, name: str, industry: str = None, **kwargs) -> Entity:
    """创建股票实体"""
    return Entity(
        id=f"stock_{code}",
        type="Stock",
        name=name,
        code=code,
        properties={
            'industry': industry,
            **kwargs
        }
    )


def create_industry_entity(name: str, **kwargs) -> Entity:
    """创建行业实体"""
    return Entity(
        id=f"industry_{name}",
        type="Industry",
        name=name,
        properties=kwargs
    )


def create_concept_entity(name: str, **kwargs) -> Entity:
    """创建概念实体"""
    return Entity(
        id=f"concept_{name}",
        type="Concept",
        name=name,
        properties=kwargs
    )


def create_belongs_to_relation(stock_id: str, industry_id: str) -> Relation:
    """创建属于行业关系"""
    return Relation(
        id=f"{stock_id}_belongs_to_{industry_id}",
        source_id=stock_id,
        target_id=industry_id,
        type="belongs_to"
    )


def create_industry_chain_relation(source_id: str, target_id: str, direction: str = "supply") -> Relation:
    """创建产业链关系"""
    return Relation(
        id=f"{source_id}_chain_{target_id}",
        source_id=source_id,
        target_id=target_id,
        type="industry_chain",
        properties={'direction': direction}
    )


# ========== 测试代码 ==========

if __name__ == "__main__":
    # 创建知识图谱实例
    kg = KnowledgeGraph()
    
    # 添加股票实体
    nvda = create_stock_entity("NVDA", "NVIDIA", "半导体", market_cap="2.3T")
    amd = create_stock_entity("AMD", "AMD", "半导体")
    intel = create_stock_entity("INTC", "Intel", "半导体")
    
    # 添加行业实体
    semiconductor = create_industry_entity("半导体", description="芯片设计与制造")
    ai = create_concept_entity("AI算力", trend="hot")
    
    # 添加到图谱
    kg.add_entity(nvda)
    kg.add_entity(amd)
    kg.add_entity(intel)
    kg.add_entity(semiconductor)
    kg.add_entity(ai)
    
    # 添加关系
    kg.add_relation(create_belongs_to_relation("stock_NVDA", "industry_半导体"))
    kg.add_relation(create_belongs_to_relation("stock_AMD", "industry_半导体"))
    kg.add_relation(create_belongs_to_relation("stock_INTC", "industry_半导体"))
    
    # 竞争关系
    kg.add_relation(Relation(
        id="stock_NVDA_competes_stock_AMD",
        source_id="stock_NVDA",
        target_id="stock_AMD",
        type="competes_with"
    ))
    
    # 概念关联
    kg.add_relation(Relation(
        id="stock_NVDA_correlates_concept_AI算力",
        source_id="stock_NVDA",
        target_id="concept_AI算力",
        type="correlates_with",
        properties={'strength': 'high'}
    ))
    
    # 加载到内存
    kg.load_to_memory()
    
    # 查询关联
    print("\n=== NVDA关联实体 ===")
    related = kg.get_related_entities("stock_NVDA", depth=1)
    for r in related:
        print(f"  {r['entity_name']} ({r['entity_type']}) - {r['relation_type']}")
    
    # 查询路径
    print("\n=== NVDA到AI算力的路径 ===")
    paths = kg.find_path("stock_NVDA", "concept_AI算力")
    for path in paths:
        print("  ", " -> ".join([p.get('entity_name', p.get('relation_type')) for p in path]))
    
    # 统计信息
    print("\n=== 图谱统计 ===")
    stats = kg.get_stats()
    print(f"  实体数: {stats['total_entities']}")
    print(f"  关系数: {stats['total_relations']}")
    print(f"  实体类型: {stats['entity_types']}")
    print(f"  关系类型: {stats['relation_types']}")
    
    # PageRank
    print("\n=== 中心性Top 5 ===")
    centrality = kg.get_centrality()
    for entity_id, score in list(centrality.items())[:5]:
        entity = kg.get_entity(entity_id)
        if entity:
            print(f"  {entity.name}: {score:.4f}")
    
    print("\n✅ 知识图谱基础框架测试完成!")
