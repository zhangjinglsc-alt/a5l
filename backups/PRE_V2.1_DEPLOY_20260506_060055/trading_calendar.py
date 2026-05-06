#!/usr/bin/env python3
"""
A5L 交易日历检查工具
统一检查A股/港股/美股是否为交易日
"""

from datetime import datetime
import akshare as ak
import pandas as pd

# A股节假日（2026年）
CN_HOLIDAYS_2026 = [
    '2026-01-01', '2026-01-02', '2026-01-03',  # 元旦
    '2026-02-16', '2026-02-17', '2026-02-18', '2026-02-19', '2026-02-20', '2026-02-21', '2026-02-22',  # 春节
    '2026-04-04', '2026-04-05', '2026-04-06',  # 清明
    '2026-05-01', '2026-05-02', '2026-05-03', '2026-05-04', '2026-05-05',  # 五一
    '2026-06-19', '2026-06-20', '2026-06-21',  # 端午
    '2026-09-26', '2026-09-27',  # 中秋调休
    '2026-10-01', '2026-10-02', '2026-10-03', '2026-10-04', '2026-10-05', '2026-10-06', '2026-10-07', '2026-10-08',  # 国庆
]

# 港股节假日（2026年）
HK_HOLIDAYS_2026 = [
    '2026-01-01', '2026-02-17', '2026-02-18', '2026-02-19', '2026-02-20',
    '2026-04-03', '2026-04-04', '2026-04-06', '2026-05-01', '2026-05-15',
    '2026-06-19', '2026-07-01', '2026-09-28', '2026-10-01', '2026-10-02',
    '2026-10-21', '2026-12-25', '2026-12-26'
]

# 美股节假日（2026年）
US_HOLIDAYS_2026 = [
    '2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25',
    '2026-07-03', '2026-09-07', '2026-11-26', '2026-12-25'
]


def is_cn_trading_day(date_str: str = None) -> bool:
    """
    检查是否为A股交易日
    
    Args:
        date_str: 日期字符串 'YYYY-MM-DD'，默认为今天
    
    Returns:
        bool: 是否为交易日
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    date = datetime.strptime(date_str, '%Y-%m-%d')
    
    # 周末非交易日
    if date.weekday() >= 5:  # 5=周六, 6=周日
        return False
    
    # 节假日非交易日
    if date_str in CN_HOLIDAYS_2026:
        return False
    
    return True


def is_hk_trading_day(date_str: str = None) -> bool:
    """检查是否为港股交易日"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    date = datetime.strptime(date_str, '%Y-%m-%d')
    
    if date.weekday() >= 5:
        return False
    
    if date_str in HK_HOLIDAYS_2026:
        return False
    
    return True


def is_us_trading_day(date_str: str = None) -> bool:
    """检查是否为美股交易日"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    date = datetime.strptime(date_str, '%Y-%m-%d')
    
    if date.weekday() >= 5:
        return False
    
    if date_str in US_HOLIDAYS_2026:
        return False
    
    return True


def check_trading_day(market: str = 'CN', date_str: str = None) -> bool:
    """
    统一检查交易日接口
    
    Args:
        market: 'CN'(A股), 'HK'(港股), 'US'(美股)
        date_str: 日期字符串，默认今天
    
    Returns:
        bool: 是否为交易日
    """
    market = market.upper()
    
    if market == 'CN':
        return is_cn_trading_day(date_str)
    elif market == 'HK':
        return is_hk_trading_day(date_str)
    elif market == 'US':
        return is_us_trading_day(date_str)
    else:
        raise ValueError(f"未知市场: {market}")


def get_next_trading_day(market: str = 'CN', date_str: str = None) -> str:
    """获取下一个交易日"""
    if date_str is None:
        date = datetime.now()
    else:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    
    # 从明天开始查找
    next_day = date + pd.Timedelta(days=1)
    
    while not check_trading_day(market, next_day.strftime('%Y-%m-%d')):
        next_day += pd.Timedelta(days=1)
    
    return next_day.strftime('%Y-%m-%d')


def assert_trading_day(market: str = 'CN', msg: str = None):
    """
    断言今天是交易日，如果不是则抛出异常
    用于cron任务开头的强制检查
    
    Args:
        market: 市场代码
        msg: 自定义错误消息
    """
    if not check_trading_day(market):
        today = datetime.now().strftime('%Y-%m-%d')
        if msg is None:
            msg = f"⚠️ {today} 非{market}交易日，任务跳过执行"
        print(msg)
        exit(0)


if __name__ == "__main__":
    # 测试
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"今天: {today}")
    print(f"A股交易日: {is_cn_trading_day()}")
    print(f"港股交易日: {is_hk_trading_day()}")
    print(f"美股交易日: {is_us_trading_day()}")
    print(f"下一个A股交易日: {get_next_trading_day('CN')}")
