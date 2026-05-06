#!/usr/bin/env python3
"""
A5L Unified Position Manager
统一持仓数据管理器 - 单一真相源 (Single Source of Truth)

所有组件必须通过此模块访问持仓数据，禁止直接读取JSON文件。
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

# 数据文件路径（唯一真相源）
DATA_DIR = Path("/workspace/projects/workspace/data/simulation")
MARKET_FILES = {
    "US": "US_SIM_001.json",
    "CN": "CN_SIM_001.json",
    "HK": "HK_SIM_001.json"
}

# 数据契约 - 必填字段
REQUIRED_FIELDS = {
    "account": str,
    "currency": str,
    "initial_capital": (int, float),
    "cash": (int, float),
    "positions": dict,
    "trades": list
}

POSITION_REQUIRED_FIELDS = {
    "symbol": str,
    "quantity": (int, float),
    "cost_basis": (int, float),
    "current_price": (int, float),
    "market_value": (int, float),
    "unrealized_pnl": (int, float),
    "unrealized_pnl_pct": (int, float)
}


class DataValidationError(Exception):
    """数据验证错误"""
    pass


class UnifiedPositionManager:
    """
    A5L统一持仓数据管理器
    
    职责：
    1. 提供统一的数据读取接口
    2. 确保数据格式符合契约
    3. 自动校验数据完整性
    4. 防止数据不一致
    """
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self._cache = {}
        self._cache_time = {}
        self.CACHE_TTL = 5  # 缓存5秒
    
    def _get_file_path(self, market: str) -> Path:
        """获取市场数据文件路径"""
        if market.upper() not in MARKET_FILES:
            raise ValueError(f"未知市场: {market}，支持: {list(MARKET_FILES.keys())}")
        return self.data_dir / MARKET_FILES[market.upper()]
    
    def _validate_data_format(self, data: Dict, market: str) -> Tuple[bool, List[str]]:
        """
        验证数据格式是否符合契约
        
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        # 检查必填字段
        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in data:
                errors.append(f"缺少必填字段: {field}")
                continue
            if not isinstance(data[field], expected_type):
                errors.append(f"字段 {field} 类型错误: 期望 {expected_type}, 实际 {type(data[field])}")
        
        # 检查positions格式
        positions = data.get("positions", {})
        if not isinstance(positions, dict):
            errors.append("positions 必须是字典类型")
        else:
            for symbol, pos in positions.items():
                if not isinstance(pos, dict):
                    errors.append(f"持仓 {symbol} 必须是字典类型")
                    continue
                for field, expected_type in POSITION_REQUIRED_FIELDS.items():
                    if field not in pos:
                        errors.append(f"持仓 {symbol} 缺少字段: {field}")
                        continue
                    if not isinstance(pos[field], expected_type):
                        errors.append(f"持仓 {symbol}.{field} 类型错误")
        
        return len(errors) == 0, errors
    
    def _calculate_checksum(self, data: Dict) -> str:
        """计算数据校验和"""
        # 移除可能变化的时间戳字段
        check_data = {k: v for k, v in data.items() if k not in ['last_updated', 'created_at']}
        json_str = json.dumps(check_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    def get_positions(self, market: str, use_cache: bool = True) -> Dict:
        """
        读取指定市场的持仓数据（唯一真相源）
        
        Args:
            market: 市场代码 (US/CN/HK)
            use_cache: 是否使用缓存
            
        Returns:
            {
                "account": str,
                "cash": float,
                "positions": Dict[str, Dict],
                "total_value": float,
                "trades": List[Dict],
                "_meta": {
                    "checksum": str,
                    "validated": bool,
                    "errors": List[str]
                }
            }
        """
        market = market.upper()
        cache_key = market
        
        # 检查缓存
        if use_cache and cache_key in self._cache:
            cache_age = (datetime.now() - self._cache_time[cache_key]).total_seconds()
            if cache_age < self.CACHE_TTL:
                return self._cache[cache_key]
        
        file_path = self._get_file_path(market)
        
        # 检查文件存在
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        # 读取数据
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # 验证数据格式
        is_valid, errors = self._validate_data_format(raw_data, market)
        
        # 计算总资产
        positions = raw_data.get("positions", {})
        total_market_value = sum(
            pos.get("market_value", 0) 
            for pos in positions.values()
        )
        total_value = raw_data.get("cash", 0) + total_market_value
        
        # 构建标准返回格式
        result = {
            "account": raw_data.get("account", f"{market}_SIM_001"),
            "currency": raw_data.get("currency", "USD" if market == "US" else "CNY" if market == "CN" else "HKD"),
            "initial_capital": raw_data.get("initial_capital", 1000000.0),
            "cash": raw_data.get("cash", 0.0),
            "positions": positions,
            "total_value": total_value,
            "trades": raw_data.get("trades", []),
            "watchlist": raw_data.get("watchlist", []),
            "_meta": {
                "source_file": str(file_path),
                "checksum": self._calculate_checksum(raw_data),
                "validated": is_valid,
                "errors": errors,
                "loaded_at": datetime.now().isoformat()
            }
        }
        
        # 缓存结果
        if use_cache:
            self._cache[cache_key] = result
            self._cache_time[cache_key] = datetime.now()
        
        return result
    
    def get_all_markets(self) -> Dict[str, Dict]:
        """获取所有市场的持仓数据"""
        return {
            market: self.get_positions(market)
            for market in MARKET_FILES.keys()
        }
    
    def get_position_summary(self, market: str) -> Dict:
        """获取持仓摘要（用于快速展示）"""
        data = self.get_positions(market)
        positions = data["positions"]
        
        return {
            "account": data["account"],
            "cash": data["cash"],
            "position_count": len(positions),
            "market_value": sum(p.get("market_value", 0) for p in positions.values()),
            "total_value": data["total_value"],
            "total_pnl": data["total_value"] - data["initial_capital"],
            "holdings": [
                {
                    "symbol": symbol,
                    "quantity": pos["quantity"],
                    "cost": pos["cost_basis"],
                    "price": pos["current_price"],
                    "value": pos["market_value"],
                    "pnl": pos["unrealized_pnl"],
                    "pnl_pct": pos["unrealized_pnl_pct"]
                }
                for symbol, pos in positions.items()
            ]
        }
    
    def validate_all(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        验证所有市场数据
        
        Returns:
            (是否全部有效, {市场: 错误列表})
        """
        all_valid = True
        all_errors = {}
        
        for market in MARKET_FILES.keys():
            try:
                data = self.get_positions(market, use_cache=False)
                if not data["_meta"]["validated"]:
                    all_valid = False
                    all_errors[market] = data["_meta"]["errors"]
                else:
                    all_errors[market] = []
            except Exception as e:
                all_valid = False
                all_errors[market] = [str(e)]
        
        return all_valid, all_errors
    
    def invalidate_cache(self):
        """清除缓存"""
        self._cache.clear()
        self._cache_time.clear()


# 全局实例
_position_manager = None

def get_position_manager() -> UnifiedPositionManager:
    """获取全局统一持仓管理器实例"""
    global _position_manager
    if _position_manager is None:
        _position_manager = UnifiedPositionManager()
    return _position_manager


# 便捷函数
def get_positions(market: str) -> Dict:
    """便捷函数：读取持仓"""
    return get_position_manager().get_positions(market)

def get_all_positions() -> Dict[str, Dict]:
    """便捷函数：读取所有市场"""
    return get_position_manager().get_all_markets()

def validate_data() -> Tuple[bool, Dict]:
    """便捷函数：验证数据"""
    return get_position_manager().validate_all()


# CLI 支持
if __name__ == "__main__":
    import sys
    
    manager = UnifiedPositionManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "validate":
            # 验证所有数据
            is_valid, errors = manager.validate_all()
            print(f"数据验证: {'✅ 通过' if is_valid else '❌ 失败'}")
            for market, errs in errors.items():
                if errs:
                    print(f"  {market}: {len(errs)} 个错误")
                    for e in errs[:3]:
                        print(f"    - {e}")
            sys.exit(0 if is_valid else 1)
        
        elif command in ["US", "CN", "HK"]:
            # 显示指定市场持仓
            data = manager.get_positions(command)
            print(f"\n=== {command} 市场持仓 ===")
            print(f"账户: {data['account']}")
            print(f"现金: {data['currency']}{data['cash']:,.2f}")
            print(f"持仓数: {len(data['positions'])}")
            print(f"总市值: {data['currency']}{data['total_value']:,.2f}")
            print("\n持仓明细:")
            for symbol, pos in data['positions'].items():
                print(f"  {symbol}: {pos['quantity']}股 @ ${pos['cost_basis']:.2f} "
                      f"(现${pos['current_price']:.2f}) "
                      f"{'🟢' if pos['unrealized_pnl'] >= 0 else '🔴'} "
                      f"{pos['unrealized_pnl']:+.2f}")
            sys.exit(0)
    
    # 默认：显示所有市场
    print("=== A5L 统一持仓管理器 ===")
    for market in ["US", "CN", "HK"]:
        try:
            data = manager.get_positions(market)
            summary = manager.get_position_summary(market)
            print(f"\n{market}: {summary['position_count']}只持仓, "
                  f"总价值{data['currency']}{summary['total_value']:,.2f}")
        except FileNotFoundError:
            print(f"\n{market}: 数据文件不存在")
    
    print("\n✅ 数据加载完成")
