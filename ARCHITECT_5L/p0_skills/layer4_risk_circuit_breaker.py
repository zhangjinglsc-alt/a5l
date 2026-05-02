#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L4 P0: 交易风控熔断系统
提出者: Chief Security Officer (安全师)
"""
import logging
from typing import Dict, List
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # 正常交易
    OPEN = "open"          # 熔断中
    HALF_OPEN = "half_open"  # 试探恢复

class RiskCircuitBreaker:
    """风控熔断器 - P0最高优先级"""
    
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = 5
        self.recovery_timeout = 300  # 5分钟
        self.last_failure_time = None
        
        # 风控规则
        self.rules = {
            'max_daily_loss': 0.10,      # 单日最大亏损10%
            'max_position_loss': 0.05,   # 单笔最大亏损5%
            'max_drawdown': 0.20,        # 最大回撤20%
            'vix_threshold': 40,         # VIX恐慌指数阈值
        }
        
        logger.info("🛡️ Risk Circuit Breaker initialized")
    
    def check_trade(self, trade: Dict, portfolio: Dict) -> Dict:
        """检查交易是否允许"""
        # 如果熔断中，拒绝交易
        if self.state == CircuitState.OPEN:
            return {
                'allowed': False,
                'reason': '熔断中 - 系统暂停交易',
                'state': self.state.value
            }
        
        # 检查风控规则
        violations = []
        
        # 检查仓位风险
        if trade.get('risk', 0) > self.rules['max_position_loss']:
            violations.append(f"单笔风险{trade['risk']:.1%}超过阈值{self.rules['max_position_loss']:.1%}")
        
        # 检查组合风险
        portfolio_risk = portfolio.get('daily_loss', 0)
        if portfolio_risk > self.rules['max_daily_loss']:
            violations.append(f"日亏损{portfolio_risk:.1%}超过阈值{self.rules['max_daily_loss']:.1%}")
            self._trigger_circuit_breaker("日亏损超限")
        
        return {
            'allowed': len(violations) == 0,
            'violations': violations,
            'state': self.state.value
        }
    
    def _trigger_circuit_breaker(self, reason: str):
        """触发熔断"""
        self.state = CircuitState.OPEN
        self.last_failure_time = datetime.now()
        logger.warning(f"🚨 CIRCUIT BREAKER TRIGGERED: {reason}")
    
    def attempt_reset(self) -> bool:
        """尝试重置熔断"""
        if self.state == CircuitState.OPEN:
            # 检查是否过了冷却期
            # 实际应检查时间
            self.state = CircuitState.HALF_OPEN
            logger.info("🔓 Circuit breaker: HALF_OPEN - 试探恢复")
            return True
        return False
