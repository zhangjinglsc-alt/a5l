#!/bin/bash
#
# SKILL自动开源脚本 v2.0 - 半自动版本
# 生成创建链接，点击后自动推送
#

set -e

SKILL_ID=$1
GITHUB_USER="zhangjinglsc-alt"
WORKSPACE="/workspace/projects/workspace"

echo "🚀 SKILL开源: ${SKILL_ID}"
echo "========================"

SKILL_PATH="${WORKSPACE}/skills/${SKILL_ID}"
REPO_NAME="a5l-skill-${SKILL_ID}"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}"
CREATE_URL="https://github.com/new?name=${REPO_NAME}&visibility=public&description=A5L+SKILL:+${SKILL_ID}"

# 1. 检查SKILL
if [ ! -d "$SKILL_PATH" ]; then
    echo "❌ SKILL不存在: ${SKILL_PATH}"
    exit 1
fi

# 2. 隐私扫描
echo "🔍 隐私扫描..."
python3 ${WORKSPACE}/TOOLS/privacy_scanner.py "$SKILL_PATH" || {
    echo "⚠️ 隐私扫描发现问题"
    exit 1
}

# 3. 准备文件
echo "📁 准备文件..."
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# 复制并创建文件
if [ -f "${SKILL_PATH}/SKILL.md" ]; then
    cp "${SKILL_PATH}/SKILL.md" "${TMP_DIR}/"
elif [ -f "${SKILL_PATH}/skill.md" ]; then
    cp "${SKILL_PATH}/skill.md" "${TMP_DIR}/SKILL.md"
else
    # 查找任意md文件
    MD_FILE=$(find "$SKILL_PATH" -maxdepth 1 -name "*.md" -type f | head -1)
    if [ -n "$MD_FILE" ]; then
        cp "$MD_FILE" "${TMP_DIR}/SKILL.md"
    else
        echo "⚠️ 未找到文档文件"
        exit 1
    fi
fi

cp "${WORKSPACE}/templates/LICENSE_MIT" "${TMP_DIR}/LICENSE"

SKILL_NAME=$(echo "$SKILL_ID" | tr '-' ' ' | tr '_' ' ' | sed 's/.*/\u&/')
cat > "${TMP_DIR}/README.md" << EOF
# ${SKILL_NAME}

A5L (Adaptive Autonomous Agent Learning) SKILL

## 🎯 简介

This is an A5L SKILL for autonomous agent capabilities.

## 📦 安装

\`\`\`bash
git clone ${REPO_URL}.git
cd ${REPO_NAME}
\`\`\`

## 📚 文档

See [SKILL.md](./SKILL.md) for detailed documentation.

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

[MIT License](./LICENSE)

## 🔗 Links

- [A5L Main Repo](https://github.com/${GITHUB_USER}/a5l)
- [OpenClaw](https://openclaw.ai)

---

<p align="center">
  Powered by <a href="https://github.com/${GITHUB_USER}/a5l">A5L</a>
</p>
EOF

cat > "${TMP_DIR}/.gitignore" << 'EOF'
__pycache__/
*.py[cod]
.env
.venv
*.log
.DS_Store
.vscode/
.idea/
EOF

# 4. Git初始化
echo "📝 Git初始化..."
cd "$TMP_DIR"
git init
git add .
git commit -m "Initial release: ${SKILL_ID}

- Add SKILL.md
- Add LICENSE (MIT)
- Add README
- Add .gitignore

A5L SKILL v1.0.0"

# 5. 输出信息和推送命令
echo ""
echo "================================"
echo "✅ 本地仓库准备完成!"
echo "================================"
echo ""
echo "📋 快速创建仓库步骤:"
echo ""
echo "1️⃣  点击创建仓库:"
echo "    ${CREATE_URL}"
echo ""
echo "2️⃣  然后执行推送:"
echo "    cd ${TMP_DIR}"
echo "    git remote add origin git@github.com:${GITHUB_USER}/${REPO_NAME}.git"
echo "    git branch -M main"
echo "    git push -u origin main"
echo ""
echo "📎 仓库地址: ${REPO_URL}"
echo ""
echo "💡 提示: 保持此终端开启，创建仓库后执行推送命令"
echo "================================"

# 保存推送脚本
cat > "${TMP_DIR}/push.sh" << EOF
#!/bin/bash
git remote add origin git@github.com:${GITHUB_USER}/${REPO_NAME}.git 2>/dev/null || true
git branch -M main
git push -u origin main
echo "✅ 推送完成!"
echo "📎 ${REPO_URL}"
EOF
chmod +x "${TMP_DIR}/push.sh"

echo ""
echo "或直接执行: ${TMP_DIR}/push.sh"
