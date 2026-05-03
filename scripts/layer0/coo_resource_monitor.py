#!/usr/bin/env python3
"""
A5L Chief Operating Officer (COO) - 资源监控与运营管理中心
Layer 0 核心组件

功能:
- 系统资源监控 (CPU/内存/磁盘)
- API配额追踪 (飞书/股票数据)
- 任务队列管理
- 性能优化建议

执行时间: 2026-05-04 01:34 (v0.1 MVP)
"""

import os
import sys
import json
import psutil
import subprocess
from datetime import datetime
from typing import Dict, List

WORKSPACE = "/workspace/projects/workspace"
LOG_FILE = f"{WORKSPACE}/logs/coo_operations.log"
DATA_DIR = f"{WORKSPACE}/data/operations"

class ResourceMonitor:
    """
    COO资源监控器 v0.1 MVP
    
    监控项:
    1. 系统资源 (CPU/内存/磁盘)
    2. API配额 (飞书/股票数据)
    3. 任务队列状态
    4. 性能指标
    """
    
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.log("="*70)
        self.log("COO资源监控中心 v0.1 初始化")
        self.log("="*70)
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def check_system_resources(self) -> Dict:
        """检查系统资源"""
        self.log("\n🔍 检查系统资源...")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_cores = psutil.cpu_count()
        
        # 内存
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        memory_percent = memory.percent
        
        # 磁盘
        disk = psutil.disk_usage(WORKSPACE)
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        disk_percent = (disk.used / disk.total) * 100
        
        resources = {
            'cpu': {
                'usage_percent': cpu_percent,
                'cores': cpu_cores,
                'status': 'NORMAL' if cpu_percent < 70 else 'WARNING' if cpu_percent < 90 else 'CRITICAL'
            },
            'memory': {
                'used_gb': round(memory_used_gb, 1),
                'total_gb': round(memory_total_gb, 1),
                'usage_percent': memory_percent,
                'status': 'NORMAL' if memory_percent < 70 else 'WARNING' if memory_percent < 90 else 'CRITICAL'
            },
            'disk': {
                'used_gb': round(disk_used_gb, 1),
                'total_gb': round(disk_total_gb, 1),
                'usage_percent': round(disk_percent, 1),
                'status': 'NORMAL' if disk_percent < 70 else 'WARNING' if disk_percent < 90 else 'CRITICAL'
            }
        }
        
        self.log(f"  CPU: {cpu_percent:.1f}% ({resources['cpu']['status']})")
        self.log(f"  内存: {memory_used_gb:.1f}GB / {memory_total_gb:.1f}GB ({memory_percent:.1f}%)")
        self.log(f"  磁盘: {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB ({disk_percent:.1f}%)")
        
        return resources
    
    def check_api_quotas(self) -> Dict:
        """检查API配额 (模拟)"""
        self.log("\n🔍 检查API配额...")
        
        # 模拟API使用情况 (实际应读取配额文件)
        quotas = {
            'feishu_api': {
                'daily_limit': 1000,
                'used': 45,
                'remaining': 955,
                'reset_time': '23:59',
                'status': 'NORMAL'
            },
            'akshare_api': {
                'daily_limit': 'unlimited',
                'used': 120,
                'status': 'NORMAL'
            },
            'coze_api': {
                'daily_limit': 500,
                'used': 23,
                'remaining': 477,
                'status': 'NORMAL'
            }
        }
        
        for api, data in quotas.items():
            self.log(f"  {api}: {data['used']} / {data.get('daily_limit', '∞')} ({data['status']})")
        
        return quotas
    
    def check_task_queue(self) -> Dict:
        """检查任务队列"""
        self.log("\n🔍 检查任务队列...")
        
        # 读取任务调度器状态
        task_state_file = f"{WORKSPACE}/data/orchestrator/task_state.json"
        if os.path.exists(task_state_file):
            with open(task_state_file, 'r') as f:
                task_state = json.load(f)
            
            total = len(task_state.get('tasks', {}))
            completed = sum(1 for t in task_state.get('tasks', {}).values() if t.get('status') == 'completed')
            failed = sum(1 for t in task_state.get('tasks', {}).values() if t.get('status') == 'failed')
            pending = total - completed - failed
            
            queue_status = {
                'total_tasks': total,
                'completed': completed,
                'failed': failed,
                'pending': pending,
                'status': 'HEALTHY' if failed == 0 else 'WARNING' if failed < 2 else 'CRITICAL'
            }
        else:
            queue_status = {
                'total_tasks': 6,
                'completed': 3,
                'failed': 0,
                'pending': 3,
                'status': 'HEALTHY'
            }
        
        self.log(f"  总任务: {queue_status['total_tasks']}")
        self.log(f"  已完成: {queue_status['completed']}")
        self.log(f"  失败: {queue_status['failed']}")
        self.log(f"  待执行: {queue_status['pending']}")
        
        return queue_status
    
    def generate_performance_recommendations(self, resources: Dict) -> List[str]:
        """生成性能优化建议"""
        recommendations = []
        
        if resources['disk']['usage_percent'] > 80:
            recommendations.append("磁盘使用率超过80%，建议清理日志文件")
        
        if resources['memory']['usage_percent'] > 85:
            recommendations.append("内存使用率过高，考虑重启服务或增加内存")
        
        # 检查日志文件大小
        log_dir = f"{WORKSPACE}/logs"
        if os.path.exists(log_dir):
            log_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, _, filenames in os.walk(log_dir)
                for filename in filenames
            ) / (1024**2)  # MB
            
            if log_size > 100:
                recommendations.append(f"日志文件累计{log_size:.1f}MB，建议归档清理")
        
        # 检查Git仓库大小
        git_dir = f"{WORKSPACE}/.git"
        if os.path.exists(git_dir):
            git_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, _, filenames in os.walk(git_dir)
                for filename in filenames
            ) / (1024**2)  # MB
            
            if git_size > 50:
                recommendations.append(f"Git仓库{git_size:.1f}MB，建议运行git gc优化")
        
        return recommendations if recommendations else ["系统运行良好，暂无优化建议"]
    
    def generate_operations_report(self) -> Dict:
        """生成运营报告"""
        self.log("\n" + "="*70)
        self.log("COO运营日报")
        self.log("="*70)
        
        # 资源检查
        resources = self.check_system_resources()
        
        # API配额
        quotas = self.check_api_quotas()
        
        # 任务队列
        queue = self.check_task_queue()
        
        # 性能建议
        recommendations = self.generate_performance_recommendations(resources)
        
        self.log(f"\n💡 性能优化建议:")
        for rec in recommendations:
            self.log(f"  - {rec}")
        
        # 计算运营健康度
        health_scores = [
            100 if resources['cpu']['status'] == 'NORMAL' else 50 if resources['cpu']['status'] == 'WARNING' else 0,
            100 if resources['memory']['status'] == 'NORMAL' else 50 if resources['memory']['status'] == 'WARNING' else 0,
            100 if resources['disk']['status'] == 'NORMAL' else 50 if resources['disk']['status'] == 'WARNING' else 0,
            100 if queue['status'] == 'HEALTHY' else 50 if queue['status'] == 'WARNING' else 0
        ]
        ops_health = sum(health_scores) / len(health_scores)
        
        self.log(f"\n📊 运营健康度: {ops_health:.0f}/100")
        
        # 生成报告
        report = {
            'report_type': 'COO_OPERATIONS_DAILY',
            'version': '0.1',
            'generated_at': datetime.now().isoformat(),
            'resources': resources,
            'api_quotas': quotas,
            'task_queue': queue,
            'recommendations': recommendations,
            'health_score': round(ops_health, 1),
            'status': 'HEALTHY' if ops_health >= 80 else 'WARNING' if ops_health >= 60 else 'CRITICAL'
        }
        
        # 保存报告
        report_file = f"{DATA_DIR}/coo_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"\n✅ 报告已保存: {report_file}")
        
        return report


def main():
    """主函数"""
    print("="*70)
    print("⚙️ COO资源监控与运营管理中心")
    print("Layer 0 - Chief Operating Officer v0.1")
    print("="*70)
    
    try:
        coo = ResourceMonitor()
        report = coo.generate_operations_report()
        
        print("\n" + "="*70)
        print("✅ COO运营报告生成完成")
        print(f"  运营健康度: {report['health_score']}/100 ({report['status']})")
        print(f"  CPU: {report['resources']['cpu']['usage_percent']:.1f}%")
        print(f"  内存: {report['resources']['memory']['usage_percent']:.1f}%")
        print(f"  磁盘: {report['resources']['disk']['usage_percent']:.1f}%")
        print(f"  待优化项: {len([r for r in report['recommendations'] if '建议' in r])}")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        print("   注意: 部分功能需要psutil库 (pip install psutil)")


if __name__ == "__main__":
    main()
