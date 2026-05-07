#!/bin/bash
# Catalyst Monitor Auto - 定时任务脚本
# 每30分钟执行一次完整扫描

cd /workspace/projects/workspace

# 记录日志
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动催化事件监控扫描..." >> logs/catalyst_monitor.log

# 执行监控扫描
python3 skills/catalyst-monitor-auto/scripts/monitor.py scan >> logs/catalyst_monitor.log 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 扫描完成" >> logs/catalyst_monitor.log
