#!/usr/bin/env python3
"""
A5L 投资信号生成引擎
Goal G010 Step 3

功能:
- 多空信号识别
- 置信度评分系统
- 投资建议生成
- 信号历史追踪

执行时间: 2026-05-04 00:01 (后台模式)
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# A5L工作空间
WORKSPACE = "/workspace/projects/workspace"
SIGNALS_DIR = f"{WORKSPACE}/data/investment_signals"
LOG_FILE = f"{WORKSPACE}/logs/signal_generator.log"

class InvestmentSignalGenerator:
    """投资信号生成器"""
    
    # 信号类型定义
    SIGNAL_BULLISH = "bullish"    # 看多
    SIGNAL_BEARISH = "bearish"    # 看空
    SIGNAL_WATCH = "watch"        # 观望
    
    # 评分维度权重
    WEIGHTS = {
        'industry_position': 0.20,   # 产业链位置
        'policy_support': 0.15,      # 政策支持
        'competition': 0.15,         # 竞争格局
        'demand_trend': 0.20,        # 需求趋势
        'valuation': 0.15,           # 估值水平
        'earnings_expectation': 0.15 # 业绩预期
    }
    
    def __init__(self):
        self.ensure_directories()
        self.log("="*60)
        self.log("A5L 投资信号生成引擎初始化")
        self.log("="*60)
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def ensure_directories(self):
        """确保目录存在"""
        os.makedirs(SIGNALS_DIR, exist_ok=True)
    
    def calculate_confidence(self, factors):
        """
        计算置信度评分
        
        factors: dict with keys matching WEIGHTS
        """
        score = 0
        for factor, value in factors.items():
            if factor in self.WEIGHTS:
                score += value * self.WEIGHTS[factor]
        
        return min(100, max(0, score * 100))  # 0-100分
    
    def get_confidence_level(self, score):
        """获取置信度等级"""
        if score >= 90:
            return "极高", "强烈建议"
        elif score >= 80:
            return "高", "重点关注"
        elif score >= 60:
            return "中", "可观察"
        else:
            return "低", "暂不关注"
    
    def generate_signal(self, entity_id, entity_type, analysis_data):
        """
        生成投资信号
        
        analysis_data: 来自KG分析的数据
        """
        self.log(f"🎯 分析 {entity_id} 的投资信号...")
        
        # 模拟评分因子
        factors = {
            'industry_position': analysis_data.get('industry_position_score', 0.7),
            'policy_support': analysis_data.get('policy_score', 0.6),
            'competition': analysis_data.get('competition_score', 0.5),
            'demand_trend': analysis_data.get('demand_score', 0.7),
            'valuation': analysis_data.get('valuation_score', 0.6),
            'earnings_expectation': analysis_data.get('earnings_score', 0.5)
        }
        
        # 计算置信度
        confidence = self.calculate_confidence(factors)
        level, suggestion = self.get_confidence_level(confidence)
        
        # 确定信号类型
        if confidence >= 70:
            signal_type = self.SIGNAL_BULLISH
            action = "看多"
        elif confidence <= 30:
            signal_type = self.SIGNAL_BEARISH
            action = "看空"
        else:
            signal_type = self.SIGNAL_WATCH
            action = "观望"
        
        # 生成信号
        signal = {
            'signal_id': f"SIG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{entity_id}",
            'entity_id': entity_id,
            'entity_type': entity_type,
            'signal_type': signal_type,
            'action': action,
            'confidence': round(confidence, 2),
            'confidence_level': level,
            'suggestion': suggestion,
            'factors': {k: round(v * 100, 1) for k, v in factors.items()},
            'reasoning': self.generate_reasoning(entity_id, factors, signal_type),
            'generated_at': datetime.now().isoformat(),
            'valid_until': (datetime.now().replace(day=datetime.now().day + 7)).isoformat()
        }
        
        self.log(f"✅ 信号生成: {action} (置信度: {confidence:.1f}分, {level})")
        
        return signal
    
    def generate_reasoning(self, entity_id, factors, signal_type):
        """生成投资建议理由"""
        reasoning = []
        
        # 产业链位置
        if factors['industry_position'] > 0.7:
            reasoning.append("产业链关键位置，具备定价权")
        elif factors['industry_position'] < 0.4:
            reasoning.append("产业链位置边缘，议价能力弱")
        
        # 政策支持
        if factors['policy_support'] > 0.7:
            reasoning.append("政策强力支持，行业景气度上行")
        elif factors['policy_support'] < 0.4:
            reasoning.append("政策风险较大，需关注监管动态")
        
        # 竞争格局
        if factors['competition'] > 0.7:
            reasoning.append("竞争格局良好，龙头地位稳固")
        elif factors['competition'] < 0.4:
            reasoning.append("竞争激烈，盈利能力承压")
        
        # 需求趋势
        if factors['demand_trend'] > 0.7:
            reasoning.append("需求快速增长，市场空间广阔")
        elif factors['demand_trend'] < 0.4:
            reasoning.append("需求疲软，短期承压")
        
        # 估值
        if factors['valuation'] > 0.7:
            reasoning.append("估值合理，安全边际充足")
        elif factors['valuation'] < 0.4:
            reasoning.append("估值偏高，注意回调风险")
        
        # 业绩预期
        if factors['earnings_expectation'] > 0.7:
            reasoning.append("业绩预期向好，超预期概率大")
        elif factors['earnings_expectation'] < 0.4:
            reasoning.append("业绩预期下调，基本面承压")
        
        return reasoning
    
    def generate_signals_batch(self, entities_data):
        """
        批量生成投资信号
        """
        self.log("\n" + "="*60)
        self.log("开始批量生成投资信号")
        self.log("="*60)
        
        signals = []
        
        for entity_data in entities_data:
            try:
                entity_id = entity_data['id']
                entity_type = entity_data['type']
                analysis = entity_data.get('analysis', {})
                
                signal = self.generate_signal(entity_id, entity_type, analysis)
                signals.append(signal)
                
            except Exception as e:
                self.log(f"❌ 生成信号失败: {entity_data.get('id', 'unknown')} - {e}")
        
        # 保存信号
        batch_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        signals_path = os.path.join(SIGNALS_DIR, f"signals_batch_{batch_id}.json")
        
        with open(signals_path, 'w', encoding='utf-8') as f:
            json.dump({
                'batch_id': batch_id,
                'generated_at': datetime.now().isoformat(),
                'signal_count': len(signals),
                'signals': signals
            }, f, ensure_ascii=False, indent=2)
        
        self.log(f"\n✅ 批量信号生成完成: {len(signals)} 个信号")
        self.log(f"📁 保存至: {signals_path}")
        
        return signals
    
    def get_signal_summary(self, signals):
        """获取信号摘要"""
        bullish = [s for s in signals if s['signal_type'] == self.SIGNAL_BULLISH]
        bearish = [s for s in signals if s['signal_type'] == self.SIGNAL_BEARISH]
        watch = [s for s in signals if s['signal_type'] == self.SIGNAL_WATCH]
        
        summary = {
            'total': len(signals),
            'bullish': len(bullish),
            'bearish': len(bearish),
            'watch': len(watch),
            'avg_confidence': sum(s['confidence'] for s in signals) / len(signals) if signals else 0,
            'top_bullish': sorted(bullish, key=lambda x: x['confidence'], reverse=True)[:3],
            'top_bearish': sorted(bearish, key=lambda x: x['confidence'], reverse=True)[:3]
        }
        
        return summary


def main():
    """主函数"""
    print("="*60)
    print("A5L 投资信号生成引擎")
    print("G010 Step 3 - 后台模式")
    print("="*60)
    
    generator = InvestmentSignalGenerator()
    
    # 模拟测试数据
    test_entities = [
        {
            'id': 'stock_NVDA',
            'type': 'stock',
            'analysis': {
                'industry_position_score': 0.95,
                'policy_score': 0.8,
                'competition_score': 0.85,
                'demand_score': 0.95,
                'valuation_score': 0.5,
                'earnings_score': 0.9
            }
        },
        {
            'id': 'stock_TSLA',
            'type': 'stock',
            'analysis': {
                'industry_position_score': 0.8,
                'policy_score': 0.4,
                'competition_score': 0.6,
                'demand_score': 0.7,
                'valuation_score': 0.3,
                'earnings_score': 0.5
            }
        }
    ]
    
    signals = generator.generate_signals_batch(test_entities)
    summary = generator.get_signal_summary(signals)
    
    print("\n" + "="*60)
    print("信号摘要")
    print("="*60)
    print(f"总信号数: {summary['total']}")
    print(f"看多信号: {summary['bullish']}")
    print(f"看空信号: {summary['bearish']}")
    print(f"观望信号: {summary['watch']}")
    print(f"平均置信度: {summary['avg_confidence']:.1f}分")
    print("="*60)


if __name__ == "__main__":
    main()
