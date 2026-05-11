"""
《关于正确处理人民内部矛盾的问题》 - 组合内部冲突处理系统
对应毛选：区分敌我矛盾和人民内部矛盾，用不同方法解决
"""

from typing import Dict, List
from datetime import datetime


class PortfolioConflictResolver:
    """
    投资组合内部冲突处理系统
    
    核心思想：
    - 敌我矛盾：系统性风险、不可逆损失 → 坚决清仓
    - 人民内部矛盾：正常波动、短期回撤 → 批评教育（持有观察）
    - 团结-批评-团结：处理问题为了团结，不是为了打倒
    """
    
    CONFLICT_TYPES = {
        'enemy_contradiction': '敌我矛盾（系统性风险）',
        'internal_contradiction': '人民内部矛盾（正常波动）'
    }
    
    def __init__(self):
        self.critical_threshold = -0.25  # 25%回撤为敌我矛盾界限
        self.warning_threshold = -0.08   # 8%回撤为内部矛盾
    
    def classify_contradiction(self, position: dict, market_context: dict) -> dict:
        """区分矛盾类型"""
        stock_code = position['stock_code']
        unrealized_pnl = position.get('unrealized_pnl', 0)
        max_drawdown = position.get('max_drawdown', 0)
        
        # 检查是否为系统性风险
        is_systemic_risk = self._check_systemic_risk(stock_code, market_context)
        
        # 检查基本面是否恶化
        fundamental_deterioration = self._check_fundamental_deterioration(stock_code)
        
        # 检查催化剂是否失效
        catalyst_failure = self._check_catalyst_failure(stock_code)
        
        if is_systemic_risk or fundamental_deterioration or catalyst_failure or max_drawdown <= self.critical_threshold:
            conflict_type = 'enemy_contradiction'
            severity = 'critical'
            solution = 'liquidate_all'
            reasoning = '敌我矛盾：系统性风险或基本面恶化，必须坚决清仓'
        elif max_drawdown <= self.warning_threshold:
            conflict_type = 'internal_contradiction'
            severity = 'warning'
            solution = 'hold_and_monitor'
            reasoning = '人民内部矛盾：正常波动，继续持有观察'
        else:
            conflict_type = 'no_contradiction'
            severity = 'normal'
            solution = 'maintain'
            reasoning = '无矛盾：持仓正常'
        
        return {
            'stock_code': stock_code,
            'conflict_type': conflict_type,
            'severity': severity,
            'solution': solution,
            'reasoning': reasoning,
            'max_drawdown': max_drawdown,
            'risk_factors': {
                'systemic_risk': is_systemic_risk,
                'fundamental_deterioration': fundamental_deterioration,
                'catalyst_failure': catalyst_failure
            }
        }
    
    def resolve_through_unity(self, conflicts: list) -> dict:
        """团结-批评-团结方法解决冲突"""
        resolutions = []
        
        for conflict in conflicts:
            if conflict['conflict_type'] == 'enemy_contradiction':
                # 敌我矛盾：坚决斗争（清仓）
                resolution = {
                    'action': 'liquidate',
                    'method': 'immediate_exit',
                    'purpose': '止损保护，保护组合整体'
                }
            else:
                # 人民内部矛盾：批评教育（调整）
                resolution = {
                    'action': 'adjust',
                    'method': 'reduce_position',
                    'purpose': '为了更好团结（优化组合）'
                }
            
            resolutions.append({
                'stock_code': conflict['stock_code'],
                'resolution': resolution
            })
        
        return {
            'total_conflicts': len(conflicts),
            'resolutions': resolutions,
            'principle': '团结-批评-团结：处理问题为了团结，不是为了打倒'
        }
    
    def _check_systemic_risk(self, stock_code: str, market_context: dict) -> bool:
        """检查是否为系统性风险"""
        market_crash = market_context.get('market_crash', False)
        sector_collapse = market_context.get('sector_collapse', False)
        return market_crash or sector_collapse
    
    def _check_fundamental_deterioration(self, stock_code: str) -> bool:
        """检查基本面是否恶化"""
        # 简化实现
        return False
    
    def _check_catalyst_failure(self, stock_code: str) -> bool:
        """检查催化剂是否失效"""
        # 简化实现
        return False
