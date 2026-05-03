#!/usr/bin/env python3
"""
A5L 版本回滚系统
Goal G012 Step 3

功能:
- SOUL/MEMORY/KG版本回滚
- Git集成回滚
- 交易记录防篡改

执行时间: 2026-05-04 01:05 (自动模式)
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime

WORKSPACE = "/workspace/projects/workspace"
LOG_FILE = f"{WORKSPACE}/logs/version_rollback.log"

class VersionRollback:
    """版本回滚管理器"""
    
    def __init__(self):
        self.log("="*60)
        self.log("A5L 版本回滚系统初始化")
        self.log("="*60)
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def list_git_commits(self, max_count=10):
        """列出最近的Git提交"""
        try:
            result = subprocess.run(
                f"cd {WORKSPACE} && git log --oneline -{max_count}",
                shell=True,
                capture_output=True,
                text=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    commit_hash = line.split()[0]
                    message = ' '.join(line.split()[1:])
                    commits.append({
                        'hash': commit_hash,
                        'message': message
                    })
            
            return commits
        except Exception as e:
            self.log(f"❌ 获取Git提交失败: {e}")
            return []
    
    def rollback_soul(self, target_version=None):
        """回滚SOUL.md到指定版本"""
        self.log("🔄 回滚SOUL.md...")
        
        if target_version:
            try:
                # 从Git恢复特定版本
                subprocess.run(
                    f"cd {WORKSPACE} && git checkout {target_version} -- SOUL.md",
                    shell=True,
                    check=True
                )
                self.log(f"  ✅ SOUL.md已回滚到 {target_version[:8]}")
                return True
            except Exception as e:
                self.log(f"  ❌ 回滚失败: {e}")
                return False
        else:
            self.log("  ℹ️ 未指定版本，使用最新备份")
            return False
    
    def rollback_memory(self, backup_date=None):
        """回滚MEMORY.md"""
        self.log("🔄 回滚MEMORY.md...")
        
        if not backup_date:
            # 使用最近的备份
            backup_dir = f"{WORKSPACE}/.backup/daily/core"
            if os.path.exists(backup_dir):
                backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('MEMORY.md')])
                if backups:
                    backup_file = f"{backup_dir}/{backups[-1]}"
                    shutil.copy2(backup_file, f"{WORKSPACE}/MEMORY.md")
                    self.log(f"  ✅ MEMORY.md已恢复: {backups[-1]}")
                    return True
        
        self.log("  ⚠️ 无可用备份")
        return False
    
    def rollback_kg(self, backup_date=None):
        """回滚知识图谱"""
        self.log("🔄 回滚知识图谱...")
        
        kg_backup_dir = f"{WORKSPACE}/.backup/daily/kg"
        kg_target = f"{WORKSPACE}/skills/knowledge-graph/knowledge_graph.db"
        
        if not backup_date:
            # 使用最近的备份
            if os.path.exists(kg_backup_dir):
                backups = sorted([f for f in os.listdir(kg_backup_dir) if f.endswith('.bak')])
                if backups:
                    backup_file = f"{kg_backup_dir}/{backups[-1]}"
                    shutil.copy2(backup_file, kg_target)
                    self.log(f"  ✅ KG已恢复: {backups[-1]}")
                    return True
        
        self.log("  ⚠️ 无可用KG备份")
        return False
    
    def protect_trading_records(self):
        """交易记录防篡改保护"""
        self.log("🔒 检查交易记录保护...")
        
        # 交易记录文件
        trading_file = f"{WORKSPACE}/data/trading_records.json"
        
        if os.path.exists(trading_file):
            # 计算哈希
            import hashlib
            with open(trading_file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # 保存哈希记录
            hash_record = f"{WORKSPACE}/data/.trading_hash"
            if os.path.exists(hash_record):
                with open(hash_record, 'r') as f:
                    old_hash = f.read().strip()
                
                if old_hash != file_hash:
                    self.log("  🚨 警告: 交易记录可能被篡改!")
                    return False
            
            with open(hash_record, 'w') as f:
                f.write(file_hash)
            
            self.log("  ✅ 交易记录完整性验证通过")
            return True
        
        self.log("  ℹ️ 无交易记录文件")
        return True
    
    def interactive_rollback(self):
        """交互式回滚"""
        print("\n" + "="*60)
        print("A5L 版本回滚系统")
        print("="*60)
        
        # 列出最近的Git提交
        commits = self.list_git_commits(5)
        
        print("\n最近的Git提交:")
        for i, commit in enumerate(commits, 1):
            print(f"  {i}. {commit['hash'][:8]} - {commit['message']}")
        
        print("\n可用的回滚操作:")
        print("  1. 回滚SOUL.md到指定Git版本")
        print("  2. 回滚MEMORY.md到最近备份")
        print("  3. 回滚知识图谱到最近备份")
        print("  4. 验证交易记录完整性")
        
        print("\n💡 使用命令行参数直接回滚:")
        print("  python3 scripts/resilience/version_rollback.py --component soul --version abc123")
        
        return commits


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='A5L 版本回滚系统')
    parser.add_argument('--component', choices=['soul', 'memory', 'kg', 'all'], 
                       help='要回滚的组件')
    parser.add_argument('--version', help='目标版本(Git hash或备份日期)')
    parser.add_argument('--list', action='store_true', help='列出可用版本')
    
    args = parser.parse_args()
    
    rollback = VersionRollback()
    
    if args.list or not args.component:
        rollback.interactive_rollback()
    else:
        print("="*60)
        print("A5L 版本回滚")
        print("="*60)
        
        if args.component == 'soul':
            rollback.rollback_soul(args.version)
        elif args.component == 'memory':
            rollback.rollback_memory(args.version)
        elif args.component == 'kg':
            rollback.rollback_kg(args.version)
        elif args.component == 'all':
            rollback.rollback_soul(args.version)
            rollback.rollback_memory(args.version)
            rollback.rollback_kg(args.version)
        
        rollback.protect_trading_records()
        
        print("="*60)
        print("✅ 回滚操作完成")
        print("="*60)


if __name__ == "__main__":
    main()
