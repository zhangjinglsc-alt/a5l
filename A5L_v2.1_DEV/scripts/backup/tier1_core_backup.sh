#!/bin/bash
# A5L Tier 1 核心数据备份脚本
# 备份内容: SOUL.md, SKILL_REGISTRY.json, MEMORY.md, GOAL/
# 执行时间: 每日23:30
# 保留期: 30天

set -e

WORKSPACE="/workspace/projects/workspace"
DATE=$(date +%Y-%m-%d)
DATETIME=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$WORKSPACE/.backup/daily/core"
LOG_FILE="$WORKSPACE/.backup/logs/backup.$DATE.log"

# 创建日志
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=========================================="
echo "A5L Tier 1 Core Backup - $DATETIME"
echo "=========================================="

# 检查目录
cd "$WORKSPACE"

# 备份SOUL.md
if [ -f "SOUL.md" ]; then
    cp SOUL.md "$BACKUP_DIR/SOUL.md.$DATE.bak"
    echo "✅ SOUL.md backed up ($(stat -c%s SOUL.md) bytes)"
else
    echo "⚠️ SOUL.md not found"
fi

# 备份SKILL_REGISTRY.json
if [ -f "SKILL_REGISTRY.json" ]; then
    cp SKILL_REGISTRY.json "$BACKUP_DIR/SKILL_REGISTRY.json.$DATE.bak"
    echo "✅ SKILL_REGISTRY.json backed up ($(stat -c%s SKILL_REGISTRY.json) bytes)"
else
    echo "⚠️ SKILL_REGISTRY.json not found"
fi

# 备份MEMORY.md
if [ -f "MEMORY.md" ]; then
    cp MEMORY.md "$BACKUP_DIR/MEMORY.md.$DATE.bak"
    echo "✅ MEMORY.md backed up ($(stat -c%s MEMORY.md) bytes)"
else
    echo "⚠️ MEMORY.md not found"
fi

# 备份GOAL目录
if [ -d "GOAL" ]; then
    tar -czf "$BACKUP_DIR/GOAL.$DATE.tar.gz" GOAL/
    echo "✅ GOAL/ backed up ($(du -sh GOAL/ | cut -f1))"
else
    echo "⚠️ GOAL/ not found"
fi

# 计算总大小
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "📦 Total backup size: $TOTAL_SIZE"

# 生成完整性哈希
if command -v sha256sum &> /dev/null; then
    find "$BACKUP_DIR" -name "*.$DATE.*" -exec sha256sum {} \; > "$BACKUP_DIR/integrity.$DATE.sha256"
    echo "🔐 Integrity hash generated"
fi

# 清理30天前的备份
echo "🧹 Cleaning backups older than 30 days..."
find "$BACKUP_DIR" -name "*.bak" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "integrity.*.sha256" -mtime +30 -delete

echo "=========================================="
echo "✅ Tier 1 Core Backup Completed"
echo "=========================================="
