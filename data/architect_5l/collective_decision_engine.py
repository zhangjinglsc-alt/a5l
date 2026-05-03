#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Layer0 集体决策系统 v3.0
CIO + CSO + UZI 联合审批机制

核心能力:
1. 多维度提案评分 (4维度)
2. 加权投票机制
3. 共识达成判断
4. 决策执行追踪
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class DecisionType(Enum):
    TRADE_EXECUTION = "trade_execution"
    POSITION_ADJUSTMENT = "position_adjustment"
    RISK_ACTION = "risk_action"
    STRATEGY_CHANGE = "strategy_change"

class ConsensusLevel(Enum):
    UNANIMOUS = "unanimous"  # 全体一致
    SUPER_MAJORITY = "super_majority"  # 绝对多数 (75%)
    SIMPLE_MAJORITY = "simple_majority"  # 简单多数 (60%)
    NO_CONSENSUS = "no_consensus"

@dataclass
class ManagerVote:
    """管理者投票"""
    manager: str
    score: float  # 0-100
    decision: str  # approve / reject / abstain
    reasoning: str
    confidence: float  # 0-1
    timestamp: str

@dataclass
class Proposal:
    """决策提案"""
    id: str
    type: str
    title: str
    description: str
    target: str  # 股票代码/策略名称
    proposed_action: str
    urgency: int  # 1-10
    submitter: str
    submitted_at: str
    
    # 评分维度
    return_potential: float  # 收益潜力 0-100
    risk_level: float  # 风险等级 0-100 (越低越好)
    compliance_score: float  # 合规分数 0-100
    timing_score: float  # 时机分数 0-100
    
    # 投票结果
    votes: List[ManagerVote] = None
    consensus_level: str = None
    final_score: float = None
    status: str = "pending"  # pending / approved / rejected / executed
    
    def __post_init__(self):
        if self.votes is None:
            self.votes = []

class CollectiveDecisionEngine:
    """集体决策引擎"""
    
    MANAGERS = {
        "CIO": {"weight": 0.35, "threshold": 60, "focus": ["returns", "timing"]},
        "CSO": {"weight": 0.35, "threshold": 70, "focus": ["risk", "compliance"]},
        "UZI": {"weight": 0.30, "threshold": 65, "focus": ["fundamentals", "valuation"]}
    }
    
    CONSENSUS_THRESHOLDS = {
        "unanimous": 100,
        "super_majority": 75,
        "simple_majority": 60
    }
    
    def __init__(self, data_dir: str = "/workspace/projects/workspace/data/architect_5l"):
        self.data_dir = data_dir
        self.decisions_file = f"{data_dir}/decisions/decisions.json"
        self._load_decisions()
    
    def _load_decisions(self):
        """加载历史决策"""
        try:
            with open(self.decisions_file, 'r') as f:
                self.decisions = json.load(f)
        except FileNotFoundError:
            self.decisions = {"proposals": [], "executed": [], "rejected": []}
    
    def _save_decisions(self):
        """保存决策记录"""
        import os
        os.makedirs(os.path.dirname(self.decisions_file), exist_ok=True)
        with open(self.decisions_file, 'w') as f:
            json.dump(self.decisions, f, indent=2, ensure_ascii=False)
    
    def _generate_id(self, proposal: Proposal) -> str:
        """生成提案ID"""
        content = f"{proposal.type}{proposal.target}{proposal.submitter}{proposal.submitted_at}"
        return f"DEC_{hashlib.md5(content.encode()).hexdigest()[:12].upper()}"
    
    def submit_proposal(self, proposal_data: Dict) -> Proposal:
        """提交决策提案"""
        proposal = Proposal(
            id="",
            type=proposal_data["type"],
            title=proposal_data["title"],
            description=proposal_data["description"],
            target=proposal_data["target"],
            proposed_action=proposal_data["proposed_action"],
            urgency=proposal_data.get("urgency", 5),
            submitter=proposal_data["submitter"],
            submitted_at=datetime.now().isoformat(),
            return_potential=proposal_data.get("return_potential", 50),
            risk_level=proposal_data.get("risk_level", 50),
            compliance_score=proposal_data.get("compliance_score", 50),
            timing_score=proposal_data.get("timing_score", 50)
        )
        proposal.id = self._generate_id(proposal)
        
        # 自动触发管理者投票
        proposal = self._auto_vote(proposal)
        
        # 评估共识
        proposal = self._evaluate_consensus(proposal)
        
        # 保存
        self.decisions["proposals"].append(asdict(proposal))
        self._save_decisions()
        
        return proposal
    
    def _auto_vote(self, proposal: Proposal) -> Proposal:
        """自动生成管理者投票"""
        
        # CIO投票 - 关注收益和时机
        cio_score = (proposal.return_potential * 0.6 + proposal.timing_score * 0.4)
        cio_decision = "approve" if cio_score >= self.MANAGERS["CIO"]["threshold"] else "reject"
        proposal.votes.append(ManagerVote(
            manager="CIO",
            score=cio_score,
            decision=cio_decision,
            reasoning=f"收益潜力{proposal.return_potential:.0f}分，时机{proposal.timing_score:.0f}分",
            confidence=min(cio_score / 100, 0.95),
            timestamp=datetime.now().isoformat()
        ))
        
        # CSO投票 - 关注风险和合规
        cso_score = (100 - proposal.risk_level) * 0.5 + proposal.compliance_score * 0.5
        cso_decision = "approve" if cso_score >= self.MANAGERS["CSO"]["threshold"] else "reject"
        proposal.votes.append(ManagerVote(
            manager="CSO",
            score=cso_score,
            decision=cso_decision,
            reasoning=f"风险等级{proposal.risk_level:.0f}分，合规{proposal.compliance_score:.0f}分",
            confidence=min(cso_score / 100, 0.95),
            timestamp=datetime.now().isoformat()
        ))
        
        # UZI投票 - 综合分析
        uzi_score = (proposal.return_potential + (100 - proposal.risk_level) + 
                     proposal.compliance_score + proposal.timing_score) / 4
        uzi_decision = "approve" if uzi_score >= self.MANAGERS["UZI"]["threshold"] else "reject"
        proposal.votes.append(ManagerVote(
            manager="UZI",
            score=uzi_score,
            decision=uzi_decision,
            reasoning=f"综合评分: 收益{proposal.return_potential:.0f}/风险{100-proposal.risk_level:.0f}/合规{proposal.compliance_score:.0f}/时机{proposal.timing_score:.0f}",
            confidence=min(uzi_score / 100, 0.95),
            timestamp=datetime.now().isoformat()
        ))
        
        return proposal
    
    def _evaluate_consensus(self, proposal: Proposal) -> Proposal:
        """评估共识水平"""
        # 计算加权得分
        total_score = 0
        approve_count = 0
        
        for vote in proposal.votes:
            weight = self.MANAGERS[vote.manager]["weight"]
            total_score += vote.score * weight
            if vote.decision == "approve":
                approve_count += 1
        
        proposal.final_score = total_score
        
        # 判断共识级别
        approve_rate = approve_count / len(proposal.votes)
        
        if approve_rate == 1.0 and total_score >= 80:
            proposal.consensus_level = "unanimous"
        elif total_score >= 75:
            proposal.consensus_level = "super_majority"
        elif total_score >= 60:
            proposal.consensus_level = "simple_majority"
        else:
            proposal.consensus_level = "no_consensus"
        
        # 根据决策类型判断是否通过
        required = self._get_required_consensus(proposal.type)
        if self._meets_threshold(proposal.consensus_level, required):
            proposal.status = "approved"
        else:
            proposal.status = "rejected"
        
        return proposal
    
    def _get_required_consensus(self, decision_type: str) -> str:
        """获取决策类型所需的共识级别"""
        rules = {
            "trade_execution": "super_majority",
            "position_adjustment": "super_majority",
            "risk_action": "unanimous",
            "strategy_change": "unanimous"
        }
        return rules.get(decision_type, "simple_majority")
    
    def _meets_threshold(self, achieved: str, required: str) -> bool:
        """判断是否达到阈值"""
        levels = ["no_consensus", "simple_majority", "super_majority", "unanimous"]
        return levels.index(achieved) >= levels.index(required)
    
    def get_decision_summary(self, proposal_id: str) -> Dict:
        """获取决策摘要"""
        for p in self.decisions["proposals"]:
            if p["id"] == proposal_id:
                return {
                    "id": p["id"],
                    "title": p["title"],
                    "target": p["target"],
                    "action": p["proposed_action"],
                    "final_score": p["final_score"],
                    "consensus_level": p["consensus_level"],
                    "status": p["status"],
                    "votes": [
                        {
                            "manager": v["manager"],
                            "decision": v["decision"],
                            "score": v["score"],
                            "reasoning": v["reasoning"]
                        }
                        for v in p["votes"]
                    ]
                }
        return {}
    
    def list_pending_decisions(self) -> List[Dict]:
        """列出待处理决策"""
        return [
            {
                "id": p["id"],
                "title": p["title"],
                "target": p["target"],
                "urgency": p["urgency"],
                "status": p["status"],
                "submitted_at": p["submitted_at"]
            }
            for p in self.decisions["proposals"]
            if p["status"] == "approved" and p.get("executed") is not True
        ]


# 演示函数
def demo_collective_decision():
    """演示集体决策系统"""
    engine = CollectiveDecisionEngine()
    
    # Demo 1: 清仓招商南油 (高风险)
    print("=" * 60)
    print("🎯 Demo 1: 清仓招商南油 (风险处置)")
    print("=" * 60)
    
    proposal1 = engine.submit_proposal({
        "type": "risk_action",
        "title": "清仓招商南油",
        "description": "CSO合规违规 + CIO Kelly=0 + UZI低评分，三系统一致看空",
        "target": "601975",
        "proposed_action": "清仓所有持仓",
        "urgency": 9,
        "submitter": "CSO",
        "return_potential": 20,  # 低收益潜力
        "risk_level": 85,  # 高风险
        "compliance_score": 30,  # 不合规
        "timing_score": 40  # 时机不佳
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
        print(f"  {emoji} {v['manager']}: {v['decision'].upper()} ({v['score']:.0f}分) - {v['reasoning']}")
    
    # Demo 2: 减持中国长城 (仓位调整)
    print("\n" + "=" * 60)
    print("🎯 Demo 2: 减持中国长城 (仓位调整)")
    print("=" * 60)
    
    proposal2 = engine.submit_proposal({
        "type": "position_adjustment",
        "title": "减持中国长城至20%",
        "description": "当前持仓36.7%，超过20%限制，需减仓",
        "target": "000066",
        "proposed_action": "减持至20%仓位",
        "urgency": 7,
        "submitter": "CSO",
        "return_potential": 65,
        "risk_level": 50,
        "compliance_score": 40,
        "timing_score": 70
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
        print(f"  {emoji} {v['manager']}: {v['decision'].upper()} ({v['score']:.0f}分) - {v['reasoning']}")
    
    # Demo 3: 新建仓中芯国际 (交易执行)
    print("\n" + "=" * 60)
    print("🎯 Demo 3: 增持中芯国际 (交易执行)")
    print("=" * 60)
    
    proposal3 = engine.submit_proposal({
        "type": "trade_execution",
        "title": "增持中芯国际",
        "description": "分散投资，增加半导体配置",
        "target": "688981",
        "proposed_action": "增持至10%仓位",
        "urgency": 5,
        "submitter": "CIO",
        "return_potential": 75,
        "risk_level": 45,
        "compliance_score": 85,
        "timing_score": 70
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
        print(f"  {emoji} {v['manager']}: {v['decision'].upper()} ({v['score']:.0f}分) - {v['reasoning']}")
    
    print("\n" + "=" * 60)
    print("📋 待执行决策列表")
    print("=" * 60)
    pending = engine.list_pending_decisions()
    for d in pending:
        urgency_emoji = "🔴" if d['urgency'] >= 8 else "🟡" if d['urgency'] >= 5 else "🟢"
        print(f"  {urgency_emoji} [{d['urgency']}/10] {d['target']} - {d['title']}")
    
    return [proposal1, proposal2, proposal3]


if __name__ == "__main__":
    demo_collective_decision()
