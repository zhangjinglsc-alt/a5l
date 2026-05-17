#!/usr/bin/env python3
"""
A5L 多源数据校验模块 v1.0
三级多源冗余架构 + 多数投票校验机制
"""

import sys
import json
import akshare as ak
import baostock as bs
import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 数据源健康度评分
data_source_health = {
    "akshare": {"score": 95, "fail_count": 0, "last_success": None},
    "baostock": {"score": 90, "fail_count": 0, "last_success": None},
    "tushare": {"score": 85, "fail_count": 0, "last_success": None},
    "yfinance": {"score": 88, "fail_count": 0, "last_success": None},
    "finnhub": {"score": 92, "fail_count": 0, "last_success": None}
}

# Tushare token配置，后续从config读取
TS_TOKEN = "your_tushare_token_here"
ts.set_token(TS_TOKEN)
pro = ts.pro_api()

class MultiSourceDataValidator:
    def __init__(self):
        self.ak = ak
        self.bs = bs
        self.ts = pro
        self.issues = []
        
    def get_stock_price_cn(self, symbol: str, start_date: str, end_date: str, adjust: str = "hfq") -> Tuple[pd.DataFrame, str, float]:
        """
        获取A股股票价格，多源校验
        :param symbol: 股票代码，如"000001"
        :param start_date: 开始日期，格式"YYYY-MM-DD"
        :param end_date: 结束日期，格式"YYYY-MM-DD"
        :param adjust: 复权类型，"qfq"前复权/"hfq"后复权/"None"不复权
        :return: (价格DataFrame, 最优数据源, 置信度)
        """
        results = {}
        
        # 1. 尝试akshare（一级主源）
        try:
            df_ak = self.ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date.replace("-", ""), 
                                           end_date=end_date.replace("-", ""), adjust=adjust)
            df_ak = df_ak.rename(columns={"日期": "date", "开盘": "open", "最高": "high", "最低": "low", 
                                        "收盘": "close", "成交量": "volume", "成交额": "amount"})
            df_ak["date"] = pd.to_datetime(df_ak["date"]).dt.strftime("%Y-%m-%d")
            df_ak = df_ak.set_index("date").sort_index()
            results["akshare"] = df_ak
            self._update_health("akshare", success=True)
        except Exception as e:
            self._update_health("akshare", success=False)
            self.issues.append(f"akshare获取{symbol}失败: {str(e)}")
            
        # 2. 尝试baostock（二级备源）
        try:
            bs.login()
            adjust_flag = "1" if adjust == "qfq" else "2" if adjust == "hfq" else "3"
            rs = bs.query_history_k_data_plus(f"sh.{symbol}" if symbol.startswith("6") else f"sz.{symbol}",
                "date,open,high,low,close,volume,amount", start_date=start_date, end_date=end_date,
                frequency="d", adjustflag=adjust_flag)
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            df_bs = pd.DataFrame(data_list, columns=rs.fields)
            for col in ["open", "high", "low", "close", "volume", "amount"]:
                df_bs[col] = pd.to_numeric(df_bs[col])
            df_bs = df_bs.set_index("date").sort_index()
            results["baostock"] = df_bs
            self._update_health("baostock", success=True)
            bs.logout()
        except Exception as e:
            bs.logout()
            self._update_health("baostock", success=False)
            self.issues.append(f"baostock获取{symbol}失败: {str(e)}")
            
        # 3. 尝试tushare（三级兜底源）
        try:
            ts_symbol = f"{symbol}.SH" if symbol.startswith("6") else f"{symbol}.SZ"
            adj = "qfq" if adjust == "qfq" else "hfq" if adjust == "hfq" else None
            df_ts = self.ts.daily(ts_code=ts_symbol, start_date=start_date.replace("-", ""), 
                                 end_date=end_date.replace("-", ""))
            if adj:
                df_adj = self.ts.adj_factor(ts_code=ts_symbol, start_date=start_date.replace("-", ""), 
                                           end_date=end_date.replace("-", ""))
                df_ts = df_ts.merge(df_adj, on="trade_date")
                for col in ["open", "high", "low", "close"]:
                    df_ts[col] = df_ts[col] * df_ts["adj_factor"] / df_ts["adj_factor"].iloc[-1]
            df_ts["date"] = pd.to_datetime(df_ts["trade_date"]).dt.strftime("%Y-%m-%d")
            df_ts = df_ts.rename(columns={"vol": "volume", "amount": "amount"})
            df_ts = df_ts[["date", "open", "high", "low", "close", "volume", "amount"]].set_index("date").sort_index()
            results["tushare"] = df_ts
            self._update_health("tushare", success=True)
        except Exception as e:
            self._update_health("tushare", success=False)
            self.issues.append(f"tushare获取{symbol}失败: {str(e)}")
            
        # 多源校验和结果融合
        return self._fuse_results(results, symbol)
    
    def _fuse_results(self, results: Dict[str, pd.DataFrame], symbol: str) -> Tuple[pd.DataFrame, str, float]:
        """多源结果融合，多数投票机制"""
        if not results:
            raise Exception(f"所有数据源获取{symbol}失败")
            
        # 按健康度排序，优先使用评分高的数据源
        sorted_sources = sorted(results.keys(), key=lambda x: data_source_health[x]["score"], reverse=True)
        primary_source = sorted_sources[0]
        primary_df = results[primary_source]
        confidence = data_source_health[primary_source]["score"] / 100
        
        if len(results) == 1:
            self.issues.append(f"{symbol}仅{primary_source}返回数据，置信度{confidence:.2f}")
            return primary_df, primary_source, confidence
            
        # 多源交叉校验
        valid_dfs = []
        for src in sorted_sources[1:]:
            df = results[src]
            common_dates = primary_df.index.intersection(df.index)
            if len(common_dates) == 0:
                continue
            # 计算收盘价差异
            close_diff = abs(primary_df.loc[common_dates, "close"] - df.loc[common_dates, "close"]) / primary_df.loc[common_dates, "close"]
            avg_diff = close_diff.mean()
            if avg_diff < 0.002: # 差异<0.2%，完全一致
                valid_dfs.append(df)
            elif avg_diff < 0.005: # 差异0.2-0.5%，标记载入issues
                self.issues.append(f"{symbol} {primary_source}与{src}收盘价平均差异{avg_diff:.2%}，在容忍范围内")
                valid_dfs.append(df)
            else: # 差异>0.5%，告警
                self.issues.append(f"⚠️ {symbol} {primary_source}与{src}收盘价平均差异{avg_diff:.2%}，超过阈值！")
                
        if len(valid_dfs) >= 1:
            # 多数投票，取均值
            all_dfs = [primary_df] + valid_dfs
            fused_df = pd.concat(all_dfs).groupby(level=0).mean()
            confidence = min(0.99, confidence + len(valid_dfs) * 0.05)
            return fused_df, f"{primary_source}+{len(valid_dfs)}源融合", confidence
        else:
            self.issues.append(f"{symbol}各数据源差异过大，使用主源{primary_source}数据，置信度{confidence:.2f}")
            return primary_df, primary_source, confidence
    
    def _update_health(self, source: str, success: bool):
        """更新数据源健康度评分"""
        if success:
            data_source_health[source]["fail_count"] = max(0, data_source_health[source]["fail_count"] - 1)
            data_source_health[source]["score"] = min(100, data_source_health[source]["score"] + 1)
            data_source_health[source]["last_success"] = datetime.now().isoformat()
        else:
            data_source_health[source]["fail_count"] += 1
            data_source_health[source]["score"] = max(0, data_source_health[source]["score"] - 5)
            
    def save_issues(self, path: str = "issues.md"):
        """保存异常问题到日志"""
        if not self.issues:
            return
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 数据异常记录\n")
            for issue in self.issues:
                f.write(f"- {issue}\n")
                
    def get_health_status(self) -> Dict:
        """获取所有数据源健康状态"""
        return data_source_health

if __name__ == "__main__":
    print("="*70)
    print("🤖 A5L 多源数据校验模块测试".center(60))
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(60))
    print("="*70)
    
    # 测试：获取中国长城(000066)近30天数据
    validator = MultiSourceDataValidator()
    try:
        df, source, confidence = validator.get_stock_price_cn("000066", 
            start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d"))
        print(f"\n✅ 测试成功！")
        print(f"   标的: 000066 中国长城")
        print(f"   数据源: {source}")
        print(f"   置信度: {confidence:.2%}")
        print(f"   数据行数: {len(df)}")
        print(f"   最新收盘价: {df['close'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        
    # 保存异常
    validator.save_issues()
    print(f"\n📝 异常记录已保存到issues.md")
    print("\n" + "="*70)
