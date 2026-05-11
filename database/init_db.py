#!/usr/bin/env python3
"""
A5L Database Initialization Script
数据库初始化脚本

Usage:
    python database/init_db.py
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager, get_db_manager
from database.db_utils import print_dashboard


def init_database():
    """初始化数据库"""
    print("🔧 Initializing A5L Database v2.2...")
    
    db = DatabaseManager()
    
    print("✅ Database structure created")
    print(f"📁 Database file: {db.db_path}")
    
    # 显示统计
    print_dashboard()
    
    print("\n🎉 Database initialization complete!")
    return True


if __name__ == '__main__':
    init_database()
