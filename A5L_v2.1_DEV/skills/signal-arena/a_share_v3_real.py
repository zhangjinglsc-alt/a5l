#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Signal Arena - A股模拟交易监控器 (v3.0)
修复版：接入AKShare真实数据源
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import akshare as ak

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class RealPriceDataSource:
    """真实价格数据源"""
    
    @staticmethod
    def get_a_stock_price(symbol: str) -> Dict:
        """获取A股真实价格"""
        try:
            # 使用AKShare获取实时行情
            spot_df = ak.stock_zh_a_spot_em()
            stock_data = spot_df[spot_df["代码"] == symbol]
            
            if not stock_data.empty:
                return {
                    "symbol": symbol,
                    "price": float(stock_data["最新价"].values[0]),
                    "open": float(stock_data["开盘价"].values[0]),
                    "high": float(stock_data["最高价"].values[0]),
                    "low": float(stock_data["最低价"].values[0]),
                    "prev_close": float(stock_data["昨收"].values[0]),
                    "volume": int(stock_data["成交量"].values[0]),
                    "change_pct": float(stock_data["涨跌幅"].values[0]),
                    "source": "akshare_real"
                }
        except Exception as e:
            logger.error(f"获取{symbol}价格失败: {e}")
        return None
    
    @staticmethod
    def get_hk_stock_price(symbol: str) -> Dict:
        """获取港股真实价格"""
        try:
            # 使用AKShare获取港股实时行情
            hk_spot = ak.stock_hk_spot_em()
            stock_data = hk_spot[hk_spot["代码"] == symbol]
            
            if not stock_data.empty:
                return {
                    "symbol": symbol,
                    "price": float(stock_data["最新价"].values[0]),
                    "open": float(stock_data["开盘价"].values[0]),
                    "high": float(stock_data["最高价"].values[0]),
                    "low": float(stock_data["最低价"].values[0]),
                    "prev_close": float(stock_data["昨收"].values[0]),
                    "volume": int(stock_data["成交量"].values[0]) if "成交量" in stock_data.columns else 0,
                    "change_pct": float(stock_data["涨跌幅"].values[0]) if "涨跌幅" in stock_data.columns else 0,
                    "source": "akshare_real"
                }
        except Exception as e:
            logger.error(f"获取港股{symbol}价格失败: {e}")
        return None


class AShareTradeSimulatorV3:
    """A股模拟交易器 v3.0 - 真实数据版"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.portfolio_file = self.data_dir / "a_portfolio.json"
        self.trades_file = self.data_dir / "a_trades.json"
        
        self.portfolio = self._load_portfolio()
        self.trades = self._load_trades()
        self.price_source = RealPriceDataSource()
        
    def _load_portfolio(self) -> Dict:
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "cash": 5000000.0,  # 初始资金500万人民币
            "positions": {},
            "total_value": 5000000.0,
            "last_updated": datetime.now().isoformat(),
            "version": "3.0_real_data"
        }
    
    def _load_trades(self) -> List:
        if self.trades_file.exists():
            with open(self.trades_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_portfolio(self):
        self.portfolio["last_updated"] = datetime.now().isoformat()
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, indent=2, ensure_ascii=False)
    
    def _save_trades(self):
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)
    
    def execute_trade(self, symbol: str, action: str, quantity: int) -> bool:
        """执行交易"""
        price_data = self.price_source.get_a_stock_price(symbol)
        if not price_data:
            logger.error(f"无法获取{symbol}价格，交易取消")
            return False
        
        price = price_data["price"]
        amount = price * quantity
        commission = amount * 0.0003  # 手续费0.03%
        
        if action == "BUY":
            total_cost = amount + commission
            if self.portfolio["cash"] < total_cost:
                logger.warning(f"资金不足，无法买入{symbol}")
                return False
            
            # 更新持仓
            if symbol not in self.portfolio["positions"]:
                self.portfolio["positions"][symbol] = {
                    "quantity": 0, "avg_cost": 0
                }
            
            pos = self.portfolio["positions"][symbol]
            total_quantity = pos["quantity"] + quantity
            total_cost_basis = pos["quantity"] * pos["avg_cost"] + amount
            pos["quantity"] = total_quantity
            pos["avg_cost"] = total_cost_basis / total_quantity if total_quantity > 0 else 0
            
            self.portfolio["cash"] -= total_cost
            
        elif action == "SELL":
            if symbol not in self.portfolio["positions"] or self.portfolio["positions"][symbol]["quantity"] < quantity:
                logger.warning(f"持仓不足，无法卖出{symbol}")
                return False
            
            revenue = amount - commission
            self.portfolio["positions"][symbol]["quantity"] -= quantity
            self.portfolio["cash"] += revenue
            
            if self.portfolio["positions"][symbol]["quantity"] == 0:
                del self.portfolio["positions"][symbol]
        
        # 记录交易
        trade = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "commission": commission,
            "source": "real_data"
        }
        self.trades.append(trade)
        
        self._save_portfolio()
        self._save_trades()
        
        logger.info(f"{action} {symbol} {quantity}股 @ {price}")
        return True


if __name__ == "__main__":
    simulator = AShareTradeSimulatorV3()
    print("A股模拟交易器 v3.0 已加载（真实数据源）")
    print(f"当前现金: {simulator.portfolio['cash']:,.2f}")
    print(f"持仓数量: {len(simulator.portfolio['positions'])}")
