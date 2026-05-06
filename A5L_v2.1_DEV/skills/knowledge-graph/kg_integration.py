"""
A5L Knowledge Graph - Integration & Automation
Phase 5: Integration with A5L system and automation

Features:
- Weekly auto-update from Feishu documents
- Integration with Knowledge Guardian
- API endpoints for other skills
- Scheduled tasks
"""

import os
import sys
import json
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_graph_core import KnowledgeGraph
from entity_extractor import FeishuDocumentProcessor, EntityExtractor
from relation_builder import RelationBuilder
from visualizer import KGVisualizer


class KGIntegration:
    """知识图谱集成器"""
    
    def __init__(self, kg: KnowledgeGraph = None):
        self.kg = kg or KnowledgeGraph()
        self.extractor = EntityExtractor()
        self.relation_builder = RelationBuilder()
        self.processor = FeishuDocumentProcessor(self.kg)
        self.visualizer = KGVisualizer(self.kg)
    
    def process_feishu_document(self, doc_content: str, doc_id: str, doc_title: str) -> Dict:
        """处理飞书文档并更新知识图谱
        
        Returns:
            {
                'doc_id': str,
                'doc_title': str,
                'entities_added': int,
                'relations_added': int,
                'entity_types': Dict,
                'timestamp': str
            }
        """
        print(f"[KG] Processing document: {doc_title}")
        
        # 1. 提取实体
        result = self.processor.process_text(doc_content, doc_id, doc_title)
        entities_added = result['entity_count']
        
        # 2. 构建关系
        relation_result = self.relation_builder.build_from_document(
            self.kg, doc_content, doc_id
        )
        relations_added = relation_result['count']
        
        # 3. 统计信息
        output = {
            'doc_id': doc_id,
            'doc_title': doc_title,
            'entities_added': entities_added,
            'relations_added': relations_added,
            'entity_types': result['by_type'],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"[KG] Added {entities_added} entities, {relations_added} relations")
        
        return output
    
    def weekly_update(self, documents: List[Dict]) -> Dict:
        """周度更新 - 处理一批文档
        
        Args:
            documents: List of {'content': str, 'id': str, 'title': str}
        
        Returns:
            更新统计
        """
        print("\n" + "=" * 60)
        print("A5L Knowledge Graph - Weekly Update")
        print("=" * 60)
        
        total_stats = {
            'documents_processed': 0,
            'total_entities': 0,
            'total_relations': 0,
            'details': []
        }
        
        for doc in documents:
            result = self.process_feishu_document(
                doc['content'],
                doc['id'],
                doc['title']
            )
            
            total_stats['documents_processed'] += 1
            total_stats['total_entities'] += result['entities_added']
            total_stats['total_relations'] += result['relations_added']
            total_stats['details'].append(result)
        
        # 生成可视化
        print("\n[KG] Generating visualizations...")
        self.visualizer.render_full_graph()
        
        # 获取最终统计
        final_stats = self.kg.get_stats()
        total_stats['final_graph_stats'] = final_stats
        
        print("\n" + "=" * 60)
        print(f"Weekly Update Complete:")
        print(f"  Documents: {total_stats['documents_processed']}")
        print(f"  Entities: +{total_stats['total_entities']}")
        print(f"  Relations: +{total_stats['total_relations']}")
        print(f"  Total in KG: {final_stats['total_entities']} entities, {final_stats['total_relations']} relations")
        print("=" * 60)
        
        return total_stats
    
    def export_report(self, output_path: str = None) -> str:
        """导出知识图谱报告"""
        if output_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(base_dir, 'reports', f'kg_report_{datetime.now().strftime("%Y%m%d")}.json')
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        stats = self.kg.get_stats()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'graph_stats': stats,
            'entity_distribution': stats['entity_types'],
            'relation_distribution': stats['relation_types'],
            'top_entities': self.kg.get_centrality()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def query_api(self, query_type: str, **kwargs) -> Dict:
        """API查询接口 - 供其他SKILL调用
        
        Args:
            query_type: 'related', 'path', 'industry_chain', 'concept_stocks'
            **kwargs: 查询参数
        
        Returns:
            查询结果
        """
        if query_type == 'related':
            entity_id = kwargs.get('entity_id')
            depth = kwargs.get('depth', 1)
            return {
                'entity_id': entity_id,
                'related': self.kg.get_related_entities(entity_id, depth=depth)
            }
        
        elif query_type == 'path':
            start_id = kwargs.get('start_id')
            end_id = kwargs.get('end_id')
            max_depth = kwargs.get('max_depth', 3)
            return {
                'start': start_id,
                'end': end_id,
                'paths': self.kg.find_path(start_id, end_id, max_depth)
            }
        
        elif query_type == 'industry_chain':
            entity_id = kwargs.get('entity_id')
            return self.kg.get_industry_chain(entity_id)
        
        elif query_type == 'concept_stocks':
            concept_id = kwargs.get('concept_id')
            return {
                'concept_id': concept_id,
                'stocks': self.kg.get_concept_stocks(concept_id)
            }
        
        elif query_type == 'stock_analysis':
            stock_id = kwargs.get('stock_id')
            return self.relation_builder.analyze_stock_relationships(self.kg, stock_id)
        
        else:
            return {'error': f'Unknown query type: {query_type}'}
    
    def scheduled_update(self):
        """定时更新任务（供schedule调用）"""
        print(f"\n[{datetime.now()}] Scheduled KG update started")
        
        # 这里应该从飞书获取本周新文档
        # 目前使用模拟数据
        documents = self._fetch_new_documents()
        
        if documents:
            self.weekly_update(documents)
        else:
            print("No new documents to process")
    
    def _fetch_new_documents(self) -> List[Dict]:
        """获取新文档（模拟）"""
        # TODO: 集成飞书API获取实际文档
        return []


def setup_scheduled_tasks():
    """设置定时任务"""
    integration = KGIntegration()
    
    # 每周日22:00执行更新
    schedule.every().sunday.at("22:00").do(integration.scheduled_update)
    
    print("[KG] Scheduled tasks setup complete:")
    print("  - Weekly update: Every Sunday 22:00")
    
    return schedule


# ========== CLI接口 ==========

def main():
    """主函数 - CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='A5L Knowledge Graph')
    parser.add_argument('--update', action='store_true', help='Run weekly update')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization')
    parser.add_argument('--query', type=str, help='Query type: related, path, industry_chain')
    parser.add_argument('--entity', type=str, help='Entity ID for query')
    parser.add_argument('--report', action='store_true', help='Generate report')
    
    args = parser.parse_args()
    
    kg = KnowledgeGraph()
    integration = KGIntegration(kg)
    
    if args.update:
        # 执行更新（需要实际文档数据）
        print("Please provide documents for update")
    
    elif args.visualize:
        output = integration.visualizer.render_full_graph()
        print(f"Visualization saved to: {output}")
    
    elif args.query and args.entity:
        result = integration.query_api(args.query, entity_id=args.entity)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.report:
        output = integration.export_report()
        print(f"Report saved to: {output}")
    
    else:
        parser.print_help()


# ========== 快捷集成函数 ==========

def get_knowledge_graph() -> KnowledgeGraph:
    """获取知识图谱实例（供其他模块使用）"""
    return KnowledgeGraph()


def analyze_stock(stock_code: str) -> Dict:
    """分析股票关系（快捷函数）"""
    kg = KnowledgeGraph()
    integration = KGIntegration(kg)
    stock_id = f"stock_{stock_code}"
    return integration.query_api('stock_analysis', stock_id=stock_id)


def find_investment_opportunities(concept: str) -> List[Dict]:
    """查找投资机会（基于概念）"""
    kg = KnowledgeGraph()
    integration = KGIntegration(kg)
    
    # 获取概念关联的所有股票
    concept_id = f"concept_{concept}"
    stocks = integration.query_api('concept_stocks', concept_id=concept_id)
    
    # 分析每只股票
    opportunities = []
    for stock in stocks.get('stocks', []):
        analysis = integration.query_api('stock_analysis', stock_id=stock['entity_id'])
        opportunities.append({
            'stock': stock,
            'analysis': analysis
        })
    
    return opportunities


if __name__ == "__main__":
    main()
