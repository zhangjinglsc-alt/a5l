#!/usr/bin/env python3
"""
CIO觉醒系统 - 自动化盘前分析脚本
生成时间: 2026-05-10
"""
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# 添加项目路径
sys.path.insert(0, '/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening')

# API配置
BASE_URL = "http://124.222.49.67:3000"
API_KEY = "sk_inst_646653fc7a80b2f8"

def call_api(path, params=None):
    """调用开盘啦API"""
    url = BASE_URL + path
    headers = {"x-api-key": API_KEY}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_market():
    """市场综合分析"""
    results = {}
    
    # 1. 市场情绪
    sentiment = call_api("/api/sentiment")
    if 'limitUp' in sentiment:
        results['sentiment'] = {
            'limit_up': sentiment.get('limitUp', 0),
            'limit_down': sentiment.get('limitDown', 0),
            'up_count': sentiment.get('upCount', 0),
            'down_count': sentiment.get('downCount', 0),
            'seal_rate': sentiment.get('sealRate', 0),
            'intensity': sentiment.get('intensity', 0)
        }
    
    # 2. 连板梯队
    ladder = call_api("/api/ladder", {"limit": 10})
    if 'levels' in ladder:
        results['ladder'] = []
        for level in ladder['levels'][:4]:
            results['ladder'].append({
                'level': level['level'],
                'count': level['count']
            })
    
    # 3. 板块排行
    sectors = call_api("/api/sectors", {"limit": 10})
    if 'sectors' in sectors:
        results['sectors'] = [
            {'name': s['name'], 'count': s['count']}
            for s in sectors['sectors'][:5]
        ]
    
    # 4. 人气榜
    hot = call_api("/api/hot/rank", {"limit": 10})
    if 'fullRank' in hot:
        results['hot_stocks'] = [
            {
                'rank': s['rank'],
                'name': s['name'],
                'code': s['code'],
                'change': float(s['changePct']),
                'score': s['score'],
                'themes': s['themes'][:3]
            }
            for s in hot['fullRank'][:5]
        ]
    
    return results

def ctf_analysis(market_data):
    """CTF催化剂分级分析"""
    sentiment = market_data.get('sentiment', {})
    limit_up = sentiment.get('limit_up', 0)
    up_count = sentiment.get('up_count', 0)
    down_count = sentiment.get('down_count', 1)
    
    # 计算催化级别
    if limit_up > 80 and up_count / down_count > 2:
        tier = "Tier 1-2共振"
        signal = "🔥 强催化"
        action = "积极做多主线"
    elif limit_up > 50:
        tier = "Tier 2-3"
        signal = "🟡 中等催化"
        action = "精选个股"
    else:
        tier = "Tier 3-4"
        signal = "⚪ 弱催化"
        action = "观望为主"
    
    return {
        'tier': tier,
        'signal': signal,
        'action': action,
        'limit_up': limit_up
    }

def generate_signals(market_data, ctf_result):
    """生成交易信号"""
    signals = []
    
    # 根据CTF级别生成信号
    if "Tier 1-2" in ctf_result['tier']:
        # 强催化日 - 关注最强板块
        if market_data.get('hot_stocks'):
            top_stock = market_data['hot_stocks'][0]
            signals.append({
                'type': '关注',
                'stock': top_stock['name'],
                'code': top_stock['code'],
                'reason': f"人气第一 + {', '.join(top_stock['themes'][:2])}",
                'score': top_stock['score']
            })
    
    # 板块轮动信号
    if market_data.get('sectors'):
        top_sector = market_data['sectors'][0]
        signals.append({
            'type': '板块',
            'sector': top_sector['name'],
            'count': top_sector['count'],
            'reason': f"涨停家数第一"
        })
    
    return signals

def generate_report():
    """生成完整分析报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 获取数据
    market_data = analyze_market()
    ctf_result = ctf_analysis(market_data)
    signals = generate_signals(market_data, ctf_result)
    
    # 构建报告
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║     🤖 CIO觉醒系统 - 盘前分析报告                            ║
║     {timestamp}                              ║
╚══════════════════════════════════════════════════════════════╝

📊 【市场情绪】
• 涨停: {market_data.get('sentiment', {}).get('limit_up', 0)}家
• 跌停: {market_data.get('sentiment', {}).get('limit_down', 0)}家  
• 上涨: {market_data.get('sentiment', {}).get('up_count', 0)}家
• 下跌: {market_data.get('sentiment', {}).get('down_count', 0)}家
• 封板率: {market_data.get('sentiment', {}).get('seal_rate', 0):.1f}%

🎯 【CTF催化分析】
• 级别: {ctf_result['tier']}
• 信号: {ctf_result['signal']}
• 建议: {ctf_result['action']}

🔥 【连板梯队】
"""
    
    for level in market_data.get('ladder', []):
        report += f"• {level['level']}板: {level['count']}只\n"
    
    report += "\n📈 【板块强度TOP5】\n"
    for i, s in enumerate(market_data.get('sectors', []), 1):
        report += f"{i}. {s['name']}: {s['count']}板\n"
    
    report += "\n🏆 【人气榜TOP5】\n"
    for s in market_data.get('hot_stocks', []):
        report += f"• {s['name']} ({s['code']}): {s['change']:+.2f}% |  Score:{s['score']}\n"
        report += f"  概念: {', '.join(s['themes'])}\n"
    
    report += "\n💡 【今日交易信号】\n"
    if signals:
        for sig in signals:
            if sig['type'] == '关注':
                report += f"• [{sig['type']}] {sig['stock']} ({sig['code']})\n"
                report += f"  理由: {sig['reason']} | AI评分:{sig['score']}\n"
            else:
                report += f"• [{sig['type']}] {sig.get('sector', 'N/A')}\n"
                report += f"  理由: {sig['reason']}\n"
    else:
        report += "• 今日观望为主，等待更好时机\n"
    
    report += "\n" + "═" * 62 + "\n"
    
    return report, market_data

def save_results(market_data):
    """保存结果到文件"""
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/results/signal_{date_str}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'data': market_data
        }, f, ensure_ascii=False, indent=2)
    
    return filename

if __name__ == "__main__":
    print("🚀 CIO觉醒系统 - 启动盘前分析...")
    
    # 生成报告
    report, market_data = generate_report()
    print(report)
    
    # 保存结果
    saved_file = save_results(market_data)
    print(f"\n💾 报告已保存: {saved_file}")
    
    # 输出摘要（用于消息推送）
    print("\n" + "="*60)
    print("📤 推送摘要:")
    ctf = ctf_analysis(market_data)
    print(f"情绪: {ctf['signal']} | 涨停: {ctf['limit_up']}家")
    if market_data.get('sectors'):
        print(f"主线: {market_data['sectors'][0]['name']}")
    if market_data.get('hot_stocks'):
        print(f"龙头: {market_data['hot_stocks'][0]['name']}")
    print("="*60)
