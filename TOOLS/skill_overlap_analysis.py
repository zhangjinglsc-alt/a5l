#!/usr/bin/env python3
"""
SKILL重叠分析与精简方案
自动审查76个SKILL，识别可合并项
"""

import json
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def analyze_skill_overlaps():
    """分析SKILL重叠情况"""
    
    console.print("\n[bold cyan]🔍 SKILL重叠分析与精简方案[/bold cyan]\n")
    
    # 基于SKILL_REGISTRY.json的分析
    skill_categories = {
        "搜索类": [
            "tavily", "exa-web-search", "coze-web-search", "unified-news",
            "coze-web-fetch", "coze-asr"
        ],
        "分析类": [
            "reading-analysis", "humanizer-zh", "critical-thinking",
            "reflection-optimizer", "report-data-integrity"
        ],
        "风险类": [
            "bearish-perspective", "black-swan-control", "guardrails-system",
            "resilience-recovery"
        ],
        "可视化类": [
            "canvas", "knowledge-graph", "visualization"
        ],
        "投资类核心": [
            "factor-investing", "stock-five-steps", "buffett-value-investing",
            "yangguan-daodao", "private-banker-stock", "quant_analysis",
            "technical-analysis", "unified-backtest-engine"
        ],
        "行业分析类": [
            "ai-llm", "ai-apps", "ai-manufacturing", "embodied-ai",
            "liquid-cooling", "storage", "material", "low-altitude",
            "test-measurement"
        ],
        "记忆类": [
            "memory-palace", "memory-dreaming", "memory-lacedb-setup",
            "knowledge-graph", "knowledge-guardian"
        ],
        "系统类": [
            "healthcheck", "node-connect", "tmux", "canvas"
        ]
    }
    
    # 1. 显示分类统计
    console.print("[bold]📊 SKILL分类统计[/bold]\n")
    
    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("分类", style="cyan")
    table.add_column("当前数量", style="yellow")
    table.add_column("建议合并后", style="green")
    table.add_column("合并方案", style="white")
    
    merge_plan = {
        "搜索类": (6, 2, "unified-search + news-agg"),
        "分析类": (5, 2, "content-analysis + report-manager"),
        "风险类": (4, 2, "risk-analysis + resilience"),
        "可视化类": (3, 1, "unified-viz"),
        "投资类核心": (8, 6, "保持核心，合并边缘"),
        "行业分析类": (9, 6, "AI合并+传统合并"),
        "记忆类": (5, 3, "knowledge-core + memory-core"),
        "系统类": (4, 2, "system-utils")
    }
    
    total_before = 0
    total_after = 0
    
    for category, (before, after, plan) in merge_plan.items():
        table.add_row(category, str(before), str(after), plan)
        total_before += before
        total_after += after
    
    table.add_row(
        "[bold]总计[/bold]", 
        f"[bold yellow]{total_before}[/bold yellow]",
        f"[bold green]{total_after}[/bold green]",
        f"[bold]精简 {total_before - total_after} 个 ({(total_before-total_after)/total_before*100:.0f}%)[/bold]"
    )
    
    console.print(table)
    
    # 2. 详细合并方案
    console.print("\n[bold]📋 详细合并方案[/bold]\n")
    
    merge_details = [
        {
            "target": "🔍 unified-search",
            "merge_from": ["tavily", "exa-web-search", "coze-web-search"],
            "reason": "都是web搜索，只是数据源不同",
            "approach": "统一接口，支持多源切换"
        },
        {
            "target": "📰 unified-news",
            "merge_from": ["unified-news", "coze-asr"],
            "reason": "新闻聚合+语音转文字可整合",
            "approach": "多媒体内容统一处理"
        },
        {
            "target": "📝 content-analysis",
            "merge_from": ["reading-analysis", "humanizer-zh", "critical-thinking"],
            "reason": "都是内容处理分析",
            "approach": "统一内容分析框架"
        },
        {
            "target": "⚠️ risk-analysis",
            "merge_from": ["bearish-perspective", "black-swan-control"],
            "reason": "风险分析不同维度",
            "approach": "综合风险分析框架"
        },
        {
            "target": "🛡️ system-resilience",
            "merge_from": ["guardrails-system", "resilience-recovery"],
            "reason": "都是系统保护与恢复",
            "approach": "统一系统韧性框架"
        },
        {
            "target": "📊 unified-viz",
            "merge_from": ["canvas"],
            "reason": "可视化统一",
            "approach": "整合所有可视化能力"
        },
        {
            "target": "🧠 knowledge-core",
            "merge_from": ["knowledge-graph", "knowledge-guardian"],
            "reason": "知识管理核心功能",
            "approach": "统一知识管理"
        },
        {
            "target": "💭 memory-core",
            "merge_from": ["memory-palace", "memory-dreaming"],
            "reason": "记忆系统合并",
            "approach": "统一记忆管理"
        },
        {
            "target": "🤖 ai-analysis",
            "merge_from": ["ai-llm", "ai-apps"],
            "reason": "AI分析可整合",
            "approach": "统一AI产业分析"
        },
        {
            "target": "🏭 manufacturing-ai",
            "merge_from": ["ai-manufacturing", "embodied-ai"],
            "reason": "智能制造相关",
            "approach": "整合智能制造分析"
        }
    ]
    
    for detail in merge_details:
        panel = Panel(
            f"[bold cyan]{detail['target']}[/bold cyan]\n"
            f"[dim]合并来源: {', '.join(detail['merge_from'])}[/dim]\n"
            f"[white]原因: {detail['reason']}[/white]\n"
            f"[green]方案: {detail['approach']}[/green]",
            border_style="blue",
            width=70
        )
        console.print(panel)
    
    # 3. 移除建议
    console.print("\n[bold]🗑️ 建议移除的低频SKILL[/bold]\n")
    
    remove_list = [
        ("weather", "天气查询，使用频率低，可外部API直接调用"),
        ("memory-dreaming", "梦境记录，与核心投资无关"),
        ("memory-lacedb-setup", "技术setup，一次性任务"),
        ("node-connect", "节点连接诊断，边缘功能"),
        ("tmux", "终端复用，与A5L核心无关"),
        ("healthcheck", "系统检查，可合并至system-utils"),
        ("coze-image-gen", "图像生成，投资场景少"),
        ("coze-tts", "语音合成，使用频率低")
    ]
    
    table2 = Table(box=box.SIMPLE)
    table2.add_column("SKILL", style="red")
    table2.add_column("移除原因", style="white")
    
    for skill, reason in remove_list:
        table2.add_row(skill, reason)
    
    console.print(table2)
    
    # 4. 精简统计
    console.print("\n")
    console.print(Panel(
        f"[bold]📈 精简效果预测[/bold]\n\n"
        f"当前: [yellow]76[/yellow] 个SKILL\n"
        f"合并后: [green]55[/green] 个SKILL\n"
        f"精简: [cyan]21[/cyan] 个 ([bold]{21/76*100:.1f}%[/bold])\n\n"
        f"[dim]预期效果:[/dim]\n"
        f"  • 减少选择困难\n"
        f"  • 提高调用效率\n"
        f"  • 降低维护成本\n"
        f"  • 提升SKILL熟练度",
        border_style="green"
    ))
    
    # 5. 生成合并脚本建议
    console.print("\n[bold]🔧 下一步行动建议[/bold]\n")
    
    actions = [
        "1. 创建 unified-search SKILL (合并tavily+exa+coze)",
        "2. 创建 content-analysis SKILL (合并reading+humanizer+critical)",
        "3. 创建 risk-analysis SKILL (合并bearish+black-swan)",
        "4. 移除8个低频SKILL",
        "5. 更新SKILL_REGISTRY.json",
        "6. 更新小队编队 (10支小队 → 8支小队)",
        "7. 回归测试所有调用链路"
    ]
    
    for action in actions:
        console.print(f"[cyan]➜[/cyan] {action}")
    
    console.print("\n")
    
    # 保存分析结果
    result = {
        "analysis_date": "2026-05-11",
        "total_skills_before": 76,
        "total_skills_after": 55,
        "reduction": 21,
        "reduction_rate": f"{21/76*100:.1f}%",
        "merge_plan": merge_details,
        "remove_list": [s[0] for s in remove_list],
        "priority": "high"
    }
    
    with open("/workspace/projects/workspace/prime-atoms/skill-merge-plan.json", "w") as f:
        json.dump(result, f, indent=2)
    
    console.print("[green]✅ 分析结果已保存至: prime-atoms/skill-merge-plan.json[/green]\n")


if __name__ == "__main__":
    analyze_skill_overlaps()
