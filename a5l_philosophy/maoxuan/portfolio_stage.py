"""
《新民主主义论》 - 投资组合阶段性发展系统
对应毛选：革命分两步走，每个阶段有每个阶段的任务
"""

from typing import Dict
from datetime import datetime


class PortfolioStageEvolution:
    """
    投资组合阶段性发展系统
    
    投资两阶段论：
    1. 资本积累期：高风险高成长，追求本金快速增值
    2. 稳健增长期：稳健收益，追求长期复利
    """
    
    STAGES = {
        'capital_accumulation': {
            'name': '资本积累期',
            'equity_ratio': (0.80, 0.90),
            'strategy': 'aggressive_growth',
            'max_drawdown': 0.30
        },
        'steady_growth': {
            'name': '稳健增长期',
            'equity_ratio': (0.50, 0.70),
            'strategy': 'balanced',
            'max_drawdown': 0.15
        }
    }
    
    def __init__(self):
        self.stage_threshold = 5000000  # 500万
        self.age_threshold = 35
    
    def determine_portfolio_stage(self, investor_profile: dict) -> dict:
        """判定投资组合所处阶段"""
        asset = investor_profile.get('total_asset', 0)
        age = investor_profile.get('age', 30)
        risk_tolerance = investor_profile.get('risk_tolerance', 0.5)
        
        if asset < self.stage_threshold or age < self.age_threshold or risk_tolerance > 0.7:
            current_stage = 'capital_accumulation'
        else:
            current_stage = 'steady_growth'
        
        stage_config = self.STAGES[current_stage]
        
        return {
            'current_stage': current_stage,
            'stage_name': stage_config['name'],
            'recommended_allocation': {
                'equity_min': stage_config['equity_ratio'][0],
                'equity_max': stage_config['equity_ratio'][1],
                'strategy': stage_config['strategy']
            },
            'risk_parameters': {
                'max_drawdown': stage_config['max_drawdown']
            }
        }
