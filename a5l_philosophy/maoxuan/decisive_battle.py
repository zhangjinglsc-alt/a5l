"""
《中国革命战争的战略问题》第七章 - 关键战役选择器
对应毛选：集中优势兵力，打歼灭战
"""

from typing import Dict, List
from datetime import datetime


class DecisiveBattleSelector:
    """
    关键战役选择器
    
    核心思想：
    - 识别关键战役（重仓机会）
    - 战役价值 = 胜率 × 收益 × 战略重要性
    - 集中兵力打歼灭战
    """
    
    def __init__(self):
        self.v_threshold = 0.28
        self.p_min = 0.65
        self.rr_ratio_min = 3.0
    
    def identify_decisive_battles(self, stock_pool: list, market_context: dict) -> list:
        """识别关键战役（重仓机会）"""
        battles = []
        
        for stock in stock_pool:
            win_prob = self._calculate_win_probability(stock, market_context)
            expected_return = self._calculate_expected_return(stock)
            strategic_importance = self._calculate_strategic_importance(stock)
            
            battle_value = win_prob * expected_return * strategic_importance
            
            risk = self._estimate_downside_risk(stock)
            rr_ratio = expected_return / risk if risk > 0 else float('inf')
            
            if (battle_value >= self.v_threshold and 
                win_prob >= self.p_min and 
                rr_ratio >= self.rr_ratio_min):
                
                battles.append({
                    'stock': stock,
                    'battle_value': battle_value,
                    'win_probability': win_prob,
                    'expected_return': expected_return,
                    'recommended_position': self._calculate_position_size(win_prob, rr_ratio)
                })
        
        battles.sort(key=lambda x: x['battle_value'], reverse=True)
        return battles
    
    def _calculate_win_probability(self, stock: dict, context: dict) -> float:
        """计算胜率"""
        value_score = stock.get('value_score', 0.5)
        catalyst_score = stock.get('catalyst_score', 0.5)
        
        win_prob = value_score * 0.5 + catalyst_score * 0.5
        return min(win_prob, 0.95)
    
    def _calculate_expected_return(self, stock: dict) -> float:
        """计算预期收益率"""
        current = stock.get('current_price', 0)
        target = stock.get('target_price', current)
        return (target - current) / current if current > 0 else 0
    
    def _calculate_strategic_importance(self, stock: dict) -> float:
        """计算战略重要性"""
        is_main_line = stock.get('is_main_line', False)
        is_leader = stock.get('is_sector_leader', False)
        
        importance = 0.0
        if is_main_line:
            importance += 0.4
        if is_leader:
            importance += 0.3
        
        return min(importance, 1.0)
    
    def _calculate_position_size(self, win_prob: float, rr_ratio: float) -> float:
        """计算推荐仓位（半凯利）"""
        b = rr_ratio
        p = win_prob
        q = 1 - p
        
        kelly = (p * b - q) / b if b > 0 else 0
        half_kelly = kelly / 2
        
        return min(half_kelly, 0.40)
    
    def _estimate_downside_risk(self, stock: dict) -> float:
        """估计下行风险"""
        return stock.get('volatility', 0.2)
