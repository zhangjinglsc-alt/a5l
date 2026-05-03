#!/bin/bash
#
# A5L G010 研报自动处理工作流
# Goal G010 Step 1 All - 统一入口
#
# 使用: ./scripts/kg/g010_report_pipeline.sh

set -e

echo "============================================================"
echo "A5L G010 研报自动处理工作流"
echo "============================================================"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

WORKSPACE="/workspace/projects/workspace"

echo "[Step 1.1] 研报监控扫描..."
python3 ${WORKSPACE}/scripts/feishu/report_monitor.py
echo ""

echo "[Step 1.2] 研报下载与预处理..."
python3 ${WORKSPACE}/scripts/kg/report_processor.py
echo ""

echo "[Step 1.3] 实体自动提取..."
python3 ${WORKSPACE}/scripts/kg/auto_entity_extractor.py
echo ""

echo "============================================================"
echo "✅ G010 Step 1 全部完成"
echo "============================================================"
echo ""
echo "说明:"
echo "  - 当飞书有新研报时，会自动下载、预处理、提取实体"
echo "  - 目前队列为空，等待新研报上传"
echo "  - 可以设置cron定时执行此脚本"
echo ""
