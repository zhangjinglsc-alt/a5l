#!/usr/bin/env python3
"""
Sector ETF Monitor - 板块ETF资金流向监控 (带模拟数据备选)
Generates sector ETF flow report for market analysis
"""

import akshare as ak
import json
import os
import argparse
from datetime import datetime, timedelta

def get_mock_sector_data():
    """模拟ETF数据（网络失败时使用）"""
    return [
        # 科技板块
        {'code': '512480', 'name': '半导体ETF', 'price': 2.85, 'change_pct': 1.25, 'change_amount': 0.035, 'volume': 1250000, 'amount': 35620000, 'category': '科技板块'},
        {'code': '159995', 'name': '芯片ETF', 'price': 1.12, 'change_pct': 0.89, 'change_amount': 0.010, 'volume': 980000, 'amount': 10976000, 'category': '科技板块'},
        {'code': '515050', 'name': '5G ETF', 'price': 0.95, 'change_pct': 0.45, 'change_amount': 0.004, 'volume': 560000, 'amount': 5320000, 'category': '科技板块'},
        {'code': '159819', 'name': 'AI ETF', 'price': 1.35, 'change_pct': 1.85, 'change_amount': 0.025, 'volume': 1560000, 'amount': 21060000, 'category': '科技板块'},
        # 新能源板块
        {'code': '515790', 'name': '光伏ETF', 'price': 0.78, 'change_pct': -0.65, 'change_amount': -0.005, 'volume': 890000, 'amount': 6942000, 'category': '新能源板块'},
        {'code': '515030', 'name': '新能源车ETF', 'price': 1.25, 'change_pct': -0.25, 'change_amount': -0.003, 'volume': 720000, 'amount': 9000000, 'category': '新能源板块'},
        {'code': '159840', 'name': '锂电池ETF', 'price': 0.68, 'change_pct': -0.85, 'change_amount': -0.006, 'volume': 650000, 'amount': 4420000, 'category': '新能源板块'},
        # 消费板块
        {'code': '512690', 'name': '白酒ETF', 'price': 2.15, 'change_pct': 0.95, 'change_amount': 0.020, 'volume': 2100000, 'amount': 45150000, 'category': '消费板块'},
        {'code': '512010', 'name': '医药ETF', 'price': 0.42, 'change_pct': -0.45, 'change_amount': -0.002, 'volume': 1800000, 'amount': 7560000, 'category': '消费板块'},
        {'code': '159862', 'name': '食品ETF', 'price': 0.88, 'change_pct': 0.35, 'change_amount': 0.003, 'volume': 420000, 'amount': 3696000, 'category': '消费板块'},
        # 金融板块
        {'code': '512800', 'name': '银行ETF', 'price': 1.05, 'change_pct': 0.15, 'change_amount': 0.002, 'volume': 2500000, 'amount': 26250000, 'category': '金融板块'},
        {'code': '512000', 'name': '券商ETF', 'price': 0.92, 'change_pct': -0.35, 'change_amount': -0.003, 'volume': 1100000, 'amount': 10120000, 'category': '金融板块'},
        {'code': '512200', 'name': '地产ETF', 'price': 0.45, 'change_pct': -1.25, 'change_amount': -0.006, 'volume': 580000, 'amount': 2610000, 'category': '金融板块'},
        # 周期板块
        {'code': '512400', 'name': '有色金属ETF', 'price': 1.18, 'change_pct': 1.45, 'change_amount': 0.017, 'volume': 1450000, 'amount': 17110000, 'category': '周期板块'},
        {'code': '515220', 'name': '煤炭ETF', 'price': 2.05, 'change_pct': 0.65, 'change_amount': 0.013, 'volume': 980000, 'amount': 20090000, 'category': '周期板块'},
        {'code': '515210', 'name': '钢铁ETF', 'price': 1.32, 'change_pct': 0.25, 'change_amount': 0.003, 'volume': 380000, 'amount': 5016000, 'category': '周期板块'},
        # 宽基ETF
        {'code': '510300', 'name': '沪深300ETF', 'price': 3.85, 'change_pct': 0.45, 'change_amount': 0.017, 'volume': 5200000, 'amount': 200200000, 'category': '宽基指数'},
        {'code': '510050', 'name': '上证50ETF', 'price': 2.65, 'change_pct': 0.35, 'change_amount': 0.009, 'volume': 3800000, 'amount': 100700000, 'category': '宽基指数'},
        {'code': '588000', 'name': '科创50ETF', 'price': 0.98, 'change_pct': 1.15, 'change_amount': 0.011, 'volume': 4500000, 'amount': 44100000, 'category': '宽基指数'},
    ]

def get_sector_etf_data():
    """获取板块ETF数据"""
    etf_data = []
    use_mock = False
    
    try:
        # 获取ETF行情数据
        etf_spot = ak.fund_etf_spot_em()
        
        # 主要板块ETF列表
        sector_etfs = {
            '512480': '半导体ETF', '159995': '芯片ETF', '515050': '5G ETF',
            '159819': 'AI ETF', '159858': '科技ETF',
            '515790': '光伏ETF', '515030': '新能源车ETF', '159840': '锂电池ETF',
            '512690': '白酒ETF', '512010': '医药ETF', '159862': '食品ETF',
            '512800': '银行ETF', '512000': '券商ETF', '512200': '地产ETF',
            '512400': '有色金属ETF', '515220': '煤炭ETF', '515210': '钢铁ETF',
            '510300': '沪深300ETF', '510050': '上证50ETF', '588000': '科创50ETF',
        }
        
        for code, name in sector_etfs.items():
            try:
                etf_row = etf_spot[etf_spot['代码'] == code]
                if not etf_row.empty:
                    row = etf_row.iloc[0]
                    etf_data.append({
                        'code': code, 'name': name,
                        'price': row.get('最新价', 'N/A'),
                        'change_pct': row.get('涨跌幅', 'N/A'),
                        'volume': row.get('成交量', 'N/A'),
                        'amount': row.get('成交额', 'N/A'),
                        'category': get_category(name)
                    })
            except:
                continue
                
        if not etf_data:
            use_mock = True
            
    except Exception as e:
        print(f"⚠️ 网络数据获取失败，使用模拟数据: {e}")
        use_mock = True
    
    if use_mock:
        etf_data = get_mock_sector_data()
        print("📊 使用模拟数据生成报告")
    
    return etf_data

def get_category(name):
    """获取板块分类"""
    if any(kw in name for kw in ['半导体', '芯片', '5G', 'AI', '科技']):
        return '科技板块'
    elif any(kw in name for kw in ['光伏', '新能源车', '锂电池', '储能']):
        return '新能源板块'
    elif any(kw in name for kw in ['白酒', '医药', '食品', '家电', '消费']):
        return '消费板块'
    elif any(kw in name for kw in ['银行', '券商', '保险', '地产', '金融']):
        return '金融板块'
    elif any(kw in name for kw in ['有色', '煤炭', '钢铁', '化工']):
        return '周期板块'
    else:
        return '宽基指数'

def save_json_data(etf_data):
    """保存JSON格式数据供其他系统使用"""
    now = datetime.utcnow() + timedelta(hours=8)
    date_str = now.strftime('%Y%m%d')
    
    # 确保目录存在
    os.makedirs('/workspace/projects/workspace/data/macro', exist_ok=True)
    
    output_file = f'/workspace/projects/workspace/data/macro/sector_{date_str}.json'
    
    # 计算板块汇总数据
    categories = {}
    for etf in etf_data:
        cat = etf['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(etf)
    
    sector_summary = {}
    for cat, etfs in categories.items():
        valid_changes = [e['change_pct'] for e in etfs if isinstance(e['change_pct'], (int, float))]
        avg_change = sum(valid_changes) / len(valid_changes) if valid_changes else 0
        sector_summary[cat] = {
            'avg_change_pct': round(avg_change, 2),
            'etf_count': len(etfs),
            'top_performer': max(etfs, key=lambda x: x['change_pct'] if isinstance(x['change_pct'], (int, float)) else 0)['name']
        }
    
    json_data = {
        'date': now.strftime('%Y-%m-%d'),
        'timestamp': now.isoformat(),
        'data_source': 'mock' if not any(isinstance(e.get('volume'), str) for e in etf_data) else 'akshare',
        'etf_count': len(etf_data),
        'sector_summary': sector_summary,
        'etf_details': etf_data
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return output_file

def generate_report(etf_data):
    """生成板块ETF报告"""
    now = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    
    report = f"""
═══════════════════════════════════════════════════════════════
                    📊 板块ETF资金流向监控报告
                              {now}
═══════════════════════════════════════════════════════════════

【市场概况】
监控ETF数量: {len(etf_data)} 只

【板块涨跌幅排行】"""
    
    # 按涨跌幅排序
    sorted_etfs = sorted(etf_data, key=lambda x: x['change_pct'] if isinstance(x['change_pct'], (int, float)) else 0, reverse=True)
    
    # 领涨TOP5
    report += "\n\n📈 领涨TOP5:\n"
    for i, etf in enumerate(sorted_etfs[:5], 1):
        emoji = "🔥" if i <= 3 else "📊"
        report += f"  {emoji} {i}. {etf['name']}({etf['code']})  +{etf['change_pct']}%\n"
    
    # 领跌TOP5
    report += "\n📉 领跌TOP5:\n"
    for i, etf in enumerate(sorted_etfs[-5:], 1):
        report += f"  ❄️  {i}. {etf['name']}({etf['code']})  {etf['change_pct']}%\n"
    
    # 板块汇总
    report += "\n【板块表现】\n"
    categories = {}
    for etf in etf_data:
        cat = etf['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(etf)
    
    for cat, etfs in categories.items():
        valid_changes = [e['change_pct'] for e in etfs if isinstance(e['change_pct'], (int, float))]
        avg_change = sum(valid_changes) / len(valid_changes) if valid_changes else 0
        trend = "📈" if avg_change > 0.5 else "📉" if avg_change < -0.5 else "➡️"
        report += f"  {trend} {cat}: 平均 {avg_change:+.2f}% ({len(etfs)}只)\n"
    
    # 成交活跃度
    report += "\n【成交活跃度TOP5】\n"
    sorted_by_amount = sorted(etf_data, key=lambda x: x['amount'] if isinstance(x['amount'], (int, float)) else 0, reverse=True)
    for i, etf in enumerate(sorted_by_amount[:5], 1):
        amount_val = etf['amount'] if isinstance(etf['amount'], (int, float)) else 0
        amount_str = f"{amount_val/10000:.2f}万" if amount_val else 'N/A'
        report += f"  💰 {i}. {etf['name']}  成交额: {amount_str}\n"
    
    report += """
【轮动策略建议】
  • 关注领涨板块的持续性，判断是否为短期热点
  • 领跌板块若基本面未恶化，可能存在反弹机会
  • 建议结合市场整体趋势和成交量综合判断

═══════════════════════════════════════════════════════════════
数据来源: 东方财富/模拟数据 | 仅供参考，不构成投资建议
═══════════════════════════════════════════════════════════════
"""
    
    return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-only', action='store_true', help='仅输出到文件')
    args = parser.parse_args()
    
    print("正在获取板块ETF数据...")
    etf_data = get_sector_etf_data()
    
    if not etf_data:
        print("❌ 未能获取到ETF数据")
        return
    
    # 生成并打印报告
    report = generate_report(etf_data)
    print(report)
    
    # 保存JSON数据
    json_file = save_json_data(etf_data)
    print(f"\n💾 JSON数据已保存: {json_file}")
    
    # 保存文本报告
    now_str = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y%m%d_%H%M')
    txt_file = f"/workspace/projects/workspace/sector_etf_report_{now_str}.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"💾 文本报告已保存: {txt_file}")

if __name__ == '__main__':
    main()
