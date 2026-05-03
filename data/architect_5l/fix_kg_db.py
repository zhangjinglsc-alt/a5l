#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱数据库修复工具
修复 entities 表缺失问题
"""

import sqlite3
import os

def fix_knowledge_graph_db():
    """修复知识图谱数据库"""
    db_path = "/workspace/projects/workspace/data/architect_5l/architect_5l.db"
    
    print("=" * 60)
    print("🔧 知识图谱数据库修复工具")
    print("=" * 60)
    
    # 检查数据库是否存在
    if not os.path.exists(db_path):
        print(f"❌ 数据库不存在: {db_path}")
        return False
    
    print(f"\n📁 数据库路径: {db_path}")
    print(f"📊 数据库大小: {os.path.getsize(db_path) / 1024:.1f} KB")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查现有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📋 现有表: {', '.join(existing_tables) if existing_tables else '无'}")
    
    # 创建 entities 表
    if 'entities' not in existing_tables:
        print("\n🔨 创建 entities 表...")
        cursor.execute("""
            CREATE TABLE entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                sector TEXT,
                industry TEXT,
                market_cap REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ entities 表创建成功")
    else:
        print("\n✅ entities 表已存在")
    
    # 创建 relations 表
    if 'relations' not in existing_tables:
        print("\n🔨 创建 relations 表...")
        cursor.execute("""
            CREATE TABLE relations (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES entities (id),
                FOREIGN KEY (target_id) REFERENCES entities (id)
            )
        """)
        print("✅ relations 表创建成功")
    else:
        print("\n✅ relations 表已存在")
    
    # 创建 decisions 表 (用于存储集体决策记录)
    if 'decisions' not in existing_tables:
        print("\n🔨 创建 decisions 表...")
        cursor.execute("""
            CREATE TABLE decisions (
                id TEXT PRIMARY KEY,
                proposal_type TEXT NOT NULL,
                title TEXT NOT NULL,
                target TEXT NOT NULL,
                proposed_action TEXT,
                final_score REAL,
                consensus_level TEXT,
                status TEXT,
                votes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_at TIMESTAMP
            )
        """)
        print("✅ decisions 表创建成功")
    else:
        print("\n✅ decisions 表已存在")
    
    # 创建 signals 表 (用于存储投资信号)
    if 'signals' not in existing_tables:
        print("\n🔨 创建 signals 表...")
        cursor.execute("""
            CREATE TABLE signals (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                confidence REAL,
                predictions TEXT,
                validations TEXT,
                overall_accuracy REAL,
                rating TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                valid_until TIMESTAMP
            )
        """)
        print("✅ signals 表创建成功")
    else:
        print("\n✅ signals 表已存在")
    
    # 插入示例数据
    print("\n📝 插入示例数据...")
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM entities")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_entities = [
            ("NVDA", "NVIDIA", "stock", "Technology", "Semiconductors", 2500000000000),
            ("AAPL", "Apple", "stock", "Technology", "Consumer Electronics", 3000000000000),
            ("TSLA", "Tesla", "stock", "Consumer Cyclical", "Auto Manufacturers", 800000000000),
            ("688981", "中芯国际", "stock", "Technology", "Semiconductors", 50000000000),
            ("000066", "中国长城", "stock", "Technology", "Computer Hardware", 20000000000),
        ]
        
        cursor.executemany("""
            INSERT INTO entities (id, name, type, sector, industry, market_cap)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_entities)
        print(f"✅ 插入 {len(sample_entities)} 个示例实体")
    else:
        print(f"✅ 已有 {count} 个实体，跳过插入")
    
    # 提交更改
    conn.commit()
    
    # 验证表结构
    print("\n📊 验证表结构:")
    for table in ['entities', 'relations', 'decisions', 'signals']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   ✅ {table}: {count} 条记录")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 知识图谱数据库修复完成!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    fix_knowledge_graph_db()
