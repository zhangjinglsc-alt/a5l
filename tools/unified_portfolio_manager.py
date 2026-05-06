#!/usr/bin/env python3
"""
A5L Unified Portfolio Manager v2.1
统一持仓管理器 - 解决真实持仓与模拟持仓混乱问题

核心功能：
1. 严格区分 [🔴 REAL] 真实持仓 和 [🔵 SIM] 模拟持仓
2. 统一数据访问接口
3. 自动校验数据完整性
4. 支持OCR截图自动解析（未来扩展）
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
from enum import Enum

class PositionType(Enum):
    """持仓类型"""
    REAL = "real"      # 🔴 真实持仓
    SIM = "sim"        # 🔵 模拟持仓

class PortfolioSource(Enum):
    """数据来源"""
    SIGNAL_ARENA = "signal_arena"      # SignalArena截图
    MANUAL_INPUT = "manual"            # 手动输入
    BROKER_API = "broker"              # 券商API（未来）
    SIMULATION = "simulation"          # 模拟交易

class UnifiedPortfolioManager:
    """
    A5L统一持仓管理器 v2.1
    
    解决的核心问题：
    - Bug #1: 系统有时记不住真实持仓
    - 真实持仓与模拟持仓混淆
    """
    
    # 数据文件路径（严格区分）
    REAL_POSITION_FILE = Path("/workspace/projects/workspace/memory/portfolio/REAL_POSITION_MASTER.md")
    SIM_POSITION_DIR = Path("/workspace/projects/workspace/data/simulation")
    
    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self.CACHE_TTL = 10  # 缓存10秒
    
    def _get_sim_file_path(self, market: str) -> Path:
        """获取模拟持仓文件路径"""
        market = market.upper()
        file_map = {
            "US": "US_SIM_001.json",
            "CN": "CN_SIM_001.json",
            "HK": "HK_SIM_001.json"
        }
        if market not in file_map:
            raise ValueError(f"未知市场: {market}，支持: {list(file_map.keys())}")
        return self.SIM_POSITION_DIR / file_map[market]
    
    def get_real_positions(self, use_cache: bool = True) -> Dict:
        """
        获取真实持仓（🔴 REAL）
        
        数据来源: memory/portfolio/REAL_POSITION_MASTER.md
        
        Returns:
            {
                "type": "REAL",
                "accounts": [
                    {
                        "name": "张晋",
                        "tail": "6662",
                        "broker": "国联民生",
                        "total_assets": 957241.03,
                        "positions": [...]
                    }
                ],
                "total_assets": 4754193.05,
                "last_update": "2026-05-06T02:57:00"
            }
        """
        cache_key = "real_positions"
        
        if use_cache and cache_key in self._cache:
            cache_age = (datetime.now() - self._cache_time[cache_key]).total_seconds()
            if cache_age < self.CACHE_TTL:
                return self._cache[cache_key]
        
        # 读取真实持仓Markdown文件
        if not self.REAL_POSITION_FILE.exists():
            raise FileNotFoundError(f"真实持仓文件不存在: {self.REAL_POSITION_FILE}")
        
        content = self.REAL_POSITION_FILE.read_text(encoding='utf-8')
        
        # 解析Markdown内容（简化解析）
        result = {
            "type": "REAL",
            "source": PortfolioSource.SIGNAL_ARENA.value,
            "accounts": [],
            "total_assets": 0.0,
            "last_update": self._extract_update_time(content),
            "raw_content": content[:500] + "..." if len(content) > 500 else content
        }
        
        # 缓存结果
        if use_cache:
            self._cache[cache_key] = result
            self._cache_time[cache_key] = datetime.now()
        
        return result
    
    def get_sim_positions(self, market: str, use_cache: bool = True) -> Dict:
        """
        获取模拟持仓（🔵 SIM）
        
        数据来源: data/simulation/{market}_SIM_001.json
        
        Args:
            market: 市场代码 (US/CN/HK)
            
        Returns:
            {
                "type": "SIM",
                "market": "US",
                "account": "US_SIM_001",
                "cash": 957629.36,
                "positions": {...},
                "total_value": 999900.0,
                "trades": [...]
            }
        """
        cache_key = f"sim_{market.upper()}"
        
        if use_cache and cache_key in self._cache:
            cache_age = (datetime.now() - self._cache_time[cache_key]).total_seconds()
            if cache_age < self.CACHE_TTL:
                return self._cache[cache_key]
        
        file_path = self._get_sim_file_path(market)
        
        if not file_path.exists():
            raise FileNotFoundError(f"模拟持仓文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 构建标准返回格式
        positions = data.get("positions", {})
        total_market_value = sum(
            pos.get("market_value", 0) 
            for pos in positions.values()
        )
        
        result = {
            "type": "SIM",
            "market": market.upper(),
            "account": data.get("account", f"{market.upper()}_SIM_001"),
            "currency": data.get("currency", "USD"),
            "initial_capital": data.get("initial_capital", 1000000.0),
            "cash": data.get("cash", 0.0),
            "positions": positions,
            "market_value": total_market_value,
            "total_value": data.get("cash", 0.0) + total_market_value,
            "trades": data.get("trades", []),
            "trade_count": len(data.get("trades", [])),
            "position_count": len(positions),
            "last_updated": data.get("last_updated", datetime.now().isoformat())
        }
        
        # 缓存结果
        if use_cache:
            self._cache[cache_key] = result
            self._cache_time[cache_key] = datetime.now()
        
        return result
    
    def get_all_sim_positions(self) -> Dict[str, Dict]:
        """获取所有市场的模拟持仓"""
        return {
            "US": self.get_sim_positions("US"),
            "CN": self.get_sim_positions("CN"),
            "HK": self.get_sim_positions("HK")
        }
    
    def get_position_summary(self, pos_type: PositionType, market: Optional[str] = None) -> Dict:
        """
        获取持仓摘要
        
        Args:
            pos_type: REAL 或 SIM
            market: 仅对SIM有效 (US/CN/HK)
        """
        if pos_type == PositionType.REAL:
            data = self.get_real_positions()
            return {
                "type": "🔴 REAL",
                "accounts": len(data.get("accounts", [])),
                "total_assets": data.get("total_assets", 0),
                "last_update": data.get("last_update", "未知")
            }
        else:
            if not market:
                raise ValueError("SIM类型必须指定市场 (US/CN/HK)")
            data = self.get_sim_positions(market)
            return {
                "type": "🔵 SIM",
                "market": market,
                "position_count": data["position_count"],
                "total_value": data["total_value"],
                "cash": data["cash"],
                "pnl": data["total_value"] - data["initial_capital"]
            }
    
    def _extract_update_time(self, content: str) -> str:
        """从Markdown内容中提取更新时间"""
        # 简化实现：查找 update_time: 字段
        for line in content.split('\n'):
            if 'update_time:' in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return datetime.now().strftime('%Y-%m-%d %H:%M')
    
    def validate_all(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        验证所有持仓数据
        
        Returns:
            (是否全部有效, {类型: 错误列表})
        """
        all_valid = True
        all_errors = {}
        
        # 验证真实持仓
        try:
            self.get_real_positions(use_cache=False)
            all_errors["REAL"] = []
        except Exception as e:
            all_valid = False
            all_errors["REAL"] = [str(e)]
        
        # 验证模拟持仓
        for market in ["US", "CN", "HK"]:
            try:
                self.get_sim_positions(market, use_cache=False)
                all_errors[f"SIM_{market}"] = []
            except Exception as e:
                all_valid = False
                all_errors[f"SIM_{market}"] = [str(e)]
        
        return all_valid, all_errors
    
    def invalidate_cache(self):
        """清除缓存"""
        self._cache.clear()
        self._cache_time.clear()


# 便捷函数
def get_real_positions() -> Dict:
    """便捷函数：获取真实持仓"""
    manager = UnifiedPortfolioManager()
    return manager.get_real_positions()

def get_sim_positions(market: str) -> Dict:
    """便捷函数：获取模拟持仓"""
    manager = UnifiedPortfolioManager()
    return manager.get_sim_positions(market)

def get_position_summary(pos_type: str, market: Optional[str] = None) -> Dict:
    """便捷函数：获取持仓摘要"""
    manager = UnifiedPortfolioManager()
    pt = PositionType.REAL if pos_type.upper() == "REAL" else PositionType.SIM
    return manager.get_position_summary(pt, market)


# CLI支持
if __name__ == "__main__":
    import sys
    
    manager = UnifiedPortfolioManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "validate":
            is_valid, errors = manager.validate_all()
            print(f"数据验证: {'✅ 通过' if is_valid else '❌ 失败'}")
            for key, errs in errors.items():
                if errs:
                    print(f"  {key}: {errs[0]}")
            sys.exit(0 if is_valid else 1)
        
        elif command == "real":
            data = manager.get_real_positions()
            print(f"\n🔴 真实持仓")
            print(f"账户数: {len(data.get('accounts', []))}")
            print(f"总资产: ¥{data.get('total_assets', 0):,.2f}")
            print(f"更新时间: {data.get('last_update', '未知')}")
            sys.exit(0)
        
        elif command in ["US", "CN", "HK"]:
            data = manager.get_sim_positions(command)
            print(f"\n🔵 模拟持仓 - {command}")
            print(f"持仓数: {data['position_count']}")
            print(f"总资产: {data['currency']}{data['total_value']:,.2f}")
            print(f"盈亏: {data['currency']}{data['pnl']:+,.2f}")
            if data['positions']:
                print("\n持仓明细:")
                for symbol, pos in data['positions'].items():
                    pnl_emoji = "🟢" if pos.get('unrealized_pnl', 0) >= 0 else "🔴"
                    print(f"  {pnl_emoji} {symbol}: {pos['quantity']}股 "
                          f"@ ${pos['cost_basis']:.2f} "
                          f"({'+' if pos.get('unrealized_pnl', 0) >= 0 else ''}{pos.get('unrealized_pnl', 0):+.2f})")
            sys.exit(0)
    
    # 默认：显示所有
    print("=== A5L 统一持仓管理器 v2.1 ===\n")
    
    # 真实持仓
    try:
        data = manager.get_real_positions()
        print(f"🔴 真实持仓: {len(data.get('accounts', []))}个账户, "
              f"总资产¥{data.get('total_assets', 0):,.2f}")
    except Exception as e:
        print(f"🔴 真实持仓: 读取失败 - {e}")
    
    # 模拟持仓
    for market in ["US", "CN", "HK"]:
        try:
            data = manager.get_sim_positions(market)
            pnl_emoji = "🟢" if data['pnl'] >= 0 else "🔴"
            print(f"🔵 {market}: {data['position_count']}只持仓, "
                  f"{data['currency']}{data['total_value']:,.2f} "
                  f"{pnl_emoji}{data['pnl']:+,.2f}")
        except Exception as e:
            print(f"🔵 {market}: 读取失败 - {e}")
    
    print("\n✅ 数据加载完成")
