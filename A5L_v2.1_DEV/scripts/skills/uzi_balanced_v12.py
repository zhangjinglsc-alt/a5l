#!/usr/bin/env python3
"""
A5L UZI-Skill v1.2 - Bearish vs Yangguan平衡器
冲突解决: bearish_perspective vs yangguan_daodao → UZI多评委整合

核心创新: 多时间框架 + 多空双视角 + 动态平衡

执行时间: 2026-05-04 02:02
作者: Chief Architect (Conflict Resolution)
"""

import os
import json
from typing import Dict, List
from datetime import datetime

WORKSPACE = "/workspace/projects/workspace"
DATA_DIR = f"{WORKSPACE}/data/analysis/uzi_balanced"

class UZIBalancedAnalyzer:
    """
    UZI平衡分析器 v1.2
    
    整合: 空方视角(风险审查) + 阳关大道(超短交易)
    
    输出: 时间框架清晰的平衡建议
    """
    
    # 时间框架定义
    TIMEFRAMES = {
        'ultra_short': {'days': 1, 'weight': 0.2},    # 超短线 (阳关)
        'short': {'days': 5, 'weight': 0.25},         # 短线
        'medium': {'days': 20, 'weight': 0.3},        # 中线
        'long': {'days': 60, 'weight': 0.25}          # 长线 (价值投资)
    }
    
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        print("UZI-Skill v1.2 Balanced Analyzer初始化")
        print("整合: Bearish Perspective + 阳关大道 = 多时间框架平衡")
    
    def bearish_analysis(self, stock_code: str, data: Dict) -> Dict:
        """
        空方视角分析 - 风险审查
        """
        risks = []
        score_deduction = 0
        
        # 估值风险
        pe = data.get('pe_ttm', 20)
        if pe > 50:
            risks.append({'type': '估值泡沫', 'level': 'HIGH', 'deduct': 20})
            score_deduction += 20
        elif pe > 30:
            risks.append({'type': '估值偏高', 'level': 'MEDIUM', 'deduct': 10})
            score_deduction += 10
        
        # 财务风险
        debt = data.get('debt_ratio', 40)
        if debt > 70:
            risks.append({'type': '高负债', 'level': 'HIGH', 'deduct': 15})
            score_deduction += 15
        
        # 经营风险
        if data.get('revenue_decline', False):
            risks.append({'type': '收入下滑', 'level': 'HIGH', 'deduct': 20})
            score_deduction += 20
        
        # 市场风险
        beta = data.get('beta', 1.0)
        if beta > 1.5:
            risks.append({'type': '高波动', 'level': 'MEDIUM', 'deduct': 10})
            score_deduction += 10
        
        # 周期风险
        if data.get('is_cyclical', False):
            risks.append({'type': '周期性强', 'level': 'MEDIUM', 'deduct': 8})
            score_deduction += 8
        
        return {
            'base_score': 100,
            'score_after_deduction': max(0, 100 - score_deduction),
            'risks_identified': risks,
            'risk_level': 'HIGH' if score_deduction > 30 else 'MEDIUM' if score_deduction > 15 else 'LOW',
            'bearish_view': 'AVOID' if score_deduction > 30 else 'CAUTION' if score_deduction > 15 else 'ACCEPTABLE'
        }
    
    def yangguan_analysis(self, stock_code: str, data: Dict) -> Dict:
        """
        阳关大道分析 - 超短交易信号
        """
        signals = []
        
        # 量价信号
        volume_spike = data.get('volume_ratio', 1.0) > 2.0
        price_break = data.get('price_vs_ma20', 0) > 5
        
        if volume_spike and price_break:
            signals.append({'signal': '放量突破', 'strength': 'STRONG_BUY', 'score': 90})
        elif volume_spike:
            signals.append({'signal': '放量整理', 'strength': 'WATCH', 'score': 60})
        
        # 技术指标
        rsi = data.get('rsi_14', 50)
        if rsi > 70:
            signals.append({'signal': 'RSI超买', 'strength': 'SELL', 'score': 30})
        elif rsi < 30:
            signals.append({'signal': 'RSI超卖', 'strength': 'BUY', 'score': 80})
        
        # 资金流向
        fund_flow = data.get('main_force_flow', 0)
        if fund_flow > 1000000:  # 1M+流入
            signals.append({'signal': '主力流入', 'strength': 'BUY', 'score': 85})
        elif fund_flow < -1000000:
            signals.append({'signal': '主力流出', 'strength': 'SELL', 'score': 25})
        
        # 计算平均信号强度
        if signals:
            avg_score = sum(s['score'] for s in signals) / len(signals)
        else:
            avg_score = 50
        
        return {
            'signals': signals,
            'composite_score': avg_score,
            'yangguan_view': 'BUY' if avg_score >= 70 else 'HOLD' if avg_score >= 50 else 'SELL',
            'timeframe': 'ultra_short (1-3 days)'
        }
    
    def timeframe_analysis(self, stock_code: str, data: Dict) -> Dict:
        """
        多时间框架分析
        """
        results = {}
        
        for tf_name, tf_config in self.TIMEFRAMES.items():
            # 根据时间框架调整数据权重
            if tf_name == 'ultra_short':
                # 超短线: 阳关信号主导
                bearish_weight = 0.3
                yangguan_weight = 0.7
            elif tf_name == 'long':
                # 长线: 空方视角主导
                bearish_weight = 0.8
                yangguan_weight = 0.2
            else:
                # 中线: 平衡
                bearish_weight = 0.5
                yangguan_weight = 0.5
            
            bearish = self.bearish_analysis(stock_code, data)
            yangguan = self.yangguan_analysis(stock_code, data)
            
            # 加权计算
            weighted_score = (
                bearish['score_after_deduction'] * bearish_weight +
                yangguan['composite_score'] * yangguan_weight
            )
            
            results[tf_name] = {
                'score': round(weighted_score, 1),
                'bearish_view': bearish['bearish_view'],
                'yangguan_view': yangguan['yangguan_view'],
                'signal': 'BUY' if weighted_score >= 70 else 'HOLD' if weighted_score >= 50 else 'SELL',
                'weight': tf_config['weight']
            }
        
        return results
    
    def generate_balanced_recommendation(self, stock_code: str, data: Dict) -> Dict:
        """
        生成平衡建议
        """
        # 多时间框架分析
        tf_results = self.timeframe_analysis(stock_code, data)
        
        # 计算加权总分
        total_score = sum(
            r['score'] * r['weight'] 
            for r in tf_results.values()
        )
        
        # 识别冲突
        conflicts = []
        ultra_short = tf_results['ultra_short']['signal']
        long_term = tf_results['long']['signal']
        
        if ultra_short == 'BUY' and long_term == 'SELL':
            conflicts.append({
                'type': '时间框架冲突',
                'description': '短线看涨但长线看跌',
                'resolution': '建议波段操作，设置严格止损'
            })
        elif ultra_short == 'SELL' and long_term == 'BUY':
            conflicts.append({
                'type': '时间框架冲突',
                'description': '短线看跌但长线看好',
                'resolution': '等待回调买入机会'
            })
        
        # 生成综合建议
        recommendation = self._synthesize_recommendation(tf_results, total_score)
        
        return {
            'stock_code': stock_code,
            'timestamp': datetime.now().isoformat(),
            'version': 'UZI-Skill v1.2 Balanced',
            'conflict_resolution': 'bearish + yangguan = timeframe_balanced',
            'timeframe_analysis': tf_results,
            'composite_score': round(total_score, 1),
            'identified_conflicts': conflicts,
            'final_recommendation': recommendation,
            'risk_warning': self._generate_risk_warning(tf_results)
        }
    
    def _synthesize_recommendation(self, tf_results: Dict, total_score: float) -> Dict:
        """综合建议"""
        ultra = tf_results['ultra_short']['signal']
        short = tf_results['short']['signal']
        medium = tf_results['medium']['signal']
        long = tf_results['long']['signal']
        
        # 判断一致性
        buy_count = sum(1 for s in [ultra, short, medium, long] if s == 'BUY')
        sell_count = sum(1 for s in [ultra, short, medium, long] if s == 'SELL')
        
        if buy_count >= 3 and total_score >= 70:
            return {
                'action': 'STRONG_BUY',
                'confidence': 'HIGH',
                'strategy': '全时间框架共振，可重仓',
                'position_size': '70-100%',
                'stop_loss': '8%'
            }
        elif sell_count >= 3 and total_score < 50:
            return {
                'action': 'STRONG_SELL',
                'confidence': 'HIGH',
                'strategy': '全时间框架看空，清仓或做空',
                'position_size': '0%',
                'stop_loss': 'N/A'
            }
        elif ultra == 'BUY' and long == 'SELL':
            return {
                'action': 'TRADE',
                'confidence': 'MEDIUM',
                'strategy': '波段操作，短线交易',
                'position_size': '20-30%',
                'stop_loss': '5%',
                'target': '10-15%'
            }
        else:
            return {
                'action': 'WATCH',
                'confidence': 'LOW',
                'strategy': '信号不一致，观望等待',
                'position_size': '0-10%',
                'stop_loss': 'N/A'
            }
    
    def _generate_risk_warning(self, tf_results: Dict) -> str:
        """生成风险提示"""
        warnings = []
        
        if tf_results['ultra_short']['score'] - tf_results['long']['score'] > 20:
            warnings.append("短期过热，注意回调风险")
        
        if tf_results['long']['bearish_view'] == 'AVOID':
            warnings.append("长线风险较高，不适合长期持有")
        
        return ' | '.join(warnings) if warnings else '无特殊风险提示'


def demo():
    """演示: 冲突解决"""
    print("="*70)
    print("UZI-Skill v1.2 Balanced Analyzer")
    print("冲突解决: bearish_perspective + 阳关大道 = 时间框架平衡")
    print("="*70)
    
    # 测试场景1: 短线热但长线风险
    print("\n【场景1: 招商南油 - 短线机会 vs 长线风险】")
    stock1_data = {
        'pe_ttm': 12.5,
        'debt_ratio': 35,
        'is_cyclical': True,
        'volume_ratio': 2.5,
        'price_vs_ma20': 8,
        'rsi_14': 65,
        'main_force_flow': 1500000,
        'revenue_decline': False,
        'beta': 1.1
    }
    
    analyzer = UZIBalancedAnalyzer()
    result1 = analyzer.generate_balanced_recommendation('601975', stock1_data)
    
    print(f"\n  📊 多时间框架分析:")
    for tf, data in result1['timeframe_analysis'].items():
        print(f"     {tf}: {data['score']:.1f}分 → {data['signal']}")
    
    print(f"\n  📈 综合评分: {result1['composite_score']}/100")
    print(f"  🎯 建议操作: {result1['final_recommendation']['action']}")
    print(f"  💡 策略: {result1['final_recommendation']['strategy']}")
    print(f"  ⚠️  风险: {result1['risk_warning']}")
    
    # 测试场景2: 全框架一致看空
    print("\n" + "="*70)
    print("【场景2: 全时间框架一致看空】")
    stock2_data = {
        'pe_ttm': 80,
        'debt_ratio': 75,
        'is_cyclical': False,
        'volume_ratio': 0.8,
        'price_vs_ma20': -5,
        'rsi_14': 75,
        'main_force_flow': -2000000,
        'revenue_decline': True,
        'beta': 1.6
    }
    
    result2 = analyzer.generate_balanced_recommendation('000XXX', stock2_data)
    
    print(f"\n  📊 多时间框架分析:")
    for tf, data in result2['timeframe_analysis'].items():
        print(f"     {tf}: {data['score']:.1f}分 → {data['signal']}")
    
    print(f"\n  📈 综合评分: {result2['composite_score']}/100")
    print(f"  🎯 建议操作: {result2['final_recommendation']['action']}")
    print(f"  💡 策略: {result2['final_recommendation']['strategy']}")
    
    print("\n" + "="*70)
    print("✅ 冲突解决完成: bearish + yangguan = 多时间框架平衡器")
    print("   空方视角(风险) + 阳关大道(机会) = 清晰的时间框架建议")
    print("="*70)


if __name__ == "__main__":
    demo()
