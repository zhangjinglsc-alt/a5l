#!/usr/bin/env python3
"""
ODA交易日历检测模块
防止在非交易日进行无意义的监控
"""
import datetime
import json

# 2026年A股休市安排（部分）
HOLIDAYS_2026 = [
    "2026-01-01",  # 元旦
    "2026-01-02",  # 元旦调休
    "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",  # 春节
    "2026-04-04", "2026-04-05", "2026-04-06",  # 清明
    "2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04", "2026-05-05",  # 五一
    "2026-06-19", "2026-06-20", "2026-06-21",  # 端午
    # ... 更多节假日
]

def is_trading_day(date=None):
    """判断是否为A股交易日"""
    if date is None:
        date = datetime.datetime.now()
    
    date_str = date.strftime("%Y-%m-%d")
    weekday = date.weekday()  # 0=周一, 6=周日
    
    # 周末休市
    if weekday >= 5:  # 周六或周日
        return False, "周末休市"
    
    # 节假日休市
    if date_str in HOLIDAYS_2026:
        return False, f"节假日休市 ({date_str})"
    
    return True, "交易日"

def get_next_trading_day():
    """获取下一个交易日"""
    date = datetime.datetime.now() + datetime.timedelta(days=1)
    while True:
        is_trading, reason = is_trading_day(date)
        if is_trading:
            return date
        date += datetime.timedelta(days=1)

def check_before_monitoring():
    """监控前检查 - 非交易日直接退出"""
    is_trading, reason = is_trading_day()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if not is_trading:
        next_trading = get_next_trading_day()
        return {
            "should_monitor": False,
            "today": today,
            "reason": reason,
            "next_trading_day": next_trading.strftime("%Y-%m-%d"),
            "message": f"📅 今日({today}){reason}，暂停监控。下次交易日: {next_trading.strftime('%Y-%m-%d')}"
        }
    
    return {
        "should_monitor": True,
        "today": today,
        "reason": reason,
        "message": f"📅 今日({today}){reason}，正常监控"
    }

if __name__ == "__main__":
    result = check_before_monitoring()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if not result["should_monitor"]:
        exit(0)  # 非交易日，退出
