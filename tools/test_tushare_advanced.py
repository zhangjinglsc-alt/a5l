#!/usr/bin/env python3
"""
Tushare高级功能测试 - 15000积分会员 + 新闻包年会员
测试全部高阶功能
"""

import os
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from tushare_client import TushareDataSource

def test_advanced_features():
    """测试高级功能"""
    print("="*70)
    print("🚀 Tushare高级功能测试 - 15000积分会员")
    print("="*70)
    
    # 加载配置
    config_path = '/workspace/projects/workspace/config/tushare_config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print(f"\n📊 会员状态:")
    print(f"   积分: {config.get('points', 'N/A')}")
    print(f"   会员类型: {config.get('membership', 'N/A')}")
    print(f"   新闻会员: {config.get('news_membership', 'N/A')}")
    
    ds = TushareDataSource(token=config['token'])
    
    # 测试1: 实时行情 (15000积分)
    print("\n" + "="*70)
    print("📈 测试1: 实时行情数据 (15000积分特权)")
    print("="*70)
    try:
        # 使用quotation_daily获取实时行情
        df = ds.pro.quotation_daily(ts_code='000001.SZ')
        if len(df) > 0:
            print(f"   ✅ 实时行情获取成功")
            print(f"   最新价: {df.iloc[0].get('price', 'N/A')}")
            print(f"   涨跌: {df.iloc[0].get('change', 'N/A')}")
        else:
            print("   ⚠️ 返回空数据")
    except Exception as e:
        print(f"   ⚠️ 实时行情接口: {e}")
    
    # 测试2: 资金流向 (需要积分)
    print("\n" + "="*70)
    print("💸 测试2: 个股资金流向 (高积分特权)")
    print("="*70)
    try:
        today = datetime.now()
        trade_date = (today - timedelta(days=1)).strftime('%Y%m%d')
        
        # 使用moneyflow接口
        df = ds.pro.moneyflow(trade_date=trade_date)
        if len(df) > 0:
            print(f"   ✅ 资金流向获取成功: {len(df)}条")
            print(f"   示例: {df.iloc[0]['ts_code']} - 主力净流入: {df.iloc[0].get('net_mf_amount', 'N/A')}")
        else:
            print("   ⚠️ 返回空数据，尝试其他日期...")
            # 尝试前几天
            for i in range(2, 5):
                trade_date = (today - timedelta(days=i)).strftime('%Y%m%d')
                df = ds.pro.moneyflow(trade_date=trade_date)
                if len(df) > 0:
                    print(f"   ✅ {trade_date} 获取成功: {len(df)}条")
                    break
    except Exception as e:
        print(f"   ❌ 资金流向接口: {e}")
    
    # 测试3: 新闻数据 (包年会员)
    print("\n" + "="*70)
    print("📰 测试3: 财经新闻数据 (包年会员特权)")
    print("="*70)
    
    news_tests = []
    
    # 3.1 重大新闻
    try:
        print("\n   3.1 重大新闻...")
        df = ds.pro.major_news(src='sina', start_date=(datetime.now() - timedelta(days=1)).strftime('%Y%m%d'))
        if len(df) > 0:
            print(f"   ✅ 新浪重大新闻: {len(df)}条")
            print(f"   最新: {df.iloc[0]['title'][:50]}...")
            news_tests.append(("重大新闻", True))
        else:
            print("   ⚠️ 无数据")
            news_tests.append(("重大新闻", False))
    except Exception as e:
        print(f"   ❌ 重大新闻: {e}")
        news_tests.append(("重大新闻", False))
    
    # 3.2 个股新闻
    try:
        print("\n   3.2 个股新闻 (000001.SZ)...")
        df = ds.pro.news(ts_code='000001.SZ')
        if len(df) > 0:
            print(f"   ✅ 个股新闻: {len(df)}条")
            print(f"   最新: {df.iloc[0]['title'][:50]}...")
            news_tests.append(("个股新闻", True))
        else:
            print("   ⚠️ 无数据")
            news_tests.append(("个股新闻", False))
    except Exception as e:
        print(f"   ❌ 个股新闻: {e}")
        news_tests.append(("个股新闻", False))
    
    # 3.3 公告数据
    try:
        print("\n   3.3 公司公告...")
        today = datetime.now()
        df = ds.pro.anns(ts_code='000001.SZ', start_date=(today - timedelta(days=7)).strftime('%Y%m%d'))
        if len(df) > 0:
            print(f"   ✅ 公司公告: {len(df)}条")
            print(f"   最新: {df.iloc[0]['title'][:50]}...")
            news_tests.append(("公司公告", True))
        else:
            print("   ⚠️ 无数据")
            news_tests.append(("公司公告", False))
    except Exception as e:
        print(f"   ❌ 公司公告: {e}")
        news_tests.append(("公司公告", False))
    
    # 测试4: 财务指标 (完整版)
    print("\n" + "="*70)
    print("💰 测试4: 完整财务指标")
    print("="*70)
    try:
        df = ds.pro.fina_indicator(ts_code='000001.SZ')
        if len(df) > 0:
            print(f"   ✅ 财务指标: {len(df)}条")
            print(f"   ROE: {df.iloc[0].get('roe', 'N/A')}")
            print(f"   毛利率: {df.iloc[0].get('grossprofit_margin', 'N/A')}")
            print(f"   净利率: {df.iloc[0].get('netprofit_margin', 'N/A')}")
        else:
            print("   ⚠️ 无数据")
    except Exception as e:
        print(f"   ❌ 财务指标: {e}")
    
    # 测试5: 港股数据
    print("\n" + "="*70)
    print("🇭🇰 测试5: 港股通数据")
    print("="*70)
    try:
        # 港股通每日成交
        today = datetime.now()
        trade_date = (today - timedelta(days=1)).strftime('%Y%m%d')
        df = ds.pro.ggt_daily(trade_date=trade_date)
        if len(df) > 0:
            print(f"   ✅ 港股通数据: {len(df)}条")
            print(f"   买入: {df.iloc[0].get('buy_amount', 'N/A')}")
            print(f"   卖出: {df.iloc[0].get('sell_amount', 'N/A')}")
        else:
            print("   ⚠️ 无数据")
    except Exception as e:
        print(f"   ❌ 港股通: {e}")
    
    # 测试6: 融资融券
    print("\n" + "="*70)
    print("📊 测试6: 融资融券数据")
    print("="*70)
    try:
        today = datetime.now()
        trade_date = (today - timedelta(days=1)).strftime('%Y%m%d')
        df = ds.pro.margin_detail(trade_date=trade_date, ts_code='000001.SZ')
        if len(df) > 0:
            print(f"   ✅ 融资融券: {len(df)}条")
            print(f"   融资余额: {df.iloc[0].get('rzye', 'N/A')}")
            print(f"   融券余额: {df.iloc[0].get('rqye', 'N/A')}")
        else:
            print("   ⚠️ 无数据")
    except Exception as e:
        print(f"   ❌ 融资融券: {e}")
    
    # 测试7: 龙虎榜机构分析
    print("\n" + "="*70)
    print("🐉 测试7: 龙虎榜机构分析")
    print("="*70)
    try:
        today = datetime.now()
        for i in range(1, 5):
            trade_date = (today - timedelta(days=i)).strftime('%Y%m%d')
            
            # 龙虎榜机构明细
            df = ds.pro.top_inst(trade_date=trade_date)
            if len(df) > 0:
                print(f"   ✅ 龙虎榜机构 ({trade_date}): {len(df)}条")
                print(f"   示例: {df.iloc[0]['ts_code']} - 机构: {df.iloc[0].get('exalter', 'N/A')[:20]}")
                break
    except Exception as e:
        print(f"   ❌ 龙虎榜机构: {e}")
    
    # 测试8: 板块数据
    print("\n" + "="*70)
    print("🏭 测试8: 行业板块数据")
    print("="*70)
    try:
        # 行业资金流向
        today = datetime.now()
        trade_date = (today - timedelta(days=1)).strftime('%Y%m%d')
        df = ds.pro.moneyflow_ind_dc(trade_date=trade_date)
        if len(df) > 0:
            print(f"   ✅ 行业资金流向: {len(df)}条")
            print(f"   示例: {df.iloc[0].get('name', 'N/A')} - 净流入: {df.iloc[0].get('net_amount', 'N/A')}")
        else:
            print("   ⚠️ 无数据")
    except Exception as e:
        print(f"   ❌ 行业板块: {e}")
    
    # 汇总
    print("\n" + "="*70)
    print("📊 高级功能测试汇总")
    print("="*70)
    print(f"\n会员特权: 15000积分 + 新闻包年")
    print(f"新闻功能测试:")
    for name, status in news_tests:
        print(f"   {name}: {'✅' if status else '❌'}")
    
    print("\n✅ 高级功能测试完成！")

if __name__ == '__main__':
    test_advanced_features()
