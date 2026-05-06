# A5L 每日自动Commit配置

## ✅ 配置完成

**任务名称**: A5L每日自动Commit  
**执行时间**: 每天17:30 (Asia/Shanghai)  
**任务ID**: `83fb9e7e-4455-410c-952e-1f1500417aae`  
**脚本位置**: `/workspace/projects/workspace/scripts/auto_daily_commit.sh`  

---

## 🔄 自动Commit流程

每天17:30自动执行：

```
1. 检查工作目录是否有修改
   ├── 无修改 → 记录日志，结束
   └── 有修改 → 继续

2. 显示修改状态 (git status)

3. 添加所有修改 (git add -A)

4. 创建Commit
   消息: "auto: Daily backup YYYYMMDD"
   
5. 推送到GitHub (git push origin main)

6. 记录结果到日志
```

---

## 📊 日志文件

**日志位置**: `/workspace/projects/workspace/logs/auto_commit.log`

查看日志：
```bash
tail -f /workspace/projects/workspace/logs/auto_commit.log
```

---

## 🛠️ 手动测试

立即测试自动commit脚本：

```bash
# 执行脚本
/workspace/projects/workspace/scripts/auto_daily_commit.sh
```

---

## 📋 管理任务

### 查看所有cron任务
```bash
openclaw cron list
```

### 禁用任务
```bash
openclaw cron update 83fb9e7e-4455-410c-952e-1f1500417aae --enabled=false
```

### 启用任务
```bash
openclaw cron update 83fb9e7e-4455-410c-952e-1f1500417aae --enabled=true
```

### 删除任务
```bash
openclaw cron remove 83fb9e7e-4455-410c-952e-1f1500417aae
```

---

## 🎯 任务特点

| 特性 | 说明 |
|------|------|
| **定时** | 每天17:30执行 |
| **智能** | 无修改时不创建空commit |
| **日志** | 详细记录每次执行结果 |
| **安全** | 失败时不会中断其他任务 |
| **SSH** | 使用已配置的SSH免密推送 |

---

## 🔔 通知配置（可选）

如需飞书通知，创建配置文件：

```bash
mkdir -p /workspace/projects/workspace/config
cat > /workspace/projects/workspace/config/feishu_webhook.conf << 'EOF'
FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook-token"
EOF
```

---

## 🎉 完成！

**A5L现在每天17:30会自动备份到GitHub！**

- ✅ 自动检测修改
- ✅ 自动commit
- ✅ 自动推送到GitHub
- ✅ 详细日志记录

**再也不怕丢失工作了！** 🚀

---

*配置时间: 2026-05-02*  
*下次执行: 今天17:30*  
*状态: ✅ 已启用*
