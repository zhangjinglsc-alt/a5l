---
name: planner
description: Agentic Design Patterns-based hierarchical planning system for A5L. Implements task decomposition, dynamic re-planning, and plan execution monitoring for complex multi-step objectives.
triggers:
  - "规划任务"
  - "制定计划"
  - "planner"
  - "分解任务"
  - "执行方案"
  - "hierarchical planning"
layer: "L0_Meta_Control"
owner: "Chief Architect"
priority: "P1"
---

# Planner SKILL

## 概述

基于Agentic Design Patterns的规划器，为A5L提供层次化任务规划与动态重规划能力。将复杂战略目标拆解为可执行的子任务，支持执行监控与自适应调整。

**设计模式来源**: Agentic Design Patterns Ch.6 Planning (Gulli, 2025)
**架构归属**: Layer 0 Meta Control - Chief Architect任务分解
**核心能力**: 任务分解、层级规划、依赖管理、动态重规划

## 层次化规划模型

### 四级规划架构

```
Level 1: 战略目标 (Strategic Goal)
    └─ 由Chief Architect定义的高层目标
    └─ 例: "构建AI产业链完整知识图谱"
    
    ↓ 分解为
    
Level 2: 阶段目标 (Phase Objectives)
    ├─ Phase 1: 数据收集阶段
    ├─ Phase 2: 实体提取阶段
    ├─ Phase 3: 关系构建阶段
    └─ Phase 4: 可视化与归档阶段
    
    ↓ 每个Phase分解为
    
Level 3: 具体任务 (Concrete Tasks)
    ├─ Task 1.1: 搜索AI算力相关研报
    ├─ Task 1.2: 下载并解析PDF文档
    ├─ Task 1.3: 提取关键数据点
    └─ ...
    
    ↓ 每个Task分解为
    
Level 4: 原子操作 (Atomic Operations)
    ├─ Op 1.1.1: 调用coze-web-search
    ├─ Op 1.1.2: 筛选相关文档
    └─ Op 1.1.3: 调用pdf工具下载
```

### 规划表示格式 (Plan Representation)

```json
{
  "plan_id": "plan_20260508_001",
  "strategic_goal": "构建AI产业链完整知识图谱",
  "created_by": "Chief Architect",
  "created_at": "2026-05-08T04:30:00Z",
  "status": "active",
  
  "phases": [
    {
      "phase_id": "P1",
      "name": "数据收集阶段",
      "status": "in_progress",
      "dependencies": [],
      "tasks": [
        {
          "task_id": "P1-T1",
          "name": "搜索AI算力相关研报",
          "status": "completed",
          "priority": "high",
          "estimated_duration": "10m",
          "actual_duration": "8m",
          "dependencies": [],
          "assigned_skill": "coze-web-search",
          "output_deliverable": "研报URL列表",
          "atomic_operations": [
            {"op_id": "P1-T1-O1", "tool": "coze_web_search", "params": {"query": "AI算力 研报 2025"}},
            {"op_id": "P1-T1-O2", "tool": "filter_results", "params": {"min_relevance": 0.8}}
          ]
        }
      ]
    }
  ],
  
  "dependency_graph": {
    "nodes": ["P1", "P2", "P3", "P4"],
    "edges": [
      {"from": "P1", "to": "P2", "type": "sequential"},
      {"from": "P2", "to": "P3", "type": "sequential"},
      {"from": "P3", "to": "P4", "type": "sequential"}
    ]
  },
  
  "execution_context": {
    "current_phase": "P1",
    "current_task": "P1-T2",
    "completion_percentage": 25,
    "blocked_tasks": [],
    "at_risk_tasks": []
  }
}
```

## 任务分解策略

### 分解维度

| 维度 | 策略 | 示例 |
|------|------|------|
| 功能分解 | 按功能模块拆分 | 数据层→分析层→输出层 |
| 时间分解 | 按时间阶段拆分 | 日度→周度→月度 |
| 空间分解 | 按市场/标的拆分 | 美股→A股→港股 |
| 责任分解 | 按角色职责拆分 | CIO→CTO→COO |
| 数据分解 | 按数据源拆分 | Finnhub→Tushare→AKShare |

### 分解检查清单

每个任务分解后需验证:
- [ ] **原子性**: 任务是否不可再分?
- [ ] **独立性**: 任务是否可以独立执行?
- [ ] **可衡量**: 任务完成标准是否明确?
- [ ] **可实现**: 任务是否在当前能力范围内?
- [ ] **有价值**: 任务产出是否有明确价值?

## 依赖关系管理

### 依赖类型

```
1. 顺序依赖 (Sequential)
   Task B 必须在 Task A 完成后开始
   例: 研报下载 → 研报分析

2. 数据依赖 (Data)
   Task B 需要 Task A 的输出作为输入
   例: 股票数据获取 → 技术分析

3. 资源依赖 (Resource)
   Task A 和 Task B 竞争同一资源
   例: 两个任务同时调用同一API (需限流)

4. 逻辑依赖 (Logical)
   根据条件决定是否执行
   例: 如果市场波动>5%，则触发风险评估

5. 时间依赖 (Temporal)
   必须在特定时间执行
   例: 美股分析必须在21:30后执行
```

### 依赖图可视化

```
[数据收集阶段]
    │
    ├─→ [研报搜索] ──┐
    │                  ├─→ [数据合并] ──→ [实体提取阶段]
    └─→ [新闻抓取] ──┘
                           │
                           ├─→ [公司实体] ──┐
                           │                 ├─→ [关系构建阶段]
                           └─→ [产品实体] ──┘
                                                  │
                                                  ↓
                                           [可视化阶段]
```

## 动态重规划

### 重规划触发条件

```
1. 任务失败
   └─ 检测到子任务失败 → 评估影响范围 → 制定补救方案

2. 外部变化
   └─ 市场环境突变 → 调整优先级 → 重新排序任务

3. 资源限制
   └─ API限流/超时 → 切换备用方案 → 调整执行顺序

4. 目标调整
   └─ 战略方向变更 → 终止无关任务 → 新增目标任务

5. 效率优化
   └─ 发现更优路径 → 重新规划 → 减少执行步骤
```

### 重规划策略

**策略1: 局部修复**
```
问题: 单个任务失败
应对: 仅重新执行失败任务，不影响其他任务
成本: 低
时间: 快
```

**策略2: 链式重组**
```
问题: 依赖任务失败导致后续任务阻塞
应对: 重新安排依赖链，寻找并行替代方案
成本: 中
时间: 中等
```

**策略3: 阶段重启**
```
问题: 整个Phase的基础假设失效
应对: 重新规划该Phase所有任务
成本: 高
时间: 慢
```

**策略4: 目标重定义**
```
问题: 战略目标本身需要调整
应对: 完全重新规划，保留已完成部分
成本: 极高
时间: 很慢
```

### 重规划决策树

```
检测到异常
    │
    ├─ 单个任务失败?
    │   ├─ 可重试? ──Yes──→ 指数退避重试
    │   └─ 不可重试? ──→ 寻找替代SKILL
    │
    ├─ 依赖链断裂?
    │   └─ 重新排序任务，解除不必要依赖
    │
    ├─ Phase级别问题?
    │   └─ 重新规划该Phase
    │
    └─ 战略目标变化?
        └─ 完全重规划，更新所有Phase
```

## 执行监控

### 实时监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 整体进度 | 已完成任务/总任务 | < 80% @ 截止时间前20% |
| Phase进度 | 当前Phase完成度 | < 50% @ Phase时间过半 |
| 阻塞任务数 | 被依赖阻塞的任务 | > 3个立即告警 |
| 失败任务数 | 已失败的任务 | > 1个立即告警 |
| 资源利用率 | SKILL并发使用率 | > 90% 告警 |
| 预计完成时间 | 基于当前速度 | > 截止时间 立即告警 |

### 状态流转

```
        ┌─────────────┐
        │   Pending   │ ← 初始状态
        └──────┬──────┘
               │ 开始执行
               ▼
        ┌─────────────┐
        │   Running   │ ← 执行中
        └──────┬──────┘
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
┌─────────┐ ┌──────┐ ┌─────────┐
│Completed│ │Failed│ │Blocked  │
└────┬────┘ └──┬───┘ └────┬────┘
     │         │          │
     ▼         │          │
┌─────────┐    │          │
│  Done   │    │          │
└─────────┘    │          │
               │          │
               ▼          ▼
        ┌─────────────┐
        │ Re-planning │ ← 触发重规划
        └─────────────┘
```

## 与Orchestrator-Engine集成

```
Planner (规划器)
    │
    ├─ 生成执行计划 (Plan)
    │
    ▼
Orchestrator-Engine (编排引擎)
    │
    ├─ 解析Plan中的依赖关系
    ├─ 选择编排模式 (Chain/Routing/Parallel)
    ├─ 调用相应SKILL执行
    └─ 返回执行结果
    │
    ▼
Planner (更新状态)
    │
    ├─ 标记已完成任务
    ├─ 检查是否触发重规划
    └─ 推进到下一任务/Phase
```

## 使用方式

### 触发指令

```
规划任务 [目标描述]
制定计划 [目标] --timeline [时间线]
分解任务 [复杂任务]
执行方案 [计划ID]
```

### 使用示例

**示例1: 研报深度分析规划**
```
用户: 规划任务：深度分析AI服务器产业链，3天内完成

Planner动作:
1. 解析目标: AI服务器产业链深度研究，3天周期
2. 生成4个Phase:
   P1-数据收集 (Day 1): 研报搜索+新闻收集+数据获取
   P2-实体提取 (Day 1-2): OCR+翻译+实体识别
   P3-分析综合 (Day 2-3): UZI+产业链+空方分析
   P4-输出归档 (Day 3): 报告生成+飞书归档+KG更新
3. 定义任务依赖图
4. 输出可视化计划
5. 启动执行监控
```

**示例2: 动态重规划**
```
执行中:
- P1完成，P2进行中
- 发现: Tushare API限流，实体提取受阻

Planner动作:
1. 检测阻塞
2. 评估影响: P2-T3, P2-T4 被阻塞
3. 制定方案:
   - 方案A: 等待API恢复 (风险: 时间不可控)
   - 方案B: 切换AKShare (推荐)
   - 方案C: 手工补充关键实体
4. 执行方案B: 更新SKILL调用
5. 重新计算时间表
6. 继续执行
```

**示例3: 多市场并行规划**
```
用户: 制定美股+A股+港股的监控计划

Planner动作:
1. 识别可并行: 三个市场独立
2. 生成3条并行管线:
   - 美股管线: 21:30数据获取→分析→简报
   - A股管线: 09:30数据获取→分析→简报
   - 港股管线: 09:30数据获取→分析→简报
3. 每个管线内部链式执行
4. 三线并行启动
5. 结果合并输出综合简报
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-05-08 | 初始版本，层次化规划与动态重规划 |

## 参考资料

- Gulli, A. (2025). *Agentic Design Patterns* Ch.6 Planning. Springer.
- Newell, A., & Simon, H. A. (1972). "Human Problem Solving"
- Tate, A. (1977). "Generating Project Networks"
