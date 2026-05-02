#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美股模拟交易引擎
功能：
1. 模拟交易执行
2. 持仓管理
3. 盈亏计算
4. 风控检查
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class USSimTradingEngine:
    """美股模拟交易引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.data_dir = f"{workspace}/data/us_sim_trading"
        self.account_file = f"{self.data_dir}/accounts/account_main.json"
        self.trades_file = f"{self.data_dir}/trades/trade_history.json"
        self.positions_file = f"{self.data_dir}/positions/current_positions.json"
        
        self.account = self._load_account()
        self.trades = self._load_trades()
        self.positions = self._load_positions()
    
    def _load_account(self) -> Dict:
        """加载账户信息"""
        with open(self.account_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_trades(self) -> Dict:
        """加载交易记录"""
        with open(self.trades_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_positions(self) -> Dict:
        """加载持仓信息"""
        with open(self.positions_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_account(self):
        """保存账户信息"""
        with open(self.account_file, 'w', encoding='utf-8') as f:
            json.dump(self.account, f, indent=2, ensure_ascii=False)
    
    def _save_trades(self):
        """保存交易记录"""
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)
    
    def _save_positions(self):
        """保存持仓信息"""
        with open(self.positions_file, 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, indent=2, ensure_ascii=False)
    
    def get_account_summary(self) -> Dict:
        """获取账户摘要"""
        status = self.account['current_status']
        return {
            "初始资金": self.account['initial_capital'],
            "当前现金": status['cash'],
            "持仓市值": status['market_value'],
            "总资产": status['total_equity'],
            "可用资金": status['available_funds'],
            "盈亏": status['total_equity'] - self.account['initial_capital'],
            "盈亏比例": (status['total_equity'] - self.account['initial_capital']) / self.account['initial_capital'] * 100
        }
    
    def get_position_summary(self) -> Dict:
        """获取持仓摘要"""
        return self.positions['position_summary']
    
    def get_trade_stats(self) -> Dict:
        """获取交易统计"""
        return self.trades['trade_stats']
    
    def execute_buy(self, symbol: str, quantity: int, price: float, 
                   strategy: str = "manual", reason: str = "") -> Dict:
        """执行买入"""
        # 计算交易成本
        amount = quantity * price
        commission = amount * self.account['trading_params']['commission_rate']
        total_cost = amount + commission
        
        # 检查资金
        if total_cost > self.account['current_status']['available_funds']:
            return {"success": False, "error": "资金不足"}
        
        # 创建交易记录
        trade = {
            "trade_id": f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "symbol": symbol,
            "action": "BUY",
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "commission": commission,
            "total_cost": total_cost,
            "strategy": strategy,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        # 更新持仓
        existing_position = None
        for pos in self.positions['positions']:
            if pos['symbol'] == symbol:
                existing_position = pos
                break
        
        if existing_position:
            # 加仓
            total_qty = existing_position['quantity'] + quantity
            avg_cost = (existing_position['cost_basis'] + total_cost) / total_qty
            existing_position['quantity'] = total_qty
            existing_position['avg_cost'] = avg_cost
            existing_position['cost_basis'] = avg_cost * total_qty
        else:
            # 新建仓
            self.positions['positions'].append({
                "symbol": symbol,
                "quantity": quantity,
                "avg_cost": price,
                "cost_basis": total_cost,
                "current_price": price,
                "market_value": amount,
                "unrealized_pnl": -commission,
                "unrealized_pnl_pct": -commission / total_cost * 100,
                "opened_at": datetime.now().isoformat()
            })
        
        # 更新账户
        self.account['current_status']['cash'] -= total_cost
        self._update_account_status()
        
        # 保存交易记录
        self.trades['trades'].append(trade)
        self._update_trade_stats()
        
        # 保存所有数据
        self._save_account()
        self._save_trades()
        self._save_positions()
        
        return {"success": True, "trade": trade}
    
    def execute_sell(self, symbol: str, quantity: int, price: float,
                    reason: str = "") -> Dict:
        """执行卖出"""
        # 查找持仓
        position = None
        for pos in self.positions['positions']:
            if pos['symbol'] == symbol:
                position = pos
                break
        
        if not position or position['quantity'] < quantity:
            return {"success": False, "error": "持仓不足"}
        
        # 计算交易结果
        amount = quantity * price
        commission = amount * self.account['trading_params']['commission_rate']
        net_proceeds = amount - commission
        cost_basis_sold = position['avg_cost'] * quantity
        realized_pnl = net_proceeds - cost_basis_sold
        realized_pnl_pct = realized_pnl / cost_basis_sold * 100
        
        # 创建交易记录
        trade = {
            "trade_id": f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "symbol": symbol,
            "action": "SELL",
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "commission": commission,
            "net_proceeds": net_proceeds,
            "cost_basis_sold": cost_basis_sold,
            "realized_pnl": realized_pnl,
            "realized_pnl_pct": realized_pnl_pct,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        # 更新持仓
        position['quantity'] -= quantity
        position['cost_basis'] = position['avg_cost'] * position['quantity']
        
        if position['quantity'] == 0:
            self.positions['positions'] = [p for p in self.positions['positions'] if p['symbol'] != symbol]
        
        # 更新账户
        self.account['current_status']['cash'] += net_proceeds
        self._update_account_status()
        
        # 保存交易记录
        self.trades['trades'].append(trade)
        self._update_trade_stats()
        
        # 保存所有数据
        self._save_account()
        self._save_trades()
        self._save_positions()
        
        return {"success": True, "trade": trade, "realized_pnl": realized_pnl}
    
    def _update_account_status(self):
        """更新账户状态"""
        total_market_value = sum(p.get('market_value', 0) for p in self.positions['positions'])
        self.account['current_status']['market_value'] = total_market_value
        self.account['current_status']['total_equity'] = self.account['current_status']['cash'] + total_market_value
        self.account['current_status']['available_funds'] = self.account['current_status']['cash']
        self.account['current_status']['updated_at'] = datetime.now().isoformat()
    
    def _update_trade_stats(self):
        """更新交易统计"""
        trades = self.trades['trades']
        if not trades:
            return
        
        # 只统计已平仓的交易（卖出交易）
        closed_trades = [t for t in trades if 'realized_pnl' in t]
        
        winning_trades = [t for t in closed_trades if t['realized_pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['realized_pnl'] <= 0]
        
        total_pnl = sum(t['realized_pnl'] for t in closed_trades) if closed_trades else 0
        
        self.trades['trade_stats'] = {
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(trades) * 100 if trades else 0,
            "total_pnl": total_pnl,
            "total_pnl_pct": total_pnl / self.account['initial_capital'] * 100,
            "avg_win": sum(t['realized_pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            "avg_loss": sum(t['realized_pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0,
            "largest_single_win": max((t['realized_pnl'] for t in winning_trades), default=0),
            "largest_single_loss": min((t['realized_pnl'] for t in losing_trades), default=0)
        }
    
    def generate_weekly_report(self) -> str:
        """生成周报"""
        account = self.get_account_summary()
        trades = self.get_trade_stats()
        
        report = f"""
📊 美股模拟交易周报
{'='*50}

💰 账户概况
初始资金: ${account['初始资金']:,.2f}
当前总资产: ${account['总资产']:,.2f}
累计盈亏: ${account['盈亏']:+,.2f} ({account['盈亏比例']:+.2f}%)
可用资金: ${account['可用资金']:,.2f}

📈 交易统计
总交易次数: {trades['total_trades']}
盈利次数: {trades['winning_trades']}
亏损次数: {trades['losing_trades']}
胜率: {trades['win_rate']:.1f}%

💵 盈亏详情
总盈亏: ${trades['total_pnl']:+,.2f}
平均盈利: ${trades['avg_win']:,.2f}
平均亏损: ${trades['avg_loss']:,.2f}
最大单笔盈利: ${trades['largest_single_win']:,.2f}
最大单笔亏损: ${trades['largest_single_loss']:,.2f}

📊 当前持仓
{self._format_positions()}

{'='*50}
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return report
    
    def _format_positions(self) -> str:
        """格式化持仓信息"""
        if not self.positions['positions']:
            return "当前无持仓"
        
        lines = ["代码\t数量\t均价\t市值\t盈亏\t盈亏率"]
        for pos in self.positions['positions']:
            lines.append(f"{pos['symbol']}\t{pos['quantity']}\t${pos['avg_cost']:.2f}\t${pos['market_value']:,.2f}\t${pos['unrealized_pnl']:+.2f}\t{pos['unrealized_pnl_pct']:+.2f}%")
        return "\n".join(lines)

if __name__ == "__main__":
    engine = USSimTradingEngine()
    print(engine.generate_weekly_report())
