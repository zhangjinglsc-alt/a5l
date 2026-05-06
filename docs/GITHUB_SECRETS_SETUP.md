# GitHub Secrets 设置教程
**目标**: 启用Upptime监控告警
**仓库**: https://github.com/zhangjinglsc-alt/a5l-upptime

---

## 需要设置的 Secrets

| Secret名称 | 用途 | 获取方式 |
|:-----------|:-----|:---------|
| `GH_PAT` | GitHub访问权限 | 创建Personal Access Token |
| `FEISHU_WEBHOOK_URL` | 飞书告警通知 | 飞书机器人Webhook |

---

## 步骤1: 设置 GH_PAT

### 1.1 创建 Personal Access Token

1. 访问: https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 填写信息:
   - **Note**: `A5L Upptime`
   - **Expiration**: 选择 `No expiration` (或30天)
   - **Scopes**: 勾选以下权限:
     - ☑️ `repo` (完整仓库权限)
     - ☑️ `workflow` (工作流权限)
4. 点击 **Generate token**
5. **立即复制token** (只显示一次！)

### 1.2 添加到仓库Secrets

1. 访问: https://github.com/zhangjinglsc-alt/a5l-upptime/settings/secrets/actions
2. 点击 **New repository secret**
3. 填写:
   - **Name**: `GH_PAT`
   - **Secret**: [粘贴刚才复制的token]
4. 点击 **Add secret**

---

## 步骤2: 设置 FEISHU_WEBHOOK_URL

### 2.1 获取飞书Webhook (如果已有请跳过)

1. 打开飞书，进入需要接收告警的群组
2. 点击群设置 → 群机器人 → 添加机器人
3. 选择 **自定义机器人**
4. 机器人名称: `A5L监控告警`
5. 复制 **Webhook地址**

格式类似:
```
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 2.2 添加到仓库Secrets

1. 访问: https://github.com/zhangjinglsc-alt/a5l-upptime/settings/secrets/actions
2. 点击 **New repository secret**
3. 填写:
   - **Name**: `FEISHU_WEBHOOK_URL`
   - **Secret**: [粘贴飞书Webhook URL]
4. 点击 **Add secret**

---

## 步骤3: 启用GitHub Actions

1. 访问: https://github.com/zhangjinglsc-alt/a5l-upptime/actions
2. 如果看到提示 "Workflows aren't being run on this repository"
3. 点击 **I understand my workflows, go ahead and enable them**

---

## 验证配置

设置完成后，访问:  
https://github.com/zhangjinglsc-alt/a5l-upptime/settings/secrets/actions

应该看到两个Secrets:
- ☑️ GH_PAT
- ☑️ FEISHU_WEBHOOK_URL

---

## 预期效果

配置完成后:
1. **每5分钟**自动检查所有服务状态
2. **服务宕机时**自动在飞书发送告警
3. **状态页面**: https://zhangjinglsc-alt.github.io/a5l-upptime

---

## 监控的服务列表

| 服务 | 检查频率 |
|:-----|:---------|
| A5L Gateway | 5分钟 |
| GitHub Repository | 5分钟 |
| Feishu API | 5分钟 |
| Finnhub API | 5分钟 |
| A5L Documentation | 5分钟 |
| GitHub API | 5分钟 |

---

**Chief，请按上述步骤设置Secrets，然后告诉我"已设置"！** 🚀

设置完成后监控就会立即启动！
