# A5L 统一数据管理器
# 提供多数据源自动故障转移能力
# 优先级: Tushare > AKShare > Yahoo > 缓存

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class A5LDataManager:
    """
    A5L 统一数据管理器
    
    设计原则：
    1. 多数据源优先级管理
    2. 自动故障转移
    3. 统一接口，透明切换
    4. 本地缓存作为最后防线
    
    数据源优先级：
    1. Tushare (主要，15000积分账户)
    2. AKShare (备用1)
    3. Yahoo Finance (备用2，美股)
    4. 本地缓存 (最终备用)
    """
    
    DATA_SOURCES = ['tushare', 'akshare', 'yahoo', 'cache']
    
    def __init__(self):
        # 优先从配置文件读取token，其次环境变量，更稳定可靠
        try:
            import json
            from pathlib import Path
            config_path = Path("/workspace/projects/workspace/config/tushare_config.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.tushare_token = config.get('token', os.getenv('TUSHARE_TOKEN', 'c8219c203eb9b321244ca3a4c577d7b6e34621035ea8f940a332ed3c'))
            else:
                self.tushare_token = os.getenv('TUSHARE_TOKEN', 'c8219c203eb9b321244ca3a4c577d7b6e34621035ea8f940a332ed3c')
        except Exception as e:
            logger.warning(f"读取Tushare配置文件失败，使用环境变量: {e}")
            self.tushare_token = os.getenv('TUSHARE_TOKEN', 'c8219c203eb9b321244ca3a4c577d7b6e34621035ea8f940a332ed3c')
        self._init_data_sources()
        self.cache = {}  # 内存缓存
        
    def _init_data_sources(self):
        """初始化各数据源"""
        self.tushare_api = None
        self.akshare_ok = False
        self.yfinance_ok = False
        
        # 尝试初始化 Tushare
        try:
            import tushare as ts
            self.tushare_api = ts.pro_api(self.tushare_token)
            logger.info("[DataManager] Tushare 初始化成功")
        except Exception as e:
            logger.warning(f"[DataManager] Tushare 初始化失败: {e}")
        
        # 检查 AKShare
        try:
            import akshare as ak
            self.akshare_ok = True
            logger.info("[DataManager] AKShare 可用")
        except Exception as e:
            logger.warning(f"[DataManager] AKShare 不可用: {e}")
        
        # 检查 YFinance
        try:
            import yfinance as yf
            self.yfinance_ok = True
            logger.info("[DataManager] Yahoo Finance 可用")
        except Exception as e:
            logger.warning(f"[DataManager] Yahoo Finance 不可用: {e}")
    
    def get_index_daily(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[Any]:
        """
        获取指数日线数据
        
        Args:
            symbol: 指数代码 (如: sh000001, sz399001)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            DataFrame or None
        """
        cache_key = f"index_daily_{symbol}_{start_date}_{end_date}"
        
        # 尝试各数据源
        for source in self.DATA_SOURCES:
            try:
                if source == 'tushare':
                    data = self._get_from_tushare_index(symbol, start_date, end_date)
                elif source == 'akshare':
                    data = self._get_from_akshare_index(symbol, start_date, end_date)
                elif source == 'yahoo':
                    data = self._get_from_yahoo_index(symbol, start_date, end_date)
                else:  # cache
                    data = self._get_from_cache(cache_key)
                
                if data is not None and len(data) > 0:
                    logger.info(f"[DataManager] 从 {source} 获取 {symbol} 数据成功")
                    self._save_to_cache(cache_key, data)
                    return data
                    
            except Exception as e:
                logger.warning(f"[DataManager] {source} 获取 {symbol} 失败: {e}")
                continue
        
        logger.error(f"[DataManager] 所有数据源均无法获取 {symbol}")
        return None
    
    def get_stock_daily(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[Any]:
        """
        获取个股日线数据
        
        Args:
            symbol: 股票代码 (如: 000001.SZ, 600000.SH)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            DataFrame or None
        """
        cache_key = f"stock_daily_{symbol}_{start_date}_{end_date}"
        
        for source in self.DATA_SOURCES:
            try:
                if source == 'tushare':
                    data = self._get_from_tushare_stock(symbol, start_date, end_date)
                elif source == 'akshare':
                    data = self._get_from_akshare_stock(symbol, start_date, end_date)
                elif source == 'yahoo':
                    data = self._get_from_yahoo_stock(symbol, start_date, end_date)
                else:
                    data = self._get_from_cache(cache_key)
                
                if data is not None and len(data) > 0:
                    logger.info(f"[DataManager] 从 {source} 获取 {symbol} 数据成功")
                    self._save_to_cache(cache_key, data)
                    return data
                    
            except Exception as e:
                logger.warning(f"[DataManager] {source} 获取 {symbol} 失败: {e}")
                continue
        
        logger.error(f"[DataManager] 所有数据源均无法获取 {symbol}")
        return None
    
    def get_realtime_quote(self, symbol: str) -> Optional[Dict]:
        """
        获取实时行情
        
        Args:
            symbol: 股票/指数代码
            
        Returns:
            dict or None
        """
        for source in self.DATA_SOURCES:
            try:
                if source == 'tushare':
                    data = self._get_realtime_from_tushare(symbol)
                elif source == 'akshare':
                    data = self._get_realtime_from_akshare(symbol)
                else:
                    continue  # 实时数据不支持 cache
                
                if data is not None:
                    logger.info(f"[DataManager] 从 {source} 获取 {symbol} 实时行情成功")
                    return data
                    
            except Exception as e:
                logger.warning(f"[DataManager] {source} 获取 {symbol} 实时行情失败: {e}")
                continue
        
        return None
    
    # ============ Tushare 实现 ============
    
    def _get_from_tushare_index(self, symbol: str, start: str, end: str) -> Optional[Any]:
        """从 Tushare 获取指数数据"""
        if self.tushare_api is None:
            return None
        
        import tushare as ts
        
        # 转换代码格式
        ts_code = self._convert_to_tushare_code(symbol)
        
        df = self.tushare_api.index_daily(ts_code=ts_code, start_date=start, end_date=end)
        return df if len(df) > 0 else None
    
    def _get_from_tushare_stock(self, symbol: str, start: str, end: str) -> Optional[Any]:
        """从 Tushare 获取股票数据"""
        if self.tushare_api is None:
            return None
        
        ts_code = self._convert_to_tushare_code(symbol)
        # Tushare接口要求日期格式为YYYYMMDD，去掉横杠
        if start:
            start = start.replace('-', '')
        if end:
            end = end.replace('-', '')
        df = self.tushare_api.daily(ts_code=ts_code, start_date=start, end_date=end)
        return df if len(df) > 0 else None
    
    def _get_realtime_from_tushare(self, symbol: str) -> Optional[Dict]:
        """从 Tushare 获取实时行情"""
        if self.tushare_api is None:
            return None
        
        ts_code = self._convert_to_tushare_code(symbol)
        df = self.tushare_api.realtime_quote(ts_code=ts_code)
        
        if df is not None and len(df) > 0:
            row = df.iloc[0]
            return {
                'symbol': symbol,
                'price': float(row.get('price', 0)),
                'open': float(row.get('open', 0)),
                'high': float(row.get('high', 0)),
                'low': float(row.get('low', 0)),
                'volume': float(row.get('vol', 0)),
                'source': 'tushare'
            }
        return None
    
    # ============ AKShare 实现 ============
    
    def _get_from_akshare_index(self, symbol: str, start: str, end: str) -> Optional[Any]:
        """从 AKShare 获取指数数据"""
        if not self.akshare_ok:
            return None
        
        import akshare as ak
        
        # 转换代码格式
        if symbol.startswith('sh'):
            code = symbol[2:] + '.SH'
        elif symbol.startswith('sz'):
            code = symbol[2:] + '.SZ'
        else:
            code = symbol
        
        df = ak.index_zh_a_hist(symbol=code, start_date=start, end_date=end)
        return df if len(df) > 0 else None
    
    def _get_from_akshare_stock(self, symbol: str, start: str, end: str) -> Optional[Any]:
        """从 AKShare 获取股票数据"""
        if not self.akshare_ok:
            return None
        
        import akshare as ak
        
        # 转换代码格式
        if '.' in symbol:
            code = symbol.split('.')[0]
        else:
            code = symbol
        
        df = ak.stock_zh_a_hist(symbol=code, start_date=start, end_date=end)
        return df if len(df) > 0 else None
    
    def _get_realtime_from_akshare(self, symbol: str) -> Optional[Dict]:
        """从 AKShare 获取实时行情"""
        if not self.akshare_ok:
            return None
        
        import akshare as ak
        
        if '.' in symbol:
            code = symbol.split('.')[0]
        else:
            code = symbol[2:] if len(symbol) > 6 else symbol
        
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == code]
        
        if len(row) > 0:
            r = row.iloc[0]
            return {
                'symbol': symbol,
                'price': float(r.get('最新价', 0)),
                'open': float(r.get('今开', 0)),
                'high': float(r.get('最高', 0)),
                'low': float(r.get('最低', 0)),
                'volume': float(r.get('成交量', 0)),
                'source': 'akshare'
            }
        return None
    
    # ============ Yahoo Finance 实现 ============
    
    def _get_from_yahoo_index(self, symbol: str, start: str, end: str) -> Optional[Any]:
        """从 Yahoo 获取指数数据（主要用于美股）"""
        if not self.yfinance_ok:
            return None
        
        import yfinance as yf
        
        # 转换代码格式
        yahoo_symbol = self._convert_to_yahoo_code(symbol)
        
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(start=start, end=end)
        
        return df if len(df) > 0 else None
    
    def _get_from_yahoo_stock(self, symbol: str, start: str, end: str) -> Optional[Any]:
        """从 Yahoo 获取股票数据"""
        if not self.yfinance_ok:
            return None
        
        import yfinance as yf
        
        yahoo_symbol = self._convert_to_yahoo_code(symbol)
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(start=start, end=end)
        
        return df if len(df) > 0 else None
    
    # ============ 缓存实现 ============
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从内存缓存获取"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            # 检查缓存是否过期（30分钟）
            if datetime.now() - timestamp < timedelta(minutes=30):
                logger.info(f"[DataManager] 从缓存获取 {key}")
                return data
        return None
    
    def _save_to_cache(self, key: str, data: Any):
        """保存到内存缓存"""
        self.cache[key] = (data, datetime.now())
    
    # ============ 辅助方法 ============
    
    def _convert_to_tushare_code(self, symbol: str) -> str:
        """转换为 Tushare 代码格式"""
        if symbol.startswith('sh'):
            return symbol[2:] + '.SH'
        elif symbol.startswith('sz'):
            return symbol[2:] + '.SZ'
        elif '.' not in symbol and len(symbol) == 6:
            # 自动判断交易所
            if symbol.startswith('6'):
                return symbol + '.SH'
            else:
                return symbol + '.SZ'
        return symbol
    
    def _convert_to_yahoo_code(self, symbol: str) -> str:
        """转换为 Yahoo 代码格式"""
        if symbol.startswith('sh'):
            return symbol[2:] + '.SS'
        elif symbol.startswith('sz'):
            return symbol[2:] + '.SZ'
        return symbol


# 全局数据管理器实例
_data_manager = None

def get_data_manager() -> A5LDataManager:
    """获取全局数据管理器实例"""
    global _data_manager
    if _data_manager is None:
        _data_manager = A5LDataManager()
    return _data_manager


# 便捷函数
def get_index_daily(symbol: str, start_date: str = None, end_date: str = None):
    """便捷函数：获取指数日线"""
    return get_data_manager().get_index_daily(symbol, start_date, end_date)

def get_stock_daily(symbol: str, start_date: str = None, end_date: str = None):
    """便捷函数：获取个股日线"""
    return get_data_manager().get_stock_daily(symbol, start_date, end_date)

def get_realtime_quote(symbol: str):
    """便捷函数：获取实时行情"""
    return get_data_manager().get_realtime_quote(symbol)
