#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 9: 交易执行优化系统
Execution Optimization with TWAP/VWAP Algorithms
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ExecutionAlgo(Enum):
    """执行算法"""
    MARKET = "market"        # 市价单
    TWAP = "twap"           # 时间加权平均价格
    VWAP = "vwap"           # 成交量加权平均价格
    ICEBERG = "iceberg"     # 冰山订单

@dataclass
class ExecutionResult:
    """执行结果"""
    algo: ExecutionAlgo
    symbol: str
    quantity: int
    filled_quantity: int
    avg_price: float
    slippage: float
    market_impact: float
    execution_time: float
    slices: int
    timestamp: str

class ExecutionOptimizer:
    """交易执行优化器"""
    
    def __init__(self):
        self.market_data = {}
        self.execution_history = []
        
    def execute(self, symbol: str, quantity: int, algo: ExecutionAlgo,
                time_window: int = 300) -> ExecutionResult:
        """
        执行订单
        
        Args:
            symbol: 股票代码
            quantity: 数量
            algo: 执行算法
            time_window: 时间窗口(秒)，TWAP/VWAP用
        """
        print(f"\n🚀 执行订单: {symbol} {quantity}股")
        print(f"   算法: {algo.value}")
        
        start_time = time.time()
        
        if algo == ExecutionAlgo.MARKET:
            result = self._execute_market(symbol, quantity)
        elif algo == ExecutionAlgo.TWAP:
            result = self._execute_twap(symbol, quantity, time_window)
        elif algo == ExecutionAlgo.VWAP:
            result = self._execute_vwap(symbol, quantity, time_window)
        elif algo == ExecutionAlgo.ICEBERG:
            result = self._execute_iceberg(symbol, quantity)
        else:
            result = self._execute_market(symbol, quantity)
        
        execution_time = time.time() - start_time
        result.execution_time = execution_time
        result.timestamp = datetime.now().isoformat()
        
        self.execution_history.append(result)
        
        return result
    
    def _get_market_price(self, symbol: str) -> float:
        """获取市场价格"""
        prices = {
            "000066": 19.82,
            "601975": 4.45,
            "688981": 125.0,
            "NVDA": 945.0,
            "AAPL": 185.5
        }
        return prices.get(symbol, 100.0)
    
    def _simulate_price_movement(self, base_price: float,
                                  volatility: float = 0.001) -> float:
        """模拟价格波动"""
        return base_price * (1 + random.uniform(-volatility, volatility))
    
    def _execute_market(self, symbol: str, quantity: int) -> ExecutionResult:
        """市价单执行"""
        base_price = self._get_market_price(symbol)
        
        # 市价单滑点较大
        slippage = random.uniform(0.001, 0.003)
        avg_price = base_price * (1 + slippage)
        
        return ExecutionResult(
            algo=ExecutionAlgo.MARKET,
            symbol=symbol,
            quantity=quantity,
            filled_quantity=quantity,
            avg_price=avg_price,
            slippage=slippage,
            market_impact=slippage * 0.5,
            execution_time=0.1,
            slices=1,
            timestamp=""
        )
    
    def _execute_twap(self, symbol: str, quantity: int,
                     time_window: int) -> ExecutionResult:
        """
        TWAP执行 (Time Weighted Average Price)
        
        将大单拆分成多个小单，均匀分布在时间窗口内执行
        """
        base_price = self._get_market_price(symbol)
        
        # 拆分成多个slice
        num_slices = min(10, max(3, quantity // 1000))
        slice_quantity = quantity // num_slices
        remaining = quantity
        
        total_cost = 0
        total_filled = 0
        
        print(f"   TWAP拆分: {num_slices}笔, 每批约{slice_quantity}股")
        
        for i in range(num_slices):
            if remaining <= 0:
                break
            
            # 最后一批处理余数
            if i == num_slices - 1:
                qty = remaining
            else:
                qty = min(slice_quantity, remaining)
            
            # 模拟价格
            price = self._simulate_price_movement(base_price, 0.0005)
            
            # TWAP滑点较小
            slippage = random.uniform(0.0003, 0.0008)
            executed_price = price * (1 + slippage)
            
            total_cost += qty * executed_price
            total_filled += qty
            remaining -= qty
            
            # 模拟时间间隔
            time.sleep(0.05)
        
        avg_price = total_cost / total_filled if total_filled > 0 else base_price
        total_slippage = (avg_price - base_price) / base_price
        
        return ExecutionResult(
            algo=ExecutionAlgo.TWAP,
            symbol=symbol,
            quantity=quantity,
            filled_quantity=total_filled,
            avg_price=avg_price,
            slippage=total_slippage,
            market_impact=total_slippage * 0.3,
            execution_time=time_window,
            slices=num_slices,
            timestamp=""
        )
    
    def _execute_vwap(self, symbol: str, quantity: int,
                     time_window: int) -> ExecutionResult:
        """
        VWAP执行 (Volume Weighted Average Price)
        
        根据历史成交量分布，在成交量大的时段多执行
        """
        base_price = self._get_market_price(symbol)
        
        # 模拟日内成交量分布 (U型曲线)
        volume_profile = [0.08, 0.12, 0.15, 0.12, 0.08, 0.10, 0.15, 0.20]
        
        total_cost = 0
        total_filled = 0
        remaining = quantity
        
        num_slices = len(volume_profile)
        print(f"   VWAP拆分: {num_slices}笔 (按成交量分布)")
        
        for i, vol_pct in enumerate(volume_profile):
            # 根据成交量占比分配订单量
            qty = int(quantity * vol_pct)
            qty = min(qty, remaining)
            
            if qty <= 0:
                continue
            
            # 成交量大的时段滑点更小
            base_slippage = 0.0005
            slippage = base_slippage * (1 - vol_pct)  # 量大滑点小
            
            price = self._simulate_price_movement(base_price, 0.0005)
            executed_price = price * (1 + slippage)
            
            total_cost += qty * executed_price
            total_filled += qty
            remaining -= qty
            
            time.sleep(0.03)
        
        # 处理余数
        if remaining > 0:
            total_cost += remaining * base_price
            total_filled += remaining
        
        avg_price = total_cost / total_filled if total_filled > 0 else base_price
        total_slippage = (avg_price - base_price) / base_price
        
        return ExecutionResult(
            algo=ExecutionAlgo.VWAP,
            symbol=symbol,
            quantity=quantity,
            filled_quantity=total_filled,
            avg_price=avg_price,
            slippage=total_slippage,
            market_impact=total_slippage * 0.25,
            execution_time=time_window,
            slices=num_slices,
            timestamp=""
        )
    
    def _execute_iceberg(self, symbol: str, quantity: int) -> ExecutionResult:
        """
        冰山订单
        
        只显示部分订单量，隐藏真实大单规模
        """
        base_price = self._get_market_price(symbol)
        
        # 显示5%的订单
        display_qty = max(100, quantity // 20)
        
        print(f"   冰山订单: 显示{display_qty}股, 实际{quantity}股")
        
        # 模拟逐步成交
        total_cost = 0
        remaining = quantity
        slices = 0
        
        while remaining > 0:
            fill_qty = min(display_qty, remaining)
            slippage = random.uniform(0.0005, 0.001)
            price = self._simulate_price_movement(base_price, 0.0005)
            executed_price = price * (1 + slippage)
            
            total_cost += fill_qty * executed_price
            remaining -= fill_qty
            slices += 1
            
            time.sleep(0.02)
        
        avg_price = total_cost / quantity
        total_slippage = (avg_price - base_price) / base_price
        
        return ExecutionResult(
            algo=ExecutionAlgo.ICEBERG,
            symbol=symbol,
            quantity=quantity,
            filled_quantity=quantity,
            avg_price=avg_price,
            slippage=total_slippage,
            market_impact=total_slippage * 0.4,
            execution_time=slices * 0.02,
            slices=slices,
            timestamp=""
        )
    
    def compare_algorithms(self, symbol: str, quantity: int) -> Dict:
        """比较不同执行算法"""
        print(f"\n📊 执行算法对比: {symbol} {quantity}股")
        print("=" * 70)
        
        results = {}
        base_price = self._get_market_price(symbol)
        
        for algo in ExecutionAlgo:
            result = self.execute(symbol, quantity, algo, time_window=60)
            results[algo.value] = result
        
        print("\n对比结果:")
        print("-" * 70)
        print(f"{'算法':<12} {'均价':<10} {'滑点':<10} {'冲击':<10} {'时间':<10} {'拆单'}")
        print("-" * 70)
        
        for algo_name, result in results.items():
            print(f"{algo_name:<12} ¥{result.avg_price:<9.2f} "
                  f"{result.slippage:<9.2%} {result.market_impact:<9.2%} "
                  f"{result.execution_time:<9.1f}s {result.slices}")
        
        # 最优算法推荐
        min_slippage_algo = min(results.items(), key=lambda x: x[1].slippage)
        print(f"\n🏆 最优滑点: {min_slippage_algo[0]} ({min_slippage_algo[1].slippage:.3%})")
        
        return results
    
    def get_execution_summary(self) -> Dict:
        """获取执行汇总"""
        if not self.execution_history:
            return {"message": "暂无执行记录"}
        
        avg_slippage = sum(r.slippage for r in self.execution_history) / len(self.execution_history)
        total_volume = sum(r.filled_quantity for r in self.execution_history)
        
        return {
            "total_executions": len(self.execution_history),
            "total_volume": total_volume,
            "avg_slippage": avg_slippage,
            "by_algo": {
                algo.value: len([r for r in self.execution_history if r.algo == algo])
                for algo in ExecutionAlgo
            }
        }


def demo():
    """交易执行优化演示"""
    print("=" * 70)
    print("⚡ A5L Week 9: 交易执行优化系统演示")
    print("=" * 70)
    
    optimizer = ExecutionOptimizer()
    
    # 演示1: 市价单
    print("\n【演示1: 市价单执行】")
    print("-" * 70)
    
    result = optimizer.execute("000066", 1000, ExecutionAlgo.MARKET)
    print(f"✅ 执行完成:")
    print(f"   均价: ¥{result.avg_price:.2f}")
    print(f"   滑点: {result.slippage:.3%}")
    print(f"   市场冲击: {result.market_impact:.3%}")
    
    # 演示2: TWAP
    print("\n【演示2: TWAP执行 (时间加权)】")
    print("-" * 70)
    
    result = optimizer.execute("601975", 10000, ExecutionAlgo.TWAP, time_window=30)
    print(f"✅ 执行完成:")
    print(f"   拆单: {result.slices}笔")
    print(f"   均价: ¥{result.avg_price:.2f}")
    print(f"   滑点: {result.slippage:.3%}")
    print(f"   相比市价单: {'优于' if result.slippage < 0.002 else '劣于'}市价")
    
    # 演示3: VWAP
    print("\n【演示3: VWAP执行 (成交量加权)】")
    print("-" * 70)
    
    result = optimizer.execute("688981", 5000, ExecutionAlgo.VWAP, time_window=30)
    print(f"✅ 执行完成:")
    print(f"   拆单: {result.slices}笔 (按成交量分布)")
    print(f"   均价: ¥{result.avg_price:.2f}")
    print(f"   滑点: {result.slippage:.3%}")
    
    # 演示4: 冰山订单
    print("\n【演示4: 冰山订单执行】")
    print("-" * 70)
    
    result = optimizer.execute("NVDA", 500, ExecutionAlgo.ICEBERG)
    print(f"✅ 执行完成:")
    print(f"   拆单: {result.slices}笔")
    print(f"   均价: ¥{result.avg_price:.2f}")
    print(f"   滑点: {result.slippage:.3%}")
    
    # 演示5: 算法对比
    print("\n【演示5: 算法性能对比】")
    print("-" * 70)
    
    optimizer.compare_algorithms("AAPL", 2000)
    
    print("\n" + "=" * 70)
    print("✅ 交易执行优化系统演示完成!")
    print("=" * 70)
    print("\n💡 生产环境增强:")
    print("   • 实时市场微观结构分析")
    print("   • 机器学习预测最优算法")
    print("   • 暗池路由 (Dark Pool)")
    print("   • 智能撤单再挂")


if __name__ == "__main__":
    demo()
