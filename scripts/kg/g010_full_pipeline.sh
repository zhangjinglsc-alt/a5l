#!/bin/bash
#
# A5L G010 完整工作流 - 从研报到投资信号
# Goal G010 全步骤统一入口
#
# 使用: ./scripts/kg/g010_full_pipeline.sh [--daemon]

set -e

WORKSPACE="/workspace/projects/workspace"
LOG_FILE="${WORKSPACE}/logs/g010_pipeline.log"

# 确保日志目录存在
mkdir -p $(dirname $LOG_FILE)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

echo "============================================================"
echo "A5L G010 知识图谱驱动投资决策系统"
echo "完整工作流执行"
echo "============================================================"
log "工作流启动"

# Step 1.1: 研报监控
echo ""
echo "[Step 1.1] 研报监控扫描..."
python3 ${WORKSPACE}/scripts/feishu/report_monitor.py 2>&1 | tee -a $LOG_FILE
echo ""

# Step 1.2: 下载与预处理
echo "[Step 1.2] 研报下载与预处理..."
python3 ${WORKSPACE}/scripts/kg/report_processor.py 2>&1 | tee -a $LOG_FILE
echo ""

# Step 1.3: 实体提取
echo "[Step 1.3] 实体自动提取..."
python3 ${WORKSPACE}/scripts/kg/auto_entity_extractor.py 2>&1 | tee -a $LOG_FILE
echo ""

# Step 2: 隐藏关系发现
echo "[Step 2] 隐藏关系发现..."
python3 ${WORKSPACE}/scripts/kg/hidden_relation_finder.py 2>&1 | tee -a $LOG_FILE
echo ""

# Step 3: 投资信号生成
echo "[Step 3] 投资信号生成..."
python3 ${WORKSPACE}/scripts/kg/signal_generator.py 2>&1 | tee -a $LOG_FILE
echo ""

# Step 4: 闭环归档
echo "[Step 4] 闭环归档..."
python3 ${WORKSPACE}/scripts/kg/signal_archiver.py 2>&1 | tee -a $LOG_FILE
echo ""

echo "============================================================"
echo "✅ G010 完整工作流执行完成"
echo "============================================================"
log "工作流完成"
echo ""
echo "说明:"
echo "  - 当有新的研报到飞书时，上述流程会自动处理"
echo "  - 从研报→实体→关系→信号→归档的完整闭环"
echo "  - 可设置cron定时执行此脚本"
echo ""
