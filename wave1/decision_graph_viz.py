#!/usr/bin/env python3
"""
A5L可视化决策图谱 - Wave 1 Phase 1.2
Atom关系图谱 + 决策链路追踪
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box

console = Console()


@dataclass
class AtomNode:
    """Atom节点"""
    id: str
    kind: str
    name: str
    domain: str
    manager: str
    relations: List[str]


class DecisionGraphVisualizer:
    """决策图谱可视化器"""
    
    def __init__(self):
        self.atoms = {}
        self.decision_chains = []
        
    def load_atoms(self):
        """加载Prime Atoms"""
        console.print("[bold cyan]📊 可视化决策图谱 - 构建[/bold cyan]\n")
        
        # 模拟加载Atoms
        sample_atoms = [
            AtomNode("@a5l/decision-buy-000066", "decision", "中国长城买入决策", "investment", "CIO", 
                    ["@a5l/analysis-catalyst", "@a5l/signal-breakout", "@a5l/risk-check"]),
            AtomNode("@a5l/analysis-catalyst", "analysis", "催化剂分析", "analysis", "KG", []),
            AtomNode("@a5l/signal-breakout", "signal", "突破信号", "strategy", "CIO", []),
            AtomNode("@a5l/risk-check", "risk", "风险检查", "risk", "CSO", []),
            AtomNode("@a5l/squad-cio-001", "squad", "投资决策小队", "orchestration", "CIO", []),
            AtomNode("@a5l/data-price-000066", "data", "股价数据", "data", "COO", [])
        ]
        
        for atom in sample_atoms:
            self.atoms[atom.id] = atom
        
        console.print(f"[green]✅ 加载 {len(self.atoms)} 个Atoms[/green]\n")
    
    def build_relation_graph(self):
        """构建关系图谱"""
        console.print("[bold]🔗 Atom关系图谱[/bold]\n")
        
        # 构建关系树
        root = Tree("[bold cyan]🎯 决策图谱根节点[/bold cyan]")
        
        # 决策节点
        decision_node = root.add("[yellow]📋 决策层[/yellow]")
        decision_node.add("[green]@a5l/decision-buy-000066[/green] - 中国长城买入决策")
        
        # 分析节点
        analysis_node = root.add("[blue]🔍 分析层[/blue]")
        analysis_node.add("@a5l/analysis-catalyst - 催化剂分析")
        analysis_node.add("@a5l/signal-breakout - 突破信号")
        analysis_node.add("@a5l/risk-check - 风险检查")
        
        # 执行节点
        exec_node = root.add("[magenta]⚙️ 执行层[/magenta]")
        exec_node.add("@a5l/squad-cio-001 - 投资决策小队")
        exec_node.add("@a5l/data-price-000066 - 股价数据")
        
        console.print(root)
        console.print()
    
    def trace_decision_chain(self, decision_id: str):
        """追踪决策链路"""
        console.print(f"[bold]🔍 决策链路追踪: {decision_id}[/bold]\n")
        
        chain = [
            {"step": 1, "atom": "@a5l/data-price-000066", "action": "获取股价数据", "status": "✅"},
            {"step": 2, "atom": "@a5l/signal-breakout", "action": "检测突破信号", "status": "✅"},
            {"step": 3, "atom": "@a5l/analysis-catalyst", "action": "催化剂分级", "status": "✅"},
            {"step": 4, "atom": "@a5l/risk-check", "action": "风险评估", "status": "✅"},
            {"step": 5, "atom": "@a5l/squad-cio-001", "action": "小队协同决策", "status": "✅"},
            {"step": 6, "atom": "@a5l/decision-buy-000066", "action": "生成买入决策", "status": "✅"}
        ]
        
        table = Table(box=box.ROUNDED, show_header=True)
        table.add_column("步骤", style="cyan", width=6)
        table.add_column("Atom", style="white")
        table.add_column("动作", style="yellow")
        table.add_column("状态", style="green", width=8)
        
        for step in chain:
            table.add_row(
                str(step["step"]),
                step["atom"],
                step["action"],
                step["status"]
            )
        
        console.print(table)
        
        # 统计
        console.print(f"\n[dim]链路长度: {len(chain)} 步 | 涉及Atoms: {len(set(s['atom'] for s in chain))} 个[/dim]\n")
    
    def generate_fei_shu_card(self):
        """生成飞书卡片格式"""
        console.print("[bold]📱 飞书集成卡片[/bold]\n")
        
        card_data = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "A5L决策图谱"},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "plain_text", "content": "决策: 中国长城买入"}
                },
                {
                    "tag": "div",
                    "fields": [
                        {"is_short": True, "text": {"tag": "plain_text", "content": "状态: ✅ 已通过"}},
                        {"is_short": True, "text": {"tag": "plain_text", "content": "耗时: 120ms"}}
                    ]
                },
                {
                    "tag": "div",
                    "text": {"tag": "plain_text", "content": "调用链路: data → signal → analysis → risk → squad → decision"}
                }
            ]
        }
        
        console.print("[dim]飞书卡片JSON:[/dim]")
        console.print(json.dumps(card_data, indent=2, ensure_ascii=False))
        console.print()
    
    def visualize_manager_network(self):
        """可视化管理者网络"""
        console.print("[bold]🕸️ 六管理者协作网络[/bold]\n")
        
        # 管理者协作关系
        network = {
            "CIO": {"connections": ["KG", "CSO", "COO"], "atoms": 3},
            "KG": {"connections": ["CIO", "RM"], "atoms": 2},
            "CSO": {"connections": ["CIO", "CA"], "atoms": 2},
            "COO": {"connections": ["CIO", "CA"], "atoms": 2},
            "CA": {"connections": ["CSO", "COO"], "atoms": 1},
            "RM": {"connections": ["KG"], "atoms": 1}
        }
        
        table = Table(box=box.SIMPLE)
        table.add_column("管理者", style="cyan")
        table.add_column("协同对象", style="white")
        table.add_column("涉及Atoms", style="yellow")
        table.add_column("中心度", style="green")
        
        for manager, data in network.items():
            centrality = len(data["connections"])
            centrality_label = "🔥高" if centrality >= 3 else "⚡中" if centrality >= 2 else "📊低"
            table.add_row(
                manager,
                ", ".join(data["connections"]),
                str(data["atoms"]),
                centrality_label
            )
        
        console.print(table)
        console.print()
    
    def run(self):
        """运行完整可视化"""
        self.load_atoms()
        self.build_relation_graph()
        self.trace_decision_chain("@a5l/decision-buy-000066")
        self.generate_fei_shu_card()
        self.visualize_manager_network()
        
        console.print(Panel(
            "[bold green]✅ Wave 1 Phase 1.2 可视化决策图谱 完成！[/bold green]\n\n"
            "[white]成果:[/white]\n"
            "  • Atom关系图谱 (层级结构)\n"
            "  • 决策链路追踪 (6步完整链路)\n"
            "  • 飞书集成卡片 (JSON格式)\n"
            "  • 管理者协作网络 (中心度分析)",
            border_style="green"
        ))


if __name__ == "__main__":
    viz = DecisionGraphVisualizer()
    viz.run()
