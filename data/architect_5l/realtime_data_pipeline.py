#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 7: 实时数据流系统
Real-time Data Pipeline with multi-source aggregation
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class DataSource(Enum):
    AKSHARE = "akshare"
    TUSHARE = "tushare"
    YAHOO = "yahoo"
    EASTMONEY = "eastmoney"

@dataclass
class PriceTick:
    """价格tick数据"""
    symbol: str
    price: float
    volume: int
    timestamp: str
    source: DataSource
    bid: float
    ask: float
    change_pct: float

class RealtimeDataPipeline:
    """实时数据流管道"""
    
    def __init__(self):
        self.data_sources = [DataSource.AKSHARE, DataSource.TUSHARE, DataSource.YAHOO]
        self.price_cache = {}
        self.last_update = {}
        self.quality_metrics = {}
        
    def fetch_price(self, symbol: str) -> Optional[PriceTick]:
        """
        获取实时价格 (多源聚合)
        
        策略:
        1. 同时请求多个数据源
        2. 比较价格，剔除异常值
        3. 返回加权平均价格
        """
        ticks = []
        
        # 模拟多源数据获取
        for source in self.data_sources:
            try:
                tick = self._fetch_from_source(symbol, source)
                if tick:
                    ticks.append(tick)
            except Exception as e:
                print(f"   ⚠️  {source.value} 数据获取失败: {e}")
        
        if not ticks:
            return None
        
        # 数据质量检查
        valid_ticks = self._validate_ticks(ticks)
        
        if not valid_ticks:
            return None
        
        # 聚合价格 (加权平均)
        aggregated = self._aggregate_ticks(valid_ticks)
        
        # 更新缓存
        self.price_cache[symbol] = aggregated
        self.last_update[symbol] = datetime.now()
        
        return aggregated
    
    def _fetch_from_source(self, symbol: str, source: DataSource) -> Optional[PriceTick]:
        """从单个数据源获取"""
        # 模拟API调用延迟
        time.sleep(0.01)
        
        # 模拟价格数据
        base_price = self._get_base_price(symbol)
        
        # 模拟不同数据源的微小差异
        if source == DataSource.AKSHARE:
            noise = random.uniform(-0.002, 0.002)
        elif source == DataSource.TUSHARE:
            noise = random.uniform(-0.001, 0.003)
        else:  # YAHOO
            noise = random.uniform(-0.003, 0.001)
        
        price = base_price * (1 + noise)
        
        return PriceTick(
            symbol=symbol,
            price=price,
            volume=random.randint(1000, 100000),
            timestamp=datetime.now().isoformat(),
            source=source,
            bid=price * 0.999,
            ask=price * 1.001,
            change_pct=random.uniform(-2.0, 2.0)
        )
    
    def _get_base_price(self, symbol: str) -> float:
        """获取基础价格"""
        prices = {
            "000066": 19.82,  # 中国长城
            "002436": 29.23,  # 兴森科技
            "300708": 8.83,   # 聚灿光电
            "NVDA": 945.0,
            "AAPL": 185.5,
            "TSLA": 168.0
        }
        return prices.get(symbol, 100.0)
    
    def _validate_ticks(self, ticks: List[PriceTick]) -> List[PriceTick]:
        """验证tick数据质量"""
        if len(ticks) <= 1:
            return ticks
        
        # 计算中位数价格
        prices = [t.price for t in ticks]
        median_price = sorted(prices)[len(prices) // 2]
        
        # 剔除偏离中位数超过1%的异常值
        valid_ticks = []
        for tick in ticks:
            deviation = abs(tick.price - median_price) / median_price
            if deviation < 0.01:  # 1%阈值
                valid_ticks.append(tick)
            else:
                print(f"   ⚠️  剔除异常价格: {tick.source.value} ¥{tick.price:.2f} (偏离{deviation:.2%})")
        
        return valid_ticks
    
    def _aggregate_ticks(self, ticks: List[PriceTick]) -> PriceTick:
        """聚合多个tick"""
        # 简单平均 (生产环境可用加权平均)
        avg_price = sum(t.price for t in ticks) / len(ticks)
        avg_bid = sum(t.bid for t in ticks) / len(ticks)
        avg_ask = sum(t.ask for t in ticks) / len(ticks)
        total_volume = sum(t.volume for t in ticks)
        avg_change = sum(t.change_pct for t in ticks) / len(ticks)
        
        # 优先使用数据源数量最多的源作为主源
        primary_source = max(set(t.source for t in ticks), 
                           key=lambda s: sum(1 for t in ticks if t.source == s))
        
        return PriceTick(
            symbol=ticks[0].symbol,
            price=avg_price,
            volume=total_volume,
            timestamp=datetime.now().isoformat(),
            source=primary_source,
            bid=avg_bid,
            ask=avg_ask,
            change_pct=avg_change
        )
    
    def get_data_quality_report(self) -> Dict:
        """获取数据质量报告"""
        return {
            "cache_size": len(self.price_cache),
            "data_sources": [s.value for s in self.data_sources],
            "last_updates": {k: v.isoformat() for k, v in self.last_update.items()},
            "health_score": 95  # 模拟
        }
    
    def stream_prices(self, symbols: List[str], duration_seconds: int = 10):
        """
        模拟实时价格流
        
        生产环境可使用WebSocket实现真正的实时推送
        """
        print(f"\n📡 启动实时价格流 (持续{duration_seconds}秒)")
        print("-" * 70)
        
        start_time = time.time()
        update_count = 0
        
        while time.time() - start_time < duration_seconds:
            for symbol in symbols:
                tick = self.fetch_price(symbol)
                if tick:
                    update_count += 1
                    emoji = "🟢" if tick.change_pct > 0 else "🔴"
                    print(f"{emoji} {tick.symbol:8s} | "
                          f"¥{tick.price:8.2f} | "
                          f"{tick.change_pct:+.2f}% | "
                          f"量: {tick.volume:,} | "
                          f"源: {tick.source.value}")
            
            time.sleep(2)  # 每2秒更新一次
        
        print(f"\n✅ 价格流结束，共更新 {update_count} 次")


def demo():
    """实时数据流演示"""
    print("=" * 70)
    print("📡 A5L Week 7: 实时数据流系统演示")
    print("=" * 70)
    
    pipeline = RealtimeDataPipeline()
    
    # 演示1: 单股票多源获取
    print("\n【演示1: 多源价格聚合 - 中国长城】")
    print("-" * 70)
    tick = pipeline.fetch_price("000066")
    if tick:
        print(f"聚合价格: ¥{tick.price:.2f}")
        print(f"买/卖: ¥{tick.bid:.2f} / ¥{tick.ask:.2f}")
        print(f"涨跌: {tick.change_pct:+.2f}%")
        print(f"数据源: {tick.source.value}")
    
    # 演示2: 实时价格流
    print("\n【演示2: 实时价格流 (多股票)】")
    pipeline.stream_prices(["000066", "002436", "NVDA"], duration_seconds=6)
    
    # 演示3: 数据质量报告
    print("\n【演示3: 数据质量报告】")
    print("-" * 70)
    report = pipeline.get_data_quality_report()
    print(f"缓存股票数: {report['cache_size']}")
    print(f"数据源: {', '.join(report['data_sources'])}")
    print(f"健康得分: {report['health_score']}/100")
    
    print("\n" + "=" * 70)
    print("✅ 实时数据流系统演示完成!")
    print("=" * 70)
    print("\n💡 生产环境增强:")
    print("   • WebSocket实时推送")
    print("   •  Redis缓存层")
    print("   •  数据持久化 (时序数据库)")
    print("   •  异常数据自动修复")


if __name__ == "__main__":
    demo()
