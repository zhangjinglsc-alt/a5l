#!/bin/bash
#
# 自动创建GitHub仓库
#

REPO_NAME=$1
GITHUB_USER="zhangjinglsc-alt"

echo "📦 创建GitHub仓库: ${REPO_NAME}"

# 使用gh命令行工具（如果存在）
if command -v gh &> /dev/null; then
    gh repo create "${REPO_NAME}" --public --description "A5L SKILL" --confirm 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ 仓库创建成功 (gh)"
        exit 0
    fi
fi

# 使用curl + GITHUB_TOKEN
if [ -n "$GITHUB_TOKEN" ]; then
    RESPONSE=$(curl -s -w "%{http_code}" -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d "{\"name\":\"${REPO_NAME}\",\"private\":false,\"description\":\"A5L SKILL: ${REPO_NAME}\",\"auto_init\":false}" 2>/dev/null)
    
    HTTP_CODE=${RESPONSE: -3}
    
    if [ "$HTTP_CODE" = "201" ]; then
        echo "✅ 仓库创建成功 (API)"
        exit 0
    elif [ "$HTTP_CODE" = "422" ]; then
        echo "⚠️ 仓库已存在"
        exit 0
    else
        echo "❌ 创建失败 (HTTP $HTTP_CODE)"
        exit 1
    fi
fi

echo "❌ 无法自动创建"
echo "请设置 GITHUB_TOKEN 或安装 gh CLI"
exit 1
