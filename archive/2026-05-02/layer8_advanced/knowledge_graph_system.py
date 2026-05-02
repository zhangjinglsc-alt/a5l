#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱系统 (Knowledge Graph System)
P3阶段 - 行业/公司关联网络

功能:
- 知识图谱构建
- 实体关系提取
- 图谱查询
- 关联分析
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import networkx as nx
import numpy as np

sys.path.insert(0, "/workspace/projects/workspace")

class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        print("🕸️ 知识图谱构建器初始化")
    
    def add_entity(self, entity_id: str, entity_type: str, 
                   properties: Dict = None):
        """
        添加实体
        
        Args:
            entity_id: 实体ID
            entity_type: 实体类型 (company/person/industry/product)
            properties: 实体属性
        """
        if properties is None:
            properties = {}
        
        self.graph.add_node(
            entity_id,
            type=entity_type,
            **properties
        )
    
    def add_relation(self, from_entity: str, to_entity: str,
                     relation_type: str, properties: Dict = None):
        """
        添加关系
        
        Args:
            from_entity: 源实体
            to_entity: 目标实体
            relation_type: 关系类型
            properties: 关系属性
        """
        if properties is None:
            properties = {}
        
        self.graph.add_edge(
            from_entity,
            to_entity,
            relation=relation_type,
            **properties
        )
    
    def build_industry_chain(self, industry: str, 
                            companies: List[Dict]):
        """
        构建产业链
        
        Args:
            industry: 行业名称
            companies: 公司列表
        """
        # 添加行业节点
        industry_id = f"industry:{industry}"
        self.add_entity(industry_id, "industry", {"name": industry})
        
        # 添加公司节点和关系
        for company in companies:
            company_id = f"company:{company['symbol']}"
            self.add_entity(
                company_id,
                "company",
                {
                    "name": company.get('name', company['symbol']),
                    "symbol": company['symbol'],
                    "market_cap": company.get('market_cap', 0)
                }
            )
            
            # 公司与行业关系
            self.add_relation(
                company_id,
                industry_id,
                "belongs_to",
                {"weight": 1.0}
            )
        
        # 添加公司间关系 (竞争/合作)
        for i, c1 in enumerate(companies):
            for c2 in companies[i+1:]:
                c1_id = f"company:{c1['symbol']}"
                c2_id = f"company:{c2['symbol']}"
                
                # 竞争关系
                self.add_relation(
                    c1_id,
                    c2_id,
                    "competes_with",
                    {"weight": 0.8}
                )
                self.add_relation(
                    c2_id,
                    c1_id,
                    "competes_with",
                    {"weight": 0.8}
                )
    
    def build_supply_chain(self, relationships: List[Dict]):
        """
        构建供应链关系
        
        Args:
            relationships: 供应链关系列表
        """
        for rel in relationships:
            supplier_id = f"company:{rel['supplier']}"
            customer_id = f"company:{rel['customer']}"
            
            # 确保节点存在
            if supplier_id not in self.graph:
                self.add_entity(supplier_id, "company", {"symbol": rel['supplier']})
            if customer_id not in self.graph:
                self.add_entity(customer_id, "company", {"symbol": rel['customer']})
            
            # 供应关系
            self.add_relation(
                supplier_id,
                customer_id,
                "supplies_to",
                {
                    "product": rel.get('product', ''),
                    "amount": rel.get('amount', 0),
                    "weight": rel.get('weight', 1.0)
                }
            )
    
    def save_graph(self, filepath: str):
        """保存图谱"""
        data = {
            "nodes": [
                {
                    "id": node,
                    **self.graph.nodes[node]
                }
                for node in self.graph.nodes()
            ],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    **self.graph.edges[u, v]
                }
                for u, v in self.graph.edges()
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 知识图谱已保存: {filepath}")
    
    def load_graph(self, filepath: str):
        """加载图谱"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.graph = nx.DiGraph()
        
        for node_data in data['nodes']:
            node_id = node_data.pop('id')
            self.graph.add_node(node_id, **node_data)
        
        for edge_data in data['edges']:
            source = edge_data.pop('source')
            target = edge_data.pop('target')
            self.graph.add_edge(source, target, **edge_data)
        
        print(f"📂 知识图谱已加载: {filepath}")

class GraphQueryEngine:
    """图谱查询引擎"""
    
    def __init__(self, graph: nx.DiGraph = None):
        self.graph = graph or nx.DiGraph()
    
    def find_related_companies(self, company_id: str, 
                               max_depth: int = 2) -> List[Tuple[str, int, str]]:
        """
        查找关联公司
        
        Args:
            company_id: 公司ID
            max_depth: 最大搜索深度
            
        Returns:
            关联公司列表 [(company_id, depth, relation_type)]
        """
        related = []
        visited = {company_id}
        
        # BFS搜索
        queue = [(company_id, 0)]
        
        while queue:
            current, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            # 遍历邻居
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    relation = self.graph.edges[current, neighbor].get('relation', 'related')
                    related.append((neighbor, depth + 1, relation))
                    queue.append((neighbor, depth + 1))
            
            # 遍历反向邻居
            for predecessor in self.graph.predecessors(current):
                if predecessor not in visited:
                    visited.add(predecessor)
                    relation = self.graph.edges[predecessor, current].get('relation', 'related')
                    related.append((predecessor, depth + 1, relation))
                    queue.append((predecessor, depth + 1))
        
        return related
    
    def find_supply_chain_partners(self, company_id: str) -> Dict:
        """
        查找供应链合作伙伴
        
        Args:
            company_id: 公司ID
            
        Returns:
            上下游合作伙伴
        """
        suppliers = []
        customers = []
        
        # 供应商 (指向该公司的)
        for predecessor in self.graph.predecessors(company_id):
            edge_data = self.graph.edges[predecessor, company_id]
            if edge_data.get('relation') == 'supplies_to':
                suppliers.append({
                    'id': predecessor,
                    **edge_data
                })
        
        # 客户 (该公司指向的)
        for successor in self.graph.successors(company_id):
            edge_data = self.graph.edges[company_id, successor]
            if edge_data.get('relation') == 'supplies_to':
                customers.append({
                    'id': successor,
                    **edge_data
                })
        
        return {
            'suppliers': suppliers,
            'customers': customers
        }
    
    def calculate_centrality(self) -> Dict[str, float]:
        """计算节点中心性"""
        if len(self.graph) == 0:
            return {}
        
        # PageRank
        try:
            pagerank = nx.pagerank(self.graph)
        except:
            pagerank = {}
        
        # 度中心性
        degree = dict(nx.degree_centrality(self.graph))
        
        return {
            'pagerank': pagerank,
            'degree': degree
        }
    
    def find_clusters(self) -> List[Set[str]]:
        """查找社区/聚类"""
        if len(self.graph) == 0:
            return []
        
        # 将图转为无向图进行社区检测
        undirected = self.graph.to_undirected()
        
        try:
            communities = nx.community.greedy_modularity_communities(undirected)
            return [set(c) for c in communities]
        except:
            return []

class KnowledgeGraphSystem:
    """知识图谱系统"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.builder = KnowledgeGraphBuilder()
        self.query_engine = GraphQueryEngine(self.builder.graph)
        
        print("🕸️ 知识图谱系统初始化")
    
    def build_demo_graph(self):
        """构建演示图谱"""
        print("\n🔨 构建演示知识图谱...")
        
        # 新能源汽车产业链
        ev_companies = [
            {"symbol": "002594.SZ", "name": "比亚迪", "market_cap": 800000000000},
            {"symbol": "300750.SZ", "name": "宁德时代", "market_cap": 900000000000},
            {"symbol": "601012.SH", "name": "隆基绿能", "market_cap": 200000000000},
            {"symbol": "002460.SZ", "name": "赣锋锂业", "market_cap": 150000000000},
        ]
        
        self.builder.build_industry_chain("新能源汽车", ev_companies)
        
        # 添加供应链关系
        supply_relationships = [
            {"supplier": "002460.SZ", "customer": "300750.SZ", "product": "锂电池材料", "weight": 0.9},
            {"supplier": "300750.SZ", "customer": "002594.SZ", "product": "动力电池", "weight": 0.8},
            {"supplier": "601012.SH", "customer": "300750.SZ", "product": "光伏组件", "weight": 0.5},
        ]
        
        self.builder.build_supply_chain(supply_relationships)
        
        # 添加人物节点
        self.builder.add_entity(
            "person:王传福",
            "person",
            {"name": "王传福", "position": "董事长", "company": "002594.SZ"}
        )
        
        self.builder.add_relation(
            "person:王传福",
            "company:002594.SZ",
            "leads",
            {"weight": 1.0}
        )
        
        print(f"   实体数: {self.builder.graph.number_of_nodes()}")
        print(f"   关系数: {self.builder.graph.number_of_edges()}")
    
    def query_demo(self):
        """查询演示"""
        print("\n" + "="*70)
        print("🔍 图谱查询演示")
        print("="*70)
        
        # 更新查询引擎的图
        self.query_engine = GraphQueryEngine(self.builder.graph)
        
        # 查询1: 关联公司
        print("\n1. 查找比亚迪的关联公司 (深度2):")
        related = self.query_engine.find_related_companies(
            "company:002594.SZ",
            max_depth=2
        )
        for company_id, depth, relation in related[:5]:
            company_name = company_id.replace("company:", "")
            print(f"   {company_name} (深度{depth}, 关系: {relation})")
        
        # 查询2: 供应链
        print("\n2. 宁德时代的供应链:")
        partners = self.query_engine.find_supply_chain_partners("company:300750.SZ")
        
        print(f"   供应商 ({len(partners['suppliers'])}):")
        for supplier in partners['suppliers']:
            name = supplier['id'].replace("company:", "")
            product = supplier.get('product', '')
            print(f"     - {name} ({product})")
        
        print(f"   客户 ({len(partners['customers'])}):")
        for customer in partners['customers']:
            name = customer['id'].replace("company:", "")
            product = customer.get('product', '')
            print(f"     - {name} ({product})")
        
        # 查询3: 中心性
        print("\n3. 节点中心性分析:")
        centrality = self.query_engine.calculate_centrality()
        
        if centrality.get('degree'):
            print("   度中心性Top 3:")
            sorted_degree = sorted(
                centrality['degree'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            for node, score in sorted_degree:
                name = node.replace("company:", "").replace("industry:", "")
                print(f"     - {name}: {score:.4f}")
        
        # 查询4: 社区
        print("\n4. 社区检测:")
        clusters = self.query_engine.find_clusters()
        for i, cluster in enumerate(clusters, 1):
            names = [n.replace("company:", "").replace("industry:", "") for n in cluster]
            print(f"   社区{i}: {', '.join(names)}")
    
    def generate_report(self) -> str:
        """生成图谱报告"""
        report = f"""# 知识图谱分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 图谱统计

- **实体数**: {self.builder.graph.number_of_nodes()}
- **关系数**: {self.builder.graph.number_of_edges()}
- **密度**: {nx.density(self.builder.graph):.4f}

## 实体类型分布

"""
        
        # 统计实体类型
        type_counts = defaultdict(int)
        for node, data in self.builder.graph.nodes(data=True):
            entity_type = data.get('type', 'unknown')
            type_counts[entity_type] += 1
        
        for entity_type, count in type_counts.items():
            report += f"- {entity_type}: {count}\n"
        
        report += """
## 关系类型分布

"""
        
        # 统计关系类型
        relation_counts = defaultdict(int)
        for u, v, data in self.builder.graph.edges(data=True):
            relation_type = data.get('relation', 'unknown')
            relation_counts[relation_type] += 1
        
        for relation_type, count in relation_counts.items():
            report += f"- {relation_type}: {count}\n"
        
        report += """
## 应用场景

1. **产业链分析**: 识别上下游关系
2. **竞争分析**: 发现竞争对手
3. **风险传导**: 分析风险传播路径
4. **机会发现**: 寻找潜在合作伙伴

---
**ARCHITECT-5L Knowledge Graph System**
"""
        
        return report

def demo():
    """演示知识图谱系统"""
    print("="*70)
    print("🕸️ 知识图谱系统演示")
    print("="*70)
    print()
    
    # 初始化系统
    kg_system = KnowledgeGraphSystem()
    
    # 构建演示图谱
    kg_system.build_demo_graph()
    
    # 查询演示
    kg_system.query_demo()
    
    # 生成报告
    print("\n" + "="*70)
    print("📄 生成图谱报告")
    print("="*70)
    report = kg_system.generate_report()
    print(report)
    
    # 保存图谱
    os.makedirs(f"{kg_system.workspace}/data/knowledge_graph", exist_ok=True)
    kg_system.builder.save_graph(
        f"{kg_system.workspace}/data/knowledge_graph/demo_graph.json"
    )
    
    print()
    print("="*70)
    print("✅ 知识图谱系统演示完成!")
    print("="*70)

if __name__ == "__main__":
    demo()
