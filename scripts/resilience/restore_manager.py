#!/usr/bin/env python3
"""
A5L 一键恢复系统
Goal G012 Step 2

功能:
- 恢复到指定时间点
- 选择性恢复
- 恢复前自动备份
- 恢复验证

执行时间: 2026-05-04 00:12 (冲刺模式)
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

WORKSPACE = "/workspace/projects/workspace"
BACKUP_DIR = f"{WORKSPACE}/.backup"
RESTORE_LOG = f"{WORKSPACE}/logs/restore.log"

class RestoreManager:
    """恢复管理器"""
    
    def __init__(self):
        self.log("="*60)
        self.log("A5L 一键恢复系统初始化")
        self.log("="*60)
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(RESTORE_LOG), exist_ok=True)
        with open(RESTORE_LOG, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def list_backup_points(self):
        """列出所有备份点"""
        self.log("📋 列出可用备份点...")
        
        points = []
        
        # 扫描备份目录
        if os.path.exists(f"{BACKUP_DIR}/daily/core"):
            for filename in os.listdir(f"{BACKUP_DIR}/daily/core"):
                if filename.endswith('.bak'):
                    # 提取日期
                    date_str = filename.split('.')[-2] if '.' in filename else 'unknown'
                    points.append({
                        'date': date_str,
                        'filename': filename,
                        'path': f"{BACKUP_DIR}/daily/core/{filename}"
                    })
        
        # 去重并按日期排序
        seen_dates = set()
        unique_points = []
        for p in sorted(points, key=lambda x: x['date'], reverse=True):
            if p['date'] not in seen_dates:
                seen_dates.add(p['date'])
                unique_points.append(p)
        
        self.log(f"  找到 {len(unique_points)} 个备份点")
        return unique_points
    
    def pre_restore_backup(self, restore_point):
        """恢复前自动备份当前状态"""
        self.log("💾 恢复前自动备份当前状态...")
        
        pre_restore_dir = f"{BACKUP_DIR}/pre_restore/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(pre_restore_dir, exist_ok=True)
        
        # 备份关键文件
        critical_files = ['SOUL.md', 'MEMORY.md', 'SKILL_REGISTRY.json']
        for filename in critical_files:
            src = f"{WORKSPACE}/{filename}"
            if os.path.exists(src):
                shutil.copy2(src, pre_restore_dir)
        
        self.log(f"  ✅ 当前状态已备份到: {pre_restore_dir}")
        return pre_restore_dir
    
    def restore_from_point(self, backup_date, components=None):
        """
        从备份点恢复
        
        Args:
            backup_date: 备份日期 (YYYY-MM-DD)
            components: 要恢复的组件 ['core', 'kg', 'all']
        """
        self.log(f"🔄 开始恢复到: {backup_date}")
        
        if components is None:
            components = ['core']
        
        # 步骤1: 恢复前备份
        pre_backup = self.pre_restore_backup(backup_date)
        
        restored = []
        failed = []
        
        # 步骤2: 恢复核心文件
        if 'core' in components or 'all' in components:
            self.log("  恢复核心文件...")
            core_files = ['SOUL.md', 'MEMORY.md', 'SKILL_REGISTRY.json']
            
            for filename in core_files:
                backup_file = f"{BACKUP_DIR}/daily/core/{filename}.{backup_date}.bak"
                target_file = f"{WORKSPACE}/{filename}"
                
                if os.path.exists(backup_file):
                    try:
                        shutil.copy2(backup_file, target_file)
                        restored.append(filename)
                        self.log(f"    ✅ {filename}")
                    except Exception as e:
                        failed.append((filename, str(e)))
                        self.log(f"    ❌ {filename}: {e}")
                else:
                    failed.append((filename, "备份文件不存在"))
                    self.log(f"    ⚠️ {filename}: 备份不存在")
        
        # 步骤3: 恢复KG
        if 'kg' in components or 'all' in components:
            self.log("  恢复知识图谱...")
            kg_backup = f"{BACKUP_DIR}/daily/kg/knowledge_graph.db.{backup_date}.bak"
            kg_target = f"{WORKSPACE}/skills/knowledge-graph/knowledge_graph.db"
            
            if os.path.exists(kg_backup):
                try:
                    shutil.copy2(kg_backup, kg_target)
                    restored.append('knowledge_graph')
                    self.log(f"    ✅ knowledge_graph.db")
                except Exception as e:
                    failed.append(('knowledge_graph', str(e)))
                    self.log(f"    ❌ knowledge_graph.db: {e}")
            else:
                self.log(f"    ⚠️ knowledge_graph.db: 备份不存在")
        
        # 步骤4: 验证恢复
        self.log("  验证恢复结果...")
        verification = self.verify_restore(restored)
        
        # 生成恢复报告
        report = {
            'restore_point': backup_date,
            'restore_time': datetime.now().isoformat(),
            'components': components,
            'pre_restore_backup': pre_backup,
            'restored_files': restored,
            'failed_files': failed,
            'verification': verification,
            'status': 'success' if not failed else 'partial'
        }
        
        # 保存报告
        report_file = f"{BACKUP_DIR}/restore_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"\n✅ 恢复完成")
        self.log(f"  成功: {len(restored)} 个文件")
        self.log(f"  失败: {len(failed)} 个文件")
        self.log(f"  报告: {report_file}")
        
        return report
    
    def verify_restore(self, restored_files):
        """验证恢复结果"""
        verification = {}
        
        for filename in restored_files:
            filepath = f"{WORKSPACE}/{filename}"
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                verification[filename] = {
                    'exists': True,
                    'size': size
                }
            else:
                verification[filename] = {
                    'exists': False
                }
        
        return verification
    
    def interactive_restore(self):
        """交互式恢复"""
        print("\n" + "="*60)
        print("A5L 一键恢复系统")
        print("="*60)
        
        # 列出备份点
        points = self.list_backup_points()
        
        if not points:
            print("❌ 无可用备份点")
            return None
        
        print("\n可用备份点:")
        for i, p in enumerate(points[:10], 1):
            print(f"  {i}. {p['date']}")
        
        print("\n💡 使用命令行参数直接恢复:")
        print(f"  python3 scripts/resilience/restore_manager.py --date YYYY-MM-DD")
        
        return points


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='A5L 一键恢复系统')
    parser.add_argument('--date', help='备份日期 (YYYY-MM-DD)')
    parser.add_argument('--components', nargs='+', default=['core'], 
                       choices=['core', 'kg', 'all'], help='要恢复的组件')
    parser.add_argument('--list', action='store_true', help='列出备份点')
    
    args = parser.parse_args()
    
    manager = RestoreManager()
    
    if args.list or not args.date:
        manager.interactive_restore()
    else:
        print("="*60)
        print("A5L 一键恢复系统")
        print("="*60)
        report = manager.restore_from_point(args.date, args.components)
        print("="*60)
        print(f"✅ 恢复状态: {report['status']}")
        print("="*60)


if __name__ == "__main__":
    main()
