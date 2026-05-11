"""
《反对本本主义》 - 反对教条主义投资检查系统
对应毛选：没有调查，没有发言权
"""

from typing import Dict, List
from datetime import datetime, timedelta


class AntiDogmatismChecker:
    """
    反对教条主义投资检查系统
    
    核心思想：
    - 没有调查就没有发言权
    - 调查研究是十月怀胎，投资决策是一朝分娩
    - 反对不看财报就买入、听消息跟风、机械套用公式
    """
    
    RESEARCH_DIMENSIONS = {
        'financial': {'weight': 0.25, 'name': '财务基本面'},
        'industry': {'weight': 0.25, 'name': '产业研究'},
        'management': {'weight': 0.15, 'name': '管理层调研'},
        'verification': {'weight': 0.15, 'name': '实地验证'},
        'comparison': {'weight': 0.10, 'name': '同行对比'},
        'expert': {'weight': 0.10, 'name': '专家访谈'}
    }
    
    def __init__(self):
        self.voice_threshold = 0.7
        self.dogmatism_threshold = 0.3
        self.research_history = {}
    
    def calculate_research_completeness(self, stock_code: str) -> dict:
        """计算调查研究完整度"""
        research = self.research_history.get(stock_code, {})
        
        scores = {}
        weighted_score = 0
        total_weight = 0
        
        for dim_key, dim_info in self.RESEARCH_DIMENSIONS.items():
            score = research.get(dim_key, 0)
            weight = dim_info['weight']
            
            scores[dim_key] = {
                'score': score,
                'weight': weight,
                'passed': score >= 0.6
            }
            
            weighted_score += score * weight
            total_weight += weight
        
        completeness = weighted_score / total_weight if total_weight > 0 else 0
        
        return {
            'completeness': completeness,
            'has_voice': completeness >= self.voice_threshold,
            'weak_dimensions': [k for k, v in scores.items() if not v['passed']]
        }
    
    def conduct_investigation(self, stock_code: str) -> dict:
        """执行调查研究（十月怀胎）"""
        investigation = {
            'stock_code': stock_code,
            'start_date': datetime.now().isoformat(),
            'phases': [
                {'name': '资料收集', 'duration_days': 30},
                {'name': '深度研究', 'duration_days': 60},
                {'name': '验证跟踪', 'duration_days': 90}
            ],
            'estimated_completion': (datetime.now() + timedelta(days=180)).isoformat()
        }
        
        self.research_history[stock_code] = {'investigation': investigation, 'scores': {}}
        return investigation
