#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 1: Data Source Manager
数据底座层 - 数据源管理器

功能：
1. 管理多数据源连接（AKShare, TuShare, EastMoney, Jin10）
2. 数据源自动切换和故障转移
3. 统一数据接口
4. 数据质量监控
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import time

@dataclass
class DataSourceConfig:
    """数据源配置"""
    name: str
    enabled: bool
    priority: int  # 优先级，数字越小优先级越高
    rate_limit: int  # 每分钟请求限制
    timeout: int  # 超时时间（秒）
    retry_count: int  # 重试次数
    config: Dict[str, Any]  # 特定配置

class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.config_dir = f"{workspace}/ARCHITECT_5L/layer1_data/config"
        self.config_file = f"{self.config_dir}/datasource_registry.json"
        
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 加载或初始化配置
        self.sources = self._load_or_init_config()
        
        # 连接器实例缓存
        self._connectors = {}
        
        # 使用统计
        self._usage_stats = {}
    
    def _load_or_init_config(self) -> Dict[str, DataSourceConfig]:
        """加载或初始化数据源配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both flat structure and nested 'connectors' structure
                if 'connectors' in data:
                    connectors = data['connectors']
                else:
                    connectors = data
                return {k: DataSourceConfig(
                    name=v['name'],
                    enabled=v['enabled'],
                    priority=v['priority'],
                    rate_limit=v['rate_limit'],
                    timeout=v['timeout'],
                    retry_count=v['retry_count'],
                    config={key: val for key, val in v.items() if key not in ['name', 'enabled', 'priority', 'rate_limit', 'timeout', 'retry_count']}
                ) for k, v in connectors.items() if isinstance(v, dict)}
        
        # 初始化默认配置
        default_config = {
            "akshare": DataSourceConfig(
                name="AKShare",
                enabled=True,
                priority=1,
                rate_limit=300,
                timeout=30,
                retry_count=3,
                config={
                    "base_url": "http://api.akshare.com",
                    "supports": ["A_share", "futures", "options", "macro"],
                    "update_frequency": "realtime"
                }
            ),
            "tushare": DataSourceConfig(
                name="TuShare",
                enabled=True,
                priority=2,
                rate_limit=200,
                timeout=30,
                retry_count=3,
                config={
                    "api_token": "",  # 需要用户配置
                    "supports": ["A_share", "financial", "market", "fund"],
                    "update_frequency": "daily"
                }
            ),
            "eastmoney": DataSourceConfig(
                name="EastMoney",
                enabled=True,
                priority=3,
                rate_limit=100,
                timeout=20,
                retry_count=2,
                config={
                    "base_url": "https://push2.eastmoney.com",
                    "supports": ["A_share", "fund_flow", "sector", "news"],
                    "update_frequency": "realtime"
                }
            ),
            "jin10": DataSourceConfig(
                name="Jin10",
                enabled=True,
                priority=4,
                rate_limit=60,
                timeout=15,
                retry_count=2,
                config={
                    "base_url": "https://flash-api.jin10.com",
                    "supports": ["news", "calendar", "sentiment", "forex"],
                    "update_frequency": "realtime"
                }
            ),
            "yahoo_finance": DataSourceConfig(
                name="Yahoo Finance",
                enabled=True,
                priority=1,
                rate_limit=200,
                timeout=30,
                retry_count=3,
                config={
                    "supports": ["US_stocks", "HK_stocks", "ETF", "forex"],
                    "update_frequency": "delayed"
                }
            ),
            "hkex": DataSourceConfig(
                name="HKEX",
                enabled=True,
                priority=2,
                rate_limit=100,
                timeout=30,
                retry_count=3,
                config={
                    "base_url": "https://www.hkex.com.hk",
                    "supports": ["HK_stocks", "derivatives"],
                    "update_frequency": "15min"
                }
            )
        }
        
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, DataSourceConfig]):
        """保存配置"""
        data = {k: {
            "name": v.name,
            "enabled": v.enabled,
            "priority": v.priority,
            "rate_limit": v.rate_limit,
            "timeout": v.timeout,
            "retry_count": v.retry_count,
            "config": v.config
        } for k, v in config.items()}
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_active_sources(self, market: Optional[str] = None) -> List[str]:
        """获取活跃数据源，按优先级排序"""
        active = [(k, v) for k, v in self.sources.items() if v.enabled]
        active.sort(key=lambda x: x[1].priority)
        
        if market:
            active = [(k, v) for k, v in active 
                     if market.lower() in str(v.config.get('supports', [])).lower()]
        
        return [k for k, v in active]
    
    def get_source_config(self, source_name: str) -> Optional[DataSourceConfig]:
        """获取数据源配置"""
        return self.sources.get(source_name)
    
    def update_source_config(self, source_name: str, **kwargs):
        """更新数据源配置"""
        if source_name in self.sources:
            config = self.sources[source_name]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            self._save_config(self.sources)
    
    def record_usage(self, source_name: str, success: bool, latency: float):
        """记录数据源使用情况"""
        if source_name not in self._usage_stats:
            self._usage_stats[source_name] = {
                "total_calls": 0,
                "success_calls": 0,
                "failed_calls": 0,
                "avg_latency": 0.0,
                "last_used": None
            }
        
        stats = self._usage_stats[source_name]
        stats["total_calls"] += 1
        stats["success_calls"] += 1 if success else 0
        stats["failed_calls"] += 0 if success else 1
        
        # 更新平均延迟
        old_avg = stats["avg_latency"]
        n = stats["total_calls"]
        stats["avg_latency"] = (old_avg * (n - 1) + latency) / n
        stats["last_used"] = datetime.now().isoformat()
    
    def get_source_health(self, source_name: str) -> Dict:
        """获取数据源健康状态"""
        config = self.sources.get(source_name)
        stats = self._usage_stats.get(source_name, {})
        
        if not config:
            return {"status": "unknown", "error": "Source not found"}
        
        total = stats.get("total_calls", 0)
        success = stats.get("success_calls", 0)
        
        success_rate = success / total if total > 0 else 1.0
        
        if not config.enabled:
            status = "disabled"
        elif success_rate < 0.5 and total > 10:
            status = "unhealthy"
        elif success_rate < 0.8 and total > 10:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "enabled": config.enabled,
            "priority": config.priority,
            "success_rate": success_rate,
            "avg_latency": stats.get("avg_latency", 0),
            "total_calls": total,
            "last_used": stats.get("last_used")
        }
    
    def get_all_health_status(self) -> Dict[str, Dict]:
        """获取所有数据源健康状态"""
        return {name: self.get_source_health(name) for name in self.sources.keys()}
    
    def select_best_source(self, data_type: str, market: str) -> Optional[str]:
        """根据数据类型和市场选择最佳数据源"""
        candidates = self.get_active_sources(market)
        
        best_source = None
        best_score = -1
        
        for source_name in candidates:
            health = self.get_source_health(source_name)
            config = self.sources[source_name]
            
            # 跳过不健康的数据源
            if health["status"] in ["disabled", "unhealthy"]:
                continue
            
            # 计算评分
            score = 0
            score += (100 - config.priority * 10)  # 优先级
            score += health["success_rate"] * 50  # 成功率
            score -= health["avg_latency"] * 2  # 延迟惩罚
            
            # 检查是否支持数据类型
            supports = config.config.get("supports", [])
            if data_type.lower() in str(supports).lower():
                score += 30
            
            if score > best_score:
                best_score = score
                best_source = source_name
        
        return best_source
    
    def generate_health_report(self) -> str:
        """生成健康报告"""
        report = f"""# 📊 数据源健康报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🔌 数据源状态

| 数据源 | 状态 | 优先级 | 成功率 | 平均延迟 | 总调用 |
|--------|------|--------|--------|----------|--------|
"""
        
        for name in sorted(self.sources.keys()):
            health = self.get_source_health(name)
            config = self.sources[name]
            
            status_icon = {
                "healthy": "🟢",
                "degraded": "🟡",
                "unhealthy": "🔴",
                "disabled": "⚪"
            }.get(health["status"], "⚪")
            
            report += f"| {config.name} | {status_icon} {health['status']} | {config.priority} | {health['success_rate']:.1%} | {health['avg_latency']:.2f}s | {health['total_calls']} |\n"
        
        report += """
---

## 📋 配置详情

"""
        
        for name, config in self.sources.items():
            report += f"""### {config.name}
- **优先级**: {config.priority}
- **速率限制**: {config.rate_limit} req/min
- **超时**: {config.timeout}s
- **重试**: {config.retry_count}次
- **支持市场**: {', '.join(config.config.get('supports', []))}
- **更新频率**: {config.config.get('update_frequency', 'unknown')}

"""
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("🔌 数据源管理器 (Layer 1)")
    print("=" * 70)
    
    manager = DataSourceManager()
    
    # 显示活跃数据源
    print("\n📡 活跃数据源（按优先级）:")
    for market in ["A_share", "US_stocks", "HK_stocks"]:
        sources = manager.get_active_sources(market)
        print(f"\n{market}:")
        for src in sources:
            config = manager.get_source_config(src)
            print(f"  • {config.name} (优先级: {config.priority})")
    
    # 显示健康状态
    print("\n" + "=" * 70)
    print("📊 健康状态:")
    print("=" * 70)
    health = manager.get_all_health_status()
    for name, status in health.items():
        icon = "🟢" if status['status'] == 'healthy' else "🟡" if status['status'] == 'degraded' else "🔴"
        print(f"{icon} {name}: {status['status']} (成功率: {status['success_rate']:.1%})")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 生成健康报告...")
    report = manager.generate_health_report()
    print(report[:500] + "...")

if __name__ == "__main__":
    main()
