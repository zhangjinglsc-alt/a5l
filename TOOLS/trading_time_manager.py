#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Time Manager
交易时间管理系统

功能：
1. 管理三大市场交易时间
2. 检查当前是否在交易时间
3. 获取下一个交易时段
4. 处理节假日
"""

from datetime import datetime, time, timedelta
from typing import Dict, Tuple, Optional
import pytz

class TradingTimeManager:
    """交易时间管理器"""
    
    def __init__(self):
        # 设置时区
        self.tz_cn = pytz.timezone('Asia/Shanghai')
        self.tz_hk = pytz.timezone('Asia/Hong_Kong')
        self.tz_us = pytz.timezone('America/New_York')
        
        # 交易时间配置
        self.trading_hours = {
            "CN": {
                "name": "A股",
                "timezone": "Asia/Shanghai",
                "sessions": [
                    (time(9, 30), time(11, 30)),  # 上午
                    (time(13, 0), time(15, 0))    # 下午
                ],
                "weekdays": [0, 1, 2, 3, 4],  # 周一到周五
                "holidays": self._get_cn_holidays()
            },
            "HK": {
                "name": "港股",
                "timezone": "Asia/Hong_Kong",
                "sessions": [
                    (time(9, 30), time(12, 0)),   # 上午
                    (time(13, 0), time(16, 0))    # 下午
                ],
                "weekdays": [0, 1, 2, 3, 4],
                "holidays": self._get_hk_holidays()
            },
            "US": {
                "name": "美股",
                "timezone": "America/New_York",
                "sessions": [
                    (time(9, 30), time(16, 0))    # 连续交易
                ],
                "weekdays": [0, 1, 2, 3, 4],
                "holidays": self._get_us_holidays()
            }
        }
    
    def _get_cn_holidays(self) -> list:
        """获取中国A股节假日（2026年）"""
        return [
            "2026-01-01",  # 元旦
            "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",  # 春节
            "2026-04-05", "2026-04-06", "2026-04-07",  # 清明
            "2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04", "2026-05-05",  # 五一
            "2026-06-19", "2026-06-20", "2026-06-21",  # 端午
            "2026-09-24", "2026-09-25", "2026-09-26", "2026-09-27",  # 中秋国庆
        ]
    
    def _get_hk_holidays(self) -> list:
        """获取港股节假日（2026年）"""
        return [
            "2026-01-01",  # 元旦
            "2026-02-16", "2026-02-17",  # 春节
            "2026-04-03", "2026-04-06",  # 耶稣受难节/复活节
            "2026-05-01",  # 劳动节
            "2026-06-19",  # 端午
            "2026-07-01",  # 香港回归
            "2026-09-28",  # 中秋
            "2026-10-01",  # 国庆
            "2026-12-25",  # 圣诞
        ]
    
    def _get_us_holidays(self) -> list:
        """获取美股节假日（2026年）"""
        return [
            "2026-01-01",   # New Year
            "2026-01-19",   # MLK Day
            "2026-02-16",   # Presidents Day
            "2026-04-03",   # Good Friday
            "2026-05-25",   # Memorial Day
            "2026-07-03",   # Independence Day (observed)
            "2026-09-07",   # Labor Day
            "2026-11-26",   # Thanksgiving
            "2026-12-25",   # Christmas
        ]
    
    def is_trading_time(self, market: str, dt: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        检查是否在交易时间
        
        Returns:
            (is_trading: bool, message: str)
        """
        if dt is None:
            dt = datetime.now()
        
        config = self.trading_hours.get(market)
        if not config:
            return False, f"未知市场: {market}"
        
        # 转换到市场本地时间
        tz = pytz.timezone(config['timezone'])
        local_dt = dt.astimezone(tz)
        date_str = local_dt.strftime('%Y-%m-%d')
        current_time = local_dt.time()
        weekday = local_dt.weekday()
        
        # 检查节假日
        if date_str in config['holidays']:
            next_trading = self._get_next_trading_day(market, local_dt)
            return False, f"{config['name']}节假日休市，下次交易: {next_trading}"
        
        # 检查周末
        if weekday not in config['weekdays']:
            next_trading = self._get_next_trading_day(market, local_dt)
            return False, f"{config['name']}周末休市，下次交易: {next_trading}"
        
        # 检查交易时段
        for start, end in config['sessions']:
            if start <= current_time <= end:
                session_name = "上午" if start.hour < 12 else "下午"
                return True, f"{config['name']}{session_name}交易中"
        
        # 非交易时段
        next_session = self._get_next_session(market, local_dt)
        return False, f"{config['name']}非交易时段，下次交易: {next_session}"
    
    def _get_next_trading_day(self, market: str, from_dt: datetime) -> str:
        """获取下一个交易日"""
        config = self.trading_hours[market]
        current = from_dt + timedelta(days=1)
        
        for _ in range(10):  # 最多查10天
            date_str = current.strftime('%Y-%m-%d')
            if current.weekday() in config['weekdays'] and date_str not in config['holidays']:
                session_start = config['sessions'][0][0]
                return f"{date_str} {session_start.strftime('%H:%M')}"
            current += timedelta(days=1)
        
        return "未知"
    
    def _get_next_session(self, market: str, from_dt: datetime) -> str:
        """获取下一个交易时段"""
        config = self.trading_hours[market]
        current_time = from_dt.time()
        date_str = from_dt.strftime('%Y-%m-%d')
        
        # 检查当天后续时段
        for start, end in config['sessions']:
            if current_time < start:
                return f"今天 {start.strftime('%H:%M')}"
        
        # 下一个交易日
        return self._get_next_trading_day(market, from_dt)
    
    def get_all_markets_status(self) -> Dict:
        """获取所有市场状态"""
        now = datetime.now()
        status = {}
        
        for market in ["CN", "HK", "US"]:
            is_trading, message = self.is_trading_time(market, now)
            status[market] = {
                "trading": is_trading,
                "message": message
            }
        
        return status
    
    def check_before_trade(self, market: str) -> Tuple[bool, str]:
        """
        交易前检查
        返回: (是否可以交易, 消息)
        """
        is_trading, message = self.is_trading_time(market)
        
        if not is_trading:
            return False, f"⏸️ 暂停交易: {message}"
        
        return True, f"✅ {message}"

def main():
    """演示"""
    manager = TradingTimeManager()
    
    print("=" * 70)
    print("⏰ 交易时间管理系统")
    print("=" * 70)
    
    now = datetime.now()
    print(f"\n当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    status = manager.get_all_markets_status()
    for market, info in status.items():
        icon = "🟢" if info["trading"] else "🔴"
        print(f"{icon} {market}: {info['message']}")
    
    print("\n" + "=" * 70)
    
    # 测试交易检查
    print("\n交易前检查:")
    for market in ["CN", "HK", "US"]:
        can_trade, msg = manager.check_before_trade(market)
        print(f"  {market}: {msg}")

if __name__ == "__main__":
    main()
