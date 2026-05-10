#!/usr/bin/env python3
"""
A5L CIO Awakening v2.1 - Hybrid Data Provider
混合数据源：本地parquet + Tushare实时数据
"""
import pandas as pd
import os
from typing import Optional, List
from datetime import datetime, timedelta

class HybridDataProvider:
    """
    混合数据提供器
    优先使用本地数据，缺失时自动切换到Tushare
    """
    
    def __init__(self, local_data_path: str = "/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/historical/1d_price_fresh"):
        self.local_path = local_data_path
        self.tushare_token = None
        self._init_tushare()
        
    def _init_tushare(self):
        """初始化Tushare连接"""
        try:
            import tushare as ts
            # Try to get token from environment or config
            self.tushare_token = os.getenv('TUSHARE_TOKEN')
            if self.tushare_token:
                ts.set_token(self.tushare_token)
                self.pro = ts.pro_api()
                print("✅ Tushare initialized successfully")
            else:
                self.pro = None
                print("⚠️ Tushare token not found, using local data only")
        except Exception as e:
            print(f"⚠️ Tushare not available: {e}")
            self.pro = None
    
    def load_local_date(self, date_str: str) -> Optional[pd.DataFrame]:
        """从本地加载单日数据"""
        filepath = os.path.join(self.local_path, f"{date_str}.parquet")
        if os.path.exists(filepath):
            try:
                return pd.read_parquet(filepath)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                return None
        return None
    
    def load_tushare_date(self, date_str: str) -> Optional[pd.DataFrame]:
        """从Tushare加载单日数据"""
        if not self.pro:
            return None
        
        try:
            # Convert date format from 20130307 to 2013-03-07
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
            
            # Fetch daily data from Tushare
            df = self.pro.daily(trade_date=date_str)
            if df is not None and not df.empty:
                # Rename columns to match local format
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
                return df
        except Exception as e:
            print(f"Error fetching from Tushare: {e}")
        
        return None
    
    def get_date(self, date_str: str) -> Optional[pd.DataFrame]:
        """
        获取指定日期的数据
        优先本地，其次Tushare
        """
        # Try local first
        local_data = self.load_local_date(date_str)
        if local_data is not None:
            return local_data
        
        # Fallback to Tushare
        print(f"Local data not found for {date_str}, trying Tushare...")
        return self.load_tushare_date(date_str)
    
    def get_local_dates(self) -> List[str]:
        """获取本地可用日期列表"""
        dates = []
        if os.path.exists(self.local_path):
            for f in os.listdir(self.local_path):
                if f.endswith('.parquet'):
                    dates.append(f.replace('.parquet', ''))
        return sorted(dates)


class CIODataEngine:
    """
    CIO数据引擎
    提供高级数据查询和分析功能
    """
    
    def __init__(self):
        self.provider = HybridDataProvider()
        
    def get_stock_history(self, code: str, days: int = 30) -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            code: 股票代码 (如 "000001.SZ")
            days: 历史天数
            
        Returns:
            DataFrame with historical data
        """
        dates = self.provider.get_local_dates()
        if not dates:
            return pd.DataFrame()
        
        # Get last N dates
        recent_dates = dates[-days:]
        
        dfs = []
        for date_str in recent_dates:
            df = self.provider.get_date(date_str)
            if df is not None:
                stock_df = df[df['code'] == code]
                if not stock_df.empty:
                    dfs.append(stock_df)
        
        if dfs:
            result = pd.concat(dfs, ignore_index=True)
            return result.sort_values('date')
        return pd.DataFrame()
    
    def get_market_snapshot(self, date_str: str) -> dict:
        """
        获取市场快照
        
        Returns:
            Dictionary with market statistics
        """
        df = self.provider.get_date(date_str)
        if df is None or df.empty:
            return {}
        
        return {
            'date': date_str,
            'total_stocks': len(df),
            'up_stocks': len(df[df['pct_chg'] > 0]),
            'down_stocks': len(df[df['pct_chg'] < 0]),
            'limit_up': len(df[df['pct_chg'] >= 9.9]),
            'limit_down': len(df[df['pct_chg'] <= -9.9]),
            'avg_change': df['pct_chg'].mean(),
            'total_amount': df['amount'].sum() / 1e8,  # 亿元
            'top_gainer': df.loc[df['pct_chg'].idxmax(), 'code'] if not df.empty else None,
            'top_gainer_pct': df['pct_chg'].max() if not df.empty else 0
        }
    
    def get_sector_analysis(self, date_str: str) -> pd.DataFrame:
        """
        获取板块分析
        
        Note: This is a simplified version. Full implementation would
        require sector classification data.
        """
        df = self.provider.get_date(date_str)
        if df is None:
            return pd.DataFrame()
        
        # Group by first 2 digits of code (simplified sector)
        df['sector'] = df['code'].str[:2]
        
        sector_stats = df.groupby('sector').agg({
            'pct_chg': 'mean',
            'amount': 'sum',
            'code': 'count'
        }).rename(columns={'code': 'count'})
        
        return sector_stats.sort_values('pct_chg', ascending=False)


# 全局引擎实例
cio_engine = CIODataEngine()


if __name__ == "__main__":
    print("=" * 70)
    print("A5L CIO Awakening v2.1 - Hybrid Data Engine Test")
    print("=" * 70)
    
    engine = CIODataEngine()
    
    # Test 1: Local dates
    print("\n📅 Local available dates:")
    dates = engine.provider.get_local_dates()
    print(f"   Found: {len(dates)} dates")
    if dates:
        print(f"   Sample: {dates[:5]}")
    
    # Test 2: Market snapshot
    if dates:
        test_date = dates[-1]
        print(f"\n📊 Market snapshot for {test_date}:")
        snapshot = engine.get_market_snapshot(test_date)
        for key, value in snapshot.items():
            print(f"   {key}: {value}")
    
    # Test 3: Stock history
    print("\n📈 Testing stock history (000001.SZ):")
    history = engine.get_stock_history("000001.SZ", days=5)
    if not history.empty:
        print(history[['date', 'open', 'close', 'pct_chg']].to_string(index=False))
    else:
        print("   No data available")
    
    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70)
