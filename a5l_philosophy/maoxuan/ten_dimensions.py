"""
《论十大关系》 - 投资组合十维度平衡系统
对应毛选：十大关系平衡艺术
"""

from typing import Dict, List
from datetime import datetime


class TenDimensionsBalanceChecker:
    """
    投资组合十维度平衡系统
    
    十大维度：
    1. 成长与价值
    2. 本土与海外
    3. 收益与风险
    4. 大盘与小盘
    5. 龙头与细分
    6. 主流与细分赛道
    7. 白马与黑马
    8. 多头与空头思维
    9. 盈亏反思
    10. 本土与全球视野
    """
    
    DIMENSIONS = {
        'growth_vs_value': {'name': '成长与价值', 'target': 0.5, 'tolerance': 0.2},
        'domestic_vs_foreign': {'name': '本土与海外', 'target': 0.7, 'tolerance': 0.15},
        'return_vs_risk': {'name': '收益与风险', 'target': 1.5, 'tolerance': 0.3},
        'large_vs_small': {'name': '大盘与小盘', 'target': 0.6, 'tolerance': 0.2},
        'leader_vs_niche': {'name': '龙头与细分', 'target': 0.7, 'tolerance': 0.15},
    }
    
    def check_balance(self, portfolio: dict) -> dict:
        """检查投资组合十维度平衡"""
        imbalances = []
        balanced_count = 0
        
        for dim_key, dim_config in self.DIMENSIONS.items():
            actual = self._measure_dimension(portfolio, dim_key)
            target = dim_config['target']
            tolerance = dim_config['tolerance']
            
            deviation = abs(actual - target)
            is_balanced = deviation <= tolerance
            
            if is_balanced:
                balanced_count += 1
            else:
                imbalances.append({
                    'dimension': dim_key,
                    'name': dim_config['name'],
                    'actual': actual,
                    'target': target,
                    'deviation': deviation
                })
        
        balance_score = balanced_count / len(self.DIMENSIONS)
        
        return {
            'balance_score': balance_score,
            'balanced_dimensions': balanced_count,
            'total_dimensions': len(self.DIMENSIONS),
            'imbalances': imbalances,
            'overall_status': 'balanced' if balance_score >= 0.8 else 'needs_adjustment'
        }
    
    def _measure_dimension(self, portfolio: dict, dimension: str) -> float:
        """测量特定维度的实际情况"""
        if dimension == 'growth_vs_value':
            growth_value = sum([p.get('market_value', 0) for p in portfolio.get('positions', [])
                              if p.get('style') == 'growth'])
            total = portfolio.get('total_value', 1)
            return growth_value / total if total > 0 else 0.5
        elif dimension == 'domestic_vs_foreign':
            domestic = sum([p.get('market_value', 0) for p in portfolio.get('positions', [])
                           if p.get('market') == 'A股'])
            total = portfolio.get('total_value', 1)
            return domestic / total if total > 0 else 0.7
        return 0.5
