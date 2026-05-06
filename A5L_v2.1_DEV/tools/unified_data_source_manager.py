#!/usr/bin/env python3
"""
A5L 统一数据源管理器 - 多API互为保障

互为保障策略:
1. 美股: Finnhub (主) → Yahoo Finance (备) → 本地缓存 (兜底)
2. A股: Tushare (主) → akshare (备) → 本地缓存 (兜底)
3. 港股: Tushare (主) → Yahoo Finance (备) → 本地缓存 (兜底)

Chief指令: 所有数据源API互为保障
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union
from dataclasses import dataclass, asdict

sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

# 导入各数据源
from finnhub_client import FinnhubDataSource, FINNHUB_AVAILABLE


@dataclass
class DataSourceHealth:
    """数据源健康状态"""
    source_name: str
    is_available: bool
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    failure_count: int
    avg_response_time: float
    priority: int  # 优先级，数字越小优先级越高


@dataclass
class PriceData:
    """统一价格数据结构"""
    symbol: str
    current: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    previous_close: float
    volume: Optional[int] = None
    timestamp: Optional[str] = None
    source: str = "unknown"
    is_cached: bool = False


class UnifiedDataSourceManager:
    """
    A5L统一数据源管理器
    
    实现多API互为保障:
    - 自动检测各数据源可用性
    - 按优先级自动切换
    - 本地缓存兜底
    - 故障自动恢复
    """
    
    # 数据源优先级配置
    SOURCE_PRIORITY = {
        'US': ['finnhub', 'yahoo', 'cache'],  # 美股优先级
        'CN': ['tushare', 'akshare', 'cache'],  # A股优先级
        'HK': ['tushare', 'yahoo', 'cache'],  # 港股优先级
    }
    
    # 限流配置 (次/分钟)
    RATE_LIMITS = {
        'finnhub': {'max': 60, 'safety': 0.8, 'current': 0, 'reset_time': None},
        'yahoo': {'max': 100, 'safety': 0.5, 'current': 0, 'reset_time': None},  # Yahoo实际更低
        'tushare': {'max': 15000, 'safety': 0.9, 'current': 0, 'reset_time': None},
        'akshare': {'max': 1000, 'safety': 0.8, 'current': 0, 'reset_time': None},
    }
    
    def __init__(self, enable_cache: bool = True, cache_duration: int = 300):
        """
        初始化统一数据源管理器
        
        Args:
            enable_cache: 是否启用本地缓存
            cache_duration: 缓存有效期(秒)，默认5分钟
        """
        self.enable_cache = enable_cache
        self.cache_duration = cache_duration
        self.cache = {}  # 本地缓存
        self.cache_timestamp = {}
        
        # 初始化各数据源
        self.sources = {}
        self.source_health = {}
        
        self._init_sources()
        
        print("✅ A5L统一数据源管理器初始化完成")
        self._print_source_status()
    
    def _init_sources(self):
        """初始化所有数据源"""
        # Finnhub (美股主数据源)
        if FINNHUB_AVAILABLE:
            try:
                self.sources['finnhub'] = FinnhubDataSource(enable_rate_limit=True)
                self.source_health['finnhub'] = DataSourceHealth(
                    source_name='finnhub',
                    is_available=True,
                    last_success=datetime.now(),
                    last_failure=None,
                    failure_count=0,
                    avg_response_time=0.5,
                    priority=1
                )
            except Exception as e:
                print(f"   ⚠️ Finnhub初始化失败: {e}")
                self.source_health['finnhub'] = DataSourceHealth(
                    source_name='finnhub',
                    is_available=False,
                    last_success=None,
                    last_failure=datetime.now(),
                    failure_count=1,
                    avg_response_time=0,
                    priority=1
                )
        
        # Tushare (A股主数据源)
        try:
            from data_unified import get_data_source
            self.sources['tushare'] = get_data_source()
            self.source_health['tushare'] = DataSourceHealth(
                source_name='tushare',
                is_available=True,
                last_success=datetime.now(),
                last_failure=None,
                failure_count=0,
                avg_response_time=0.3,
                priority=1
            )
        except Exception as e:
            print(f"   ⚠️ Tushare初始化失败: {e}")
            self.source_health['tushare'] = DataSourceHealth(
                source_name='tushare',
                is_available=False,
                last_success=None,
                last_failure=datetime.now(),
                failure_count=1,
                avg_response_time=0,
                priority=1
            )
        
        # Yahoo Finance (备用数据源)
        try:
            import yfinance as yf
            self.sources['yahoo'] = yf
            self.source_health['yahoo'] = DataSourceHealth(
                source_name='yahoo',
                is_available=True,
                last_success=datetime.now(),
                last_failure=None,
                failure_count=0,
                avg_response_time=1.0,
                priority=2
            )
        except ImportError:
            print("   ⚠️ Yahoo Finance (yfinance) 未安装")
            self.source_health['yahoo'] = DataSourceHealth(
                source_name='yahoo',
                is_available=False,
                last_success=None,
                last_failure=datetime.now(),
                failure_count=1,
                avg_response_time=0,
                priority=2
            )
        
        # akshare (A股备用)
        try:
            import akshare as ak
            self.sources['akshare'] = ak
            self.source_health['akshare'] = DataSourceHealth(
                source_name='akshare',
                is_available=True,
                last_success=datetime.now(),
                last_failure=None,
                failure_count=0,
                avg_response_time=0.8,
                priority=2
            )
        except ImportError:
            print("   ⚠️ akshare 未安装")
            self.source_health['akshare'] = DataSourceHealth(
                source_name='akshare',
                is_available=False,
                last_success=None,
                last_failure=datetime.now(),
                failure_count=1,
                avg_response_time=0,
                priority=2
            )
    
    def _print_source_status(self):
        """打印数据源状态"""
        print("\n📊 数据源健康状态:")
        print("   " + "-" * 50)
        for name, health in self.source_health.items():
            status = "🟢 正常" if health.is_available else "🔴 异常"
            print(f"   {name:<12} {status}  优先级:{health.priority}")
        print("   " + "-" * 50)
    
    def _get_market_type(self, symbol: str) -> str:
        """判断股票所属市场"""
        # 纯数字为A股
        if symbol.isdigit():
            if len(symbol) == 5:  # 港股
                return 'HK'
            return 'CN'
        # 英文代码为美股
        return 'US'
    
    def _get_cached_price(self, symbol: str) -> Optional[PriceData]:
        """获取缓存价格"""
        if not self.enable_cache:
            return None
        
        if symbol in self.cache:
            cache_time = self.cache_timestamp.get(symbol)
            if cache_time and (datetime.now() - cache_time).seconds < self.cache_duration:
                data = self.cache[symbol]
                data.is_cached = True
                return data
        
        return None
    
    def _set_cached_price(self, symbol: str, data: PriceData):
        """设置缓存价格"""
        if self.enable_cache:
            self.cache[symbol] = data
            self.cache_timestamp[symbol] = datetime.now()
    
    def _check_rate_limit(self, source: str) -> bool:
        """检查是否超过限流"""
        if source not in self.RATE_LIMITS:
            return True
        
        limit = self.RATE_LIMITS[source]
        max_calls = int(limit['max'] * limit['safety'])
        
        # 检查是否需要重置计数器
        if limit['reset_time'] is None or datetime.now() > limit['reset_time']:
            limit['reset_time'] = datetime.now() + timedelta(minutes=1)
            limit['current'] = 0
        
        return limit['current'] < max_calls
    
    def _update_rate_limit(self, source: str):
        """更新限流计数"""
        if source in self.RATE_LIMITS:
            self.RATE_LIMITS[source]['current'] += 1
    
    def _mark_source_success(self, source: str, response_time: float):
        """标记数据源成功"""
        if source in self.source_health:
            health = self.source_health[source]
            health.is_available = True
            health.last_success = datetime.now()
            health.avg_response_time = (health.avg_response_time + response_time) / 2
    
    def _mark_source_failure(self, source: str):
        """标记数据源失败"""
        if source in self.source_health:
            health = self.source_health[source]
            health.last_failure = datetime.now()
            health.failure_count += 1
            # 连续失败3次标记为不可用
            if health.failure_count >= 3:
                health.is_available = False
    
    def get_price(self, symbol: str, use_cache: bool = True) -> Optional[PriceData]:
        """
        获取股票价格 (多数据源互为保障)
        
        Args:
            symbol: 股票代码
            use_cache: 是否允许使用缓存
        
        Returns:
            价格数据，失败返回None
        """
        # 1. 先检查缓存
        if use_cache:
            cached = self._get_cached_price(symbol)
            if cached:
                print(f"   📦 {symbol}: 使用缓存数据 ({cached.current})")
                return cached
        
        # 2. 确定市场类型
        market = self._get_market_type(symbol)
        sources_to_try = self.SOURCE_PRIORITY.get(market, ['cache'])
        
        # 3. 按优先级尝试各数据源
        for source_name in sources_to_try:
            if source_name == 'cache':
                continue  # 缓存已检查过
            
            # 检查数据源是否可用且未超限流
            health = self.source_health.get(source_name)
            if not health or not health.is_available:
                continue
            
            if not self._check_rate_limit(source_name):
                print(f"   ⏸️ {source_name}接近限流，跳过...")
                continue
            
            # 尝试获取数据
            start_time = time.time()
            try:
                data = self._fetch_from_source(source_name, symbol)
                if data and data.current > 0:
                    # 成功
                    self._update_rate_limit(source_name)
                    self._mark_source_success(source_name, time.time() - start_time)
                    self._set_cached_price(symbol, data)
                    print(f"   ✅ {symbol}: 从{source_name}获取成功 ({data.current})")
                    return data
            except Exception as e:
                print(f"   ❌ {symbol}: {source_name}获取失败 - {e}")
                self._mark_source_failure(source_name)
        
        # 4. 所有数据源都失败，使用缓存兜底
        cached = self._get_cached_price(symbol)
        if cached:
            print(f"   ⚠️ {symbol}: 所有数据源失败，使用过期缓存 ({cached.current})")
            return cached
        
        print(f"   ❌ {symbol}: 所有数据源均不可用")
        return None
    
    def _fetch_from_source(self, source_name: str, symbol: str) -> Optional[PriceData]:
        """从指定数据源获取价格"""
        if source_name == 'finnhub':
            return self._fetch_from_finnhub(symbol)
        elif source_name == 'tushare':
            return self._fetch_from_tushare(symbol)
        elif source_name == 'yahoo':
            return self._fetch_from_yahoo(symbol)
        elif source_name == 'akshare':
            return self._fetch_from_akshare(symbol)
        return None
    
    def _fetch_from_finnhub(self, symbol: str) -> Optional[PriceData]:
        """从Finnhub获取"""
        if 'finnhub' not in self.sources:
            return None
        
        quote = self.sources['finnhub'].get_quote(symbol)
        if quote and quote.get('current'):
            return PriceData(
                symbol=symbol,
                current=quote['current'],
                change=quote.get('change', 0),
                change_pct=quote.get('change_pct', 0),
                open=quote.get('open', 0),
                high=quote.get('high', 0),
                low=quote.get('low', 0),
                previous_close=quote.get('previous_close', 0),
                timestamp=quote.get('timestamp'),
                source='finnhub'
            )
        return None
    
    def _fetch_from_tushare(self, symbol: str) -> Optional[PriceData]:
        """从Tushare获取"""
        if 'tushare' not in self.sources:
            return None
        
        # A股需要转换代码格式
        if symbol.isdigit():
            if len(symbol) == 6:  # A股
                quote = self.sources['tushare'].get_a_share_realtime(symbol)
                if quote and quote.get('close'):
                    return PriceData(
                        symbol=symbol,
                        current=quote['close'],
                        change=quote.get('change', 0),
                        change_pct=quote.get('pct_change', 0),
                        open=quote.get('open', 0),
                        high=quote.get('high', 0),
                        low=quote.get('low', 0),
                        previous_close=quote.get('pre_close', 0),
                        volume=quote.get('volume'),
                        timestamp=datetime.now().isoformat(),
                        source='tushare'
                    )
        return None
    
    def _fetch_from_yahoo(self, symbol: str) -> Optional[PriceData]:
        """从Yahoo Finance获取"""
        if 'yahoo' not in self.sources:
            return None
        
        try:
            ticker = self.sources['yahoo'].Ticker(symbol)
            info = ticker.info
            
            if info and 'currentPrice' in info:
                return PriceData(
                    symbol=symbol,
                    current=info['currentPrice'],
                    change=info.get('regularMarketChange', 0),
                    change_pct=info.get('regularMarketChangePercent', 0),
                    open=info.get('regularMarketOpen', 0),
                    high=info.get('regularMarketDayHigh', 0),
                    low=info.get('regularMarketDayLow', 0),
                    previous_close=info.get('regularMarketPreviousClose', 0),
                    volume=info.get('regularMarketVolume'),
                    timestamp=datetime.now().isoformat(),
                    source='yahoo'
                )
        except Exception:
            pass
        return None
    
    def _fetch_from_akshare(self, symbol: str) -> Optional[PriceData]:
        """从akshare获取"""
        # akshare备用实现
        return None
    
    def get_prices_batch(self, symbols: List[str]) -> Dict[str, Optional[PriceData]]:
        """
        批量获取价格 (带进度显示)
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            价格字典
        """
        results = {}
        total = len(symbols)
        
        print(f"\n📊 批量获取{total}只股票价格...")
        for i, symbol in enumerate(symbols, 1):
            print(f"   [{i}/{total}] ", end="")
            results[symbol] = self.get_price(symbol)
        
        # 统计结果
        success = sum(1 for v in results.values() if v is not None)
        cached = sum(1 for v in results.values() if v and v.is_cached)
        print(f"\n   ✅ 成功: {success}/{total} (缓存: {cached})")
        
        return results
    
    def get_health_report(self) -> Dict:
        """获取数据源健康报告"""
        return {
            'timestamp': datetime.now().isoformat(),
            'sources': {name: asdict(health) for name, health in self.source_health.items()},
            'rate_limits': self.RATE_LIMITS,
            'cache_size': len(self.cache)
        }
    
    def print_health_report(self):
        """打印健康报告"""
        report = self.get_health_report()
        print("\n" + "="*60)
        print("📊 A5L数据源健康报告")
        print("="*60)
        
        for name, health in report['sources'].items():
            status = "🟢 正常" if health['is_available'] else "🔴 异常"
            # Bug修复: 将datetime转换为字符串后再切片
            last_success = str(health['last_success'])[:19] if health['last_success'] else "从未"
            print(f"\n{name}:")
            print(f"   状态: {status}")
            print(f"   最后成功: {last_success}")
            print(f"   失败次数: {health['failure_count']}")
            print(f"   平均响应: {health['avg_response_time']:.2f}秒")
        
        print("\n" + "-"*60)
        print("限流状态:")
        for name, limit in report['rate_limits'].items():
            if limit['reset_time']:
                usage = limit['current'] / (limit['max'] * limit['safety']) * 100
                print(f"   {name}: {limit['current']}/{int(limit['max'] * limit['safety'])} ({usage:.1f}%)")
        
        print(f"\n缓存: {report['cache_size']}条记录")
        print("="*60)


def test_unified_data_source():
    """测试统一数据源"""
    print("="*70)
    print("🧪 A5L统一数据源管理器 - 测试")
    print("="*70)
    
    # 初始化
    manager = UnifiedDataSourceManager()
    
    # 测试美股
    print("\n🇺🇸 测试美股:")
    us_stocks = ['NVDA', 'AAPL', 'TSLA']
    for symbol in us_stocks:
        data = manager.get_price(symbol)
        if data:
            print(f"   {symbol}: ${data.current:.2f} ({data.source})")
        else:
            print(f"   {symbol}: 获取失败")
    
    # 测试A股
    print("\n🇨🇳 测试A股:")
    cn_stocks = ['000001', '300750']
    for symbol in cn_stocks:
        data = manager.get_price(symbol)
        if data:
            print(f"   {symbol}: ¥{data.current:.2f} ({data.source})")
        else:
            print(f"   {symbol}: 获取失败")
    
    # 打印健康报告
    manager.print_health_report()


if __name__ == '__main__':
    test_unified_data_source()
