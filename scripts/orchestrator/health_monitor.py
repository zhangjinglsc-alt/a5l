#!/usr/bin/env python3
"""
A5L 健康检查系统
Goal G011 Step 2

功能:
- 各子系统健康度检测
- 异常告警
- 健康评分

执行时间: 2026-05-04 00:07 (后台模式)
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

WORKSPACE = "/workspace/projects/workspace"
LOG_FILE = f"{WORKSPACE}/logs/health_check.log"
METRICS_FILE = f"{WORKSPACE}/data/health_metrics.json"

class HealthMonitor:
    """健康监控器"""
    
    def __init__(self):
        self.log("="*60)
        self.log("A5L 健康检查系统")
        self.log("="*60)
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def check_kg_health(self):
        """检查KG系统健康"""
        self.log("🔍 检查KG系统...")
        
        kg_db = f"{WORKSPACE}/skills/knowledge-graph/knowledge_graph.db"
        
        try:
            conn = sqlite3.connect(kg_db)
            cursor = conn.cursor()
            
            # 检查实体数量
            cursor.execute("SELECT COUNT(*) FROM entities")
            entity_count = cursor.fetchone()[0]
            
            # 检查关系数量
            cursor.execute("SELECT COUNT(*) FROM relations")
            relation_count = cursor.fetchone()[0]
            
            conn.close()
            
            # 健康度评分
            score = min(100, entity_count * 1.5)  # 每1个实体1.5分，最高100
            
            status = 'healthy' if score >= 70 else 'warning' if score >= 50 else 'critical'
            
            self.log(f"  实体数: {entity_count}, 关系数: {relation_count}, 健康度: {score:.1f}%")
            
            return {
                'component': 'knowledge_graph',
                'status': status,
                'score': round(score, 1),
                'metrics': {
                    'entity_count': entity_count,
                    'relation_count': relation_count
                }
            }
            
        except Exception as e:
            self.log(f"  ⚠️ KG检查失败: {e}")
            return {
                'component': 'knowledge_graph',
                'status': 'critical',
                'score': 0,
                'error': str(e)
            }
    
    def check_backup_health(self):
        """检查备份系统健康"""
        self.log("🔍 检查备份系统...")
        
        backup_dir = f"{WORKSPACE}/.backup/daily"
        
        try:
            # 检查最近的备份
            core_backup = os.path.exists(f"{backup_dir}/core")
            kg_backup = os.path.exists(f"{backup_dir}/kg")
            
            # 检查备份文件日期
            today = datetime.now().strftime('%Y-%m-%d')
            today_backup = False
            
            if core_backup:
                files = os.listdir(f"{backup_dir}/core")
                today_backup = any(today in f for f in files)
            
            score = 100 if today_backup else 50 if core_backup else 0
            status = 'healthy' if score >= 80 else 'warning' if score >= 50 else 'critical'
            
            self.log(f"  今日备份: {'✅' if today_backup else '❌'}, 健康度: {score}%")
            
            return {
                'component': 'backup',
                'status': status,
                'score': score,
                'metrics': {
                    'today_backup': today_backup,
                    'core_backup_exists': core_backup,
                    'kg_backup_exists': kg_backup
                }
            }
            
        except Exception as e:
            self.log(f"  ⚠️ 备份检查失败: {e}")
            return {
                'component': 'backup',
                'status': 'critical',
                'score': 0,
                'error': str(e)
            }
    
    def check_signal_health(self):
        """检查信号系统健康"""
        self.log("🔍 检查信号系统...")
        
        signals_dir = f"{WORKSPACE}/data/investment_signals"
        
        try:
            # 检查信号文件
            signal_files = []
            if os.path.exists(signals_dir):
                signal_files = [f for f in os.listdir(signals_dir) if f.endswith('.json')]
            
            signal_count = len(signal_files)
            score = min(100, signal_count * 20 + 50)  # 基础50分，每个信号+20
            
            status = 'healthy' if score >= 70 else 'warning'
            
            self.log(f"  信号文件: {signal_count}, 健康度: {score}%")
            
            return {
                'component': 'signal_system',
                'status': status,
                'score': score,
                'metrics': {
                    'signal_count': signal_count
                }
            }
            
        except Exception as e:
            self.log(f"  ⚠️ 信号检查失败: {e}")
            return {
                'component': 'signal_system',
                'status': 'warning',
                'score': 50,
                'error': str(e)
            }
    
    def check_git_health(self):
        """检查Git同步健康"""
        self.log("🔍 检查Git同步...")
        
        try:
            import subprocess
            
            # 检查未提交更改
            result = subprocess.run(
                f"cd {WORKSPACE} && git status --porcelain | wc -l",
                shell=True,
                capture_output=True,
                text=True
            )
            
            uncommitted = int(result.stdout.strip())
            
            score = 100 if uncommitted == 0 else max(0, 100 - uncommitted * 10)
            status = 'healthy' if uncommitted == 0 else 'warning'
            
            self.log(f"  未提交: {uncommitted}, 健康度: {score}%")
            
            return {
                'component': 'git_sync',
                'status': status,
                'score': score,
                'metrics': {
                    'uncommitted_files': uncommitted
                }
            }
            
        except Exception as e:
            self.log(f"  ⚠️ Git检查失败: {e}")
            return {
                'component': 'git_sync',
                'status': 'warning',
                'score': 50,
                'error': str(e)
            }
    
    def run_all_checks(self):
        """运行所有检查"""
        self.log("\n" + "="*60)
        self.log("开始全面健康检查")
        self.log("="*60)
        
        checks = [
            self.check_kg_health(),
            self.check_backup_health(),
            self.check_signal_health(),
            self.check_git_health()
        ]
        
        # 计算整体健康度
        avg_score = sum(c['score'] for c in checks) / len(checks)
        
        critical_count = sum(1 for c in checks if c['status'] == 'critical')
        warning_count = sum(1 for c in checks if c['status'] == 'warning')
        
        overall_status = 'healthy' if critical_count == 0 and warning_count == 0 else \
                        'warning' if critical_count == 0 else 'critical'
        
        report = {
            'checked_at': datetime.now().isoformat(),
            'overall_status': overall_status,
            'overall_score': round(avg_score, 1),
            'summary': {
                'healthy': sum(1 for c in checks if c['status'] == 'healthy'),
                'warning': warning_count,
                'critical': critical_count
            },
            'details': checks
        }
        
        # 保存报告
        os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
        with open(METRICS_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log("\n" + "="*60)
        self.log(f"健康检查完成")
        self.log(f"  整体状态: {overall_status}")
        self.log(f"  整体评分: {avg_score:.1f}%")
        self.log(f"  Healthy: {report['summary']['healthy']}")
        self.log(f"  Warning: {report['summary']['warning']}")
        self.log(f"  Critical: {report['summary']['critical']}")
        self.log("="*60)
        
        return report


def main():
    print("="*60)
    print("A5L 健康检查系统")
    print("G011 Step 2 - 后台模式")
    print("="*60)
    
    monitor = HealthMonitor()
    report = monitor.run_all_checks()
    
    print("="*60)
    print(f"✅ 检查完成 - 整体健康度: {report['overall_score']}%")
    print("="*60)


if __name__ == "__main__":
    main()
