#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 1: Data Store
数据底座层 - 数据存储

功能：
1. 时序数据高效存储
2. 增量更新支持
3. 数据版本管理
4. 快速查询接口
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sqlite3

class DataStore:
    """数据存储管理器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.data_dir = f"{workspace}/data/architect_5l"
        self.db_path = f"{self.data_dir}/architect_5l.db"
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建价格数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                amount REAL,
                change_pct REAL,
                turnover REAL,
                market TEXT,
                source TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, date)
            )
        ''')
        
        # 创建财务数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_data (
                symbol TEXT NOT NULL,
                report_date TEXT NOT NULL,
                report_type TEXT,
                revenue REAL,
                net_profit REAL,
                eps REAL,
                roe REAL,
                debt_ratio REAL,
                gross_margin REAL,
                source TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, report_date)
            )
        ''')
        
        # 创建公告数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcement_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                announce_date TIMESTAMP NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                type TEXT,
                source TEXT,
                url TEXT,
                sentiment_score REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建资金流数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fund_flow_data (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                main_inflow REAL,
                retail_inflow REAL,
                institutional_inflow REAL,
                net_inflow REAL,
                source TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, date)
            )
        ''')
        
        # 创建情绪数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_data (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                sentiment_score REAL,
                news_count INTEGER,
                positive_count INTEGER,
                negative_count INTEGER,
                heat_score REAL,
                source TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, date)
            )
        ''')
        
        # 创建数据更新日志
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                symbol TEXT,
                date_range TEXT,
                record_count INTEGER,
                source TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_price(self, data: Dict) -> bool:
        """插入价格数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO price_data 
                (symbol, date, open, high, low, close, volume, amount, change_pct, turnover, market, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('symbol'),
                data.get('date'),
                data.get('open'),
                data.get('high'),
                data.get('low'),
                data.get('close'),
                data.get('volume'),
                data.get('amount'),
                data.get('change_pct'),
                data.get('turnover'),
                data.get('market'),
                data.get('source')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting price data: {e}")
            return False
    
    def insert_financial(self, data: Dict) -> bool:
        """插入财务数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO financial_data 
                (symbol, report_date, report_type, revenue, net_profit, eps, roe, debt_ratio, gross_margin, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('symbol'),
                data.get('report_date'),
                data.get('report_type'),
                data.get('revenue'),
                data.get('net_profit'),
                data.get('eps'),
                data.get('roe'),
                data.get('debt_ratio'),
                data.get('gross_margin'),
                data.get('source')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting financial data: {e}")
            return False
    
    def query_price(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """查询价格数据"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM price_data 
            WHERE symbol = ? AND date >= ? AND date <= ?
            ORDER BY date ASC
        ''', (symbol, start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def query_latest_price(self, symbol: str) -> Optional[Dict]:
        """查询最新价格"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM price_data 
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT 1
        ''', (symbol,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def query_financial(self, symbol: str, limit: int = 8) -> List[Dict]:
        """查询财务数据"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM financial_data 
            WHERE symbol = ?
            ORDER BY report_date DESC
            LIMIT ?
        ''', (symbol, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_data_summary(self) -> Dict:
        """获取数据摘要"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        summary = {}
        
        tables = ['price_data', 'financial_data', 'announcement_data', 'fund_flow_data', 'sentiment_data']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(DISTINCT symbol) FROM {table}")
            symbols = cursor.fetchone()[0]
            
            summary[table] = {
                "record_count": count,
                "symbol_count": symbols
            }
        
        conn.close()
        return summary
    
    def get_last_update(self, table_name: str, symbol: str = None) -> Optional[str]:
        """获取最后更新时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute('''
                SELECT MAX(updated_at) FROM update_log 
                WHERE table_name = ? AND symbol = ?
            ''', (table_name, symbol))
        else:
            cursor.execute('''
                SELECT MAX(updated_at) FROM update_log 
                WHERE table_name = ?
            ''', (table_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result and result[0] else None
    
    def log_update(self, table_name: str, record_count: int, symbol: str = None, 
                   date_range: str = None, source: str = None):
        """记录更新日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO update_log (table_name, symbol, date_range, record_count, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (table_name, symbol, date_range, record_count, source))
        
        conn.commit()
        conn.close()
    
    def generate_store_report(self) -> str:
        """生成存储报告"""
        summary = self.get_data_summary()
        
        report = f"""# 📦 数据存储报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**数据库**: {self.db_path}

---

## 📊 数据概览

| 数据表 | 记录数 | 股票数 |
|--------|--------|--------|
"""
        
        for table, stats in summary.items():
            report += f"| {table} | {stats['record_count']:,} | {stats['symbol_count']:,} |\n"
        
        total_records = sum(s['record_count'] for s in summary.values())
        report += f"\n**总计**: {total_records:,} 条记录\n"
        
        report += """
---

## 📁 存储位置

- **SQLite数据库**: `data/architect_5l/architect_5l.db`
- **原始数据**: `data/architect_5l/raw_data/`
- **处理后数据**: `data/architect_5l/processed_data/`
- **信号数据**: `data/architect_5l/signals/`
- **报告数据**: `data/architect_5l/reports/`

---

## 🔄 数据更新

系统支持增量更新，自动记录每次更新的时间和来源。

"""
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("📦 数据存储 (Layer 1)")
    print("=" * 70)
    
    store = DataStore()
    
    # 插入示例数据
    print("\n📝 插入示例数据...")
    
    price_data = {
        "symbol": "000001.SZ",
        "date": "2026-05-02",
        "open": 10.5,
        "high": 10.8,
        "low": 10.3,
        "close": 10.6,
        "volume": 1000000,
        "amount": 10600000.0,
        "change_pct": 0.95,
        "turnover": 2.5,
        "market": "CN",
        "source": "akshare"
    }
    
    success = store.insert_price(price_data)
    print(f"  价格数据: {'✅ 成功' if success else '❌ 失败'}")
    
    financial_data = {
        "symbol": "000001.SZ",
        "report_date": "2026-03-31",
        "report_type": "quarterly",
        "revenue": 1500000000.0,
        "net_profit": 450000000.0,
        "eps": 1.25,
        "roe": 15.5,
        "debt_ratio": 0.35,
        "gross_margin": 0.42,
        "source": "tushare"
    }
    
    success = store.insert_financial(financial_data)
    print(f"  财务数据: {'✅ 成功' if success else '❌ 失败'}")
    
    # 查询数据
    print("\n🔍 查询数据...")
    latest = store.query_latest_price("000001.SZ")
    if latest:
        print(f"  最新价格: {latest['close']} ({latest['date']})")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 存储报告:")
    report = store.generate_store_report()
    print(report)

if __name__ == "__main__":
    main()
