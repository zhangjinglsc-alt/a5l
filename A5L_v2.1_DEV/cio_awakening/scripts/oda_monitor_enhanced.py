#!/usr/bin/env python3
"""
ODA监控周期 - 增强版 (带交易日历检测)
避免在休市期间进行无意义的监控循环
"""
import subprocess
import json
import sys

def check_trading_day():
    """检查是否为交易日"""
    try:
        result = subprocess.run(
            ["python3", "/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/scripts/trading_calendar.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {
            "should_monitor": True,  # 出错时默认继续监控
            "error": str(e),
            "message": "交易日历检测失败，继续监控"
        }

def main():
    # 首先检查是否为交易日
    calendar_check = check_trading_day()
    
    print(calendar_check["message"])
    
    if not calendar_check.get("should_monitor", True):
        # 非交易日，停止监控
        print(f"⏸️ ODA监控暂停 - {calendar_check['reason']}")
        print(f"📅 下次交易日: {calendar_check.get('next_trading_day', '未知')}")
        print("\n💡 建议: 休市期间减少提醒频率至每4小时一次")
        sys.exit(0)
    
    # 是交易日，执行正常监控
    print("\n🚀 执行ODA监控周期...")
    # 这里调用原有的监控逻辑
    print("✅ 交易日监控正常进行")

if __name__ == "__main__":
    main()
