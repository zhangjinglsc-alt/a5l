#!/usr/bin/env python3
"""
A5L Chief Security Officer (CSO) - 合规检查与风控系统
Layer 0 核心组件

功能:
- 持仓集中度实时监控
- 止损线自动检测
- 异常交易告警
- 合规报告生成

执行时间: 2026-05-04 01:26 (立即实施模式)
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple

WORKSPACE = "/workspace/projects/workspace"
LOG_FILE = f"{WORKSPACE}/logs/cso_compliance.log"
ALERT_FILE = f"{WORKSPACE}/data/alerts/compliance_alerts.json"

class ComplianceChecker:
    """
    CSO合规检查器
    
    检查项:
    1. 单一持仓集中度 ≤ 20%
    2. 前三大持仓集中度 ≤ 50%
    3. 个股止损线 (-10%)
    4. 组合单日跌幅 (-5%熔断)
    5. 行业集中度 ≤ 40%
    """
    
    # 合规阈值
    THRESHOLDS = {
        'single_stock_max': 0.20,      # 单一持仓最大20%
        'top3_max': 0.50,               # 前三大持仓最大50%
        'industry_max': 0.40,           # 行业集中度最大40%
        'stop_loss': -0.10,             # 个股止损线-10%
        'circuit_breaker': -0.05,       # 组合熔断线-5%
        'position_warning': 0.30        # 持仓警告线30%
    }
    
    def __init__(self):
        os.makedirs(os.path.dirname(ALERT_FILE), exist_ok=True)
        self.log("="*70)
        self.log("CSO合规检查系统初始化")
        self.log("="*70)
        
        # 当前持仓
        self.positions = [
            {'code': '000066', 'name': '中国长城', 'weight': 0.367, 'industry': '信创', 'pnl': 0.10},
            {'code': '601975', 'name': '招商南油', 'weight': 0.367, 'industry': '航运', 'pnl': 0.00},
            {'code': '688981', 'name': '中芯国际', 'weight': 0.026, 'industry': '半导体', 'pnl': -0.0224},
        ]
        
        self.total_capital = 3770000
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def check_concentration_risk(self) -> Dict:
        """检查持仓集中度风险"""
        self.log("\n🔍 检查持仓集中度...")
        
        violations = []
        warnings = []
        
        # 按权重排序
        sorted_positions = sorted(self.positions, key=lambda x: x['weight'], reverse=True)
        
        # 检查单一持仓
        for pos in sorted_positions:
            if pos['weight'] > self.THRESHOLDS['single_stock_max']:
                violation = {
                    'type': 'SINGLE_STOCK_OVER_LIMIT',
                    'stock': pos['name'],
                    'code': pos['code'],
                    'current_weight': f"{pos['weight']*100:.1f}%",
                    'limit': f"{self.THRESHOLDS['single_stock_max']*100:.0f}%",
                    'severity': 'HIGH',
                    'action': 'REDUCE_POSITION'
                }
                violations.append(violation)
                self.log(f"  🚨 违规: {pos['name']} 持仓{pos['weight']*100:.1f}% > 限制{self.THRESHOLDS['single_stock_max']*100:.0f}%")
            elif pos['weight'] > self.THRESHOLDS['position_warning']:
                warning = {
                    'type': 'SINGLE_STOCK_WARNING',
                    'stock': pos['name'],
                    'code': pos['code'],
                    'current_weight': f"{pos['weight']*100:.1f}%",
                    'threshold': f"{self.THRESHOLDS['position_warning']*100:.0f}%"
                }
                warnings.append(warning)
                self.log(f"  ⚠️  警告: {pos['name']} 持仓{pos['weight']*100:.1f}% 接近限制")
        
        # 检查前三大持仓
        top3_weight = sum(p['weight'] for p in sorted_positions[:3])
        if top3_weight > self.THRESHOLDS['top3_max']:
            violation = {
                'type': 'TOP3_OVER_LIMIT',
                'current_weight': f"{top3_weight*100:.1f}%",
                'limit': f"{self.THRESHOLDS['top3_max']*100:.0f}%",
                'severity': 'MEDIUM',
                'action': 'REBALANCE'
            }
            violations.append(violation)
            self.log(f"  🚨 违规: 前三大持仓{top3_weight*100:.1f}% > 限制{self.THRESHOLDS['top3_max']*100:.0f}%")
        
        return {
            'violations': violations,
            'warnings': warnings,
            'max_single_position': sorted_positions[0]['weight'] if sorted_positions else 0,
            'top3_concentration': top3_weight,
            'status': 'PASS' if not violations else 'VIOLATION'
        }
    
    def check_stop_loss(self) -> Dict:
        """检查止损线"""
        self.log("\n🔍 检查止损线...")
        
        violations = []
        
        for pos in self.positions:
            if pos['pnl'] <= self.THRESHOLDS['stop_loss']:
                violation = {
                    'type': 'STOP_LOSS_TRIGGERED',
                    'stock': pos['name'],
                    'code': pos['code'],
                    'pnl': f"{pos['pnl']*100:.1f}%",
                    'stop_loss': f"{self.THRESHOLDS['stop_loss']*100:.0f}%",
                    'severity': 'CRITICAL',
                    'action': 'SELL_IMMEDIATELY'
                }
                violations.append(violation)
                self.log(f"  🚨 止损触发: {pos['name']} 盈亏{pos['pnl']*100:.1f}% ≤ 止损线{self.THRESHOLDS['stop_loss']*100:.0f}%")
            elif pos['pnl'] <= -0.05:  # 警告线-5%
                self.log(f"  ⚠️  接近止损: {pos['name']} 盈亏{pos['pnl']*100:.1f}%")
        
        return {
            'violations': violations,
            'status': 'PASS' if not violations else 'VIOLATION'
        }
    
    def check_industry_concentration(self) -> Dict:
        """检查行业集中度"""
        self.log("\n🔍 检查行业集中度...")
        
        # 按行业汇总
        industry_weights = {}
        for pos in self.positions:
            industry = pos['industry']
            industry_weights[industry] = industry_weights.get(industry, 0) + pos['weight']
        
        violations = []
        for industry, weight in industry_weights.items():
            if weight > self.THRESHOLDS['industry_max']:
                violation = {
                    'type': 'INDUSTRY_OVER_LIMIT',
                    'industry': industry,
                    'current_weight': f"{weight*100:.1f}%",
                    'limit': f"{self.THRESHOLDS['industry_max']*100:.0f}%",
                    'severity': 'MEDIUM',
                    'action': 'DIVERSIFY'
                }
                violations.append(violation)
                self.log(f"  🚨 违规: {industry} 行业占比{weight*100:.1f}% > 限制{self.THRESHOLDS['industry_max']*100:.0f}%")
        
        return {
            'violations': violations,
            'industry_weights': {k: f"{v*100:.1f}%" for k, v in industry_weights.items()},
            'status': 'PASS' if not violations else 'VIOLATION'
        }
    
    def circuit_breaker_check(self, daily_pnl: float = 0) -> Dict:
        """
        熔断检查
        
        Args:
            daily_pnl: 当日组合盈亏 (-0.05表示-5%)
        """
        self.log("\n🔍 检查熔断线...")
        
        # 模拟当日跌幅 (实际应从数据源获取)
        if daily_pnl <= self.THRESHOLDS['circuit_breaker']:
            self.log(f"  🚨 熔断触发: 当日跌幅{daily_pnl*100:.1f}% ≤ 熔断线{self.THRESHOLDS['circuit_breaker']*100:.0f}%")
            return {
                'triggered': True,
                'daily_pnl': f"{daily_pnl*100:.1f}%",
                'circuit_breaker': f"{self.THRESHOLDS['circuit_breaker']*100:.0f}%",
                'action': 'TRADING_HALT',
                'duration': '当日剩余时间'
            }
        
        self.log(f"  ✅ 熔断检查通过")
        return {'triggered': False}
    
    def generate_compliance_report(self) -> Dict:
        """生成合规报告"""
        self.log("\n" + "="*70)
        self.log("CSO合规检查报告")
        self.log("="*70)
        
        # 执行所有检查
        concentration = self.check_concentration_risk()
        stop_loss = self.check_stop_loss()
        industry = self.check_industry_concentration()
        circuit = self.circuit_breaker_check()
        
        # 汇总违规
        all_violations = []
        all_violations.extend(concentration.get('violations', []))
        all_violations.extend(stop_loss.get('violations', []))
        all_violations.extend(industry.get('violations', []))
        
        # 计算合规得分
        checks = ['concentration', 'stop_loss', 'industry']
        passed = sum([
            concentration['status'] == 'PASS',
            stop_loss['status'] == 'PASS',
            industry['status'] == 'PASS'
        ])
        compliance_score = (passed / len(checks)) * 100
        
        self.log(f"\n📊 合规评分: {compliance_score:.0f}/100")
        self.log(f"  检查通过: {passed}/{len(checks)}")
        self.log(f"  违规项: {len(all_violations)}")
        
        if all_violations:
            self.log(f"\n🚨 违规列表:")
            for v in all_violations:
                self.log(f"  [{v['severity']}] {v['type']}: {v.get('stock', v.get('industry', 'N/A'))}")
                self.log(f"    建议操作: {v['action']}")
        
        # 生成报告
        report = {
            'report_type': 'CSO_COMPLIANCE_CHECK',
            'generated_at': datetime.now().isoformat(),
            'compliance_score': round(compliance_score, 1),
            'status': 'COMPLIANT' if compliance_score == 100 else 'NON_COMPLIANT',
            'checks': {
                'concentration': concentration,
                'stop_loss': stop_loss,
                'industry': industry,
                'circuit_breaker': circuit
            },
            'violations': all_violations,
            'summary': {
                'high_risk_count': len([v for v in all_violations if v.get('severity') == 'HIGH']),
                'critical_count': len([v for v in all_violations if v.get('severity') == 'CRITICAL']),
                'immediate_action_required': len([v for v in all_violations if v.get('severity') in ['HIGH', 'CRITICAL']]) > 0
            }
        }
        
        # 保存报告
        report_file = f"{WORKSPACE}/data/compliance_report_{datetime.now().strftime('%Y%m%d')}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"\n✅ 报告已保存: {report_file}")
        
        return report
    
    def send_alert(self, report: Dict):
        """发送告警 (模拟)"""
        if report['summary']['immediate_action_required']:
            self.log("\n🚨 立即行动告警")
            self.log("  检测到高风险违规，需要立即处理!")
            # TODO: 集成飞书消息发送
        else:
            self.log("\n✅ 无立即行动项")


def main():
    """主函数"""
    print("="*70)
    print("🛡️ CSO合规检查与风控系统")
    print("Layer 0 - Chief Security Officer")
    print("="*70)
    
    cso = ComplianceChecker()
    report = cso.generate_compliance_report()
    cso.send_alert(report)
    
    print("\n" + "="*70)
    print(f"✅ 合规检查完成")
    print(f"  合规评分: {report['compliance_score']}/100")
    print(f"  状态: {'合规' if report['status'] == 'COMPLIANT' else '不合规'}")
    print(f"  需立即处理: {'是' if report['summary']['immediate_action_required'] else '否'}")
    print("="*70)


if __name__ == "__main__":
    main()
