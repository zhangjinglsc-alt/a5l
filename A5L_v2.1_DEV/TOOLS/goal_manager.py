#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goal-Oriented Task Management System
目标导向任务管理系统 v2.0

功能：
1. 目标分解为任务树
2. 任务状态跟踪
3. 进度可视化
4. 主动汇报生成
5. 验收流程管理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

class TaskStatus(Enum):
    PENDING = "待开始"
    IN_PROGRESS = "进行中"
    BLOCKED = "阻塞中"
    REVIEW = "待验收"
    COMPLETED = "已完成"
    CANCELLED = "已取消"

class GoalManager:
    """目标管理器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.goals_file = f"{workspace}/data/goals/goals.json"
        self.tasks_file = f"{workspace}/data/goals/tasks.json"
        self.progress_file = f"{workspace}/data/goals/progress.json"
        
        # 确保目录存在
        os.makedirs(f"{workspace}/data/goals", exist_ok=True)
        
        # 加载数据
        self.goals = self._load_json(self.goals_file, [])
        self.tasks = self._load_json(self.tasks_file, [])
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """加载JSON文件"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, filepath: str, data: Any):
        """保存JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_goal(self, title: str, description: str, 
                   deadline: Optional[str] = None,
                   parent_id: Optional[str] = None) -> Dict:
        """创建目标"""
        goal_id = f"G{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        goal = {
            "id": goal_id,
            "title": title,
            "description": description,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "deadline": deadline,
            "parent_id": parent_id,
            "progress": 0,
            "tasks": []
        }
        
        self.goals.append(goal)
        self._save_json(self.goals_file, self.goals)
        
        return goal
    
    def create_task(self, goal_id: str, title: str, 
                   description: str = "",
                   estimated_hours: int = 0,
                   dependencies: List[str] = None) -> Dict:
        """创建任务"""
        task_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        task = {
            "id": task_id,
            "goal_id": goal_id,
            "title": title,
            "description": description,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "estimated_hours": estimated_hours,
            "actual_hours": 0,
            "dependencies": dependencies or [],
            "progress": 0,
            "blockers": [],
            "notes": []
        }
        
        self.tasks.append(task)
        
        # 关联到目标
        for goal in self.goals:
            if goal['id'] == goal_id:
                goal['tasks'].append(task_id)
                break
        
        self._save_json(self.tasks_file, self.tasks)
        self._save_json(self.goals_file, self.goals)
        
        return task
    
    def start_task(self, task_id: str) -> Dict:
        """开始任务"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = TaskStatus.IN_PROGRESS.value
                task['started_at'] = datetime.now().isoformat()
                self._save_json(self.tasks_file, self.tasks)
                return task
        return None
    
    def update_task_progress(self, task_id: str, progress: int, 
                            notes: str = "") -> Dict:
        """更新任务进度"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['progress'] = min(100, max(0, progress))
                if notes:
                    task['notes'].append({
                        "timestamp": datetime.now().isoformat(),
                        "content": notes
                    })
                
                # 自动状态流转
                if progress >= 100:
                    task['status'] = TaskStatus.REVIEW.value
                
                self._save_json(self.tasks_file, self.tasks)
                self._update_goal_progress(task['goal_id'])
                return task
        return None
    
    def block_task(self, task_id: str, reason: str) -> Dict:
        """标记任务阻塞"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = TaskStatus.BLOCKED.value
                task['blockers'].append({
                    "timestamp": datetime.now().isoformat(),
                    "reason": reason
                })
                self._save_json(self.tasks_file, self.tasks)
                return task
        return None
    
    def unblock_task(self, task_id: str, solution: str = "") -> Dict:
        """解除任务阻塞"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = TaskStatus.IN_PROGRESS.value
                task['notes'].append({
                    "timestamp": datetime.now().isoformat(),
                    "content": f"阻塞解除: {solution}"
                })
                self._save_json(self.tasks_file, self.tasks)
                return task
        return None
    
    def complete_task(self, task_id: str, actual_hours: int = 0,
                     self_rating: int = 0, summary: str = "") -> Dict:
        """完成任务"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = TaskStatus.COMPLETED.value
                task['progress'] = 100
                task['completed_at'] = datetime.now().isoformat()
                task['actual_hours'] = actual_hours
                task['self_rating'] = self_rating
                task['summary'] = summary
                
                self._save_json(self.tasks_file, self.tasks)
                self._update_goal_progress(task['goal_id'])
                return task
        return None
    
    def _update_goal_progress(self, goal_id: str):
        """更新目标进度"""
        for goal in self.goals:
            if goal['id'] == goal_id:
                task_ids = goal.get('tasks', [])
                if not task_ids:
                    goal['progress'] = 0
                else:
                    total_progress = 0
                    for tid in task_ids:
                        for task in self.tasks:
                            if task['id'] == tid:
                                total_progress += task.get('progress', 0)
                                break
                    goal['progress'] = round(total_progress / len(task_ids), 1)
                
                self._save_json(self.goals_file, self.goals)
                break
    
    def get_progress_dashboard(self) -> str:
        """获取进度看板"""
        dashboard = []
        dashboard.append("=" * 60)
        dashboard.append("📊 GOAL-ORIENTED 进度看板")
        dashboard.append("=" * 60)
        dashboard.append(f"\n更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 统计
        total_tasks = len(self.tasks)
        completed = len([t for t in self.tasks if t['status'] == TaskStatus.COMPLETED.value])
        in_progress = len([t for t in self.tasks if t['status'] == TaskStatus.IN_PROGRESS.value])
        blocked = len([t for t in self.tasks if t['status'] == TaskStatus.BLOCKED.value])
        pending = len([t for t in self.tasks if t['status'] == TaskStatus.PENDING.value])
        
        dashboard.append(f"📈 任务统计")
        dashboard.append(f"   总计: {total_tasks} | 已完成: {completed} | 进行中: {in_progress}")
        dashboard.append(f"   阻塞: {blocked} | 待开始: {pending}")
        
        if total_tasks > 0:
            overall_progress = sum(t.get('progress', 0) for t in self.tasks) / total_tasks
            bar_length = 30
            filled = int(bar_length * overall_progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            dashboard.append(f"\n🎯 整体进度 [{bar}] {overall_progress:.1f}%")
        
        # 目标详情
        if self.goals:
            dashboard.append(f"\n📋 目标列表\n")
            for goal in self.goals:
                g_bar = "█" * int(20 * goal.get('progress', 0) / 100) + "░" * (20 - int(20 * goal.get('progress', 0) / 100))
                dashboard.append(f"   [{g_bar}] {goal.get('progress', 0):>5.1f}% | {goal['title']}")
        
        # 进行中任务
        active_tasks = [t for t in self.tasks if t['status'] == TaskStatus.IN_PROGRESS.value]
        if active_tasks:
            dashboard.append(f"\n🔄 进行中任务\n")
            for task in active_tasks[:5]:  # 只显示前5个
                t_bar = "█" * int(15 * task.get('progress', 0) / 100) + "░" * (15 - int(15 * task.get('progress', 0) / 100))
                dashboard.append(f"   [{t_bar}] {task.get('progress', 0):>4.0f}% | {task['title']}")
        
        # 阻塞任务
        blocked_tasks = [t for t in self.tasks if t['status'] == TaskStatus.BLOCKED.value]
        if blocked_tasks:
            dashboard.append(f"\n🚨 阻塞任务 (需关注)\n")
            for task in blocked_tasks:
                blocker = task.get('blockers', [{}])[-1]
                dashboard.append(f"   ⚠️ {task['title']}")
                dashboard.append(f"      原因: {blocker.get('reason', '未知')}")
        
        # 待验收任务
        review_tasks = [t for t in self.tasks if t['status'] == TaskStatus.REVIEW.value]
        if review_tasks:
            dashboard.append(f"\n✅ 待验收任务\n")
            for task in review_tasks:
                dashboard.append(f"   📋 {task['title']}")
                dashboard.append(f"      自评: {task.get('self_rating', 'N/A')}/100")
        
        dashboard.append("\n" + "=" * 60)
        
        return "\n".join(dashboard)
    
    def generate_daily_report(self) -> str:
        """生成每日简报"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        report = []
        report.append("=" * 60)
        report.append("📅 GOAL-ORIENTED 每日简报")
        report.append("=" * 60)
        report.append(f"\n日期: {today.strftime('%Y-%m-%d')}\n")
        
        # 昨日完成
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        completed_yesterday = [
            t for t in self.tasks 
            if t.get('completed_at') and t['completed_at'].startswith(yesterday_str)
        ]
        
        report.append("✅ 昨日完成")
        if completed_yesterday:
            for task in completed_yesterday:
                report.append(f"   • {task['title']} (自评: {task.get('self_rating', 'N/A')}/100)")
        else:
            report.append("   (无)")
        
        # 今日计划
        in_progress = [t for t in self.tasks if t['status'] == TaskStatus.IN_PROGRESS.value]
        pending = [t for t in self.tasks if t['status'] == TaskStatus.PENDING.value][:3]
        
        report.append(f"\n📋 今日计划")
        if in_progress:
            report.append("   进行中:")
            for task in in_progress:
                report.append(f"      • {task['title']} ({task.get('progress', 0)}%)")
        if pending:
            report.append("   待开始:")
            for task in pending:
                report.append(f"      • {task['title']}")
        
        # 阻塞风险
        blocked = [t for t in self.tasks if t['status'] == TaskStatus.BLOCKED.value]
        if blocked:
            report.append(f"\n🚨 阻塞风险 (需决策)")
            for task in blocked:
                blocker = task.get('blockers', [{}])[-1]
                report.append(f"   ⚠️ {task['title']}")
                report.append(f"      原因: {blocker.get('reason', '未知')}")
        
        # 待验收
        review = [t for t in self.tasks if t['status'] == TaskStatus.REVIEW.value]
        if review:
            report.append(f"\n📋 待验收 (请确认)")
            for task in review:
                report.append(f"   • {task['title']} - 自评{task.get('self_rating', 'N/A')}/100")
        
        # 关键指标
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t['status'] == TaskStatus.COMPLETED.value])
        progress = (completed / total * 100) if total > 0 else 0
        
        report.append(f"\n📊 关键指标")
        report.append(f"   任务完成率: {completed}/{total} ({progress:.1f}%)")
        report.append(f"   当前阻塞: {len(blocked)} 个")
        report.append(f"   待验收: {len(review)} 个")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)

def main():
    """主函数 - 演示"""
    gm = GoalManager()
    
    print("🎯 Goal-Oriented Task Management System v2.0\n")
    print("=" * 60)
    
    # 创建目标
    goal = gm.create_goal(
        title="实现L3自主进化",
        description="从L2半辅助模式进化到L3半自主模式",
        deadline="2026-05-15"
    )
    print(f"\n✅ 创建目标: {goal['title']}")
    
    # 创建任务
    tasks = [
        ("建立自诊断引擎", "实现系统自检功能", 4),
        ("实现自修复功能", "自动识别并修复简单问题", 8),
        ("建立预测能力", "预测性维护与优化建议", 12),
        ("完善验收机制", "任务完成自评与验收流程", 4),
        ("持续运行7天无干预", "验证L3自主能力", 168)
    ]
    
    for title, desc, hours in tasks:
        task = gm.create_task(goal['id'], title, desc, hours)
        print(f"   📋 创建任务: {title}")
    
    # 模拟进度更新
    print("\n🔄 模拟任务进度...\n")
    
    # 任务1完成
    task1 = [t for t in gm.tasks if "自诊断" in t['title']][0]
    gm.start_task(task1['id'])
    gm.update_task_progress(task1['id'], 100, "自检5项全部通过")
    gm.complete_task(task1['id'], 3, 95, "首次自检成功，系统健康")
    print(f"✅ 完成任务: {task1['title']} (自评95分)")
    
    # 任务2进行中
    task2 = [t for t in gm.tasks if "自修复" in t['title']][0]
    gm.start_task(task2['id'])
    gm.update_task_progress(task2['id'], 35, "正在实现自动修复逻辑")
    print(f"🔄 进行中: {task2['title']} (35%)")
    
    # 任务3待开始
    task3 = [t for t in gm.tasks if "预测" in t['title']][0]
    print(f"⏳ 待开始: {task3['title']}")
    
    # 显示看板
    print("\n" + gm.get_progress_dashboard())
    
    # 生成每日简报
    print("\n" + gm.generate_daily_report())

if __name__ == "__main__":
    main()
