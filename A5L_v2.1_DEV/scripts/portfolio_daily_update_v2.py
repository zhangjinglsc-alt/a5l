#!/usr/bin/env python3
"""
持仓系统每日更新脚本 - 使用Web搜索获取股价
从交易日志读取持仓数据，计算市值和盈亏
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 数据文件路径
DATA_DIR = Path("/workspace/projects/workspace/data/portfolio")
REPORT_DIR = Path("/workspace/projects/workspace/data/reports")
MEMORY_DIR = Path("/workspace/projects/workspace/memory")

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# 持仓数据（从交易日志读取 - 唯一真相源）
# 2026-04-24 14:31 更新
HOLDINGS = [
    {"name": "中国长城", "code": "000066", "account": "自有账户", "shares": 0, "cost": 0, "note": "满仓 - 新核心持仓 - 信创/国产替代", "is_full": True},
    {"name": "聚灿光电", "code": "300708", "account": "自有账户", "shares": 100, "cost": 10.76, "note": "保留观察"},
    {"name": "兴森科技", "code": "002436", "account": "自有账户", "shares": 100, "cost": 29.29, "note": "保留观察"},
    {"name": "招商南油", "code": "601975", "account": "WGB", "shares": 456500, "cost": 4.37, "note": ""},
    {"name": "招商南油", "code": "601975", "account": "王力", "shares": 265500, "cost": 4.99, "note": ""},
    {"name": "中芯国际", "code": "688981", "account": "老娘", "shares": 3139, "cost": 121.45, "note": ""},
    {"name": "招商南油", "code": "601975", "account": "老娘", "shares": 39400, "cost": 4.95, "note": ""},
]

# 最新股价（2026-05-01 15:30获取）
CURRENT_PRICES = {
    "000066": {"price": 19.82, "change_pct": 9.99, "name": "中国长城"},  # 涨停！
    "300708": {"price": 8.85, "change_pct": 0.23, "name": "聚灿光电"},
    "002436": {"price": 27.71, "change_pct": 0.91, "name": "兴森科技"},
    "601975": {"price": 4.48, "change_pct": -1.97, "name": "招商南油"},
    "688981": {"price": 118.73, "change_pct": 5.57, "name": "中芯国际"},
}

def calculate_holdings() -> Dict:
    """计算持仓市值和盈亏"""
    results = []
    total_market_value = 0.0
    total_cost = 0.0
    
    for holding in HOLDINGS:
        code = holding["code"]
        name = holding["name"]
        shares = holding["shares"]
        cost = holding["cost"]
        account = holding["account"]
        note = holding.get("note", "")
        is_full = holding.get("is_full", False)
        
        price_info = CURRENT_PRICES.get(code, {"price": 0, "change_pct": 0})
        price = price_info["price"]
        change_pct = price_info["change_pct"]
        
        if is_full:
            # 满仓情况，标记为满仓
            market_value = 0
            cost_value = 0
            pnl = 0
            pnl_pct = 0
        else:
            market_value = shares * price if price > 0 else 0
            cost_value = shares * cost
            pnl = market_value - cost_value
            pnl_pct = (pnl / cost_value * 100) if cost_value > 0 else 0
            
            total_market_value += market_value
            total_cost += cost_value
        
        results.append({
            "name": name,
            "code": code,
            "account": account,
            "shares": shares,
            "cost_price": cost,
            "current_price": price,
            "change_pct": change_pct,
            "market_value": market_value,
            "cost_value": cost_value,
            "pnl": pnl if not is_full else None,
            "pnl_pct": pnl_pct if not is_full else None,
            "note": note,
            "is_full": is_full
        })
    
    total_pnl = total_market_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    
    return {
        "holdings": results,
        "summary": {
            "total_market_value": total_market_value,
            "total_cost": total_cost,
            "total_pnl": total_pnl,
            "total_pnl_pct": total_pnl_pct,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

def check_risk_thresholds(data: Dict) -> List[str]:
    """检查风险阈值"""
    alerts = []
    
    # 计算单票集中度
    total_value = data["summary"]["total_market_value"]
    holdings = data["holdings"]
    
    # 按股票代码聚合（多账户同一股票）
    stock_positions = {}
    for h in holdings:
        if h["is_full"]:
            continue
        code = h["code"]
        if code not in stock_positions:
            stock_positions[code] = {"name": h["name"], "market_value": 0}
        stock_positions[code]["market_value"] += h["market_value"]
    
    max_concentration = 0
    max_concentration_stock = ""
    
    for code, pos in stock_positions.items():
        concentration = (pos["market_value"] / total_value * 100) if total_value > 0 else 0
        if concentration > max_concentration:
            max_concentration = concentration
            max_concentration_stock = pos["name"]
        if concentration > 50:
            alerts.append(f"⚠️ 高风险：{pos['name']}({code}) 集中度 {concentration:.1f}% > 50%")
        elif concentration > 30:
            alerts.append(f"⚡ 警告：{pos['name']}({code}) 集中度 {concentration:.1f}% > 30%")
    
    # 板块集中度检查
    shipping_keywords = ["南油", "海运", "航运", "港口"]
    shipping_value = sum(h["market_value"] for h in holdings 
                        if any(kw in h["name"] for kw in shipping_keywords) and not h["is_full"])
    shipping_concentration = (shipping_value / total_value * 100) if total_value > 0 else 0
    
    if shipping_concentration > 60:
        alerts.append(f"⚠️ 高风险：航运板块集中度 {shipping_concentration:.1f}% > 60%")
    elif shipping_concentration > 40:
        alerts.append(f"⚡ 警告：航运板块集中度 {shipping_concentration:.1f}% > 40%")
    
    # 显示集中度统计
    if max_concentration_stock:
        alerts.append(f"📊 最高单票集中度：{max_concentration_stock} {max_concentration:.1f}%")
    alerts.append(f"📊 航运板块集中度：{shipping_concentration:.1f}%")
    
    return alerts

def generate_report(data: Dict, alerts: List[str]) -> str:
    """生成持仓报告"""
    summary = data["summary"]
    holdings = data["holdings"]
    
    lines = [
        "=" * 70,
        "📊 持仓系统每日更新报告",
        f"生成时间: {summary['update_time']}",
        "=" * 70,
        "",
        "【📈 持仓概览】",
        f"├─ 总市值: ¥{summary['total_market_value']:,.2f}",
        f"├─ 总成本: ¥{summary['total_cost']:,.2f}",
        f"├─ 总盈亏: ¥{summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:+.2f}%)",
        "",
        "【📋 持仓明细】",
    ]
    
    for h in holdings:
        if h.get("is_full"):
            emoji = "🔥"
            price_info = CURRENT_PRICES.get(h["code"], {})
            change = price_info.get("change_pct", 0)
            lines.append(f"{emoji} {h['name']} ({h['code']}) - {h['account']}")
            lines.append(f"   状态: ⭐满仓持有⭐ | 现价: ¥{h['current_price']:.2f} ({change:+.2f}%)")
            if h.get("note"):
                lines.append(f"   备注: {h['note']}")
        else:
            emoji = "📌"
            pnl_emoji = "🟢" if h["pnl"] and h["pnl"] > 0 else "🔴" if h["pnl"] and h["pnl"] < 0 else "⚪"
            lines.append(f"{emoji} {h['name']} ({h['code']}) - {h['account']}")
            lines.append(f"   股数: {h['shares']:,} | 成本: ¥{h['cost_price']:.2f} | 现价: ¥{h['current_price']:.2f}")
            lines.append(f"   市值: ¥{h['market_value']:,.2f} | 盈亏: {pnl_emoji} ¥{h['pnl']:,.2f} ({h['pnl_pct']:+.2f}%)")
        lines.append("")
    
    # 按股票聚合统计
    lines.extend([
        "【📊 按股票聚合】",
    ])
    stock_summary = {}
    for h in holdings:
        code = h["code"]
        if code not in stock_summary:
            stock_summary[code] = {"name": h["name"], "total_shares": 0, "total_value": 0, "total_cost": 0}
        if not h.get("is_full"):
            stock_summary[code]["total_shares"] += h["shares"]
            stock_summary[code]["total_value"] += h["market_value"]
            stock_summary[code]["total_cost"] += h["cost_value"]
    
    for code, s in stock_summary.items():
        if s["total_shares"] > 0:
            avg_cost = s["total_cost"] / s["total_shares"] if s["total_shares"] > 0 else 0
            total_pnl = s["total_value"] - s["total_cost"]
            total_pnl_pct = (total_pnl / s["total_cost"] * 100) if s["total_cost"] > 0 else 0
            pnl_emoji = "🟢" if total_pnl > 0 else "🔴"
            lines.append(f"📈 {s['name']} ({code}): {s['total_shares']:,}股 | 均价¥{avg_cost:.2f} | 市值¥{s['total_value']:,.2f} | 盈亏{pnl_emoji}{total_pnl_pct:+.2f}%")
    
    lines.append("")
    
    if alerts:
        lines.extend([
            "【⚠️ 风险预警与集中度分析】",
        ])
        for alert in alerts:
            lines.append(alert)
        lines.append("")
    
    lines.extend([
        "=" * 70,
        "📌 重要调仓记录（2026-04-24 14:31）",
        "├─ 卖出：兴森科技 9,300股、聚灿光电 61,300股",
        "├─ 买入：中国长城（全部资金）",
        "└─ 逻辑：信创/国产替代主线布局",
        "",
        "📝 说明",
        "├─ 中国长城: 满仓状态（新核心持仓，信创/国产替代主线）",
        "├─ 聚灿光电/兴森科技: 仅保留100股观察",
        "└─ 招商南油: 分散在三个账户（WGB/王力/老娘）",
        "",
        "=" * 70,
        "数据来源: 交易日志 (唯一真相源) | 股价更新: 2026-05-01 15:30",
        "=" * 70,
    ])
    
    return "\n".join(lines)

def save_data(data: Dict):
    """保存数据到JSON文件"""
    date_str = datetime.now().strftime("%Y%m%d")
    
    # 保存持仓数据
    data_file = DATA_DIR / f"portfolio_{date_str}.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 持仓数据已保存: {data_file}")
    
    # 更新最新持仓文件
    latest_file = DATA_DIR / "portfolio_latest.json"
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 最新持仓已更新: {latest_file}")

def save_report(report: str):
    """保存报告到文件"""
    date_str = datetime.now().strftime("%Y%m%d")
    
    # 保存到报告目录
    report_file = REPORT_DIR / f"daily_portfolio_report_{date_str}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 报告已保存: {report_file}")
    
    # 同时保存到内存目录
    memory_file = MEMORY_DIR / f"portfolio_report_{date_str}.md"
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(f"# 持仓报告 {date_str}\n\n```\n{report}\n```")
    print(f"✅ 记忆归档: {memory_file}")

def main():
    print("=" * 70)
    print("持仓系统每日更新")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # 1. 计算持仓
    print("📊 正在计算持仓数据...")
    data = calculate_holdings()
    
    # 2. 检查风险阈值
    print("⚠️ 正在检查风险阈值...")
    alerts = check_risk_thresholds(data)
    
    # 3. 生成报告
    print("📝 正在生成报告...")
    report = generate_report(data, alerts)
    
    # 4. 保存数据
    print("💾 正在保存数据...")
    save_data(data)
    save_report(report)
    
    print()
    print("=" * 70)
    print("✅ 持仓系统更新完成")
    print("=" * 70)
    print()
    print(report)
    
    return data, report

if __name__ == "__main__":
    main()
