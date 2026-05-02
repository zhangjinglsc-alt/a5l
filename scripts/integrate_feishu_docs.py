#!/usr/bin/env python3
"""
飞书云文档整合脚本
将飞书中已有的研报和分析导入Knowledge Guardian
"""

import sys
sys.path.insert(0, '/workspace/projects/workspace')

from ARCHITECT_5L.layer0_control.knowledge_guardian import (
    KnowledgeGuardian, ContentType, KnowledgeSource, KnowledgeItem
)
from datetime import datetime
import hashlib

def integrate_feishu_documents():
    """整合飞书云文档到知识库"""
    
    guardian = KnowledgeGuardian()
    
    # 飞书云文档列表
    feishu_docs = [
        {
            "name": "水晶光电 (002273.SZ) 深度分析报告 - A5L+UZI",
            "token": "QJSRdidsuooUSkxMwsucG1nMnq4",
            "url": "https://my.feishu.cn/docx/QJSRdidsuooUSkxMwsucG1nMnq4",
            "type": "stock_analysis",
            "stock_code": "002273.SZ",
            "stock_name": "水晶光电",
            "industry": "光学光电子"
        },
        {
            "name": "A5L-研报阅读补充说明-2026-05-02",
            "token": "DouqdbQnqo1BL4xShYBcmtJPnCe",
            "url": "https://my.feishu.cn/docx/DouqdbQnqo1BL4xShYBcmtJPnCe",
            "type": "system_doc",
            "category": "说明文档"
        },
        {
            "name": "A5L系统最终同步报告-2026-05-02",
            "token": "ZEOfd9N49o3vh2xiqAHcEceEn6e",
            "url": "https://my.feishu.cn/docx/ZEOfd9N49o3vh2xiqAHcEceEn6e",
            "type": "system_doc",
            "category": "系统报告"
        }
    ]
    
    print("=" * 70)
    print("☁️ 飞书云文档整合到知识库")
    print("=" * 70)
    
    integrated_count = 0
    
    for doc in feishu_docs:
        try:
            # 生成唯一ID
            item_id = hashlib.md5(f"feishu_{doc['token']}".encode()).hexdigest()[:12]
            
            if doc["type"] == "stock_analysis":
                # 创建个股分析条目
                item = KnowledgeItem(
                    item_id=item_id,
                    title=doc["name"],
                    content_type=ContentType.STOCK_ANALYSIS.value,
                    source=KnowledgeSource.A5L_GENERATED.value,
                    stock_code=doc.get("stock_code"),
                    stock_name=doc.get("stock_name"),
                    industry=doc.get("industry"),
                    feishu_url=doc["url"],
                    tags=["飞书同步", "A5L分析", doc.get("industry", "")],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                guardian.knowledge_index[item_id] = item
                print(f"✅ 已整合个股分析: {doc['name']}")
                
            else:
                # 创建系统文档条目
                item = KnowledgeItem(
                    item_id=item_id,
                    title=doc["name"],
                    content_type=ContentType.SYSTEM_DOC.value,
                    source=KnowledgeSource.A5L_GENERATED.value,
                    feishu_url=doc["url"],
                    tags=["飞书同步", doc.get("category", "文档")],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                guardian.knowledge_index[item_id] = item
                print(f"✅ 已整合系统文档: {doc['name']}")
            
            integrated_count += 1
            
        except Exception as e:
            print(f"❌ 整合失败 {doc['name']}: {e}")
    
    # 保存索引
    guardian._save_indexes()
    
    print(f"\n{'=' * 70}")
    print(f"📊 整合完成: {integrated_count}/{len(feishu_docs)} 个文档")
    print("=" * 70)
    
    # 显示知识库统计
    stats = guardian.get_knowledge_stats()
    print(f"\n📈 知识库当前状态:")
    print(f"   • 总条目数: {stats['total_items']}")
    print(f"   • 覆盖股票: {stats['stocks_covered']}")
    print(f"   • 行业分布: {list(stats['by_industry'].keys())[:5]}")
    
    return integrated_count

if __name__ == "__main__":
    integrate_feishu_documents()
