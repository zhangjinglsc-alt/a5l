#!/usr/bin/env python3
"""
SKILL小队Prime Atom生成器
为六管理者创建SKILL小队编队Atom
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/workspace/projects/workspace/TOOLS')
from prime_poc import PrimeAtom, A5LKnowledgeGraph


def create_skill_squads():
    """创建所有SKILL小队"""
    
    print("="*70)
    print("🎯 SKILL小队Prime Atom生成")
    print("="*70)
    
    kg = A5LKnowledgeGraph()
    squads = []
    
    # ========================================
    # 1. CA - 核心架构小队
    # ========================================
    print("\n📦 创建 CA-核心架构小队...")
    
    ca_squad = PrimeAtom(
        id="@a5l/squad-ca-001",
        kind="squad",
        version="2.1.0",
        domain="a5l-core"
    )
    ca_squad.set_content(
        name="核心架构小队",
        name_en="Core Architecture Squad",
        manager="@a5l/persona-chief-architect",
        description="A5L五层架构设计与维护，Prime系统集成",
        members=[
            {"skill": "@a5l/skill-architect-5l", "role": "队长", "domain": "architecture"},
            {"skill": "@a5l/skill-ssmg-integration", "role": "副队长", "domain": "integration"},
            {"skill": "@a5l/skill-prime-poc", "role": "工程师", "domain": "prime"},
            {"skill": "@a5l/skill-evolution-engine", "role": "工程师", "domain": "evolution"},
            {"skill": "@a5l/skill-meta-control", "role": "架构师", "domain": "meta-control"}
        ],
        core_functions=["架构设计", "Prime集成", "自进化维护"]
    )
    ca_squad.add_edge("managed_by", "@a5l/persona-chief-architect")
    ca_squad.add_edge("requires", "@a5l/principle-recursive-improvement")
    kg.add_atom(ca_squad)
    ca_squad.save()
    squads.append(ca_squad)
    print(f"  ✅ {ca_squad.content['name']} - {len(ca_squad.content['members'])}名成员")
    
    # ========================================
    # 2. CIO - 投资决策小队
    # ========================================
    print("\n📦 创建 CIO-投资决策小队...")
    
    cio_squad_1 = PrimeAtom(
        id="@a5l/squad-cio-001",
        kind="squad",
        version="2.1.0",
        domain="investment-analysis"
    )
    cio_squad_1.set_content(
        name="投资决策小队",
        name_en="Investment Decision Squad",
        manager="@a5l/persona-cio",
        description="投资决策执行，策略开发与回测，风险控制",
        members=[
            {"skill": "@a5l/skill-factor-investing", "role": "队长", "expertise": "因子投资"},
            {"skill": "@a5l/skill-stock-five-steps", "role": "副队长", "expertise": "五步法分析"},
            {"skill": "@a5l/skill-yangguan-daodao", "role": "策略师", "expertise": "超短线"},
            {"skill": "@a5l/skill-buffett-value", "role": "策略师", "expertise": "价值投资"},
            {"skill": "@a5l/skill-bearish-perspective", "role": "风控师", "expertise": "空方审查"},
            {"skill": "@a5l/skill-quant-analysis", "role": "量化师", "expertise": "量化分析"}
        ],
        core_functions=["投资决策", "策略回测", "风险控制", "盈亏归因"]
    )
    cio_squad_1.add_edge("managed_by", "@a5l/persona-cio")
    cio_squad_1.add_edge("collaborates_with", "@a5l/squad-platinum-001")
    kg.add_atom(cio_squad_1)
    cio_squad_1.save()
    squads.append(cio_squad_1)
    print(f"  ✅ {cio_squad_1.content['name']} - {len(cio_squad_1.content['members'])}名成员")
    
    # 3. CIO - 市场情报小队
    print("\n📦 创建 CIO-市场情报小队...")
    
    cio_squad_2 = PrimeAtom(
        id="@a5l/squad-cio-002",
        kind="squad",
        version="2.1.0",
        domain="investment-analysis"
    )
    cio_squad_2.set_content(
        name="市场情报小队",
        name_en="Market Intel Squad",
        manager="@a5l/persona-cio",
        description="催化事件监控，新闻聚合，市场情绪分析",
        members=[
            {"skill": "@a5l/skill-catalyst-monitor-auto", "role": "队长", "expertise": "催化监控"},
            {"skill": "@a5l/skill-unified-news", "role": "副队长", "expertise": "新闻聚合"},
            {"skill": "@a5l/skill-catalyst-tier-framework", "role": "分析师", "expertise": "CTF分级"},
            {"skill": "@a5l/skill-etf-monitor", "role": "分析师", "expertise": "ETF监控"}
        ],
        core_functions=["催化监控", "新闻聚合", "市场情绪"]
    )
    cio_squad_2.add_edge("managed_by", "@a5l/persona-cio")
    kg.add_atom(cio_squad_2)
    cio_squad_2.save()
    squads.append(cio_squad_2)
    print(f"  ✅ {cio_squad_2.content['name']} - {len(cio_squad_2.content['members'])}名成员")
    
    # ========================================
    # 4. COO - 运营协调小队
    # ========================================
    print("\n📦 创建 COO-运营协调小队...")
    
    coo_squad_1 = PrimeAtom(
        id="@a5l/squad-coo-001",
        kind="squad",
        version="2.1.0",
        domain="a5l-core"
    )
    coo_squad_1.set_content(
        name="运营协调小队",
        name_en="Operations Coordination Squad",
        manager="@a5l/persona-coo",
        description="SKILL自动组队，任务调度，日常运营维护",
        members=[
            {"skill": "@a5l/skill-orchestrator-engine", "role": "队长", "expertise": "协调引擎"},
            {"skill": "@a5l/skill-planner", "role": "副队长", "expertise": "规划系统"},
            {"skill": "@a5l/skill-auto-briefing", "role": "调度员", "expertise": "自动简报"},
            {"skill": "@a5l/skill-claw-daily-sync", "role": "调度员", "expertise": "日常同步"}
        ],
        core_functions=["SKILL组队", "任务调度", "日常运营", "资源协调"]
    )
    coo_squad_1.add_edge("managed_by", "@a5l/persona-coo")
    kg.add_atom(coo_squad_1)
    coo_squad_1.save()
    squads.append(coo_squad_1)
    print(f"  ✅ {coo_squad_1.content['name']} - {len(coo_squad_1.content['members'])}名成员")
    
    # 5. COO - 系统维护小队
    print("\n📦 创建 COO-系统维护小队...")
    
    coo_squad_2 = PrimeAtom(
        id="@a5l/squad-coo-002",
        kind="squad",
        version="2.1.0",
        domain="a5l-core"
    )
    coo_squad_2.set_content(
        name="系统维护小队",
        name_en="System Maintenance Squad",
        manager="@a5l/persona-coo",
        description="系统安全检查，异常恢复，安全护栏",
        members=[
            {"skill": "@a5l/skill-healthcheck", "role": "队长", "expertise": "安全检查"},
            {"skill": "@a5l/skill-resilience-recovery", "role": "工程师", "expertise": "异常恢复"},
            {"skill": "@a5l/skill-guardrails-system", "role": "工程师", "expertise": "安全护栏"}
        ],
        core_functions=["安全检查", "异常恢复", "合规检查"]
    )
    coo_squad_2.add_edge("managed_by", "@a5l/persona-coo")
    kg.add_atom(coo_squad_2)
    coo_squad_2.save()
    squads.append(coo_squad_2)
    print(f"  ✅ {coo_squad_2.content['name']} - {len(coo_squad_2.content['members'])}名成员")
    
    # ========================================
    # 6. CSO - 安全风控小队
    # ========================================
    print("\n📦 创建 CSO-安全风控小队...")
    
    cso_squad = PrimeAtom(
        id="@a5l/squad-cso-001",
        kind="squad",
        version="2.1.0",
        domain="risk-control"
    )
    cso_squad.set_content(
        name="安全风控小队",
        name_en="Security & Risk Squad",
        manager="@a5l/persona-cso",
        description="风险识别与控制，安全合规检查，黑天鹅应对",
        members=[
            {"skill": "@a5l/skill-black-swan-control", "role": "队长", "expertise": "黑天鹅控制"},
            {"skill": "@a5l/skill-bearish-perspective", "role": "副队长", "expertise": "空方审查"},
            {"skill": "@a5l/skill-data-integrity", "role": "审计员", "expertise": "数据完整性"},
            {"skill": "@a5l/skill-validation-metrics", "role": "审计员", "expertise": "验证指标"},
            {"skill": "@a5l/skill-guardrails-system", "role": "合规官", "expertise": "合规检查"}
        ],
        core_functions=["风险控制", "安全合规", "数据验证", "黑天鹅应对"]
    )
    cso_squad.add_edge("managed_by", "@a5l/persona-cso")
    cso_squad.add_edge("validates_with", "@a5l/squad-cio-001")
    kg.add_atom(cso_squad)
    cso_squad.save()
    squads.append(cso_squad)
    print(f"  ✅ {cso_squad.content['name']} - {len(cso_squad.content['members'])}名成员")
    
    # ========================================
    # 7. KG - 知识管理小队
    # ========================================
    print("\n📦 创建 KG-知识管理小队...")
    
    kg_squad_1 = PrimeAtom(
        id="@a5l/squad-kg-001",
        kind="squad",
        version="2.1.0",
        domain="memory-system"
    )
    kg_squad_1.set_content(
        name="知识管理小队",
        name_en="Knowledge Management Squad",
        manager="@a5l/persona-kg",
        description="知识图谱维护，研报管理，记忆系统，信息检索",
        members=[
            {"skill": "@a5l/skill-knowledge-graph", "role": "队长", "expertise": "知识图谱"},
            {"skill": "@a5l/skill-knowledge-guardian", "role": "副队长", "expertise": "知识守护"},
            {"skill": "@a5l/skill-report-manager", "role": "图书管理员", "expertise": "研报管理"},
            {"skill": "@a5l/skill-memory-palace", "role": "档案员", "expertise": "记忆系统"},
            {"skill": "@a5l/skill-exa-web-search", "role": "研究员", "expertise": "Exa搜索"},
            {"skill": "@a5l/skill-tavily", "role": "研究员", "expertise": "Tavily搜索"}
        ],
        core_functions=["知识图谱", "研报管理", "记忆系统", "信息检索"]
    )
    kg_squad_1.add_edge("managed_by", "@a5l/persona-kg")
    kg.add_atom(kg_squad_1)
    kg_squad_1.save()
    squads.append(kg_squad_1)
    print(f"  ✅ {kg_squad_1.content['name']} - {len(kg_squad_1.content['members'])}名成员")
    
    # 8. KG - 产业研究小队
    print("\n📦 创建 KG-产业研究小队...")
    
    kg_squad_2 = PrimeAtom(
        id="@a5l/squad-kg-002",
        kind="squad",
        version="2.1.0",
        domain="ai-industry"
    )
    kg_squad_2.set_content(
        name="产业研究小队",
        name_en="Industry Research Squad",
        manager="@a5l/persona-kg",
        description="AI产业链，具身智能，液冷，存储芯片，新材料，低空经济",
        members=[
            {"skill": "@a5l/skill-ai-llm", "role": "队长", "expertise": "AI大模型"},
            {"skill": "@a5l/skill-embodied-ai", "role": "分析师", "expertise": "具身智能"},
            {"skill": "@a5l/skill-liquid-cooling", "role": "分析师", "expertise": "液冷"},
            {"skill": "@a5l/skill-storage", "role": "分析师", "expertise": "存储芯片"},
            {"skill": "@a5l/skill-material", "role": "分析师", "expertise": "新材料"},
            {"skill": "@a5l/skill-low-altitude", "role": "分析师", "expertise": "低空经济"}
        ],
        core_functions=["产业研究", "产业链分析", "技术趋势"]
    )
    kg_squad_2.add_edge("managed_by", "@a5l/persona-kg")
    kg.add_atom(kg_squad_2)
    kg_squad_2.save()
    squads.append(kg_squad_2)
    print(f"  ✅ {kg_squad_2.content['name']} - {len(kg_squad_2.content['members'])}名成员")
    
    # ========================================
    # 9. RM - 报告生成小队
    # ========================================
    print("\n📦 创建 RM-报告生成小队...")
    
    rm_squad = PrimeAtom(
        id="@a5l/squad-rm-001",
        kind="squad",
        version="2.1.0",
        domain="a5l-core"
    )
    rm_squad.set_content(
        name="报告生成小队",
        name_en="Report Generation Squad",
        manager="@a5l/persona-report-manager",
        description="报告撰写与编辑，内容质量审查，可视化呈现",
        members=[
            {"skill": "@a5l/skill-reading-analysis", "role": "队长", "expertise": "阅读分析"},
            {"skill": "@a5l/skill-humanizer-zh", "role": "副队长", "expertise": "文本优化"},
            {"skill": "@a5l/skill-critical-thinking", "role": "编辑", "expertise": "批判审查"},
            {"skill": "@a5l/skill-canvas", "role": "设计师", "expertise": "可视化"},
            {"skill": "@a5l/skill-coze-asr", "role": "翻译", "expertise": "语音转写"}
        ],
        core_functions=["报告撰写", "质量审查", "可视化", "多语言"]
    )
    rm_squad.add_edge("managed_by", "@a5l/persona-report-manager")
    kg.add_atom(rm_squad)
    rm_squad.save()
    squads.append(rm_squad)
    print(f"  ✅ {rm_squad.content['name']} - {len(rm_squad.content['members'])}名成员")
    
    # ========================================
    # 10. 白金分析师小队 (跨领域精英)
    # ========================================
    print("\n📦 创建 白金分析师小队...")
    
    platinum_squad = PrimeAtom(
        id="@a5l/squad-platinum-001",
        kind="squad",
        version="2.1.0",
        domain="investment-analysis"
    )
    platinum_squad.set_content(
        name="白金分析师小队",
        name_en="Platinum Analyst Squad",
        manager="@a5l/persona-chief-architect",  # 直接对Chief汇报
        description="跨领域深度分析，重大投资决策支持，白金方法论v4.0应用",
        members=[
            {"skill": "@a5l/skill-private-banker-stock", "role": "队长", "expertise": "私行级分析"},
            {"skill": "@a5l/skill-uzi-integration", "role": "副队长", "expertise": "51评委打分"},
            {"skill": "@a5l/skill-value-cell", "role": "策略师", "expertise": "VALUE分析"},
            {"skill": "@a5l/skill-industry-chain", "role": "分析师", "expertise": "产业链"},
            {"skill": "@a5l/skill-bearish-perspective", "role": "风控师", "expertise": "空方审查"},
            {"skill": "@a5l/skill-unified-backtest", "role": "量化师", "expertise": "回测引擎"}
        ],
        core_functions=["深度分析", "决策支持", "综合评估", "方法论应用"],
        special_attribute="跨管理者调用，直接对Chief汇报"
    )
    platinum_squad.add_edge("reports_to", "@a5l/persona-chief-architect")
    platinum_squad.add_edge("collaborates_with", "@a5l/squad-cio-001")
    platinum_squad.add_edge("collaborates_with", "@a5l/squad-kg-002")
    kg.add_atom(platinum_squad)
    platinum_squad.save()
    squads.append(platinum_squad)
    print(f"  ✅ {platinum_squad.content['name']} - {len(platinum_squad.content['members'])}名成员 [⭐精英小队]")
    
    # ========================================
    # 生成编队报告
    # ========================================
    print("\n" + "="*70)
    print("📊 SKILL小队编队完成")
    print("="*70)
    
    total_members = sum(len(s.content.get("members", [])) for s in squads)
    
    print(f"\n总编队统计:")
    print(f"  • 小队数量: {len(squads)}支")
    print(f"  • SKILL成员: {total_members}个")
    print(f"  • 平均每队: {total_members/len(squads):.1f}个SKILL")
    
    print(f"\n编队分布:")
    for squad in squads:
        manager = squad.content.get("manager", "unknown").split("-")[-1].upper()
        name = squad.content.get("name", "")
        members = len(squad.content.get("members", []))
        print(f"  • [{manager}] {name}: {members}人")
    
    # 保存编队注册表
    registry = {
        "version": "2.1.0",
        "total_squads": len(squads),
        "total_members": total_members,
        "squads": [s.to_dict() for s in squads],
        "managers": {
            "CA": ["@a5l/squad-ca-001"],
            "CIO": ["@a5l/squad-cio-001", "@a5l/squad-cio-002"],
            "COO": ["@a5l/squad-coo-001", "@a5l/squad-coo-002"],
            "CSO": ["@a5l/squad-cso-001"],
            "KG": ["@a5l/squad-kg-001", "@a5l/squad-kg-002"],
            "RM": ["@a5l/squad-rm-001"],
            "PLATINUM": ["@a5l/squad-platinum-001"]
        },
        "timestamp": datetime.now().isoformat()
    }
    
    registry_path = "/workspace/projects/workspace/prime-atoms/squad-registry.json"
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 编队注册表: {registry_path}")
    print(f"\n✅ 所有SKILL小队编队完成！")
    
    return squads


if __name__ == "__main__":
    create_skill_squads()
