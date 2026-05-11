"""
《中国革命战争的战略问题》第三章 - 全局与局部资产配置器
对应毛选：懂得了全局性的东西，就更会使用局部性的东西
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime


class GlobalLocalAllocator:
    """
    全局-局部资产配置器
    
    核心思想：
    - 全局决定局部：市场周期、宏观环境决定资产配置
    - 局部服从全局：个股选择服从于资产配置框架
    - 战略配置矩阵：根据市场环境确定股债配比
    """
    
    def __init__(self, total_capital: float, risk_budget: float):
        self.total_capital = total_capital
        self.risk_budget = risk_budget
        self.global_state = None
        
        # 战略资产配置矩阵
        self.allocation_matrix = {
            'bull_riskon': {'equity': 0.80, 'bond': 0.10, 'cash': 0.05, 'alt': 0.05},
            'bull_riskoff': {'equity': 0.60, 'bond': 0.25, 'cash': 0.10, 'alt': 0.05},
            'bear_riskon': {'equity': 0.30, 'bond': 0.40, 'cash': 0.25, 'alt': 0.05},
            'bear_riskoff': {'equity': 0.15, 'bond': 0.50, 'cash': 0.30, 'alt': 0.05},
            'sideways_riskon': {'equity': 0.50, 'bond': 0.30, 'cash': 0.15, 'alt': 0.05},
            'sideways_riskoff': {'equity': 0.35, 'bond': 0.40, 'cash': 0.20, 'alt': 0.05}
        }
    
    def determine_global_allocation(self, market_analysis: dict) -> dict:
        """
        确定全局资产配置
        
        Returns:
            global_allocation: 全局配置方案
        """
        # 分析全局状态
        self.global_state = self._analyze_global_state(market_analysis)
        
        # 根据全局状态确定资产配置
        cycle = self.global_state['market_cycle']
        risk_appetite = self.global_state['risk_appetite']
        
        state_key = f"{cycle}_{risk_appetite}"
        allocation = self.allocation_matrix.get(state_key, self.allocation_matrix['sideways_riskoff'])
        
        return {
            'global_state': self.global_state,
            'allocation': allocation,
            'total_capital': self.total_capital,
            'equity_capital': self.total_capital * allocation['equity'],
            'thesis': self._generate_allocation_thesis(),
            'timestamp': datetime.now().isoformat()
        }
    
    def allocate_to_locals(self, stock_pool: list, global_allocation: dict) -> dict:
        """
        将全局配置分配到局部个股
        
        Args:
            stock_pool: 可选股票池
            global_allocation: 全局配置方案
            
        Returns:
            local_allocations: 个股配置方案
        """
        equity_capital = global_allocation['equity_capital']
        global_state = global_allocation['global_state']
        
        # 基于全局状态筛选和配置个股
        selected_stocks = []
        
        for stock in stock_pool:
            # 评估个股与全局状态的匹配度
            match_score = self._evaluate_global_local_match(stock, global_state)
            
            if match_score > 0.6:  # 匹配度阈值
                selected_stocks.append({
                    'stock': stock,
                    'match_score': match_score,
                    'local_characteristics': self._analyze_local_characteristics(stock)
                })
        
        # 按匹配度排序
        selected_stocks.sort(key=lambda x: x['match_score'], reverse=True)
        
        # 分配资金（匹配度越高，仓位越大）
        local_allocations = []
        
        for i, item in enumerate(selected_stocks[:10]):  # 最多10只
            # 仓位权重 = 匹配度 / 总匹配度
            total_match = sum([s['match_score'] for s in selected_stocks[:10]])
            weight = item['match_score'] / total_match if total_match > 0 else 0
            capital = equity_capital * weight
            
            local_allocations.append({
                'code': item['stock']['code'],
                'name': item['stock']['name'],
                'capital': capital,
                'weight': weight,
                'match_score': item['match_score'],
                'rationale': self._generate_rationale(item, global_state)
            })
        
        return {
            'global_context': global_allocation,
            'local_allocations': local_allocations,
            'num_positions': len(local_allocations),
            'concentration': self._calculate_concentration(local_allocations)
        }
    
    def _analyze_global_state(self, market_analysis: dict) -> dict:
        """分析全局状态"""
        return {
            'market_cycle': market_analysis.get('cycle', 'sideways'),
            'macro_environment': market_analysis.get('macro', 'neutral'),
            'risk_appetite': market_analysis.get('risk_appetite', 'riskoff'),
            'capital_structure': market_analysis.get('capital_structure', 'mixed'),
            'confidence': market_analysis.get('confidence', 0.5)
        }
    
    def _evaluate_global_local_match(self, stock: dict, global_state: dict) -> float:
        """评估个股与全局状态的匹配度"""
        score = 0.0
        
        # 市场周期匹配
        if global_state['market_cycle'] == 'bull':
            score += stock.get('growth_potential', 0) * 0.3
        elif global_state['market_cycle'] == 'bear':
            score += stock.get('defensive_characteristic', 0) * 0.3
        
        # 风险偏好匹配
        if global_state['risk_appetite'] == 'risk_on':
            score += stock.get('beta', 1.0) * 0.3
        else:
            score += (1 / max(stock.get('beta', 1.0), 0.1)) * 0.3
        
        return min(score, 1.0)
    
    def _analyze_local_characteristics(self, stock: dict) -> dict:
        """分析个股特性"""
        return {
            'sector': stock.get('sector', 'unknown'),
            'market_cap': stock.get('market_cap', 0),
            'beta': stock.get('beta', 1.0),
            'style': stock.get('style', 'blend')
        }
    
    def _generate_rationale(self, item: dict, global_state: dict) -> str:
        """生成配置逻辑说明"""
        return f"全局状态匹配度{item['match_score']:.1%}，符合当前{global_state['market_cycle']}周期配置"
    
    def _generate_allocation_thesis(self) -> str:
        """生成配置逻辑说明"""
        return f"""
        全局状态：{self.global_state}
        配置逻辑：基于全局-局部关系，当前处于{self.global_state['market_cycle']}周期，
        风险偏好在{self.global_state['risk_appetite']}状态。
        个股选择将服从于这一全局配置框架。
        """
    
    def _calculate_concentration(self, allocations: list) -> float:
        """计算集中度"""
        if not allocations:
            return 0
        weights = [a['weight'] for a in allocations]
        return sum([w**2 for w in weights])
