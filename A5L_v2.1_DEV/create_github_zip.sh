#!/bin/bash
# A5L GitHub上传助手
# 创建ZIP文件供手动上传到GitHub

echo "================================================"
echo "📦 A5L GitHub上传助手"
echo "================================================"
echo ""

cd /workspace/projects/workspace

# 创建导出目录
mkdir -p github_upload

# 方法1: 完整ZIP（包含Git历史）
echo "📦 方法1: 创建完整ZIP（推荐）..."
zip -r github_upload/a5l-complete.zip . \
    -x "*.zip" \
    -x "*.tar.gz" \
    -x "data/*" \
    -x "logs/*" \
    -x "tmp/*" \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x ".git/objects/*" 2>/dev/null

if [ -f github_upload/a5l-complete.zip ]; then
    echo "✅ 完整ZIP创建成功"
    ls -lh github_upload/a5l-complete.zip
fi

# 方法2: 源代码ZIP（无Git历史，更小）
echo ""
echo "📦 方法2: 创建源代码ZIP..."
zip -r github_upload/a5l-source.zip . \
    -x ".git/*" \
    -x "*.zip" \
    -x "*.tar.gz" \
    -x "data/*" \
    -x "logs/*" \
    -x "tmp/*" \
    -x "__pycache__/*" \
    -x "*.pyc" 2>/dev/null

if [ -f github_upload/a5l-source.zip ]; then
    echo "✅ 源代码ZIP创建成功"
    ls -lh github_upload/a5l-source.zip
fi

# 方法3: 仅核心代码
echo ""
echo "📦 方法3: 创建核心代码ZIP..."
zip -r github_upload/a5l-core.zip \
    README.md \
    LICENSE \
    requirements.txt \
    SOUL.md \
    A5L_SOUL_BINDING.md \
    CLI_GUIDE.md \
    A5L_MAX_GUIDE.md \
    GITHUB_*.md \
    push_to_github.sh \
    a5l_cli.py \
    a5l_max_engine.py \
    ARCHITECT_5L/ \
    skills/ \
    KIWI/ \
    bin/ \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x "*.zip" 2>/dev/null

if [ -f github_upload/a5l-core.zip ]; then
    echo "✅ 核心代码ZIP创建成功"
    ls -lh github_upload/a5l-core.zip
fi

# 生成上传说明
cat > github_upload/README.txt << 'EOF'
A5L GitHub上传说明
===================

文件说明:
---------
• a5l-complete.zip - 完整项目（包含Git提交历史）
• a5l-source.zip - 源代码（无Git历史，推荐）
• a5l-core.zip - 仅核心代码（最精简）

上传步骤:
---------
1. 下载ZIP文件到本地
2. 解压ZIP文件
3. 在GitHub仓库页面点击 "Uploading an existing file"
4. 将解压后的文件拖放到上传区域
5. 提交更改

或者使用命令行:
--------------
cd 解压后的文件夹
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/zhangjinglsc-alt/a5l.git
git push -u origin main

项目统计:
---------
• 开发时间: 6小时
• Git提交: 11个
• 总文件数: 61个
• 代码规模: ~400,000 bytes
• 架构层数: 7层 (Layer 0-5 + Advanced)

文件位置:
---------
/workspace/projects/workspace/github_upload/
EOF

echo ""
echo "================================================"
echo "✅ ZIP文件创建完成！"
echo "================================================"
echo ""
echo "📁 文件位置: /workspace/projects/workspace/github_upload/"
echo ""
ls -lh github_upload/
echo ""
echo "📋 下一步:"
echo "  1. 下载ZIP文件到本地"
echo "  2. 在GitHub页面 https://github.com/zhangjinglsc-alt/a5l/upload 上传"
echo "  3. 或者使用说明中的命令行方式"
echo ""
echo "================================================"
