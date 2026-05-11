"""
《人的正确思想是从哪里来的？》 - 交易认知形成机制
对应毛选：物质→感觉→思想→实践→再认识
"""

from typing import Dict, List
from datetime import datetime


class TradingCognitionFormation:
    """
    交易认知形成机制
    
    三阶段认识论：
    1. 物质→感觉：市场数据→直观感受
    2. 感觉→思想：感性认识→理性策略
    3. 思想→实践：策略→交易执行→验证
    """
    
    def __init__(self):
        self.cognition_stages = ['sensation', 'perception', 'practice']
        self.cognition_history = []
    
    def form_cognition_from_material(self, market_data: dict) -> dict:
        """从物质（市场数据）形成感觉"""
        sensation = {
            'price_movement': market_data.get('price_change', 0),
            'volume_sensation': 'high' if market_data.get('volume_ratio', 1) > 2 else 'normal',
            'mood': self._sense_market_mood(market_data),
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'stage': 'sensation',
            'input': 'market_material',
            'output': sensation,
            'description': '市场数据→直观感受'
        }
    
    def elevate_to_thought(self, sensation: dict, analysis: dict) -> dict:
        """从感觉上升到思想（理性认识）"""
        thought = {
            'market_judgment': self._form_market_judgment(sensation),
            'strategy_hypothesis': self._form_strategy_hypothesis(sensation, analysis),
            'risk_assessment': self._assess_risk(sensation),
            'confidence_level': self._calculate_confidence(sensation, analysis)
        }
        
        return {
            'stage': 'thought',
            'input': 'sensation',
            'output': thought,
            'description': '感性认识→理性策略'
        }
    
    def practice_and_verify(self, thought: dict, trade_execution: dict) -> dict:
        """实践检验认识"""
        pnl = trade_execution.get('pnl', 0)
        expected_return = thought['strategy_hypothesis'].get('expected_return', 0)
        
        # 检验认识是否正确
        if pnl > 0 and expected_return > 0:
            verification = 'correct'
            lesson = '认识正确，策略有效'
        elif pnl < 0 and expected_return > 0:
            verification = 'incorrect'
            lesson = '认识有误，需修正策略'
        else:
            verification = 'inconclusive'
            lesson = '需更多数据验证'
        
        practice_result = {
            'verification': verification,
            'pnl': pnl,
            'expected_vs_actual': expected_return - pnl,
            'lesson': lesson
        }
        
        self.cognition_history.append({
            'thought': thought,
            'practice': practice_result
        })
        
        return {
            'stage': 'practice',
            'input': 'thought',
            'output': practice_result,
            'description': '策略→交易执行→验证'
        }
    
    def re_cognition(self, practice_result: dict) -> dict:
        """再认识：根据实践修正认识"""
        if practice_result['verification'] == 'incorrect':
            correction = {
                'bias_identified': self._identify_cognitive_bias(practice_result),
                'correction_needed': True,
                'new_hypothesis': '需重新分析市场'
            }
        else:
            correction = {
                'bias_identified': None,
                'correction_needed': False,
                'new_hypothesis': '维持原策略'
            }
        
        return {
            'stage': 're_cognition',
            'input': 'practice_result',
            'output': correction,
            'description': '实践→再认识→修正策略'
        }
    
    def _sense_market_mood(self, data: dict) -> str:
        """感知市场情绪"""
        change = data.get('price_change', 0)
        if change > 0.03:
            return 'optimistic'
        elif change < -0.03:
            return 'pessimistic'
        return 'neutral'
    
    def _form_market_judgment(self, sensation: dict) -> str:
        """形成市场判断"""
        mood = sensation.get('mood', 'neutral')
        return f'市场处于{mood}状态'
    
    def _form_strategy_hypothesis(self, sensation: dict, analysis: dict) -> dict:
        """形成策略假设"""
        return {
            'expected_return': analysis.get('expected_return', 0.10),
            'time_horizon': analysis.get('time_horizon', 'medium'),
            'risk_level': analysis.get('risk_level', 'medium')
        }
    
    def _assess_risk(self, sensation: dict) -> str:
        """评估风险"""
        return 'medium'
    
    def _calculate_confidence(self, sensation: dict, analysis: dict) -> float:
        """计算信心水平"""
        return 0.7
    
    def _identify_cognitive_bias(self, practice_result: dict) -> str:
        """识别认知偏差"""
        return 'overconfidence'
