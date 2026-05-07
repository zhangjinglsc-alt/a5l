---
name: orchestrator-engine
description: Agentic Design Patterns-based workflow orchestration engine for A5L. Implements Prompt Chaining, Routing, and Parallelization patterns to dynamically coordinate multi-SKILL execution pipelines.
triggers:
  - "编排执行"
  - "orchestrate"
  - "workflow"
  - "并行分析"
  - "链式执行"
  - "智能路由"
layer: "L0_Meta_Control"
owner: "COO"
priority: "P0"
---

# Orchestrator-Engine SKILL

## 概述

基于Agentic Design Patterns的编排引擎，为A5L提供动态工作流编排能力。整合Prompt Chaining、Routing、Parallelization三大基础模式，实现复杂任务的自动化拆解与执行。

**设计模式来源**: Agentic Design Patterns Ch.1-3 (Gulli, 2025)
**架构归属**: Layer 0 Meta Control - COO职能扩展
**核心能力**: 动态编排、智能路由、并行执行、结果合并

## 三大编排模式

### 模式1: Prompt Chaining (提示链)
将复杂任务拆解为顺序执行的子任务序列，每步输出作为下一步输入。

```
输入 → [Step1] → 输出1 → [Step2] → 输出2 → [Step3] → 最终结果
        ↓                    ↓                    ↓
     SKILL A              SKILL B              SKILL C
```

**适用场景**:
- 研报摄入流程: OCR → 翻译 → 实体提取 → KG归档
- 日报生成: 数据收集 → 分析 → 撰写 → 审查
- 复杂分析: 数据获取 → 初步分析 → 深度挖掘 → 综合报告

### 模式2: Routing (智能路由)
根据输入特征自动选择执行路径，类似策略模式的多路分支。

```
                    ┌→ 路径A (个股分析) → [股票数据+UZI+产业链+空方]
输入 → [Classifier] ┼→ 路径B (行业研究) → [行业数据+研报搜索+产业链]
                    └→ 路径C (市场监控) → [新闻聚合+因子监控+情绪分析]
```

**路由决策因子**:
- 输入类型 (个股代码/行业名称/新闻文本)
- 任务复杂度 (简单/中等/复杂)
- 时效性要求 (实时/日内/日常)
- 数据依赖关系

### 模式3: Parallelization (并行化)
同时执行多个独立SKILL，结果合并后统一输出。

```
输入 ─┬→ [SKILL A] ─┐
      ├→ [SKILL B] ─┼→ [Merger] → 统一输出
      ├→ [SKILL C] ─┤
      └→ [SKILL D] ─┘
```

**适用场景**:
- 个股全面分析: 股票数据 + UZI + 产业链 + 空方视角 同时运行
- 多源数据收集: AKShare + Tushare + Finnhub 并行查询
- 多角度验证: 技术分析 + 基本面分析 + 情绪分析 同步执行

## 工作流程

### 标准编排流程

```
1. 任务解析 (Task Parsing)
   └─ 分析用户请求，识别任务类型、关键实体、约束条件
   
2. 模式选择 (Pattern Selection)
   └─ 根据任务特征选择编排模式 (Chain/Routing/Parallel/Mixed)
   
3. 子任务生成 (Subtask Generation)
   └─ 将任务拆解为可执行的子任务，分配SKILL
   
4. 依赖分析 (Dependency Analysis)
   └─ 识别子任务间的依赖关系，构建执行DAG
   
5. 执行编排 (Execution Orchestration)
   └─ 按依赖关系执行子任务，管理状态传递
   
6. 结果合并 (Result Merging)
   └─ 整合各子任务输出，生成统一结果
   
7. 质量检查 (Quality Check)
   └─ 验证结果完整性，必要时触发重试或补偿
```

### 动态路由决策树

```
输入分析
    │
    ├─ 包含股票代码? ──Yes──┐
    │                       ├─ 需要深度分析? ──Yes──→ 个股分析管线
    │                       │                        (并行: 数据+UZI+产业链+空方)
    │                       └─ No ──→ 快速数据查询管线
    │                                    (链式: 数据获取→格式化输出)
    │
    ├─ 包含行业关键词? ──Yes──→ 行业研究管线
    │                           (链式: 研报搜索→OCR→翻译→分析→归档)
    │
    ├─ 市场监控/新闻相关? ──Yes──→ 市场监控管线
    │                              (并行: 新闻聚合+因子监控+情绪分析)
    │
    └─ 其他 ──→ 通用分析管线
                 (根据内容特征动态选择SKILL组合)
```

## SKILL调用矩阵

### 个股分析管线 (Stock Analysis Pipeline)

| 执行顺序 | SKILL | 模式 | 输入 | 输出 |
|---------|-------|------|------|------|
| 1-并行 | unified-stock-price | Parallel | 股票代码 | 价格数据 |
| 1-并行 | stock-five-steps | Parallel | 股票代码 | 五维分析 |
| 1-并行 | private-banker | Parallel | 股票代码 | 投行分析 |
| 1-并行 | bearish-perspective | Parallel | 股票代码 | 风险评估 |
| 2-合并 | result-merger | Chain | 上述结果 | 综合分析 |

### 行业研究管线 (Industry Research Pipeline)

| 执行顺序 | SKILL | 模式 | 输入 | 输出 |
|---------|-------|------|------|------|
| 1 | coze-web-search | Chain | 行业名称 | 相关新闻 |
| 2 | pdf (研报) | Chain | URL/Path | 研报内容 |
| 3 | industry-research | Chain | 内容 | 分析报告 |
| 4 | knowledge-graph | Chain | 分析结果 | 实体关系 |
| 5 | feishu-doc | Chain | 报告 | 归档文档 |

### 市场监控管线 (Market Monitor Pipeline)

| 执行顺序 | SKILL | 模式 | 输入 | 输出 |
|---------|-------|------|------|------|
| 1-并行 | unified-news-aggregator | Parallel | 关键词 | 新闻列表 |
| 1-并行 | sector-etf-monitor | Parallel | 板块 | ETF数据 |
| 1-并行 | fx-factor-monitor | Parallel | 货币对 | 汇率数据 |
| 2-合并 | market-synthesizer | Chain | 上述结果 | 市场摘要 |

## 使用方式

### 触发指令

**直接触发**:
```
编排执行 [任务描述]
orchestrate [task]
workflow [task]
```

**管线专用**:
```
并行分析 [股票代码]      → 启动个股分析管线(并行模式)
链式执行 [任务]          → 启动链式执行模式
智能路由 [输入]          → 自动选择最优管线
```

### 使用示例

**示例1: 个股全面分析** (并行模式)
```
用户: 并行分析 000066

编排引擎动作:
1. 识别输入: 股票代码000066 (中国长城)
2. 选择模式: Parallelization
3. 并行调用:
   - unified-stock-price 000066
   - stock-five-steps 000066
   - private-banker 000066
   - bearish-perspective 000066
4. 等待全部完成
5. 合并结果生成综合分析报告
6. 输出: 结构化分析报告
```

**示例2: 研报深度处理** (链式模式)
```
用户: 分析这份研报 [上传PDF]

编排引擎动作:
1. 识别输入: PDF文档
2. 选择模式: Prompt Chaining
3. 链式执行:
   Step1: pdf分析 → 提取文本内容
   Step2: industry-research → 生成分析报告
   Step3: knowledge-graph → 提取实体关系
   Step4: feishu-doc → 创建云文档归档
4. 每步输出作为下一步输入
5. 输出: 归档文档链接+知识图谱更新
```

**示例3: 智能路由决策** (路由模式)
```
用户: 看看AI算力板块的最新情况

编排引擎动作:
1. 识别输入: 行业关键词"AI算力"
2. 选择模式: Routing
3. 路由决策: 行业研究管线
4. 执行:
   - 搜索AI算力相关新闻
   - 获取相关ETF数据
   - 检索产业链图谱
5. 输出: 行业综合情报
```

## 高级功能

### 混合编排 (Mixed Orchestration)

复杂任务可组合多种编排模式:

```
[个股深度分析任务]
    │
    ├─ Step1: 数据获取 (并行)
    │   ├─ 股票数据
    │   ├─ 新闻检索
    │   └─ 研报搜索
    │
    ├─ Step2: 多维度分析 (并行)
    │   ├─ UZI评分
    │   ├─ 产业链分析
    │   └─ 空方视角
    │
    ├─ Step3: 深度挖掘 (链式)
    │   ├─ 交叉验证
    │   ├─ 矛盾识别
    │   └─ 综合判断
    │
    └─ Step4: 输出与归档 (链式)
        ├─ 报告生成
        └─ 知识库归档
```

### 动态重试与补偿

```
子任务执行
    │
    ├─ 成功 ──→ 继续下一步
    │
    └─ 失败 ──→ 重试策略
                ├─ 可重试? ──Yes──→ 指数退避重试 (最多3次)
                │                    └─ 重试成功 → 继续
                │                    └─ 重试失败 → 降级策略
                │
                └─ 不可重试? ──→ 降级策略
                                   ├─ 使用缓存数据
                                   ├─ 使用备用SKILL
                                   └─ 标记为缺失继续执行
```

### 执行监控与追踪

```
每个编排任务分配唯一trace_id:
{
  "trace_id": "orch_20260508_001",
  "pipeline": "stock_analysis",
  "mode": "parallel",
  "start_time": "2026-05-08T04:20:00Z",
  "subtasks": [
    {"id": "t1", "skill": "unified-stock-price", "status": "completed", "duration_ms": 1200},
    {"id": "t2", "skill": "stock-five-steps", "status": "running", "duration_ms": 3500},
    ...
  ],
  "overall_status": "in_progress",
  "completion_percentage": 65
}
```

## 与A5L架构集成

### Layer 0 职责

Orchestrator-Engine作为COO的核心工具，负责:
- 接收Chief Architect的任务分配
- 动态编排Six-in-One Hub各管理者协作
- 优化资源利用，避免重复调用
- 监控执行进度，异常时升级报告

### 与其他SKILL的关系

```
                    ┌─────────────────────┐
                    │   Orchestrator-Engine  │
                    │     (编排引擎)         │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │   Data Layer   │    │ Analysis Layer │    │   Output Layer  │
    │  (数据获取SKILL) │    │  (分析SKILL)   │    │  (输出/归档SKILL) │
    └──────────────┘    └──────────────┘    └──────────────┘
```

## 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 编排延迟 | < 500ms | 从接收到开始执行 |
| 并行效率 | > 80% | 并行任务时间节省比例 |
| 路由准确率 | > 95% | 正确选择管线的比例 |
| 任务成功率 | > 98% | 成功完成的编排任务比例 |
| 资源利用率 | > 70% | SKILL调用效率 |

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-05-08 | 初始版本，实现三大编排模式 |

## 参考资料

- Gulli, A. (2025). *Agentic Design Patterns*. Springer.
- Ch.1: Prompt Chaining
- Ch.2: Routing
- Ch.3: Parallelization
