#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算法交易执行器 (Algorithmic Trading Executor)
P3阶段 - 订单执行优化

功能:
- TWAP (时间加权平均价格)
- VWAP (成交量加权平均价格)
- 冰山订单 (Iceberg)
- 市场冲击模型
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import os
import sys

sys.path.insert(0, "/workspace/projects/workspace")

class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    """订单类型"""
    MARKET = "market"
    LIMIT = "limit"
    TWAP = "twap"
    VWAP = "vwap"
    ICEBERG = "iceberg"

@dataclass
class Order:
    """订单"""
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    limit_price: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    executed_quantity: int = 0
    avg_price: float = 0.0
    status: str = "pending"

@dataclass
class ExecutionSlice:
    """执行切片"""
    timestamp: datetime
    quantity: int
    price: float
    order_type: OrderType

class TWAPExecutor:
    """TWAP执行器"""
    
    def __init__(self, num_slices: int = 10):
        self.num_slices = num_slices
    
    def execute(self, order: Order, 
                price_data: pd.DataFrame) -> List[ExecutionSlice]:
        """
        执行TWAP订单
        
        Args:
            order: 订单
            price_data: 价格数据
            
        Returns:
            执行切片列表
        """
        slices = []
        quantity_per_slice = order.quantity // self.num_slices
        remaining = order.quantity % self.num_slices
        
        # 时间间隔
        if order.start_time and order.end_time:
            total_seconds = (order.end_time - order.start_time).total_seconds()
            interval = total_seconds / self.num_slices
        else:
            interval = 60  # 默认60秒
        
        current_time = order.start_time or datetime.now()
        
        for i in range(self.num_slices):
            qty = quantity_per_slice + (1 if i < remaining else 0)
            
            # 获取当前时间的价格
            price = self._get_price_at_time(price_data, current_time)
            
            slices.append(ExecutionSlice(
                timestamp=current_time,
                quantity=qty,
                price=price,
                order_type=OrderType.TWAP
            ))
            
            current_time += timedelta(seconds=interval)
        
        return slices
    
    def _get_price_at_time(self, price_data: pd.DataFrame, 
                          timestamp: datetime) -> float:
        """获取指定时间的价格"""
        if len(price_data) == 0:
            return 100.0
        
        # 简化: 返回最新价格
        return price_data['close'].iloc[-1] if 'close' in price_data.columns else 100.0

class VWAPExecutor:
    """VWAP执行器"""
    
    def __init__(self, num_slices: int = 10):
        self.num_slices = num_slices
    
    def execute(self, order: Order,
                price_data: pd.DataFrame) -> List[ExecutionSlice]:
        """
        执行VWAP订单
        
        根据历史成交量分布来分配订单
        """
        slices = []
        
        # 计算成交量分布 (简化: 均匀分布)
        volume_profile = self._estimate_volume_profile(price_data)
        
        # 根据成交量分布分配订单量
        quantities = []
        for ratio in volume_profile:
            qty = int(order.quantity * ratio)
            quantities.append(qty)
        
        # 调整以确保总量正确
        diff = order.quantity - sum(quantities)
        quantities[0] += diff
        
        # 执行
        current_time = order.start_time or datetime.now()
        interval = 60  # 60秒间隔
        
        for i, qty in enumerate(quantities):
            if qty <= 0:
                continue
            
            price = self._get_price_at_time(price_data, current_time)
            
            slices.append(ExecutionSlice(
                timestamp=current_time,
                quantity=qty,
                price=price,
                order_type=OrderType.VWAP
            ))
            
            current_time += timedelta(seconds=interval)
        
        return slices
    
    def _estimate_volume_profile(self, price_data: pd.DataFrame) -> List[float]:
        """估计成交量分布"""
        # 简化: 均匀分布
        return [1.0 / self.num_slices] * self.num_slices
    
    def _get_price_at_time(self, price_data: pd.DataFrame,
                          timestamp: datetime) -> float:
        """获取指定时间的价格"""
        if len(price_data) == 0:
            return 100.0
        return price_data['close'].iloc[-1] if 'close' in price_data.columns else 100.0

class IcebergExecutor:
    """冰山订单执行器"""
    
    def __init__(self, display_size: int = 100):
        self.display_size = display_size
    
    def execute(self, order: Order,
                price_data: pd.DataFrame) -> List[ExecutionSlice]:
        """
        执行冰山订单
        
        只显示部分订单量，隐藏真实订单规模
        """
        slices = []
        remaining = order.quantity
        
        current_time = order.start_time or datetime.now()
        
        while remaining > 0:
            # 显示量
            display_qty = min(self.display_size, remaining)
            
            price = self._get_price_at_time(price_data, current_time)
            
            slices.append(ExecutionSlice(
                timestamp=current_time,
                quantity=display_qty,
                price=price,
                order_type=OrderType.ICEBERG
            ))
            
            remaining -= display_qty
            current_time += timedelta(seconds=np.random.randint(30, 120))
        
        return slices
    
    def _get_price_at_time(self, price_data: pd.DataFrame,
                          timestamp: datetime) -> float:
        """获取指定时间的价格"""
        if len(price_data) == 0:
            return 100.0
        return price_data['close'].iloc[-1] if 'close' in price_data.columns else 100.0

class MarketImpactModel:
    """市场冲击模型"""
    
    def __init__(self):
        # 冲击系数 (简化参数)
        self.permanent_impact_coef = 0.1
        self.temporary_impact_coef = 0.05
    
    def estimate_impact(self, order_size: int, avg_daily_volume: int,
                       volatility: float) -> Dict:
        """
        估计市场冲击
        
        Args:
            order_size: 订单规模
            avg_daily_volume: 日均成交量
            volatility: 波动率
            
        Returns:
            冲击估计
        """
        # 参与率
        participation_rate = order_size / avg_daily_volume if avg_daily_volume > 0 else 0
        
        # 永久冲击 (影响价格水平)
        permanent_impact = self.permanent_impact_coef * volatility * np.sqrt(participation_rate)
        
        # 临时冲击 (影响即时价格，会恢复)
        temporary_impact = self.temporary_impact_coef * volatility * participation_rate
        
        # 总冲击成本
        total_cost = permanent_impact + temporary_impact
        
        return {
            "participation_rate": participation_rate,
            "permanent_impact": permanent_impact,
            "temporary_impact": temporary_impact,
            "total_cost": total_cost,
            "impact_bps": total_cost * 10000,  # 基点
            "suggested_slice_size": int(avg_daily_volume * 0.05)  # 建议单次规模 (5% ADV)
        }

class AlgorithmicTradingExecutor:
    """算法交易执行器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.twap_executor = TWAPExecutor()
        self.vwap_executor = VWAPExecutor()
        self.iceberg_executor = IcebergExecutor()
        self.impact_model = MarketImpactModel()
        
        print("⚡ 算法交易执行器初始化")
        print("   支持算法: TWAP, VWAP, 冰山订单")
    
    def execute_order(self, order: Order,
                     price_data: pd.DataFrame,
                     market_data: Dict = None) -> Dict:
        """
        执行订单
        
        Args:
            order: 订单
            price_data: 价格数据
            market_data: 市场数据 (ADV, volatility等)
            
        Returns:
            执行结果
        """
        print(f"\n{'='*70}")
        print(f"⚡ 执行订单: {order.symbol} {order.side.value} {order.quantity}")
        print(f"   算法: {order.order_type.value.upper()}")
        print(f"{'='*70}")
        
        # 估计市场冲击
        if market_data:
            impact = self.impact_model.estimate_impact(
                order_size=order.quantity,
                avg_daily_volume=market_data.get('adv', 1000000),
                volatility=market_data.get('volatility', 0.02)
            )
            
            print(f"\n📊 市场冲击分析:")
            print(f"   参与率: {impact['participation_rate']:.2%}")
            print(f"   冲击成本: {impact['total_cost']:.4f} ({impact['impact_bps']:.2f} bps)")
            print(f"   建议单次规模: {impact['suggested_slice_size']:,} 股")
        
        # 执行
        if order.order_type == OrderType.TWAP:
            slices = self.twap_executor.execute(order, price_data)
        elif order.order_type == OrderType.VWAP:
            slices = self.vwap_executor.execute(order, price_data)
        elif order.order_type == OrderType.ICEBERG:
            slices = self.iceberg_executor.execute(order, price_data)
        else:
            # 市价单 (立即执行)
            price = price_data['close'].iloc[-1] if len(price_data) > 0 else 100.0
            slices = [ExecutionSlice(
                timestamp=datetime.now(),
                quantity=order.quantity,
                price=price,
                order_type=order.order_type
            )]
        
        # 计算执行结果
        total_qty = sum(s.quantity for s in slices)
        total_value = sum(s.quantity * s.price for s in slices)
        avg_price = total_value / total_qty if total_qty > 0 else 0
        
        # 滑点计算
        arrival_price = price_data['close'].iloc[-1] if len(price_data) > 0 else avg_price
        slippage = (avg_price - arrival_price) / arrival_price if arrival_price > 0 else 0
        
        result = {
            "order": {
                "symbol": order.symbol,
                "side": order.side.value,
                "quantity": order.quantity,
                "order_type": order.order_type.value
            },
            "execution": {
                "slices": len(slices),
                "executed_quantity": total_qty,
                "avg_price": avg_price,
                "total_value": total_value,
                "arrival_price": arrival_price,
                "slippage": slippage,
                "slippage_bps": slippage * 10000
            },
            "slices": [
                {
                    "time": s.timestamp.strftime("%H:%M:%S"),
                    "quantity": s.quantity,
                    "price": s.price,
                    "type": s.order_type.value
                }
                for s in slices[:10]  # 只显示前10个切片
            ]
        }
        
        if len(slices) > 10:
            result["slices"].append({"...": f"还有 {len(slices)-10} 个切片"})
        
        return result

def demo():
    """演示算法交易执行器"""
    print("="*70)
    print("⚡ 算法交易执行器演示")
    print("="*70)
    print()
    
    executor = AlgorithmicTradingExecutor()
    
    # 创建模拟价格数据
    np.random.seed(42)
    dates = pd.date_range(start='2026-05-02', periods=100, freq='1min')
    price = 100.0
    prices = []
    for _ in range(100):
        price = price * (1 + np.random.normal(0, 0.001))
        prices.append(price)
    
    price_data = pd.DataFrame({
        'timestamp': dates,
        'close': prices
    })
    
    # 市场数据
    market_data = {
        'adv': 5000000,  # 日均成交量
        'volatility': 0.02  # 日波动率
    }
    
    # 测试订单
    orders = [
        Order(symbol="000001.SZ", side=OrderSide.BUY, quantity=10000,
              order_type=OrderType.TWAP, start_time=datetime.now(),
              end_time=datetime.now() + timedelta(minutes=30)),
        Order(symbol="000001.SZ", side=OrderSide.BUY, quantity=10000,
              order_type=OrderType.VWAP, start_time=datetime.now(),
              end_time=datetime.now() + timedelta(minutes=30)),
        Order(symbol="000001.SZ", side=OrderSide.SELL, quantity=50000,
              order_type=OrderType.ICEBERG),
    ]
    
    for i, order in enumerate(orders, 1):
        result = executor.execute_order(order, price_data, market_data)
        
        print(f"\n📈 执行结果:")
        print(f"   切片数: {result['execution']['slices']}")
        print(f"   成交均价: {result['execution']['avg_price']:.4f}")
        print(f"   到达价格: {result['execution']['arrival_price']:.4f}")
        print(f"   滑点: {result['execution']['slippage']:.4f} ({result['execution']['slippage_bps']:.2f} bps)")
        print(f"   成交数量: {result['execution']['executed_quantity']:,}")
        print(f"   成交金额: {result['execution']['total_value']:,.2f}")
        
        print(f"\n   前几个切片:")
        for s in result['slices'][:5]:
            if 'time' in s:
                print(f"     {s['time']} | {s['quantity']:>6}股 | {s['price']:.4f} | {s['type']}")
            else:
                print(f"     {s}")
        
        if i < len(orders):
            print()
    
    print()
    print("="*70)
    print("✅ 算法交易执行器演示完成!")
    print("="*70)
    print()
    print("说明:")
    print("  • TWAP: 时间加权平均价格，均匀分布在时间段内")
    print("  • VWAP: 成交量加权平均价格，按成交量分布执行")
    print("  • 冰山订单: 隐藏大单，只显示部分订单量")

if __name__ == "__main__":
    demo()
