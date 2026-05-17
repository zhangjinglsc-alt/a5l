#!/usr/bin/env python3
"""
Stockformer风格因子中性化工具
基于论文360量价因子的预处理流程：极值处理 -> 标准化 -> 市值中性化 -> 行业中性化
适配A5L现有因子库
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings

warnings.filterwarnings('ignore')

def neutralize_factor(factor_df, market_cap_df, industry_df, exclude_cols=['datetime', 'instrument', 'LABEL0']):
    """
    对因子DataFrame进行市值+行业中性化处理
    :param factor_df: 原始因子数据， columns包含datetime, instrument, 因子名, [可选LABEL0]
    :param market_cap_df: 市值数据，index=日期，columns=股票代码，values=对数市值
    :param industry_df: 行业哑变量数据，index=股票代码，columns=行业哑变量
    :param exclude_cols: 不需要中性化的列名
    :return: 中性化后的因子DataFrame
    """
    all_factor = []
    factor_cols = [col for col in factor_df.columns if col not in exclude_cols]
    grouped_by_date = factor_df.groupby('datetime')

    for date, df_day in grouped_by_date:
        df_day = df_day.rename(columns={'instrument': 'code'})
        df_day = df_day.set_index('code')
        
        # 获取当日对数市值
        try:
            ltsz = np.log(market_cap_df.loc[date].to_frame())
        except KeyError:
            print(f"Warning: No market cap data for date {date}, skipped")
            continue

        day_result = []
        for factor_name in factor_cols:
            # 提取单因子数据
            factor_series = df_day[factor_name].to_frame(name='factor')
            
            # 跳过全NaN的因子
            if factor_series['factor'].isna().all():
                continue

            # 拼接因子、市值、行业数据
            merged = pd.concat([factor_series, ltsz, industry_df], axis=1, join='inner')
            if merged.empty:
                continue

            # 回归取残差（中性化）
            X = merged.drop('factor', axis=1)
            y = merged['factor']
            model = sm.OLS(y, X, missing='drop')
            results = model.fit()
            
            # 计算残差即中性化后的因子
            neutralized = y.loc[results.fittedvalues.index] - results.fittedvalues
            
            # 标准化处理
            neutralized = neutralized.replace([np.inf, -np.inf], np.nan)
            neutralized = (neutralized - neutralized.mean()) / neutralized.std()
            
            # 恢复索引并命名
            neutralized = neutralized.reindex(factor_series.index)
            neutralized.name = factor_name
            day_result.append(neutralized)

        if not day_result:
            continue
            
        # 合并当日所有因子
        df_day_neutral = pd.concat(day_result, axis=1)
        df_day_neutral['datetime'] = date
        all_factor.append(df_day_neutral.reset_index())

    if not all_factor:
        return pd.DataFrame()
        
    return pd.concat(all_factor, ignore_index=True)

def preprocess_factor_raw(factor_df):
    """
    因子原始数据预处理：极值处理（3σ）、缺失值填充
    :param factor_df: 原始因子数据
    :return: 预处理后的因子数据
    """
    factor_cols = [col for col in factor_df.columns if col not in ['datetime', 'instrument', 'LABEL0']]
    
    for col in factor_cols:
        # 3σ极值处理
        mean = factor_df[col].mean()
        std = factor_df[col].std()
        upper = mean + 3 * std
        lower = mean - 3 * std
        factor_df[col] = factor_df[col].clip(lower, upper)
        
        # 中位数填充缺失值
        factor_df[col] = factor_df[col].fillna(factor_df[col].median())
    
    return factor_df

if __name__ == '__main__':
    # 测试示例
    print("Stockformer因子中性化工具加载完成")
    print("使用方法：")
    print("1. preprocess_factor_raw() 做极值处理和缺失值填充")
    print("2. neutralize_factor() 做市值+行业中性化")
