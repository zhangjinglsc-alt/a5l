#!/usr/bin/env python3
"""
A5L 浪主预测系统 - 每日总结报告
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/workspace/projects/workspace/skills/langzhu-wave-predictor/data")
LOGS_DIR = Path("/workspace/projects/workspace/skills/langzhu-wave-predictor/logs")

def generate_daily_summary(date: str = None):
    """生成每日总结报告"""
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    db_path = DATA_DIR / "predictions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取今日所有预测
    cursor.execute('''
        SELECT * FROM predictions 
        WHERE date(timestamp) = ?
        ORDER BY timestamp
    ''', (date,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"今日({date})暂无预测记录")
        return
    
    # 统计分析
    total = len(rows)
    verified = sum(1 for r in rows if r[18])  # verified字段
    correct = sum(1 for r in rows if r[19] == 'correct')
    
    avg_confidence = sum(r[16] for r in rows) / total if total > 0 else 0
    avg_accuracy = sum(r[20] for r in rows if r[20] is not None) / verified if verified > 0 else 0
    
    # 生成报告
    report = f"""# 🌊 浪主波浪理论预测日报

## 📅 日期: {date}

## 📊 统计概览

| 指标 | 数值 |
|:-----|:-----|
| 总预测数 | {total} |
| 已验证 | {verified} |
| 正确数 | {correct} |
| 准确率 | {correct/verified*100:.1f}% (验证样本) |
| 平均置信度 | {avg_confidence*100:.1f}% |
| 平均准确度 | {avg_accuracy*100:.1f}% |

## 📈 详细记录

| 时间 | 时段 | 预测 | 置信度 | 验证结果 | 准确度 |
|:-----|:-----|:-----|:-------|:---------|:-------|
"""
    
    for row in rows:
        time_str = row[1].split()[1][:5]  # HH:MM
        session = '早盘' if row[2] == 'morning' else '午盘'
        pred = {'up': '看涨', 'down': '看跌', 'consolidation': '震荡'}.get(row[15], row[15])
        confidence = f"{row[16]*100:.0f}%"
        result = '✅正确' if row[19] == 'correct' else ('❌错误' if row[19] == 'wrong' else '⏳待验证')
        accuracy = f"{row[20]*100:.0f}%" if row[20] else '-'
        
        report += f"| {time_str} | {session} | {pred} | {confidence} | {result} | {accuracy} |\n"
    
    report += f"""

## 🎯 关键点位跟踪

"""
    
    # 提取最新的关键点位
    latest = rows[-1]
    report += f"""```
阻力位:   {latest[8]:.2f}
    ↑
最新价:   {latest[11]:.2f}
    ↓
支撑1:    {latest[9]:.2f} (长4浪)
    ↓
支撑2:    {latest[10]:.2f} (4浪)
```

## 💡 学习洞察

"""
    
    # 简单洞察
    if verified > 0:
        if correct / verified >= 0.7:
            report += "- 今日预测准确率较好，模型表现稳定\n"
        elif correct / verified >= 0.5:
            report += "- 今日预测准确率一般，需要关注边界条件\n"
        else:
            report += "- 今日预测准确率偏低，建议回顾分析逻辑\n"
    
    report += f"""

## 📝 明日关注

- 观察时间周期是否超过23个15分钟
- 关注4143.56支撑位是否跌破
- 留意国家队行为模式（钝化消失/过度延伸）

---
*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存报告
    report_file = LOGS_DIR / f"daily_summary_{date}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print(f"\n报告已保存: {report_file}")

if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else None
    generate_daily_summary(date)
