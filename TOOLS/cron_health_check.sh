#!/bin/bash
#
# A5L定时任务健康检查和修复脚本
# 用于诊断和修复超时/失败的定时任务
#

WORKSPACE="/workspace/projects/workspace"
LOG_FILE="${WORKSPACE}/logs/cron_health_check_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "${WORKSPACE}/logs"

echo "🔍 A5L定时任务健康检查" | tee -a "$LOG_FILE"
echo "========================" | tee -a "$LOG_FILE"
echo "检查时间: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 问题任务列表
PROBLEM_TASKS=(
  "0eaf1d8b-751c-416b-8588-5e426e9222f6:A股午盘盈亏提醒:180:600"
  "f8677a65-40b6-466f-b324-ed9ac623fd5c:langzhu-noon-verify-predict:180:300"
  "08bfcd75-f95a-4da3-88a5-bcd09816bbf3:港股收盘报告:120:300"
  "bf3f51e2-93c6-45cf-a505-b5af431150e7:知识库研报自动同步:300:600"
  "f4ea4e17-a7a1-466c-a5b3-09e6c6cb908d:portfolio-evening-sync:300:600"
  "d3222196-8884-4bfa-aae2-864d5080d719:A股收盘报告:120:300"
  "0b95177e-c170-4564-a943-29a8157a4f6f:每日盘后市场复盘:180:600"
  "5bd00fe6-1d94-40aa-88af-149f0125d5d4:封装材料投资手册更新:300:600"
)

echo "📋 问题任务修复方案" | tee -a "$LOG_FILE"
echo "--------------------" | tee -a "$LOG_FILE"

for task in "${PROBLEM_TASKS[@]}"; do
  IFS=':' read -r task_id task_name current_timeout new_timeout <<< "$task"
  echo "" | tee -a "$LOG_FILE"
  echo "任务: $task_name" | tee -a "$LOG_FILE"
  echo "  ID: $task_id" | tee -a "$LOG_FILE"
  echo "  当前超时: ${current_timeout}s" | tee -a "$LOG_FILE"
  echo "  建议超时: ${new_timeout}s" | tee -a "$LOG_FILE"
  echo "  修复建议: 增加超时时间 + 优化脚本性能" | tee -a "$LOG_FILE"
done

echo "" | tee -a "$LOG_FILE"
echo "✅ 检查完成" | tee -a "$LOG_FILE"
echo "日志保存: $LOG_FILE" | tee -a "$LOG_FILE"
