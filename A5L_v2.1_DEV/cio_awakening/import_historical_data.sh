#!/bin/bash
# CIO历史数据导入脚本 - 处理大型zip文件
# 适用于800MB+日K数据

set -e

DATA_DIR="/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/historical"
ZIP_FILE="$DATA_DIR/kaipanla_history.zip"
TEMP_DIR="$DATA_DIR/temp"
CHUNK_SIZE="50M"

echo "🚀 CIO历史数据导入工具"
echo "========================"
echo ""

# 创建目录
mkdir -p "$DATA_DIR" "$TEMP_DIR"

echo "📦 准备处理800MB日K数据..."
echo "   临时目录: $TEMP_DIR"
echo "   数据目录: $DATA_DIR"
echo ""

# 检查磁盘空间
echo "💾 检查磁盘空间..."
available=$(df -B1G /workspace | tail -1 | awk '{print $4}')
echo "   可用空间: ${available}GB"

if [ "$available" -lt 2 ]; then
    echo "⚠️ 警告: 磁盘空间不足2GB，建议清理空间"
fi
echo ""

echo "✅ 准备就绪，等待数据文件..."
echo ""
echo "使用方法:"
echo "   1. 将 zip文件放到: $DATA_DIR/kaipanla_history.zip"
echo "   2. 运行: bash import_historical_data.sh"
echo ""
echo "处理流程:"
echo "   1. 验证zip文件完整性"
echo "   2. 流式解压 (不解压全部，逐文件处理)"
echo "   3. CSV验证和清洗"
echo "   4. 导入SQLite数据库"
echo "   5. 生成训练样本"
echo ""
