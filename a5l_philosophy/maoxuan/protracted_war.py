"""
《论持久战》 - 持久战三阶段识别器
对应毛选：战略防御、战略相持、战略反攻
"""

from typing import Dict
from datetime import datetime


class ProtractedWarPhaseIdentifier:
    """
    持久战三阶段识别器
    
    三阶段：
    1. 防御阶段（建仓期）：市场低迷，逐步建仓
    2. 相持阶段（持有期）：震荡整理，耐心持有
    3. 反攻阶段（收获期）：主升浪，逐步减仓
    """
    
    PHASES = ['defense', 'stalemate', 'counteroffensive']
    
    def __init__(self):
        self.phase_features = {
            'defense': {'valuation': 'low', 'sentiment': 'fear', 'catalyst': 'none'},
            'stalemate': {'valuation': 'fair', 'sentiment': 'neutral', 'catalyst': 'building'},
            'counteroffensive': {'valuation': 'recovering', 'sentiment': 'optimistic', 'catalyst': 'active'}
        }
    
    def identify_phase(self, stock_state: dict, market_context: dict) -> dict:
        """识别个股处于持久战的哪个阶段"""
        phase_scores = {}
        
        for phase in self.PHASES:
            score = self._calculate_phase_match_score(phase, stock_state, market_context)
            phase_scores[phase] = score
        
        current_phase = max(phase_scores, key=phase_scores.get)
        confidence = phase_scores[current_phase]
        
        return {
            'current_phase': current_phase,
            'phase_scores': phase_scores,
            'confidence': confidence,
            'strategy': self._recommend_strategy(current_phase)
        }
    
    def _calculate_phase_match_score(self, phase: str, stock: dict, market: dict) -> float:
        """计算与特定阶段的匹配度"""
        score = 0.0
        
        # 估值匹配
        if phase == 'defense' and stock.get('valuation_percentile', 0.5) < 0.3:
            score += 0.25
        elif phase == 'stalemate' and 0.3 <= stock.get('valuation_percentile', 0.5) <= 0.7:
            score += 0.25
        elif phase == 'counteroffensive' and stock.get('valuation_percentile', 0.5) > 0.5:
            score += 0.25
        
        # 情绪匹配
        sentiment = market.get('sentiment_score', 0.5)
        if phase == 'defense' and sentiment < 0.3:
            score += 0.25
        elif phase == 'stalemate' and 0.3 <= sentiment <= 0.7:
            score += 0.25
        elif phase == 'counteroffensive' and sentiment > 0.7:
            score += 0.25
        
        return score
    
    def _recommend_strategy(self, phase: str) -> dict:
        """根据阶段推荐策略"""
        strategies = {
            'defense': {'action': 'accumulate', 'position_target': 0.3, 'time_horizon': '1-3 months'},
            'stalemate': {'action': 'hold', 'position_target': 0.5, 'time_horizon': '3-12 months'},
            'counteroffensive': {'action': 'realize', 'position_target': 0.1, 'time_horizon': '1-3 months'}
        }
        return strategies.get(phase, strategies['stalemate'])
