# GitHub仓库创建教程
**目标**: 创建 `a5l-upptime` 仓库用于状态监控
**适用**: Chief (张晋)

---

## 步骤1: 登录GitHub

1. 打开浏览器访问: https://github.com
2. 使用账号: `zhangjinglsc-alt` 登录
3. 确保已登录成功 (右上角显示头像)

---

## 步骤2: 进入创建页面

**方法一** (推荐):
- 直接访问: https://github.com/new

**方法二**:
- 点击右上角 `+` 号
- 选择 `New repository`

---

## 步骤3: 填写仓库信息

在创建页面填写以下内容:

| 字段 | 填写内容 | 说明 |
|:-----|:---------|:-----|
| **Repository name** | `a5l-upptime` | 仓库名称，必须完全一致 |
| **Description** | `A5L System Status Monitoring` | 描述 (可选) |
| **Public/Private** | ☑️ Public | 公开仓库 (Upptime需要) |
| **Add a README** | ☐ 不勾选 | 我们不使用默认README |
| **Add .gitignore** | ☐ 不勾选 | 我们已有配置文件 |
| **Choose a license** | ☐ 不勾选 | 不需要许可证 |

填写完成后点击 **Create repository** 按钮

---

## 步骤4: 验证创建成功

创建成功后，页面会跳转到:
`https://github.com/zhangjinglsc-alt/a5l-upptime`

页面显示:
```
zhangjinglsc-alt/a5l-upptime
Public

Quick setup — if you've done this kind of thing before
```

---

## 步骤5: 告诉我已创建

创建完成后，请回复我:
> "GitHub仓库已创建"

我会立即执行:
```bash
git push origin main
```

将Upptime配置推送到您的新仓库。

---

## 完整流程图

```
1. 打开 https://github.com/new
   ↓
2. Repository name: a5l-upptime
   ↓
3. 选择 Public
   ↓
4. 点击 Create repository
   ↓
5. 告诉我"已创建"
   ↓
6. 我推送配置
   ↓
7. 完成！
```

---

## 常见问题

**Q: 仓库名必须是 `a5l-upptime` 吗？**
A: 是的，这样统一好管理。

**Q: 必须是 Public 吗？**
A: 是的，Upptime的状态页面需要公开访问。

**Q: 创建错了怎么办？**
A: 可以删除重建。进入仓库 → Settings → Delete this repository。

**Q: 需要设置什么Secrets吗？**
A: 创建后我会告诉您如何设置 GH_PAT 和 FEISHU_WEBHOOK_URL。

---

## 下一步 (创建后)

仓库创建后，还需要:
1. 设置 GitHub Secrets (GH_PAT)
2. 配置飞书 Webhook
3. 启用 GitHub Actions

这些我后续会一步步教您。

---

**Chief，请按上述步骤创建仓库，然后告诉我！** 🚀
