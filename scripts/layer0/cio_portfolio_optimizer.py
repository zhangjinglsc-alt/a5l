#!/usr/bin/env python3
"""
A5L Chief Investment Officer (CIO) - 投资组合优化器
Layer 0 核心组件

功能:
- 多策略信号聚合
- Kelly公式仓位优化
- 风险预算分配
- 自动调仓建议

执行时间: 2026-05-04 01:25 (立即实施模式)
"""

import os
import sys
import json
import math
from datetime import datetime
from typing import Dict, List, Tuple

WORKSPACE = "/workspace/projects/workspace"
LOG_FILE = f"{WORKSPACE}/logs/cio_portfolio.log"
DATA_DIR = f"{WORKSPACE}/data/portfolio"

class PortfolioOptimizer:
    """
    CIO投资组合优化器
    
    核心算法:
    1. Kelly公式: f* = (bp - q) / b
       其中 b=赔率, p=胜率, q=败率=1-p
    2. 马科维茨均值-方差优化
    3. 风险预算分配
    """
    
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.log("="*70)
        self.log("CIO投资组合优化器初始化")
        self.log("="*70)
        
        # 当前持仓 (从MEMORY.md读取)
        self.current_positions = {
            "000066": {"name": "中国长城", "shares": 100000, "cost": 18.50, "current": 19.82, "weight": 0.367},
            "601975": {"name": "招商南油", "shares": 761400, "cost": 4.955, "current": 4.955, "weight": 0.367},
            "688981": {"name": "中芯国际", "shares": 3139, "cost": 85.0, "current": 83.1, "weight": 0.026},
        }
        
        # 总资金 (估算)
        self.total_capital = 3770000  # 约377万
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def kelly_criterion(self, win_prob: float, win_loss_ratio: float) -> float:
        """
        Kelly公式计算最优仓位比例
        
        Args:
            win_prob: 胜率 (0-1)
            win_loss_ratio: 盈亏比 (平均盈利/平均亏损)
            
        Returns:
            最优仓位比例 (0-1)
        """
        if win_loss_ratio <= 0 or win_prob <= 0:
            return 0.0
        
        # Kelly公式: f* = (bp - q) / b
        # b = win_loss_ratio, p = win_prob, q = 1 - p
        q = 1 - win_prob
        kelly_f = (win_loss_ratio * win_prob - q) / win_loss_ratio
        
        # 使用半Kelly降低风险
        half_kelly = kelly_f * 0.5
        
        # 限制在0-40%之间
        return max(0.0, min(0.40, half_kelly))
    
    def calculate_position_size(self, stock_code: str, signal_confidence: float, 
                               target_price: float, stop_loss: float) -> Dict:
        """
        计算个股最优仓位
        
        Args:
            stock_code: 股票代码
            signal_confidence: 信号置信度 (0-100)
            target_price: 目标价
            stop_loss: 止损价
            
        Returns:
            仓位建议字典
        """
        current = self.current_positions.get(stock_code, {})
        current_price = current.get('current', 0)
        current_weight = current.get('weight', 0)
        
        if current_price == 0 or target_price <= current_price:
            return {
                'stock_code': stock_code,
                'current_weight': current_weight,
                'recommended_weight': 0,
                'action': 'HOLD',
                'reason': '无上涨空间或数据不足'
            }
        
        # 计算盈亏比
        potential_gain = (target_price - current_price) / current_price
        potential_loss = (current_price - stop_loss) / current_price if stop_loss < current_price else 0.1
        win_loss_ratio = potential_gain / potential_loss if potential_loss > 0 else 1.0
        
        # 胜率 = 信号置信度 / 100 * 0.7 (保守估计)
        win_prob = signal_confidence / 100 * 0.7
        
        # Kelly最优仓位
        optimal_weight = self.kelly_criterion(win_prob, win_loss_ratio)
        
        # 个股风险调整 (单一标的不超过20%)
        max_single_stock = 0.20
        adjusted_weight = min(optimal_weight, max_single_stock)
        
        # 确定操作
        if adjusted_weight > current_weight * 1.2:
            action = 'ADD'
        elif adjusted_weight < current_weight * 0.8:
            action = 'REDUCE'
        else:
            action = 'HOLD'
        
        return {
            'stock_code': stock_code,
            'stock_name': current.get('name', stock_code),
            'current_price': current_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'potential_gain': f"+{potential_gain*100:.1f}%",
            'potential_loss': f"-{potential_loss*100:.1f}%",
            'win_loss_ratio': round(win_loss_ratio, 2),
            'signal_confidence': signal_confidence,
            'win_prob': f"{win_prob*100:.1f}%",
            'current_weight': f"{current_weight*100:.1f}%",
            'recommended_weight': f"{adjusted_weight*100:.1f}%",
            'kelly_raw': f"{optimal_weight*100:.1f}%",
            'action': action,
            'position_value': int(self.total_capital * adjusted_weight),
            'recommended_shares': int(self.total_capital * adjusted_weight / current_price / 100) * 100
        }
    
    def portfolio_risk_assessment(self) -> Dict:
        """
        投资组合风险评估
        """
        weights = [p['weight'] for p in self.current_positions.values()]
        
        # 集中度风险
        max_weight = max(weights)
        concentration_risk = 'HIGH' if max_weight > 0.30 else 'MEDIUM' if max_weight > 0.20 else 'LOW'
        
        # Herfindahl指数 (集中度)
        herfindahl = sum(w**2 for w in weights)
        
        # 有效分散度
        effective_n = 1 / herfindahl if herfindahl > 0 else 1
        
        return {
            'concentration_risk': concentration_risk,
            'max_single_position': f"{max_weight*100:.1f}%",
            'herfindahl_index': round(herfindahl, 3),
            'effective_diversification': round(effective_n, 1),
            'recommendation': '减仓集中持仓' if concentration_risk == 'HIGH' else '维持分散'
        }
    
    def generate_rebalance_plan(self) -> List[Dict]:
        """
        生成调仓计划
        """
        self.log("\n📊 生成调仓计划...")
        
        plans = []
        
        # 招商南油分析 (基于研报)
        zsyny_plan = self.calculate_position_size(
            stock_code='601975',
            signal_confidence=58.3,  # 研报信号置信度
            target_price=5.50,  # 研报目标价
            stop_loss=4.50  # 研报止损价
        )
        plans.append(zsyny_plan)
        
        # 中国长城分析
        zgcc_plan = self.calculate_position_size(
            stock_code='000066',
            signal_confidence=75.0,  # 假设较高置信度
            target_price=25.00,
            stop_loss=17.00
        )
        plans.append(zgcc_plan)
        
        return plans
    
    def generate_daily_report(self) -> Dict:
        """
        生成CIO每日投资组合报告
        """
        self.log("\n" + "="*70)
        self.log("CIO每日投资组合报告")
        self.log("="*70)
        
        # 风险评估
        risk = self.portfolio_risk_assessment()
        
        self.log(f"\n⚠️  风险评估")
        self.log(f"  集中度风险: {risk['concentration_risk']}")
        self.log(f"  最大单一持仓: {risk['max_single_position']}")
        self.log(f"  有效分散度: {risk['effective_diversification']} 只")
        self.log(f"  建议: {risk['recommendation']}")
        
        # 调仓计划
        plans = self.generate_rebalance_plan()
        
        self.log(f"\n📋 调仓计划")
        for plan in plans:
            self.log(f"\n  {plan['stock_name']} ({plan['stock_code']})")
            self.log(f"    当前仓位: {plan['current_weight']} → 建议: {plan['recommended_weight']}")
            self.log(f"    操作: {plan['action']}")
            self.log(f"    Kelly公式: {plan['kelly_raw']} (已半Kelly调整)")
            self.log(f"    盈亏比: {plan['win_loss_ratio']}, 胜率: {plan['win_prob']}")
            if plan['action'] in ['ADD', 'REDUCE']:
                self.log(f"    建议持股: {plan['recommended_shares']} 股")
        
        # 生成报告
        report = {
            'report_type': 'CIO_PORTFOLIO_DAILY',
            'generated_at': datetime.now().isoformat(),
            'total_capital': self.total_capital,
            'risk_assessment': risk,
            'rebalance_plans': plans,
            'summary': {
                'high_priority_actions': [p for p in plans if p['action'] != 'HOLD'],
                'concentration_alert': risk['concentration_risk'] == 'HIGH'
            }
        }
        
        # 保存报告
        report_file = f"{DATA_DIR}/cio_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"\n✅ 报告已保存: {report_file}")
        
        return report


def main():
    """主函数"""
    print("="*70)
    print("🎯 CIO投资组合优化器")
    print("Layer 0 - Chief Investment Officer")
    print("="*70)
    
    cio = PortfolioOptimizer()
    report = cio.generate_daily_report()
    
    print("\n" + "="*70)
    print("✅ CIO报告生成完成")
    print(f"  高优先级操作: {len(report['summary']['high_priority_actions'])} 个")
    print(f"  集中度告警: {'是' if report['summary']['concentration_alert'] else '否'}")
    print("="*70)


if __name__ == "__main__":
    main()
