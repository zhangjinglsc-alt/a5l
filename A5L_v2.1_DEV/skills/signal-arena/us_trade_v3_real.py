#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美股模拟交易器 v3.0 - 真实数据源版
使用Yahoo Finance获取实时美股价格
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class USStockPriceSource:
    """美股真实价格数据源"""
    
    @staticmethod
    def get_us_stock_price(symbol: str) -> Optional[Dict]:
        """
        获取美股真实价格
        优先使用yfinance，失败时使用akshare
        """
        try:
            # 尝试使用yfinance
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            
            if not data.empty:
                latest = data.iloc[-1]
                prev_close = data.iloc[0]['Open'] if len(data) > 1 else latest['Close']
                change_pct = ((latest['Close'] - prev_close) / prev_close * 100) if prev_close else 0
                
                return {
                    "symbol": symbol,
                    "price": round(float(latest['Close']), 2),
                    "open": round(float(latest['Open']), 2),
                    "high": round(float(latest['High']), 2),
                    "low": round(float(latest['Low']), 2),
                    "prev_close": round(float(prev_close), 2),
                    "volume": int(latest['Volume']),
                    "change_pct": round(change_pct, 2),
                    "source": "yfinance_real",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning(f"yfinance获取{symbol}失败: {e}")
        
        # 降级使用akshare
        try:
            import akshare as ak
            us_spot = ak.stock_us_spot_em()
            symbol_mapping = {
                "AAPL": "AAPL",
                "NVDA": "NVDA", 
                "TSLA": "TSLA",
                "MSFT": "MSFT",
                "GOOGL": "GOOGL",
                "AMZN": "AMZN",
                "META": "META"
            }
            search_symbol = symbol_mapping.get(symbol, symbol)
            stock_data = us_spot[us_spot["代码"].str.contains(search_symbol, case=False, na=False)]
            
            if not stock_data.empty:
                return {
                    "symbol": symbol,
                    "price": float(stock_data["最新价"].values[0]),
                    "open": float(stock_data["开盘价"].values[0]) if "开盘价" in stock_data.columns else 0,
                    "high": float(stock_data["最高价"].values[0]) if "最高价" in stock_data.columns else 0,
                    "low": float(stock_data["最低价"].values[0]) if "最低价" in stock_data.columns else 0,
                    "prev_close": float(stock_data["昨收"].values[0]) if "昨收" in stock_data.columns else 0,
                    "volume": int(stock_data["成交量"].values[0]) if "成交量" in stock_data.columns else 0,
                    "change_pct": float(stock_data["涨跌幅"].values[0]) if "涨跌幅" in stock_data.columns else 0,
                    "source": "akshare_real",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"akshare获取美股{symbol}失败: {e}")
        
        return None


class USSimTraderV3:
    """美股模拟交易器 v3.0"""
    
    def __init__(self, account_id: str = "US_SIM_001"):
        self.account_id = account_id
        self.data_dir = Path("/workspace/projects/workspace/data/us_sim_trading")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.positions_file = self.data_dir / "positions" / "current_positions.json"
        self.trades_file = self.data_dir / "trades" / "trade_history.json"
        
        # 确保目录存在
        self.positions_file.parent.mkdir(parents=True, exist_ok=True)
        self.trades_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.positions = self._load_positions()
        self.trades = self._load_trades()
        self.price_source = USStockPriceSource()
        
    def _load_positions(self) -> Dict:
        if self.positions_file.exists():
            with open(self.positions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "account_id": self.account_id,
            "cash": 1000000.0,  # 初始资金100万美金
            "positions": [],
            "updated_at": datetime.now().isoformat(),
            "version": "3.0_real_data"
        }
    
    def _load_trades(self) -> List:
        if self.trades_file.exists():
            with open(self.trades_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("trades", [])
        return []
    
    def _save_positions(self):
        self.positions["updated_at"] = datetime.now().isoformat()
        with open(self.positions_file, 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, indent=2, ensure_ascii=False)
    
    def _save_trades(self):
        trade_data = {
            "trades": self.trades,
            "trade_stats": self._calculate_stats(),
            "updated_at": datetime.now().isoformat()
        }
        with open(self.trades_file, 'w', encoding='utf-8') as f:
            json.dump(trade_data, f, indent=2, ensure_ascii=False)
    
    def _calculate_stats(self) -> Dict:
        """计算交易统计"""
        if not self.trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0,
                "total_pnl_pct": 0.0
            }
        
        # 简化统计
        return {
            "total_trades": len(self.trades),
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0,
            "total_pnl_pct": 0.0,
            "updated_at": datetime.now().isoformat()
        }
    
    def update_positions_with_real_prices(self) -> Dict:
        """使用真实价格更新持仓市值"""
        total_market_value = 0
        total_cost_basis = 0
        
        for pos in self.positions.get("positions", []):
            symbol = pos["symbol"]
            price_data = self.price_source.get_us_stock_price(symbol)
            
            if price_data:
                current_price = price_data["price"]
                pos["current_price"] = current_price
                pos["market_value"] = current_price * pos["quantity"]
                pos["unrealized_pnl"] = pos["market_value"] - pos["cost_basis"]
                pos["unrealized_pnl_pct"] = (pos["unrealized_pnl"] / pos["cost_basis"] * 100) if pos["cost_basis"] else 0
                pos["price_updated_at"] = datetime.now().isoformat()
                
                total_market_value += pos["market_value"]
                total_cost_basis += pos["cost_basis"]
            else:
                logger.warning(f"无法获取{symbol}价格，使用上次已知价格")
                total_market_value += pos.get("market_value", 0)
                total_cost_basis += pos.get("cost_basis", 0)
        
        # 更新汇总
        self.positions["position_summary"] = {
            "total_positions": len(self.positions.get("positions", [])),
            "total_market_value": total_market_value,
            "total_cost_basis": total_cost_basis,
            "total_unrealized_pnl": total_market_value - total_cost_basis,
            "total_unrealized_pnl_pct": ((total_market_value - total_cost_basis) / total_cost_basis * 100) if total_cost_basis else 0,
            "updated_at": datetime.now().isoformat()
        }
        
        self._save_positions()
        return self.positions["position_summary"]
    
    def execute_trade(self, symbol: str, action: str, quantity: int, strategy: str = "", reason: str = "") -> bool:
        """执行交易"""
        price_data = self.price_source.get_us_stock_price(symbol)
        if not price_data:
            logger.error(f"无法获取{symbol}价格，交易取消")
            return False
        
        price = price_data["price"]
        amount = price * quantity
        commission = max(amount * 0.0005, 1.0)  # 美股佣金0.05%，最低$1
        
        if action == "BUY":
            total_cost = amount + commission
            if self.positions["cash"] < total_cost:
                logger.warning(f"资金不足，无法买入{symbol}")
                return False
            
            # 查找现有持仓
            existing_pos = None
            for pos in self.positions.get("positions", []):
                if pos["symbol"] == symbol:
                    existing_pos = pos
                    break
            
            if existing_pos:
                # 更新现有持仓
                total_quantity = existing_pos["quantity"] + quantity
                total_cost_basis = existing_pos["cost_basis"] + amount
                existing_pos["quantity"] = total_quantity
                existing_pos["avg_cost"] = total_cost_basis / total_quantity
                existing_pos["cost_basis"] = total_cost_basis
            else:
                # 新建持仓
                new_pos = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "avg_cost": price,
                    "cost_basis": amount,
                    "current_price": price,
                    "market_value": amount,
                    "unrealized_pnl": 0,
                    "unrealized_pnl_pct": 0,
                    "opened_at": datetime.now().isoformat()
                }
                self.positions.setdefault("positions", []).append(new_pos)
            
            self.positions["cash"] -= total_cost
            
        elif action == "SELL":
            # 查找持仓
            existing_pos = None
            pos_index = -1
            for i, pos in enumerate(self.positions.get("positions", [])):
                if pos["symbol"] == symbol:
                    existing_pos = pos
                    pos_index = i
                    break
            
            if not existing_pos or existing_pos["quantity"] < quantity:
                logger.warning(f"持仓不足，无法卖出{symbol}")
                return False
            
            revenue = amount - commission
            self.positions["cash"] += revenue
            
            # 更新或删除持仓
            existing_pos["quantity"] -= quantity
            existing_pos["cost_basis"] = existing_pos["avg_cost"] * existing_pos["quantity"]
            
            if existing_pos["quantity"] == 0:
                self.positions["positions"].pop(pos_index)
        
        # 记录交易
        trade = {
            "trade_id": f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "commission": commission,
            "total_cost": amount + commission if action == "BUY" else amount - commission,
            "strategy": strategy,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "source": "real_data"
        }
        self.trades.append(trade)
        
        self._save_positions()
        self._save_trades()
        
        logger.info(f"{action} {symbol} {quantity}股 @ ${price}")
        return True
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        # 先更新价格
        self.update_positions_with_real_prices()
        
        total_value = self.positions.get("cash", 0)
        for pos in self.positions.get("positions", []):
            total_value += pos.get("market_value", 0)
        
        return {
            "account_id": self.account_id,
            "cash": self.positions.get("cash", 0),
            "positions_count": len(self.positions.get("positions", [])),
            "total_value": total_value,
            "positions": self.positions.get("positions", []),
            "updated_at": datetime.now().isoformat()
        }


if __name__ == "__main__":
    trader = USSimTraderV3()
    print("🇺🇸 美股模拟交易器 v3.0 已加载（真实数据源）")
    print(f"账户: {trader.account_id}")
    print(f"现金: ${trader.positions.get('cash', 0):,.2f}")
    print(f"持仓数: {len(trader.positions.get('positions', []))}")
    
    # 测试获取价格
    for symbol in ["AAPL", "NVDA", "TSLA"]:
        price_data = trader.price_source.get_us_stock_price(symbol)
        if price_data:
            print(f"  {symbol}: ${price_data['price']} ({price_data['change_pct']:+.2f}%)")
        else:
            print(f"  {symbol}: 获取失败")
