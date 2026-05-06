#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复盘关联分析工具
功能：
1. 分析当日复盘与历史相似记录
2. 提取成功/失败模式
3. 生成模式摘要
"""

import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

WORKSPACE = "/workspace/projects/workspace"
MEMORY_DIR = f"{WORKSPACE}/memory"
REVIEW_LAYERS_DIR = f"{MEMORY_DIR}/review_layers"
REVIEW_LINKED_DIR = f"{MEMORY_DIR}/review_linked"
DATA_DIR = f"{WORKSPACE}/data"

def ensure_dirs():
    """确保目录存在"""
    for d in [REVIEW_LAYERS_DIR, REVIEW_LINKED_DIR]:
        os.makedirs(d, exist_ok=True)

def load_portfolio_data():
    """加载持仓数据"""
    portfolio_file = f"{DATA_DIR}/portfolio/portfolio_latest.json"
    if os.path.exists(portfolio_file):
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_memory_files():
    """加载历史记忆文件"""
    memories = []
    if os.path.exists(MEMORY_DIR):
        for fname in os.listdir(MEMORY_DIR):
            if fname.endswith('.md') and fname.startswith('2026'):
                fpath = os.path.join(MEMORY_DIR, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        memories.append({
                            'file': fname,
                            'date': fname.replace('.md', ''),
                            'content': content
                        })
                except Exception as e:
                    print(f"  读取文件失败: {fname}, 错误: {e}")
    return sorted(memories, key=lambda x: x['date'], reverse=True)

def extract_trading_patterns(content):
    """提取交易模式关键词"""
    patterns = {
        'success_signals': [],
        'failure_signals': [],
        'market_context': [],
        'emotions': []
    }
    
    # 成功信号
    success_keywords = ['涨停', '大涨', '突破', '放量', '金叉', '买入', '加仓', '盈利', '赚钱']
    for kw in success_keywords:
        if kw in content:
            patterns['success_signals'].append(kw)
    
    # 失败信号
    failure_keywords = ['跌停', '大跌', '跌破', '缩量', '死叉', '卖出', '减仓', '止损', '亏损', '割肉']
    for kw in failure_keywords:
        if kw in content:
            patterns['failure_signals'].append(kw)
    
    # 市场环境
    market_keywords = ['牛市', '熊市', '震荡', '反弹', '回调', '突破', '支撑位', '压力位']
    for kw in market_keywords:
        if kw in content:
            patterns['market_context'].append(kw)
    
    return patterns

def analyze_holdings(holdings_data):
    """分析持仓数据"""
    if not holdings_data:
        return None
    
    analysis = {
        'total_positions': len(holdings_data.get('holdings', [])),
        'profitable': 0,
        'losing': 0,
        'neutral': 0,
        'total_pnl': holdings_data.get('summary', {}).get('total_pnl', 0),
        'stocks': []
    }
    
    for h in holdings_data.get('holdings', []):
        pnl = h.get('pnl')
        if pnl is not None:
            if pnl > 0:
                analysis['profitable'] += 1
                status = '盈利'
            elif pnl < 0:
                analysis['losing'] += 1
                status = '亏损'
            else:
                analysis['neutral'] += 1
                status = '持平'
        else:
            status = '满仓标记'
        
        analysis['stocks'].append({
            'code': h.get('code'),
            'name': h.get('name'),
            'account': h.get('account'),
            'pnl': pnl,
            'pnl_pct': h.get('pnl_pct'),
            'status': status
        })
    
    return analysis

def find_similar_patterns(current_analysis, historical_memories):
    """寻找相似历史模式"""
    similar_patterns = []
    
    for mem in historical_memories[:10]:  # 只分析最近10条
        patterns = extract_trading_patterns(mem['content'])
        
        # 简单的相似度判断
        similarity_score = 0
        if patterns['success_signals']:
            similarity_score += len(patterns['success_signals'])
        if patterns['failure_signals']:
            similarity_score += len(patterns['failure_signals'])
        
        if similarity_score > 0:
            similar_patterns.append({
                'date': mem['date'],
                'similarity_score': similarity_score,
                'patterns': patterns,
                'preview': mem['content'][:200] + '...' if len(mem['content']) > 200 else mem['content']
            })
    
    return sorted(similar_patterns, key=lambda x: x['similarity_score'], reverse=True)[:5]

def generate_mode_summary(analysis, similar_patterns, date_str):
    """生成模式摘要"""
    summary = {
        'analysis_date': date_str,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'current_state': analysis,
        'historical_patterns': similar_patterns,
        'insights': [],
        'recommendations': []
    }
    
    # 生成洞察
    if analysis:
        if analysis['total_pnl'] > 0:
            summary['insights'].append(f"当前整体盈利 ¥{analysis['total_pnl']:,.2f}，持仓状态良好")
        elif analysis['total_pnl'] < 0:
            summary['insights'].append(f"当前整体亏损 ¥{abs(analysis['total_pnl']):,.2f}，需要关注风险控制")
        
        if analysis['profitable'] > analysis['losing']:
            summary['insights'].append(f"盈利个股({analysis['profitable']}只)多于亏损({analysis['losing']}只)，策略有效")
        elif analysis['losing'] > analysis['profitable']:
            summary['insights'].append(f"亏损个股({analysis['losing']}只)多于盈利({analysis['profitable']}只)，需审视策略")
    
    # 生成建议
    if similar_patterns:
        top_pattern = similar_patterns[0]
        summary['recommendations'].append(f"参考历史模式 [{top_pattern['date']}]，关注{'、'.join(top_pattern['patterns']['market_context'][:3])}")
    
    summary['recommendations'].append("假期期间关注美股走势，为节后开盘做准备")
    summary['recommendations'].append("5月8日兴森科技业绩说明会，提前准备关注问题")
    
    return summary

def save_layered_review(analysis, summary, date_str):
    """保存分层复盘数据"""
    # 原始层
    raw_file = f"{REVIEW_LAYERS_DIR}/raw_{date_str}.json"
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': date_str,
            'type': 'raw_data',
            'holdings': analysis
        }, f, ensure_ascii=False, indent=2)
    
    # 特征层
    feature_file = f"{REVIEW_LAYERS_DIR}/feature_{date_str}.json"
    features = {
        'date': date_str,
        'type': 'feature_extraction',
        'key_metrics': {
            'total_positions': analysis.get('total_positions', 0),
            'profitable_count': analysis.get('profitable', 0),
            'losing_count': analysis.get('losing', 0),
            'total_pnl': analysis.get('total_pnl', 0)
        },
        'stock_features': [
            {
                'code': s['code'],
                'name': s['name'],
                'status': s['status'],
                'pnl_pct': s.get('pnl_pct')
            }
            for s in analysis.get('stocks', [])
        ]
    }
    with open(feature_file, 'w', encoding='utf-8') as f:
        json.dump(features, f, ensure_ascii=False, indent=2)
    
    # 关联层
    linked_file = f"{REVIEW_LINKED_DIR}/linked_{date_str}.json"
    with open(linked_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    return {
        'raw': raw_file,
        'feature': feature_file,
        'linked': linked_file
    }

def main():
    """主函数"""
    print("=" * 60)
    print("🔄 复盘关联分析任务")
    print("=" * 60)
    
    today = datetime.now()
    date_str = today.strftime('%Y%m%d')
    
    print(f"\n📅 分析日期: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📝 记录日期: {date_str}")
    
    # 确保目录
    ensure_dirs()
    print(f"\n✅ 目录检查完成")
    
    # 加载数据
    print(f"\n📊 加载持仓数据...")
    holdings_data = load_portfolio_data()
    if holdings_data:
        print(f"   - 持仓数量: {len(holdings_data.get('holdings', []))}")
    
    print(f"\n📚 加载历史记忆...")
    memories = load_memory_files()
    print(f"   - 历史记录: {len(memories)} 条")
    
    # 分析持仓
    print(f"\n🔍 分析持仓数据...")
    analysis = analyze_holdings(holdings_data)
    if analysis:
        print(f"   - 总持仓: {analysis['total_positions']} 只")
        print(f"   - 盈利: {analysis['profitable']} 只")
        print(f"   - 亏损: {analysis['losing']} 只")
        print(f"   - 总盈亏: ¥{analysis['total_pnl']:,.2f}")
    
    # 寻找相似模式
    print(f"\n🔗 关联历史模式...")
    similar_patterns = find_similar_patterns(analysis, memories)
    print(f"   - 找到 {len(similar_patterns)} 个相似模式")
    for i, p in enumerate(similar_patterns[:3], 1):
        print(f"   {i}. [{p['date']}] 相似度: {p['similarity_score']}")
    
    # 生成摘要
    print(f"\n📝 生成模式摘要...")
    summary = generate_mode_summary(analysis, similar_patterns, date_str)
    
    # 保存分层数据
    print(f"\n💾 保存分层复盘数据...")
    paths = save_layered_review(analysis, summary, date_str)
    
    print(f"\n✅ 文件保存完成:")
    print(f"   📁 原始层: {paths['raw']}")
    print(f"   📁 特征层: {paths['feature']}")
    print(f"   📁 关联层: {paths['linked']}")
    
    # 输出摘要
    print(f"\n" + "=" * 60)
    print("📋 模式摘要")
    print("=" * 60)
    
    for insight in summary['insights']:
        print(f"\n💡 {insight}")
    
    print(f"\n📌 建议:")
    for i, rec in enumerate(summary['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n" + "=" * 60)
    print("✅ 任务完成")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
