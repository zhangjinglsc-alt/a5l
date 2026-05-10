#!/usr/bin/env python3
"""
A5L CIO Awakening - Feishu Cloud Data Access Layer
直接从飞书云文档读取parquet数据
"""
import pandas as pd
import json
import os
from typing import Optional, List, Dict
from datetime import datetime, timedelta

class FeishuCloudDataAccessor:
    """
    飞书云文档数据访问层
    直接从飞书云文档读取历史股价数据
    """
    
    def __init__(self, folder_token: str = "IvY8fOY3ZlfOHeduM3Tcw3k9nxh"):
        self.folder_token = folder_token
        self._file_cache = {}  # 文件名到token的缓存
        self._data_cache = {}  # 数据缓存
        
    def _list_files(self) -> List[Dict]:
        """列出云文档中的所有文件"""
        try:
            # 使用openclaw命令行工具获取文件列表
            import subprocess
            result = subprocess.run(
                ["openclaw", "tools", "feishu_drive_file", "list", 
                 "--folder_token", self.folder_token],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print(f"Error listing files: {result.stderr}")
                return []
            
            # 解析输出
            try:
                data = json.loads(result.stdout)
                return data.get("files", [])
            except:
                return []
        except Exception as e:
            print(f"Exception listing files: {e}")
            return []
    
    def _download_file(self, file_token: str, output_path: str) -> bool:
        """下载单个文件"""
        try:
            import subprocess
            result = subprocess.run(
                ["openclaw", "tools", "feishu_drive_file", "download",
                 "--file_token", file_token,
                 "--type", "file",
                 "--output_path", output_path],
                capture_output=True, text=True
            )
            return result.returncode == 0 or "saved_path" in result.stdout
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
    
    def load_date(self, date_str: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        加载指定日期的数据
        
        Args:
            date_str: 日期字符串 (如 "20130307")
            use_cache: 是否使用本地缓存
            
        Returns:
            DataFrame or None
        """
        cache_path = f"/tmp/feishu_data_{date_str}.parquet"
        
        # 检查缓存
        if use_cache and os.path.exists(cache_path):
            return pd.read_parquet(cache_path)
        
        # 构建文件名
        filename = f"{date_str}.parquet"
        
        # 从云文档下载
        # 首先获取文件token
        files = self._list_files()
        file_token = None
        for f in files:
            if f.get("name") == filename:
                file_token = f.get("token")
                break
        
        if not file_token:
            print(f"File not found in cloud: {filename}")
            return None
        
        # 下载文件
        if self._download_file(file_token, cache_path):
            return pd.read_parquet(cache_path)
        else:
            return None
    
    def get_available_dates(self) -> List[str]:
        """获取所有可用日期列表"""
        files = self._list_files()
        dates = []
        for f in files:
            name = f.get("name", "")
            if name.endswith(".parquet"):
                date_str = name.replace(".parquet", "")
                dates.append(date_str)
        return sorted(dates)
    
    def load_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        加载日期范围的数据
        
        Args:
            start_date: 开始日期 (如 "20130101")
            end_date: 结束日期 (如 "20130307")
            
        Returns:
            Combined DataFrame
        """
        dates = self.get_available_dates()
        
        # 过滤日期范围
        filtered_dates = [d for d in dates if start_date <= d <= end_date]
        
        if not filtered_dates:
            return pd.DataFrame()
        
        # 加载所有数据
        dfs = []
        for date_str in filtered_dates:
            df = self.load_date(date_str)
            if df is not None:
                dfs.append(df)
        
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        else:
            return pd.DataFrame()


class CIODataManager:
    """
    CIO数据管理器
    提供高级数据查询接口
    """
    
    def __init__(self):
        self.accessor = FeishuCloudDataAccessor()
        
    def get_stock_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指定股票的历史数据
        
        Args:
            code: 股票代码 (如 "000001.SZ")
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            DataFrame with stock data
        """
        df = self.accessor.load_date_range(start_date, end_date)
        if df.empty:
            return df
        return df[df['code'] == code].sort_values('date')
    
    def get_market_data(self, date: str) -> pd.DataFrame:
        """
        获取某日的全市场数据
        
        Args:
            date: 日期 (如 "20130307")
            
        Returns:
            DataFrame
        """
        return self.accessor.load_date(date)
    
    def get_top_movers(self, date: str, n: int = 20) -> pd.DataFrame:
        """
        获取当日涨跌幅最大的股票
        
        Args:
            date: 日期
            n: 返回数量
            
        Returns:
            DataFrame
        """
        df = self.accessor.load_date(date)
        if df.empty:
            return df
        return df.nlargest(n, 'pct_chg')[['code', 'name' if 'name' in df.columns else 'code', 'close', 'pct_chg']]


# 全局实例
data_manager = CIODataManager()


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("A5L CIO Cloud Data Access Layer - Test")
    print("=" * 60)
    
    accessor = FeishuCloudDataAccessor()
    
    # 测试获取可用日期
    print("\nAvailable dates (first 10):")
    dates = accessor.get_available_dates()
    for d in dates[:10]:
        print(f"  {d}")
    print(f"  ... ({len(dates)} total)")
    
    # 测试加载单日数据
    print("\nLoading 20130307 data:")
    df = accessor.load_date("20130307")
    if df is not None:
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"\nTop 5 by pct_chg:")
        print(df.nlargest(5, 'pct_chg')[['code', 'close', 'pct_chg']])
    else:
        print("  Failed to load data")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
