#!/bin/bash
# Catalyst Monitor Auto - 日报生成脚本
# 每日17:30执行

cd /workspace/projects/workspace

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 生成催化事件日报..." >> logs/catalyst_monitor.log

# 生成日报
python3 skills/catalyst-monitor-auto/scripts/monitor.py daily-report >> logs/catalyst_monitor.log 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日报生成完成" >> logs/catalyst_monitor.log
