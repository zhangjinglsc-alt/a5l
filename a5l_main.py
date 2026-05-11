#!/usr/bin/env python3
"""
A5L v2.2 Main Entry
主入口 - 整合所有数据库功能

Usage:
    python a5l_main.py [command]
    
Commands:
    init        初始化数据库
    status      显示系统状态
    demo        运行演示
    dashboard   显示仪表板
"""

import sys
import argparse
from pathlib import Path

# 确保项目路径
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from database import get_db_manager, print_dashboard, get_dashboard_stats

console = Console()


def init_system():
    """初始化A5L系统"""
    console.print(Panel.fit(
        "[bold cyan]A5L v2.2 Initialization[/bold cyan]",
        border_style="cyan"
    ))
    
    # 初始化数据库
    db = get_db_manager()
    
    console.print("\n[green]✅ A5L系统初始化完成![/green]")
    console.print(f"[dim]数据库: {db.db_path}[/dim]")
    
    # 显示状态
    print_dashboard()


def show_status():
    """显示系统状态"""
    console.print(Panel.fit(
        "[bold cyan]A5L v2.2 System Status[/bold cyan]",
        border_style="cyan"
    ))
    
    dashboard = get_dashboard_stats()
    stats = dashboard['stats']
    
    table = Table(box=box.ROUNDED)
    table.add_column("Component", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Count", justify="right")
    
    table.add_row(
        "Database",
        "[green]✅ Connected[/green]",
        str(stats.get('total_atoms', 0))
    )
    table.add_row(
        "Atoms",
        "[green]✅ Active[/green]",
        f"{stats.get('active_atoms', 0)} / {stats.get('total_atoms', 0)}"
    )
    table.add_row(
        "Decisions",
        "[yellow]⏳ Pending[/yellow]" if stats.get('pending_decisions', 0) > 0 else "[green]✅ Clear[/green]",
        f"{stats.get('pending_decisions', 0)} / {stats.get('total_decisions', 0)}"
    )
    table.add_row(
        "Signals",
        "[green]✅ Generated[/green]",
        str(stats.get('total_signals', 0))
    )
    
    console.print(table)
    
    # Wave状态
    console.print("\n[bold]Wave Status:[/bold]")
    console.print("  Wave 1 (Prime): [green]✅ SQLite持久化完成[/green]")
    console.print("  Wave 2 (Level3): [green]✅ 决策系统完成[/green]")
    console.print("  Wave 3 (KIWI): [yellow]⏳ 待实现[/yellow]")


def run_demo():
    """运行完整演示"""
    console.print(Panel.fit(
        "[bold cyan]A5L v2.2 Demo[/bold cyan]\n"
        "[dim]展示数据库持久化功能[/dim]",
        border_style="cyan"
    ))
    
    from database.db_utils import save_analysis, save_decision_record, save_trade_signal
    
    # 1. 保存分析
    console.print("\n[bold]1. 保存分析[/bold]")
    analysis_id = save_analysis(
        content="测试分析内容 - 基于技术面和基本面的综合分析",
        title="演示分析",
        symbol="000001.SZ",
        analysis_type="demo"
    )
    console.print(f"[green]✅ Analysis saved: {analysis_id}[/green]")
    
    # 2. 保存决策
    console.print("\n[bold]2. 保存决策[/bold]")
    decision_id = save_decision_record(
        decision_type='trade',
        action='buy',
        symbol='000001.SZ',
        confidence=0.82,
        urgency=4,
        reason="演示决策",
        source_squad='execution_force'
    )
    console.print(f"[green]✅ Decision saved: {decision_id}[/green]")
    
    # 3. 保存信号
    console.print("\n[bold]3. 保存信号[/bold]")
    signal_id = save_trade_signal(
        symbol='000001.SZ',
        direction='bullish',
        strength=0.85,
        signal_type='demo',
        reason="演示信号"
    )
    console.print(f"[green]✅ Signal saved: ID={signal_id}[/green]")
    
    # 4. 显示最终状态
    console.print("\n[bold]4. 系统状态[/bold]")
    print_dashboard()
    
    console.print("\n[bold green]✅ Demo complete![/bold green]")


def show_dashboard():
    """显示仪表板"""
    console.print(Panel.fit(
        "[bold cyan]A5L v2.2 Dashboard[/bold cyan]",
        border_style="cyan"
    ))
    print_dashboard()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='A5L v2.2 - SQLite Persistence Edition')
    parser.add_argument('command', nargs='?', default='status',
                       choices=['init', 'status', 'demo', 'dashboard'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_system()
    elif args.command == 'status':
        show_status()
    elif args.command == 'demo':
        run_demo()
    elif args.command == 'dashboard':
        show_dashboard()
    else:
        show_status()


if __name__ == '__main__':
    main()
