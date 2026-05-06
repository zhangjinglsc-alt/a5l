#!/usr/bin/env python3
"""
重要事件日检测与频率调整工具
检测美联储利率决议、非农就业数据、CPI、期权到期日等关键事件
"""

import datetime
import json
import os

# 配置目录
CONFIG_DIR = "/workspace/projects/workspace/config"
STATE_FILE = os.path.join(CONFIG_DIR, "event_day_state.json")

def ensure_config_dir():
    """确保配置目录存在"""
    os.makedirs(CONFIG_DIR, exist_ok=True)

def is_nth_weekday(year, month, n, weekday):
    """
    判断某月的第n个星期几是几号
    weekday: 0=周一, 1=周二, ..., 6=周日
    """
    # 获取该月第一天
    first_day = datetime.date(year, month, 1)
    # 找到第一个目标星期几
    days_until_weekday = (weekday - first_day.weekday()) % 7
    first_occurrence = first_day + datetime.timedelta(days=days_until_weekday)
    # 计算第n个
    nth_date = first_occurrence + datetime.timedelta(weeks=n-1)
    return nth_date

def get_third_friday(year, month):
    """获取某月的第3个周五（期权到期日）"""
    return is_nth_weekday(year, month, 3, 4)  # 4=周五

def get_first_friday(year, month):
    """获取某月的第1个周五（非农就业数据）"""
    return is_nth_weekday(year, month, 1, 4)

def get_second_wednesday(year, month):
    """获取某月的第2个周三（CPI数据）"""
    return is_nth_weekday(year, month, 2, 2)  # 2=周三

def get_third_wednesday(year, month):
    """获取某月的第3个周三（FOMC利率决议）"""
    return is_nth_weekday(year, month, 3, 2)

def detect_event_days(year, month):
    """检测某月的所有重要事件日"""
    events = {
        "NFP": get_first_friday(year, month),  # 非农就业
        "CPI": get_second_wednesday(year, month),  # CPI数据
        "FOMC": get_third_wednesday(year, month),  # 美联储利率决议
        "OPEX": get_third_friday(year, month),  # 期权到期日
    }
    return events

def check_today_events():
    """检查今天是否是重要事件日"""
    today = datetime.date.today()
    # today = datetime.date(2026, 5, 1)  # 调试用
    
    events = detect_event_days(today.year, today.month)
    
    today_events = []
    for event_type, event_date in events.items():
        if event_date == today:
            today_events.append(event_type)
    
    return today, today_events, events

def determine_frequency(event_count):
    """根据事件数量确定采集频率"""
    if event_count == 0:
        return 120, "常规监控"  # 每2小时
    elif event_count == 1:
        return 30, "重要事件日监控"  # 每30分钟
    else:
        return 15, "超级事件日监控"  # 每15分钟

def save_state(today, events, freq_minutes, mode):
    """保存当前状态"""
    ensure_config_dir()
    state = {
        "date": today.isoformat(),
        "events": events,
        "frequency_minutes": freq_minutes,
        "mode": mode,
        "updated_at": datetime.datetime.now().isoformat(),
        "next_reset": (today + datetime.timedelta(days=1)).isoformat() + "T06:00:00"
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    return state

def load_state():
    """加载上次保存的状态"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def format_event_name(event_type):
    """格式化事件名称"""
    names = {
        "NFP": "📊 非农就业数据",
        "CPI": "📈 CPI通胀数据",
        "FOMC": "🏦 美联储利率决议",
        "OPEX": "📉 期权到期日"
    }
    return names.get(event_type, event_type)

def format_events_list(events):
    """格式化事件列表"""
    if not events:
        return "无"
    return "、".join([format_event_name(e) for e in events])

def main():
    print("=" * 60)
    print("🗓️  重要事件日智能检测")
    print("=" * 60)
    print()
    
    # 检查今天的事件
    today, today_events, month_events = check_today_events()
    
    print(f"📅 当前日期: {today.strftime('%Y年%m月%d日')} ({['周一','周二','周三','周四','周五','周六','周日'][today.weekday()]})")
    print()
    
    # 显示本月事件日历
    print("📋 本月重要事件日历:")
    for event_type, event_date in month_events.items():
        marker = " ⭐ TODAY" if event_date == today else ""
        print(f"   • {format_event_name(event_type)}: {event_date.strftime('%m月%d日')}{marker}")
    print()
    
    # 判断频率
    event_count = len(today_events)
    freq_minutes, mode = determine_frequency(event_count)
    
    # 保存状态
    state = save_state(today, today_events, freq_minutes, mode)
    
    # 输出结果
    if event_count == 0:
        print("✅ 检测结果: 普通交易日")
        print(f"📊 采集频率: 每{freq_minutes}分钟")
        print("📝 说明: 常规市场监控模式")
    elif event_count == 1:
        print(f"⚠️  检测结果: 重要事件日")
        print(f"📢 今日事件: {format_events_list(today_events)}")
        print(f"📊 采集频率: 每{freq_minutes}分钟")
        print("📝 说明: 重要数据发布，提高监控频率")
    else:
        print(f"🚨 检测结果: 超级事件日")
        print(f"📢 今日事件: {format_events_list(today_events)}")
        print(f"📊 采集频率: 每{freq_minutes}分钟")
        print("📝 说明: 多重事件叠加，启用高频监控")
    
    print()
    print("💾 状态已保存至:", STATE_FILE)
    print("🔄 次日06:00后将自动恢复常规频率")
    print("=" * 60)
    
    # 返回JSON格式的结果（供外部调用使用）
    result = {
        "today": today.isoformat(),
        "is_event_day": event_count > 0,
        "is_super_event_day": event_count > 1,
        "events": today_events,
        "frequency_minutes": freq_minutes,
        "mode": mode
    }
    
    return result

if __name__ == "__main__":
    result = main()
    print()
    print("JSON_OUTPUT:", json.dumps(result, ensure_ascii=False))
