"""
《中国革命战争的战略问题》第七章 - 集中兵力仓位分配器
对应毛选：集中绝对优势兵力
"""

from typing import Dict, List
from datetime import datetime


class ConcentratedPositionAllocator:
    """
    集中兵力仓位分配器
    
    仓位金字塔：
    - 核心仓位：40-50%，1-2只最确定标的
    - 卫星仓位：30-40%，3-5只有潜力标的
    - 游击仓位：10-20%，5-10只试探性标的
    """
    
    def __init__(self, total_capital: float):
        self.total_capital = total_capital
        self.allocation_pyramid = {
            'core': 0.50,
            'satellite': 0.35,
            'guerrilla': 0.15
        }
    
    def allocate_concentrated_positions(self, stock_rankings: list) -> dict:
        """执行集中兵力仓位分配"""
        allocation = {
            'core_positions': [],
            'satellite_positions': [],
            'guerrilla_positions': [],
            'concentration_coefficient': 0
        }
        
        # 分配核心仓位（TOP 1-2）
        core_capital = self.total_capital * self.allocation_pyramid['core']
        core_stocks = stock_rankings[:2]
        
        if core_stocks:
            total_value = sum([s['battle_value'] for s in core_stocks])
            for stock in core_stocks:
                weight = stock['battle_value'] / total_value if total_value > 0 else 0
                capital = core_capital * weight
                allocation['core_positions'].append({
                    'stock': stock,
                    'capital': capital,
                    'weight': capital / self.total_capital,
                    'tier': 'core'
                })
        
        # 分配卫星仓位（TOP 3-7）
        satellite_capital = self.total_capital * self.allocation_pyramid['satellite']
        satellite_stocks = stock_rankings[2:7]
        
        if satellite_stocks:
            total_value = sum([s['battle_value'] for s in satellite_stocks])
            for stock in satellite_stocks:
                weight = stock['battle_value'] / total_value if total_value > 0 else 0
                capital = satellite_capital * weight
                allocation['satellite_positions'].append({
                    'stock': stock,
                    'capital': capital,
                    'weight': capital / self.total_capital,
                    'tier': 'satellite'
                })
        
        # 分配游击仓位（TOP 8-17）
        guerrilla_capital = self.total_capital * self.allocation_pyramid['guerrilla']
        guerrilla_stocks = stock_rankings[7:17]
        
        if guerrilla_stocks:
            capital_per_stock = guerrilla_capital / len(guerrilla_stocks)
            for stock in guerrilla_stocks:
                allocation['guerrilla_positions'].append({
                    'stock': stock,
                    'capital': capital_per_stock,
                    'weight': capital_per_stock / self.total_capital,
                    'tier': 'guerrilla'
                })
        
        # 计算集中系数
        all_positions = allocation['core_positions'] + allocation['satellite_positions'] + allocation['guerrilla_positions']
        weights = [p['weight'] for p in all_positions]
        allocation['concentration_coefficient'] = self._calculate_concentration_coefficient(weights)
        
        return allocation
    
    def _calculate_concentration_coefficient(self, weights: list) -> float:
        """计算集中系数"""
        if not weights or sum(weights) == 0:
            return 0
        return sum([w**2 for w in weights]) / (sum(weights)**2)
