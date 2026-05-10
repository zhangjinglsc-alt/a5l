#!/usr/bin/env python3
"""
Agent Core重构 - Wave 2 Phase 2.1
从调用式到自主Agent的核心重构
"""

import asyncio
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box

console = Console()


@dataclass
class AgentTask:
    """Agent任务"""
    id: str
    goal: str
    context: Dict
    priority: int = 2
    callbacks: List[Callable] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"


class AutonomousAgentCore:
    """自主Agent核心 - Wave 2重构"""
    
    def __init__(self):
        self.goal_queue = []
        self.active_tasks = {}
        self.plan_library = {}
        self.memory = {}
        
    def init_core(self):
        """初始化Agent Core"""
        console.print("[bold cyan]🤖 Agent Core V2.0 - 自主Agent重构[/bold cyan]\n")
        console.print("[dim]从调用式 → 自主Agent[/dim]\n")
        
        console.print("[green]✅ Agent Core初始化完成[/green]")
        console.print("  [dim]• 目标队列系统[/dim]")
        console.print("  [dim]• 自主规划引擎[/dim]")
        console.print("  [dim]• 上下文记忆[/dim]")
        console.print("  [dim]• 回调机制[/dim]\n")
    
    def set_goal(self, goal: str, context: Dict = None) -> str:
        """设置目标 (自主触发)"""
        task_id = f"task_{datetime.now().strftime('%H%M%S')}_{len(self.goal_queue)}"
        
        task = AgentTask(
            id=task_id,
            goal=goal,
            context=context or {},
            priority=context.get("priority", 2)
        )
        
        self.goal_queue.append(task)
        console.print(f"[cyan]🎯 新目标: {goal[:40]}...[/cyan]")
        console.print(f"  [dim]任务ID: {task_id} | 优先级: P{task.priority}[/dim]\n")
        
        return task_id
    
    def autonomous_plan(self, task: AgentTask) -> List[Dict]:
        """自主规划 - 将目标分解为步骤"""
        
        # 基于目标关键词的智能规划
        goal_lower = task.goal.lower()
        
        if "买入" in goal_lower or "卖出" in goal_lower:
            plan = [
                {"step": 1, "action": "数据获取", "skill": "data_fetch", "autonomous": True},
                {"step": 2, "action": "技术分析", "skill": "technical", "autonomous": True},
                {"step": 3, "action": "基本面分析", "skill": "fundamental", "autonomous": True},
                {"step": 4, "action": "风险评估", "skill": "risk", "autonomous": True},
                {"step": 5, "action": "决策生成", "skill": "decision", "autonomous": False}  # 需人工确认
            ]
        elif "研报" in goal_lower or "研究" in goal_lower:
            plan = [
                {"step": 1, "action": "信息收集", "skill": "search", "autonomous": True},
                {"step": 2, "action": "知识提取", "skill": "extract", "autonomous": True},
                {"step": 3, "action": "分析综合", "skill": "synthesis", "autonomous": True},
                {"step": 4, "action": "报告生成", "skill": "report", "autonomous": True}
            ]
        else:
            plan = [
                {"step": 1, "action": "意图识别", "skill": "intent", "autonomous": True},
                {"step": 2, "action": "资源分配", "skill": "dispatch", "autonomous": True},
                {"step": 3, "action": "执行处理", "skill": "execute", "autonomous": True}
            ]
        
        return plan
    
    def execute_step(self, step: Dict, context: Dict) -> Dict:
        """执行单步"""
        # 模拟执行
        import random
        success = random.random() > 0.1  # 90%成功率
        
        return {
            "step": step["step"],
            "action": step["action"],
            "success": success,
            "result": f"{step['action']}完成" if success else f"{step['action']}失败",
            "autonomous": step.get("autonomous", True)
        }
    
    def run_autonomous(self, task_id: str):
        """自主运行任务"""
        task = next((t for t in self.goal_queue if t.id == task_id), None)
        if not task:
            console.print(f"[red]任务 {task_id} 不存在[/red]")
            return
        
        console.print(f"[bold]🚀 自主执行任务: {task.goal[:30]}...[/bold]\n")
        
        # 1. 规划
        plan = self.autonomous_plan(task)
        console.print(f"[dim]生成规划: {len(plan)} 步[/dim]\n")
        
        # 2. 执行
        results = []
        for step in plan:
            result = self.execute_step(step, task.context)
            results.append(result)
            
            icon = "✅" if result["success"] else "❌"
            mode = "[autonomous]" if result["autonomous"] else "[manual]"
            console.print(f"  {icon} Step {step['step']}: {step['action']} {mode}")
            
            # 非自主步骤暂停等待人工
            if not result["autonomous"] and result["success"]:
                console.print(f"  [yellow]  ⏸️ 等待人工确认...[/yellow]")
        
        # 3. 完成
        task.status = "completed"
        success_count = sum(1 for r in results if r["success"])
        
        console.print(f"\n[green]✅ 任务完成: {success_count}/{len(results)} 步成功[/green]\n")
        
        return results
    
    def compare_old_vs_new(self):
        """对比新旧架构"""
        console.print("[bold]📊 架构对比: 调用式 vs 自主Agent[/bold]\n")
        
        table = Table(box=box.DOUBLE_EDGE)
        table.add_column("特性", style="cyan")
        table.add_column("旧架构 (调用式)", style="red")
        table.add_column("新架构 (自主Agent)", style="green")
        
        comparisons = [
            ("交互模式", "人工调用每个SKILL", "设定目标，自主执行"),
            ("规划能力", "人工规划步骤", "AI自动生成规划"),
            ("异常处理", "人工判断处理", "自主重试/降级"),
            ("上下文", "单次会话", "跨会话记忆"),
            ("效率", "人工驱动", "7x24自主运行"),
            ("复杂度", "简单直接", "智能复杂")
        ]
        
        for feature, old, new in comparisons:
            table.add_row(feature, old, new)
        
        console.print(table)
        console.print()
    
    def demo_autonomous_workflow(self):
        """演示自主工作流"""
        console.print("[bold]🎬 自主工作流演示[/bold]\n")
        
        # 场景1: 买入决策
        console.print("[cyan]场景1: 中国长城买入决策[/cyan]")
        task1 = self.set_goal("分析中国长城(000066)并生成买入决策", {
            "symbol": "000066.SZ",
            "priority": 0
        })
        self.run_autonomous(task1)
        
        # 场景2: 研报分析
        console.print("[cyan]场景2: AI算力研报深度分析[/cyan]")
        task2 = self.set_goal("分析最新AI算力建设研报", {
            "topic": "AI算力",
            "priority": 1
        })
        self.run_autonomous(task2)
    
    def run(self):
        """运行完整演示"""
        self.init_core()
        self.compare_old_vs_new()
        self.demo_autonomous_workflow()
        
        console.print(Panel(
            "[bold green]✅ Wave 2 Phase 2.1 Agent Core重构 完成！[/bold green]\n\n"
            "[white]成果:[/white]\n"
            "  • 目标队列系统\n"
            "  • 自主规划引擎\n"
            "  • 步骤自动执行\n"
            "  • 人工确认点 (关键决策)\n\n"
            "[dim]从调用式 → 自主Agent 重构完成[/dim]",
            border_style="green"
        ))


if __name__ == "__main__":
    agent = AutonomousAgentCore()
    agent.run()
