#!/usr/bin/env python3
"""
A5L 持仓数据统一接口
确保所有SKILL和Cron任务调用到完全正确的持仓

 Chief指令: "一定要让所有的SKILL能够调用到完全正确的持仓！"
"""

import json
import os
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

# 持仓文件路径 (唯一真相源)
POSITION_SOURCES = {
    # 🔴 REAL - 真实持仓
    "REAL": {
        "master_file": "/workspace/projects/workspace/memory/portfolio/REAL_POSITION_MASTER.md",
        "mapping_file": "/workspace/projects/workspace/config/position_mapping.json",
        "type": "真实资金",
        "warning": "⚠️ 涉及真实资金，操作前必须二次确认！"
    },
    # 🔵 SIM - 模拟持仓
    "US_SIM_001": {
        "data_file": "/workspace/projects/workspace/data/simulation/US_SIM_001.json",
        "type": "美股模拟",
        "currency": "USD",
        "initial_capital": 1000000
    },
    "CN_SIM_001": {
        "data_file": "/workspace/projects/workspace/data/simulation/CN_SIM_001.json",
        "type": "A股模拟",
        "currency": "CNY",
        "initial_capital": 5000000
    },
    "HK_SIM_001": {
        "data_file": "/workspace/projects/workspace/data/simulation/HK_SIM_001.json",
        "type": "港股模拟",
        "currency": "HKD",
        "initial_capital": 5000000
    }
}


@dataclass
class PositionData:
    """持仓数据结构"""
    account_id: str
    account_type: str  # REAL or SIM
    total_assets: float
    cash: float
    positions: Dict
    last_update: str
    source_file: str


def get_real_position(account_suffix: str = None) -> Dict:
    """
    获取真实持仓数据 (🔴 REAL)
    
    Args:
        account_suffix: 账户尾号 (6662/9603/0055/0179)，None则返回全部
    
    Returns:
        真实持仓数据字典
    """
    mapping_file = POSITION_SOURCES["REAL"]["mapping_file"]
    
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    real_data = mapping.get("real_positions", {})
    
    if account_suffix:
        # 返回指定账户
        for account in real_data.get("accounts", []):
            if account.get("account_suffix") == account_suffix:
                return {
                    "type": "REAL",
                    "account": account,
                    "holdings": real_data.get("current_holdings", {}),
                    "warning": POSITION_SOURCES["REAL"]["warning"]
                }
        return {"error": f"未找到尾号{account_suffix}的账户"}
    
    # 返回全部真实持仓
    return {
        "type": "REAL",
        "accounts": real_data.get("accounts", []),
        "holdings": real_data.get("current_holdings", {}),
        "total_assets": real_data.get("risk_summary", {}).get("total_assets_all_accounts", 0),
        "warning": POSITION_SOURCES["REAL"]["warning"]
    }


def get_sim_position(account_id: str) -> Dict:
    """
    获取模拟持仓数据 (🔵 SIM)
    
    Args:
        account_id: 模拟账户ID (US_SIM_001/CN_SIM_001/HK_SIM_001)
    
    Returns:
        模拟持仓数据字典
    """
    if account_id not in POSITION_SOURCES:
        return {"error": f"未知的模拟账户: {account_id}"}
    
    source = POSITION_SOURCES[account_id]
    data_file = source["data_file"]
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    return {
        "type": "SIM",
        "account_id": account_id,
        "account_type": source["type"],
        "currency": source["currency"],
        "initial_capital": source["initial_capital"],
        "current_equity": data.get("current_equity", 0),
        "cash": data.get("cash", 0),
        "positions": data.get("positions", {}),
        "trades": data.get("trades", []),
        "note": "模拟账户，不涉及真实资金"
    }


def get_position_summary() -> Dict:
    """
    获取所有持仓汇总 (REAL + SIM)
    
    Returns:
        完整持仓汇总
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "real": get_real_position(),
        "sim": {
            "US_SIM_001": get_sim_position("US_SIM_001"),
            "CN_SIM_001": get_sim_position("CN_SIM_001"),
            "HK_SIM_001": get_sim_position("HK_SIM_001")
        }
    }


def validate_position_type(account_id: str) -> str:
    """
    验证账户类型 (REAL vs SIM)
    
    Args:
        account_id: 账户ID或尾号
    
    Returns:
        "REAL" 或 "SIM" 或 "UNKNOWN"
    """
    # 检查是否是真实账户尾号
    real_suffixes = ["6662", "9603", "0055", "0179"]
    if account_id in real_suffixes:
        return "REAL"
    
    # 检查是否是模拟账户
    if account_id in ["US_SIM_001", "CN_SIM_001", "HK_SIM_001"]:
        return "SIM"
    
    return "UNKNOWN"


def format_position_for_skill(position_data: Dict) -> str:
    """
    格式化持仓数据为SKILL可用格式
    
    Args:
        position_data: 持仓数据字典
    
    Returns:
        Markdown格式字符串
    """
    if position_data.get("type") == "REAL":
        holdings = position_data.get("holdings", {})
        md = "### [🔴 REAL] 真实持仓\n\n"
        md += f"⚠️ {position_data.get('warning', '')}\n\n"
        md += "| 标的 | 代码 | 总数量 | 市值 | 盈亏 |\n"
        md += "|:-----|:-----|:------:|:-----|:-----|\n"
        
        for code, info in holdings.items():
            md += f"| {info.get('name', '-')} | {code} | {info.get('total_shares', '-')} | - | {info.get('status', '-')} |\n"
        
        return md
    
    elif position_data.get("type") == "SIM":
        positions = position_data.get("positions", {})
        md = f"### [🔵 SIM] {position_data.get('account_type', '模拟持仓')}\n\n"
        md += f"本金: {position_data.get('initial_capital', 0):,.0f} {position_data.get('currency', '')}\n\n"
        
        if positions:
            md += "| 标的 | 数量 | 成本 | 现价 | 盈亏 |\n"
            md += "|:-----|:----:|:----:|:----:|:-----|\n"
            for symbol, pos in positions.items():
                pnl = pos.get('unrealized_pnl', 0)
                pnl_pct = pos.get('unrealized_pnl_pct', 0)
                md += f"| {symbol} | {pos.get('quantity', '-')} | {pos.get('cost_basis', '-')} | {pos.get('current_price', '-')} | {pnl:,.0f} ({pnl_pct:+.2f}%) |\n"
        else:
            md += "暂无持仓\n"
        
        return md
    
    return "未知的持仓类型"


# 快速查询函数
def quick_real():
    """快速查询真实持仓"""
    return get_real_position()

def quick_us_sim():
    """快速查询美股模拟持仓"""
    return get_sim_position("US_SIM_001")

def quick_cn_sim():
    """快速查询A股模拟持仓"""
    return get_sim_position("CN_SIM_001")

def quick_hk_sim():
    """快速查询港股模拟持仓"""
    return get_sim_position("HK_SIM_001")


if __name__ == "__main__":
    # 测试查询
    print("=" * 70)
    print("A5L 持仓数据统一接口测试")
    print("=" * 70)
    
    print("\n1. 真实持仓 (全部):")
    real = get_real_position()
    print(f"   类型: {real.get('type')}")
    print(f"   账户数: {len(real.get('accounts', []))}")
    print(f"   持仓数: {len(real.get('holdings', {}))}")
    
    print("\n2. 张晋账户 (6662):")
    zhangjin = get_real_position("6662")
    print(f"   账户: {zhangjin.get('account', {}).get('name')}")
    
    print("\n3. 美股模拟持仓:")
    us_sim = get_sim_position("US_SIM_001")
    print(f"   类型: {us_sim.get('account_type')}")
    print(f"   持仓数: {len(us_sim.get('positions', {}))}")
    
    print("\n4. 持仓汇总:")
    summary = get_position_summary()
    print(f"   时间戳: {summary.get('timestamp')}")
    
    print("\n" + "=" * 70)
    print("✅ 接口测试完成！")
    print("=" * 70)
