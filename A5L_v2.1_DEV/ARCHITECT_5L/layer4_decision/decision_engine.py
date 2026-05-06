#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 4: Decision Engine
决策信号层 - 决策引擎

功能：
1. 信号聚合 + 仓位管理整合
2. 模拟交易执行
3. 实盘研究助手模式
4. 交易日志记录
"""

import json
import os
import sys
sys.path.insert(0, '/workspace/projects/workspace/ARCHITECT_5L/layer4_decision')

from datetime import datetime
from typing import Dict, List, Optional
from signal_aggregator import SignalAggregator, AggregatedSignal
from position_manager import PositionManager, Portfolio, Position

class DecisionEngine:
    """决策引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.signal_aggregator = SignalAggregator(workspace)
        self.position_manager = PositionManager(workspace)
        
        # 交易日志
        self.trade_log_file = f"{workspace}/data/architect_5l/trade_log.json"
        os.makedirs(os.path.dirname(self.trade_log_file), exist_ok=True)
    
    def make_decision(self, symbol: str, mode: str = "simulated") -> Dict:
        """
        做出交易决策
        
        Args:
            symbol: 股票代码
            mode: "simulated" (模拟) | "research" (研究助手)
        
        Returns:
            决策结果
        """
        # 1. 获取信号聚合结果
        strategy_signals = [
            {"strategy_name": "股票魔法师", "action": "BUY", "confidence": 0.9},
            {"strategy_name": "趋势突破", "action": "BUY", "confidence": 0.75}
        ]
        
        analysis_results = {
            "sentiment": {"score": 0.6, "confidence": 0.8},
            "risks": []
        }
        
        signal = self.signal_aggregator.aggregate_signals(
            symbol, strategy_signals, analysis_results
        )
        
        # 2. 根据模式处理
        if mode == "simulated":
            decision = self._simulated_trading_decision(symbol, signal)
        else:
            decision = self._research_assistant_decision(symbol, signal)
        
        # 3. 记录日志
        self._log_decision(decision)
        
        return decision
    
    def _simulated_trading_decision(self, symbol: str, signal: AggregatedSignal) -> Dict:
        """模拟交易决策"""
        # 模拟投资组合
        portfolio = Portfolio(
            account_id="SIM_001",
            total_equity=1000000,
            available_cash=500000,
            positions={},
            total_market_value=500000,
            total_unrealized_pnl=0,
            risk_exposure=0.05
        )
        
        # 获取仓位建议
        position_rec = self.position_manager.calculate_position_size(
            portfolio, symbol, signal.strength, 10.5, signal.risk_level
        )
        
        # 模拟执行
        if signal.action == "BUY" and signal.confidence > 0.6:
            executed = True
            shares = position_rec["recommended_shares"]
            price = 10.5
            total_value = shares * price
        else:
            executed = False
            shares = 0
            price = 0
            total_value = 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "mode": "simulated",
            "symbol": symbol,
            "signal": {
                "action": signal.action,
                "confidence": signal.confidence,
                "strength": signal.strength,
                "risk_level": signal.risk_level
            },
            "decision": {
                "action": "BUY" if executed else "HOLD",
                "shares": shares,
                "price": price,
                "total_value": total_value,
                "stop_loss": position_rec["stop_loss_price"],
                "take_profit": position_rec["take_profit_price"]
            },
            "execution_status": "EXECUTED" if executed else "PENDING",
            "portfolio_impact": {
                "position_pct": position_rec["position_pct_of_equity"],
                "cash_remaining": portfolio.available_cash - total_value
            }
        }
    
    def _research_assistant_decision(self, symbol: str, signal: AggregatedSignal) -> Dict:
        """研究助手模式决策"""
        # 研究助手模式只提供建议，不执行
        return {
            "timestamp": datetime.now().isoformat(),
            "mode": "research_assistant",
            "symbol": symbol,
            "signal": {
                "action": signal.action,
                "confidence": signal.confidence,
                "strength": signal.strength,
                "risk_level": signal.risk_level
            },
            "recommendation": {
                "action": signal.action if signal.confidence > 0.6 else "HOLD",
                "rationale": f"基于{len(signal.sources)}个信号源聚合，置信度{signal.confidence:.0%}",
                "suggested_position_size": "10%" if signal.strength == "strong" else "5-8%",
                "stop_loss_suggestion": "3%" if signal.risk_level == "high" else "5%",
                "disclaimer": "此为研究建议，不构成投资建议。最终决策请结合个人判断。"
            },
            "execution_status": "ADVISORY_ONLY",
            "human_decision_required": True
        }
    
    def _log_decision(self, decision: Dict):
        """记录决策日志"""
        log_entry = {
            "timestamp": decision["timestamp"],
            "mode": decision["mode"],
            "symbol": decision["symbol"],
            "action": decision.get("decision", {}).get("action", "HOLD"),
            "status": decision["execution_status"]
        }
        
        # 追加到日志文件
        logs = []
        if os.path.exists(self.trade_log_file):
            with open(self.trade_log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(self.trade_log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """获取决策历史"""
        if not os.path.exists(self.trade_log_file):
            return []
        
        with open(self.trade_log_file, 'r') as f:
            logs = json.load(f)
        
        return logs[-limit:]
    
    def generate_decision_report(self) -> str:
        """生成决策报告"""
        history = self.get_decision_history(20)
        
        report = f"""# 📊 决策引擎报告

**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**近期决策数**: {len(history)}

---

## 📝 最近决策

| 时间 | 模式 | 标的 | 动作 | 状态 |
|------|------|------|------|------|
"""
        
        for log in history:
            report += f"| {log['timestamp'][:16]} | {log['mode']} | {log['symbol']} | {log['action']} | {log['status']} |\n"
        
        # 统计
        simulated_count = sum(1 for h in history if h['mode'] == 'simulated')
        research_count = sum(1 for h in history if h['mode'] == 'research_assistant')
        
        report += f"""
---

## 📈 模式统计

- **模拟交易**: {simulated_count} 次
- **研究助手**: {research_count} 次

---

## ⚠️ 说明

- **模拟交易模式**: 自动执行交易决策，用于策略验证
- **研究助手模式**: 提供研究建议，需要人工确认后执行
"""
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("🤖 决策引擎 (Layer 4)")
    print("=" * 70)
    
    engine = DecisionEngine()
    
    # 模拟交易模式
    print("\n🎮 模拟交易模式:")
    decision1 = engine.make_decision("000001.SZ", mode="simulated")
    print(f"  标的: {decision1['symbol']}")
    print(f"  信号: {decision1['signal']['action']} (置信度: {decision1['signal']['confidence']:.0%})")
    print(f"  决策: {decision1['decision']['action']}")
    print(f"  执行状态: {decision1['execution_status']}")
    
    # 研究助手模式
    print("\n📖 研究助手模式:")
    decision2 = engine.make_decision("000002.SZ", mode="research")
    print(f"  标的: {decision2['symbol']}")
    print(f"  建议: {decision2['recommendation']['action']}")
    print(f"  理由: {decision2['recommendation']['rationale']}")
    print(f"  需要人工决策: {decision2['human_decision_required']}")
    
    # 决策历史
    print("\n📜 决策历史:")
    history = engine.get_decision_history(5)
    for h in history:
        print(f"  • {h['timestamp'][:16]} - {h['symbol']} {h['action']} ({h['mode']})")

if __name__ == "__main__":
    main()
