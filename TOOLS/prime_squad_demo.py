#!/usr/bin/env python3
"""
SKILL小队完整调用演示
展示六管理者SKILL小队的实际工作流程
"""

import json
import sys
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, '/workspace/projects/workspace/TOOLS')
from prime_poc import PrimeAtom, A5LKnowledgeGraph
from prime_six_in_one_hub import SixInOneHubPrime
from prime_automated_recorder import AutomatedDecisionRecorder


class SkillSquadDispatcher:
    """SKILL小队调度器 - 自动组队与调用"""
    
    def __init__(self):
        self.kg = A5LKnowledgeGraph()
        self.hub = SixInOneHubPrime(self.kg)
        self.recorder = AutomatedDecisionRecorder(self.kg)
        
        # 加载所有小队
        self.squads = self._load_squads()
        
    def _load_squads(self) -> Dict[str, PrimeAtom]:
        """加载所有SKILL小队"""
        squads = {}
        squad_ids = [
            "@a5l/squad-ca-001",      # 核心架构
            "@a5l/squad-cio-001",     # 投资决策
            "@a5l/squad-cio-002",     # 市场情报
            "@a5l/squad-coo-001",     # 运营协调
            "@a5l/squad-coo-002",     # 系统维护
            "@a5l/squad-cso-001",     # 安全风控
            "@a5l/squad-kg-001",      # 知识管理
            "@a5l/squad-kg-002",      # 产业研究
            "@a5l/squad-rm-001",      # 报告生成
            "@a5l/squad-platinum-001" # 白金分析师
        ]
        
        for squad_id in squad_ids:
            atom = self.kg.get_atom(squad_id)
            if atom:
                squads[squad_id] = atom
        
        return squads
    
    def form_squad(self, scenario: str) -> List[PrimeAtom]:
        """根据场景自动组队"""
        
        scenario_squads = {
            "买入决策": [
                "@a5l/squad-cio-002",      # 市场情报 (催化剂/新闻)
                "@a5l/squad-cio-001",      # 投资决策 (策略分析)
                "@a5l/squad-cso-001",      # 安全风控 (风险评估)
                "@a5l/squad-platinum-001"  # 白金分析师 (深度分析)
            ],
            "每日复盘": [
                "@a5l/squad-coo-001",      # 运营协调 (简报生成)
                "@a5l/squad-kg-001",       # 知识管理 (信息检索)
                "@a5l/squad-rm-001"        # 报告生成 (报告撰写)
            ],
            "产业研究": [
                "@a5l/squad-kg-002",       # 产业研究 (产业链)
                "@a5l/squad-platinum-001", # 白金分析师 (深度分析)
                "@a5l/squad-kg-001"        # 知识管理 (知识图谱)
            ],
            "系统检查": [
                "@a5l/squad-coo-002",      # 系统维护
                "@a5l/squad-cso-001",      # 安全风控
                "@a5l/squad-ca-001"        # 核心架构
            ],
            "紧急决策": [
                "@a5l/squad-platinum-001", # 白金分析师 (快速深度分析)
                "@a5l/squad-cio-001",      # 投资决策
                "@a5l/squad-cso-001"       # 安全风控
            ]
        }
        
        squad_ids = scenario_squads.get(scenario, ["@a5l/squad-platinum-001"])
        return [self.squads.get(sid) for sid in squad_ids if sid in self.squads]
    
    def dispatch_squads(self, scenario: str, task_details: Dict) -> Dict:
        """调度SKILL小队执行任务"""
        
        print(f"\n{'='*70}")
        print(f"🚀 场景: {scenario}")
        print(f"{'='*70}")
        
        # 1. 自动组队
        print(f"\n📋 Step 1: 自动组队")
        squads = self.form_squad(scenario)
        print(f"  根据场景'{scenario}'组建特遣队:")
        for i, squad in enumerate(squads, 1):
            if squad:
                print(f"    {i}. {squad.content.get('name')} ({len(squad.content.get('members', []))}人)")
        
        # 2. 六管理者共识
        print(f"\n📋 Step 2: 六管理者共识")
        
        # 收集各管理者意见
        consensus = {}
        for persona_id, persona in self.hub.managers.items():
            # 根据场景生成模拟意见
            opinion = self._generate_opinion(persona_id, scenario, task_details)
            consensus[persona_id] = opinion
            print(f"  ✅ {persona.content.get('name')}: {opinion[:40]}...")
        
        # 创建共识决策
        decision = self.hub.create_consensus_decision(
            decision_type="skill_squad_dispatch",
            description=f"{scenario} - SKILL小队调度",
            consensus=consensus,
            final_decision=f"执行{scenario}，调用{len(squads)}支小队",
            confidence=0.88
        )
        
        # 3. 小队执行
        print(f"\n📋 Step 3: 小队执行")
        execution_results = []
        
        for squad in squads:
            if squad:
                result = self._execute_squad_tasks(squad, scenario, task_details)
                execution_results.append(result)
                print(f"  ✅ {squad.content.get('name')} 完成")
                print(f"     执行了 {len(result['tasks'])} 个任务")
        
        # 4. 记录决策
        print(f"\n📋 Step 4: 自动记录")
        
        record = self.recorder.record_trading_decision(
            action="ANALYSIS",
            symbol=task_details.get("symbol", "UNKNOWN"),
            name=task_details.get("name", "未知"),
            quantity=0,
            price=0,
            reasoning=f"{scenario}分析，调用{len(squads)}支SKILL小队",
            signals=[f"squad-{squad.id.split('-')[-1]}" for squad in squads if squad],
            confidence=0.88
        )
        
        print(f"  ✅ 决策已记录: {record.id}")
        
        # 5. 生成报告
        print(f"\n📋 Step 5: 生成报告")
        
        report = {
            "scenario": scenario,
            "timestamp": datetime.now().isoformat(),
            "squads_deployed": [s.content.get('name') for s in squads if s],
            "consensus_decision": decision.id,
            "execution_summary": {
                "total_squads": len(squads),
                "total_tasks": sum(len(r['tasks']) for r in execution_results),
                "record_id": record.id
            }
        }
        
        print(f"  ✅ 报告生成完成")
        print(f"     部署小队: {len(squads)}支")
        print(f"     执行任务: {report['execution_summary']['total_tasks']}个")
        
        return report
    
    def _generate_opinion(self, persona_id: str, scenario: str, details: Dict) -> str:
        """生成管理者意见"""
        
        opinions = {
            "@a5l/persona-chief-architect": f"系统架构支持{scenario}，建议调用Prime集成SKILL",
            "@a5l/persona-cio": f"投资决策层面{scenario}可行，需关注风险控制",
            "@a5l/persona-coo": f"运营资源充足，可调度{details.get('symbol', '该标的')}分析小队",
            "@a5l/persona-cso": f"风险评估完成，{scenario}风险可控，建议执行",
            "@a5l/persona-kg": f"知识库已准备好{scenario}相关资料，支持执行",
            "@a5l/persona-report-manager": f"报告模板就绪，可生成{scenario}分析报告"
        }
        
        return opinions.get(persona_id, "同意执行")
    
    def _execute_squad_tasks(self, squad: PrimeAtom, scenario: str, details: Dict) -> Dict:
        """执行小队任务"""
        
        members = squad.content.get("members", [])
        tasks = []
        
        # 根据小队类型生成任务
        if "投资决策" in squad.content.get("name", ""):
            tasks = [
                "技术指标分析 (factor-investing)",
                "五步法深度分析 (stock-five-steps)",
                "风险评估 (bearish-perspective)",
                "量化验证 (quant-analysis)"
            ]
        elif "市场情报" in squad.content.get("name", ""):
            tasks = [
                "催化事件扫描 (catalyst-monitor)",
                "新闻聚合分析 (unified-news)",
                "CTF分级评估 (catalyst-tier)",
                "ETF资金流向 (etf-monitor)"
            ]
        elif "白金分析师" in squad.content.get("name", ""):
            tasks = [
                "私行级深度分析 (private-banker)",
                "51评委多维打分 (uzi-integration)",
                "VALUE五维分析 (value-cell)",
                "产业链验证 (industry-chain)",
                "回测验证 (unified-backtest)"
            ]
        elif "安全风控" in squad.content.get("name", ""):
            tasks = [
                "黑天鹅风险扫描 (black-swan)",
                "空方视角审查 (bearish-perspective)",
                "数据完整性检查 (data-integrity)",
                "合规性验证 (guardrails)"
            ]
        elif "知识管理" in squad.content.get("name", ""):
            tasks = [
                "知识图谱查询 (knowledge-graph)",
                "历史案例检索 (knowledge-guardian)",
                "研报归档整理 (report-manager)",
                "记忆系统调用 (memory-palace)"
            ]
        elif "产业研究" in squad.content.get("name", ""):
            tasks = [
                "AI产业链分析 (ai-llm)",
                "技术趋势研究 (embodied-ai)",
                "供应链验证 (liquid-cooling/storage/material)",
                "竞争格局分析 (low-altitude)"
            ]
        else:
            tasks = [f"执行{squad.content.get('name')}标准任务"]
        
        return {
            "squad": squad.id,
            "squad_name": squad.content.get("name"),
            "tasks": tasks,
            "members_count": len(members)
        }


def demo_scenario_1_buy_decision():
    """场景1: 买入决策 - 中国长城"""
    
    print("\n" + "="*70)
    print("🎬 演示场景1: 买入决策 - 中国长城 (000066.SZ)")
    print("="*70)
    
    dispatcher = SkillSquadDispatcher()
    
    task = {
        "symbol": "000066.SZ",
        "name": "中国长城",
        "action": "BUY",
        "context": "4连板后技术突破，信创催化剂"
    }
    
    result = dispatcher.dispatch_squads("买入决策", task)
    
    return result


def demo_scenario_2_daily_review():
    """场景2: 每日复盘"""
    
    print("\n" + "="*70)
    print("🎬 演示场景2: 每日复盘 - 2026-05-11")
    print("="*70)
    
    dispatcher = SkillSquadDispatcher()
    
    task = {
        "date": "2026-05-11",
        "context": "生成今日交易复盘报告"
    }
    
    result = dispatcher.dispatch_squads("每日复盘", task)
    
    return result


def demo_scenario_3_industry_research():
    """场景3: 产业研究 - AI算力"""
    
    print("\n" + "="*70)
    print("🎬 演示场景3: 产业研究 - AI算力产业链")
    print("="*70)
    
    dispatcher = SkillSquadDispatcher()
    
    task = {
        "sector": "AI算力",
        "focus": "CPO/光模块/液冷",
        "context": "深度研究AI基础设施产业链"
    }
    
    result = dispatcher.dispatch_squads("产业研究", task)
    
    return result


def demo_scenario_4_system_check():
    """场景4: 系统安全检查"""
    
    print("\n" + "="*70)
    print("🎬 演示场景4: 系统安全检查")
    print("="*70)
    
    dispatcher = SkillSquadDispatcher()
    
    task = {
        "type": "security_audit",
        "context": "定期系统安全检查"
    }
    
    result = dispatcher.dispatch_squads("系统检查", task)
    
    return result


def main():
    """主函数 - 运行所有演示"""
    
    print("="*70)
    print("🚀 SKILL小队完整调用演示")
    print("   展示六管理者SKILL小队的实际工作流程")
    print("="*70)
    
    results = []
    
    # 场景1: 买入决策
    results.append(("买入决策", demo_scenario_1_buy_decision()))
    
    # 场景2: 每日复盘
    results.append(("每日复盘", demo_scenario_2_daily_review()))
    
    # 场景3: 产业研究
    results.append(("产业研究", demo_scenario_3_industry_research()))
    
    # 场景4: 系统检查
    results.append(("系统检查", demo_scenario_4_system_check()))
    
    # 汇总报告
    print("\n" + "="*70)
    print("📊 演示总结")
    print("="*70)
    
    for scenario, result in results:
        print(f"\n{scenario}:")
        print(f"  部署小队: {', '.join(result['squads_deployed'])}")
        print(f"  执行任务: {result['execution_summary']['total_tasks']}个")
        print(f"  决策记录: {result['execution_summary']['record_id']}")
    
    print("\n" + "="*70)
    print("✅ 所有演示完成！SKILL小队调用流程已完整展示。")
    print("="*70)


if __name__ == "__main__":
    main()
