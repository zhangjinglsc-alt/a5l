#!/bin/bash
# 数据上传监控脚本
# 检测到数据上传后自动触发完整升级流水线

CIO_DIR="/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening"
DATA_DIR="$CIO_DIR/data/historical"
LOG_FILE="$CIO_DIR/data/upload_monitor.log"

mkdir -p "$DATA_DIR"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 启动数据上传监控..." >> "$LOG_FILE"
echo "监控目录: $DATA_DIR"
echo "等待数据文件..."

while true; do
    # 检测zip文件
    for zipfile in "$DATA_DIR"/*.zip; do
        if [ -f "$zipfile" ]; then
            FILENAME=$(basename "$zipfile")
            FILESIZE=$(du -h "$zipfile" | cut -f1)
            
            echo ""
            echo "🎉 检测到数据文件！"
            echo "   文件名: $FILENAME"
            echo "   大小: $FILESIZE"
            echo ""
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 检测到数据: $FILENAME ($FILESIZE)" >> "$LOG_FILE"
            
            # 标准化文件名
            if [ "$FILENAME" != "kaipanla_history.zip" ]; then
                mv "$zipfile" "$DATA_DIR/kaipanla_history.zip"
                echo "已重命名为: kaipanla_history.zip"
            fi
            
            echo "🚀 自动启动完整升级流水线..."
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 启动升级流水线" >> "$LOG_FILE"
            
            # 执行升级流水线
            bash "$CIO_DIR/full_upgrade_pipeline.sh" 2>&1 | tee -a "$LOG_FILE"
            
            echo ""
            echo "✅ 升级完成！"
            echo "$(date '+%Y-%m-%d %H:%M:%S') - 升级完成" >> "$LOG_FILE"
            
            exit 0
        fi
    done
    
    # 每10秒检查一次
    sleep 10
done
