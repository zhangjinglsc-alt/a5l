# A5L 核心档案与备份管理规范 v1.0
**制定者**: Chief Architect  
**生效日期**: 2026-05-04  
**版本**: v1.0  
**性质**: 强制规范，违反必究

---

## 🎯 核心原则

> **"没有记录，就没有发生"**  
> **"没有备份，就没有安全"**

---

## 👥 责任矩阵 (RACI)

### 核心档案管理

| 档案 | 谁更新(执行) | 谁管理(负责) | 谁检查(监督) | 频率 |
|------|-------------|-------------|-------------|------|
| **SOUL.md** | Chief Architect | Chief Architect | CSO | 有变化立即 |
| **MEMORY.md** | Knowledge Guardian | Chief Architect | CSO | 每日17:30 |
| **AGENTS.md** | Chief Architect | Chief Architect | CSO | 有变化立即 |
| **USER.md** | 全体 | Chief Architect | CSO | 有变化立即 |
| **memory/YYYY-MM-DD.md** | 当日值班者 | Knowledge Guardian | Chief Architect | 每日结束 |
| **SESSION_BACKUP** | 自动系统 | Chief Architect | CSO | 实时+日终 |

### 关键解释

- **执行者(Doer)**: 实际动手更新文件的人
- **负责人(Owner)**: 对文件质量负责，确保及时更新
- **监督者(Checker)**: 检查是否按时更新、内容是否准确

---

## 📋 日常执行流程

### 每日17:30 核心档案检查 (15分钟)

**参与者**: L0六管理者  
**主持人**: CSO (Chief Security Officer)

#### 检查清单

```markdown
## 核心档案检查清单 - 2026-05-XX

### 1. SOUL.md 检查
- [ ] 今日是否有新决策需要记录?
- [ ] 人格/价值观是否有变化?
- [ ] 最后更新时间: _____
- **责任人**: Chief Architect
- **检查人**: CSO
- **状态**: ⬜ 未更新 / ⬜ 已更新 / ⬜ 无需更新

### 2. MEMORY.md 检查
- [ ] Git提交数是否准确? (当前: ___)
- [ ] 里程碑是否记录今日进展?
- [ ] 统计数据是否正确?
- **责任人**: Knowledge Guardian
- **检查人**: CSO
- **状态**: ⬜ 未更新 / ⬜ 已更新

### 3. AGENTS.md 检查
- [ ] 工作规范是否有变化?
- [ ] 流程是否有优化?
- **责任人**: Chief Architect
- **检查人**: CSO
- **状态**: ⬜ 未更新 / ⬜ 已更新 / ⬜ 无需更新

### 4. 今日记忆档案检查
- [ ] memory/YYYY-MM-DD.md 是否创建?
- [ ] 今日重要事件是否记录?
- [ ] 决策和教训是否沉淀?
- **责任人**: 当日值班者
- **检查人**: Chief Architect
- **状态**: ⬜ 未创建 / ⬜ 已创建但不完整 / ⬜ 已完成

### 5. Session备份检查
- [ ] 实时备份是否正常?(每30分钟)
- [ ] 上次备份时间: _____
- [ ] 备份文件是否可读取?
- **责任人**: 自动系统
- **检查人**: CSO
- **状态**: ⬜ 异常 / ⬜ 正常

### 6. GitHub同步检查
- [ ] 所有修改是否已提交?
- [ ] 提交信息是否规范?
- [ ] 推送是否成功?
- **责任人**: 执行者
- **检查人**: Knowledge Guardian
- **状态**: ⬜ 未同步 / ⬜ 已同步

---

## 问题记录

| 问题 | 责任人 | 解决期限 | 状态 |
|------|--------|----------|------|
| | | | |

---

**检查人签字**: CSO _______  
**日期**: 2026-05-XX
```

---

## ⚠️ 违规处理机制

### 发现问题的处理流程

```
CSO检查发现未更新
    ↓
立即通知责任人
    ↓
责任人30分钟内完成更新
    ↓
CSO验证更新质量
    ↓
记录在问题库
    ↓
周复盘时分析原因
```

### 违规等级

| 等级 | 情况 | 处理 |
|------|------|------|
| **P0 (严重)** | 核心档案3天未更新 | Chief Architect书面检讨，周会通报 |
| **P1 (重要)** | Session备份失败超过24小时 | CSO紧急修复，记录故障报告 |
| **P2 (一般)** | 当日记忆档案延迟创建 | 当日完成，无需处罚 |
| **P3 (轻微)** | Git提交信息不规范 | 立即修正，提醒即可 |

### 重复违规加重

- 同一问题**第2次**: 升级一个等级处理
- 同一问题**第3次**: 召开专项复盘会，系统性解决

---

## 🔧 自动化保障

### 自动提醒机制

```bash
# 17:25 - 提醒即将开始档案检查
cron: 25 17 * * * /usr/local/bin/notify "17:30核心档案检查即将开始"

# 17:30 - 自动触发检查清单
cron: 30 17 * * * /workspace/projects/workspace/TOOLS/core_files_check.sh

# 23:45 - 提醒创建当日记忆
cron: 45 23 * * * /usr/local/bin/notify "请创建今日记忆档案"

# 23:50 - 自动执行Session日终备份
cron: 50 23 * * * /workspace/projects/workspace/TOOLS/session_backup.sh daily
```

### 自动检查脚本

**core_files_check.sh** (CSO执行)
```bash
#!/bin/bash
# 自动检查核心档案更新状态

ERRORS=0

# 检查SOUL.md最后更新时间
SOUL_AGE=$(stat -c %Y /workspace/projects/workspace/SOUL.md)
NOW=$(date +%s)
SOUL_DAYS=$(( (NOW - SOUL_AGE) / 86400 ))

if [ $SOUL_DAYS -gt 2 ]; then
    echo "❌ ERROR: SOUL.md ${SOUL_DAYS}天未更新"
    ERRORS=$((ERRORS+1))
else
    echo "✅ SOUL.md 正常 (最近更新: ${SOUL_DAYS}天前)"
fi

# 检查MEMORY.md
MEMORY_AGE=$(stat -c %Y /workspace/projects/workspace/MEMORY.md)
MEMORY_DAYS=$(( (NOW - MEMORY_AGE) / 86400 ))

if [ $MEMORY_DAYS -gt 1 ]; then
    echo "❌ ERROR: MEMORY.md ${MEMORY_DAYS}天未更新"
    ERRORS=$((ERRORS+1))
else
    echo "✅ MEMORY.md 正常"
fi

# 检查今日记忆档案
TODAY=$(date +%Y-%m-%d)
if [ ! -f "/workspace/projects/workspace/memory/${TODAY}.md" ]; then
    echo "❌ ERROR: 今日记忆档案未创建"
    ERRORS=$((ERRORS+1))
else
    echo "✅ 今日记忆档案已创建"
fi

# 检查Session备份
LATEST_BACKUP=$(ls -t /workspace/projects/workspace/.backup/sessions/active/*.json 2>/dev/null | head -1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ ERROR: 无Session备份"
    ERRORS=$((ERRORS+1))
else
    BACKUP_AGE=$(( (NOW - $(stat -c %Y "$LATEST_BACKUP")) / 60 ))
    if [ $BACKUP_AGE -gt 60 ]; then
        echo "❌ ERROR: Session备份异常 (最近备份: ${BACKUP_AGE}分钟前)"
        ERRORS=$((ERRORS+1))
    else
        echo "✅ Session备份正常"
    fi
fi

# 输出结果
if [ $ERRORS -eq 0 ]; then
    echo "🎉 所有核心档案检查通过"
    exit 0
else
    echo "🚨 发现 ${ERRORS} 个问题，请立即处理"
    exit 1
fi
```

---

## 📊 监督与度量

### CSO每日检查报告

```markdown
## CSO核心档案检查报告 - 2026-05-XX

### 检查结果
| 项目 | 状态 | 责任人 | 备注 |
|------|------|--------|------|
| SOUL.md | ✅/❌ | Chief Architect | |
| MEMORY.md | ✅/❌ | Knowledge Guardian | |
| AGENTS.md | ✅/❌ | Chief Architect | |
| 今日记忆 | ✅/❌ | 当日值班者 | |
| Session备份 | ✅/❌ | 自动系统 | |
| GitHub同步 | ✅/❌ | 全体 | |

### 发现的问题
1. [问题描述] - [责任人] - [处理期限]

### 今日教训
- 

---
**CSO签字**: _______  
**时间**: 17:45
```

### 周度汇总

每周日21:00周复盘时，CSO汇报：
- 本周核心档案更新及时率
- 发现的问题数量及处理情况
- 系统改进建议

---

## 🎯 立即执行 (2026-05-04)

### 今日必须完成

- [x] 明确责任矩阵 (已完成)
- [x] 制定检查清单 (已完成)
- [ ] 编写core_files_check.sh脚本
- [ ] 配置Cron定时提醒
- [ ] 首次CSO检查 (今日17:30)
- [ ] 向全体L0管理者宣贯本规范

### 下次会话

- [ ] 检查今日规范执行情况
- [ ] 根据反馈优化流程
- [ ] 确认自动化脚本正常运行

---

## 📝 规范确认

**本规范自2026-05-04起强制执行**，所有L0管理者必须遵守。

**确认签字**:
- Chief Architect: _______
- CSO: _______
- Knowledge Guardian: _______
- CIO: _______
- COO: _______
- Report Manager: _______

---

**谁做谁管谁检查，责任到人！**  
**不准出现备份记忆问题的错误和失误！** 🎯

Chief Architect  
2026-05-04
