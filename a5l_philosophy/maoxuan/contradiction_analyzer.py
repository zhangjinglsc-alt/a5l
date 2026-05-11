"""
《矛盾论》 - 多空矛盾分析器
对应毛选：主要矛盾与次要矛盾分析
"""

from typing import Dict
from datetime import datetime


class ContradictionAnalyzer:
    """
    多空矛盾分析器
    
    核心思想：
    - 多空力量对比
    - 主要矛盾识别
    - 矛盾主次转化
    """
    
    CONTRADICTION_TYPES = ['valuation', 'growth', 'sentiment', 'capital_flow']
    
    def __init__(self):
        self.contradiction_weights = {
            'valuation': 0.30,
            'growth': 0.30,
            'sentiment': 0.20,
            'capital_flow': 0.20
        }
    
    def analyze_contradictions(self, stock_data: dict, market_data: dict) -> dict:
        """分析多空矛盾"""
        contradictions = {}
        
        for c_type in self.CONTRADICTION_TYPES:
            bull_force, bear_force = self._analyze_contradiction_type(c_type, stock_data, market_data)
            contradictions[c_type] = {
                'bull_force': bull_force,
                'bear_force': bear_force,
                'dominant_side': 'bull' if bull_force > bear_force else 'bear',
                'force_ratio': max(bull_force, bear_force) / max(min(bull_force, bear_force), 0.01)
            }
        
        # 识别主要矛盾
        primary = max(contradictions.items(), key=lambda x: abs(x[1]['bull_force'] - x[1]['bear_force']))
        
        # 计算多空总力量
        total_bull = sum([c['bull_force'] * self.contradiction_weights[t] for t, c in contradictions.items()])
        total_bear = sum([c['bear_force'] * self.contradiction_weights[t] for t, c in contradictions.items()])
        
        return {
            'contradictions': contradictions,
            'primary_contradiction': {'type': primary[0], 'details': primary[1]},
            'total_bull_force': total_bull,
            'total_bear_force': total_bear,
            'dominant_force': 'bull' if total_bull > total_bear else 'bear'
        }
    
    def _analyze_contradiction_type(self, c_type: str, stock: dict, market: dict) -> tuple:
        """分析特定类型的矛盾"""
        if c_type == 'valuation':
            percentile = stock.get('valuation_percentile', 0.5)
            bull = (1 - percentile) * 0.5
            bear = percentile * 0.5
        elif c_type == 'growth':
            growth = stock.get('revenue_growth', 0)
            bull = min(growth / 0.30, 1) * 0.6
            bear = max(0, 1 - growth / 0.10) * 0.6
        elif c_type == 'sentiment':
            sentiment = market.get('sentiment_score', 0.5)
            bull = max(0, (30 - sentiment * 100) / 30) if sentiment < 0.3 else 0.1
            bear = max(0, (sentiment * 100 - 70) / 30) if sentiment > 0.7 else 0.1
        else:  # capital_flow
            inflow = stock.get('capital_inflow', 0)
            bull = min(max(inflow / 100, 0), 1) * 0.5
            bear = 0.0
        
        return bull, bear
