# A5L v2.2 迭代路线图 - Prime原生架构

**版本**: v2.2.0-alpha "Prime Native"  
**制定日期**: 2026-05-11  
**基础**: v2.1.0 + Prime深度集成完成  
**状态**: 规划中

---

## 🎯 新路线图核心理念

### 从"修补旧架构"到"Prime原生"

**原有计划的问题**:
- 基于v2.0架构的渐进式修补
- 6个Phase线性执行，缺乏灵活性
- 数据上传依赖，容易被阻塞

**新路线图的优势**:
- 基于Prime Atom架构重新设计
- SKILL小队按需组合，灵活调度
- 决策溯源驱动，结果导向
- 模块化迭代，快速验证

---

## 📊 当前状态盘点

### ✅ 已完成 (v2.1.0基础)

| 组件 | 状态 | 说明 |
|------|------|------|
| Prime集成 | ✅ 100% | 74 SKILLs → Atoms, 100+ atoms |
| SKILL小队 | ✅ 100% | 10支小队, 50 SKILLs, 编队完成 |
| 调用演示 | ✅ 100% | 4场景42任务跑通 |
| 五层架构 | ✅ 98% | L0-L5基本实现 |
| SKILL Expert | ✅ 100% | 76个全部Expert级 |

### 🆕 新机会点

基于Prime集成带来的新能力：

1. **决策图谱可观测** - 每个决策完整可追溯
2. **SKILL按需组合** - 场景驱动，自动组队
3. **六管理者共识** - 避免独断，集体智慧
4. **知识编译化** - 从检索到编译的范式转换

---

## 🗺️ v2.2 迭代路线图 (3个Wave)

### Wave 1: Prime生态深化 (Week 1-2)

**目标**: 从"集成Prime"到"Prime原生"

#### Phase 1.1: Prime MCP Server
**时间**: Day 1-3  
**负责人**: CA核心架构小队

```
当前: Python Prime实现 (prime_poc.py)
目标: Node.js MCP Server + Python Client

价值:
- 与Prime官方协议完全兼容
- 支持跨语言Agent通信
- 可接入Prime生态其他工具

交付:
- mcp-server-prime/ (Node.js)
- prime_mcp_client.py (Python)
- 协议测试通过
```

#### Phase 1.2: 可视化决策图谱
**时间**: Day 4-7  
**负责人**: KG知识管理小队 + RM报告生成小队

```
当前: 文本格式Atom，命令行查看
目标: 交互式决策图谱可视化

价值:
- 一眼看清决策关联
- 支持钻取溯源
- 复盘时直观展示

交付:
- prime-visualizer/ (Web界面)
- 支持: 决策树、关系图谱、时间线
- 集成到prime-atoms/
```

#### Phase 1.3: Prime Registry 上线
**时间**: Day 8-10  
**负责人**: COO运营协调小队

```
当前: 本地registry.json (175KB)
目标: 可查询的Prime Registry服务

价值:
- SKILL快速发现
- 关系图谱查询
- 版本管理

交付:
- prime-registry-service/
- RESTful API
- 搜索/过滤/关系查询
```

**Wave 1 里程碑**: 
- ✅ MCP Server运行
- ✅ 可视化界面可用
- ✅ Registry服务上线

---

### Wave 2: 智能体化重构 (Week 3-4)

**目标**: 从"工具集合"到"智能体系统"

#### Phase 2.1: Agent Core重构
**时间**: Week 3  
**负责人**: CA核心架构小队 + 白金分析师小队

```
当前: 调用式SKILL (request → response)
目标: 自主Agent (observe → decide → act)

核心变化:
1. Agent Loop
   while True:
     observe()      # 感知环境
     reason()       # 推理决策
     plan()         # 制定计划
     execute()      # 执行动作
     learn()        # 学习反馈

2. Prime驱动决策
   - 所有decision都是Prime Atom
   - 自动记录到知识图谱
   - 支持后期归因分析

3. SKILL小队Agent化
   - 每支小队 = 一个Agent
   - 有独立的状态和记忆
   - 可自主决策和协作

交付:
- agent_core/ (Python)
- agent_loop.py
- squad_agents/ (10支小队Agent)
```

#### Phase 2.2: 自主决策系统
**时间**: Week 4  
**负责人**: CIO投资决策小队 + CSO安全风控小队

```
当前: 被动调用，人工触发
目标: 主动监控，自动触发

场景:
1. 盘前自动分析
   - 09:15自动触发SKILL小队
   - 生成分析报告
   - 推送到飞书

2. 持仓风险监控
   - 实时监控集中度
   - 超限时自动预警
   - 建议调仓方案

3. 催化事件响应
   - 监控新闻/公告
   - Tier 1事件自动分析
   - 推送投资机会

交付:
- auto_decision_engine.py
- trigger_system/
- 3个自动场景跑通
```

#### Phase 2.3: 递归自我改进
**时间**: Week 4-5  
**负责人**: CA核心架构小队

```
当前: 自诊断引擎35%，停滞
目标: 基于Prime的递归改进

新架构:
1. Observe: 监控决策质量和结果
2. Analyze: Prime图谱归因分析
3. Improve: SKILL小队自动迭代
4. Verify: A/B测试验证改进
5. Meta-Improve: 改进改进流程本身

交付:
- recursive_improvement/
- improvement_loop.py
- 自动迭代第一个SKILL
```

**Wave 2 里程碑**:
- ✅ Agent Core运行
- ✅ 3个自动决策场景
- ✅ 递归改进跑通

---

### Wave 3: KIWI Prime融合 (Week 5-6)

**目标**: 飞书知识库与Prime深度集成

#### Phase 3.1: KIWI → Prime同步
**时间**: Week 5  
**负责人**: KG知识管理小队

```
当前: 飞书知识库 (空间2) 与Prime atoms分离
目标: 双向同步，统一知识图谱

架构:
飞书 Wiki Page → Prime Atom (自动转换)
Prime Atom → 飞书 Wiki (自动生成)

同步规则:
- 个股分析 → @a5l/analysis-stock-*
- 行业研报 → @a5l/analysis-industry-*
- 复盘记录 → @a5l/decision-review-*

交付:
- kiwi_prime_bridge.py
- 自动同步服务
- 初始全量同步
```

#### Phase 3.2: Prime智能搜索
**时间**: Week 5-6  
**负责人**: KG知识管理小队 + RM报告生成小队

```
当前: 飞书原生搜索 (关键词匹配)
目标: Prime语义搜索 (关系推理)

能力:
- "中国长城的所有关联分析"
  → 自动检索相关SKILL、决策、研报
- "找找看空方观点"
  → 自动筛选bearish-perspective相关的所有内容
- "最近一个月的买入决策"
  → 时间+类型过滤

交付:
- prime_search_engine.py
- 自然语言查询接口
- 关系推理能力
```

#### Phase 3.3: 协同决策工作流
**时间**: Week 6  
**负责人**: 全体六管理者

```
当前: 六管理者各自为战
目标: Prime驱动的协同决策

工作流:
1. 问题提出 (飞书)
   ↓
2. 自动分解为Prime Atoms
   ↓
3. 分配SKILL小队并行分析
   ↓
4. 六管理者在Prime图谱上协作
   ↓
5. 共识决策自动同步到飞书
   ↓
6. 执行结果自动记录

交付:
- collaborative_decision/
- 飞书机器人集成
- 3个协同决策案例
```

**Wave 3 里程碑**:
- ✅ KIWI ↔ Prime 双向同步
- ✅ 语义搜索上线
- ✅ 协同决策工作流跑通

---

## 📈 与原有计划的对比

### 原有6 Phase计划

| Phase | 内容 | 问题 |
|-------|------|------|
| 1 | 数据完整性检查 | 依赖数据上传，易阻塞 |
| 2 | 全SKILL数据学习 | 线性执行，耗时长 |
| 3 | CIO Awakening | 单一目标，不灵活 |
| 4 | 交易策略形成 | 缺乏系统支撑 |
| 5 | SKILL超级迭代 | 范围模糊 |
| 6 | A5L终极迭代 | 时间压缩 |

### 新3 Wave路线图

| Wave | 主题 | 优势 |
|------|------|------|
| 1 | Prime生态深化 | 基于已完成工作，快速扩展 |
| 2 | 智能体化重构 | Prime原生，决策驱动 |
| 3 | KIWI Prime融合 | 打通飞书生态 |

**核心差异**:
- 从"数据驱动" → "决策驱动"
- 从"线性执行" → "模块化迭代"
- 从"单一目标" → "生态构建"
- 从"被动响应" → "主动智能"

---

## 🎯 关键成功指标 (KPI)

### Wave 1
- [ ] MCP Server响应延迟 < 100ms
- [ ] 可视化界面覆盖100%决策类型
- [ ] Registry查询支持复杂关系

### Wave 2
- [ ] Agent自主决策准确率 > 80%
- [ ] 3个自动场景稳定运行
- [ ] 递归改进第一个SKILL

### Wave 3
- [ ] KIWI ↔ Prime 同步延迟 < 5分钟
- [ ] 语义搜索准确率 > 85%
- [ ] 协同决策时间缩短50%

---

## ⏱️ 时间规划

```
Week 1-2: Wave 1 (Prime生态深化)
  ├─ Day 1-3:  MCP Server
  ├─ Day 4-7:  可视化
  └─ Day 8-10: Registry

Week 3-4: Wave 2 (智能体化重构)
  ├─ Week 3: Agent Core + 自主决策
  └─ Week 4: 递归改进

Week 5-6: Wave 3 (KIWI Prime融合)
  ├─ Week 5: KIWI同步 + 语义搜索
  └─ Week 6: 协同决策

总计: 6周 (vs 原计划25-30天的6 Phase)
效率提升: 基于Prime基础，避免重复建设
```

---

## 🚀 启动条件

### 立即可以开始 (无需等待)
✅ Prime集成已完成  
✅ SKILL小队已编队  
✅ 基础设施已就绪  

### 需要准备
- [ ] Node.js环境 (MCP Server)
- [ ] 前端框架选择 (可视化)
- [ ] KIWI API权限 (飞书集成)

---

## 💡 一句话总结

> 从"给旧系统打补丁"到"基于Prime原生重构"，
> 从"工具集合"到"智能体生态"，
> 从"被动响应"到"主动进化"。

**v2.2 = Prime Native + Agent化 + KIWI融合**

---

**路线图制定**: Chief Architect  
**制定时间**: 2026-05-11  
**版本**: v1.0  
**待确认**: 等待Chief批准启动
