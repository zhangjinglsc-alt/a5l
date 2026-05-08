#!/bin/bash
#
# SKILL自动开源脚本
# 将单个SKILL发布到GitHub
#

set -e

# 配置
SKILL_ID=$1
GITHUB_USER="zhangjinglsc-alt"
WORKSPACE="/workspace/projects/workspace"
TEMPLATES_DIR="${WORKSPACE}/templates"

if [ -z "$SKILL_ID" ]; then
    echo "Usage: $0 <skill_id>"
    echo "Example: $0 unified_stock_price"
    exit 1
fi

SKILL_PATH="${WORKSPACE}/skills/${SKILL_ID}"
REPO_NAME="a5l-skill-${SKILL_ID}"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}"

echo "🚀 开始开源SKILL: ${SKILL_ID}"
echo "================================"

# 1. 检查SKILL是否存在
if [ ! -d "$SKILL_PATH" ]; then
    echo "❌ SKILL不存在: ${SKILL_PATH}"
    exit 1
fi

echo "✅ SKILL目录存在"

# 2. 隐私扫描
echo ""
echo "🔍 执行隐私扫描..."
python3 ${WORKSPACE}/TOOLS/privacy_scanner.py "$SKILL_PATH"
if [ $? -ne 0 ]; then
    echo "⚠️ 隐私扫描发现潜在问题，请检查"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 3. 创建临时目录
echo ""
echo "📁 准备开源文件..."
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# 4. 复制核心文件
if [ -f "${SKILL_PATH}/SKILL.md" ]; then
    cp "${SKILL_PATH}/SKILL.md" "${TMP_DIR}/"
else
    echo "⚠️ 未找到SKILL.md，尝试其他文档..."
    # 查找任何.md文件
    MD_FILES=$(find "$SKILL_PATH" -maxdepth 1 -name "*.md" -type f)
    if [ -n "$MD_FILES" ]; then
        echo "$MD_FILES" | head -1 | xargs -I {} cp {} "${TMP_DIR}/SKILL.md"
    fi
fi

# 5. 创建LICENSE
cp "${TEMPLATES_DIR}/LICENSE_MIT" "${TMP_DIR}/LICENSE"

# 6. 创建README
SKILL_NAME=$(echo "$SKILL_ID" | tr '_' ' ' | tr '-' ' ' | sed 's/.*/\u&/')
cat > "${TMP_DIR}/README.md" << EOF
# ${SKILL_NAME}

A5L (Adaptive Autonomous Agent Learning) SKILL - ${SKILL_ID}

## 🎯 简介

This is an A5L SKILL for autonomous agent capabilities.

## 📦 安装

\`\`\`bash
git clone ${REPO_URL}.git
cd ${REPO_NAME}
\`\`\`

## 📚 文档

详细文档请参考 [SKILL.md](./SKILL.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

[MIT License](./LICENSE)

## 🔗 相关链接

- [A5L 主仓库](https://github.com/${GITHUB_USER}/a5l)
- [OpenClaw](https://openclaw.ai)

---

<p align="center">
  Powered by <a href="https://github.com/${GITHUB_USER}/a5l">A5L</a> - Adaptive Autonomous Agent Learning
</p>
EOF

# 7. 创建.gitignore
cat > "${TMP_DIR}/.gitignore" << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Environment
.env
.venv
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# A5L specific
*.log
data/
EOF

echo "✅ 文件准备完成"

# 8. 创建GitHub仓库 (如果API token可用)
if [ -n "$GITHUB_TOKEN" ]; then
    echo ""
    echo "📦 创建GitHub仓库..."
    curl -s -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d "{\"name\":\"${REPO_NAME}\",\"private\":false,\"description\":\"A5L SKILL: ${SKILL_ID}\",\"topics\":[\"a5l\",\"skill\",\"ai-agent\",\"autonomous-agent\"]}" > /dev/null 2>&1 || true
fi

# 9. Git提交
echo ""
echo "📝 Git提交..."
cd "$TMP_DIR"
git init
git add .
git commit -m "Initial release: ${SKILL_ID}

- Add SKILL.md
- Add LICENSE (MIT)
- Add README
- Add .gitignore

A5L SKILL Release v1.0.0"

# 10. 推送到GitHub
echo ""
echo "⬆️ 推送到GitHub..."
git remote add origin "git@github.com:${GITHUB_USER}/${REPO_NAME}.git" 2>/dev/null || true
git branch -M main

# 尝试推送
if git push -u origin main 2>/dev/null; then
    echo "✅ 推送成功!"
    echo ""
    echo "🎉 SKILL开源完成!"
    echo "   仓库: ${REPO_URL}"
    echo "   本地: ${TMP_DIR}"
else
    echo "⚠️ 推送失败，可能仓库未创建"
    echo ""
    echo "手动创建仓库步骤:"
    echo "1. 访问 https://github.com/new"
    echo "2. 仓库名: ${REPO_NAME}"
    echo "3. 设置为Public"
    echo "4. 然后执行: cd ${TMP_DIR} && git push -u origin main"
fi

echo ""
echo "================================"
echo "SKILL: ${SKILL_ID}"
echo "状态: 准备完成"
