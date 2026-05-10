#!/usr/bin/env python3
"""
A5L历史数据批量下载器
下载15年+历史数据用于回测
"""
import tushare as ts
import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path
import time

# 设置Token
TUSHARE_TOKEN = "fd24d18cd957a2feb18629058771772d8820c244719d67fca7d7d73b"
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# 数据保存路径
DATA_PATH = "/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/historical/1d_price_fresh"
Path(DATA_PATH).mkdir(parents=True, exist_ok=True)

# 下载状态记录
STATUS_FILE = os.path.join(DATA_PATH, "download_status.json")

def load_status():
    """加载下载状态"""
    if os.path.exists(STATUS_FILE):
        import json
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {"completed_dates": [], "last_download": None}

def save_status(status):
    """保存下载状态"""
    import json
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)

def download_daily_data(date_str):
    """下载单日全市场数据"""
    try:
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
            df['vwap'] = df['amount'] / df['vol'] * 10
            
            # 保存
            filepath = os.path.join(DATA_PATH, f"{date_str}.parquet")
            df.to_parquet(filepath, index=False, compression='snappy')
            
            return len(df)
        return 0
    except Exception as e:
        print(f"  ⚠️ {date_str} 错误: {e}")
        return 0

def get_trade_dates(start_date, end_date):
    """获取交易日历"""
    df = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
    return df[df['is_open'] == 1]['cal_date'].tolist()

def batch_download(start_year=2010, end_year=2026):
    """批量下载历史数据"""
    print("=" * 70)
    print("🚀 A5L历史数据批量下载器")
    print(f"📅 下载范围: {start_year}年 - {end_year}年")
    print("=" * 70)
    
    status = load_status()
    total_days = 0
    total_stocks = 0
    
    for year in range(start_year, end_year + 1):
        print(f"\n📊 下载 {year} 年数据...")
        
        start_date = f"{year}0101"
        end_date = f"{year}1231"
        
        trade_dates = get_trade_dates(start_date, end_date)
        year_days = 0
        year_stocks = 0
        
        # 过滤已下载的
        dates_to_download = [d for d in trade_dates if d not in status["completed_dates"]]
        
        if not dates_to_download:
            print(f"  ⏭️ {year}年数据已全部下载")
            continue
        
        print(f"  共 {len(trade_dates)} 个交易日, 需下载 {len(dates_to_download)} 天")
        
        for i, date in enumerate(dates_to_download):
            count = download_daily_data(date)
            if count > 0:
                year_days += 1
                year_stocks += count
                status["completed_dates"].append(date)
                
                # 每10天保存一次状态
                if i % 10 == 0:
                    save_status(status)
                
                # 每50天暂停一下，避免API限制
                if i % 50 == 0 and i > 0:
                    print(f"    ⏸️ 已下载 {i} 天，暂停1秒...")
                    time.sleep(1)
        
        # 年度统计
        print(f"  ✅ {year}年: {year_days} 天, {year_stocks} 条记录")
        total_days += year_days
        total_stocks += year_stocks
        
        # 每年保存一次状态
        save_status(status)
    
    print("\n" + "=" * 70)
    print("✅ 批量下载完成!")
    print(f"📊 总计: {total_days} 天, {total_stocks:,} 条记录")
    print("=" * 70)

if __name__ == "__main__":
    # 默认下载最近5年数据 (2021-2026)
    # 如需15年数据，改为 batch_download(2010, 2026)
    batch_download(2021, 2026)
