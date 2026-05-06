#!/bin/bash
# A5L Tier 2 知识图谱备份脚本
# 备份内容: knowledge_graph.db, 实体快照, 分析结果
# 执行时间: 每日23:45
# 保留期: 14天

set -e

WORKSPACE="/workspace/projects/workspace"
DATE=$(date +%Y-%m-%d)
DATETIME=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$WORKSPACE/.backup/daily/kg"
KG_DIR="$WORKSPACE/skills/knowledge-graph"
LOG_FILE="$WORKSPACE/.backup/logs/backup.$DATE.log"

exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=========================================="
echo "A5L Tier 2 KG Backup - $DATETIME"
echo "=========================================="

cd "$WORKSPACE"

# 备份知识图谱数据库
if [ -f "$KG_DIR/data/knowledge_graph.db" ]; then
    cp "$KG_DIR/data/knowledge_graph.db" "$BACKUP_DIR/knowledge_graph.db.$DATE.bak"
    echo "✅ knowledge_graph.db backed up"
else
    echo "⚠️ knowledge_graph.db not found"
fi

# 备份知识图谱代码（以防修改）
if [ -d "$KG_DIR" ]; then
    tar -czf "$BACKUP_DIR/kg_code.$DATE.tar.gz" -C "$WORKSPACE" skills/knowledge-graph/*.py
    echo "✅ KG code backed up"
fi

# 备份reports目录中的分析结果
if [ -d "$WORKSPACE/reports" ]; then
    tar -czf "$BACKUP_DIR/reports.$DATE.tar.gz" -C "$WORKSPACE" reports/
    echo "✅ Reports backed up"
fi

# 生成备份清单
find "$BACKUP_DIR" -name "*.$DATE.*" > "$BACKUP_DIR/manifest.$DATE.txt"
echo "📋 Manifest generated"

# 计算总大小
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "📦 Total backup size: $TOTAL_SIZE"

# 清理14天前的备份
echo "🧹 Cleaning backups older than 14 days..."
find "$BACKUP_DIR" -name "*.bak" -mtime +14 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +14 -delete
find "$BACKUP_DIR" -name "manifest.*.txt" -mtime +14 -delete

echo "=========================================="
echo "✅ Tier 2 KG Backup Completed"
echo "=========================================="
