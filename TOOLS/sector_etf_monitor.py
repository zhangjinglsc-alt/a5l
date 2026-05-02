#!/usr/bin/env python3
"""
Sector ETF Monitor - 板块ETF资金流向监控
Generates sector ETF flow report for market analysis
"""

import akshare as ak
import json
from datetime import datetime

def get_sector_etf_data():
    """获取板块ETF数据"""
    # 使用akshare获取ETF数据
    etf_data = []
    
    try:
        # 获取ETF行情数据
        etf_spot = ak.fund_etf_spot_em()
        
        # 主要板块ETF列表（代码和名称映射）
        sector_etfs = {
            # 科技板块
            '512480': '半导体ETF',
            '159995': '芯片ETF',
            '515050': '5G ETF',
            '159819': 'AI ETF',
            '159858': '科技ETF',
            # 新能源板块
            '515790': '光伏ETF',
            '515030': '新能源车ETF',
            '159840': '锂电池ETF',
            '159866': '储能ETF',
            # 消费板块
            '512690': '白酒ETF',
            '512010': '医药ETF',
            '159862': '食品ETF',
            '159996': '家电ETF',
            # 金融板块
            '512800': '银行ETF',
            '512000': '券商ETF',
            '512300': '保险ETF',
            '512200': '地产ETF',
            # 周期板块
            '512400': '有色金属ETF',
            '515220': '煤炭ETF',
            '515210': '钢铁ETF',
            '516690': '化工ETF',
            # 宽基ETF
            '510300': '沪深300ETF',
            '510050': '上证50ETF',
            '510500': '中证500ETF',
            '159915': '创业板ETF',
            '588000': '科创50ETF',
        }
        
        for code, name in sector_etfs.items():
            try:
                # 查找对应的ETF数据
                etf_row = etf_spot[etf_spot['代码'] == code]
                if not etf_row.empty:
                    row = etf_row.iloc[0]
                    etf_data.append({
                        'code': code,
                        'name': name,
                        'price': row.get('最新价', 'N/A'),
                        'change_pct': row.get('涨跌幅', 'N/A'),
                        'change_amount': row.get('涨跌额', 'N/A'),
                        'volume': row.get('成交量', 'N/A'),
                        'amount': row.get('成交额', 'N/A'),
                        'category': get_category(name)
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"获取ETF数据失败: {e}")
    
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

def generate_report(etf_data):
    """生成板块ETF报告"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    report = f"""
═══════════════════════════════════════════════════════════════
                    📊 板块ETF资金流向监控报告
                              {now}
═══════════════════════════════════════════════════════════════

【市场概况】
监控ETF数量: {len(etf_data)} 只

【板块涨跌幅排行】"""
    
    # 按涨跌幅排序
    try:
        sorted_etfs = sorted([e for e in etf_data if e['change_pct'] != 'N/A'], 
                             key=lambda x: float(x['change_pct']) if x['change_pct'] != 'N/A' else 0, 
                             reverse=True)
        
        # 领涨TOP5
        report += "\n\n📈 领涨TOP5:\n"
        for i, etf in enumerate(sorted_etfs[:5], 1):
            emoji = "🔥" if i <= 3 else "📊"
            report += f"  {emoji} {i}. {etf['name']}({etf['code']})  +{etf['change_pct']}%\n"
        
        # 领跌TOP5
        report += "\n📉 领跌TOP5:\n"
        for i, etf in enumerate(sorted_etfs[-5:], 1):
            report += f"  ❄️  {i}. {etf['name']}({etf['code']})  {etf['change_pct']}%\n"
        
    except Exception as e:
        report += "\n  数据获取异常，暂无法显示排行\n"
    
    # 板块汇总
    report += "\n【板块表现】\n"
    categories = {}
    for etf in etf_data:
        cat = etf['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(etf)
    
    for cat, etfs in categories.items():
        try:
            valid_changes = [float(e['change_pct']) for e in etfs if e['change_pct'] != 'N/A']
            avg_change = sum(valid_changes) / len(valid_changes) if valid_changes else 0
            trend = "📈" if avg_change > 0.5 else "📉" if avg_change < -0.5 else "➡️"
            report += f"  {trend} {cat}: 平均 {avg_change:+.2f}% ({len(etfs)}只)\n"
        except:
            report += f"  ➡️ {cat}: 数据异常\n"
    
    # 成交活跃度
    report += "\n【成交活跃度TOP5】\n"
    try:
        sorted_by_amount = sorted([e for e in etf_data if e['amount'] != 'N/A'],
                                  key=lambda x: float(x['amount']) if x['amount'] != 'N/A' else 0,
                                  reverse=True)
        for i, etf in enumerate(sorted_by_amount[:5], 1):
            amount_str = f"{float(etf['amount'])/10000:.2f}万" if etf['amount'] != 'N/A' else 'N/A'
            report += f"  💰 {i}. {etf['name']}  成交额: {amount_str}\n"
    except:
        report += "  数据获取异常\n"
    
    report += """
【轮动策略建议】
  • 关注领涨板块的持续性，判断是否为短期热点
  • 领跌板块若基本面未恶化，可能存在反弹机会
  • 建议结合市场整体趋势和成交量综合判断

═══════════════════════════════════════════════════════════════
数据来源: 东方财富 | 仅供参考，不构成投资建议
═══════════════════════════════════════════════════════════════
"""
    
    return report

def main():
    """主函数"""
    print("正在获取板块ETF数据...")
    etf_data = get_sector_etf_data()
    
    if not etf_data:
        print("❌ 未能获取到ETF数据，请检查网络连接或数据源")
        return
    
    report = generate_report(etf_data)
    print(report)
    
    # 保存到文件
    output_file = f"/workspace/projects/workspace/sector_etf_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 报告已保存至: {output_file}")

if __name__ == '__main__':
    main()
