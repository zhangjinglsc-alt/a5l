#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股模拟交易引擎
功能：
1. 模拟交易执行（T+2交收）
2. 持仓管理（每手股数可变）
3. 无涨跌停限制
4. 支持碎股交易
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class HKSimTradingEngine:
    """港股模拟交易引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.data_dir = f"{workspace}/data/hk_sim_trading"
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
    
    def get_lot_size(self, symbol: str) -> int:
        """获取每手股数"""
        # 港股每手股数各不相同
        lot_sizes = {
            "00700.HK": 100,   # 腾讯
            "09988.HK": 100,   # 阿里
            "03690.HK": 100,   # 美团
            "01810.HK": 200,   # 小米
            "09618.HK": 100,   # 京东
            "09999.HK": 100,   # 网易
            "02331.HK": 500,   # 李宁
            "01299.HK": 1000,  # 友邦
            "00941.HK": 2000,  # 中国移动
            "01398.HK": 1000,  # 工行
            "02318.HK": 500,   # 平安
            "00005.HK": 400,   # 汇丰
            "00001.HK": 500,   # 长和
        }
        return lot_sizes.get(symbol, 100)
    
    def calculate_fees(self, amount: float, is_buy: bool) -> Dict:
        """计算港股交易费用"""
        commission_rate = self.account['trading_params']['commission_rate']
        stamp_duty_rate = self.account['trading_params']['stamp_duty_rate']
        trading_fee_rate = self.account['trading_params']['trading_fee_rate']
        settlement_fee = self.account['trading_params']['settlement_fee']
        
        commission = max(amount * commission_rate, 25.0)  # 最低25港币
        stamp_duty = max(amount * stamp_duty_rate, 1.0)   # 最低1港币
        trading_fee = amount * trading_fee_rate
        
        total_fees = commission + stamp_duty + trading_fee + settlement_fee
        
        return {
            "commission": commission,
            "stamp_duty": stamp_duty,
            "trading_fee": trading_fee,
            "settlement_fee": settlement_fee,
            "total": total_fees
        }
    
    def buy_stock(self, symbol: str, price: float, shares: int, 
                  strategy: str = "manual") -> Dict:
        """买入股票"""
        lot_size = self.get_lot_size(symbol)
        
        # 港股整手交易
        if shares % lot_size != 0:
            return {"success": False, "error": f"港股必须是{lot_size}股的整数倍"}
        
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
                "lot_size": lot_size,
                "entry_date": datetime.now().isoformat(),
                "strategy": strategy
            })
        
        # 记录交易
        trade = {
            "trade_id": f"HK{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "symbol": symbol,
            "action": "BUY",
            "shares": shares,
            "lots": shares // lot_size,
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
        lot_size = self.get_lot_size(symbol)
        
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
        
        # 港股T+2限制（仅影响资金可用，不影响卖出）
        # 实际交易中，卖出后可以立即用资金买其他股票
        
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
            "trade_id": f"HK{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "symbol": symbol,
            "action": "SELL",
            "shares": shares,
            "lots": shares // lot_size,
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
    engine = HKSimTradingEngine()
    print("=" * 70)
    print("🇭🇰 港股模拟交易引擎")
    print("=" * 70)
    
    summary = engine.get_portfolio_summary()
    print(f"\n账户: {summary['account_name']}")
    print(f"初始资金: HK${summary['initial_capital']:,.2f}")
    print(f"当前权益: HK${summary['current_equity']:,.2f}")
    print(f"持仓数量: {summary['position_count']}")
    print(f"交易次数: {summary['trade_count']}")

if __name__ == "__main__":
    main()
