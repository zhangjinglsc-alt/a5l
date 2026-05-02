# A5L GitHub自动推送配置

## ✅ Git Hooks已配置

**钩子文件**: `.git/hooks/post-commit`

## 🔄 自动推送流程

现在每次执行 `git commit` 后会**自动**推送到GitHub：

```bash
# 1. 修改文件
echo "新内容" >> README.md

# 2. 添加文件
git add README.md

# 3. 提交（会自动触发推送！）
git commit -m "feat: 添加新功能"

# 输出示例:
# 🚀 A5L GitHub自动推送钩子
# ==========================================
# 📡 正在推送到GitHub...
#   分支: main
#   远程: https://github.com/zhangjinglsc-alt/a5l.git
#
# ✅ 自动推送成功！
# ==========================================
```

## ⚠️ 重要提醒

**推送仍然需要GitHub Token认证！**

钩子执行 `git push` 时会提示输入：
- Username: `zhangjinglsc-alt`
- Password: 你的GitHub Token

## 🔐 解决方案

### 方案A: 配置Git凭证存储（推荐）

```bash
# 启用凭证缓存（缓存15分钟）
git config --global credential.helper cache

# 或者永久存储（明文，注意安全）
git config --global credential.helper store
```

然后执行一次手动推送，输入Token后会被缓存：
```bash
git push origin main
# 输入用户名和Token
```

### 方案B: 使用SSH密钥（最安全）

```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "your@email.com"

# 添加公钥到GitHub
# https://github.com/settings/keys

# 修改远程URL为SSH
git remote set-url origin git@github.com:zhangjinglsc-alt/a5l.git
```

### 方案C: 更新远程URL包含Token（不推荐，Token会暴露在配置中）

```bash
# 注意：这会将Token保存在.git/config中
git remote set-url origin https://zhangjinglsc-alt:YOUR_TOKEN@github.com/zhangjinglsc-alt/a5l.git
```

## 🧪 测试钩子

执行以下命令测试自动推送：

```bash
cd /workspace/projects/workspace

# 创建一个测试文件
echo "$(date) - 测试自动推送" >> auto_push_test.log

# 提交（会自动推送）
git add auto_push_test.log
git commit -m "test: 验证自动推送钩子"

# 如果配置了凭证缓存，这次会自动推送成功
```

## 📊 当前配置

| 配置项 | 状态 |
|--------|------|
| Git Hooks | ✅ 已配置 |
| 自动推送 | ✅ 已启用 |
| 认证方式 | ⚠️ 需要配置 |

## 🎯 建议

**最简单的方案**：
1. 配置凭证缓存：`git config --global credential.helper cache`
2. 执行一次手动推送，输入Token
3. 之后15分钟内所有提交都会自动推送

**或者使用SSH**：
1. 生成SSH密钥
2. 添加到GitHub
3. 永久免密推送

---
*配置时间: 2026-05-02*
*钩子状态: 已启用*
