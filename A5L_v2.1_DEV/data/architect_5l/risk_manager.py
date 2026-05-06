#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 10: 实时风控系统
Real-time Risk Management with Greeks & Stress Testing
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"          # 🟢
    MEDIUM = "medium"    # 🟡
    HIGH = "high"        # 🟠
    CRITICAL = "critical" # 🔴

@dataclass
class RiskMetrics:
    """风险指标"""
    portfolio_delta: float
    portfolio_gamma: float
    portfolio_theta: float
    portfolio_vega: float
    portfolio_rho: float
    var_95: float
    var_99: float
    expected_shortfall: float
    beta: float
    correlation_risk: float
    liquidity_score: float
    concentration_risk: float

class RealtimeRiskManager:
    """实时风控管理器"""
    
    def __init__(self):
        self.risk_limits = {
            "max_position_size": 0.20,      # 单股最大20%
            "max_sector_exposure": 0.50,    # 行业最大50%
            "max_portfolio_var": 0.05,      # 组合VaR最大5%
            "max_drawdown": 0.15,           # 最大回撤15%
            "max_leverage": 2.0,            # 最大杠杆2倍
            "min_liquidity_score": 0.3      # 最低流动性分数
        }
        
        self.circuit_breakers = {
            "daily_loss_limit": 0.05,       # 日亏损5%熔断
            "consecutive_losses": 3,        # 连续3笔亏损暂停
            "volatility_spike": 0.50        # 波动率飙升50%暂停
        }
        
        self.risk_history = []
        self.violations = []
        
    def calculate_greeks(self, positions: List[Dict], 
                        market_data: Dict) -> Dict:
        """
        计算期权希腊字母 (简化版，适用于股票组合)
        
        对于股票:
        - Delta: 价格敏感度
        - Gamma: Delta变化率
        - Theta: 时间衰减
        - Vega: 波动率敏感度
        """
        greeks = {
            "delta": 0,
            "gamma": 0,
            "theta": 0,
            "vega": 0,
            "rho": 0
        }
        
        total_value = sum(p.get("market_value", 0) for p in positions)
        
        for pos in positions:
            symbol = pos["symbol"]
            value = pos.get("market_value", 0)
            weight = value / total_value if total_value > 0 else 0
            
            # 模拟希腊字母计算
            volatility = market_data.get(symbol, {}).get("volatility", 0.2)
            
            # Delta ≈ 股票价格变动1%带来的组合价值变动
            greeks["delta"] += weight * random.uniform(0.8, 1.2)
            
            # Gamma (二阶导数)
            greeks["gamma"] += weight * random.uniform(-0.1, 0.1)
            
            # Theta (时间衰减，股票近似为股息)
            greeks["theta"] += weight * random.uniform(-0.001, 0.001)
            
            # Vega (波动率敏感度)
            greeks["vega"] += weight * volatility * random.uniform(0.5, 1.5)
            
            # Rho (利率敏感度)
            greeks["rho"] += weight * random.uniform(-0.01, 0.01)
        
        return greeks
    
    def calculate_var(self, positions: List[Dict],
                     confidence: float = 0.95) -> Tuple[float, float]:
        """
        计算风险价值 (VaR)
        
        使用参数法 (方差-协方差法)
        VaR = Portfolio_Value * Z * σ
        """
        total_value = sum(p.get("market_value", 0) for p in positions)
        
        # 计算组合波动率 (简化)
        portfolio_volatility = 0.0
        for pos in positions:
            vol = pos.get("volatility", 0.2)
            weight = pos.get("market_value", 0) / total_value if total_value > 0 else 0
            portfolio_volatility += (weight * vol) ** 2
        
        portfolio_volatility = portfolio_volatility ** 0.5
        
        # Z分数
        z_scores = {0.95: 1.645, 0.99: 2.326}
        z = z_scores.get(confidence, 1.645)
        
        var = total_value * z * portfolio_volatility
        
        return var, portfolio_volatility
    
    def stress_test(self, positions: List[Dict],
                   scenarios: List[Dict]) -> Dict:
        """
        压力测试
        
        模拟极端市场情景下的组合表现
        """
        print(f"\n🧪 压力测试")
        print("-" * 70)
        
        results = []
        total_value = sum(p.get("market_value", 0) for p in positions)
        
        for scenario in scenarios:
            name = scenario["name"]
            market_shock = scenario["market_shock"]
            sector_impacts = scenario.get("sector_impacts", {})
            
            # 计算组合损失
            portfolio_loss = 0
            
            for pos in positions:
                symbol = pos["symbol"]
                value = pos.get("market_value", 0)
                sector = pos.get("sector", "other")
                
                # 基础市场冲击
                base_impact = market_shock
                
                # 行业特定冲击
                sector_impact = sector_impacts.get(sector, 0)
                
                # 个股特定冲击
                stock_impact = random.uniform(-0.05, 0.05)
                
                total_impact = base_impact + sector_impact + stock_impact
                loss = value * total_impact
                portfolio_loss += loss
            
            loss_pct = portfolio_loss / total_value if total_value > 0 else 0
            
            results.append({
                "scenario": name,
                "loss_amount": portfolio_loss,
                "loss_pct": loss_pct,
                "remaining_capital": total_value + portfolio_loss,
                "survival": loss_pct > -0.5  # 损失超过50%视为无法承受
            })
            
            status = "✅ 可承受" if loss_pct > -0.5 else "❌ 无法承受"
            print(f"{name:20s}: {loss_pct:+.1%} {status}")
        
        return {
            "scenarios_tested": len(scenarios),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_risk_limits(self, positions: List[Dict]) -> List[Dict]:
        """检查风险限制"""
        violations = []
        
        total_value = sum(p.get("market_value", 0) for p in positions)
        
        # 1. 单股集中度检查
        for pos in positions:
            symbol = pos["symbol"]
            weight = pos.get("market_value", 0) / total_value if total_value > 0 else 0
            
            if weight > self.risk_limits["max_position_size"]:
                violations.append({
                    "level": RiskLevel.HIGH,
                    "type": "concentration",
                    "message": f"{symbol} 集中度 {weight:.1%} 超过限制 {self.risk_limits['max_position_size']:.1%}",
                    "action": "reduce_position"
                })
        
        # 2. VaR检查
        var_95, _ = self.calculate_var(positions, 0.95)
        var_pct = var_95 / total_value if total_value > 0 else 0
        
        if var_pct > self.risk_limits["max_portfolio_var"]:
            violations.append({
                "level": RiskLevel.CRITICAL,
                "type": "var",
                "message": f"VaR(95%) {var_pct:.1%} 超过限制 {self.risk_limits['max_portfolio_var']:.1%}",
                "action": "hedge_or_reduce"
            })
        
        # 3. 流动性检查
        for pos in positions:
            liquidity = pos.get("liquidity_score", 1.0)
            if liquidity < self.risk_limits["min_liquidity_score"]:
                violations.append({
                    "level": RiskLevel.MEDIUM,
                    "type": "liquidity",
                    "message": f"{pos['symbol']} 流动性不足 {liquidity:.2f}",
                    "action": "monitor"
                })
        
        return violations
    
    def check_circuit_breakers(self, portfolio_stats: Dict) -> Optional[Dict]:
        """检查熔断条件"""
        
        # 1. 日亏损检查
        daily_pnl_pct = portfolio_stats.get("daily_pnl_pct", 0)
        if daily_pnl_pct < -self.circuit_breakers["daily_loss_limit"]:
            return {
                "triggered": True,
                "reason": "daily_loss_limit",
                "message": f"日亏损 {daily_pnl_pct:.1%} 超过限制 {self.circuit_breakers['daily_loss_limit']:.1%}",
                "action": "halt_trading"
            }
        
        # 2. 连续亏损检查
        consecutive_losses = portfolio_stats.get("consecutive_losses", 0)
        if consecutive_losses >= self.circuit_breakers["consecutive_losses"]:
            return {
                "triggered": True,
                "reason": "consecutive_losses",
                "message": f"连续 {consecutive_losses} 笔亏损",
                "action": "pause_trading"
            }
        
        # 3. 波动率飙升检查
        vol_spike = portfolio_stats.get("volatility_spike", 0)
        if vol_spike > self.circuit_breakers["volatility_spike"]:
            return {
                "triggered": True,
                "reason": "volatility_spike",
                "message": f"波动率飙升 {vol_spike:.0%}",
                "action": "reduce_exposure"
            }
        
        return {"triggered": False}
    
    def generate_risk_report(self, positions: List[Dict]) -> Dict:
        """生成风险报告"""
        
        # 计算各项指标
        greeks = self.calculate_greeks(positions, {})
        var_95, vol = self.calculate_var(positions, 0.95)
        var_99, _ = self.calculate_var(positions, 0.99)
        violations = self.check_risk_limits(positions)
        
        total_value = sum(p.get("market_value", 0) for p in positions)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "portfolio_value": total_value,
            "greeks": greeks,
            "var": {
                "95": var_95,
                "99": var_99,
                "95_pct": var_95 / total_value if total_value > 0 else 0,
                "99_pct": var_99 / total_value if total_value > 0 else 0
            },
            "portfolio_volatility": vol,
            "violations": len(violations),
            "violation_details": violations,
            "risk_score": max(0, 100 - len(violations) * 20),
            "status": "healthy" if not violations else "warning"
        }


def demo():
    """实时风控演示"""
    print("=" * 70)
    print("🛡️ A5L Week 10: 实时风控系统演示")
    print("=" * 70)
    
    risk_manager = RealtimeRiskManager()
    
    # 模拟持仓
    positions = [
        {"symbol": "000066", "market_value": 200000, "volatility": 0.25, "sector": "tech", "liquidity_score": 0.8},
        {"symbol": "601975", "market_value": 150000, "volatility": 0.30, "sector": "energy", "liquidity_score": 0.6},
        {"symbol": "688981", "market_value": 180000, "volatility": 0.35, "sector": "tech", "liquidity_score": 0.7},
        {"symbol": "002436", "market_value": 120000, "volatility": 0.28, "sector": "tech", "liquidity_score": 0.5},
        {"symbol": "300708", "market_value": 100000, "volatility": 0.32, "sector": "manufacturing", "liquidity_score": 0.4},
    ]
    
    # 演示1: 希腊字母计算
    print("\n【演示1: 组合希腊字母】")
    print("-" * 70)
    
    greeks = risk_manager.calculate_greeks(positions, {})
    print(f"   Delta: {greeks['delta']:.4f} (价格敏感度)")
    print(f"   Gamma: {greeks['gamma']:.4f} (二阶敏感度)")
    print(f"   Theta: {greeks['theta']:.4f} (时间衰减)")
    print(f"   Vega:  {greeks['vega']:.4f} (波动率敏感度)")
    print(f"   Rho:   {greeks['rho']:.4f} (利率敏感度)")
    
    # 演示2: VaR计算
    print("\n【演示2: 风险价值 (VaR)】")
    print("-" * 70)
    
    var_95, vol = risk_manager.calculate_var(positions, 0.95)
    var_99, _ = risk_manager.calculate_var(positions, 0.99)
    total_value = sum(p.get("market_value", 0) for p in positions)
    
    print(f"   组合价值: ¥{total_value:,.2f}")
    print(f"   组合波动率: {vol:.1%}")
    print(f"   VaR(95%): ¥{var_95:,.2f} ({var_95/total_value:.1%})")
    print(f"   VaR(99%): ¥{var_99:,.2f} ({var_99/total_value:.1%})")
    print(f"   含义: 有95%概率单日损失不超过¥{var_95:,.2f}")
    
    # 演示3: 压力测试
    print("\n【演示3: 压力测试】")
    print("-" * 70)
    
    scenarios = [
        {"name": "2008金融危机", "market_shock": -0.40, "sector_impacts": {"tech": -0.50, "energy": -0.45}},
        {"name": "2020疫情冲击", "market_shock": -0.35, "sector_impacts": {"tech": -0.20, "energy": -0.60}},
        {"name": "利率急升", "market_shock": -0.20, "sector_impacts": {"tech": -0.30, "energy": 0.10}},
        {"name": "地缘冲突", "market_shock": -0.25, "sector_impacts": {"tech": -0.15, "energy": 0.30}},
        {"name": "市场崩盘", "market_shock": -0.50, "sector_impacts": {"tech": -0.55, "energy": -0.50}},
    ]
    
    stress_results = risk_manager.stress_test(positions, scenarios)
    
    # 演示4: 风险限制检查
    print("\n【演示4: 风险限制检查】")
    print("-" * 70)
    
    violations = risk_manager.check_risk_limits(positions)
    
    if violations:
        print(f"⚠️  发现 {len(violations)} 项风险违规:")
        for v in violations:
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[v["level"].value]
            print(f"   {emoji} [{v['level'].value.upper()}] {v['message']}")
            print(f"      建议操作: {v['action']}")
    else:
        print("✅ 所有风险指标正常")
    
    # 演示5: 熔断检查
    print("\n【演示5: 熔断机制检查】")
    print("-" * 70)
    
    # 模拟触发熔断
    portfolio_stats = {
        "daily_pnl_pct": -0.06,  # 超过5%限制
        "consecutive_losses": 2,
        "volatility_spike": 0.3
    }
    
    circuit = risk_manager.check_circuit_breakers(portfolio_stats)
    
    if circuit.get("triggered"):
        print(f"🔴 熔断触发!")
        print(f"   原因: {circuit['message']}")
        print(f"   动作: {circuit['action']}")
    else:
        print("✅ 未触发熔断")
    
    # 演示6: 风险报告
    print("\n【演示6: 风险报告】")
    print("-" * 70)
    
    report = risk_manager.generate_risk_report(positions)
    
    print(f"风险评分: {report['risk_score']}/100")
    print(f"状态: {report['status'].upper()}")
    print(f"违规数: {report['violations']}")
    
    print("\n" + "=" * 70)
    print("✅ 实时风控系统演示完成!")
    print("=" * 70)
    print("\n💡 生产环境增强:")
    print("   • 实时希腊字母计算")
    print("   • 蒙特卡洛VaR模拟")
    print("   • 极值理论 (EVT)")
    print("   •  Copula模型相关性风险")


if __name__ == "__main__":
    demo()
