#!/bin/bash
#
# 批量准备首批10个SKILL开源
#

WORKSPACE="/workspace/projects/workspace"
GITHUB_USER="zhangjinglsc-alt"
OUTPUT_DIR="${WORKSPACE}/tmp/batch1_repos"

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

mkdir -p "$OUTPUT_DIR"

echo "🚀 A5L SKILL Batch 1 - 自动准备"
echo "=================================="
echo "数量: ${#SKILLS[@]} 个SKILL"
echo "输出: ${OUTPUT_DIR}"
echo ""

# 创建总览文件
INDEX_FILE="${OUTPUT_DIR}/_batch1_index.md"
echo "# A5L SKILL Batch 1 - 开源准备" > "$INDEX_FILE"
echo "" >> "$INDEX_FILE"
echo "生成时间: $(date)" >> "$INDEX_FILE"
echo "" >> "$INDEX_FILE"
echo "| # | SKILL | 状态 | 创建链接 | 推送脚本 |" >> "$INDEX_FILE"
echo "|---|-------|------|----------|----------|" >> "$INDEX_FILE"

SUCCESS=0
FAILED=0

for i in "${!SKILLS[@]}"; do
    SKILL_ID="${SKILLS[$i]}"
    NUM=$((i+1))
    
    echo "[$NUM/${#SKILLS[@]}] 处理: ${SKILL_ID}"
    
    SKILL_PATH="${WORKSPACE}/skills/${SKILL_ID}"
    REPO_NAME="a5l-skill-${SKILL_ID}"
    CREATE_URL="https://github.com/new?name=${REPO_NAME}&visibility=public&description=A5L+SKILL:+${SKILL_ID}"
    
    # 检查存在
    if [ ! -d "$SKILL_PATH" ]; then
        echo "  ⚠️ 跳过 - 目录不存在"
        echo "| ${NUM} | ${SKILL_ID} | ❌ 不存在 | - | - |" >> "$INDEX_FILE"
        FAILED=$((FAILED+1))
        continue
    fi
    
    # 隐私扫描
    python3 ${WORKSPACE}/TOOLS/privacy_scanner.py "$SKILL_PATH" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "  ⚠️ 跳过 - 隐私扫描失败"
        echo "| ${NUM} | ${SKILL_ID} | ⚠️ 隐私问题 | - | - |" >> "$INDEX_FILE"
        FAILED=$((FAILED+1))
        continue
    fi
    
    # 准备文件
    REPO_DIR="${OUTPUT_DIR}/${REPO_NAME}"
    mkdir -p "$REPO_DIR"
    
    # 复制SKILL.md
    if [ -f "${SKILL_PATH}/SKILL.md" ]; then
        cp "${SKILL_PATH}/SKILL.md" "${REPO_DIR}/"
    else
        find "$SKILL_PATH" -maxdepth 1 -name "*.md" -type f | head -1 | xargs -I {} cp {} "${REPO_DIR}/SKILL.md"
    fi
    
    # 复制LICENSE
    cp "${WORKSPACE}/templates/LICENSE_MIT" "${REPO_DIR}/LICENSE"
    
    # 创建README
    SKILL_NAME=$(echo "$SKILL_ID" | tr '-' ' ' | sed 's/.*/\u&/')
    cat > "${REPO_DIR}/README.md" << EOF
# ${SKILL_NAME}

A5L (Adaptive Autonomous Agent Learning) SKILL

## 📦 Install

\`\`\`bash
git clone https://github.com/${GITHUB_USER}/${REPO_NAME}.git
cd ${REPO_NAME}
\`\`\`

## 📚 Docs

See [SKILL.md](./SKILL.md)

## 📄 License

[MIT](./LICENSE)

---

Powered by [A5L](https://github.com/${GITHUB_USER}/a5l)
EOF
    
    # 创建.gitignore
    cat > "${REPO_DIR}/.gitignore" << 'EOF'
__pycache__/
*.py[cod]
.env
*.log
.DS_Store
EOF
    
    # Git初始化
    cd "$REPO_DIR"
    git init --quiet
    git add .
    git commit -m "Initial: ${SKILL_ID}" --quiet
    
    # 创建推送脚本
    cat > "${REPO_DIR}/_push.sh" << EOF
#!/bin/bash
git remote add origin git@github.com:${GITHUB_USER}/${REPO_NAME}.git 2>/dev/null || true
git branch -M main
git push -u origin main
echo "✅ ${SKILL_ID} 推送完成!"
EOF
    chmod +x "${REPO_DIR}/_push.sh"
    
    # 创建快捷链接文件
    echo "$CREATE_URL" > "${REPO_DIR}/_create_url.txt"
    
    echo "  ✅ 准备完成"
    echo "| ${NUM} | ${SKILL_ID} | ✅ 就绪 | [创建](${CREATE_URL}) | \`_push.sh\` |" >> "$INDEX_FILE"
    SUCCESS=$((SUCCESS+1))
done

echo "" >> "$INDEX_FILE"
echo "## 批量推送脚本" >> "$INDEX_FILE"
echo "" >> "$INDEX_FILE"
echo "\`\`\`bash" >> "$INDEX_FILE"
echo "# 创建所有仓库后，批量推送" >> "$INDEX_FILE"
echo "cd ${OUTPUT_DIR}" >> "$INDEX_FILE"
for SKILL_ID in "${SKILLS[@]}"; do
    REPO_NAME="a5l-skill-${SKILL_ID}"
    echo "cd ${REPO_NAME} && bash _push.sh && cd .." >> "$INDEX_FILE"
done
echo "\`\`\`" >> "$INDEX_FILE"

echo ""
echo "=================================="
echo "📊 批量准备完成"
echo "=================================="
echo "成功: ${SUCCESS} 个"
echo "失败: ${FAILED} 个"
echo ""
echo "📁 输出目录: ${OUTPUT_DIR}"
echo "📋 索引文件: ${INDEX_FILE}"
echo ""
echo "🚀 下一步:"
echo "1. 查看索引: cat ${INDEX_FILE}"
echo "2. 点击创建链接创建GitHub仓库"
echo "3. 运行推送脚本完成开源"
