#!/usr/bin/env python3
"""
A5L-Prime 自动化决策记录系统
完整工作流：交易→记录→溯源→报告
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from prime_poc import PrimeAtom, A5LKnowledgeGraph


class AutomatedDecisionRecorder:
    """
    自动化决策记录系统
    与A5L交易系统集成，自动记录所有决策
    """
    
    def __init__(self, kg: A5LKnowledgeGraph):
        self.kg = kg
        self.session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.decisions = []
        
    def record_trading_decision(self,
                                 action: str,  # BUY/SELL/HOLD
                                 symbol: str,
                                 name: str,
                                 quantity: int,
                                 price: float,
                                 reasoning: str,
                                 signals: List[str],
                                 confidence: float,
                                 manager: str = "@a5l/persona-cio") -> PrimeAtom:
        """
        记录交易决策（自动化入口）
        
        这是主要API，交易后自动调用
        """
        
        decision_id = f"@a5l/decision-trade-{symbol.replace('.', '-')}-{datetime.now().strftime('%Y%m%d-%H%M%S%f')[:-3]}"
        
        # 创建决策原子
        decision = PrimeAtom(
            id=decision_id,
            kind="decision",
            version="1.0.0",
            domain="trading"
        )
        
        decision.set_content(
            session_id=self.session_id,
            action=action,
            symbol=symbol,
            name=name,
            quantity=quantity,
            price=price,
            total_value=quantity * price,
            reasoning=reasoning,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            status="recorded"
        )
        
        # 关联信号
        for signal in signals:
            signal_atom_id = f"@a5l/signal-{signal}-{datetime.now().strftime('%Y%m%d')}"
            decision.add_edge("triggered_by", signal_atom_id)
        
        # 关联管理者
        decision.add_edge("authorized_by", manager)
        
        # 使用的SKILL（自动推断）
        skills = self._infer_skills(reasoning, signals)
        for skill in skills:
            decision.add_edge("requires", skill)
        
        # 风险检查
        risks = self._check_risks(action, symbol, quantity, price)
        for risk in risks:
            risk_id = f"{decision_id}-risk-{len(risks)}"
            decision.add_edge("has_risk", risk_id)
        
        self.kg.add_atom(decision)
        decision.save()
        self.decisions.append(decision)
        
        return decision
    
    def _infer_skills(self, reasoning: str, signals: List[str]) -> List[str]:
        """根据决策内容推断使用的SKILL"""
        skills = []
        
        keyword_mapping = {
            " catalyst": "@a5l/skill-catalyst-tier-framework",
            "tier": "@a5l/skill-catalyst-tier-framework",
            "突破": "@a5l/skill-technical-analysis",
            "连板": "@a5l/skill-yangguan-daodao",
            "产业链": "@a5l/skill-industry-research",
            "估值": "@a5l/skill-buffett-value-investing",
            "因子": "@a5l/skill-factor-investing",
            "回测": "@a5l/skill-unified-backtest-engine",
            "风险": "@a5l/skill-guardrails-system",
            "记忆": "@a5l/skill-memory-palace"
        }
        
        for keyword, skill_id in keyword_mapping.items():
            if keyword in reasoning.lower() or any(keyword in s for s in signals):
                if skill_id not in skills:
                    skills.append(skill_id)
        
        return skills[:5]
    
    def _check_risks(self, action: str, symbol: str, quantity: int, price: float) -> List[str]:
        """自动风险检查"""
        risks = []
        
        # 集中度检查
        total_value = quantity * price
        if total_value > 500000:  # 超过50万
            risks.append(f"单票金额较大: ¥{total_value:,.0f}")
        
        # 价格检查
        if price > 100:
            risks.append(f"高价股: ¥{price}")
        
        return risks
    
    def generate_decision_report(self, decision_id: str) -> Dict:
        """生成单个决策的完整报告"""
        
        decision = self.kg.get_atom(decision_id)
        if not decision:
            return {}
        
        report = {
            "decision": decision.to_dict(),
            "signals": [],
            "skills": [],
            "risks": [],
            "timeline": []
        }
        
        # 收集触发信号
        for signal_id in decision.edges.get("triggered_by", []):
            signal = self.kg.get_atom(signal_id)
            if signal:
                report["signals"].append(signal.to_dict())
        
        # 收集使用的SKILL
        for skill_id in decision.edges.get("requires", []):
            skill = self.kg.get_atom(skill_id)
            if skill:
                report["skills"].append({
                    "id": skill_id,
                    "name": skill.content.get("name", skill_id)
                })
        
        # 收集风险
        for risk_id in decision.edges.get("has_risk", []):
            risk = self.kg.get_atom(risk_id)
            if risk:
                report["risks"].append(risk.to_dict())
        
        return report
    
    def get_session_summary(self) -> Dict:
        """获取会话摘要"""
        
        buy_decisions = [d for d in self.decisions if d.content.get("action") == "BUY"]
        sell_decisions = [d for d in self.decisions if d.content.get("action") == "SELL"]
        
        total_buy = sum(d.content.get("total_value", 0) for d in buy_decisions)
        total_sell = sum(d.content.get("total_value", 0) for d in sell_decisions)
        
        return {
            "session_id": self.session_id,
            "start_time": self.decisions[0].content.get("timestamp") if self.decisions else None,
            "end_time": datetime.now().isoformat(),
            "total_decisions": len(self.decisions),
            "buy_count": len(buy_decisions),
            "sell_count": len(sell_decisions),
            "total_buy_value": total_buy,
            "total_sell_value": total_sell,
            "net_flow": total_sell - total_buy,
            "decision_ids": [d.id for d in self.decisions]
        }
    
    def export_to_prime_format(self, output_path: str):
        """导出为Prime标准格式"""
        
        prime_export = {
            "version": "1.0.0",
            "session": self.get_session_summary(),
            "atoms": {d.id: d.to_dict() for d in self.decisions},
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "exporter": "A5L-Prime-AutomatedDecisionRecorder",
                "total_atoms": len(self.decisions)
            }
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(prime_export, f, indent=2)
        
        return output_path


def demonstrate_automated_recorder():
    """演示自动化决策记录系统"""
    
    print("="*70)
    print("🤖 A5L-Prime 自动化决策记录系统")
    print("="*70)
    
    # 初始化
    kg = A5LKnowledgeGraph()
    recorder = AutomatedDecisionRecorder(kg)
    
    print(f"\n📋 会话ID: {recorder.session_id}")
    
    # 场景1：买入中国长城
    print("\n📈 场景1: 买入中国长城")
    print("-"*70)
    
    decision1 = recorder.record_trading_decision(
        action="BUY",
        symbol="000066.SZ",
        name="中国长城",
        quantity=48000,
        price=16.86,
        reasoning="催化剂Tier 2 + 4连板突破 + 信创CPU产业链 + 集中度策略",
        signals=[
            "catalyst-tier-2",
            "breakout-4consecutive",
            "volume-expansion-3x",
            "industry-chain-cpu"
        ],
        confidence=0.85,
        manager="@a5l/persona-cio"
    )
    
    print(f"✅ 决策已记录: {decision1.id}")
    print(f"   自动推断SKILL: {decision1.edges.get('requires', [])}")
    print(f"   风险标记: {len(decision1.edges.get('has_risk', []))}个")
    
    # 场景2：卖出兴森科技
    print("\n📉 场景2: 卖出兴森科技（调仓）")
    print("-"*70)
    
    decision2 = recorder.record_trading_decision(
        action="SELL",
        symbol="002436.SZ",
        name="兴森科技",
        quantity=9300,
        price=9.85,
        reasoning="调仓换股：集中资金买入中国长城，兴森涨幅已达标",
        signals=[
            "portfolio-rebalance",
            "profit-taking-15pct"
        ],
        confidence=0.75,
        manager="@a5l/persona-cio"
    )
    
    print(f"✅ 决策已记录: {decision2.id}")
    print(f"   自动推断SKILL: {decision2.edges.get('requires', [])}")
    
    # 生成决策报告
    print("\n📊 生成决策溯源报告...")
    print("-"*70)
    
    report = recorder.generate_decision_report(decision1.id)
    print(f"决策: {decision1.content.get('action')} {decision1.content.get('name')}")
    print(f"关联信号: {len(report['signals'])}个")
    print(f"使用SKILL: {len(report['skills'])}个")
    for skill in report['skills']:
        print(f"  • {skill['id']}")
    print(f"风险点: {len(report['risks'])}个")
    
    # 会话摘要
    print("\n📋 会话摘要")
    print("-"*70)
    summary = recorder.get_session_summary()
    print(f"总决策数: {summary['total_decisions']}")
    print(f"买入: {summary['buy_count']}次, ¥{summary['total_buy_value']:,.0f}")
    print(f"卖出: {summary['sell_count']}次, ¥{summary['total_sell_value']:,.0f}")
    print(f"净流向: ¥{summary['net_flow']:+,.0f}")
    
    # 导出Prime格式
    print("\n💾 导出Prime格式...")
    export_path = recorder.export_to_prime_format(
        "/workspace/projects/workspace/prime-atoms/automated-session-export.json"
    )
    print(f"   导出路径: {export_path}")
    
    print("\n" + "="*70)
    print("✅ 自动化决策记录系统演示完成！")
    print("="*70)
    print("\n系统能力:")
    print("  • 交易后自动记录决策")
    print("  • 自动推断使用的SKILL")
    print("  • 自动风险检查和标记")
    print("  • 生成完整溯源报告")
    print("  • 导出Prime标准格式")
    print("\n集成方式:")
    print("  1. 交易系统调用 record_trading_decision()")
    print("  2. 自动生成决策原子")
    print("  3. 关联信号/SKILL/风险")
    print("  4. 可查询、可复盘、可审计")


if __name__ == "__main__":
    demonstrate_automated_recorder()
