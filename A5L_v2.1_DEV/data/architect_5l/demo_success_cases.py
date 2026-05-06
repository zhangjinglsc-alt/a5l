#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Week 3 Demo: 成功案例演示
展示高评分提案如何通过集体决策
"""

import json
import sys
sys.path.insert(0, '/workspace/projects/workspace/data/architect_5l')

from collective_decision_engine import CollectiveDecisionEngine

def demo_success_cases():
    """演示成功案例"""
    engine = CollectiveDecisionEngine()
    
    print("=" * 70)
    print("🎯 Week 3: 集体决策系统 - 成功案例演示")
    print("=" * 70)
    
    # Case 1: 新建仓优质标的 (Super Majority通过)
    print("\n" + "=" * 70)
    print("✅ Case 1: 新建仓宁德时代 (Super Majority通过)")
    print("=" * 70)
    
    proposal1 = engine.submit_proposal({
        "type": "trade_execution",
        "title": "新建仓宁德时代",
        "description": "新能源龙头，基本面优秀，估值合理",
        "target": "300750",
        "proposed_action": "建仓10%仓位",
        "urgency": 6,
        "submitter": "CIO",
        "return_potential": 85,
        "risk_level": 35,
        "compliance_score": 90,
        "timing_score": 80
    })
    
    summary1 = engine.get_decision_summary(proposal1.id)
    print(f"\n📊 决策ID: {summary1['id']}")
    print(f"🎯 目标: {summary1['target']} - {summary1['title']}")
    print(f"📈 最终得分: {summary1['final_score']:.1f}/100")
    print(f"🤝 共识级别: {summary1['consensus_level'].upper()}")
    print(f"✅ 决策状态: {summary1['status'].upper()}")
    print("\n🗳️ 投票详情:")
    for v in summary1['votes']:
        emoji = "✅" if v['decision'] == 'approve' else "❌"
        print(f"  {emoji} {v['manager']}: {v['decision'].upper()} ({v['score']:.0f}分)")
    
    # Case 2: 紧急止损 (Unanimous通过)
    print("\n" + "=" * 70)
    print("✅ Case 2: 止盈兑现收益 (Unanimous通过)")
    print("=" * 70)
    
    proposal2 = engine.submit_proposal({
        "type": "risk_action",
        "title": "止盈兑现部分收益",
        "description": "股价达到目标价位，建议部分止盈",
        "target": "PROFIT_001",
        "proposed_action": "卖出50%持仓",
        "urgency": 8,
        "submitter": "CIO",
        "return_potential": 75,
        "risk_level": 30,
        "compliance_score": 90,
        "timing_score": 85
    })
    
    summary2 = engine.get_decision_summary(proposal2.id)
    print(f"\n📊 决策ID: {summary2['id']}")
    print(f"🎯 目标: {summary2['target']} - {summary2['title']}")
    print(f"📈 最终得分: {summary2['final_score']:.1f}/100")
    print(f"🤝 共识级别: {summary2['consensus_level'].upper()}")
    print(f"✅ 决策状态: {summary2['status'].upper()}")
    print("\n🗳️ 投票详情:")
    for v in summary2['votes']:
        emoji = "✅" if v['decision'] == 'approve' else "❌"
        print(f"  {emoji} {v['manager']}: {v['decision'].upper()} ({v['score']:.0f}分)")
    
    # Case 3: 策略微调 (Simple Majority通过)
    print("\n" + "=" * 70)
    print("✅ Case 3: 调整仓位配比 (Simple Majority通过)")
    print("=" * 70)
    
    proposal3 = engine.submit_proposal({
        "type": "position_adjustment",
        "title": "科技板块仓位微调",
        "description": "增加AI算力配置，减少传统科技",
        "target": "SECTOR_TECH",
        "proposed_action": "调整子板块配比",
        "urgency": 4,
        "submitter": "UZI",
        "return_potential": 70,
        "risk_level": 50,
        "compliance_score": 80,
        "timing_score": 65
    })
    
    summary3 = engine.get_decision_summary(proposal3.id)
    print(f"\n📊 决策ID: {summary3['id']}")
    print(f"🎯 目标: {summary3['target']} - {summary3['title']}")
    print(f"📈 最终得分: {summary3['final_score']:.1f}/100")
    print(f"🤝 共识级别: {summary3['consensus_level'].upper()}")
    print(f"✅ 决策状态: {summary3['status'].upper()}")
    print("\n🗳️ 投票详情:")
    for v in summary3['votes']:
        emoji = "✅" if v['decision'] == 'approve' else "❌"
        print(f"  {emoji} {v['manager']}: {v['decision'].upper()} ({v['score']:.0f}分)")
    
    # 统计
    print("\n" + "=" * 70)
    print("📊 演示统计")
    print("=" * 70)
    
    results = [summary1, summary2, summary3]
    approved = sum(1 for r in results if r['status'] == 'approved')
    rejected = sum(1 for r in results if r['status'] == 'rejected')
    
    print(f"\n总提案数: 3")
    print(f"✅ 通过: {approved}")
    print(f"❌ 否决: {rejected}")
    print(f"通过率: {approved/3*100:.0f}%")
    
    print("\n共识级别分布:")
    consensus_counts = {}
    for r in results:
        level = r['consensus_level']
        consensus_counts[level] = consensus_counts.get(level, 0) + 1
    
    for level, count in sorted(consensus_counts.items()):
        emoji = {"unanimous": "🥇", "super_majority": "🥈", 
                "simple_majority": "🥉", "no_consensus": "❌"}.get(level, "➖")
        print(f"  {emoji} {level}: {count}")
    
    print("\n" + "=" * 70)
    print("✨ Week 3 集体决策系统演示完成!")
    print("=" * 70)

if __name__ == "__main__":
    demo_success_cases()
