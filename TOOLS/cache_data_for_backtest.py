#!/usr/bin/env python3
"""
数据预缓存脚本 - 为三版本回测准备数据
避免明天Tushare API限流
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("❌ Tushare未安装")
    exit(1)

# 测试股票池
stocks = [
    '000001.SZ', '000858.SZ', '600519.SH', '600036.SH', '000066.SZ',
    '000333.SZ', '002594.SZ', '601318.SH', '600900.SH', '300750.SZ'
]

start_date = '20200101'
end_date = '20241231'

print("="*60)
print("📦 数据预缓存开始")
print(f"📅 周期: {start_date} ~ {end_date}")
print(f"📊 股票: {len(stocks)}只")
print("="*60)

pro = ts.pro_api()
cache_dir = Path('/tmp/strategy_data_cache')
cache_dir.mkdir(parents=True, exist_ok=True)

success_count = 0
fail_count = 0

for i, code in enumerate(stocks, 1):
    cache_file = cache_dir / f"{code}_{start_date}_{end_date}.csv"
    
    if cache_file.exists():
        print(f"[{i}/{len(stocks)}] {code} - 已缓存 ✓")
        success_count += 1
        continue
    
    try:
        # 添加延迟避免限流
        time.sleep(0.5)
        
        df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
        
        if not df.empty:
            df = df.sort_values('trade_date')
            df.set_index('trade_date', inplace=True)
            df.index = pd.to_datetime(df.index)
            
            # 预计算指标
            for p in [5, 10, 12, 15, 20, 60]:
                df[f'ma{p}'] = df['close'].rolling(window=p).mean()
            
            df['change_pct'] = df['close'].pct_change() * 100
            df['high_10'] = df['high'].rolling(window=10).max()
            df['high_20'] = df['high'].rolling(window=20).max()
            df['high_60'] = df['high'].rolling(window=60).max()
            df['vol_ma20'] = df['vol'].rolling(window=20).mean()
            df['volume_ratio'] = df['vol'] / df['vol_ma20']
            
            # 趋势评分
            df['trend_score'] = (
                (df['close'] > df['ma5']).astype(int) +
                (df['close'] > df['ma10']).astype(int) +
                (df['close'] > df['ma20']).astype(int) +
                (df['close'] > df['ma60']).astype(int)
            )
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
            
            df.to_csv(cache_file)
            print(f"[{i}/{len(stocks)}] {code} - 缓存成功 ✓ ({len(df)}条)")
            success_count += 1
        else:
            print(f"[{i}/{len(stocks)}] {code} - 无数据 ✗")
            fail_count += 1
            
    except Exception as e:
        print(f"[{i}/{len(stocks)}] {code} - 失败: {str(e)[:50]}")
        fail_count += 1

print(f"\n{'='*60}")
print(f"📊 缓存完成")
print(f"成功: {success_count}只 | 失败: {fail_count}只")
print(f"缓存路径: {cache_dir}")
print(f"{'='*60}")
