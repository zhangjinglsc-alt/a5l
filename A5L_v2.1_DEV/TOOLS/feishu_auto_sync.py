#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓数据自动同步脚本
同步内容：
- 持仓明细表（当前状态）
- 历史记录表（每日快照）
- 盈亏汇总表（每日盈亏）
- 交易流水表（如有交易）
"""

import json
import os
import shutil
from datetime import datetime, timedelta

WORKSPACE = "/workspace/projects/workspace"
DATA_DIR = f"{WORKSPACE}/data"
PORTFOLIO_DIR = f"{DATA_DIR}/portfolio"
HISTORY_DIR = f"{DATA_DIR}/holdings_history"
PREVIEW_DIR = f"{DATA_DIR}/feishu_sync_preview"

def ensure_dirs():
    """确保目录存在"""
    for d in [HISTORY_DIR, PREVIEW_DIR]:
        os.makedirs(d, exist_ok=True)

def load_portfolio():
    """加载最新持仓数据"""
    portfolio_file = f"{PORTFOLIO_DIR}/portfolio_latest.json"
    if os.path.exists(portfolio_file):
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_daily_snapshot(data, date_str):
    """保存每日持仓快照"""
    snapshot_file = f"{HISTORY_DIR}/holdings_{date_str}.json"
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return snapshot_file

def generate_pnl_report(data, date_str):
    """生成盈亏报告"""
    holdings = data.get('holdings', [])
    summary = data.get('summary', {})
    
    report = {
        "date": date_str,
        "holdings_count": len(holdings),
        "total_market_value": summary.get('total_market_value', 0),
        "total_cost": summary.get('total_cost', 0),
        "total_pnl": summary.get('total_pnl', 0),
        "total_pnl_pct": summary.get('total_pnl_pct', 0),
        "update_time": summary.get('update_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        "details": []
    }
    
    for h in holdings:
        report["details"].append({
            "name": h.get('name'),
            "code": h.get('code'),
            "account": h.get('account'),
            "shares": h.get('shares'),
            "current_price": h.get('current_price'),
            "market_value": h.get('market_value'),
            "pnl": h.get('pnl'),
            "pnl_pct": h.get('pnl_pct'),
            "change_pct": h.get('change_pct')
        })
    
    return report

def generate_feishu_preview(data, date_str):
    """生成飞书同步预览数据"""
    preview = {
        "sync_date": date_str,
        "sync_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "tables": {
            "持仓明细表": [],
            "历史记录表": [],
            "盈亏汇总表": [],
            "交易流水表": []
        }
    }
    
    holdings = data.get('holdings', [])
    summary = data.get('summary', {})
    
    # 持仓明细表
    for h in holdings:
        preview["tables"]["持仓明细表"].append({
            "日期": date_str,
            "股票名称": h.get('name'),
            "股票代码": h.get('code'),
            "账户": h.get('account'),
            "持仓数量": h.get('shares'),
            "成本价": h.get('cost_price'),
            "当前价": h.get('current_price'),
            "市值": round(h.get('market_value', 0), 2),
            "盈亏金额": round(h.get('pnl', 0), 2) if h.get('pnl') else None,
            "盈亏比例": round(h.get('pnl_pct', 0), 2) if h.get('pnl_pct') else None,
            "当日涨跌": h.get('change_pct'),
            "备注": h.get('note', '')
        })
    
    # 盈亏汇总表
    preview["tables"]["盈亏汇总表"].append({
        "日期": date_str,
        "总持仓数": len(holdings),
        "总市值": round(summary.get('total_market_value', 0), 2),
        "总成本": round(summary.get('total_cost', 0), 2),
        "总盈亏": round(summary.get('total_pnl', 0), 2),
        "总盈亏比例": round(summary.get('total_pnl_pct', 0), 2),
        "更新时间": summary.get('update_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    })
    
    # 历史记录表（当日快照）
    preview["tables"]["历史记录表"].append({
        "日期": date_str,
        "持仓数据": json.dumps(data, ensure_ascii=False),
        "记录类型": "每日收盘快照"
    })
    
    return preview

def sync_to_local(data, date_str):
    """同步到本地存储"""
    # 保存每日快照
    snapshot_path = save_daily_snapshot(data, date_str)
    
    # 生成盈亏报告
    pnl_report = generate_pnl_report(data, date_str)
    pnl_path = f"{HISTORY_DIR}/pnl_report_{date_str}.json"
    with open(pnl_path, 'w', encoding='utf-8') as f:
        json.dump(pnl_report, f, ensure_ascii=False, indent=2)
    
    # 生成飞书同步预览
    preview = generate_feishu_preview(data, date_str)
    preview_path = f"{PREVIEW_DIR}/feishu_sync_preview_{date_str}.json"
    with open(preview_path, 'w', encoding='utf-8') as f:
        json.dump(preview, f, ensure_ascii=False, indent=2)
    
    return {
        "snapshot": snapshot_path,
        "pnl_report": pnl_path,
        "preview": preview_path
    }

def main():
    """主函数"""
    print("=" * 60)
    print("📊 持仓数据自动同步任务")
    print("=" * 60)
    
    # 获取当前日期
    today = datetime.now()
    date_str = today.strftime('%Y%m%d')
    
    print(f"\n📅 当前日期: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📝 记录日期: {date_str}")
    
    # 确保目录存在
    ensure_dirs()
    print(f"\n✅ 目录检查完成")
    
    # 加载持仓数据
    data = load_portfolio()
    if not data:
        print("\n❌ 错误: 未找到持仓数据文件")
        return 1
    
    holdings_count = len(data.get('holdings', []))
    summary = data.get('summary', {})
    
    print(f"\n📈 持仓数据加载成功:")
    print(f"   - 持仓数量: {holdings_count} 只")
    print(f"   - 总市值: ¥{summary.get('total_market_value', 0):,.2f}")
    print(f"   - 总盈亏: ¥{summary.get('total_pnl', 0):,.2f} ({summary.get('total_pnl_pct', 0):.2f}%)")
    
    # 执行本地同步
    print(f"\n💾 正在同步到本地存储...")
    paths = sync_to_local(data, date_str)
    
    print(f"\n✅ 同步完成:")
    print(f"   📁 持仓快照: {paths['snapshot']}")
    print(f"   📁 盈亏报告: {paths['pnl_report']}")
    print(f"   📁 飞书预览: {paths['preview']}")
    
    # 生成摘要
    print(f"\n" + "=" * 60)
    print("📋 同步摘要")
    print("=" * 60)
    print(f"\n日期: {date_str}")
    print(f"状态: {'A股休市' if today.weekday() >= 4 else '正常交易'}")
    print(f"持仓数: {holdings_count}")
    print(f"总市值: ¥{summary.get('total_market_value', 0):,.2f}")
    print(f"当日盈亏: ¥{summary.get('total_pnl', 0):,.2f}")
    
    # 持仓明细
    print(f"\n📊 持仓明细:")
    for h in data.get('holdings', []):
        pnl_str = f"¥{h.get('pnl', 0):,.0f}" if h.get('pnl') is not None else "N/A"
        pnl_pct_str = f"{h.get('pnl_pct', 0):.2f}%" if h.get('pnl_pct') is not None else "N/A"
        print(f"   {h.get('code')} {h.get('name'):8s} | {h.get('account'):8s} | 市值: ¥{h.get('market_value', 0):>10,.0f} | 盈亏: {pnl_str:>12s} ({pnl_pct_str:>8s})")
    
    print(f"\n" + "=" * 60)
    print("✅ 任务完成")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
