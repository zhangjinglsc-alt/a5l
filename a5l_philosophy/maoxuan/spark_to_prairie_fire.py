"""
《星星之火，可以燎原》 - 波浪式建仓演进系统
对应毛选：波浪式前进，渐进重仓
"""

from typing import Dict
from datetime import datetime


class SparkToPrairieFireSystem:
    """
    星星之火到燎原之势建仓系统
    
    四阶段演进：
    1. 侦察阶段：100股试水（星星之火）
    2. 游击阶段：小仓位参与
    3. 根据地阶段：回调加仓
    4. 燎原阶段：主升浪满仓
    """
    
    STAGES = ['scout', 'guerrilla', 'base_area', 'prairie_fire']
    
    def __init__(self, target_position: float = 0.20):
        self.target_position = target_position
        self.stage_allocation = {
            'scout': 0.05,
            'guerrilla': 0.25,
            'base_area': 0.60,
            'prairie_fire': 1.00
        }
    
    def evaluate_entry_signal(self, stock: dict, market_context: dict) -> dict:
        """评估是否具备星星之火的初始条件"""
        criteria = {
            'value': stock.get('value_cell_score', 0) > 0.6,
            'catalyst': stock.get('catalyst_tier', 0) >= 1,
            'technical': stock.get('technical_score', 0) > 0.5,
        }
        
        score = sum(criteria.values()) / len(criteria)
        
        if score >= 0.7:
            return {
                'can_enter': True,
                'stage': 'scout',
                'initial_position': self.target_position * self.stage_allocation['scout'],
                'message': '具备星星之火条件'
            }
        else:
            return {'can_enter': False, 'message': '条件不足'}
    
    def advance_stage(self, current_stage: str, performance: dict, market_context: dict) -> dict:
        """判断是否可以进阶到下一阶段"""
        stages = self.STAGES
        idx = stages.index(current_stage)
        
        if idx >= len(stages) - 1:
            return {'can_advance': False, 'message': '已达到最高阶段'}
        
        pnl = performance.get('pnl', 0)
        catalyst_confirmed = performance.get('catalyst_confirmed', False)
        breakout = performance.get('breakout', False)
        
        # 阶段转换条件
        if current_stage == 'scout' and pnl > 0.03:
            can_advance = True
        elif current_stage == 'guerrilla' and pnl > 0.08 and catalyst_confirmed:
            can_advance = True
        elif current_stage == 'base_area' and breakout and pnl > 0.15:
            can_advance = True
        else:
            can_advance = False
        
        if can_advance:
            next_stage = stages[idx + 1]
            return {
                'can_advance': True,
                'to_stage': next_stage,
                'new_position': self.target_position * self.stage_allocation[next_stage]
            }
        else:
            return {'can_advance': False}
