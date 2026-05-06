#!/bin/bash
# A5L Session Backup Script
# 使用: ./session_backup.sh [--mode=realtime|daily|milestone]

MODE=${1:-realtime}
BACKUP_DIR="/workspace/projects/workspace/.backup/sessions"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)

# 创建备份目录
mkdir -p "$BACKUP_DIR/active"
mkdir -p "$BACKUP_DIR/daily/$DATE"
mkdir -p "$BACKUP_DIR/milestones"

# 获取当前状态
WORK_DIR=$(pwd)
GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
UNSTAGED=$(git diff --name-only 2>/dev/null | wc -l)

# 构建备份内容
case $MODE in
    realtime)
        BACKUP_FILE="$BACKUP_DIR/active/session_${TIMESTAMP}.json"
        echo "Creating realtime backup: $BACKUP_FILE"
        ;;
    daily)
        BACKUP_FILE="$BACKUP_DIR/daily/$DATE/session_final.json"
        echo "Creating daily backup: $BACKUP_FILE"
        ;;
    milestone)
        MILESTONE_NAME=${2:-"milestone_$TIMESTAMP"}
        mkdir -p "$BACKUP_DIR/milestones/$MILESTONE_NAME"
        BACKUP_FILE="$BACKUP_DIR/milestones/$MILESTONE_NAME/session.json"
        echo "Creating milestone backup: $BACKUP_FILE"
        ;;
esac

# 生成备份内容
cat > "$BACKUP_FILE" << EOF
{
  "backup_info": {
    "mode": "$MODE",
    "timestamp": "$(date -Iseconds)",
    "timestamp_readable": "$(date '+%Y-%m-%d %H:%M:%S')"
  },
  "session_context": {
    "working_directory": "$WORK_DIR",
    "mode": "$MODE"
  },
  "git_state": {
    "branch": "$GIT_BRANCH",
    "last_commit": "$GIT_COMMIT",
    "unstaged_changes": $UNSTAGED
  },
  "system_info": {
    "hostname": "$(hostname)",
    "user": "$(whoami)"
  }
}
EOF

# 如果是日终备份，额外保存关键文件
if [ "$MODE" = "daily" ]; then
    cp /workspace/projects/workspace/memory/$DATE.md "$BACKUP_DIR/daily/$DATE/" 2>/dev/null
    cp /workspace/projects/workspace/MEMORY.md "$BACKUP_DIR/daily/$DATE/" 2>/dev/null
    cp /workspace/projects/workspace/SOUL.md "$BACKUP_DIR/daily/$DATE/" 2>/dev/null
    echo "Key files backed up to: $BACKUP_DIR/daily/$DATE/"
fi

echo "✅ Backup completed: $BACKUP_FILE"
