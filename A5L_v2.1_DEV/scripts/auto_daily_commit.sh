#!/bin/bash
# A5L每日自动Commit和推送脚本
# 执行时间: 每天17:30
# 功能: 自动保存当天所有修改到GitHub

set -e  # 遇到错误立即退出

A5L_DIR="/workspace/projects/workspace"
LOG_FILE="$A5L_DIR/logs/auto_commit.log"
DATE=$(date +"%Y-%m-%d %H:%M:%S")
DATE_SHORT=$(date +"%Y%m%d")

# 确保日志目录存在
mkdir -p "$A5L_DIR/logs"

# 日志函数
log() {
    echo "[$DATE] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "🚀 A5L每日自动Commit开始"
log "=========================================="

# 进入工作目录
cd "$A5L_DIR"

# 检查是否有修改
if git diff --quiet && git diff --cached --quiet; then
    log "📋 没有需要提交的修改"
    log "✅ 任务完成 (无需提交)"
    exit 0
fi

# 显示修改状态
log "📊 当前修改状态:"
git status --short | while read line; do
    log "  $line"
done

# 添加所有修改
log "📦 添加所有修改..."
git add -A

# 创建commit
log "💾 创建Commit..."
git commit -m "auto: Daily backup $DATE_SHORT

- Automated daily commit at 17:30
- Backup all changes to GitHub
- Preserve work progress" || {
    log "⚠️ Commit失败或没有修改"
    exit 0
}

# 推送到GitHub
log "📡 推送到GitHub..."
if git push origin main; then
    COMMIT_HASH=$(git rev-parse --short HEAD)
    log "✅ 推送成功!"
    log "   Commit: $COMMIT_HASH"
    log "   时间: $DATE"
else
    log "❌ 推送失败"
    exit 1
fi

log "=========================================="
log "✅ 每日自动Commit完成"
log "=========================================="

# 可选: 发送通知（如果配置了飞书webhook）
if [ -f "$A5L_DIR/config/feishu_webhook.conf" ]; then
    source "$A5L_DIR/config/feishu_webhook.conf"
    curl -s -X POST "$FEISHU_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"✅ A5L每日备份完成\nCommit: $COMMIT_HASH\n时间: $DATE\"}}" \
        > /dev/null 2>&1 || true
fi

exit 0
