#!/bin/bash
# CIO Awakening v2.1 - Pre-Market Analysis Cron Job
# 盘前分析定时任务 - 每日09:15运行

WORKSPACE="/workspace/projects/workspace"
CIO_DIR="$WORKSPACE/A5L_v2.1_DEV/cio_awakening"
LOG_DIR="$CIO_DIR/logs"
RESULT_DIR="$CIO_DIR/results"

# 创建日志目录
mkdir -p "$LOG_DIR"
mkdir -p "$RESULT_DIR"

# 日志文件
LOG_FILE="$LOG_DIR/pre_market_$(date +%Y%m%d).log"

echo "==============================================" >> "$LOG_FILE"
echo "CIO Awakening v2.1 - Pre-Market Analysis" >> "$LOG_FILE"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "==============================================" >> "$LOG_FILE"

# 切换到工作目录
cd "$CIO_DIR"

# 运行盘前分析
echo "Running pre-market analysis..." >> "$LOG_FILE"
python3 cio_system_v21.py >> "$LOG_FILE" 2>&1

# 检查结果
if [ -f "$RESULT_DIR/pre_market_signal_v21.json" ]; then
    echo "✅ Analysis completed successfully" >> "$LOG_FILE"
    
    # 发送飞书通知 (通过OpenClaw)
    SIGNAL_FILE="$RESULT_DIR/pre_market_signal_v21.json"
    
    # 提取关键信息生成飞书消息
    echo "Sending Feishu notification..." >> "$LOG_FILE"
    
    # 使用OpenClaw发送消息
    # Note: This will be handled by the main system
    
else
    echo "❌ Analysis failed - no output file" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "Done at $(date '+%H:%M:%S')" >> "$LOG_FILE"
echo "==============================================" >> "$LOG_FILE"
