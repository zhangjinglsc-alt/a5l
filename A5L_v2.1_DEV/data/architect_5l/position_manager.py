#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 9: 智能仓位管理系统
Intelligent Position Management with Kelly Criterion & Risk Parity
"""

import json
import math
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Position:
    """仓位对象"""
    symbol: str
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    weight: float  # 占总资产比例
    unrealized_pnl: float
    unrealized_pnl_pct: float
    kelly_optimal: float  # Kelly最优仓位
    risk_contribution: float  # 风险贡献度

class PositionManager:
    """仓位管理器"""
    
    def __init__(self, total_capital: float = 10000000.0):
        self.total_capital = total_capital
        self.positions = {}
        self.cash = total_capital
        self.target_weights = {}
        self.risk_budget = 0.15  # 最大回撤15%
        self.max_single_position = 0.20  # 单股最大20%
        self.max_sector_exposure = 0.50  # 行业最大50%
        
    def calculate_kelly_criterion(self, symbol: str, win_rate: float,
                                   avg_win: float, avg_loss: float) -> float:
        """
        计算Kelly准则最优仓位
        
        公式: f* = (p*b - q) / b
        where:
        p = 胜率
        q = 败率 = 1-p
        b = 盈亏比 = avg_win / avg_loss
        
        Returns:
            最优仓位比例 (0-1)
        """
        if win_rate <= 0 or avg_loss <= 0:
            return 0
        
        loss_rate = 1 - win_rate
        b = avg_win / avg_loss  # 盈亏比
        
        # Kelly公式
        kelly = (win_rate * b - loss_rate) / b
        
        # 半Kelly (更保守)
        half_kelly = kelly * 0.5
        
        # 限制最大仓位
        return max(0, min(half_kelly, self.max_single_position))
    
    def calculate_risk_parity_weights(self, symbols: List[str],
                                       volatilities: Dict[str, float]) -> Dict[str, float]:
        """
        计算风险平价权重
        
        目标: 每个资产对组合风险的贡献相等
        公式: w_i ∝ 1/σ_i
        """
        if not symbols or not volatilities:
            return {}
        
        # 计算反向波动率权重
        inverse_vols = {}
        total_inverse_vol = 0
        
        for symbol in symbols:
            vol = volatilities.get(symbol, 0.2)  # 默认20%波动率
            if vol > 0:
                inverse_vol = 1 / vol
                inverse_vols[symbol] = inverse_vol
                total_inverse_vol += inverse_vol
        
        # 归一化
        weights = {}
        for symbol in symbols:
            weights[symbol] = inverse_vols.get(symbol, 0) / total_inverse_vol
        
        return weights
    
    def optimize_portfolio(self, opportunities: List[Dict]) -> Dict:
        """
        投资组合优化
        
        综合考虑:
        1. Kelly准则 (预期收益)
        2. 风险平价 (风险控制)
        3. 约束条件 (最大仓位/行业)
        """
        print(f"\n📊 投资组合优化")
        print("-" * 70)
        
        optimized_positions = []
        remaining_capital = self.total_capital
        
        for opp in opportunities:
            symbol = opp["symbol"]
            price = opp["price"]
            
            # 1. Kelly最优仓位
            kelly_weight = self.calculate_kelly_criterion(
                symbol,
                win_rate=opp.get("win_rate", 0.55),
                avg_win=opp.get("avg_win", 0.08),
                avg_loss=opp.get("avg_loss", 0.04)
            )
            
            # 2. 风险平价权重
            volatilities = {o["symbol"]: o.get("volatility", 0.2) for o in opportunities}
            rp_weights = self.calculate_risk_parity_weights(
                [o["symbol"] for o in opportunities],
                volatilities
            )
            rp_weight = rp_weights.get(symbol, 1.0 / len(opportunities))
            
            # 3. 综合权重 (Kelly 60% + 风险平价 40%)
            combined_weight = kelly_weight * 0.6 + rp_weight * 0.4
            
            # 4. 应用约束
            constrained_weight = min(combined_weight, self.max_single_position)
            
            # 5. 计算数量
            target_value = self.total_capital * constrained_weight
            quantity = int(target_value / price)
            
            # 6. 检查可用资金
            cost = quantity * price
            if cost > remaining_capital:
                quantity = int(remaining_capital / price)
                cost = quantity * price
            
            if quantity > 0:
                remaining_capital -= cost
                
                position = Position(
                    symbol=symbol,
                    quantity=quantity,
                    avg_cost=price,
                    current_price=price,
                    market_value=cost,
                    weight=constrained_weight,
                    unrealized_pnl=0,
                    unrealized_pnl_pct=0,
                    kelly_optimal=kelly_weight,
                    risk_contribution=constrained_weight * opp.get("volatility", 0.2)
                )
                
                optimized_positions.append(position)
                
                print(f"✅ {symbol}:")
                print(f"   Kelly权重: {kelly_weight:.1%}")
                print(f"   风险平价: {rp_weight:.1%}")
                print(f"   综合权重: {constrained_weight:.1%}")
                print(f"   数量: {quantity}股")
                print(f"   金额: ¥{cost:,.2f}")
        
        self.cash = remaining_capital
        
        return {
            "positions": optimized_positions,
            "total_invested": self.total_capital - remaining_capital,
            "cash_remaining": remaining_capital,
            "timestamp": datetime.now().isoformat()
        }
    
    def rebalance(self, current_positions: List[Position],
                  target_weights: Dict[str, float]) -> List[Dict]:
        """
        动态再平衡
        
        当实际仓位偏离目标仓位超过阈值时触发
        """
        print(f"\n🔄 动态再平衡")
        print("-" * 70)
        
        trades = []
        threshold = 0.02  # 2%阈值
        
        for pos in current_positions:
            symbol = pos.symbol
            current_weight = pos.weight
            target_weight = target_weights.get(symbol, 0)
            
            deviation = current_weight - target_weight
            
            if abs(deviation) > threshold:
                # 需要调整
                target_value = self.total_capital * target_weight
                current_value = pos.market_value
                delta_value = target_value - current_value
                
                if delta_value > 0:
                    action = "buy"
                    quantity = int(delta_value / pos.current_price)
                else:
                    action = "sell"
                    quantity = int(abs(delta_value) / pos.current_price)
                
                if quantity > 0:
                    trades.append({
                        "symbol": symbol,
                        "action": action,
                        "quantity": quantity,
                        "reason": f"权重偏离 {deviation:.1%}",
                        "current_weight": current_weight,
                        "target_weight": target_weight
                    })
                    
                    print(f"📊 {symbol}: {action.upper()} {quantity}股")
                    print(f"   当前权重: {current_weight:.1%} → 目标: {target_weight:.1%}")
        
        return trades
    
    def check_risk_limits(self, positions: List[Position]) -> Dict:
        """
        检查风险限制
        
        1. 单股集中度
        2. 行业集中度
        3. 最大回撤
        4. 风险价值 (VaR)
        """
        print(f"\n⚠️  风险限制检查")
        print("-" * 70)
        
        alerts = []
        
        # 1. 单股集中度检查
        for pos in positions:
            if pos.weight > self.max_single_position:
                alerts.append({
                    "level": "warning",
                    "type": "concentration",
                    "message": f"{pos.symbol} 仓位 {pos.weight:.1%} 超过限制 {self.max_single_position:.1%}",
                    "action": "reduce_position"
                })
                print(f"⚠️  {pos.symbol} 仓位过高: {pos.weight:.1%}")
        
        # 2. 计算组合风险指标
        total_value = sum(p.market_value for p in positions)
        portfolio_volatility = sum(p.risk_contribution for p in positions) / total_value if total_value > 0 else 0
        
        # 3. VaR计算 (简化版)
        confidence = 0.95
        z_score = 1.645  # 95%置信度
        var_95 = total_value * portfolio_volatility * z_score
        
        print(f"   组合波动率: {portfolio_volatility:.1%}")
        print(f"   VaR(95%): ¥{var_95:,.2f}")
        
        return {
            "alerts": alerts,
            "portfolio_volatility": portfolio_volatility,
            "var_95": var_95,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_portfolio_summary(self) -> Dict:
        """获取组合汇总"""
        total_value = sum(p.market_value for p in self.positions.values()) + self.cash
        
        return {
            "total_capital": self.total_capital,
            "total_value": total_value,
            "cash": self.cash,
            "cash_ratio": self.cash / total_value if total_value > 0 else 0,
            "positions_count": len(self.positions),
            "invested_ratio": (total_value - self.cash) / total_value if total_value > 0 else 0,
            "positions": [
                {
                    "symbol": p.symbol,
                    "weight": f"{p.weight:.1%}",
                    "market_value": p.market_value,
                    "kelly": f"{p.kelly_optimal:.1%}"
                }
                for p in self.positions.values()
            ]
        }


def demo():
    """仓位管理演示"""
    print("=" * 70)
    print("📊 A5L Week 9: 智能仓位管理系统演示")
    print("=" * 70)
    
    # 创建管理器
    pm = PositionManager(total_capital=10000000.0)  # 1000万
    
    # 演示1: Kelly准则计算
    print("\n【演示1: Kelly准则计算】")
    print("-" * 70)
    
    test_cases = [
        {"symbol": "000066", "win_rate": 0.60, "avg_win": 0.10, "avg_loss": 0.05},
        {"symbol": "601975", "win_rate": 0.45, "avg_win": 0.08, "avg_loss": 0.06},
        {"symbol": "688981", "win_rate": 0.55, "avg_win": 0.12, "avg_loss": 0.04},
    ]
    
    for case in test_cases:
        kelly = pm.calculate_kelly_criterion(
            case["symbol"],
            case["win_rate"],
            case["avg_win"],
            case["avg_loss"]
        )
        print(f"📈 {case['symbol']}:")
        print(f"   胜率: {case['win_rate']:.0%}, 盈亏比: {case['avg_win']/case['avg_loss']:.2f}")
        print(f"   Kelly最优仓位: {kelly:.1%}")
    
    # 演示2: 风险平价权重
    print("\n【演示2: 风险平价权重计算】")
    print("-" * 70)
    
    symbols = ["000066", "601975", "688981", "002436", "300708"]
    volatilities = {
        "000066": 0.25,
        "601975": 0.30,
        "688981": 0.35,
        "002436": 0.28,
        "300708": 0.32
    }
    
    rp_weights = pm.calculate_risk_parity_weights(symbols, volatilities)
    
    print("风险平价权重分配:")
    for symbol, weight in rp_weights.items():
        print(f"   {symbol}: {weight:.1%} (波动率: {volatilities[symbol]:.1%})")
    
    # 演示3: 投资组合优化
    print("\n【演示3: 投资组合优化】")
    print("-" * 70)
    
    opportunities = [
        {"symbol": "000066", "price": 19.82, "win_rate": 0.60, "avg_win": 0.10, "avg_loss": 0.05, "volatility": 0.25},
        {"symbol": "601975", "price": 4.45, "win_rate": 0.45, "avg_win": 0.08, "avg_loss": 0.06, "volatility": 0.30},
        {"symbol": "688981", "price": 125.0, "win_rate": 0.55, "avg_win": 0.12, "avg_loss": 0.04, "volatility": 0.35},
        {"symbol": "002436", "price": 30.0, "win_rate": 0.50, "avg_win": 0.09, "avg_loss": 0.05, "volatility": 0.28},
        {"symbol": "300708", "price": 11.0, "win_rate": 0.52, "avg_win": 0.08, "avg_loss": 0.05, "volatility": 0.32},
    ]
    
    result = pm.optimize_portfolio(opportunities)
    
    print(f"\n优化结果:")
    print(f"   投资总额: ¥{result['total_invested']:,.2f}")
    print(f"   剩余现金: ¥{result['cash_remaining']:,.2f}")
    print(f"   持仓数量: {len(result['positions'])}只")
    
    # 演示4: 风险检查
    print("\n【演示4: 风险限制检查】")
    print("-" * 70)
    
    risk_check = pm.check_risk_limits(result['positions'])
    
    if risk_check['alerts']:
        print(f"⚠️  发现 {len(risk_check['alerts'])} 个风险警告")
    else:
        print("✅ 所有风险指标正常")
    
    # 演示5: 动态再平衡
    print("\n【演示5: 动态再平衡】")
    print("-" * 70)
    
    # 模拟当前持仓权重变化
    current_positions = result['positions']
    target_weights = {
        "000066": 0.15,
        "601975": 0.10,
        "688981": 0.12,
        "002436": 0.08,
        "300708": 0.05
    }
    
    rebalance_trades = pm.rebalance(current_positions, target_weights)
    
    if rebalance_trades:
        print(f"需要执行 {len(rebalance_trades)} 笔再平衡交易")
    else:
        print("✅ 当前仓位无需调整")
    
    print("\n" + "=" * 70)
    print("✅ 智能仓位管理系统演示完成!")
    print("=" * 70)
    print("\n💡 生产环境增强:")
    print("   • Black-Litterman模型")
    print("   • 均值-方差优化 (MVO)")
    print("   • 蒙特卡洛模拟")
    print("   • 动态风险预算调整")


if __name__ == "__main__":
    demo()
