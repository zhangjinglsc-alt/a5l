#!/usr/bin/env python3
"""
A5L-Prime 决策溯源系统演示
展示Prime最重要的应用场景：为什么做出某个决策
"""

import json
from datetime import datetime
from pathlib import Path
from prime_poc import PrimeAtom, A5LKnowledgeGraph


def create_buy_decision_atom():
    """
    创建"买入中国长城"决策的原子记录
    这是Prime最核心价值：决策溯源
    """
    
    decision = PrimeAtom(
        id="@a5l/decision-buy-cgw-20260506",
        kind="decision",
        version="1.0.0",
        domain="trading"
    )
    
    # 决策内容
    decision.set_content(
        action="BUY",
        symbol="000066.SZ",
        name="中国长城",
        quantity=48000,
        price=16.86,
        total_value=809280,
        decision_time="2026-05-06T09:35:00+08:00",
        confidence=0.85,
        rationale="信创主线+4连板突破+集中持股策略"
    )
    
    # 决策来源（关键！这是Prime的核心）
    # 说明这个决策是基于哪些分析和信号做出的
    decision.add_edge("derived_from", "@a5l/analysis-catalyst-tier-2")
    decision.add_edge("derived_from", "@a5l/signal-breakout-4consecutive")
    decision.add_edge("derived_from", "@a5l/analysis-industry-chain-cpu")
    decision.add_edge("derived_from", "@a5l/signal-volume-expansion")
    
    # 使用的SKILL
    decision.add_edge("requires", "@a5l/skill-unified-stock-price")
    decision.add_edge("requires", "@a5l/skill-catalyst-tier-framework")
    decision.add_edge("requires", "@a5l/skill-industry-research")
    decision.add_edge("requires", "@a5l/skill-technical-analysis")
    
    # 矛盾/风险点（重要！）
    decision.add_edge("contradicts", "@a5l/principle-diversification")
    decision.add_edge("contradicts", "@a5l/risk-concentration-limit")
    
    # 相关决策
    decision.add_edge("related", "@a5l/decision-sell-xingesen-20260506")
    decision.add_edge("related", "@a5l/decision-sell-jucan-20260506")
    
    # 验证
    decision.add_edge("validates_with", "@a5l/position-cgw-20260509")
    decision.add_edge("validates_with", "@a5l/pnl-cgw-plus42pct")
    
    return decision


def create_analysis_catalyst_atom():
    """创建催化剂分析原子"""
    analysis = PrimeAtom(
        id="@a5l/analysis-catalyst-tier-2",
        kind="analysis",
        version="1.0.0",
        domain="investment-analysis"
    )
    
    analysis.set_content(
        type="catalyst_tier_framework",
        target="中国长城",
        catalyst_tier="Tier 2 - 周期确认级",
        description="信创政策催化+国产CPU自主可控+华为鸿蒙生态",
        confidence=0.82,
        analysis_time="2026-05-05"
    )
    
    analysis.add_edge("requires", "@a5l/skill-catalyst-tier-framework")
    analysis.add_edge("requires", "@a5l/data-news-aggregator")
    analysis.add_edge("enhances", "@a5l/decision-buy-cgw-20260506")
    
    return analysis


def create_signal_breakout_atom():
    """创建突破信号原子"""
    signal = PrimeAtom(
        id="@a5l/signal-breakout-4consecutive",
        kind="signal",
        version="1.0.0",
        domain="trading"
    )
    
    signal.set_content(
        type="price_action",
        pattern="4_consecutive_limit_up",
        target="000066.SZ",
        entry_price=16.86,
        signal_strength=0.90,
        detected_at="2026-05-06T09:25:00+08:00"
    )
    
    signal.add_edge("requires", "@a5l/skill-technical-analysis")
    signal.add_edge("requires", "@a5l/skill-yangguan-daodao")
    signal.add_edge("enhances", "@a5l/decision-buy-cgw-20260506")
    
    return signal


def demonstrate_traceability():
    """演示决策溯源能力"""
    
    print("="*70)
    print("🔍 A5L-Prime 决策溯源演示")
    print("="*70)
    
    # 创建知识图谱
    kg = A5LKnowledgeGraph()
    
    # 创建决策和相关原子
    print("\n📦 创建决策原子...")
    
    decision = create_buy_decision_atom()
    kg.add_atom(decision)
    decision.save()
    print(f"  ✅ {decision.id}")
    
    analysis = create_analysis_catalyst_atom()
    kg.add_atom(analysis)
    analysis.save()
    print(f"  ✅ {analysis.id}")
    
    signal = create_signal_breakout_atom()
    kg.add_atom(signal)
    signal.save()
    print(f"  ✅ {signal.id}")
    
    # 重建索引
    kg.build_index()
    
    # 演示溯源查询
    print("\n" + "="*70)
    print("📊 决策溯源查询")
    print("="*70)
    
    print(f"\n决策: 买入中国长城 (2026-05-06)")
    print(f"  代码: {decision.content['symbol']}")
    print(f"  数量: {decision.content['quantity']}股")
    print(f"  价格: ¥{decision.content['price']}")
    print(f"  置信度: {decision.content['confidence']*100:.0f}%")
    
    print(f"\n  📚 决策来源（为什么买）:")
    for source in decision.edges.get("derived_from", []):
        atom = kg.get_atom(source)
        if atom:
            print(f"    → {source}")
            print(f"      {atom.content.get('description', '')[:60]}...")
    
    print(f"\n  ⚠️  风险/矛盾点:")
    for contra in decision.edges.get("contradicts", []):
        print(f"    ! {contra}")
    
    print(f"\n  🔧 使用的SKILL:")
    for skill in decision.edges.get("requires", [])[:4]:
        print(f"    • {skill}")
    
    print(f"\n  📈 验证结果:")
    for valid in decision.edges.get("validates_with", []):
        print(f"    ✓ {valid}")
    
    # 反向查询：哪些决策使用了催化剂分析SKILL？
    print("\n" + "="*70)
    print("🔄 反向溯源查询")
    print("="*70)
    
    dependents = kg.get_dependents("@a5l/analysis-catalyst-tier-2")
    print(f"\n使用 '催化剂分析' 的决策:")
    for dep in dependents:
        atom = kg.get_atom(dep)
        if atom and atom.kind == "decision":
            print(f"  • {dep}")
            print(f"    动作: {atom.content.get('action')} {atom.content.get('symbol')}")
    
    # 生成决策报告
    print("\n" + "="*70)
    print("📄 生成决策溯源报告")
    print("="*70)
    
    report = {
        "decision_id": decision.id,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "action": decision.content["action"],
            "target": decision.content["symbol"],
            "confidence": decision.content["confidence"],
            "sources_count": len(decision.edges.get("derived_from", [])),
            "risks_count": len(decision.edges.get("contradicts", [])),
        },
        "sources": decision.edges.get("derived_from", []),
        "risks": decision.edges.get("contradicts", []),
        "skills_used": decision.edges.get("requires", []),
        "validation": decision.edges.get("validates_with", [])
    }
    
    report_path = Path("/workspace/projects/workspace/prime-atoms/decision-report-cgw.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n报告已保存: {report_path}")
    
    print("\n" + "="*70)
    print("✅ 决策溯源演示完成！")
    print("="*70)
    print("\n核心价值:")
    print("  1. 任何决策都可追溯到源头分析")
    print("  2. 矛盾点和风险被显式记录")
    print("  3. 验证结果与决策关联")
    print("  4. 支持反向查询（哪些决策用了某SKILL）")
    print("\n应用场景:")
    print("  • 复盘时理解当时的决策逻辑")
    print("  • 审计决策过程是否合规")
    print("  • 优化SKILL使用效率")
    print("  • 知识传承和经验积累")


if __name__ == "__main__":
    demonstrate_traceability()
