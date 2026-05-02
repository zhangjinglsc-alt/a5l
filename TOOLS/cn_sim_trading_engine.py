#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股模拟交易引擎
功能：
1. 模拟交易执行（含印花税、T+1规则）
2. 持仓管理（100股整数倍）
3. 涨跌停保护
4. 盈亏计算
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CNSimTradingEngine:
    """A股模拟交易引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.data_dir = f"{workspace}/data/cn_sim_trading"
        self.account_file = f"{self.data_dir}/accounts/account_main.json"
        self.trades_file = f"{self.data_dir}/trades/trade_history.json"
        self.positions_file = f"{self.data_dir}/positions/current_positions.json"
        
        self.account = self._load_account()
        self.trades = self._load_trades()
        self.positions = self._load_positions()
    
    def _load_account(self) -> Dict:
        with open(self.account_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_trades(self) -> Dict:
        with open(self.trades_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_positions(self) -> Dict:
        with open(self.positions_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_account(self):
        with open(self.account_file, 'w', encoding='utf-8') as f:
            json.dump(self.account, f, indent=2, ensure_ascii=False)
    
    def _save_trades(self):
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)
    
    def _save_positions(self):
        with open(self.positions_file, 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, indent=2, ensure_ascii=False)
    
    def calculate_fees(self, amount: float, is_buy: bool) -> Dict:
        """计算A股交易费用"""
        commission_rate = self.account['trading_params']['commission_rate']
        stamp_duty_rate = self.account['trading_params']['stamp_duty_rate'] if not is_buy else 0
        transfer_fee_rate = self.account['trading_params']['transfer_fee_rate']
        
        commission = max(amount * commission_rate, 5.0)  # 最低5元
        stamp_duty = amount * stamp_duty_rate
        transfer_fee = amount * transfer_fee_rate
        
        total_fees = commission + stamp_duty + transfer_fee
        
        return {
            "commission": commission,
            "stamp_duty": stamp_duty,
            "transfer_fee": transfer_fee,
            "total": total_fees
        }
    
    def check_price_limit(self, symbol: str, price: float, prev_close: float) -> bool:
        """检查涨跌停限制"""
        if ".SH" in symbol or ".SZ" in symbol:
            code = symbol.split('.')[0]
            # 科创板 20%
            if code.startswith('688'):
                limit_pct = 0.20
            # ST股 5%
            elif code.startswith('ST') or code.startswith('*ST'):
                limit_pct = 0.05
            # 普通A股 10%
            else:
                limit_pct = 0.10
            
            upper_limit = prev_close * (1 + limit_pct)
            lower_limit = prev_close * (1 - limit_pct)
            
            return lower_limit <= price <= upper_limit
        return True
    
    def buy_stock(self, symbol: str, price: float, shares: int, 
                  strategy: str = "manual") -> Dict:
        """买入股票"""
        # A股必须是100的整数倍
        if shares % 100 != 0:
            return {"success": False, "error": "A股交易必须是100股的整数倍"}
        
        amount = price * shares
        fees = self.calculate_fees(amount, is_buy=True)
        total_cost = amount + fees['total']
        
        # 检查资金
        if total_cost > self.account['current_status']['available_funds']:
            return {"success": False, "error": "资金不足"}
        
        # 检查持仓限制
        if len(self.positions['positions']) >= self.account['trading_params']['max_positions']:
            return {"success": False, "error": "超出最大持仓数量限制"}
        
        # 执行交易
        self.account['current_status']['cash'] -= total_cost
        self.account['current_status']['available_funds'] -= total_cost
        
        # 更新持仓
        position_found = False
        for pos in self.positions['positions']:
            if pos['symbol'] == symbol:
                pos['shares'] += shares
                pos['cost_basis'] = (pos['cost_basis'] * pos['shares'] + amount) / (pos['shares'] + shares)
                position_found = True
                break
        
        if not position_found:
            self.positions['positions'].append({
                "symbol": symbol,
                "shares": shares,
                "cost_basis": price,
                "entry_date": datetime.now().isoformat(),
                "strategy": strategy
            })
        
        # 记录交易
        trade = {
            "trade_id": f"CN{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "symbol": symbol,
            "action": "BUY",
            "shares": shares,
            "price": price,
            "amount": amount,
            "fees": fees,
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy
        }
        self.trades['trades'].append(trade)
        self.trades['trade_count'] += 1
        self.trades['total_commission'] += fees['commission']
        self.trades['total_stamp_duty'] += fees['stamp_duty']
        
        self._save_account()
        self._save_positions()
        self._save_trades()
        
        return {"success": True, "trade": trade}
    
    def sell_stock(self, symbol: str, price: float, shares: int,
                   strategy: str = "manual") -> Dict:
        """卖出股票"""
        # 检查持仓
        position = None
        for pos in self.positions['positions']:
            if pos['symbol'] == symbol:
                position = pos
                break
        
        if not position:
            return {"success": False, "error": "未持有该股票"}
        
        if shares > position['shares']:
            return {"success": False, "error": "持仓不足"}
        
        # A股T+1限制
        entry_date = datetime.fromisoformat(position['entry_date'])
        if (datetime.now() - entry_date).days < 1:
            return {"success": False, "error": "A股T+1规则：今日买入不能卖出"}
        
        amount = price * shares
        fees = self.calculate_fees(amount, is_buy=False)
        net_proceeds = amount - fees['total']
        
        # 计算盈亏
        cost = shares * position['cost_basis']
        pnl = amount - cost - fees['total']
        pnl_pct = (pnl / cost) * 100 if cost > 0 else 0
        
        # 更新账户
        self.account['current_status']['cash'] += net_proceeds
        self.account['current_status']['available_funds'] += net_proceeds
        
        # 更新持仓
        position['shares'] -= shares
        if position['shares'] == 0:
            self.positions['positions'].remove(position)
        
        # 记录交易
        trade = {
            "trade_id": f"CN{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "symbol": symbol,
            "action": "SELL",
            "shares": shares,
            "price": price,
            "amount": amount,
            "fees": fees,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy
        }
        self.trades['trades'].append(trade)
        self.trades['trade_count'] += 1
        self.trades['total_commission'] += fees['commission']
        self.trades['total_stamp_duty'] += fees['stamp_duty']
        
        self._save_account()
        self._save_positions()
        self._save_trades()
        
        return {"success": True, "trade": trade, "pnl": pnl}
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        return {
            "account_id": self.account['account_id'],
            "account_name": self.account['account_name'],
            "initial_capital": self.account['initial_capital'],
            "current_equity": self.account['current_status']['total_equity'],
            "cash": self.account['current_status']['cash'],
            "market_value": self.account['current_status']['market_value'],
            "total_pnl": self.account['current_status']['total_equity'] - self.account['initial_capital'],
            "total_pnl_pct": ((self.account['current_status']['total_equity'] - self.account['initial_capital']) / self.account['initial_capital']) * 100,
            "position_count": len(self.positions['positions']),
            "trade_count": self.trades['trade_count'],
            "updated_at": datetime.now().isoformat()
        }

def main():
    """演示"""
    engine = CNSimTradingEngine()
    print("=" * 70)
    print("🇨🇳 A股模拟交易引擎")
    print("=" * 70)
    
    summary = engine.get_portfolio_summary()
    print(f"\n账户: {summary['account_name']}")
    print(f"初始资金: ¥{summary['initial_capital']:,.2f}")
    print(f"当前权益: ¥{summary['current_equity']:,.2f}")
    print(f"持仓数量: {summary['position_count']}")
    print(f"交易次数: {summary['trade_count']}")

if __name__ == "__main__":
    main()
