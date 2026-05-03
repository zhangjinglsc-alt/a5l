#!/usr/bin/env python3
"""
A5L 任务调度器 (Layer 0协调中心)
Goal G011 Step 1

功能:
- 统一管理所有定时任务
- 任务依赖DAG管理
- 失败重试机制
- 状态跟踪

执行时间: 2026-05-04 00:05 (后台模式)
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# A5L工作空间
WORKSPACE = "/workspace/projects/workspace"
STATE_FILE = f"{WORKSPACE}/data/orchestrator/task_state.json"
DAG_FILE = f"{WORKSPACE}/config/task_dag.json"
LOG_FILE = f"{WORKSPACE}/logs/task_scheduler.log"

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.ensure_directories()
        self.log("="*60)
        self.log("A5L 任务调度器初始化")
        self.log("="*60)
        self.dag = self.load_dag()
        self.state = self.load_state()
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def ensure_directories(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(DAG_FILE), exist_ok=True)
    
    def load_dag(self):
        """加载任务依赖图"""
        if os.path.exists(DAG_FILE):
            with open(DAG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认DAG配置
        default_dag = {
            "tasks": {
                "ssmg_archive": {
                    "command": "scripts/archive/ssmg_daily_archive.sh",
                    "schedule": "30 23 * * *",
                    "dependencies": [],
                    "timeout": 300,
                    "retries": 3
                },
                "tier1_backup": {
                    "command": "scripts/backup/tier1_core_backup.sh",
                    "schedule": "30 23 * * *",
                    "dependencies": [],
                    "timeout": 180,
                    "retries": 3
                },
                "tier2_backup": {
                    "command": "scripts/backup/tier2_kg_backup.sh",
                    "schedule": "45 23 * * *",
                    "dependencies": ["tier1_backup"],
                    "timeout": 300,
                    "retries": 3
                },
                "health_check": {
                    "command": "scripts/backup/health_check.py",
                    "schedule": "55 23 * * *",
                    "dependencies": ["tier2_backup"],
                    "timeout": 60,
                    "retries": 2
                },
                "feishu_sync": {
                    "command": "scripts/feishu/sync_to_feishu.sh",
                    "schedule": "35 23 * * *",
                    "dependencies": ["ssmg_archive"],
                    "timeout": 600,
                    "retries": 2
                },
                "report_processing": {
                    "command": "scripts/kg/g010_full_pipeline.sh",
                    "schedule": "0 */4 * * *",
                    "dependencies": [],
                    "timeout": 1800,
                    "retries": 1
                }
            }
        }
        
        with open(DAG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_dag, f, ensure_ascii=False, indent=2)
        
        self.log(f"✅ 已创建默认DAG配置")
        return default_dag
    
    def load_state(self):
        """加载任务状态"""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_state(self):
        """保存任务状态"""
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        return self.state.get(task_id, {
            'status': 'pending',
            'last_run': None,
            'last_success': None,
            'retry_count': 0,
            'error': None
        })
    
    def check_dependencies(self, task_id):
        """检查依赖是否满足"""
        task = self.dag['tasks'].get(task_id, {})
        deps = task.get('dependencies', [])
        
        for dep_id in deps:
            dep_status = self.get_task_status(dep_id)
            if dep_status['status'] != 'completed':
                return False, f"依赖任务 {dep_id} 未完成 (当前: {dep_status['status']})"
        
        return True, "所有依赖满足"
    
    def execute_task(self, task_id):
        """执行任务"""
        task = self.dag['tasks'].get(task_id)
        if not task:
            self.log(f"❌ 任务不存在: {task_id}")
            return False
        
        # 检查依赖
        deps_ok, deps_msg = self.check_dependencies(task_id)
        if not deps_ok:
            self.log(f"⏳ 任务 {task_id} 等待依赖: {deps_msg}")
            return False
        
        # 更新状态为运行中
        self.state[task_id] = {
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'retry_count': self.get_task_status(task_id).get('retry_count', 0)
        }
        self.save_state()
        
        self.log(f"🚀 执行任务: {task_id}")
        
        try:
            # 执行命令
            command = task['command']
            timeout = task.get('timeout', 300)
            
            full_command = f"cd {WORKSPACE} && bash {command}"
            
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                # 成功
                self.state[task_id] = {
                    'status': 'completed',
                    'started_at': self.state[task_id]['started_at'],
                    'completed_at': datetime.now().isoformat(),
                    'retry_count': 0,
                    'error': None
                }
                self.log(f"✅ 任务完成: {task_id}")
                success = True
            else:
                # 失败
                raise Exception(f"返回码: {result.returncode}, 错误: {result.stderr}")
                
        except Exception as e:
            # 失败，更新重试计数
            retry_count = self.get_task_status(task_id).get('retry_count', 0) + 1
            max_retries = task.get('retries', 3)
            
            self.state[task_id] = {
                'status': 'failed' if retry_count >= max_retries else 'pending',
                'started_at': self.state[task_id].get('started_at'),
                'failed_at': datetime.now().isoformat(),
                'retry_count': retry_count,
                'error': str(e)
            }
            
            self.log(f"❌ 任务失败: {task_id} (重试 {retry_count}/{max_retries}): {e}")
            success = False
        
        self.save_state()
        return success
    
    def run_all_ready_tasks(self):
        """运行所有就绪的任务"""
        self.log("\n" + "="*60)
        self.log("检查并执行就绪任务")
        self.log("="*60)
        
        completed = []
        failed = []
        
        for task_id in self.dag['tasks']:
            status = self.get_task_status(task_id)
            
            if status['status'] == 'pending':
                deps_ok, _ = self.check_dependencies(task_id)
                if deps_ok:
                    if self.execute_task(task_id):
                        completed.append(task_id)
                    else:
                        failed.append(task_id)
        
        self.log("\n" + "="*60)
        self.log(f"任务执行完成: {len(completed)} 成功, {len(failed)} 失败")
        self.log("="*60)
        
        return completed, failed
    
    def get_scheduler_summary(self):
        """获取调度器摘要"""
        total = len(self.dag['tasks'])
        completed = sum(1 for t in self.state.values() if t.get('status') == 'completed')
        running = sum(1 for t in self.state.values() if t.get('status') == 'running')
        failed = sum(1 for t in self.state.values() if t.get('status') == 'failed')
        pending = total - completed - running - failed
        
        return {
            'total_tasks': total,
            'completed': completed,
            'running': running,
            'failed': failed,
            'pending': pending,
            'health_score': round((completed / total * 100) if total > 0 else 0, 1)
        }


def main():
    """主函数"""
    print("="*60)
    print("A5L 任务调度器")
    print("G011 Step 1 - 后台模式")
    print("="*60)
    
    scheduler = TaskScheduler()
    
    # 显示摘要
    summary = scheduler.get_scheduler_summary()
    print(f"\n📊 调度器状态:")
    print(f"  总任务: {summary['total_tasks']}")
    print(f"  已完成: {summary['completed']}")
    print(f"  运行中: {summary['running']}")
    print(f"  失败: {summary['failed']}")
    print(f"  待执行: {summary['pending']}")
    print(f"  健康度: {summary['health_score']}%")
    
    # 执行就绪任务
    completed, failed = scheduler.run_all_ready_tasks()
    
    print("="*60)
    print(f"✅ 调度完成")
    print("="*60)


if __name__ == "__main__":
    main()
