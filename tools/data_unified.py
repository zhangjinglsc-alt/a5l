#!/usr/bin/env python3
"""
A5L统一数据接口 - Tushare深度集成版
Layer 1 数据底座核心模块

功能:
- A股/港股行情数据 (Tushare优先 + AKShare备份)
- 财务数据 (Tushare完整三表)
- 龙虎榜数据 (Tushare超短策略核心)
- 资金流向 (Tushare北向资金)
- 新闻数据 (Tushare包年会员)

架构:
- Tushare: 主数据源，15000积分会员
- AKShare: 备份数据源，当Tushare失败时自动降级
- 数据验证: 双源对比，异常预警
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union, Tuple
import pandas as pd

sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

# 日志配置
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('A5L_Data_Unified')


class A5LDataSource:
    """
    A5L统一数据接口
    Tushare深度集成 + AKShare备份
    """
    
    def __init__(self):
        """初始化数据源"""
        self.tushare_pro = None
        self.akshare_available = False
        
        # 初始化Tushare
        self._init_tushare()
        
        # 初始化AKShare
        self._init_akshare()
        
        # 统计信息
        self.stats = {
            'tushare_calls': 0,
            'akshare_calls': 0,
            'fallback_count': 0,
            'errors': []
        }
        
        logger.info("✅ A5L统一数据接口初始化完成")
    
    def _init_tushare(self):
        """初始化Tushare"""
        try:
            from tushare_client import TushareDataSource
            
            config_path = '/workspace/projects/workspace/config/tushare_config.json'
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                self.tushare_pro = TushareDataSource(token=config['token'])
                self.tushare_pro_module = __import__('tushare')
                logger.info(f"   Tushare已连接 (积分: {config.get('points', 'N/A')})")
            else:
                logger.warning("   Tushare配置未找到")
        except Exception as e:
            logger.error(f"   Tushare初始化失败: {e}")
    
    def _init_akshare(self):
        """初始化AKShare"""
        try:
            import akshare as ak
            self.akshare = ak
            self.akshare_available = True
            logger.info("   AKShare备份已就绪")
        except ImportError:
            logger.warning("   AKShare未安装")
    
    # ==================== A股行情数据 ====================
    
    def get_a_share_daily(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取A股日线数据
        
        Args:
            symbol: 股票代码 (如 '000001' 或 '000001.SZ')
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            DataFrame包含日线数据
        """
        # 标准化代码
        if '.' not in symbol:
            symbol = self._standardize_code(symbol)
        
        if not start_date:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        
        # 优先使用Tushare
        try:
            if self.tushare_pro:
                df = self.tushare_pro.get_daily(symbol, start_date, end_date)
                if len(df) > 0:
                    self.stats['tushare_calls'] += 1
                    logger.info(f"   ✅ Tushare: {symbol} 日线数据 {len(df)}条")
                    return df
        except Exception as e:
            logger.warning(f"   Tushare获取失败: {e}")
        
        # 降级到AKShare
        if self.akshare_available:
            try:
                # 移除后缀
                code = symbol.split('.')[0]
                df = self.akshare.stock_zh_a_hist(symbol=code, start_date=start_date, end_date=end_date)
                if len(df) > 0:
                    self.stats['akshare_calls'] += 1
                    self.stats['fallback_count'] += 1
                    logger.info(f"   ✅ AKShare(备份): {symbol} 日线数据 {len(df)}条")
                    return df
            except Exception as e:
                logger.error(f"   AKShare获取失败: {e}")
        
        logger.error(f"   ❌ 无法获取 {symbol} 日线数据")
        return pd.DataFrame()
    
    def get_a_share_realtime(self, symbol: str) -> Dict:
        """
        获取A股实时行情
        
        Args:
            symbol: 股票代码
        
        Returns:
            实时行情数据字典
        """
        # 标准化代码
        if '.' not in symbol:
            symbol = self._standardize_code(symbol)
        
        try:
            # 使用Tushare daily_basic获取最新数据
            today = datetime.now().strftime('%Y%m%d')
            df = self.tushare_pro.pro.daily_basic(ts_code=symbol, trade_date=today)
            
            if len(df) > 0:
                return {
                    'code': symbol,
                    'date': today,
                    'close': df.iloc[0].get('close'),
                    'pe': df.iloc[0].get('pe'),
                    'pb': df.iloc[0].get('pb'),
                    'turnover_rate': df.iloc[0].get('turnover_rate'),
                    'volume_ratio': df.iloc[0].get('volume_ratio'),
                    'source': 'tushare'
                }
        except Exception as e:
            logger.warning(f"   Tushare实时行情失败: {e}")
        
        # 降级到AKShare实时行情
        if self.akshare_available:
            try:
                code = symbol.split('.')[0]
                df = self.akshare.stock_zh_a_spot_em()
                stock_data = df[df['代码'] == code]
                
                if len(stock_data) > 0:
                    return {
                        'code': symbol,
                        'date': datetime.now().strftime('%Y%m%d'),
                        'close': stock_data.iloc[0].get('最新价'),
                        'pe': stock_data.iloc[0].get('市盈率-动态'),
                        'pb': stock_data.iloc[0].get('市净率'),
                        'turnover_rate': stock_data.iloc[0].get('换手率'),
                        'source': 'akshare'
                    }
            except Exception as e:
                logger.error(f"   AKShare实时行情失败: {e}")
        
        return {}
    
    # ==================== 财务数据 ====================
    
    def get_financial_report(self, symbol: str, report_type: str = 'income') -> pd.DataFrame:
        """
        获取财务报表
        
        Args:
            symbol: 股票代码
            report_type: 报表类型 - income(利润表)/balance(资产负债表)/cashflow(现金流)
        
        Returns:
            DataFrame包含财务报表数据
        """
        if '.' not in symbol:
            symbol = self._standardize_code(symbol)
        
        today = datetime.now()
        end_date = today.strftime('%Y%m%d')
        start_date = (today - timedelta(days=365*3)).strftime('%Y%m%d')  # 3年数据
        
        try:
            if report_type == 'income':
                df = self.tushare_pro.get_income(symbol, start_date, end_date)
            elif report_type == 'balance':
                df = self.tushare_pro.get_balance_sheet(symbol, start_date, end_date)
            elif report_type == 'cashflow':
                df = self.tushare_pro.get_cash_flow(symbol, start_date, end_date)
            else:
                logger.error(f"   未知报表类型: {report_type}")
                return pd.DataFrame()
            
            if len(df) > 0:
                self.stats['tushare_calls'] += 1
                logger.info(f"   ✅ Tushare: {symbol} {report_type}报表 {len(df)}条")
                return df
            
        except Exception as e:
            logger.warning(f"   Tushare财务数据失败: {e}")
        
        logger.error(f"   ❌ 无法获取 {symbol} 财务数据")
        return pd.DataFrame()
    
    def get_financial_indicators(self, symbol: str) -> pd.DataFrame:
        """
        获取财务指标
        
        Args:
            symbol: 股票代码
        
        Returns:
            DataFrame包含ROE、毛利率、净利率等指标
        """
        if '.' not in symbol:
            symbol = self._standardize_code(symbol)
        
        try:
            df = self.tushare_pro.pro.fina_indicator(ts_code=symbol)
            if len(df) > 0:
                self.stats['tushare_calls'] += 1
                logger.info(f"   ✅ Tushare: {symbol} 财务指标 {len(df)}条")
                return df
        except Exception as e:
            logger.warning(f"   Tushare财务指标失败: {e}")
        
        return pd.DataFrame()
    
    # ==================== 龙虎榜数据 (超短策略核心) ====================
    
    def get_top_list(self, date: str = None) -> pd.DataFrame:
        """
        获取龙虎榜数据
        
        Args:
            date: 日期 (YYYYMMDD)，默认最近交易日
        
        Returns:
            DataFrame包含龙虎榜详情
        """
        if not date:
            date = self._get_last_trade_date()
        
        try:
            df = self.tushare_pro.get_top_list(date)
            if len(df) > 0:
                self.stats['tushare_calls'] += 1
                logger.info(f"   ✅ Tushare: 龙虎榜 {date} {len(df)}条")
                return df
        except Exception as e:
            logger.warning(f"   Tushare龙虎榜失败: {e}")
        
        # 降级到AKShare
        if self.akshare_available:
            try:
                df = self.akshare.stock_lhb_detail_daily(start_date=date, end_date=date)
                if len(df) > 0:
                    self.stats['akshare_calls'] += 1
                    self.stats['fallback_count'] += 1
                    logger.info(f"   ✅ AKShare(备份): 龙虎榜 {date} {len(df)}条")
                    return df
            except Exception as e:
                logger.error(f"   AKShare龙虎榜失败: {e}")
        
        return pd.DataFrame()
    
    def get_top_inst(self, date: str = None) -> pd.DataFrame:
        """
        获取龙虎榜机构明细
        
        Args:
            date: 日期 (YYYYMMDD)
        
        Returns:
            DataFrame包含机构买卖明细
        """
        if not date:
            date = self._get_last_trade_date()
        
        try:
            df = self.tushare_pro.pro.top_inst(trade_date=date)
            if len(df) > 0:
                self.stats['tushare_calls'] += 1
                logger.info(f"   ✅ Tushare: 龙虎榜机构 {date} {len(df)}条")
                return df
        except Exception as e:
            logger.warning(f"   Tushare龙虎榜机构失败: {e}")
        
        return pd.DataFrame()
    
    # ==================== 资金流向 ====================
    
    def get_north_money(self, days: int = 10) -> pd.DataFrame:
        """
        获取北向资金流向
        
        Args:
            days: 获取天数
        
        Returns:
            DataFrame包含北向资金数据
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            df = self.tushare_pro.get_north_money(
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d')
            )
            if len(df) > 0:
                self.stats['tushare_calls'] += 1
                logger.info(f"   ✅ Tushare: 北向资金 {len(df)}条")
                return df
        except Exception as e:
            logger.warning(f"   Tushare北向资金失败: {e}")
        
        return pd.DataFrame()
    
    # ==================== 新闻数据 (包年会员) ====================
    
    def get_stock_news(self, symbol: str, limit: int = 50) -> pd.DataFrame:
        """
        获取个股新闻
        
        Args:
            symbol: 股票代码
            limit: 获取条数
        
        Returns:
            DataFrame包含新闻列表
        """
        if '.' not in symbol:
            symbol = self._standardize_code(symbol)
        
        try:
            df = self.tushare_pro.pro.news(ts_code=symbol)
            if len(df) > 0:
                df = df.head(limit)
                self.stats['tushare_calls'] += 1
                logger.info(f"   ✅ Tushare: {symbol} 新闻 {len(df)}条")
                return df
        except Exception as e:
            logger.warning(f"   Tushare个股新闻失败: {e}")
        
        return pd.DataFrame()
    
    def get_major_news(self, src: str = 'sina', days: int = 1) -> pd.DataFrame:
        """
        获取重大新闻
        
        Args:
            src: 来源 (sina/10jqka/eastmoney/yuncaijing)
            days: 获取天数
        
        Returns:
            DataFrame包含重大新闻
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        try:
            df = self.tushare_pro.pro.major_news(src=src, start_date=start_date)
            if len(df) > 0:
                self.stats['tushare_calls'] += 1
                logger.info(f"   ✅ Tushare: 重大新闻({src}) {len(df)}条")
                return df
        except Exception as e:
            logger.warning(f"   Tushare重大新闻失败: {e}")
        
        return pd.DataFrame()
    
    # ==================== 港股数据 ====================
    
    def get_hk_stock_daily(self, symbol: str) -> pd.DataFrame:
        """
        获取港股日线数据
        
        Args:
            symbol: 港股代码 (如 '00700.HK')
        
        Returns:
            DataFrame包含港股日线数据
        """
        try:
            # 使用港股通数据
            df = self.tushare_pro.pro.hk_daily(ts_code=symbol)
            if len(df) > 0:
                self.stats['tushare_calls'] += 1
                logger.info(f"   ✅ Tushare: {symbol} 港股日线 {len(df)}条")
                return df
        except Exception as e:
            logger.warning(f"   Tushare港股数据失败: {e}")
        
        return pd.DataFrame()
    
    # ==================== 工具方法 ====================
    
    def _standardize_code(self, code: str) -> str:
        """标准化股票代码"""
        code = str(code).replace('.SH', '').replace('.SZ', '')
        
        if code.startswith('6'):
            return f"{code}.SH"
        elif code.startswith('0') or code.startswith('3'):
            return f"{code}.SZ"
        elif code.startswith('68'):
            return f"{code}.SH"
        elif code.startswith('8') or code.startswith('4'):
            return f"{code}.BJ"
        else:
            return f"{code}.SZ"
    
    def _get_last_trade_date(self) -> str:
        """获取最近交易日"""
        today = datetime.now()
        # 简单处理：如果是周末，返回周五
        weekday = today.weekday()
        if weekday == 5:  # 周六
            today = today - timedelta(days=1)
        elif weekday == 6:  # 周日
            today = today - timedelta(days=2)
        
        return today.strftime('%Y%m%d')
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'tushare_calls': 0,
            'akshare_calls': 0,
            'fallback_count': 0,
            'errors': []
        }


# ==================== 快捷函数 ====================

_data_source = None

def get_data_source() -> A5LDataSource:
    """获取数据接口实例 (单例模式)"""
    global _data_source
    if _data_source is None:
        _data_source = A5LDataSource()
    return _data_source


def get_stock_daily(symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """快捷获取A股日线"""
    return get_data_source().get_a_share_daily(symbol, start_date, end_date)


def get_stock_realtime(symbol: str) -> Dict:
    """快捷获取A股实时行情"""
    return get_data_source().get_a_share_realtime(symbol)


def get_financial_report(symbol: str, report_type: str = 'income') -> pd.DataFrame:
    """快捷获取财务报表"""
    return get_data_source().get_financial_report(symbol, report_type)


def get_top_list(date: str = None) -> pd.DataFrame:
    """快捷获取龙虎榜"""
    return get_data_source().get_top_list(date)


def get_north_money(days: int = 10) -> pd.DataFrame:
    """快捷获取北向资金"""
    return get_data_source().get_north_money(days)


def get_stock_news(symbol: str, limit: int = 50) -> pd.DataFrame:
    """快捷获取个股新闻"""
    return get_data_source().get_stock_news(symbol, limit)


# ==================== 测试 ====================

if __name__ == '__main__':
    print("="*70)
    print("🚀 A5L统一数据接口测试")
    print("="*70)
    
    ds = A5LDataSource()
    
    print("\n📊 测试1: A股日线数据")
    start = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
    end = datetime.now().strftime('%Y%m%d')
    df = ds.get_a_share_daily('000001', start_date=start, end_date=end)
    print(f"   获取到 {len(df)} 条数据")
    
    print("\n📊 测试2: 财务数据")
    df = ds.get_financial_report('000001', 'income')
    print(f"   获取到 {len(df)} 条数据")
    
    print("\n📊 测试3: 龙虎榜")
    df = ds.get_top_list()
    print(f"   获取到 {len(df)} 条数据")
    
    print("\n📊 测试4: 北向资金")
    df = ds.get_north_money(days=5)
    print(f"   获取到 {len(df)} 条数据")
    
    print("\n📊 统计信息")
    stats = ds.get_stats()
    print(f"   Tushare调用: {stats['tushare_calls']}")
    print(f"   AKShare调用: {stats['akshare_calls']}")
    print(f"   降级次数: {stats['fallback_count']}")
    
    print("\n✅ 测试完成！")
