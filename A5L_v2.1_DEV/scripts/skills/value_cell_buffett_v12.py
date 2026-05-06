#!/usr/bin/env python3
"""
A5L VALUE CELL v1.2 - Buffett集成版
冲突解决: buffett_value vs value_cell → 合并到VALUE_CELL

升级功能 (v1.1 → v1.2):
- Buffett方法论作为配置选项
- 7维评分: V-A-L-U-E + Buffett专项
- 投资风格切换: 价值/成长/平衡

执行时间: 2026-05-04 02:02
作者: Chief Architect (Conflict Resolution)
"""

import os
import json
from typing import Dict, List
from datetime import datetime

WORKSPACE = "/workspace/projects/workspace"
DATA_DIR = f"{WORKSPACE}/data/value_cell"

class ValueCellBuffett:
    """
    VALUE CELL v1.2 - Buffett集成版
    
    7维评分体系:
    - V (Valuation): 估值水平
    - A (Advantage): 竞争优势
    - L (Liquidity): 流动性
    - U (Uncertainty): 不确定性
    - E (Earnings): 盈利质量
    - B (Buffett): 巴菲特专项
    - S (Safety): 安全边际
    """
    
    # 投资风格配置
    STYLES = {
        'value': {  # 纯价值 (Buffett模式)
            'weights': {'V': 20, 'A': 15, 'L': 10, 'U': 10, 'E': 15, 'B': 20, 'S': 10},
            'threshold': 70
        },
        'growth': {  # 纯成长
            'weights': {'V': 10, 'A': 20, 'L': 15, 'U': 15, 'E': 25, 'B': 5, 'S': 10},
            'threshold': 65
        },
        'balanced': {  # 平衡 (默认)
            'weights': {'V': 15, 'A': 15, 'L': 10, 'U': 10, 'E': 20, 'B': 15, 'S': 15},
            'threshold': 68
        }
    }
    
    def __init__(self, style='balanced'):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.style = style
        self.config = self.STYLES[style]
        print(f"VALUE CELL v1.2初始化 - 风格: {style}")
    
    def calculate_buffett_score(self, metrics: Dict) -> Dict:
        """
        Buffett专项评分 (7个子维度)
        """
        scores = {}
        
        # B1: 护城河 (Moat)
        scores['moat'] = min(100, metrics.get('roic_5yr', 0) * 2.5)
        
        # B2: 管理层质量
        scores['management'] = metrics.get('management_score', 70)
        
        # B3: 盈利能力 (ROE)
        scores['profitability'] = min(100, metrics.get('roe_5yr', 0) * 2)
        
        # B4: 财务保守
        debt_ratio = metrics.get('debt_ratio', 50)
        scores['conservatism'] = max(0, 100 - debt_ratio)
        
        # B5: 估值合理 (PE<20为满分)
        pe = metrics.get('pe_ttm', 25)
        scores['valuation'] = max(0, min(100, (25 - pe) * 5 + 50))
        
        # B6: 长期持有适合度
        scores['longevity'] = metrics.get('business_stability', 70)
        
        # B7: 简单易懂
        scores['simplicity'] = metrics.get('business_simplicity', 80)
        
        # Buffett总分
        buffett_total = sum(scores.values()) / len(scores)
        
        return {
            'sub_scores': scores,
            'total': buffett_total,
            'signal': 'BUY' if buffett_total >= 80 else 'HOLD' if buffett_total >= 60 else 'AVOID'
        }
    
    def analyze(self, stock_code: str, metrics: Dict) -> Dict:
        """
        7维综合分析
        """
        # V: 估值水平
        pe = metrics.get('pe_ttm', 25)
        pb = metrics.get('pb_lf', 2.0)
        v_score = max(0, min(100, (30 - pe) * 3 + (3 - pb) * 10 + 50))
        
        # A: 竞争优势
        a_score = metrics.get('competitive_advantage', 60)
        
        # L: 流动性
        market_cap = metrics.get('market_cap', 100)
        l_score = min(100, market_cap / 10)
        
        # U: 不确定性
        beta = metrics.get('beta', 1.0)
        u_score = max(0, min(100, (1.5 - beta) * 50 + 50))
        
        # E: 盈利质量
        e_score = min(100, metrics.get('roe_ttm', 0) * 2.5)
        
        # B: Buffett专项
        buffett = self.calculate_buffett_score(metrics)
        b_score = buffett['total']
        
        # S: 安全边际
        intrinsic = metrics.get('intrinsic_value', 100)
        price = metrics.get('current_price', 100)
        margin = (intrinsic - price) / intrinsic * 100
        s_score = max(0, min(100, margin * 2 + 50))
        
        # 加权总分
        weights = self.config['weights']
        total_score = (
            v_score * weights['V'] / 100 +
            a_score * weights['A'] / 100 +
            l_score * weights['L'] / 100 +
            u_score * weights['U'] / 100 +
            e_score * weights['E'] / 100 +
            b_score * weights['B'] / 100 +
            s_score * weights['S'] / 100
        )
        
        result = {
            'stock_code': stock_code,
            'style': self.style,
            'timestamp': datetime.now().isoformat(),
            'dimensions': {
                'V_Valuation': round(v_score, 1),
                'A_Advantage': round(a_score, 1),
                'L_Liquidity': round(l_score, 1),
                'U_Uncertainty': round(u_score, 1),
                'E_Earnings': round(e_score, 1),
                'B_Buffett': round(b_score, 1),
                'S_Safety': round(s_score, 1)
            },
            'buffett_details': buffett['sub_scores'],
            'total_score': round(total_score, 1),
            'threshold': self.config['threshold'],
            'signal': 'BUY' if total_score >= self.config['threshold'] else 'HOLD' if total_score >= 50 else 'AVOID',
            'conflict_resolution': 'buffett_value merged into VALUE_CELL v1.2'
        }
        
        return result
    
    def batch_analyze(self, stocks: List[Dict]) -> List[Dict]:
        """批量分析"""
        results = []
        for stock in stocks:
            result = self.analyze(stock['code'], stock['metrics'])
            results.append(result)
        return results


def demo():
    """演示: Buffett与VALUE CELL合并"""
    print("="*70)
    print("VALUE CELL v1.2 - Buffett集成版")
    print("冲突解决: buffett_value → merged → VALUE_CELL")
    print("="*70)
    
    # 测试数据
    test_stocks = [
        {
            'code': '601975',
            'metrics': {
                'pe_ttm': 12.5,
                'pb_lf': 1.2,
                'roe_ttm': 15.0,
                'roic_5yr': 12.0,
                'market_cap': 200,
                'beta': 1.1,
                'debt_ratio': 35,
                'management_score': 75,
                'business_stability': 70,
                'business_simplicity': 80,
                'intrinsic_value': 6.5,
                'current_price': 5.0,
                'competitive_advantage': 65
            }
        },
        {
            'code': '000066',
            'metrics': {
                'pe_ttm': 45.0,
                'pb_lf': 3.5,
                'roe_ttm': 8.0,
                'roic_5yr': 6.0,
                'market_cap': 800,
                'beta': 1.3,
                'debt_ratio': 45,
                'management_score': 70,
                'business_stability': 65,
                'business_simplicity': 60,
                'intrinsic_value': 16.0,
                'current_price': 19.8,
                'competitive_advantage': 70
            }
        }
    ]
    
    # 平衡风格分析
    print("\n【平衡风格分析】")
    vc_balanced = ValueCellBuffett('balanced')
    for stock in test_stocks:
        result = vc_balanced.analyze(stock['code'], stock['metrics'])
        print(f"\n  📊 {result['stock_code']}")
        print(f"     总分: {result['total_score']}/100")
        print(f"     信号: {result['signal']}")
        print(f"     Buffett分: {result['dimensions']['B_Buffett']}")
    
    # 纯Buffett风格
    print("\n" + "="*70)
    print("【纯Buffett价值风格】")
    vc_buffett = ValueCellBuffett('value')
    for stock in test_stocks:
        result = vc_buffett.analyze(stock['code'], stock['metrics'])
        print(f"\n  📊 {result['stock_code']}")
        print(f"     总分: {result['total_score']}/100")
        print(f"     信号: {result['signal']}")
        print(f"     护城河: {result['buffett_details']['moat']:.1f}")
        print(f"     安全边际: {result['dimensions']['S_Safety']:.1f}")
    
    print("\n" + "="*70)
    print("✅ 冲突解决完成: buffett_value + value_cell = VALUE_CELL v1.2")
    print("="*70)


if __name__ == "__main__":
    demo()
