# A5L 三重备份标准 SKILL

description: A5L所有角色产出强制执行三重备份：本地SSMG归档 → 飞书云文档 → GitHub版本控制。Chief触发词"三重备份"/"备份"自动执行。

**版本**: v1.0.0  
**生效日期**: 2026-05-06  
**强制级别**: P0 (最高)

---

## 🎯 核心原则

**所有A5L角色的所有产出，必须执行三重备份！**

> Chief触发词: **"三重备份"** / **"备份"**  
> 自动执行: 本地归档 → 飞书上传 → GitHub推送

---

## 📋 三重备份架构

```
┌─────────────────────────────────────────────────────────────┐
│  第一重: SSMG本地归档 (Local Archive)                       │
│  ├─ SOUL.md, SKILL.md, MEMORY.md, AGENTS.md                 │
│  ├─ memory/YYYY-MM-DD.md                                    │
│  ├─ data/simulation/plans/                                  │
│  └─ archive/YYYY-MM-DD/                                     │
├─────────────────────────────────────────────────────────────┤
│  第二重: 飞书云文档 (Cloud Archive)                         │
│  ├─ 空间2/30_每日批注/                                      │
│  ├─ 空间2/40_持仓与交易/                                    │
│  ├─ 空间2/50_研报中心/                                      │
│  └─ 多维表格SKILL注册表                                     │
├─────────────────────────────────────────────────────────────┤
│  第三重: GitHub版本控制 (Remote Archive)                    │
│  ├─ git add -A                                              │
│  ├─ git commit -m "backup: 三重备份自动执行"                │
│  └─ git push origin main                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎭 各角色产出备份清单

### Layer 0 - 六管理者

| 角色 | 产出类型 | 备份位置 | 频率 |
|:----:|:---------|:---------|:----:|
| **Chief Architect** | 架构决策、技术规范 | `AGENTS.md` + 飞书空间2 | 实时 |
| **CIO** | 交易计划、持仓日报 | `data/simulation/` + 飞书空间2/40_持仓与交易/ | 每小时 |
| **COO** | 执行方案、资源协调 | `docs/COO_*.md` + 飞书空间2 | 每日 |
| **CSO** | 安全检查报告 | `docs/CSO_*.md` + 飞书空间2 | 每日 |
| **Knowledge Guardian** | 知识库维护、批注 | `trading-review-wiki/` + 飞书空间2 | 每日 |
| **Report Manager** | 研报归档、分类 | `docs/REPORT_MANAGER_*.md` + 飞书空间2/50_研报中心/ | 每日 |

### Layer 1-5 - 技能产出

| 产出类型 | 本地归档 | 飞书归档 | GitHub |
|:---------|:---------|:---------|:-------|
| **SKILL.md** | skills/ | 空间2/SKILL注册表 | ✅ 提交 |
| **交易计划** | data/simulation/plans/ | 空间2/40_持仓与交易/ | ✅ 提交 |
| **日报/周报** | data/reports/ | 空间2/30_每日批注/ | ✅ 提交 |
| **配置文件** | config/ | 空间2/60_数据监控/ | ✅ 提交 |
| **代码脚本** | tools/, skills/ | 不上传(代码在GitHub) | ✅ 提交 |

---

## ⚡ 自动执行流程

### 触发条件

```python
# Chief说以下任一触发词:
triggers = ["三重备份", "备份", "triple backup", "archive now"]
```

### 执行命令

```bash
# 执行三重备份
cd /workspace/projects/workspace && \
python3 TOOLS/ssmg_archive_system.py && \
python3 TOOLS/feishu_auto_uploader.py && \
git add -A && \
git commit -m "backup: 三重备份自动执行 $(date +%Y-%m-%d-%H:%M)" && \
git push origin main
```

### 执行结果验证

| 层级 | 验证命令 | 成功标志 |
|:----:|:---------|:---------|
| 本地 | `ls -la archive/$(date +%Y-%m-%d)/` | 文件存在 |
| 飞书 | 检查云文档/多维表格 | 最新内容可见 |
| GitHub | `git log --oneline -1` | commit推送成功 |

---

## 🔧 关键配置文件

### 飞书同步配置
```json
// config/feishu_sync.json
{
  "backup_policy": "triple_backup",
  "local_archive": "archive/",
  "feishu_space_id": "空间2_ID",
  "github_repo": "zhangjinglsc-alt/a5l",
  "auto_backup": true
}
```

### GitHub推送配置
```bash
# .git/config
[remote "origin"]
    url = git@github.com:zhangjinglsc-alt/a5l.git
    fetch = +refs/heads/*:refs/remotes/origin/*
```

---

## 📊 备份状态监控

### 健康度指标

| 指标 | 权重 | 目标值 |
|:-----|:----:|:-------|
| 本地归档完成率 | 30% | 100% |
| 飞书上传成功率 | 30% | 100% |
| GitHub推送成功率 | 40% | 100% |

### 告警规则

```python
if local_backup_rate < 100:
    alert("P0: 本地归档失败!")
if feishu_upload_rate < 100:
    alert("P0: 飞书上传失败!")
if github_push_rate < 100:
    alert("P0: GitHub推送失败!")
```

---

## 🚨 紧急恢复流程

### 本地丢失 → 从GitHub恢复
```bash
git clone git@github.com:zhangjinglsc-alt/a5l.git
```

### 飞书丢失 → 从本地恢复
```bash
python3 TOOLS/feishu_auto_uploader.py --force-resync
```

### GitHub丢失 → 从本地推送
```bash
git push origin main --force
```

---

## 📝 CTO交付文档

**文档位置**: `docs/CTO_DELIVERY_TRIPLE_BACKUP_STANDARD.md`

**包含内容**:
1. 三重备份架构图
2. 各角色备份清单
3. 自动执行脚本
4. 监控告警配置
5. 紧急恢复流程

**更新记录**:
- 2026-05-06: v1.0.0 初始版本，Chief触发词"三重备份"生效

---

## ✅ 检查清单

- [x] SSMG本地归档系统部署
- [x] 飞书自动上传系统部署
- [x] GitHub自动推送钩子配置
- [x] Chief触发词"三重备份"绑定
- [ ] 所有角色产出自动触发备份（开发中）
- [ ] 备份健康度监控面板（开发中）

---

**CTO承诺**: 所有A5L产出，无一例外，强制执行三重备份！
