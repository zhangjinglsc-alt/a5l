#!/bin/bash
# A5L 月度SKILL审计 - 自动设置脚本

echo "========================================"
echo "📅 设置A5L月度SKILL审计"
echo "========================================"

# 创建日志目录
mkdir -p /workspace/projects/workspace/logs

# 添加到crontab
crontab -l > /tmp/current_crontab 2>/dev/null || true

# 检查是否已存在
if grep -q "skill_lifecycle_manager.py" /tmp/current_crontab; then
    echo "✅ CRON任务已存在，跳过设置"
else
    echo "" >> /tmp/current_crontab
    echo "# A5L Monthly SKILL Audit - 每月第一个周日9:00" >> /tmp/current_crontab
    echo "0 9 1-7 * 0 cd /workspace/projects/workspace && python3 ARCHITECT_5L/layer0_control/skill_lifecycle_manager.py >> logs/monthly_audit.log 2>&1" >> /tmp/current_crontab
    
    crontab /tmp/current_crontab
    echo "✅ CRON任务已添加"
fi

# 显示当前crontab
echo ""
echo "📋 当前CRON任务:"
crontab -l | grep -A1 "A5L Monthly" || echo "未找到"

echo ""
echo "========================================"
echo "✅ 设置完成！"
echo "下次审计: $(date -d 'next month' +%Y年%m月)第一个周日 09:00"
echo "========================================"
