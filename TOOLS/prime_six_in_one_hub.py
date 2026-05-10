#!/usr/bin/env python3
"""
A5L-Prime 六管理者Hub集成
将Layer 0 Six-in-One Hub接入Prime知识图谱协议
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from prime_poc import PrimeAtom, A5LKnowledgeGraph


class SixInOneHubPrime:
    """
    六管理者Hub的Prime协议实现
    每个管理者作为一个Persona Atom
    决策过程全程记录为Decision Atom
    """
    
    def __init__(self, kg: A5LKnowledgeGraph):
        self.kg = kg
        self.managers = {}
        self._create_manager_personas()
    
    def _create_manager_personas(self):
        """创建六管理者Persona"""
        
        managers_config = [
            {
                "id": "@a5l/persona-chief-architect",
                "name": "Chief Architect (CA)",
                "role": "系统总设计师",
                "responsibilities": ["架构设计", "技术决策", "标准制定"],
                "domain": "a5l-core",
                "principles": ["HONESTY_ABOVE_ALL", "VERIFICATION_MANDATE", "RECURSIVE_IMPROVEMENT"]
            },
            {
                "id": "@a5l/persona-cio",
                "name": "Chief Investment Officer (CIO)",
                "role": "首席投资官",
                "responsibilities": ["投资决策", "策略执行", "盈亏管理"],
                "domain": "investment-analysis",
                "principles": ["RISK_ADJUSTED_RETURNS", "BEARISH_PERSPECTIVE", "VALUE_CELL_FRAMEWORK"]
            },
            {
                "id": "@a5l/persona-coo",
                "name": "Chief Operating Officer (COO)",
                "role": "首席运营官",
                "responsibilities": ["资源协调", "任务分配", "进度管理"],
                "domain": "a5l-core",
                "principles": ["EFFICIENCY", "RESOURCE_OPTIMIZATION", "CROSS_MARKET_COORDINATION"]
            },
            {
                "id": "@a5l/persona-cso",
                "name": "Chief Security Officer (CSO)",
                "role": "首席安全官",
                "responsibilities": ["风险审查", "合规检查", "安全审计"],
                "domain": "risk-control",
                "principles": ["RED_LINE_ENFORCEMENT", "NO_EXFILTRATION", "DESTRUCTIVE_COMMAND_CHECK"]
            },
            {
                "id": "@a5l/persona-kg",
                "name": "Knowledge Guardian (KG)",
                "role": "知识守护者",
                "responsibilities": ["知识管理", "文档归档", "信息检索"],
                "domain": "memory-system",
                "principles": ["CHIEF_LIBRARIAN", "ORGANIZED_MEMORY", "TRACEABILITY"]
            },
            {
                "id": "@a5l/persona-report-manager",
                "name": "Report Manager (RM)",
                "role": "研报管理",
                "responsibilities": ["研报整理", "研究归档", "报告生成"],
                "domain": "investment-analysis",
                "principles": ["SYSTEMATIC_CLASSIFICATION", "VERSION_CONTROL", "QUICK_RETRIEVAL"]
            }
        ]
        
        for config in managers_config:
            persona = PrimeAtom(
                id=config["id"],
                kind="persona",
                version="2.1.0",
                domain=config["domain"]
            )
            
            persona.set_content(
                name=config["name"],
                role=config["role"],
                responsibilities=config["responsibilities"],
                principles=config["principles"]
            )
            
            # 管理者间协作关系
            for other in managers_config:
                if other["id"] != config["id"]:
                    persona.add_edge("collaborates_with", other["id"])
            
            self.kg.add_atom(persona)
            persona.save()
            self.managers[config["id"]] = persona
            
            print(f"  ✅ {config['name']}")
    
    def create_consensus_decision(self, 
                                   decision_type: str,
                                   description: str,
                                   consensus: Dict[str, str],
                                   final_decision: str,
                                   confidence: float = 0.8) -> PrimeAtom:
        """
        记录六管理者共识决策
        
        Args:
            decision_type: 决策类型 (investment/strategy/operation)
            description: 决策描述
            consensus: 各管理者意见 {manager_id: opinion}
            final_decision: 最终决策
            confidence: 共识置信度
        """
        
        decision_id = f"@a5l/decision-consensus-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        decision = PrimeAtom(
            id=decision_id,
            kind="decision",
            version="1.0.0",
            domain="a5l-core"
        )
        
        decision.set_content(
            type="six_in_one_consensus",
            decision_type=decision_type,
            description=description,
            final_decision=final_decision,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )
        
        # 记录各管理者意见
        for manager_id, opinion in consensus.items():
            decision.add_edge("contributed_by", manager_id)
            # 创建意见原子
            opinion_atom = PrimeAtom(
                id=f"{decision_id}-opinion-{manager_id.split('-')[-1]}",
                kind="opinion",
                version="1.0.0",
                domain="a5l-core"
            )
            opinion_atom.set_content(
                manager=manager_id,
                opinion=opinion,
                decision_id=decision_id
            )
            opinion_atom.add_edge("contributes_to", decision_id)
            opinion_atom.save()
        
        # 验证关系
        decision.add_edge("validates_with", "@a5l/principle-recursive-improvement")
        
        self.kg.add_atom(decision)
        decision.save()
        
        return decision
    
    def get_manager_history(self, manager_id: str) -> List[PrimeAtom]:
        """获取某管理者的所有决策历史"""
        history = []
        for atom_id, atom in self.kg.atoms.items():
            if atom.kind == "decision" and manager_id in atom.edges.get("contributed_by", []):
                history.append(atom)
        return sorted(history, key=lambda x: x.content.get("timestamp", ""))
    
    def get_decision_trace(self, decision_id: str) -> Dict:
        """获取决策的完整溯源链"""
        decision = self.kg.get_atom(decision_id)
        if not decision:
            return {}
        
        trace = {
            "decision": decision.to_dict(),
            "contributors": [],
            "opinions": [],
            "related_decisions": []
        }
        
        # 获取各管理者意见
        for contributor in decision.edges.get("contributed_by", []):
            persona = self.kg.get_atom(contributor)
            if persona:
                trace["contributors"].append({
                    "id": contributor,
                    "name": persona.content.get("name"),
                    "role": persona.content.get("role")
                })
            
            # 获取具体意见
            opinion_id = f"{decision_id}-opinion-{contributor.split('-')[-1]}"
            opinion = self.kg.get_atom(opinion_id)
            if opinion:
                trace["opinions"].append(opinion.to_dict())
        
        return trace


def demonstrate_six_in_one_hub():
    """演示六管理者Hub集成"""
    
    print("="*70)
    print("🚀 A5L-Prime 六管理者Hub集成演示")
    print("="*70)
    
    # 初始化知识图谱
    kg = A5LKnowledgeGraph()
    
    # 加载已迁移的SKILL
    print("\n📦 加载已迁移的74个SKILL...")
    # 这里简化处理，实际应该从文件加载
    
    # 创建六管理者Hub
    print("\n👥 创建六管理者Persona...")
    hub = SixInOneHubPrime(kg)
    
    # 演示共识决策：Prime集成决策
    print("\n📊 演示：六管理者共识决策")
    print("-"*70)
    
    consensus = {
        "@a5l/persona-chief-architect": "Prime理念先进，值得深度集成。建议分阶段实施，先POC验证。",
        "@a5l/persona-cio": "决策溯源能力对投资复盘价值巨大，支持集成。",
        "@a5l/persona-coo": "25-30天时间可控，资源可协调。注意冻结新SKILL开发。",
        "@a5l/persona-cso": "需评估Node/Python互操作安全风险，建议隔离MCP通信。",
        "@a5l/persona-kg": "知识图谱标准化长期价值显著，全力支持。",
        "@a5l/persona-report-manager": "文档和版本管理将大幅改善，支持集成。"
    }
    
    decision = hub.create_consensus_decision(
        decision_type="strategy",
        description="A5L系统Prime深度集成决策",
        consensus=consensus,
        final_decision="执行选项A：深度集成，分3个阶段，预计25-30天完成",
        confidence=0.92
    )
    
    print(f"\n决策ID: {decision.id}")
    print(f"决策类型: {decision.content['decision_type']}")
    print(f"决策描述: {decision.content['description']}")
    print(f"最终决策: {decision.content['final_decision']}")
    print(f"共识置信度: {decision.content['confidence']*100:.0f}%")
    
    print(f"\n参与者意见:")
    for manager_id, opinion in consensus.items():
        manager = hub.managers.get(manager_id)
        if manager:
            print(f"  [{manager.content['role']}]")
            print(f"    {opinion[:50]}...")
    
    # 决策溯源
    print("\n" + "="*70)
    print("🔍 决策溯源查询")
    print("="*70)
    
    trace = hub.get_decision_trace(decision.id)
    print(f"\n决策完整溯源:")
    print(f"  决策者数量: {len(trace['contributors'])}")
    print(f"  意见数量: {len(trace['opinions'])}")
    
    for contributor in trace['contributors']:
        print(f"    • {contributor['name']} ({contributor['role']})")
    
    # 保存Hub配置
    print("\n💾 保存Hub配置...")
    hub_config = {
        "version": "2.1.0-prime",
        "managers": {k: v.to_dict() for k, v in hub.managers.items()},
        "decisions": [decision.to_dict()],
        "timestamp": datetime.now().isoformat()
    }
    
    hub_path = Path("/workspace/projects/workspace/prime-atoms/six-in-one-hub.json")
    with open(hub_path, 'w') as f:
        json.dump(hub_config, f, indent=2)
    
    print(f"  配置已保存: {hub_path}")
    
    print("\n" + "="*70)
    print("✅ 六管理者Hub集成完成！")
    print("="*70)
    print("\n核心价值:")
    print("  1. 六管理者作为独立Persona，职责清晰")
    print("  2. 共识决策全程记录，可追溯可审计")
    print("  3. 决策与SKILL、分析结果关联")
    print("  4. 支持决策复盘和模式识别")


if __name__ == "__main__":
    demonstrate_six_in_one_hub()
