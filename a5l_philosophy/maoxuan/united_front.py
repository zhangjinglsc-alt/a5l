"""
《论联合政府》第五章 - 统一战线投资组合管理器
对应毛选：发展进步势力，争取中间势力，孤立顽固势力
"""

from typing import Dict, List
from datetime import datetime


class UnitedFrontPortfolioManager:
    """
    统一战线投资组合管理器
    
    三类势力：
    - 进步势力：核心持仓（高成长、高确定性、重仓）
    - 中间势力：卫星持仓（中等成长、观察持有）
    - 顽固势力：回避（周期性顶部、估值泡沫）
    """
    
    FORCE_TYPES = ['progressive', 'middle', 'isolated']
    
    def __init__(self, total_capital: float):
        self.total_capital = total_capital
        self.target_allocation = {
            'progressive': 0.60,
            'middle': 0.30,
            'isolated': 0.00
        }
        self.positions = {
            'progressive': [],
            'middle': [],
            'isolated': []
        }
    
    def classify_force(self, stock: dict, market_context: dict) -> str:
        """对股票进行势力分类"""
        progressive_criteria = {
            'value_cell': stock.get('value_cell_score', 0) >= 0.75,
            'catalyst': stock.get('catalyst_tier', 0) >= 2,
            'moat': stock.get('moat_score', 0) >= 0.7,
        }
        
        isolated_criteria = {
            'valuation_bubble': stock.get('valuation_percentile', 0) > 0.90,
            'catalyst_exhausted': stock.get('catalyst_tier', 0) == 0,
        }
        
        if sum(isolated_criteria.values()) >= 2:
            return 'isolated'
        elif sum(progressive_criteria.values()) >= 3:
            return 'progressive'
        else:
            return 'middle'
    
    def develop_progressive_force(self, stock: dict, current_allocation: dict) -> dict:
        """发展进步势力"""
        current = current_allocation.get('progressive', 0)
        target = self.target_allocation['progressive']
        room = target - current
        
        if room <= 0:
            return {'action': 'hold', 'reason': '进步势力已达目标'}
        
        addition = self.total_capital * min(room * 0.3, 0.10)
        
        return {
            'action': 'increase_progressive',
            'addition_capital': addition,
            'reason': '发展进步势力'
        }
    
    def isolate_reactionary_force(self, stock: dict, market_context: dict) -> dict:
        """孤立顽固势力"""
        force_type = self.classify_force(stock, market_context)
        
        if force_type != 'isolated':
            return {'action': 'monitor'}
        
        if stock.get('is_held', False):
            return {
                'action': 'exit_all',
                'reason': '股票被识别为顽固势力，全部清仓',
                'urgency': 'high'
            }
        else:
            return {
                'action': 'avoid',
                'reason': '识别为顽固势力，坚决不参与'
            }
