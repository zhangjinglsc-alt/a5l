#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L4 P0: 决策审计日志系统
提出者: Chief Architect (顶级架构师)
"""
import logging
import json
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DecisionRecord:
    decision_id: str
    timestamp: str
    symbol: str
    decision_type: str  # BUY/SELL/HOLD
    quantity: int
    price: float
    reasoning: str
    signals: Dict
    risk_checks: Dict
    confidence: float
    executor: str

class DecisionAuditLog:
    """决策审计日志 - P0最高优先级"""
    
    def __init__(self):
        self.decisions = []
        logger.info("📋 Decision Audit Log initialized")
    
    def record_decision(self, symbol: str, decision_type: str,
                       quantity: int, price: float, reasoning: str,
                       signals: Dict, risk_checks: Dict,
                       confidence: float, executor: str = "A5L") -> DecisionRecord:
        """记录决策"""
        decision = DecisionRecord(
            decision_id=f"dec_{len(self.decisions) + 1}",
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            decision_type=decision_type,
            quantity=quantity,
            price=price,
            reasoning=reasoning,
            signals=signals,
            risk_checks=risk_checks,
            confidence=confidence,
            executor=executor
        )
        
        self.decisions.append(decision)
        
        logger.info(f"📝 Decision recorded: {decision_type} {quantity} {symbol} @ {price}")
        return decision
    
    def query_decisions(self, symbol: str = None, 
                       start_time: str = None,
                       end_time: str = None) -> List[DecisionRecord]:
        """查询决策记录"""
        results = self.decisions
        
        if symbol:
            results = [d for d in results if d.symbol == symbol]
        
        if start_time:
            results = [d for d in results if d.timestamp >= start_time]
        
        if end_time:
            results = [d for d in results if d.timestamp <= end_time]
        
        return results
    
    def export_audit_trail(self, output_path: str):
        """导出审计轨迹"""
        audit_data = [
            {
                'decision_id': d.decision_id,
                'timestamp': d.timestamp,
                'symbol': d.symbol,
                'type': d.decision_type,
                'quantity': d.quantity,
                'price': d.price,
                'reasoning': d.reasoning,
                'confidence': d.confidence
            }
            for d in self.decisions
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Audit trail exported: {output_path}")
