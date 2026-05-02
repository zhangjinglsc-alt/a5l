#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取SKILL v2.0
从多个数据源获取市场数据
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

class DataSource(ABC):
    """数据源抽象类"""
    
    @abstractmethod
    def fetch(self, symbol: str) -> Dict:
        """获取数据"""
        pass

class EastMoneySource(DataSource):
    """东方财富数据源"""
    
    def fetch(self, symbol: str) -> Dict:
        # 模拟东方财富数据获取
        return {
            "source": "eastmoney",
            "symbol": symbol,
            "price": 19.82,
            "change": 0.1,
            "change_pct": 0.5,
            "volume": 1000000,
            "timestamp": datetime.now().isoformat()
        }

class SinaSource(DataSource):
    """新浪数据源"""
    
    def fetch(self, symbol: str) -> Dict:
        # 模拟新浪数据获取
        return {
            "source": "sina",
            "symbol": symbol,
            "price": 19.80,
            "change": 0.08,
            "change_pct": 0.4,
            "volume": 950000,
            "timestamp": datetime.now().isoformat()
        }

class DataFetcher:
    """数据获取器 v2.0"""
    
    METADATA = {
        "id": "skill_data_fetcher",
        "name": "数据获取",
        "version": "2.0.0",
        "category": "system",
        "description": "从多个数据源获取市场数据",
        "author": "Evolution Daemon",
        "created_at": "2026-05-01T00:35:00+08:00",
        "updated_at": "2026-05-01T00:35:00+08:00",
        "enabled": True,
        "dependencies": [],
        "config": {
            "sources": ["eastmoney", "sina", "tencent"],
            "cache_enabled": True,
            "cache_ttl": 300,
            "timeout": 10
        }
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.sources = {}
        self.cache = {}
        self._init_sources()
        
    def _init_sources(self):
        """初始化数据源"""
        self.sources["eastmoney"] = EastMoneySource()
        self.sources["sina"] = SinaSource()
        # 可以添加更多数据源
        
    def initialize(self) -> bool:
        """初始化数据获取器"""
        try:
            self.logger.info("初始化数据获取器")
            return True
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False
    
    def execute(self, request: Dict) -> Dict:
        """执行数据获取"""
        try:
            symbol = request.get("symbol", "")
            source_name = request.get("source", "eastmoney")
            use_cache = request.get("use_cache", True)
            
            # 检查缓存
            if use_cache and self._is_cache_valid(symbol):
                return self._get_from_cache(symbol)
            
            # 从数据源获取
            data = self._fetch_from_source(symbol, source_name)
            
            # 更新缓存
            if use_cache:
                self._update_cache(symbol, data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"数据获取失败: {e}")
            return {"error": str(e)}
    
    def _fetch_from_source(self, symbol: str, source_name: str) -> Dict:
        """从指定数据源获取数据"""
        source = self.sources.get(source_name)
        if not source:
            return {"error": f"数据源 {source_name} 不存在"}
        
        return source.fetch(symbol)
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """检查缓存是否有效"""
        if symbol not in self.cache:
            return False
        
        cache_entry = self.cache[symbol]
        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        ttl = self.config.get("cache_ttl", 300)
        
        return (datetime.now() - cache_time).total_seconds() < ttl
    
    def _get_from_cache(self, symbol: str) -> Dict:
        """从缓存获取数据"""
        return self.cache.get(symbol, {})
    
    def _update_cache(self, symbol: str, data: Dict):
        """更新缓存"""
        self.cache[symbol] = {
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    def fetch_batch(self, symbols: List[str]) -> List[Dict]:
        """批量获取数据"""
        results = []
        for symbol in symbols:
            data = self.execute({"symbol": symbol})
            results.append(data)
        return results
    
    def get_metadata(self) -> Dict:
        """获取SKILL元数据"""
        return self.METADATA
    
    def get_status(self) -> Dict:
        """获取SKILL运行状态"""
        return {
            "status": "running",
            "available_sources": list(self.sources.keys()),
            "cache_size": len(self.cache),
            "config": self.config
        }
    
    def cleanup(self) -> bool:
        """清理数据获取器"""
        try:
            self.cache = {}
            return True
        except Exception as e:
            self.logger.error(f"清理失败: {e}")
            return False

if __name__ == "__main__":
    fetcher = DataFetcher()
    fetcher.initialize()
    
    result = fetcher.execute({"symbol": "000066"})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n=== SKILL状态 ===")
    print(json.dumps(fetcher.get_status(), indent=2, ensure_ascii=False))
    
    print("\n=== SKILL元数据 ===")
    print(json.dumps(fetcher.get_metadata(), indent=2, ensure_ascii=False))
