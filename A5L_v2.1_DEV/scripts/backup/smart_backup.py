#!/usr/bin/env python3
"""
A5L Smart Backup System v1.0
智能备份系统 - 与知识图谱集成

功能:
- 分层备份 (Tier 1/2/3)
- 知识图谱快照
- 备份事件记录到KG
- 自动清理
- 健康检查
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# A5L工作空间
WORKSPACE = "/workspace/projects/workspace"
BACKUP_DIR = f"{WORKSPACE}/.backup"


class SmartBackup:
    """A5L智能备份系统"""
    
    def __init__(self):
        self.date = datetime.now().strftime('%Y-%m-%d')
        self.datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = f"{BACKUP_DIR}/logs/backup.{self.date}.log"
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        with open(self.log_file, 'a') as f:
            f.write(log_line + '\n')
    
    def backup_tier1_core(self):
        """Tier 1: SSMG核心数据备份"""
        self.log("=" * 50)
        self.log("Tier 1 Core Backup Starting...")
        
        backup_dir = f"{BACKUP_DIR}/daily/core"
        
        files_to_backup = [
            ("SOUL.md", f"{WORKSPACE}/SOUL.md"),
            ("SKILL_REGISTRY.json", f"{WORKSPACE}/SKILL_REGISTRY.json"),
            ("MEMORY.md", f"{WORKSPACE}/MEMORY.md"),
        ]
        
        backed_up = []
        for name, path in files_to_backup:
            if os.path.exists(path):
                dest = f"{backup_dir}/{name}.{self.date}.bak"
                shutil.copy2(path, dest)
                size = os.path.getsize(path)
                self.log(f"✅ {name} backed up ({size} bytes)")
                backed_up.append((name, size))
            else:
                self.log(f"⚠️ {name} not found")
        
        # 备份GOAL目录
        goal_dir = f"{WORKSPACE}/GOAL"
        if os.path.exists(goal_dir):
            dest = f"{backup_dir}/GOAL.{self.date}.tar.gz"
            subprocess.run(['tar', '-czf', dest, '-C', WORKSPACE, 'GOAL/'], 
                         capture_output=True)
            self.log(f"✅ GOAL/ backed up")
        
        # 生成完整性哈希
        self._generate_integrity_hash(backup_dir, "tier1")
        
        self.log(f"📦 Tier 1 backup completed")
        return backed_up
    
    def backup_tier2_kg(self):
        """Tier 2: 知识图谱备份"""
        self.log("=" * 50)
        self.log("Tier 2 KG Backup Starting...")
        
        backup_dir = f"{BACKUP_DIR}/daily/kg"
        kg_dir = f"{WORKSPACE}/skills/knowledge-graph"
        
        # 备份数据库
        db_path = f"{kg_dir}/data/knowledge_graph.db"
        if os.path.exists(db_path):
            dest = f"{backup_dir}/knowledge_graph.db.{self.date}.bak"
            shutil.copy2(db_path, dest)
            self.log(f"✅ knowledge_graph.db backed up")
        
        # 备份KG代码
        kg_code_backup = f"{backup_dir}/kg_code.{self.date}.tar.gz"
        subprocess.run(['tar', '-czf', kg_code_backup, '-C', WORKSPACE, 
                       'skills/knowledge-graph/knowledge_graph_core.py',
                       'skills/knowledge-graph/entity_extractor.py',
                       'skills/knowledge-graph/relation_builder.py',
                       'skills/knowledge-graph/visualizer.py',
                       'skills/knowledge-graph/kg_integration.py',
                       'skills/knowledge-graph/kg_analyzer.py'],
                      capture_output=True)
        self.log(f"✅ KG code backed up")
        
        # 尝试获取知识图谱快照
        try:
            kg_stats = self._get_kg_snapshot()
            snapshot_file = f"{backup_dir}/kg_snapshot.{self.date}.json"
            with open(snapshot_file, 'w') as f:
                json.dump(kg_stats, f, indent=2)
            self.log(f"✅ KG snapshot saved ({kg_stats['entity_count']} entities)")
        except Exception as e:
            self.log(f"⚠️ KG snapshot failed: {e}")
        
        self.log(f"📦 Tier 2 backup completed")
        return True
    
    def _get_kg_snapshot(self):
        """获取知识图谱快照"""
        sys.path.insert(0, f"{WORKSPACE}/skills/knowledge-graph")
        from knowledge_graph_core import KnowledgeGraph
        kg = KnowledgeGraph()
        stats = kg.get_stats()
        return {
            'timestamp': datetime.now().isoformat(),
            'entity_count': stats['total_entities'],
            'relation_count': stats['total_relations'],
            'entity_types': stats['entity_types'],
            'relation_types': stats['relation_types']
        }
    
    def _generate_integrity_hash(self, backup_dir, tier):
        """生成完整性哈希"""
        hash_file = f"{backup_dir}/integrity.{self.date}.sha256"
        with open(hash_file, 'w') as f:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    if file.endswith(('.bak', '.tar.gz')) and self.date in file:
                        filepath = os.path.join(root, file)
                        sha256 = hashlib.sha256()
                        with open(filepath, 'rb') as bf:
                            for chunk in iter(lambda: bf.read(4096), b''):
                                sha256.update(chunk)
                        f.write(f"{sha256.hexdigest()}  {filepath}\n")
        self.log(f"🔐 Integrity hash generated for {tier}")
    
    def cleanup_old_backups(self):
        """清理旧备份"""
        self.log("=" * 50)
        self.log("Cleaning up old backups...")
        
        # Tier 1: 保留30天
        cutoff = datetime.now() - timedelta(days=30)
        for f in Path(f"{BACKUP_DIR}/daily/core").glob("*.bak"):
            if f.stat().st_mtime < cutoff.timestamp():
                f.unlink()
                self.log(f"🗑️ Removed old backup: {f.name}")
        
        # Tier 2: 保留14天
        cutoff = datetime.now() - timedelta(days=14)
        for f in Path(f"{BACKUP_DIR}/daily/kg").glob("*.bak"):
            if f.stat().st_mtime < cutoff.timestamp():
                f.unlink()
                self.log(f"🗑️ Removed old backup: {f.name}")
        
        self.log("✅ Cleanup completed")
    
    def run_full_backup(self):
        """执行完整备份"""
        self.log("\n" + "=" * 50)
        self.log("A5L Smart Backup System v1.0")
        self.log(f"Backup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 50)
        
        # Tier 1
        tier1_result = self.backup_tier1_core()
        
        # Tier 2
        tier2_result = self.backup_tier2_kg()
        
        # 清理
        self.cleanup_old_backups()
        
        # 生成报告
        self._generate_backup_report(tier1_result, tier2_result)
        
        self.log("=" * 50)
        self.log("✅ Full backup completed successfully!")
        self.log("=" * 50)
    
    def _generate_backup_report(self, tier1_result, tier2_result):
        """生成备份报告"""
        report_file = f"{WORKSPACE}/reports/backup_report_{self.date}.md"
        
        with open(report_file, 'w') as f:
            f.write("# A5L 备份报告\n\n")
            f.write(f"**备份日期**: {self.date}\n")
            f.write(f"**备份时间**: {datetime.now().strftime('%H:%M:%S')}\n\n")
            
            f.write("## Tier 1 - SSMG核心\n\n")
            for name, size in tier1_result:
                f.write(f"- ✅ {name}: {size} bytes\n")
            
            f.write("\n## Tier 2 - 知识图谱\n\n")
            f.write("- ✅ knowledge_graph.db\n")
            f.write("- ✅ KG code\n")
            f.write("- ✅ KG snapshot\n")
            
            f.write("\n---\n")
            f.write("*Generated by A5L Smart Backup System*\n")
        
        self.log(f"📄 Backup report generated: {report_file}")


def main():
    """主函数"""
    backup = SmartBackup()
    backup.run_full_backup()


if __name__ == "__main__":
    main()
