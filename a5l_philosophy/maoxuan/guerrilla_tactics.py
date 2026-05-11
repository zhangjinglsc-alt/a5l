"""
《抗日游击战争的战略问题》第三章 - 游击战术仓位管理器
对应毛选：敌进我退，敌驻我扰，敌疲我打，敌退我追
"""

from typing import Dict, Any
from datetime import datetime


class GuerrillaTacticsPositionManager:
    """
    游击战术仓位管理器
    
    十六字诀投资版：
    - 敌进我退：主力拉升我减仓（不追高）
    - 敌驻我扰：震荡期间做T降成本
    - 敌疲我打：回调企稳加仓
    - 敌退我追：趋势确认追涨
    
    根据地理论：
    - 根据地：核心仓位（长期持有）
    - 游击区：试探仓位（灵活机动）
    """
    
    TACTICS = {
        'enemy_advance': 'retreat',      # 敌进我退
        'enemy_station': 'harass',       # 敌驻我扰
        'enemy_fatigue': 'attack',       # 敌疲我打
        'enemy_retreat': 'pursue'        # 敌退我追
    }
    
    def __init__(self, base_position_ratio: float = 0.5):
        self.base_position = base_position_ratio
        self.guerrilla_position = 0.2
        self.cash_ratio = 0.3
        self.base_holdings = {}
        self.guerrilla_holdings = {}
    
    def analyze_market_tactics(self, stock_data: dict, market_context: dict) -> dict:
        """分析市场战术态势"""
        price_change = stock_data.get('price_change_1d', 0)
        volume_ratio = stock_data.get('volume_ratio', 1.0)
        pullback_from_high = stock_data.get('pullback_from_high', 0)
        breakout_status = stock_data.get('breakout_status', False)
        volatility = stock_data.get('volatility_20d', 0.02)
        
        # 判断战术态势
        if price_change > 0.05 and volume_ratio > 2.0:
            tactic = 'retreat'
            signal_strength = min(abs(price_change) / 0.10, 1.0)
            action = 'reduce_position'
            quantity = self._calculate_reduction(stock_data, signal_strength)
            
        elif abs(price_change) < 0.03 and volume_ratio < 0.8 and volatility < 0.025:
            tactic = 'harass'
            signal_strength = 0.6
            action = 't_trade'
            quantity = self._calculate_t_trade_size(stock_data)
            
        elif pullback_from_high > 0.08 and volume_ratio < 1.0:
            tactic = 'attack'
            signal_strength = min(pullback_from_high / 0.15, 1.0)
            action = 'add_position'
            quantity = self._calculate_addition(stock_data, signal_strength)
            
        elif breakout_status and volume_ratio > 1.5:
            tactic = 'pursue'
            signal_strength = 0.8
            action = 'chase_rally'
            quantity = self._calculate_chase_size(stock_data)
            
        else:
            tactic = 'hold'
            signal_strength = 0.0
            action = 'maintain'
            quantity = 0
        
        return {
            'tactic': tactic,
            'tactic_cn': self._translate_tactic(tactic),
            'signal_strength': signal_strength,
            'action': action,
            'quantity': quantity,
            'timestamp': datetime.now().isoformat()
        }
    
    def manage_base_area(self, stock: dict, fundamentals: dict) -> dict:
        """根据地管理"""
        stock_code = stock['code']
        
        maintenance_checks = {
            'fundamental_intact': fundamentals.get('roe', 0) > 0.10,
            'catalyst_active': stock.get('catalyst_tier', 0) >= 2,
            'valuation_reasonable': stock.get('valuation_percentile', 0.5) < 0.80,
            'technical_support': stock.get('price', 0) > stock.get('ma60', 0),
        }
        
        passed = sum(maintenance_checks.values())
        total = len(maintenance_checks)
        score = passed / total
        
        if score >= 0.8:
            status = 'stable'
            action = 'hold_core'
        elif score >= 0.5:
            status = 'warning'
            action = 'reduce_partially'
        else:
            status = 'collapse'
            action = 'evacuate'
        
        return {
            'stock_code': stock_code,
            'base_status': status,
            'maintenance_score': score,
            'action': action
        }
    
    def _translate_tactic(self, tactic: str) -> str:
        translations = {
            'retreat': '敌进我退',
            'harass': '敌驻我扰',
            'attack': '敌疲我打',
            'pursue': '敌退我追',
            'hold': '按兵不动'
        }
        return translations.get(tactic, tactic)
    
    def _calculate_reduction(self, stock_data: dict, strength: float) -> int:
        current = stock_data.get('current_position', 0)
        reduction_ratio = 0.2 + strength * 0.3
        return int(current * reduction_ratio)
    
    def _calculate_addition(self, stock_data: dict, strength: float) -> int:
        target = stock_data.get('target_position', 0)
        current = stock_data.get('current_position', 0)
        return int((target - current) * strength * 0.5)
    
    def _calculate_t_trade_size(self, stock_data: dict) -> int:
        guerrilla = stock_data.get('guerrilla_position', 0)
        return int(guerrilla * 0.2)
    
    def _calculate_chase_size(self, stock_data: dict) -> int:
        max_chase = stock_data.get('total_position', 0) * 0.1
        return int(max_chase)
