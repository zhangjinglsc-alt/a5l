#!/usr/bin/env python3
"""
Tushare历史数据下载器
为ODA系统获取A股历史K线数据
"""
import tushare as ts
import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path

# 设置Token
ts.set_token('fd24d18cd957a2feb18629058771772d8820c244719d67fca7d7d73b')
pro = ts.pro_api()

# 数据保存路径
DATA_PATH = "/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/historical/1d_price_fresh"
Path(DATA_PATH).mkdir(parents=True, exist_ok=True)

def download_daily_data(date_str):
    """下载单日全市场数据"""
    print(f"📊 下载 {date_str} 数据...")
    
    try:
        # 获取日线数据
        df = pro.daily(trade_date=date_str)
        
        if df is not None and not df.empty:
            # 标准化字段名
            column_mapping = {
                'ts_code': 'code',
                'trade_date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'pre_close': 'pre_close',
                'change': 'change',
                'pct_chg': 'pct_chg',
                'vol': 'vol',
                'amount': 'amount'
            }
            df = df.rename(columns=column_mapping)
            
            # 添加vwap字段 (成交额/成交量*10)
            df['vwap'] = df['amount'] / df['vol'] * 10
            
            # 保存为parquet
            filepath = os.path.join(DATA_PATH, f"{date_str}.parquet")
            df.to_parquet(filepath, index=False, compression='snappy')
            
            print(f"  ✅ 成功: {len(df)} 只股票, 保存到 {filepath}")
            return len(df)
        else:
            print(f"  ⚠️ 无数据")
            return 0
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return 0

def get_trade_dates(start_date, end_date):
    """获取交易日历"""
    df = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
    trade_dates = df[df['is_open'] == 1]['cal_date'].tolist()
    return trade_dates

def main():
    """主函数 - 下载最近N个交易日数据"""
    print("=" * 60)
    print("🚀 Tushare历史数据下载器")
    print("=" * 60)
    
    # 下载最近30个交易日
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
    
    print(f"\n📅 时间范围: {start_date} 到 {end_date}")
    
    # 获取交易日历
    trade_dates = get_trade_dates(start_date, end_date)
    print(f"📊 共 {len(trade_dates)} 个交易日")
    
    # 过滤已存在的文件
    dates_to_download = []
    for date in trade_dates:
        filepath = os.path.join(DATA_PATH, f"{date}.parquet")
        if not os.path.exists(filepath):
            dates_to_download.append(date)
    
    print(f"💾 需要下载: {len(dates_to_download)} 天")
    print(f"⏭️ 已存在: {len(trade_dates) - len(dates_to_download)} 天")
    
    if not dates_to_download:
        print("\n✅ 所有数据已是最新！")
        return
    
    # 下载数据
    print("\n" + "=" * 60)
    total_stocks = 0
    for i, date in enumerate(dates_to_download):
        print(f"\n[{i+1}/{len(dates_to_download)}] ", end="")
        count = download_daily_data(date)
        total_stocks += count
    
    print("\n" + "=" * 60)
    print("✅ 下载完成!")
    print(f"📊 总计: {len(dates_to_download)} 天, {total_stocks} 条股票记录")
    print("=" * 60)

if __name__ == "__main__":
    main()
