#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Archive Scheduler
每日归档定时任务

每日23:30自动执行：
1. 创建当日SSMG归档
2. 生成飞书导出文件
3. 记录归档日志
"""

import sys
sys.path.insert(0, '/workspace/projects/workspace/TOOLS')

from ssmg_archive_system import SSMGArchiveSystem
from datetime import datetime
import json
import os

def daily_archive_job():
    """每日归档任务"""
    print("=" * 70)
    print(f"📅 Daily Archive Job - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # 创建归档
        archiver = SSMGArchiveSystem()
        
        # 1. 创建本地归档
        archive_dir = archiver.create_daily_archive()
        
        # 2. 生成飞书导出
        export_files = archiver.generate_feishu_export()
        
        # 3. 记录日志
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "archive_dir": archive_dir,
            "export_files": list(export_files.values()),
            "status": "success"
        }
        
        log_file = "/workspace/projects/workspace/archive/archive_log.json"
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        # 只保留最近30天日志
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs[-30:], f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 70)
        print("✅ 每日归档任务完成")
        print("=" * 70)
        print("\n📋 归档摘要:")
        print(f"   本地归档: {archive_dir}")
        print(f"   飞书导出: {len(export_files)} 个文件")
        print(f"\n💡 提示:")
        print(f"   飞书导出文件位于: feishu_export/")
        print(f"   可直接复制粘贴到飞书文档")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 归档任务失败: {e}")
        return False

if __name__ == "__main__":
    success = daily_archive_job()
    sys.exit(0 if success else 1)
