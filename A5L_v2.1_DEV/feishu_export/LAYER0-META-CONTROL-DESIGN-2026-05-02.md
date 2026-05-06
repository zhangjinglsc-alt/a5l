# Layer 0: 元控制层设计文档

**创建时间**: 2026-05-02 05:45  
**核心功能**: A5L系统大脑 - 智能指挥中枢  
**解决痛点**: 新增SKILL放置决策、故障协调、资源编排

---

## 🧠 设计背景

### 原有问题
A5L原有的5层架构存在**指挥缺失**:
- 新SKILL不知道该放入哪个Layer
- 故障时只知道告警，不知道如何协调恢复
- 各层资源调度缺乏全局优化

### 解决方案
添加 **Layer 0: 元控制层** 作为系统大脑，实现:
1. **智能路由** - 自动决策SKILL归属
2. **故障自愈** - 智能协调恢复流程
3. **资源编排** - 全局优化资源分配
4. **系统监控** - 全局视角健康检查

---

## 🏗️ 架构位置

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 0: 元控制层 (Meta Control)                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 🧠 系统大脑                                             │ │
│  │ • SKILL放置决策器 (SkillPlacementDecider)              │ │
│  │ • 故障恢复协调器 (FaultRecoveryCoordinator)            │ │
│  │ • 资源编排器 (ResourceOrchestrator)                    │ │
│  │ • 元控制器 (MetaController)                            │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓ 指挥调度
┌─────────────────────────────────────────────────────────────┐
│  Layer 1-5: 执行层 (原有架构)                               │
│  数据感知 → 策略决策 → 认知分析 → 执行控制 → 元学习       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 核心组件

### 1. SKILL放置决策器 (SkillPlacementDecider)

**功能**: 决定新SKILL应该放入哪个Layer

**决策逻辑**:
```
输入: SKILL名称、描述、能力列表
  ↓
关键词匹配 + 数据类型分析 + 频率评估
  ↓
输出: 推荐Layer + 置信度 + 集成复杂度
```

**决策标准**:

| Layer | 关键词 | 数据类型 | 频率 |
|-------|--------|----------|------|
| Layer 1 | 数据/采集/API/价格 | raw_data/market_data | high |
| Layer 2 | 策略/信号/买卖/交易 | signal/strategy/rule | high |
| Layer 3 | 分析/研究/研报/情绪 | analysis/insight | medium |
| Layer 4 | 决策/执行/风控/管理 | decision/execution | high |
| Layer 5 | 复盘/学习/优化/归因 | review/learning | low |
| Independent | 工具/通用/辅助 | utility/tool | on_demand |

**使用示例**:
```python
skill = Architect5LSuperSkill()

decision = skill.layer0.decide_skill_placement(
    skill_name="产业链深度分析器",
    skill_description="分析公司所处产业链的上下游关系",
    skill_capabilities=["产业链图谱", "议价能力分析"]
)

print(decision['recommended_layer'])  # layer3_analysis
print(decision['confidence'])  # 0.85
print(decision['integration_complexity'])  # medium
```

---

### 2. 故障恢复协调器 (FaultRecoveryCoordinator)

**功能**: 智能处理系统故障，协调各层恢复

**故障分类与策略**:

| 故障类型 | 严重级别 | 自动恢复 | 恢复步骤 |
|----------|----------|----------|----------|
| Layer 1数据失败 | critical | 是 | 切换备用源→降级缓存→通知用户 |
| Layer 2策略错误 | high | 是 | 切换备用策略→降低置信度→标记检查 |
| Layer 3分析超时 | medium | 是 | 使用简化分析→返回缓存→异步完成 |
| Layer 4执行失败 | critical | 否 | 立即停止→保全状态→人工介入 |

**使用示例**:
```python
recovery = skill.layer0.coordinate_recovery(
    error_type="layer1_data_failure",
    error_context={"error": "AKShare连接超时"}
)

if recovery['auto_execute']:
    # 自动执行恢复步骤
    execute_recovery(recovery['recovery_plan'])
else:
    # 需要人工确认
    notify_admin(recovery)
```

---

### 3. 资源编排器 (ResourceOrchestrator)

**功能**: 动态调度各层资源

**资源类型**:
- compute: 计算资源
- memory: 内存资源
- io: IO资源

**编排策略**:
```python
task_requirements = {
    "full_pipeline": {"compute": 60, "memory": 50, "io": 40},
    "quick_analysis": {"compute": 30, "memory": 20, "io": 20},
    "deep_research": {"compute": 80, "memory": 70, "io": 60}
}
```

**使用示例**:
```python
orchestration = skill.layer0.orchestrate_task(
    task_type="full_pipeline",
    task_params={"symbol": "300750.SZ"}
)

print(orchestration['priority'])  # high
print(orchestration['can_execute'])  # True
print(orchestration['estimated_completion'])  # 2-5 minutes
```

---

### 4. 元控制器 (MetaController)

**功能**: 统一入口，整合所有控制功能

**核心方法**:
- `decide_skill_placement()` - SKILL放置决策
- `coordinate_recovery()` - 故障恢复协调
- `orchestrate_execution()` - 任务资源编排
- `get_system_report()` - 系统整体报告

---

## 💡 使用场景

### 场景1: 新SKILL接入
```python
# 来了一个新SKILL
new_skill = {
    "name": "产业链深度分析器",
    "capabilities": ["产业链图谱", "议价能力分析"]
}

# 问Layer 0该放在哪里
decision = skill.layer0.decide_skill_placement(**new_skill)

# 根据决策自动放置
if decision['confidence'] > 0.8:
    place_skill(decision['recommended_layer'], new_skill)
```

### 场景2: 故障自动恢复
```python
try:
    result = skill.layer1.get_stock_data("300750.SZ")
except DataSourceError as e:
    # Layer 0自动协调恢复
    recovery = skill.layer0.coordinate_recovery(
        "layer1_data_failure",
        {"error": str(e)}
    )
    
    if recovery['auto_execute']:
        execute_recovery_steps(recovery['recovery_plan'])
```

### 场景3: 系统健康检查
```python
status = skill.layer0.get_system_status()

print(f"系统健康度: {status['system_health']:.1%}")
print(f"活跃SKILL数: {status['active_skills']}")

for rec in status['recommendations']:
    print(f"优化建议: {rec}")
```

---

## 📊 集成效果

### 使用Layer 0前
```
新增SKILL → 人工判断放哪里 → 可能放错 → 后期调整
故障发生 → 记录日志 → 人工排查 → 手动恢复
资源分配 → 各层各自为政 → 资源争抢 → 性能下降
```

### 使用Layer 0后
```
新增SKILL → Layer 0自动决策 → 推荐最佳位置 → 一键放置
故障发生 → Layer 0自动识别 → 智能协调恢复 → 最小化影响
资源分配 → Layer 0全局编排 → 优化调度 → 性能提升
```

---

## 🔧 技术实现

### 文件位置
- 核心代码: `ARCHITECT_5L/layer0_control/meta_controller.py` (21,395 bytes)
- A5L集成: `skills/ARCHITECT-5L-SUPER/SKILL.py` (Layer0_MetaControl类)

### 类结构
```python
Layer0_MetaControl
├── SkillPlacementDecider      # SKILL放置决策
├── FaultRecoveryCoordinator   # 故障恢复协调
├── ResourceOrchestrator       # 资源编排
└── MetaController             # 统一控制器
```

---

## 🎯 解决的核心问题

| 问题 | Layer 0解决方案 |
|------|----------------|
| 新SKILL放哪里? | SKILL放置决策器自动推荐 |
| 故障如何处理? | 故障恢复协调器智能恢复 |
| 资源如何分配? | 资源编排器全局优化 |
| 系统健康如何? | 元控制器统一监控 |

---

## 🚀 下一步演进

Layer 0未来可增强:
1. **自学习能力** - 根据历史决策优化算法
2. **预测能力** - 预测系统瓶颈和故障
3. **自主优化** - 自动调整各层参数
4. **人机协作** - 智能判断何时需要人工介入

---

**结论**: Layer 0元控制层是A5L从"被动响应"到"主动智能"的关键进化！
