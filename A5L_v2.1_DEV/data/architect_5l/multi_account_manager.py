#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 6: 多账户管理系统
Multi-Account Manager with unified risk control
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class AccountType(Enum):
    SIMULATION = "simulation"
    PAPER_TRADING = "paper_trading"
    LIVE_TRADING = "live_trading"

class RiskLevel(Enum):
    CONSERVATIVE = "conservative"  # 保守
    MODERATE = "moderate"          # 稳健
    AGGRESSIVE = "aggressive"      # 积极

@dataclass
class Account:
    """账户"""
    account_id: str
    name: str
    account_type: AccountType
    risk_level: RiskLevel
    initial_capital: float
    current_capital: float
    available_cash: float
    positions_value: float
    total_pnl: float
    total_pnl_pct: float
    created_at: str
    is_active: bool = True

class MultiAccountManager:
    """多账户管理器"""
    
    def __init__(self):
        self.accounts = {}
        self.risk_limits = {
            RiskLevel.CONSERVATIVE: {
                "max_position_size": 0.10,  # 单股最大10%
                "max_total_exposure": 0.50,  # 总仓位最大50%
                "max_daily_loss": 0.02,      # 日最大亏损2%
                "stop_loss_pct": 0.05        # 止损5%
            },
            RiskLevel.MODERATE: {
                "max_position_size": 0.20,
                "max_total_exposure": 0.70,
                "max_daily_loss": 0.03,
                "stop_loss_pct": 0.08
            },
            RiskLevel.AGGRESSIVE: {
                "max_position_size": 0.30,
                "max_total_exposure": 0.90,
                "max_daily_loss": 0.05,
                "stop_loss_pct": 0.10
            }
        }
    
    def create_account(self, name: str, account_type: AccountType,
                      risk_level: RiskLevel, initial_capital: float) -> Account:
        """创建账户"""
        account_id = f"ACC{datetime.now().strftime('%Y%m%d%H%M%S')}{len(self.accounts)+1:03d}"
        
        account = Account(
            account_id=account_id,
            name=name,
            account_type=account_type,
            risk_level=risk_level,
            initial_capital=initial_capital,
            current_capital=initial_capital,
            available_cash=initial_capital,
            positions_value=0.0,
            total_pnl=0.0,
            total_pnl_pct=0.0,
            created_at=datetime.now().isoformat()
        )
        
        self.accounts[account_id] = account
        print(f"✅ 账户创建成功: {name} ({account_id})")
        print(f"   类型: {account_type.value} | 风险级别: {risk_level.value}")
        print(f"   初始资金: ${initial_capital:,.2f}")
        
        return account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """获取账户"""
        return self.accounts.get(account_id)
    
    def get_all_accounts(self) -> List[Account]:
        """获取所有账户"""
        return list(self.accounts.values())
    
    def update_account_capital(self, account_id: str, new_capital: float):
        """更新账户资金"""
        if account_id in self.accounts:
            account = self.accounts[account_id]
            account.current_capital = new_capital
            account.total_pnl = new_capital - account.initial_capital
            account.total_pnl_pct = (account.total_pnl / account.initial_capital) * 100
    
    def check_risk_limits(self, account_id: str, symbol: str,
                         quantity: int, price: float) -> Dict:
        """检查风险限制"""
        account = self.accounts.get(account_id)
        if not account:
            return {"passed": False, "reason": "账户不存在"}
        
        limits = self.risk_limits[account.risk_level]
        
        trade_value = quantity * price
        position_pct = trade_value / account.current_capital
        
        # 检查单股仓位限制
        if position_pct > limits["max_position_size"]:
            return {
                "passed": False,
                "reason": f"单股仓位超限 (当前: {position_pct:.1%}, 限制: {limits['max_position_size']:.1%})"
            }
        
        # 检查总仓位限制
        new_exposure = (account.positions_value + trade_value) / account.current_capital
        if new_exposure > limits["max_total_exposure"]:
            return {
                "passed": False,
                "reason": f"总仓位超限 (当前: {new_exposure:.1%}, 限制: {limits['max_total_exposure']:.1%})"
            }
        
        # 检查可用资金
        if trade_value > account.available_cash:
            return {
                "passed": False,
                "reason": f"可用资金不足 (需要: ${trade_value:,.2f}, 可用: ${account.available_cash:,.2f})"
            }
        
        return {"passed": True, "reason": "风险检查通过"}
    
    def get_portfolio_summary(self) -> Dict:
        """获取组合汇总"""
        total_capital = sum(acc.current_capital for acc in self.accounts.values())
        total_initial = sum(acc.initial_capital for acc in self.accounts.values())
        total_pnl = total_capital - total_initial
        total_pnl_pct = (total_pnl / total_initial) * 100 if total_initial > 0 else 0
        
        account_details = []
        for acc in self.accounts.values():
            account_details.append({
                "account_id": acc.account_id,
                "name": acc.name,
                "type": acc.account_type.value,
                "risk_level": acc.risk_level.value,
                "capital": acc.current_capital,
                "pnl": acc.total_pnl,
                "pnl_pct": acc.total_pnl_pct
            })
        
        return {
            "total_accounts": len(self.accounts),
            "total_initial_capital": total_initial,
            "total_current_capital": total_capital,
            "total_pnl": total_pnl,
            "total_pnl_pct": total_pnl_pct,
            "accounts": account_details
        }
    
    def get_risk_report(self) -> Dict:
        """获取风险报告"""
        risk_by_level = {level: [] for level in RiskLevel}
        
        for acc in self.accounts.values():
            risk_by_level[acc.risk_level].append({
                "account_id": acc.account_id,
                "name": acc.name,
                "capital": acc.current_capital
            })
        
        return {
            "risk_distribution": {
                level.value: {
                    "count": len(accounts),
                    "total_capital": sum(a["capital"] for a in accounts)
                }
                for level, accounts in risk_by_level.items()
            },
            "risk_limits": {
                level.value: self.risk_limits[level]
                for level in RiskLevel
            }
        }


def demo():
    """多账户管理演示"""
    print("=" * 70)
    print("👥 A5L Week 6: 多账户管理系统演示")
    print("=" * 70)
    
    manager = MultiAccountManager()
    
    # 创建不同风险级别的账户
    print("\n【创建账户】")
    print("-" * 70)
    
    # 保守型 - 模拟盘
    acc1 = manager.create_account(
        name="保守型模拟盘",
        account_type=AccountType.SIMULATION,
        risk_level=RiskLevel.CONSERVATIVE,
        initial_capital=50000.0
    )
    print()
    
    # 稳健型 - 纸交易
    acc2 = manager.create_account(
        name="稳健型纸交易",
        account_type=AccountType.PAPER_TRADING,
        risk_level=RiskLevel.MODERATE,
        initial_capital=100000.0
    )
    print()
    
    # 积极型 - 模拟盘
    acc3 = manager.create_account(
        name="积极型模拟盘",
        account_type=AccountType.SIMULATION,
        risk_level=RiskLevel.AGGRESSIVE,
        initial_capital=200000.0
    )
    print()
    
    # 模拟资金变动
    print("【更新账户资金】")
    print("-" * 70)
    manager.update_account_capital(acc1.account_id, 52000.0)  # 盈利
    manager.update_account_capital(acc2.account_id, 98000.0)  # 亏损
    manager.update_account_capital(acc3.account_id, 225000.0)  # 大幅盈利
    print("资金已更新")
    print()
    
    # 风险检查测试
    print("【风险检查测试】")
    print("-" * 70)
    
    # 测试1: 保守型账户大额交易 (应被拒绝)
    print("测试1: 保守型账户买入 $20,000 NVDA")
    result = manager.check_risk_limits(acc1.account_id, "NVDA", 20, 1000.0)
    status = "✅ 通过" if result["passed"] else "❌ 拒绝"
    print(f"结果: {status}")
    print(f"原因: {result['reason']}")
    print()
    
    # 测试2: 稳健型账户正常交易 (应通过)
    print("测试2: 稳健型账户买入 $15,000 AAPL")
    result = manager.check_risk_limits(acc2.account_id, "AAPL", 100, 150.0)
    status = "✅ 通过" if result["passed"] else "❌ 拒绝"
    print(f"结果: {status}")
    print(f"原因: {result['reason']}")
    print()
    
    # 组合汇总
    print("【组合汇总】")
    print("-" * 70)
    summary = manager.get_portfolio_summary()
    
    print(f"账户总数: {summary['total_accounts']}")
    print(f"初始总资本: ${summary['total_initial_capital']:,.2f}")
    print(f"当前总资本: ${summary['total_current_capital']:,.2f}")
    
    emoji = "🟢" if summary['total_pnl'] > 0 else "🔴"
    print(f"{emoji} 总盈亏: ${summary['total_pnl']:+.2f} ({summary['total_pnl_pct']:+.2f}%)")
    print()
    
    print("账户明细:")
    for acc in summary['accounts']:
        emoji = "🟢" if acc['pnl'] > 0 else "🔴"
        print(f"  {emoji} {acc['name']} ({acc['risk_level']})")
        print(f"     资本: ${acc['capital']:,.2f} | 盈亏: ${acc['pnl']:+.2f} ({acc['pnl_pct']:+.2f}%)")
    print()
    
    # 风险报告
    print("【风险分布】")
    print("-" * 70)
    risk_report = manager.get_risk_report()
    
    for level, data in risk_report['risk_distribution'].items():
        print(f"{level}: {data['count']}个账户, 总资本: ${data['total_capital']:,.2f}")
    print()
    
    print("【风控规则】")
    print("-" * 70)
    for level, limits in risk_report['risk_limits'].items():
        print(f"{level}:")
        print(f"  单股最大: {limits['max_position_size']:.0%}")
        print(f"  总仓位最大: {limits['max_total_exposure']:.0%}")
        print(f"  日最大亏损: {limits['max_daily_loss']:.0%}")
        print(f"  止损线: {limits['stop_loss_pct']:.0%}")
    
    print("\n" + "=" * 70)
    print("✅ 多账户管理系统演示完成!")
    print("=" * 70)


if __name__ == "__main__":
    demo()
