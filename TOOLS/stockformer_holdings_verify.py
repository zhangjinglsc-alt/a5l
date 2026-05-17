#!/usr/bin/env python3
"""
Stockformer持仓验证工具
针对现有持仓股票做预测效果验证
"""
import sys
sys.path.insert(0, '/workspace/projects/workspace/extern/Multitask-Stockformer')
import pandas as pd
import numpy as np
import akshare as ak

# 现有持仓列表
HOLDINGS = [
    {"name": "中国长城", "code": "000066"},
    {"name": "盈峰环境", "code": "000967"},
    {"name": "招商南油", "code": "601975"},
    {"name": "中芯国际", "code": "688981"},
    {"name": "兴森科技", "code": "002436"},
    {"name": "聚灿光电", "code": "300708"},
]

def get_stock_history(code, start_date="2022-01-01", end_date="2026-05-17"):
    """
    获取A股股票历史行情数据
    """
    try:
        # 后复权日线数据
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="hfq")
        df['code'] = code
        df['datetime'] = pd.to_datetime(df['日期'])
        df = df.rename(columns={
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount',
            '涨跌幅': 'pct_chg'
        })
        return df[['datetime', 'code', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']]
    except Exception as e:
        print(f"获取{code}数据失败: {e}")
        return None

def build_alpha360_factors(df):
    """
    构建精简版Alpha360因子（6维度×6期=36个因子，避免冗余）
    """
    factor_df = df.copy()
    # 6个核心维度
    dimensions = ['open', 'high', 'low', 'close', 'volume']
    
    for dim in dimensions:
        # 构建历史6期比值因子
        for i in range(1, 7):
            factor_df[f"{dim}_ratio_{i}"] = factor_df[dim].shift(i) / factor_df['close']
    
    # 计算收益率
    factor_df['return_1d'] = factor_df['close'].pct_change(1)
    factor_df['return_5d'] = factor_df['close'].pct_change(5)
    factor_df['return_10d'] = factor_df['close'].pct_change(10)
    
    # 标签：未来1天涨跌幅
    factor_df['LABEL0'] = factor_df['return_1d'].shift(-1)
    
    # 去掉NaN
    factor_df = factor_df.dropna()
    return factor_df

if __name__ == '__main__':
    print("Stockformer持仓验证工具加载完成")
    print("持仓列表:")
    for stk in HOLDINGS:
        print(f"- {stk['name']}({stk['code']})")
    print("\n使用方法:")
    print("1. get_stock_history() 获取历史行情")
    print("2. build_alpha360_factors() 构建精简版量价因子")
    print("3. 调用Stockformer模型做预测验证")
