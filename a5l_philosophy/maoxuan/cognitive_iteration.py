"""
《实践论》 - 认知迭代与知行合一投资系统
对应毛选：实践、认识、再实践、再认识，循环往复
"""

from typing import Dict, List
from datetime import datetime


class CognitiveIterationSystem:
    """
    认知迭代与知行合一系统
    
    投资认知四阶段：
    1. 感性认识：初识股票（听说、K线、涨跌感觉）
    2. 理性认识：深度研究（财务、产业、估值）
    3. 实践检验：小仓位试错（验证假设）
    4. 再认识：修正完善（根据实践调整）
    """
    
    COGNITIVE_STAGES = ['perceptual', 'rational', 'practice_test', 're_cognition']
    
    def __init__(self):
        self.alpha = 0.3  # 实践收益权重
        self.beta = 0.2   # 学习投入权重
        self.gamma = 0.4  # 偏见固执惩罚
        self.cognitive_level = 0.5
        self.cognitive_history = []
    
    def assess_cognitive_stage(self, investor_profile: dict) -> dict:
        """评估投资者当前认知阶段"""
        study_hours = investor_profile.get('study_hours_per_week', 0)
        experience = investor_profile.get('trading_years', 0)
        has_system = investor_profile.get('has_trading_system', False)
        
        if study_hours < 5 and experience < 1:
            stage = 'perceptual'
            characteristics = ['依靠感觉交易', '缺乏系统研究']
        elif not has_system and study_hours < 20:
            stage = 'rational'
            characteristics = ['有研究能力', '但缺乏实战经验']
        elif study_hours >= 20 and has_system:
            stage = 're_cognition'
            characteristics = ['研究指导实践', '持续迭代进化']
        else:
            stage = 'practice_test'
            characteristics = ['有交易经验', '但缺乏系统反思']
        
        return {
            'current_stage': stage,
            'stage_name': self._translate_stage(stage),
            'characteristics': characteristics
        }
    
    def measure_knowledge_action_unity(self, trades: list, research: list) -> dict:
        """测量知行合一程度"""
        if not trades:
            return {'unity_score': 0}
        
        aligned = 0
        for trade in trades:
            # 检查是否有研究支撑
            has_research = any(r.get('stock_code') == trade.get('stock_code') for r in research)
            if has_research and trade.get('followed_plan', False):
                aligned += 1
        
        score = aligned / len(trades)
        
        return {
            'unity_score': score,
            'aligned_trades': aligned,
            'total_trades': len(trades)
        }
    
    def _translate_stage(self, stage: str) -> str:
        translations = {
            'perceptual': '感性认识阶段',
            'rational': '理性认识阶段',
            'practice_test': '实践检验阶段',
            're_cognition': '再认识阶段'
        }
        return translations.get(stage, stage)
