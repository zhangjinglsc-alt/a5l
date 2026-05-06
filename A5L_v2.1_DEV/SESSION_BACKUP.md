# SESSION_BACKUP.md - Session备份与恢复规范
**制定者**: Chief Architect  
**生效日期**: 2026-05-04  
**版本**: v1.0

---

## 🚨 问题发现

**2026-05-04 发现**: A5L完全没有session备份机制！
- 会话上下文丢失风险
- 工作进度无法恢复
- 重要决策可能遗漏

**立即建立备份机制！**

---

## 📋 Session备份规范

### 备份频率

| 类型 | 频率 | 触发条件 | 保留时间 |
|------|------|----------|----------|
| **实时备份** | 每30分钟 | 自动执行 | 24小时 |
| **任务完成备份** | 每次任务结束 | 手动/自动触发 | 永久 |
| **日终备份** | 每天23:50 | 自动执行 | 30天 |
| **重要节点备份** | 里程碑达成 | 手动触发 | 永久 |

### 备份内容

```
session_backup/
├── active/                    # 实时备份 (最近24小时)
│   ├── session_20260504_1430.json
│   ├── session_20260504_1500.json
│   └── ...
├── daily/                     # 日终备份 (保留30天)
│   ├── 2026-05-04/
│   │   ├── session_final.json
│   │   ├── memory_state.json
│   │   └── task_progress.json
│   └── ...
├── milestones/                # 里程碑备份 (永久保留)
│   ├── v2.0.0-alpha-release/
│   ├── 7-research-reports-complete/
│   └── ...
└── recovery/                  # 恢复点
    └── latest_recovery_point.json
```

### 备份数据内容

```json
{
  "session_id": "uuid",
  "timestamp": "2026-05-04T15:00:00+08:00",
  "context": {
    "working_directory": "/workspace/projects/workspace",
    "active_task": "当前任务描述",
    "pending_tasks": ["任务1", "任务2"]
  },
  "memory": {
    "short_term": "短期记忆摘要",
    "working_context": "工作上下文"
  },
  "files_modified": ["修改的文件列表"],
  "decisions_made": ["决策记录"],
  "git_state": {
    "branch": "main",
    "last_commit": "commit_hash",
    "uncommitted_changes": ["文件列表"]
  }
}
```

---

## 🔄 备份执行流程

### 自动备份 (Cron任务)

```bash
# 每30分钟执行一次实时备份
*/30 * * * * /workspace/projects/workspace/TOOLS/session_backup.sh --mode=realtime

# 每天23:50执行日终备份
50 23 * * * /workspace/projects/workspace/TOOLS/session_backup.sh --mode=daily
```

### 手动备份命令

```bash
# 任务完成备份
openclaw session backup --task="任务名称" --importance=high

# 里程碑备份
openclaw session backup --milestone="里程碑名称" --tag=v2.0.0

# 查看备份列表
openclaw session list-backups

# 恢复到指定时间点
openclaw session restore --timestamp="2026-05-04T15:00:00"
```

---

## 📊 备份检查清单

### 每次会话结束前必须检查

- [ ] 重要决策是否已记录到memory/YYYYMMDD.md
- [ ] 修改的文件是否已Git提交
- [ ] 未完成任务是否已记录
- [ ] Session备份是否已执行
- [ ] 关键上下文是否已保存

### 每日检查 (Chief Architect职责)

- [ ] 检查当日备份是否完整
- [ ] 验证备份文件可读取
- [ ] 确认重要里程碑已备份
- [ ] 清理过期备份(>30天)

---

## 🆘 恢复流程

### 场景1: 会话异常中断

```bash
1. 启动新会话
2. 执行: openclaw session restore --latest
3. 检查恢复状态
4. 继续未完成任务
```

### 场景2: 恢复到指定时间点

```bash
1. 查看备份列表: openclaw session list-backups
2. 选择恢复点: openclaw session restore --timestamp="2026-05-04T15:00"
3. 确认恢复内容
4. 继续工作
```

---

## ⚠️ 重要提醒

### 谁负责备份?

**Chief Architect** - 确保备份机制运行
**Knowledge Guardian** - 管理备份文件归档
**每位L0管理者** - 在重要节点手动触发备份

### 什么时候必须备份?

1. **重要决策后** - 立即备份决策上下文
2. **任务完成后** - 备份任务产出和总结
3. **里程碑达成** - 永久备份里程碑状态
4. **会话结束前** - 备份当前工作状态
5. **重大变更前** - 备份以便回滚

### 备份失败怎么办?

1. 立即通知Chief Architect
2. 手动执行备份命令
3. 检查磁盘空间和权限
4. 记录备份失败原因

---

## 📈 备份效果度量

| 指标 | 目标 | 检查频率 |
|------|------|----------|
| 备份成功率 | >99% | 每日 |
| 恢复成功率 | 100% | 每周测试 |
| 备份及时率 | 100% | 每日 |
| 存储使用率 | <80% | 每周 |

---

## 🔧 立即执行 (2026-05-04)

### 今日必须完成

- [ ] 创建session_backup目录结构
- [ ] 编写session_backup.sh脚本
- [ ] 配置Cron定时任务
- [ ] 手动执行首次备份
- [ ] 验证备份可恢复

### 下次会话检查

- [ ] 确认备份机制正常运行
- [ ] 检查昨日备份完整性
- [ ] 测试恢复流程

---

**Session备份机制建立完成！** 🛡️

Chief Architect  
2026-05-04 (立即生效)
