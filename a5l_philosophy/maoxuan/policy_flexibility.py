"""
《论政策》 - 投资政策灵活性系统
对应毛选：策略要根据形势变化而变化
"""

from typing import Dict
from datetime import datetime


class InvestmentPolicyFlexibility:
    """
    投资政策灵活性系统
    
    投资政策三原则：
    - 进攻型：牛市高仓位
    - 防御型：熊市低仓位
    - 中性型：震荡市均衡
    """
    
    POLICY_TYPES = {
        'offensive': {
            'name': '进攻型政策',
            'equity_ratio': 0.80,
            'new_position_limit': 0.20,
            'stop_loss': 0.10,
            'take_profit': 0.30
        },
        'defensive': {
            'name': '防御型政策',
            'equity_ratio': 0.40,
            'new_position_limit': 0.05,
            'stop_loss': 0.05,
            'take_profit': 0.15
        },
        'neutral': {
            'name': '中性政策',
            'equity_ratio': 0.60,
            'new_position_limit': 0.10,
            'stop_loss': 0.08,
            'take_profit': 0.20
        }
    }
    
    def determine_policy(self, market_context: dict, portfolio: dict) -> dict:
        """根据形势确定投资政策"""
        market_phase = market_context.get('phase', 'neutral')
        valuation = market_context.get('valuation_percentile', 0.5)
        sentiment = market_context.get('sentiment', 0.5)
        
        if market_phase == 'bull' and valuation < 0.7 and sentiment > 0.6:
            policy = 'offensive'
            reason = '牛市中期，进攻型政策'
        elif market_phase == 'bear' or valuation > 0.8:
            policy = 'defensive'
            reason = '熊市或估值过高，防御型政策'
        else:
            policy = 'neutral'
            reason = '形势不明，中性政策'
        
        return {
            'current_policy': policy,
            'policy_name': self.POLICY_TYPES[policy]['name'],
            'reason': reason,
            'parameters': self.POLICY_TYPES[policy]
        }
