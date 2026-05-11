"""
《论持久战》第六章 - 主动性、灵活性、计划性交易器
对应毛选：三性是游击战争的基本指导原则
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta


class ThreePrinciplesTrader:
    """
    主动性、灵活性、计划性交易器
    
    三性原则：
    - 主动性：交易自由度，现金储备=行动自由
    - 灵活性：策略应变，根据市场变化调整
    - 计划性：交易计划，买入前制定完整计划
    """
    
    def __init__(self):
        self.weights = {
            'freedom': 0.4,
            'adaptability': 0.3,
            'planning': 0.3
        }
        self.trade_history = []
        self.plans = {}
    
    def calculate_freedom_index(self, portfolio: dict) -> dict:
        """计算主动性（自由度）指数"""
        total = portfolio.get('total_capital', 0)
        cash = portfolio.get('cash', 0)
        
        cash_ratio = cash / total if total > 0 else 0
        
        # 可交易品种数
        positions = portfolio.get('positions', {})
        tradable = sum([1 for p in positions.values() if not p.get('is_limit_down', False)])
        tradable_ratio = tradable / max(len(positions), 1)
        
        # 时间自由度
        time_freedom = self._check_time_freedom()
        
        freedom_index = cash_ratio * 0.5 + tradable_ratio * 0.3 + time_freedom * 0.2
        
        return {
            'freedom_index': freedom_index,
            'status': 'active' if freedom_index > 0.3 else 'restricted',
            'components': {
                'cash_ratio': cash_ratio,
                'tradable_ratio': tradable_ratio,
                'time_freedom': time_freedom
            }
        }
    
    def create_trade_plan(self, stock: dict, thesis: str) -> dict:
        """制定交易计划（计划性）"""
        plan_id = f"{stock['code']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        plan = {
            'plan_id': plan_id,
            'stock': stock,
            'thesis': thesis,
            'created_at': datetime.now().isoformat(),
            'entry': {
                'trigger_price': stock.get('target_entry', 0),
                'position_size': stock.get('recommended_position', 0),
            },
            'exit': {
                'target_price': stock.get('target_price', 0),
                'stop_loss': stock.get('stop_loss', stock.get('target_entry', 0) * 0.92),
            },
        }
        
        self.plans[plan_id] = plan
        return plan
    
    def evaluate_flexibility(self, plan_id: str, current_market: dict) -> dict:
        """评估是否需要灵活调整计划"""
        if plan_id not in self.plans:
            return {'error': 'Plan not found'}
        
        plan = self.plans[plan_id]
        adjustments = []
        
        # 检查催化剂变化
        current_catalyst = current_market.get('catalyst_tier', 0)
        original = plan['stock'].get('catalyst_tier', 0)
        
        if current_catalyst < original - 1:
            adjustments.append({
                'type': 'catalyst_downgrade',
                'action': 'reduce_position'
            })
        
        return {
            'needs_adjustment': len(adjustments) > 0,
            'adjustments': adjustments
        }
    
    def _check_time_freedom(self) -> float:
        """检查时间自由度"""
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        
        # A股交易时间
        if (9 <= hour <= 11) or (13 <= hour <= 15):
            return 1.0
        return 0.0
