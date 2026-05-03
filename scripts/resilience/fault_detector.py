#!/usr/bin/env python3
"""
A5L 故障自动检测系统
Goal G012 Step 1

功能:
- 文件完整性监控
- 数据库一致性校验
- 飞书同步状态监控
- 异常告警

执行时间: 2026-05-04 00:11 (冲刺模式)
"""

import os
import sys
import json
import hashlib
import sqlite3
from datetime import datetime

WORKSPACE = "/workspace/projects/workspace"
LOG_FILE = f"{WORKSPACE}/logs/fault_detection.log"
ALERT_FILE = f"{WORKSPACE}/data/alerts.json"

# 关键文件列表
CRITICAL_FILES = [
    "SOUL.md",
    "MEMORY.md",
    "SKILL_REGISTRY.json",
    "GOAL/goals.json",
    "skills/knowledge-graph/knowledge_graph.db"
]

class FaultDetector:
    """故障检测器"""
    
    def __init__(self):
        self.log("="*60)
        self.log("A5L 故障检测系统初始化")
        self.log("="*60)
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def calculate_file_hash(self, filepath):
        """计算文件SHA256哈希"""
        if not os.path.exists(filepath):
            return None
        
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def check_file_integrity(self):
        """检查文件完整性"""
        self.log("🔍 检查文件完整性...")
        
        issues = []
        
        for rel_path in CRITICAL_FILES:
            full_path = os.path.join(WORKSPACE, rel_path)
            
            if not os.path.exists(full_path):
                issues.append({
                    'type': 'file_missing',
                    'file': rel_path,
                    'severity': 'critical'
                })
                self.log(f"  ❌ 文件缺失: {rel_path}")
            else:
                file_hash = self.calculate_file_hash(full_path)
                self.log(f"  ✅ {rel_path}: {file_hash[:16]}...")
        
        return issues
    
    def check_database_consistency(self):
        """检查数据库一致性"""
        self.log("🔍 检查数据库一致性...")
        
        issues = []
        kg_db = f"{WORKSPACE}/skills/knowledge-graph/knowledge_graph.db"
        msg_db = f"{WORKSPACE}/data/message_bus.db"
        
        # 检查KG数据库
        if os.path.exists(kg_db):
            try:
                conn = sqlite3.connect(kg_db)
                cursor = conn.cursor()
                
                # 检查表是否存在
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in cursor.fetchall()]
                
                if 'entities' not in tables:
                    issues.append({
                        'type': 'db_table_missing',
                        'db': 'knowledge_graph',
                        'table': 'entities',
                        'severity': 'warning'
                    })
                    self.log(f"  ⚠️ KG数据库缺少entities表")
                else:
                    self.log(f"  ✅ KG数据库表正常")
                
                conn.close()
            except Exception as e:
                issues.append({
                    'type': 'db_error',
                    'db': 'knowledge_graph',
                    'error': str(e),
                    'severity': 'critical'
                })
                self.log(f"  ❌ KG数据库错误: {e}")
        else:
            issues.append({
                'type': 'db_missing',
                'db': 'knowledge_graph',
                'severity': 'warning'
            })
            self.log(f"  ⚠️ KG数据库不存在")
        
        return issues
    
    def check_backup_status(self):
        """检查备份状态"""
        self.log("🔍 检查备份状态...")
        
        issues = []
        backup_dir = f"{WORKSPACE}/.backup/daily"
        
        if not os.path.exists(backup_dir):
            issues.append({
                'type': 'backup_dir_missing',
                'severity': 'warning'
            })
            self.log(f"  ⚠️ 备份目录不存在")
            return issues
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查今日备份
        core_backup = f"{backup_dir}/core/SOUL.md.{today}.bak"
        if os.path.exists(core_backup):
            self.log(f"  ✅ 今日核心备份存在")
        else:
            issues.append({
                'type': 'backup_missing',
                'backup_type': 'core',
                'date': today,
                'severity': 'warning'
            })
            self.log(f"  ⚠️ 今日核心备份缺失")
        
        return issues
    
    def send_alert(self, issues):
        """发送告警"""
        if not issues:
            return
        
        self.log(f"🚨 检测到 {len(issues)} 个问题")
        
        # 保存告警记录
        alerts = []
        if os.path.exists(ALERT_FILE):
            with open(ALERT_FILE, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
        
        for issue in issues:
            alert = {
                'id': f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(issue))}",
                'timestamp': datetime.now().isoformat(),
                'issue': issue,
                'acknowledged': False
            }
            alerts.append(alert)
        
        os.makedirs(os.path.dirname(ALERT_FILE), exist_ok=True)
        with open(ALERT_FILE, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, ensure_ascii=False, indent=2)
        
        # TODO: 发送飞书告警
        critical_count = sum(1 for i in issues if i.get('severity') == 'critical')
        if critical_count > 0:
            self.log(f"  🚨 {critical_count} 个严重问题需要立即处理!")
    
    def run_all_checks(self):
        """运行所有检查"""
        self.log("\n" + "="*60)
        self.log("开始全面故障检测")
        self.log("="*60)
        
        all_issues = []
        
        # 检查文件完整性
        file_issues = self.check_file_integrity()
        all_issues.extend(file_issues)
        
        # 检查数据库一致性
        db_issues = self.check_database_consistency()
        all_issues.extend(db_issues)
        
        # 检查备份状态
        backup_issues = self.check_backup_status()
        all_issues.extend(backup_issues)
        
        # 发送告警
        self.send_alert(all_issues)
        
        # 总结
        self.log("\n" + "="*60)
        self.log("故障检测完成")
        self.log(f"  发现问题: {len(all_issues)} 个")
        self.log(f"  严重: {sum(1 for i in all_issues if i.get('severity') == 'critical')}")
        self.log(f"  警告: {sum(1 for i in all_issues if i.get('severity') == 'warning')}")
        self.log("="*60)
        
        return all_issues


def main():
    """主函数"""
    print("="*60)
    print("A5L 故障自动检测系统")
    print("G012 Step 1 - 冲刺模式")
    print("="*60)
    
    detector = FaultDetector()
    issues = detector.run_all_checks()
    
    print("="*60)
    if issues:
        print(f"⚠️ 检测到 {len(issues)} 个问题，请查看日志")
    else:
        print("✅ 所有检查通过，系统健康")
    print("="*60)


if __name__ == "__main__":
    main()
