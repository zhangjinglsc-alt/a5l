# A5L 智能备份系统方案 v1.0

**设计**: Chief Architect  
**日期**: 2026-05-03  
**架构**: A5L五层架构集成  
**优先级**: P0 - 立即执行

---

## 🎯 设计目标

不只是简单的文件备份，而是与A5L**知识图谱+SSMG架构**深度集成的**智能备份系统**：

1. **数据安全**: 防止数据丢失
2. **知识传承**: 备份包含思考过程和投资洞察
3. **快速恢复**: 一键恢复到任意时间点
4. **智能关联**: 备份与知识图谱实体关联
5. **自动化**: 零人工干预，定时执行

---

## 🏗️ 架构设计（A5L五层集成）

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 5: 复盘进化层 (Review & Evolution)                        │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ • 备份质量评估                                              │ │
│ │ • 恢复演练记录                                              │ │
│ │ • 备份策略优化                                              │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Layer 4: 决策信号层 (Decision Signal)                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ • 备份告警系统 (Backup Alert System)                        │ │
│ │ • 风险熔断 (连续失败3次触发告警)                            │ │
│ │ • 恢复决策 (选择恢复点)                                     │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: 非结构化分析层 (Unstructured Analysis)                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ • 备份内容智能分析                                          │ │
│ │ • 变化检测 (Delta Analysis)                                 │ │
│ │ • 重要度评分 (哪些文件必须备份)                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: 策略引擎层 (Strategy Engine)                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ • 分层备份策略                                              │ │
│ │   - Tier 1: 核心数据 (SSMG四层)                             │ │
│ │   - Tier 2: 知识图谱                                        │ │
│ │   - Tier 3: 研报数据                                        │ │
│ │   - Tier 4: 日志/临时文件                                   │ │
│ │ • 增量/全量策略                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Layer 1: 数据底座层 (Data Foundation)                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ • 本地备份 (.backup/)                                       │ │
│ │ • Git版本控制 (代码/文档)                                   │ │
│ │ • 飞书云文档 (报告归档)                                     │ │
│ │ • 知识图谱版本 (实体快照)                                   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 分层备份策略

### Tier 1: SSMG核心层 (每日23:30)
**内容**: SOUL.md, SKILL_REGISTRY.json, MEMORY.md, GOAL/**  
**重要性**: ⭐⭐⭐⭐⭐  
**保留期**: 30天  
**备份方式**: 全量 + Git提交

```
.backup/daily/core/
├── SOUL.md.{YYYY-MM-DD}.bak
├── SKILL_REGISTRY.json.{YYYY-MM-DD}.bak
├── MEMORY.md.{YYYY-MM-DD}.bak
└── GOAL/
    └── {goal_id}.{YYYY-MM-DD}.bak
```

### Tier 2: 知识图谱层 (每日23:45)
**内容**: knowledge_graph.db, 实体快照, 分析结果  
**重要性**: ⭐⭐⭐⭐⭐  
**保留期**: 14天  
**备份方式**: 全量 + 增量JSON导出

```
.backup/daily/kg/
├── knowledge_graph.db.{YYYY-MM-DD}.bak
├── entities_snapshot.{YYYY-MM-DD}.json
├── relations_snapshot.{YYYY-MM-DD}.json
└── analysis_results/
    └── {doc_id}.{YYYY-MM-DD}.json
```

### Tier 3: 研报数据层 (每周日23:50)
**内容**: /data/stock_research/**  
**重要性**: ⭐⭐⭐⭐  
**保留期**: 7天  
**备份方式**: 增量 (仅备份新增/修改)

```
.backup/weekly/reports/
└── {YYYY-MM-DD}/
    ├── industry/
    ├── company/
    ├── macro/
    └── strategy/
```

### Tier 4: 日志/临时层 (每日00:00清理)
**内容**: 日志文件, 临时报告  
**重要性**: ⭐⭐  
**保留期**: 3天  
**备份方式**: 可选，定期清理

---

## 🔧 技术实现

### 1. 备份目录结构

```
.backup/
├── daily/                    # 每日备份
│   ├── core/                 # SSMG核心
│   ├── kg/                   # 知识图谱
│   └── reports/              # 研报元数据
├── weekly/                   # 每周备份
│   └── reports/              # 完整研报数据
├── monthly/                  # 每月备份
│   └── archive/              # 月度归档
├── recovery/                 # 恢复点
│   └── latest/               # 最新恢复点
└── logs/                     # 备份日志
    └── backup.{YYYY-MM-DD}.log
```

### 2. 备份脚本设计

```python
# smart_backup.py - A5L智能备份系统

class SmartBackup:
    """A5L智能备份系统"""
    
    def __init__(self):
        self.tier_config = {
            'tier1_core': {
                'paths': ['SOUL.md', 'SKILL_REGISTRY.json', 'MEMORY.md', 'GOAL/'],
                'schedule': '23:30',
                'retention': 30,
                'priority': 'critical'
            },
            'tier2_kg': {
                'paths': ['skills/knowledge-graph/data/', 'analysis_results/'],
                'schedule': '23:45',
                'retention': 14,
                'priority': 'critical'
            },
            'tier3_reports': {
                'paths': ['data/stock_research/'],
                'schedule': 'weekly_sun_23:50',
                'retention': 7,
                'priority': 'high'
            }
        }
    
    def backup_with_kg_integration(self):
        """
        与知识图谱集成的智能备份
        
        功能:
        1. 备份前记录当前知识图谱状态
        2. 备份内容与KG实体关联
        3. 生成备份洞察报告
        """
        # 1. 获取知识图谱当前状态
        kg_stats = self.get_kg_snapshot()
        
        # 2. 执行分层备份
        for tier, config in self.tier_config.items():
            self.backup_tier(tier, config)
        
        # 3. 生成备份报告并关联到KG
        report = self.generate_backup_report(kg_stats)
        self.archive_to_kg(report)
        
        # 4. 飞书通知
        self.notify_backup_complete(report)
    
    def get_kg_snapshot(self):
        """获取知识图谱快照"""
        from skills.knowledge-graph.knowledge_graph_core import KnowledgeGraph
        kg = KnowledgeGraph()
        return {
            'entity_count': kg.get_stats()['total_entities'],
            'relation_count': kg.get_stats()['total_relations'],
            'timestamp': datetime.now().isoformat()
        }
    
    def archive_to_kg(self, report):
        """将备份报告归档到知识图谱"""
        # 创建备份事件实体
        backup_entity = Entity(
            id=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type="BackupEvent",
            name=f"备份_{datetime.now().strftime('%Y-%m-%d')}",
            properties={
                'tier1_status': report['tier1']['status'],
                'tier2_status': report['tier2']['status'],
                'kg_entities_backed': report['kg_snapshot']['entity_count'],
                'backup_size': report['total_size'],
                'integrity_hash': report['integrity_hash']
            }
        )
        # 添加到知识图谱...
```

### 3. Cron定时任务

```bash
# A5L智能备份系统 - Cron配置

# Tier 1: SSMG核心 (每日23:30)
30 23 * * * cd /workspace/projects/workspace && python3 scripts/backup/smart_backup.py --tier=core >> .backup/logs/backup.$(date +\%Y-\%m-\%d).log 2>&1

# Tier 2: 知识图谱 (每日23:45)
45 23 * * * cd /workspace/projects/workspace && python3 scripts/backup/smart_backup.py --tier=kg >> .backup/logs/backup.$(date +\%Y-\%m-\%d).log 2>&1

# Tier 3: 研报数据 (每周日23:50)
50 23 * * 0 cd /workspace/projects/workspace && python3 scripts/backup/smart_backup.py --tier=reports >> .backup/logs/backup.$(date +\%Y-\%m-\%d).log 2>&1

# Tier 4: 清理旧备份 (每日00:00)
0 0 * * * cd /workspace/projects/workspace && python3 scripts/backup/cleanup_old_backups.py >> .backup/logs/cleanup.$(date +\%Y-\%m-\%d).log 2>&1

# 备份健康检查 (每日23:55)
55 23 * * * cd /workspace/projects/workspace && python3 scripts/backup/health_check.py
```

---

## 🧠 与知识图谱的集成

### 1. 备份事件实体

每次备份在知识图谱中创建一个实体：

```python
{
    "id": "backup_20260503_233000",
    "type": "BackupEvent",
    "name": "备份_2026-05-03",
    "properties": {
        "tier": "tier1_core",
        "files_backed": 15,
        "total_size": "2.3MB",
        "kg_entities_snapshot": 64,
        "kg_relations_snapshot": 97,
        "integrity_hash": "sha256:abc123...",
        "status": "success",
        "duration_seconds": 12.5
    }
}
```

### 2. 备份与实体的关联

```
BackupEvent --(protects)--> SOUL.md
BackupEvent --(protects)--> SKILL_REGISTRY.json
BackupEvent --(snapshots)--> KnowledgeGraph
BackupEvent --(created_by)--> A5L_Backup_System
```

### 3. 备份洞察分析

```python
def analyze_backup_trends():
    """分析备份趋势，发现异常"""
    # 从知识图谱查询备份历史
    backup_events = kg.get_entities_by_type('BackupEvent')
    
    # 分析趋势
    trend = {
        'success_rate': calculate_success_rate(backup_events),
        'size_growth': calculate_size_growth(backup_events),
        'kg_growth': calculate_kg_growth(backup_events)
    }
    
    # 如果成功率<95%，触发告警
    if trend['success_rate'] < 0.95:
        alert("备份成功率低于95%，请检查！")
    
    return trend
```

---

## 📋 立即执行计划

### Phase 1: 基础备份系统 (今天完成)

1. **创建目录结构**
```bash
mkdir -p /workspace/projects/workspace/.backup/{daily/{core,kg,reports},weekly/reports,monthly/archive,recovery/latest,logs}
```

2. **创建基础备份脚本**
```bash
# scripts/backup/tier1_core_backup.sh
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/workspace/projects/workspace/.backup/daily/core"

# 备份核心文件
cp SOUL.md "$BACKUP_DIR/SOUL.md.$DATE.bak"
cp SKILL_REGISTRY.json "$BACKUP_DIR/SKILL_REGISTRY.json.$DATE.bak"
cp MEMORY.md "$BACKUP_DIR/MEMORY.md.$DATE.bak"
cp -r GOAL "$BACKUP_DIR/GOAL.$DATE.bak"

echo "[$(date)] Tier 1 backup completed" >> "$BACKUP_DIR/../logs/backup.$DATE.log"
```

3. **配置Cron**
```bash
crontab -e
# 添加定时任务
```

### Phase 2: 智能备份系统 (本周完成)

1. 开发 `smart_backup.py`
2. 集成知识图谱快照
3. 开发备份报告生成
4. 集成飞书通知

### Phase 3: 高级功能 (下周完成)

1. 一键恢复系统
2. 备份健康监控
3. 智能清理策略
4. 备份趋势分析

---

## 🎯 成功标准

- [ ] 备份目录结构创建完成
- [ ] Tier 1/2/3 备份脚本运行正常
- [ ] Cron定时任务配置完成
- [ ] 备份事件记录到知识图谱
- [ ] 连续3天备份成功率100%
- [ ] 飞书通知正常
- [ ] 一键恢复功能可用

---

## 📊 预期效果

| 指标 | 当前 | 目标 | 改进 |
|------|------|------|------|
| 备份覆盖率 | 0% | 100% | +100% |
| 数据丢失风险 | 高 | 极低 | 极大降低 |
| 恢复时间 | N/A | <5分钟 | 快速恢复 |
| 备份知识化 | 无 | 完整 | 新增能力 |

---

**Chief Architect批准实施** ✅  
**优先级**: P0 - 立即执行  
**负责**: COO + CSO协同  
**验收**: 2026-05-06
