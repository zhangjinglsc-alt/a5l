#!/usr/bin/env python3
"""
AKShare历史数据下载器
为ODA系统获取A股历史K线数据
"""
import akshare as ak
import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path

# 数据保存路径
DATA_PATH = "/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/historical/1d_price_fresh"
Path(DATA_PATH).mkdir(parents=True, exist_ok=True)

def get_all_stocks():
    """获取所有A股股票列表"""
    print("📋 获取A股股票列表...")
    try:
        # 获取上海和深圳股票
        sh_df = ak.stock_info_sh_name_code()
        sz_df = ak.stock_info_sz_name_code()
        
        stocks = []
        # 上海股票 .SH
        for _, row in sh_df.iterrows():
            code = row['证券代码']
            name = row['证券简称']
            stocks.append({'code': f'{code}.SH', 'name': name})
        
        # 深圳股票 .SZ
        for _, row in sz_df.iterrows():
            code = row['A股代码']
            name = row['A股简称']
            stocks.append({'code': f'{code}.SZ', 'name': name})
        
        print(f"✅ 获取到 {len(stocks)} 只股票")
        return stocks
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return []

def download_stock_history(code, name, start_date, end_date):
    """下载单只股票历史数据"""
    try:
        # 去除后缀，AKShare只需要纯数字代码
        pure_code = code.split('.')[0]
        
        # 判断市场
        if code.endswith('.SH'):
            df = ak.stock_zh_a_hist(symbol=pure_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        else:  # .SZ
            df = ak.stock_zh_a_hist(symbol=pure_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df is not None and not df.empty:
            # 标准化字段名
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'vol',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_chg',
                '涨跌额': 'change',
                '换手率': 'turnover'
            })
            df['code'] = code
            df['name'] = name
            
            # 计算pre_close
            df['pre_close'] = df['close'].shift(1)
            
            return df
        return None
    except Exception as e:
        print(f"  ⚠️ {code} 下载失败: {e}")
        return None

def save_daily_data(date_str, all_stocks_data):
    """保存单日所有股票数据到parquet"""
    if not all_stocks_data:
        print(f"⚠️ {date_str} 无数据")
        return
    
    df = pd.concat(all_stocks_data, ignore_index=True)
    
    # 确保日期格式正确
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y%m%d')
    
    # 保存
    filepath = os.path.join(DATA_PATH, f"{date_str}.parquet")
    df.to_parquet(filepath, index=False, compression='snappy')
    print(f"💾 保存 {date_str}: {len(df)} 条记录")

def download_date_range(start_date, end_date):
    """下载指定日期范围的数据"""
    print(f"\n🚀 开始下载历史数据: {start_date} 到 {end_date}")
    print("=" * 60)
    
    # 获取股票列表
    stocks = get_all_stocks()
    if not stocks:
        print("❌ 无法获取股票列表")
        return
    
    # 生成交易日列表
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # B = Business days
    
    total_days = len(date_range)
    print(f"📅 共 {total_days} 个交易日需要下载\n")
    
    # 限制下载数量，避免超时 (先下载最近30天)
    date_range = date_range[-30:]  # 最近30个交易日
    print(f"⏱️ 本次下载最近30个交易日数据\n")
    
    for i, date in enumerate(date_range):
        date_str = date.strftime('%Y%m%d')
        
        # 检查是否已存在
        filepath = os.path.join(DATA_PATH, f"{date_str}.parquet")
        if os.path.exists(filepath):
            print(f"⏭️  [{i+1}/{len(date_range)}] {date_str} 已存在，跳过")
            continue
        
        print(f"📊 [{i+1}/{len(date_range)}] 下载 {date_str}...")
        
        daily_data = []
        success_count = 0
        
        for stock in stocks[:100]:  # 先下载前100只测试
            df = download_stock_history(stock['code'], stock['name'], date_str, date_str)
            if df is not None and not df.empty:
                daily_data.append(df)
                success_count += 1
        
        if daily_data:
            save_daily_data(date_str, daily_data)
            print(f"  ✅ 成功: {success_count}/{len(stocks[:100])} 只股票\n")
        else:
            print(f"  ⚠️ 无数据\n")
    
    print("=" * 60)
    print("✅ 下载完成!")

def quick_test():
    """快速测试下载最近1天数据"""
    print("🧪 快速测试: 下载最近1个交易日数据")
    
    # 获取最近交易日数据 (使用2025-05-09作为测试，因为akshare有延迟)
    test_date = "20250509"
    
    stocks = get_all_stocks()
    if not stocks:
        return
    
    print(f"\n下载 {test_date} 数据...")
    daily_data = []
    
    for stock in stocks[:50]:  # 先下载50只测试
        df = download_stock_history(stock['code'], stock['name'], test_date, test_date)
        if df is not None and not df.empty:
            daily_data.append(df)
    
    if daily_data:
        save_daily_data(test_date, daily_data)
        print(f"✅ 测试成功! 下载了 {len(daily_data)} 只股票数据")
    else:
        print("⚠️ 测试失败，可能该日期非交易日或数据尚未更新")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        quick_test()
    else:
        # 下载最近60个交易日数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
        download_date_range(start_date, end_date)
