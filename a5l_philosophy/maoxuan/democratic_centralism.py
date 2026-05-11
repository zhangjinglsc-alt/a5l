"""
《论人民民主专政》 - 投资决策民主集中制
对应毛选：民主基础上的集中，集中指导下的民主
"""

from typing import Dict, List
from datetime import datetime


class DemocraticCentralismDecision:
    """
    投资决策民主集中制
    
    核心机制：
    - 民主：六管理者充分讨论，各抒己见
    - 集中：Chief Architect最终决策
    - 民主基础上的集中，集中指导下的民主
    """
    
    def __init__(self):
        self.managers = ['CA', 'CIO', 'COO', 'CSO', 'KG', 'RM']
        self.decision_threshold = 0.75
    
    def democratic_discussion(self, proposal: dict, context: dict) -> dict:
        """民主讨论阶段"""
        opinions = []
        
        for manager in self.managers:
            opinion = self._gather_opinion(manager, proposal, context)
            opinions.append({
                'manager': manager,
                'position': opinion['position'],  # support / oppose / neutral
                'reasoning': opinion['reasoning'],
                'confidence': opinion['confidence']
            })
        
        # 统计民主意见
        support = sum(1 for o in opinions if o['position'] == 'support')
        oppose = sum(1 for o in opinions if o['position'] == 'oppose')
        neutral = sum(1 for o in opinions if o['position'] == 'neutral')
        
        consensus_level = support / len(self.managers)
        
        return {
            'stage': 'democratic_discussion',
            'opinions': opinions,
            'statistics': {
                'support': support,
                'oppose': oppose,
                'neutral': neutral,
                'consensus_level': consensus_level
            }
        }
    
    def centralized_decision(self, democratic_result: dict, ca_judgment: dict) -> dict:
        """集中决策阶段"""
        consensus = democratic_result['statistics']['consensus_level']
        
        # CA综合民主意见做出决策
        if consensus >= self.decision_threshold:
            # 高度共识，支持民主意见
            decision = 'approve'
            reasoning = f'六管理者高度共识({consensus:.0%})，CA支持通过'
        elif consensus >= 0.5:
            # 多数支持，CA审慎批准
            decision = 'conditional_approve'
            reasoning = f'多数支持({consensus:.0%})，CA审慎批准，附加条件'
        else:
            # 分歧较大，CA综合判断
            decision = ca_judgment.get('decision', 'hold')
            reasoning = f'民主分歧，CA综合判断：{ca_judgment.get("reasoning", "")}'
        
        return {
            'stage': 'centralized_decision',
            'decision': decision,
            'final_authority': 'CA',
            'democratic_basis': democratic_result,
            'reasoning': reasoning,
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_with_democratic_centralism(self, proposal: dict, context: dict) -> dict:
        """执行民主集中制完整流程"""
        # 1. 民主讨论
        democratic = self.democratic_discussion(proposal, context)
        
        # 2. CA判断
        ca_judgment = self._ca_comprehensive_judgment(democratic, proposal)
        
        # 3. 集中决策
        final = self.centralized_decision(democratic, ca_judgment)
        
        return {
            'process': 'democratic_centralism',
            'democratic_stage': democratic,
            'centralized_stage': final,
            'final_decision': final['decision'],
            'principle': '民主基础上的集中，集中指导下的民主'
        }
    
    def _gather_opinion(self, manager: str, proposal: dict, context: dict) -> dict:
        """收集某管理者的意见"""
        # 简化实现
        return {
            'position': 'support',
            'reasoning': f'{manager}支持',
            'confidence': 0.7
        }
    
    def _ca_comprehensive_judgment(self, democratic: dict, proposal: dict) -> dict:
        """CA综合判断"""
        return {
            'decision': 'approve',
            'reasoning': '综合六管理者意见，符合战略方向'
        }
