#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 4: Position Manager
决策信号层 - 仓位管理器

功能：
1. 仓位计算和分配
2. 风险敞口控制
3. 止损/止盈管理
4. 仓位再平衡
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Position:
    """持仓"""
    symbol: str
    shares: int
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None

@dataclass
class Portfolio:
    """投资组合"""
    account_id: str
    total_equity: float
    available_cash: float
    positions: Dict[str, Position]
    total_market_value: float
    total_unrealized_pnl: float
    risk_exposure: float  # 风险敞口比例

class PositionManager:
    """仓位管理器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.config_file = f"{workspace}/ARCHITECT_5L/layer4_decision/config/position_config.json"
        
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载仓位配置"""
        default_config = {
            "max_position_per_stock": 0.10,  # 单股最大10%
            "max_total_positions": 20,        # 最大持仓数
            "default_stop_loss_pct": 0.07,    # 默认止损7%
            "default_take_profit_pct": 0.25,  # 默认止盈25%
            "position_sizing": {
                "strong_signal": 0.10,        # 强信号10%仓位
                "moderate_signal": 0.06,      # 中信号6%仓位
                "weak_signal": 0.03           # 弱信号3%仓位
            },
            "risk_limits": {
                "max_daily_loss_pct": 0.10,   # 单日最大亏损10%
                "max_consecutive_losses": 3,  # 连续亏损3次暂停
                "max_portfolio_drawdown": 0.15  # 最大回撤15%
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return {**default_config, **json.load(f)}
        
        # 保存默认配置
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def calculate_position_size(self, portfolio: Portfolio, symbol: str,
                               signal_strength: str, current_price: float,
                               risk_level: str) -> Dict:
        """
        计算建议仓位
        
        Returns:
            仓位建议
        """
        # 基于信号强度确定仓位比例
        if signal_strength == "strong":
            position_pct = self.config["position_sizing"]["strong_signal"]
        elif signal_strength == "moderate":
            position_pct = self.config["position_sizing"]["moderate_signal"]
        else:
            position_pct = self.config["position_sizing"]["weak_signal"]
        
        # 风险调整
        if risk_level == "high":
            position_pct *= 0.5  # 高风险减半
        elif risk_level == "low":
            position_pct *= 1.2  # 低风险可增加20%
        
        # 确保不超过最大仓位限制
        position_pct = min(position_pct, self.config["max_position_per_stock"])
        
        # 计算金额和股数
        position_value = portfolio.total_equity * position_pct
        available_for_trade = min(position_value, portfolio.available_cash)
        
        shares = int(available_for_trade / current_price)
        actual_value = shares * current_price
        
        # 计算止损止盈价格
        stop_loss_pct = self.config["default_stop_loss_pct"]
        if risk_level == "high":
            stop_loss_pct = 0.03  # 高风险3%止损
        elif risk_level == "low":
            stop_loss_pct = 0.08  # 低风险8%止损
        
        stop_loss_price = current_price * (1 - stop_loss_pct)
        take_profit_price = current_price * (1 + self.config["default_take_profit_pct"])
        
        return {
            "symbol": symbol,
            "recommended_shares": shares,
            "recommended_value": actual_value,
            "position_pct_of_equity": actual_value / portfolio.total_equity if portfolio.total_equity > 0 else 0,
            "stop_loss_price": round(stop_loss_price, 2),
            "take_profit_price": round(take_profit_price, 2),
            "stop_loss_pct": stop_loss_pct,
            "take_profit_pct": self.config["default_take_profit_pct"],
            "risk_level": risk_level,
            "signal_strength": signal_strength
        }
    
    def check_risk_limits(self, portfolio: Portfolio) -> List[Dict]:
        """检查风险限制"""
        alerts = []
        
        # 检查单日亏损
        daily_pnl_pct = portfolio.total_unrealized_pnl / portfolio.total_equity if portfolio.total_equity > 0 else 0
        if daily_pnl_pct < -self.config["risk_limits"]["max_daily_loss_pct"]:
            alerts.append({
                "type": "daily_loss_limit",
                "severity": "critical",
                "message": f"单日亏损 {daily_pnl_pct:.1%} 超过限制 {self.config['risk_limits']['max_daily_loss_pct']:.0%}",
                "action": "建议暂停交易，检查持仓"
            })
        
        # 检查最大回撤
        # 简化计算：基于未实现盈亏
        if portfolio.risk_exposure > self.config["risk_limits"]["max_portfolio_drawdown"]:
            alerts.append({
                "type": "drawdown_limit",
                "severity": "warning",
                "message": f"风险敞口 {portfolio.risk_exposure:.1%} 接近限制",
                "action": "建议减仓或对冲"
            })
        
        # 检查持仓集中度
        if portfolio.positions:
            max_position_value = max(p.market_value for p in portfolio.positions.values())
            max_position_pct = max_position_value / portfolio.total_market_value if portfolio.total_market_value > 0 else 0
            
            if max_position_pct > self.config["max_position_per_stock"]:
                alerts.append({
                    "type": "concentration_limit",
                    "severity": "warning",
                    "message": f"单股持仓 {max_position_pct:.1%} 超过限制 {self.config['max_position_per_stock']:.0%}",
                    "action": "建议减仓"
                })
        
        return alerts
    
    def generate_position_report(self, portfolio: Portfolio) -> str:
        """生成仓位报告"""
        report = f"""# 📊 仓位管理报告

**账户**: {portfolio.account_id}  
**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 💰 账户概览

| 指标 | 数值 |
|------|------|
| 总资产 | ¥{portfolio.total_equity:,.2f} |
| 可用现金 | ¥{portfolio.available_cash:,.2f} |
| 持仓市值 | ¥{portfolio.total_market_value:,.2f} |
| 未实现盈亏 | ¥{portfolio.total_unrealized_pnl:,.2f} ({portfolio.total_unrealized_pnl/portfolio.total_equity*100 if portfolio.total_equity > 0 else 0:+.2f}%) |
| 风险敞口 | {portfolio.risk_exposure:.1%} |

---

## 📈 持仓明细

| 代码 | 股数 | 成本价 | 现价 | 市值 | 盈亏 | 盈亏% |
|------|------|--------|------|------|------|-------|
"""
        
        for symbol, pos in portfolio.positions.items():
            report += f"| {symbol} | {pos.shares:,} | ¥{pos.avg_cost:.2f} | ¥{pos.current_price:.2f} | ¥{pos.market_value:,.2f} | ¥{pos.unrealized_pnl:,.2f} | {pos.unrealized_pnl_pct:+.2f}% |\n"
        
        # 风险检查
        alerts = self.check_risk_limits(portfolio)
        if alerts:
            report += """
---

## ⚠️ 风险警告

"""
            for alert in alerts:
                icon = "🔴" if alert["severity"] == "critical" else "🟡"
                report += f"""{icon} **{alert['type']}**
- 消息: {alert['message']}
- 建议: {alert['action']}

"""
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("📊 仓位管理器 (Layer 4)")
    print("=" * 70)
    
    manager = PositionManager()
    
    # 演示仓位计算
    print("\n🧪 测试仓位计算...")
    
    portfolio = Portfolio(
        account_id="CN_SIM_001",
        total_equity=1000000,
        available_cash=500000,
        positions={},
        total_market_value=500000,
        total_unrealized_pnl=25000,
        risk_exposure=0.08
    )
    
    recommendation = manager.calculate_position_size(
        portfolio=portfolio,
        symbol="000001.SZ",
        signal_strength="strong",
        current_price=10.5,
        risk_level="medium"
    )
    
    print(f"\n  标的: {recommendation['symbol']}")
    print(f"  建议股数: {recommendation['recommended_shares']:,}")
    print(f"  建议金额: ¥{recommendation['recommended_value']:,.2f}")
    print(f"  仓位比例: {recommendation['position_pct_of_equity']:.1%}")
    print(f"  止损价: ¥{recommendation['stop_loss_price']}")
    print(f"  止盈价: ¥{recommendation['take_profit_price']}")
    
    # 风险检查
    print("\n⚠️ 风险检查:")
    alerts = manager.check_risk_limits(portfolio)
    if alerts:
        for alert in alerts:
            print(f"  [{alert['severity']}] {alert['message']}")
    else:
        print("  ✅ 无风险警告")

if __name__ == "__main__":
    main()
