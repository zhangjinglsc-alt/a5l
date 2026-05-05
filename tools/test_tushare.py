#!/usr/bin/env python3
"""
Tushare自动测试脚本
收到Token后立即执行全面测试
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

# 添加路径
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

# 测试结果存储
TEST_RESULTS = {
    'test_time': datetime.now().isoformat(),
    'token_configured': False,
    'tests_passed': 0,
    'tests_failed': 0,
    'details': []
}

def log_test(test_name: str, status: bool, message: str = ""):
    """记录测试结果"""
    result = {
        'test': test_name,
        'status': '✅ PASS' if status else '❌ FAIL',
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    TEST_RESULTS['details'].append(result)
    
    if status:
        TEST_RESULTS['tests_passed'] += 1
        print(f"✅ {test_name}: PASS")
    else:
        TEST_RESULTS['tests_failed'] += 1
        print(f"❌ {test_name}: FAIL - {message}")
    
    return status

def test_token_configuration():
    """测试Token配置"""
    print("\n" + "="*60)
    print("🔑 测试1: Token配置检查")
    print("="*60)
    
    config_path = '/workspace/projects/workspace/config/tushare_config.json'
    
    if not os.path.exists(config_path):
        log_test("Token配置文件", False, f"配置文件不存在: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        token = config.get('token')
        if not token:
            log_test("Token有效性", False, "Token为空")
            return False
        
        print(f"   Token前10位: {token[:10]}...")
        TEST_RESULTS['token_configured'] = True
        log_test("Token配置", True, f"Token已配置，长度: {len(token)}")
        return True
        
    except Exception as e:
        log_test("Token配置", False, f"读取配置失败: {e}")
        return False

def test_basic_connection():
    """测试基础连接"""
    print("\n" + "="*60)
    print("🔗 测试2: 基础连接测试")
    print("="*60)
    
    try:
        from tushare_client import TushareDataSource
        
        config_path = '/workspace/projects/workspace/config/tushare_config.json'
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        ds = TushareDataSource(token=config['token'])
        log_test("基础连接", True, "Tushare API连接成功")
        return ds
        
    except Exception as e:
        log_test("基础连接", False, f"连接失败: {e}")
        return None

def test_stock_list(ds):
    """测试股票列表获取"""
    print("\n" + "="*60)
    print("📈 测试3: A股股票列表")
    print("="*60)
    
    try:
        stocks = ds.get_stock_basic()
        
        if len(stocks) == 0:
            log_test("股票列表", False, "返回空数据")
            return False
        
        print(f"   获取股票数量: {len(stocks)}")
        print(f"   示例股票: {stocks.iloc[0]['ts_code']} - {stocks.iloc[0]['name']}")
        
        # 检查关键字段
        required_cols = ['ts_code', 'symbol', 'name', 'industry', 'list_date']
        missing_cols = [col for col in required_cols if col not in stocks.columns]
        
        if missing_cols:
            log_test("股票列表字段", False, f"缺少字段: {missing_cols}")
            return False
        
        log_test("股票列表", True, f"成功获取{len(stocks)}只股票")
        return True
        
    except Exception as e:
        log_test("股票列表", False, f"获取失败: {e}")
        return False

def test_daily_data(ds):
    """测试日线数据"""
    print("\n" + "="*60)
    print("📊 测试4: 日线行情数据")
    print("="*60)
    
    try:
        today = datetime.now()
        end = today.strftime('%Y%m%d')
        start = (today - timedelta(days=10)).strftime('%Y%m%d')
        
        # 测试平安银行
        df = ds.get_daily('000001.SZ', start_date=start, end_date=end)
        
        if len(df) == 0:
            log_test("日线数据", False, "返回空数据")
            return False
        
        print(f"   获取数据条数: {len(df)}")
        print(f"   最新收盘价: {df.iloc[0]['close']}")
        print(f"   数据日期范围: {df.iloc[-1]['trade_date']} ~ {df.iloc[0]['trade_date']}")
        
        # 检查关键字段
        required_cols = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            log_test("日线数据字段", False, f"缺少字段: {missing_cols}")
            return False
        
        log_test("日线数据", True, f"成功获取{len(df)}条数据")
        return True
        
    except Exception as e:
        log_test("日线数据", False, f"获取失败: {e}")
        return False

def test_financial_data(ds):
    """测试财务数据"""
    print("\n" + "="*60)
    print("💰 测试5: 财务数据")
    print("="*60)
    
    try:
        # 获取利润表
        today = datetime.now()
        end = today.strftime('%Y%m%d')
        start = (today - timedelta(days=365)).strftime('%Y%m%d')
        
        income = ds.get_income('000001.SZ', start_date=start, end_date=end)
        
        if len(income) == 0:
            log_test("财务数据(利润表)", False, "返回空数据（可能需要积分）")
        else:
            print(f"   获取利润表条数: {len(income)}")
            log_test("财务数据(利润表)", True, f"成功获取{len(income)}条")
        
        # 获取资产负债表
        balance = ds.get_balance_sheet('000001.SZ', start_date=start, end_date=end)
        
        if len(balance) == 0:
            log_test("财务数据(资产负债表)", False, "返回空数据（可能需要积分）")
        else:
            print(f"   获取资产负债表条数: {len(balance)}")
            log_test("财务数据(资产负债表)", True, f"成功获取{len(balance)}条")
        
        return True
        
    except Exception as e:
        log_test("财务数据", False, f"获取失败: {e}")
        return False

def test_top_list(ds):
    """测试龙虎榜数据"""
    print("\n" + "="*60)
    print("🐉 测试6: 龙虎榜数据 (超短策略关键)")
    print("="*60)
    
    try:
        today = datetime.now()
        # 获取最近交易日
        for i in range(1, 10):
            trade_date = (today - timedelta(days=i)).strftime('%Y%m%d')
            top = ds.get_top_list(trade_date)
            if len(top) > 0:
                print(f"   获取日期: {trade_date}")
                print(f"   龙虎榜条目: {len(top)}")
                print(f"   示例: {top.iloc[0]['ts_code']} - {top.iloc[0]['name']}")
                log_test("龙虎榜数据", True, f"成功获取{len(top)}条")
                return True
        
        log_test("龙虎榜数据", False, "最近10天无数据（可能需要积分或数据延迟）")
        return False
        
    except Exception as e:
        log_test("龙虎榜数据", False, f"获取失败: {e}")
        return False

def test_money_flow(ds):
    """测试资金流向数据"""
    print("\n" + "="*60)
    print("💸 测试7: 资金流向数据")
    print("="*60)
    
    try:
        today = datetime.now()
        trade_date = (today - timedelta(days=1)).strftime('%Y%m%d')
        
        flow = ds.get_money_flow(trade_date)
        
        if len(flow) == 0:
            log_test("资金流向", False, "返回空数据（可能需要积分）")
            return False
        
        print(f"   获取日期: {trade_date}")
        print(f"   资金流向条目: {len(flow)}")
        print(f"   示例: {flow.iloc[0]['ts_code']} - 主力净流入: {flow.iloc[0].get('net_mf_amount', 'N/A')}")
        
        log_test("资金流向", True, f"成功获取{len(flow)}条")
        return True
        
    except Exception as e:
        log_test("资金流向", False, f"获取失败: {e}")
        return False

def test_north_money(ds):
    """测试北向资金"""
    print("\n" + "="*60)
    print("🌏 测试8: 北向资金流向")
    print("="*60)
    
    try:
        today = datetime.now()
        end = today.strftime('%Y%m%d')
        start = (today - timedelta(days=10)).strftime('%Y%m%d')
        
        north = ds.get_north_money(start_date=start, end_date=end)
        
        if len(north) == 0:
            log_test("北向资金", False, "返回空数据（可能需要积分）")
            return False
        
        print(f"   获取数据条数: {len(north)}")
        print(f"   最新北向资金: {north.iloc[0].get('north_money', 'N/A')}")
        
        log_test("北向资金", True, f"成功获取{len(north)}条")
        return True
        
    except Exception as e:
        log_test("北向资金", False, f"获取失败: {e}")
        return False

def test_news_data(ds):
    """测试新闻数据 (包年会员功能)"""
    print("\n" + "="*60)
    print("📰 测试9: 新闻数据 (包年会员功能)")
    print("="*60)
    
    try:
        # Tushare新闻数据需要特定接口
        # 这里使用pro.major_news()或pro.news()
        news = ds.pro.major_news(src='sina', start_date=(datetime.now() - timedelta(days=1)).strftime('%Y%m%d'))
        
        if len(news) == 0:
            log_test("新闻数据", False, "返回空数据（可能会员等级不足）")
            return False
        
        print(f"   获取新闻条数: {len(news)}")
        print(f"   最新新闻: {news.iloc[0]['title'][:50]}...")
        
        log_test("新闻数据", True, f"成功获取{len(news)}条")
        return True
        
    except Exception as e:
        if "权限" in str(e) or "积分" in str(e):
            log_test("新闻数据", False, f"会员权限不足: {e}")
        else:
            log_test("新闻数据", False, f"获取失败: {e}")
        return False

def generate_report():
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 测试报告生成")
    print("="*60)
    
    total = TEST_RESULTS['tests_passed'] + TEST_RESULTS['tests_failed']
    pass_rate = (TEST_RESULTS['tests_passed'] / total * 100) if total > 0 else 0
    
    print(f"\n测试时间: {TEST_RESULTS['test_time']}")
    print(f"Token配置: {'✅ 已配置' if TEST_RESULTS['token_configured'] else '❌ 未配置'}")
    print(f"总测试数: {total}")
    print(f"通过: {TEST_RESULTS['tests_passed']}")
    print(f"失败: {TEST_RESULTS['tests_failed']}")
    print(f"通过率: {pass_rate:.1f}%")
    
    # 保存报告
    report_path = '/workspace/projects/workspace/reports/tushare_test_report.json'
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(TEST_RESULTS, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 测试报告已保存: {report_path}")
    
    # 生成Markdown报告
    md_report = f"""# Tushare自动测试报告

**测试时间**: {TEST_RESULTS['test_time']}
**Token配置**: {'✅ 已配置' if TEST_RESULTS['token_configured'] else '❌ 未配置'}
**总测试数**: {total}
**通过**: {TEST_RESULTS['tests_passed']}
**失败**: {TEST_RESULTS['tests_failed']}
**通过率**: {pass_rate:.1f}%

## 详细测试结果

| 测试项 | 状态 | 说明 |
|--------|------|------|
"""
    
    for detail in TEST_RESULTS['details']:
        md_report += f"| {detail['test']} | {detail['status']} | {detail['message']} |\n"
    
    md_report += f"""
## 结论

"""
    
    if pass_rate >= 80:
        md_report += "✅ **测试通过**: Tushare接口运行正常，可以投入生产使用。\n"
    elif pass_rate >= 50:
        md_report += "⚠️ **部分通过**: 部分接口需要积分或更高会员等级，基础功能可用。\n"
    else:
        md_report += "❌ **测试失败**: 请检查Token配置和会员权限。\n"
    
    md_path = '/workspace/projects/workspace/reports/tushare_test_report.md'
    with open(md_path, 'w') as f:
        f.write(md_report)
    
    print(f"✅ Markdown报告已保存: {md_path}")
    
    return pass_rate

def main():
    """主函数"""
    print("="*60)
    print("🚀 Tushare自动测试脚本启动")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 测试Token配置
    if not test_token_configuration():
        print("\n❌ Token未配置，测试终止")
        print("请运行: python3 tools/tushare_client.py setup")
        generate_report()
        return
    
    # 2. 测试基础连接
    ds = test_basic_connection()
    if not ds:
        print("\n❌ 基础连接失败，测试终止")
        generate_report()
        return
    
    # 3. 测试各项功能
    test_stock_list(ds)
    test_daily_data(ds)
    test_financial_data(ds)
    test_top_list(ds)
    test_money_flow(ds)
    test_north_money(ds)
    test_news_data(ds)
    
    # 4. 生成报告
    pass_rate = generate_report()
    
    print("\n" + "="*60)
    if pass_rate >= 80:
        print("🎉 测试通过！Tushare已准备就绪")
    elif pass_rate >= 50:
        print("⚠️ 部分通过，基础功能可用")
    else:
        print("❌ 测试未通过，请检查配置")
    print("="*60)

if __name__ == '__main__':
    main()
