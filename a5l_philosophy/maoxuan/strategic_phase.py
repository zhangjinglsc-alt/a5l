"""
《中国革命战争的战略问题》第五章、第六章 - 战略阶段管理器
对应毛选：战略防御、战略进攻、战略转移
"""

from typing import Dict
from datetime import datetime


class StrategicPhaseManager:
    """
    战略阶段管理器
    
    四阶段：
    - 防御：弱势市场，小仓位试探
    - 相持：方向不明，等待信号
    - 进攻：市场转强，逐步加仓
    - 转移：目标达成，有序撤退
    """
    
    PHASES = ['defense', 'stalemate', 'offense', 'transition']
    
    def __init__(self):
        self.current_phase = 'defense'
        self.position_limits = {
            'defense': (0, 0.20),
            'stalemate': (0.20, 0.50),
            'offense': (0.50, 0.90),
            'transition': (0, 1.0)
        }
    
    def evaluate_strategic_phase(self, market_data: dict, portfolio: dict) -> dict:
        """评估当前战略阶段"""
        trend_strength = self._calculate_trend_strength(market_data)
        sentiment = self._calculate_sentiment(market_data)
        
        if self.current_phase == 'defense':
            if trend_strength > 0.3 and sentiment > 0.4:
                new_phase = 'stalemate'
                reasoning = '市场企稳，转入相持阶段'
            else:
                new_phase = 'defense'
                reasoning = '市场仍处弱势'
        elif self.current_phase == 'stalemate':
            if trend_strength > 0.6:
                new_phase = 'offense'
                reasoning = '主升浪确认'
            else:
                new_phase = 'stalemate'
                reasoning = '方向不明'
        elif self.current_phase == 'offense':
            portfolio_return = portfolio.get('total_return', 0)
            if portfolio_return >= 0.30 or trend_strength < 0.4:
                new_phase = 'transition'
                reasoning = '目标达成或趋势转弱'
            else:
                new_phase = 'offense'
                reasoning = '趋势健康'
        else:
            new_phase = 'transition'
            reasoning = '继续转移'
        
        target_position = self._calculate_target_position(new_phase, trend_strength, sentiment)
        
        return {
            'previous_phase': self.current_phase,
            'current_phase': new_phase,
            'reasoning': reasoning,
            'target_position': target_position,
            'market_indicators': {'trend_strength': trend_strength, 'sentiment': sentiment}
        }
    
    def _calculate_trend_strength(self, data: dict) -> float:
        """计算趋势强度"""
        return data.get('trend_strength', 0.5)
    
    def _calculate_sentiment(self, data: dict) -> float:
        """计算情绪"""
        return data.get('sentiment_index', 0.5)
    
    def _calculate_target_position(self, phase: str, trend: float, sentiment: float) -> float:
        """计算目标仓位"""
        min_pos, max_pos = self.position_limits[phase]
        
        if phase == 'defense':
            return min_pos + (max_pos - min_pos) * trend
        elif phase == 'stalemate':
            return min_pos + (max_pos - min_pos) * ((trend + sentiment) / 2)
        elif phase == 'offense':
            return min_pos + (max_pos - min_pos) * trend
        else:
            return max_pos * (1 - trend)
