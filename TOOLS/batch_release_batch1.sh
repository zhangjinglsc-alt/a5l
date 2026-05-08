#!/bin/bash
#
# 批量开源首批10个SKILL
#

WORKSPACE="/workspace/projects/workspace"
GITHUB_USER="zhangjinglsc-alt"

# 首批10个SKILL (Batch 1)
SKILLS=(
    "unified-stock-price"
    "coze-web-search"
    "stock-five-steps"
    "catalyst-tier-framework"
    "factor-investing"
    "industry-research"
    "private-banker-stock"
    "buffett-value-investing"
    "quant-analysis"
    "technical-analysis"
)

echo "🚀 A5L SKILL开源 - Batch 1"
echo "=========================="
echo "目标: ${#SKILLS[@]} 个SKILL"
echo "账号: ${GITHUB_USER}"
echo ""

SUCCESS_COUNT=0
FAILED_COUNT=0

for SKILL_ID in "${SKILLS[@]}"; do
    echo "----------------------------------------"
    echo "处理: ${SKILL_ID}"
    
    SKILL_PATH="${WORKSPACE}/skills/${SKILL_ID}"
    
    # 检查是否存在
    if [ ! -d "$SKILL_PATH" ]; then
        echo "⚠️ 跳过 - 目录不存在: ${SKILL_PATH}"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        continue
    fi
    
    # 执行开源脚本
    if bash ${WORKSPACE}/TOOLS/skill_release.sh "$SKILL_ID"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
    
    echo ""
done

echo "========================================"
echo "📊 开源完成统计"
echo "========================================"
echo "成功: ${SUCCESS_COUNT} 个"
echo "失败: ${FAILED_COUNT} 个"
echo "总计: ${#SKILLS[@]} 个"
echo ""
echo "查看仓库: https://github.com/${GITHUB_USER}?tab=repositories"
