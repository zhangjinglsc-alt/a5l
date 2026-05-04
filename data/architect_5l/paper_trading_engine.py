#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 6: 实盘模拟交易引擎
Paper Trading Engine with realistic execution simulation
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float]
    stop_price: Optional[float]
    status: OrderStatus
    created_at: str
    filled_at: Optional[str] = None
    filled_price: Optional[float] = None
    filled_quantity: int = 0
    commission: float = 0.0
    slippage: float = 0.0

class PaperTradingEngine:
    """实盘模拟交易引擎"""
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.orders = []
        self.trade_history = []
        self.order_counter = 0
        
        # 模拟参数
        self.commission_rate = 0.0003  # 0.03% 佣金
        self.min_commission = 1.0  # 最低佣金
        self.slippage_model = "random"  # random/volume/volatility
        self.slippage_basis = 0.001  # 0.1% 基础滑点
        
    def _generate_order_id(self) -> str:
        """生成订单ID"""
        self.order_counter += 1
        return f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{self.order_counter:04d}"
    
    def _calculate_slippage(self, symbol: str, side: OrderSide, 
                           intended_price: float, quantity: int) -> float:
        """计算滑点"""
        if self.slippage_model == "random":
            # 随机滑点: -0.1% 到 +0.3% (买入向上滑点，卖出向下滑点)
            base_slippage = random.uniform(-0.001, 0.003)
        else:
            base_slippage = self.slippage_basis
        
        # 根据方向调整滑点
        if side == OrderSide.BUY:
            slippage = abs(base_slippage)  # 买入: 价格更高
        else:
            slippage = -abs(base_slippage)  # 卖出: 价格更低
            
        return intended_price * slippage
    
    def _calculate_commission(self, amount: float) -> float:
        """计算佣金"""
        commission = amount * self.commission_rate
        return max(commission, self.min_commission)
    
    def place_order(self, symbol: str, side: OrderSide, quantity: int,
                   order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Order:
        """下单"""
        
        order_id = self._generate_order_id()
        created_at = datetime.now().isoformat()
        
        # 获取当前市场价格 (模拟)
        market_price = self._get_market_price(symbol)
        
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            status=OrderStatus.PENDING,
            created_at=created_at
        )
        
        # 计算滑点和成交价格
        slippage = self._calculate_slippage(symbol, side, market_price, quantity)
        filled_price = market_price + slippage
        
        # 计算佣金
        trade_amount = filled_price * quantity
        commission = self._calculate_commission(trade_amount)
        
        # 检查资金是否充足
        if side == OrderSide.BUY:
            total_cost = trade_amount + commission
            if total_cost > self.cash:
                order.status = OrderStatus.REJECTED
                print(f"❌ 订单拒绝: 资金不足 (需要 ${total_cost:.2f}, 可用 ${self.cash:.2f})")
                self.orders.append(order)
                return order
        
        # 执行成交
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now().isoformat()
        order.filled_price = filled_price
        order.filled_quantity = quantity
        order.commission = commission
        order.slippage = slippage
        
        # 更新资金和持仓
        if side == OrderSide.BUY:
            self.cash -= (trade_amount + commission)
            if symbol not in self.positions:
                self.positions[symbol] = {"quantity": 0, "avg_cost": 0.0}
            
            # 更新平均成本
            old_quantity = self.positions[symbol]["quantity"]
            old_cost = self.positions[symbol]["avg_cost"] * old_quantity
            new_quantity = old_quantity + quantity
            new_cost = (old_cost + trade_amount + commission) / new_quantity if new_quantity > 0 else 0
            
            self.positions[symbol]["quantity"] = new_quantity
            self.positions[symbol]["avg_cost"] = new_cost
            
        else:  # SELL
            self.cash += (trade_amount - commission)
            if symbol in self.positions:
                self.positions[symbol]["quantity"] -= quantity
                if self.positions[symbol]["quantity"] <= 0:
                    del self.positions[symbol]
        
        # 记录交易
        self.trade_history.append({
            "order_id": order_id,
            "symbol": symbol,
            "side": side.value,
            "quantity": quantity,
            "price": filled_price,
            "commission": commission,
            "timestamp": order.filled_at
        })
        
        self.orders.append(order)
        
        print(f"✅ 订单成交: {side.value.upper()} {quantity} {symbol} @ ${filled_price:.2f}")
        print(f"   滑点: ${slippage:.4f} | 佣金: ${commission:.2f}")
        
        return order
    
    def _get_market_price(self, symbol: str) -> float:
        """获取市场价格 (模拟)"""
        # 模拟价格
        prices = {
            "NVDA": 945.0,
            "AAPL": 185.5,
            "TSLA": 168.0,
            "MSFT": 420.0,
            "GOOGL": 165.0
        }
        base_price = prices.get(symbol, 100.0)
        # 添加微小随机波动
        return base_price * (1 + random.uniform(-0.001, 0.001))
    
    def get_portfolio_value(self) -> Dict:
        """获取组合价值"""
        positions_value = 0.0
        positions_detail = []
        
        for symbol, pos in self.positions.items():
            current_price = self._get_market_price(symbol)
            market_value = pos["quantity"] * current_price
            cost_basis = pos["quantity"] * pos["avg_cost"]
            unrealized_pnl = market_value - cost_basis
            unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            positions_value += market_value
            positions_detail.append({
                "symbol": symbol,
                "quantity": pos["quantity"],
                "avg_cost": pos["avg_cost"],
                "current_price": current_price,
                "market_value": market_value,
                "unrealized_pnl": unrealized_pnl,
                "unrealized_pnl_pct": unrealized_pnl_pct
            })
        
        total_value = self.cash + positions_value
        total_return = total_value - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        return {
            "cash": self.cash,
            "positions_value": positions_value,
            "total_value": total_value,
            "total_return": total_return,
            "total_return_pct": total_return_pct,
            "positions": positions_detail
        }
    
    def get_trade_summary(self) -> Dict:
        """获取交易汇总"""
        total_trades = len(self.trade_history)
        buy_trades = [t for t in self.trade_history if t["side"] == "buy"]
        sell_trades = [t for t in self.trade_history if t["side"] == "sell"]
        total_commission = sum(t["commission"] for t in self.trade_history)
        
        return {
            "total_trades": total_trades,
            "buy_trades": len(buy_trades),
            "sell_trades": len(sell_trades),
            "total_commission": total_commission,
            "open_positions": len(self.positions)
        }


def demo():
    """实盘模拟演示"""
    print("=" * 70)
    print("🚀 A5L Week 6: 实盘模拟交易引擎演示")
    print("=" * 70)
    
    # 创建模拟引擎
    engine = PaperTradingEngine(initial_capital=100000.0)
    
    print("\n📊 初始资金: $100,000.00")
    print(f"佣金率: 0.03% | 最低佣金: $1.00 | 滑点模型: 随机")
    print()
    
    # 执行交易
    print("【交易执行】")
    print("-" * 70)
    
    # 买入NVDA
    engine.place_order("NVDA", OrderSide.BUY, 10, OrderType.MARKET)
    print()
    
    # 买入AAPL
    engine.place_order("AAPL", OrderSide.BUY, 20, OrderType.MARKET)
    print()
    
    # 买入TSLA
    engine.place_order("TSLA", OrderSide.BUY, 15, OrderType.MARKET)
    print()
    
    # 尝试买入更多 (测试资金不足)
    print("【测试资金不足场景】")
    print("-" * 70)
    engine.place_order("MSFT", OrderSide.BUY, 1000, OrderType.MARKET)
    print()
    
    # 显示持仓
    print("【当前持仓】")
    print("-" * 70)
    portfolio = engine.get_portfolio_value()
    
    for pos in portfolio["positions"]:
        emoji = "🟢" if pos["unrealized_pnl"] > 0 else "🔴"
        print(f"{emoji} {pos['symbol']}: {pos['quantity']}股")
        print(f"   成本: ${pos['avg_cost']:.2f} | 现价: ${pos['current_price']:.2f}")
        print(f"   市值: ${pos['market_value']:,.2f}")
        print(f"   盈亏: ${pos['unrealized_pnl']:+.2f} ({pos['unrealized_pnl_pct']:+.2f}%)")
        print()
    
    print(f"💰 现金: ${portfolio['cash']:,.2f}")
    print(f"📈 持仓市值: ${portfolio['positions_value']:,.2f}")
    print(f"💵 总资产: ${portfolio['total_value']:,.2f}")
    print(f"📊 总收益: ${portfolio['total_return']:+.2f} ({portfolio['total_return_pct']:+.2f}%)")
    print()
    
    # 交易汇总
    print("【交易汇总】")
    print("-" * 70)
    summary = engine.get_trade_summary()
    print(f"总交易次数: {summary['total_trades']}")
    print(f"买入次数: {summary['buy_trades']}")
    print(f"卖出次数: {summary['sell_trades']}")
    print(f"总佣金: ${summary['total_commission']:.2f}")
    print(f"持仓数量: {summary['open_positions']}")
    print()
    
    print("=" * 70)
    print("✅ 实盘模拟演示完成!")
    print("=" * 70)


if __name__ == "__main__":
    demo()
