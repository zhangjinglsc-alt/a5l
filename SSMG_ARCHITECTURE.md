# SOUL-SKILL-MEMORY-GOAL 整合架构
# 记忆增强型Goal-Oriented系统

## 核心理念
> "一个完整的Agent需要知道：我是谁(SOUL)、我会什么(SKILL)、我经历过什么(MEMORY)、我要成为什么(GOAL)"

---

## 四层架构

### Layer 1: SOUL (灵魂层) - 身份定义
**文件**: `SOUL.md` (主宪章) + `SOUL_HISTORY.md` (版本记录)

**内容**:
- 核心身份定义
- 价值观与行为准则
- 能力清单 (引用SKILL层)
- 进化里程碑 (引用GOAL层)
- 重要记忆摘要 (引用MEMORY层)

**更新机制**:
- 每次重大进化后自动更新
- 保留历史版本 (SOUL_HISTORY)
- 人类可随时审阅和修正

---

### Layer 2: SKILL (技能层) - 能力定义
**文件**: `SKILL_REGISTRY.json` (技能注册表) + `skills/` (代码实现)

**内容**:
```json
{
  "skills": [
    {
      "id": "factor_investing",
      "name": "因子投资",
      "location": "skills/factor-investing/SKILL.md",
      "proficiency": 0.85,  // 熟练度 0-1
      "usage_count": 42,    // 使用次数
      "last_used": "2026-05-01",
      "success_rate": 0.92  // 成功率
    }
  ],
  "total_skills": 54,
  "categories": {...}
}
```

**整合点**:
- SOUL.md中引用"我有50+技能"
- Goal执行时自动匹配skill
- 每次使用后更新熟练度

---

### Layer 3: MEMORY (记忆层) - 经验沉淀
**三个子系统**:

#### 3.1 长期记忆 (Long-term Memory)
- **文件**: `MEMORY.md` (精华摘要)
- **内容**: 重要决策、成功经验、失败教训、核心认知
- **更新**: 每周回顾memory/*.md，萃取精华写入MEMORY.md
- **用途**: 快速加载核心上下文

#### 3.2 工作记忆 (Working Memory)
- **文件**: `memory/working_memory.json`
- **内容**: 
  ```json
  {
    "active_goals": ["G001"],
    "current_tasks": ["T001", "T002"],
    "recent_context": {...},
    "session_id": "..."
  }
  ```
- **更新**: 实时更新
- **用途**: 当前对话上下文

#### 3.3 情景记忆 (Episodic Memory)
- **文件**: `memory/YYYY-MM-DD.md` (每日记录)
- **内容**: 详细对话历史、具体事件、执行日志
- **更新**: 每次对话/任务后追加
- **用途**: 追溯具体事件、复盘分析

#### 3.4 语义记忆 (Semantic Memory)
- **文件**: `memory_palace/` (向量化存储)
- **技术**: 嵌入向量 + 相似度检索
- **内容**: 所有记忆的向量化表示
- **用途**: 快速检索相关经验

**整合点**:
- Goal执行前检索相关记忆
- 执行后萃取经验写入记忆
- SOUL.md引用重要记忆

---

### Layer 4: GOAL (目标层) - 方向定义
**文件**: `data/goals/` (活跃目标) + `data/goals_archive/` (历史目标)

**内容**:
```json
{
  "id": "G001",
  "title": "实现L3半自主进化",
  "status": "active",
  "created_at": "2026-05-01",
  "deadline": "2026-05-15",
  "progress": 35,
  "tasks": [...],
  "memory_refs": ["2026-05-01-evolution"],  // 关联记忆
  "skill_refs": ["agent_evolution", "goal_management"],  // 使用技能
  "soul_impact": "增强自主能力，向L3进化"  // 对SOUL的影响
}
```

**整合点**:
- 每个Goal关联相关SKILL
- 每个Goal产生MEMORY
- 重大Goal完成后更新SOUL

---

## 启动加载流程

### 会话启动时
```python
def session_startup():
    # 1. 加载SOUL (定义身份)
    soul = load_soul()
    print(f"身份加载: {soul['name']} - {soul['core_identity']}")
    
    # 2. 加载SKILL (定义能力)
    skills = load_skill_registry()
    print(f"技能加载: {skills['total_skills']} 个技能就绪")
    
    # 3. 加载MEMORY (定义经验)
    # 3.1 长期记忆 (快速上下文)
    long_term = load_memory_summary()
    # 3.2 工作记忆 (当前状态)
    working = load_working_memory()
    # 3.3 情景记忆 (最近对话)
    recent = load_recent_episodes(7)
    print(f"记忆加载: {len(recent)} 天历史 + {len(long_term)} 条精华")
    
    # 4. 加载GOAL (定义方向)
    active_goals = load_active_goals()
    print(f"目标加载: {len(active_goals)} 个活跃目标")
    for goal in active_goals:
        print(f"   - {goal['title']}: {goal['progress']}%")
    
    # 5. 整合上下文
    context = {
        "soul": soul,
        "skills": skills,
        "memory": {
            "long_term": long_term,
            "working": working,
            "recent": recent
        },
        "goals": active_goals
    }
    
    return context
```

---

## 运行时整合机制

### 执行Task时的记忆流程

```
收到Task
   │
   ▼
[记忆检索] ──► 检索相似历史任务 ──► 获取经验教训
   │
   ▼
[技能匹配] ──► 根据Task类型匹配Skill ──► 检查熟练度
   │
   ▼
[Goal对齐] ──► 检查是否对齐活跃Goal ──► 更新Goal进度
   │
   ▼
执行Task
   │
   ▼
[经验萃取] ──► 成功/失败模式 ──► 写入Memory
   │
   ▼
[SOUL评估] ──► 是否重大认知更新 ──► 必要时更新SOUL
   │
   ▼
[Skill更新] ──► 更新使用次数/熟练度
   │
   ▼
[Goal更新] ──► 更新进度/产出关联
```

---

## 文件结构

```
workspace/
├── SOUL.md                      # 灵魂宪章 (当前版本)
├── SOUL_HISTORY.md              # SOUL版本历史
├── SKILL_REGISTRY.json          # 技能注册表
├── MEMORY.md                    # 长期记忆精华
├── memory/                      # 情景记忆
│   ├── working_memory.json      # 工作记忆
│   ├── 2026-05-01.md           # 每日记录
│   ├── 2026-04-30.md
│   └── ...
├── memory_palace/               # 语义记忆
│   └── ...
├── data/goals/                  # 活跃目标
│   ├── goals.json
│   └── G001_tasks.json
├── data/goals_archive/          # 历史目标
│   └── ...
└── skills/                      # 技能实现
    └── ...
```

---

## 关键整合点

### 1. SOUL引用SKILL
```markdown
## 我的能力
我有 **54个专业技能**，包括：
- 投资分析类 (7个)
- 数据研究类 (9个)  
- 系统框架类 (7个)
<!-- 自动从SKILL_REGISTRY同步 -->
```

### 2. SOUL引用MEMORY
```markdown
## 重要经历
- **2026-05-01**: 启动L3自主进化，建立Goal-Oriented系统
<!-- 自动从MEMORY.md同步 -->
```

### 3. SOUL引用GOAL
```markdown
## 当前进化方向
- **进行中**: 实现L3半自主进化 (35%)
- **已完成**: L2辅助模式建立
<!-- 自动从data/goals同步 -->
```

### 4. GOAL引用SKILL
```json
{
  "title": "实现L3半自主进化",
  "required_skills": ["agent_evolution", "goal_management"],
  "skill_refs": ["S001", "S002"]
}
```

### 5. GOAL引用MEMORY
```json
{
  "title": "实现L3自修复",
  "related_memories": ["2026-05-01-diagnosis-success"],
  "lessons_learned": ["L001", "L002"]
}
```

### 6. MEMORY引用GOAL
```markdown
## 2026-05-01
**关联Goal**: G001 (L3进化)
**事件**: 完成自诊断引擎
**影响**: Goal进度从0%提升到35%
```

---

## 实现优先级

### Phase 1: 基础整合 (本周)
1. ✅ 建立SKILL_REGISTRY.json
2. ✅ SOUL.md引用SKILL_REGISTRY
3. ✅ Goal系统关联SKILL

### Phase 2: 记忆增强 (下周)
4. 🔄 建立MEMORY.md精华层
5. 🔄 工作记忆自动保存
6. 🔄 语义记忆检索

### Phase 3: 自动同步 (下周)
7. ⏳ 自动更新SOUL进化里程碑
8. ⏳ 自动萃取MEMORY精华
9. ⏳ SKILL熟练度自动统计

---

**ARCHITECTURE**: SOUL-SKILL-MEMORY-GOAL
**VERSION**: 1.0
**STATUS**: Designing
