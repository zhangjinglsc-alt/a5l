#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L 交易日历系统
自动检测A股休市日（周末+节假日）
"""

from datetime import datetime, timedelta
from typing import List, Set, Tuple
import calendar

class TradingCalendar:
    """A股交易日历"""
    
    def __init__(self):
        # 2026年A股休市日期 (周末+节假日)
        self.holidays_2026 = self._load_holidays_2026()
        
    def _load_holidays_2026(self) -> Set[str]:
        """加载2026年休市日期"""
        holidays = set()
        
        # 元旦: 1月1日-1月2日
        holidays.update(["2026-01-01", "2026-01-02"])
        
        # 春节: 2月17日-2月25日
        for i in range(17, 26):
            holidays.add(f"2026-02-{i:02d}")
        
        # 清明节: 4月4日-4月6日
        holidays.update(["2026-04-04", "2026-04-05", "2026-04-06"])
        
        # 劳动节: 5月1日-5月5日 ⚠️ 今天在这范围内！
        for i in range(1, 6):
            holidays.add(f"2026-05-{i:02d}")
        
        # 端午节: 6月19日-6月21日
        holidays.update(["2026-06-19", "2026-06-20", "2026-06-21"])
        
        # 中秋节+国庆节: 9月30日-10月7日
        for i in range(30, 32):
            holidays.add(f"2026-09-{i}")
        for i in range(1, 8):
            holidays.add(f"2026-10-{i:02d}")
        
        return holidays
    
    def is_trading_day(self, date: datetime = None) -> bool:
        """
        判断是否为交易日
        
        Returns:
            True: 交易日
            False: 休市日(周末或节假日)
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        weekday = date.weekday()  # 0=周一, 6=周日
        
        # 检查周末
        if weekday >= 5:  # 周六或周日
            return False
        
        # 检查节假日
        if date_str in self.holidays_2026:
            return False
        
        return True
    
    def get_trading_hours(self) -> Tuple[str, str]:
        """
        获取交易时间
        
        Returns:
            (开盘时间, 收盘时间) HH:MM格式
        """
        return ("09:30", "15:00")
    
    def is_trading_hours(self, time: datetime = None) -> bool:
        """
        判断当前是否在交易时段内
        
        A股交易时间:
        - 上午: 09:30 - 11:30
        - 下午: 13:00 - 15:00
        """
        if time is None:
            time = datetime.now()
        
        if not self.is_trading_day(time):
            return False
        
        hour = time.hour
        minute = time.minute
        current_time = hour * 60 + minute
        
        # 上午交易时段: 09:30 - 11:30
        morning_start = 9 * 60 + 30
        morning_end = 11 * 60 + 30
        
        # 下午交易时段: 13:00 - 15:00
        afternoon_start = 13 * 60
        afternoon_end = 15 * 60
        
        return (morning_start <= current_time <= morning_end) or \
               (afternoon_start <= current_time <= afternoon_end)
    
    def get_next_trading_day(self, date: datetime = None) -> datetime:
        """获取下一个交易日"""
        if date is None:
            date = datetime.now()
        
        next_day = date + timedelta(days=1)
        while not self.is_trading_day(next_day):
            next_day += timedelta(days=1)
        
        return next_day
    
    def get_market_status(self) -> dict:
        """获取当前市场状态"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        
        is_trading_day = self.is_trading_day(now)
        is_trading_hours = self.is_trading_hours(now) if is_trading_day else False
        
        if not is_trading_day:
            next_trading_day = self.get_next_trading_day(now)
            status = "closed"
            message = f"今日休市 ({date_str})，下一交易日: {next_trading_day.strftime('%Y-%m-%d')}"
        elif not is_trading_hours:
            status = "closed"
            message = f"非交易时段 ({time_str})，交易时间: 09:30-11:30, 13:00-15:00"
        else:
            status = "open"
            message = f"交易中 ({time_str})"
        
        return {
            "date": date_str,
            "time": time_str,
            "is_trading_day": is_trading_day,
            "is_trading_hours": is_trading_hours,
            "status": status,
            "message": message,
            "next_trading_day": self.get_next_trading_day(now).strftime("%Y-%m-%d") if not is_trading_day else None
        }
    
    def validate_trade(self) -> Tuple[bool, str]:
        """
        验证是否可以执行交易
        
        Returns:
            (是否可以交易, 原因)
        """
        status = self.get_market_status()
        
        if status["status"] == "open":
            return True, "市场开放，可以交易"
        else:
            return False, status["message"]


def check_today_market():
    """检查今日市场状态"""
    calendar = TradingCalendar()
    status = calendar.get_market_status()
    
    print("=" * 60)
    print("📅 A股市场状态检查")
    print("=" * 60)
    print(f"日期: {status['date']}")
    print(f"时间: {status['time']}")
    print(f"是否交易日: {'✅ 是' if status['is_trading_day'] else '❌ 否'}")
    print(f"是否交易时段: {'✅ 是' if status['is_trading_hours'] else '⏸️ 否'}")
    print()
    
    if status['status'] == 'open':
        print("🟢 市场状态: 交易中")
    else:
        print(f"🔴 市场状态: 休市")
        print(f"原因: {status['message']}")
    
    print()
    
    # 验证交易
    can_trade, reason = calendar.validate_trade()
    print(f"交易验证: {'✅ 可以交易' if can_trade else '❌ 不可交易'}")
    print(f"原因: {reason}")
    
    print("=" * 60)
    
    return can_trade


if __name__ == "__main__":
    check_today_market()
