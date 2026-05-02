#!/usr/bin/env python3
"""
持仓系统每日更新脚本
从交易日志读取持仓数据，获取最新股价，计算市值和盈亏
"""

import json
import akshare as ak
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 数据文件路径
DATA_DIR = Path("/workspace/projects/workspace/data/portfolio")
REPORT_DIR = Path("/workspace/projects/workspace/data/reports")

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

def get_stock_price(code: str) -> Tuple[float, float]:
    """获取股票最新价格和涨跌幅"""
    try:
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == code]
        if not row.empty:
            price = float(row['最新价'].values[0])
            change_pct = float(row['涨跌幅'].values[0])
            return price, change_pct
        return 0.0, 0.0
    except Exception as e:
        print(f"获取 {code} 价格失败: {e}")
        return 0.0, 0.0

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
        
        price, change_pct = get_stock_price(code)
        
        if is_full:
            # 满仓情况，需要估算股数
            market_value = 0  # 无法计算具体市值
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
    
    for code, pos in stock_positions.items():
        concentration = (pos["market_value"] / total_value * 100) if total_value > 0 else 0
        if concentration > 50:
            alerts.append(f"⚠️ 高风险：{pos['name']}({code}) 集中度 {concentration:.1f}% > 50%")
        elif concentration > 30:
            alerts.append(f"⚡ 警告：{pos['name']}({code}) 集中度 {concentration:.1f}% > 30%")
    
    # 板块集中度检查（简化版 - 基于股票名称关键词）
    shipping_keywords = ["南油", "海运", "航运", "港口"]
    shipping_value = sum(h["market_value"] for h in holdings 
                        if any(kw in h["name"] for kw in shipping_keywords) and not h["is_full"])
    shipping_concentration = (shipping_value / total_value * 100) if total_value > 0 else 0
    
    if shipping_concentration > 60:
        alerts.append(f"⚠️ 高风险：航运板块集中度 {shipping_concentration:.1f}% > 60%")
    elif shipping_concentration > 40:
        alerts.append(f"⚡ 警告：航运板块集中度 {shipping_concentration:.1f}% > 40%")
    
    return alerts

def generate_report(data: Dict, alerts: List[str]) -> str:
    """生成持仓报告"""
    summary = data["summary"]
    holdings = data["holdings"]
    
    lines = [
        "=" * 60,
        "📊 持仓系统每日更新报告",
        f"生成时间: {summary['update_time']}",
        "=" * 60,
        "",
        "【📈 持仓概览】",
        f"├─ 总市值: ¥{summary['total_market_value']:,.2f}",
        f"├─ 总成本: ¥{summary['total_cost']:,.2f}",
        f"├─ 总盈亏: ¥{summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:+.2f}%)",
        "",
        "【📋 持仓明细】",
    ]
    
    for h in holdings:
        emoji = "🔥" if h.get("is_full") else "📌"
        lines.append(f"{emoji} {h['name']} ({h['code']}) - {h['account']}")
        if h.get("is_full"):
            lines.append(f"   状态: 满仓持有 | 现价: ¥{h['current_price']:.2f}")
        else:
            lines.append(f"   股数: {h['shares']:,} | 成本: ¥{h['cost_price']:.2f} | 现价: ¥{h['current_price']:.2f}")
            lines.append(f"   市值: ¥{h['market_value']:,.2f} | 盈亏: ¥{h['pnl']:,.2f} ({h['pnl_pct']:+.2f}%)")
        if h.get("note"):
            lines.append(f"   备注: {h['note']}")
        lines.append("")
    
    if alerts:
        lines.extend([
            "【⚠️ 风险预警】",
        ])
        for alert in alerts:
            lines.append(alert)
        lines.append("")
    else:
        lines.extend([
            "【✅ 风险检查】",
            "所有指标正常，无风险警告",
            "",
        ])
    
    # 按股票聚合统计
    lines.extend([
        "【📊 按股票聚合】",
    ])
    stock_summary = {}
    for h in holdings:
        code = h["code"]
        if code not in stock_summary:
            stock_summary[code] = {"name": h["name"], "total_shares": 0, "total_value": 0}
        if not h.get("is_full"):
            stock_summary[code]["total_shares"] += h["shares"]
            stock_summary[code]["total_value"] += h["market_value"]
    
    for code, s in stock_summary.items():
        lines.append(f"📈 {s['name']} ({code}): {s['total_shares']:,}股 | 市值 ¥{s['total_value']:,.2f}")
    
    lines.extend([
        "",
        "=" * 60,
        "数据来源: 交易日志 (唯一真相源)",
        "数据更新: 2026-04-24 14:31",
        "=" * 60,
    ])
    
    return "\n".join(lines)

def save_data(data: Dict):
    """保存数据到JSON文件"""
    date_str = datetime.now().strftime("%Y%m%d")
    
    # 保存持仓数据
    data_file = DATA_DIR / f"portfolio_{date_str}.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"持仓数据已保存: {data_file}")
    
    # 更新最新持仓文件
    latest_file = DATA_DIR / "portfolio_latest.json"
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"最新持仓已更新: {latest_file}")

def save_report(report: str):
    """保存报告到文件"""
    date_str = datetime.now().strftime("%Y%m%d")
    report_file = REPORT_DIR / f"daily_portfolio_report_{date_str}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"报告已保存: {report_file}")
    
    # 同时保存到内存目录
    memory_file = Path("/workspace/projects/workspace/memory") / f"portfolio_report_{date_str}.md"
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(f"# 持仓报告 {date_str}\n\n```\n{report}\n```")
    print(f"记忆归档: {memory_file}")

def main():
    print("=" * 60)
    print("持仓系统每日更新")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # 1. 计算持仓
    print("📊 正在获取最新股价并计算持仓...")
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
    print("=" * 60)
    print("✅ 持仓系统更新完成")
    print("=" * 60)
    print()
    print(report)
    
    return data, report

if __name__ == "__main__":
    main()
