#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 10: 券商API模拟器
Broker API Simulator for A-share and US stocks
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class Market(Enum):
    """市场"""
    A_SHARE = "a_share"      # A股
    HK = "hk"                # 港股
    US = "us"                # 美股

class OrderType(Enum):
    """订单类型"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    """订单对象"""
    order_id: str
    symbol: str
    market: Market
    action: str  # buy/sell
    order_type: OrderType
    quantity: int
    price: Optional[float]
    status: OrderStatus
    filled_quantity: int = 0
    avg_fill_price: float = 0.0
    commission: float = 0.0
    created_at: str = ""
    updated_at: str = ""

class BrokerAPI:
    """券商API基类"""
    
    def __init__(self, broker_name: str):
        self.broker_name = broker_name
        self.orders = {}
        self.order_counter = 0
        self.positions = {}
        self.cash = 0.0
        self.account_value = 0.0
        
    def connect(self) -> bool:
        """连接券商"""
        raise NotImplementedError
    
    def disconnect(self):
        """断开连接"""
        pass
    
    def place_order(self, symbol: str, action: str, quantity: int,
                   order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None) -> Order:
        """下单"""
        raise NotImplementedError
    
    def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        raise NotImplementedError
    
    def get_order_status(self, order_id: str) -> Order:
        """查询订单状态"""
        return self.orders.get(order_id)
    
    def get_positions(self) -> List[Dict]:
        """获取持仓"""
        return list(self.positions.values())
    
    def get_account(self) -> Dict:
        """获取账户信息"""
        return {
            "cash": self.cash,
            "account_value": self.account_value,
            "positions_value": sum(p.get("market_value", 0) for p in self.positions.values())
        }
    
    def _generate_order_id(self) -> str:
        """生成订单ID"""
        self.order_counter += 1
        return f"{self.broker_name.upper()}{datetime.now().strftime('%Y%m%d%H%M%S')}{self.order_counter:06d}"


class ASHAREBrokerAPI(BrokerAPI):
    """A股券商API (模拟)"""
    
    def __init__(self):
        super().__init__("ashare")
        self.commission_rate = 0.0003  # 0.03%
        self.min_commission = 5.0      # 最低5元
        self.stamp_duty_rate = 0.001   # 印花税 0.1% (卖出)
        self.transfer_fee_rate = 0.00002  # 过户费 0.002%
        
    def connect(self) -> bool:
        """连接A股券商"""
        print(f"✅ 已连接A股券商: {self.broker_name}")
        self.cash = 1000000.0  # 模拟100万资金
        self.account_value = self.cash
        return True
    
    def place_order(self, symbol: str, action: str, quantity: int,
                   order_type: OrderType = OrderType.LIMIT,
                   price: Optional[float] = None) -> Order:
        """A股下单"""
        
        # A股必须是100的整数倍
        if quantity % 100 != 0:
            print(f"❌ A股必须是100的整数倍: {quantity}")
            return None
        
        # 获取当前价格
        if price is None:
            price = self._get_price(symbol)
        
        order_id = self._generate_order_id()
        
        order = Order(
            order_id=order_id,
            symbol=symbol,
            market=Market.A_SHARE,
            action=action,
            order_type=order_type,
            quantity=quantity,
            price=price,
            status=OrderStatus.SUBMITTED,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.orders[order_id] = order
        
        print(f"📤 A股下单: {symbol} {action} {quantity}股 @ ¥{price:.2f}")
        
        # 模拟执行
        self._simulate_execution(order)
        
        return order
    
    def _simulate_execution(self, order: Order):
        """模拟订单执行"""
        time.sleep(0.1)  # 模拟延迟
        
        # 模拟滑点
        slippage = random.uniform(-0.01, 0.01)
        executed_price = order.price * (1 + slippage)
        
        # 计算费用
        trade_value = executed_price * order.quantity
        
        # 佣金
        commission = max(trade_value * self.commission_rate, self.min_commission)
        
        # 印花税 (仅卖出)
        stamp_duty = trade_value * self.stamp_duty_rate if order.action == "sell" else 0
        
        # 过户费
        transfer_fee = trade_value * self.transfer_fee_rate
        
        total_cost = commission + stamp_duty + transfer_fee
        
        # 更新订单
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.avg_fill_price = executed_price
        order.commission = total_cost
        order.updated_at = datetime.now().isoformat()
        
        # 更新持仓和资金
        if order.action == "buy":
            total_cost_with_trade = trade_value + total_cost
            if total_cost_with_trade > self.cash:
                order.status = OrderStatus.REJECTED
                print(f"   ❌ 资金不足")
                return
            
            self.cash -= total_cost_with_trade
            
            if order.symbol not in self.positions:
                self.positions[order.symbol] = {
                    "symbol": order.symbol,
                    "quantity": 0,
                    "avg_cost": 0,
                    "market_value": 0
                }
            
            pos = self.positions[order.symbol]
            old_qty = pos["quantity"]
            old_cost = old_qty * pos["avg_cost"]
            new_qty = old_qty + order.quantity
            pos["quantity"] = new_qty
            pos["avg_cost"] = (old_cost + trade_value) / new_qty if new_qty > 0 else 0
            pos["market_value"] = new_qty * executed_price
            
        else:  # sell
            if order.symbol not in self.positions or self.positions[order.symbol]["quantity"] < order.quantity:
                order.status = OrderStatus.REJECTED
                print(f"   ❌ 持仓不足")
                return
            
            proceeds = trade_value - total_cost
            self.cash += proceeds
            
            self.positions[order.symbol]["quantity"] -= order.quantity
            if self.positions[order.symbol]["quantity"] == 0:
                del self.positions[order.symbol]
        
        print(f"   ✅ 成交: ¥{executed_price:.2f} (滑点: {slippage:.2%})")
        print(f"   💰 费用: ¥{total_cost:.2f} (佣金¥{commission:.2f} + 印花税¥{stamp_duty:.2f})")
    
    def _get_price(self, symbol: str) -> float:
        """获取价格"""
        prices = {
            "000066": 19.82,
            "601975": 4.45,
            "688981": 125.0,
            "002436": 30.0,
            "300708": 11.0
        }
        return prices.get(symbol, 20.0)
    
    def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
                order.status = OrderStatus.CANCELLED
                print(f"✅ 订单已撤销: {order_id}")
                return True
        return False


class USBrokerAPI(BrokerAPI):
    """美股券商API (模拟)"""
    
    def __init__(self):
        super().__init__("us")
        self.commission_rate = 0.0003  # 0.03%
        self.min_commission = 1.0      # 最低$1
        self.sec_fee_rate = 0.000008   # SEC费
        
    def connect(self) -> bool:
        """连接美股券商"""
        print(f"✅ 已连接美股券商: {self.broker_name}")
        self.cash = 100000.0  # 模拟10万美元
        self.account_value = self.cash
        return True
    
    def place_order(self, symbol: str, action: str, quantity: int,
                   order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None) -> Order:
        """美股下单"""
        
        if price is None:
            price = self._get_price(symbol)
        
        order_id = self._generate_order_id()
        
        order = Order(
            order_id=order_id,
            symbol=symbol,
            market=Market.US,
            action=action,
            order_type=order_type,
            quantity=quantity,
            price=price,
            status=OrderStatus.SUBMITTED,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.orders[order_id] = order
        
        print(f"📤 美股下单: {symbol} {action} {quantity}股 @ ${price:.2f}")
        
        # 模拟执行
        self._simulate_execution(order)
        
        return order
    
    def _simulate_execution(self, order: Order):
        """模拟订单执行"""
        time.sleep(0.05)  # 美股更快
        
        slippage = random.uniform(-0.005, 0.005)
        executed_price = order.price * (1 + slippage)
        
        trade_value = executed_price * order.quantity
        
        # 佣金
        commission = max(trade_value * self.commission_rate, self.min_commission)
        
        # SEC费 (卖出)
        sec_fee = trade_value * self.sec_fee_rate if order.action == "sell" else 0
        
        total_cost = commission + sec_fee
        
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.avg_fill_price = executed_price
        order.commission = total_cost
        order.updated_at = datetime.now().isoformat()
        
        # 更新持仓和资金
        if order.action == "buy":
            total_cost_with_trade = trade_value + total_cost
            if total_cost_with_trade > self.cash:
                order.status = OrderStatus.REJECTED
                print(f"   ❌ 资金不足")
                return
            
            self.cash -= total_cost_with_trade
            
            if order.symbol not in self.positions:
                self.positions[order.symbol] = {
                    "symbol": order.symbol,
                    "quantity": 0,
                    "avg_cost": 0,
                    "market_value": 0
                }
            
            pos = self.positions[order.symbol]
            old_qty = pos["quantity"]
            old_cost = old_qty * pos["avg_cost"]
            new_qty = old_qty + order.quantity
            pos["quantity"] = new_qty
            pos["avg_cost"] = (old_cost + trade_value) / new_qty if new_qty > 0 else 0
            pos["market_value"] = new_qty * executed_price
            
        else:
            if order.symbol not in self.positions or self.positions[order.symbol]["quantity"] < order.quantity:
                order.status = OrderStatus.REJECTED
                print(f"   ❌ 持仓不足")
                return
            
            proceeds = trade_value - total_cost
            self.cash += proceeds
            self.positions[order.symbol]["quantity"] -= order.quantity
        
        print(f"   ✅ 成交: ${executed_price:.2f} (滑点: {slippage:.2%})")
        print(f"   💰 费用: ${total_cost:.2f}")
    
    def _get_price(self, symbol: str) -> float:
        """获取价格"""
        prices = {
            "AAPL": 185.5,
            "NVDA": 945.0,
            "TSLA": 168.0,
            "MSFT": 420.0,
            "GOOGL": 175.0
        }
        return prices.get(symbol, 100.0)
    
    def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
                order.status = OrderStatus.CANCELLED
                print(f"✅ 订单已撤销: {order_id}")
                return True
        return False


class UnifiedTradingAPI:
    """统一交易API"""
    
    def __init__(self):
        self.brokers = {}
        self.active_broker = None
        
    def register_broker(self, market: Market, broker: BrokerAPI):
        """注册券商"""
        self.brokers[market] = broker
        
    def connect_all(self) -> Dict[Market, bool]:
        """连接所有券商"""
        results = {}
        for market, broker in self.brokers.items():
            results[market] = broker.connect()
        return results
    
    def place_order(self, symbol: str, market: Market, action: str,
                   quantity: int, order_type: OrderType = OrderType.MARKET,
                   price: Optional[float] = None) -> Optional[Order]:
        """统一下单接口"""
        
        if market not in self.brokers:
            print(f"❌ 未找到券商: {market.value}")
            return None
        
        broker = self.brokers[market]
        return broker.place_order(symbol, action, quantity, order_type, price)
    
    def get_all_positions(self) -> Dict[Market, List[Dict]]:
        """获取所有持仓"""
        return {market: broker.get_positions() for market, broker in self.brokers.items()}
    
    def get_all_accounts(self) -> Dict[Market, Dict]:
        """获取所有账户"""
        return {market: broker.get_account() for market, broker in self.brokers.items()}


def demo():
    """券商API演示"""
    print("=" * 70)
    print("🏦 A5L Week 10: 券商API模拟器演示")
    print("=" * 70)
    
    # 创建统一API
    unified = UnifiedTradingAPI()
    
    # 注册券商
    unified.register_broker(Market.A_SHARE, ASHAREBrokerAPI())
    unified.register_broker(Market.US, USBrokerAPI())
    
    # 连接所有券商
    print("\n【连接券商】")
    print("-" * 70)
    results = unified.connect_all()
    
    # 演示1: A股交易
    print("\n【演示1: A股交易】")
    print("-" * 70)
    
    # 买入
    order1 = unified.place_order("000066", Market.A_SHARE, "buy", 1000, OrderType.LIMIT, 19.80)
    order2 = unified.place_order("601975", Market.A_SHARE, "buy", 2000, OrderType.LIMIT, 4.45)
    
    # 显示账户
    a_account = unified.brokers[Market.A_SHARE].get_account()
    print(f"\n📊 A股账户:")
    print(f"   现金: ¥{a_account['cash']:,.2f}")
    print(f"   持仓市值: ¥{a_account['positions_value']:,.2f}")
    
    # 显示持仓
    a_positions = unified.brokers[Market.A_SHARE].get_positions()
    print(f"   持仓数量: {len(a_positions)}只")
    for pos in a_positions:
        print(f"      {pos['symbol']}: {pos['quantity']}股 @ ¥{pos['avg_cost']:.2f}")
    
    # 演示2: 美股交易
    print("\n【演示2: 美股交易】")
    print("-" * 70)
    
    # 买入
    order3 = unified.place_order("NVDA", Market.US, "buy", 10, OrderType.MARKET)
    order4 = unified.place_order("AAPL", Market.US, "buy", 20, OrderType.MARKET)
    
    # 显示账户
    us_account = unified.brokers[Market.US].get_account()
    print(f"\n📊 美股账户:")
    print(f"   现金: ${us_account['cash']:,.2f}")
    print(f"   持仓市值: ${us_account['positions_value']:,.2f}")
    
    # 演示3: 多账户汇总
    print("\n【演示3: 多账户汇总】")
    print("-" * 70)
    
    all_accounts = unified.get_all_accounts()
    total_cash = sum(acc['cash'] for acc in all_accounts.values())
    total_positions = sum(acc['positions_value'] for acc in all_accounts.values())
    
    print(f"总现金: ¥/${total_cash:,.2f}")
    print(f"总持仓: ¥/${total_positions:,.2f}")
    print(f"总资产: ¥/${total_cash + total_positions:,.2f}")
    
    # 演示4: 卖出
    print("\n【演示4: 卖出操作】")
    print("-" * 70)
    
    # A股卖出
    order5 = unified.place_order("000066", Market.A_SHARE, "sell", 500, OrderType.LIMIT, 20.00)
    
    # 显示更新后的A股账户
    a_account = unified.brokers[Market.A_SHARE].get_account()
    print(f"\n📊 A股账户 (卖出后):")
    print(f"   现金: ¥{a_account['cash']:,.2f}")
    print(f"   持仓市值: ¥{a_account['positions_value']:,.2f}")
    
    print("\n" + "=" * 70)
    print("✅ 券商API模拟器演示完成!")
    print("=" * 70)
    print("\n💡 生产环境增强:")
    print("   • 真实券商API对接 (中泰/华泰/盈透)")
    print("   • WebSocket实时行情推送")
    print("   • 订单簿深度分析")
    print("   • 智能路由 (最优券商选择)")


if __name__ == "__main__":
    demo()
