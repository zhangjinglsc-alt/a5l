#!/bin/bash
# A5L Core Files Check Script
# 执行者: CSO
# 频率: 每日17:30
# 用途: 检查核心档案更新状态

echo "=========================================="
echo "🔍 A5L 核心档案检查"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "执行者: CSO"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# 获取当前时间
NOW=$(date +%s)
TODAY=$(date +%Y-%m-%d)

# 1. 检查SOUL.md
echo "📋 1. 检查 SOUL.md"
if [ -f "/workspace/projects/workspace/SOUL.md" ]; then
    SOUL_AGE=$(stat -c %Y /workspace/projects/workspace/SOUL.md)
    SOUL_DAYS=$(( (NOW - SOUL_AGE) / 86400 ))
    SOUL_HOURS=$(( (NOW - SOUL_AGE) / 3600 ))
    
    if [ $SOUL_DAYS -gt 2 ]; then
        echo "   ❌ 严重: SOUL.md ${SOUL_DAYS}天未更新 (责任人: Chief Architect)"
        ERRORS=$((ERRORS+1))
    elif [ $SOUL_DAYS -gt 1 ]; then
        echo "   ⚠️  警告: SOUL.md ${SOUL_DAYS}天未更新"
        WARNINGS=$((WARNINGS+1))
    else
        echo "   ✅ 正常 (最近更新: ${SOUL_HOURS}小时前)"
    fi
else
    echo "   ❌ 严重: SOUL.md 文件不存在!"
    ERRORS=$((ERRORS+1))
fi
echo ""

# 2. 检查MEMORY.md
echo "📋 2. 检查 MEMORY.md"
if [ -f "/workspace/projects/workspace/MEMORY.md" ]; then
    MEMORY_AGE=$(stat -c %Y /workspace/projects/workspace/MEMORY.md)
    MEMORY_DAYS=$(( (NOW - MEMORY_AGE) / 86400 ))
    MEMORY_HOURS=$(( (NOW - MEMORY_AGE) / 3600 ))
    
    if [ $MEMORY_DAYS -gt 1 ]; then
        echo "   ❌ 严重: MEMORY.md ${MEMORY_DAYS}天未更新 (责任人: Knowledge Guardian)"
        ERRORS=$((ERRORS+1))
    else
        echo "   ✅ 正常 (最近更新: ${MEMORY_HOURS}小时前)"
    fi
    
    # 检查Git提交数是否准确
    cd /workspace/projects/workspace
    ACTUAL_COMMITS=$(git rev-list --count HEAD)
    # 简单检查MEMORY.md中是否包含Git提交信息
    if grep -q "Git提交" /workspace/projects/workspace/MEMORY.md; then
        echo "   ℹ️  Git提交数记录: 请确认是否为 ${ACTUAL_COMMITS}"
    fi
else
    echo "   ❌ 严重: MEMORY.md 文件不存在!"
    ERRORS=$((ERRORS+1))
fi
echo ""

# 3. 检查AGENTS.md
echo "📋 3. 检查 AGENTS.md"
if [ -f "/workspace/projects/workspace/AGENTS.md" ]; then
    AGENTS_AGE=$(stat -c %Y /workspace/projects/workspace/AGENTS.md)
    AGENTS_DAYS=$(( (NOW - AGENTS_AGE) / 86400 ))
    AGENTS_HOURS=$(( (NOW - AGENTS_AGE) / 3600 ))
    
    if [ $AGENTS_DAYS -gt 2 ]; then
        echo "   ❌ 严重: AGENTS.md ${AGENTS_DAYS}天未更新 (责任人: Chief Architect)"
        ERRORS=$((ERRORS+1))
    elif [ $AGENTS_DAYS -gt 1 ]; then
        echo "   ⚠️  警告: AGENTS.md ${AGENTS_DAYS}天未更新"
        WARNINGS=$((WARNINGS+1))
    else
        echo "   ✅ 正常 (最近更新: ${AGENTS_HOURS}小时前)"
    fi
else
    echo "   ❌ 严重: AGENTS.md 文件不存在!"
    ERRORS=$((ERRORS+1))
fi
echo ""

# 4. 检查今日记忆档案
echo "📋 4. 检查今日记忆档案 (memory/${TODAY}.md)"
if [ -f "/workspace/projects/workspace/memory/${TODAY}.md" ]; then
    echo "   ✅ 已创建"
    # 检查文件大小(确保有内容)
    FILE_SIZE=$(stat -c %s "/workspace/projects/workspace/memory/${TODAY}.md")
    if [ $FILE_SIZE -lt 100 ]; then
        echo "   ⚠️  警告: 文件内容过少 (${FILE_SIZE} bytes)"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo "   ❌ 严重: 今日记忆档案未创建 (责任人: 当日值班者)"
    ERRORS=$((ERRORS+1))
fi
echo ""

# 5. 检查Session备份
echo "📋 5. 检查 Session备份"
if [ -d "/workspace/projects/workspace/.backup/sessions/active" ]; then
    LATEST_BACKUP=$(ls -t /workspace/projects/workspace/.backup/sessions/active/*.json 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        BACKUP_AGE_MIN=$(( (NOW - $(stat -c %Y "$LATEST_BACKUP")) / 60 ))
        if [ $BACKUP_AGE_MIN -gt 60 ]; then
            echo "   ❌ 严重: Session备份异常 (最近备份: ${BACKUP_AGE_MIN}分钟前)"
            ERRORS=$((ERRORS+1))
        else
            echo "   ✅ 正常 (最近备份: ${BACKUP_AGE_MIN}分钟前)"
        fi
    else
        echo "   ❌ 严重: 无Session备份文件"
        ERRORS=$((ERRORS+1))
    fi
else
    echo "   ❌ 严重: Session备份目录不存在"
    ERRORS=$((ERRORS+1))
fi
echo ""

# 6. 检查GitHub同步状态
echo "📋 6. 检查 GitHub同步"
cd /workspace/projects/workspace
UNSTAGED=$(git diff --name-only 2>/dev/null | wc -l)
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)

if [ $UNSTAGED -gt 0 ] || [ $UNTRACKED -gt 0 ]; then
    echo "   ⚠️  警告: 有 ${UNSTAGED} 个未提交修改, ${UNTRACKED} 个未跟踪文件"
    echo "   📄 未提交文件:"
    git diff --name-only 2>/dev/null | head -5 | sed 's/^/      - /'
    WARNINGS=$((WARNINGS+1))
else
    echo "   ✅ 所有修改已同步"
fi
echo ""

# 汇总
echo "=========================================="
echo "📊 检查结果汇总"
echo "=========================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "🎉 所有检查通过！"
    echo ""
    echo "✅ SOUL.md - 正常"
    echo "✅ MEMORY.md - 正常"
    echo "✅ AGENTS.md - 正常"
    echo "✅ 今日记忆档案 - 已创建"
    echo "✅ Session备份 - 正常"
    echo "✅ GitHub同步 - 正常"
    exit 0
else
    echo "🚨 发现 ${ERRORS} 个错误, ${WARNINGS} 个警告"
    echo ""
    if [ $ERRORS -gt 0 ]; then
        echo "❌ 错误必须立即处理！"
    fi
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠️  警告需要关注"
    fi
    echo ""
    echo "⏰ 处理截止时间: 今日18:00"
    echo "📋 处理后请重新运行本脚本验证"
    exit 1
fi
