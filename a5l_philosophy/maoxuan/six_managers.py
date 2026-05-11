"""
六管理者Hub决策系统
对应毛选：统筹全局、协调各方、民主集中
"""

from typing import Dict, List, Any
from datetime import datetime


class SixManagersHub:
    """
    六管理者Hub决策系统
    
    六管理者：
    - CA (Chief Architect): 战略契合度
    - CIO (Chief Investment Officer): 投资价值
    - COO (Chief Operating Officer): 执行可行性
    - CSO (Chief Security Officer): 安全合规（否决权）
    - KG (Knowledge Guardian): 知识支持
    - RM (Report Manager): 信息充分度
    """
    
    MANAGERS = ['CA', 'CIO', 'COO', 'CSO', 'KG', 'RM']
    
    # 权重配置
    WEIGHTS = {
        'CA': 0.20,   # 战略权重
        'CIO': 0.25,  # 投资权重
        'COO': 0.15,  # 执行权重
        'CSO': 0.20,  # 安全权重（否决权）
        'KG': 0.10,   # 知识权重
        'RM': 0.10    # 信息权重
    }
    
    # 决策阈值
    THRESHOLDS = {
        'pass': 0.75,
        'conditional': 0.60,
        'hold': 0.50
    }
    
    def __init__(self):
        self.philosophy = 'maoxuan_democratic_centralism'
        self.history = []
    
    def evaluate_proposal(self, proposal: dict, context: dict) -> dict:
        """
        评估投资提案（六管理者联合评估）
        """
        # 各管理者独立评估
        scores = {
            'CA': self._ca_evaluate(proposal, context),
            'CIO': self._cio_evaluate(proposal, context),
            'COO': self._coo_evaluate(proposal, context),
            'CSO': self._cso_evaluate(proposal, context),
            'KG': self._kg_evaluate(proposal, context),
            'RM': self._rm_evaluate(proposal, context)
        }
        
        # CSO一票否决权
        if scores['CSO'].get('score', 0) < 0.5:
            final_score = 0
            decision = 'veto'
            reason = f"CSO否决: {scores['CSO'].get('risk_reason', '风险不可接受')}"
        else:
            final_score = sum([self.WEIGHTS[m] * scores[m].get('score', 0) 
                              for m in self.MANAGERS])
            decision, reason = self._determine_decision(final_score, scores)
        
        result = {
            'proposal': proposal,
            'individual_scores': scores,
            'final_score': final_score,
            'decision': decision,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'philosophy': self.philosophy
        }
        
        self.history.append(result)
        return result
    
    def _ca_evaluate(self, proposal: dict, context: dict) -> dict:
        """CA评估：战略契合度"""
        score = 0.7  # 简化实现
        return {'score': score, 'reason': '战略匹配度良好'}
    
    def _cio_evaluate(self, proposal: dict, context: dict) -> dict:
        """CIO评估：投资价值"""
        stock = proposal.get('stock', {})
        score = stock.get('value_cell_score', 0.5) * 0.6 + stock.get('catalyst_score', 0.5) * 0.4
        return {'score': score, 'reason': f"投资价值评分{score:.1%}"}
    
    def _coo_evaluate(self, proposal: dict, context: dict) -> dict:
        """COO评估：执行可行性"""
        score = 0.7
        return {'score': score, 'reason': '执行可行'}
    
    def _cso_evaluate(self, proposal: dict, context: dict) -> dict:
        """CSO评估：安全合规（否决权）"""
        stock = proposal.get('stock', {})
        position = proposal.get('position', 0)
        
        # 风险检查
        concentration_risk = position > 0.4
        drawdown_risk = stock.get('max_drawdown_risk', 0) > 0.25
        
        if concentration_risk or drawdown_risk:
            return {
                'score': 0.3,
                'risk_reason': '集中度或回撤风险过高',
                'dimensions': {'concentration_risk': concentration_risk}
            }
        
        return {'score': 0.8, 'risk_reason': '风险可控'}
    
    def _kg_evaluate(self, proposal: dict, context: dict) -> dict:
        """KG评估：知识支持"""
        score = 0.6
        return {'score': score, 'reason': '知识支持度中等'}
    
    def _rm_evaluate(self, proposal: dict, context: dict) -> dict:
        """RM评估：信息充分度"""
        score = 0.7
        return {'score': score, 'reason': '信息较充分'}
    
    def _determine_decision(self, final_score: float, scores: dict) -> tuple:
        """确定决策"""
        if final_score >= self.THRESHOLDS['pass']:
            return 'approve', f'一致通过，综合得分{final_score:.1%}'
        elif final_score >= self.THRESHOLDS['conditional']:
            weak = [m for m, s in scores.items() if s.get('score', 0) < 0.6]
            return 'conditional', f'有条件通过，需补充{weak}材料'
        elif final_score >= self.THRESHOLDS['hold']:
            return 'hold', f'暂缓决策，得分{final_score:.1%}'
        else:
            return 'reject', f'否决，得分{final_score:.1%}'
