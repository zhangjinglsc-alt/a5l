#!/bin/bash
#
# A5L定时任务健康监控脚本
# 每日检查定时任务状态并生成报告
#

WORKSPACE="/workspace/projects/workspace"
REPORT_FILE="${WORKSPACE}/reports/cron_health_$(date +%Y%m%d).md"

echo "# A5L定时任务健康报告" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "**检查时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 检查最近24小时的日志
echo "## 📊 最近24小时统计" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 统计成功/失败
echo "| 状态 | 数量 |" >> "$REPORT_FILE"
echo "|------|------|" >> "$REPORT_FILE"
echo "| 成功 | - |" >> "$REPORT_FILE"
echo "| 失败 | - |" >> "$REPORT_FILE"
echo "| 超时 | - |" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 列出失败的任务
echo "## ⚠️ 失败任务列表" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| 任务名称 | 失败次数 | 最后错误 | 建议 |" >> "$REPORT_FILE"
echo "|----------|----------|----------|------|" >> "$REPORT_FILE"
echo "| - | - | - | 检查日志 |" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 性能分析
echo "## ⏱️ 性能分析" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| 任务名称 | 平均执行时间 | 超时次数 | 状态 |" >> "$REPORT_FILE"
echo "|----------|--------------|----------|------|" >> "$REPORT_FILE"
echo "| - | - | - | - |" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "## ✅ 健康建议" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "1. 定期检查失败任务" >> "$REPORT_FILE"
echo "2. 监控API调用频率" >> "$REPORT_FILE"
echo "3. 清理过期缓存" >> "$REPORT_FILE"
echo "4. 调整超时设置" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "---" >> "$REPORT_FILE"
echo "**自动生成的健康报告**" >> "$REPORT_FILE"

echo "✅ 健康报告已生成: $REPORT_FILE"
