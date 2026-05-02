#!/bin/bash
# A5L SSH配置脚本
# 配置SSH免密推送到GitHub

echo "================================================"
echo "🔐 A5L SSH免密推送配置"
echo "================================================"
echo ""

# 1. 检查SSH密钥
if [ -f ~/.ssh/id_ed25519.pub ]; then
    echo "✅ SSH密钥已存在"
else
    echo "🔑 生成SSH密钥..."
    ssh-keygen -t ed25519 -C "zhangjinglsc-alt@github.com" -f ~/.ssh/id_ed25519 -N ""
    echo "✅ SSH密钥生成成功"
fi

echo ""
echo "📋 你的SSH公钥:"
echo "================================================"
cat ~/.ssh/id_ed25519.pub
echo "================================================"
echo ""

# 2. 添加到SSH agent
echo "🚀 启动SSH agent..."
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
echo "✅ SSH密钥已添加到agent"

echo ""
echo "================================================"
echo "📋 下一步: 添加公钥到GitHub"
echo "================================================"
echo ""
echo "1. 复制上面的公钥 (以 ssh-ed25519 开头)"
echo "2. 访问: https://github.com/settings/keys"
echo "3. 点击 'New SSH key'"
echo "4. Title: A5L-Deploy"
echo "5. Key: 粘贴公钥"
echo "6. 点击 'Add SSH key'"
echo ""
echo "================================================"
echo "🔗 修改远程仓库为SSH地址"
echo "================================================"
echo ""
cd /workspace/projects/workspace
git remote set-url origin git@github.com:zhangjinglsc-alt/a5l.git
echo "✅ 远程仓库已修改为SSH地址"
echo "   新地址: $(git remote get-url origin)"
echo ""
echo "================================================"
echo "🧪 测试SSH连接"
echo "================================================"
echo ""
ssh -T git@github.com
echo ""
echo "如果看到 'Hi zhangjinglsc-alt! You've successfully authenticated' 说明成功！"
echo ""
echo "================================================"
echo "🎉 配置完成！"
echo "================================================"
echo ""
echo "现在你可以免密推送到GitHub了："
echo "  git push origin main"
echo ""
