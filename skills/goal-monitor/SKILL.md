---
name: goal-monitor
description: Agentic Design Patterns-based goal setting and monitoring system for A5L. Implements SMART goal tracking, progress monitoring, and adaptive feedback loops to ensure strategic objectives are met.
triggers:
  - "目标监控"
  - "goal monitor"
  - "追踪目标"
  - "检查进度"
  - "SMART目标"
  - "目标达成"
layer: "L4_Decision_Signal"
owner: "CIO"
priority: "P1"
---

# Goal-Monitor SKILL

## 概述

基于Agentic Design Patterns的目标监控器，为A5L提供SMART目标设定、进度追踪和自适应反馈能力。确保战略目标可衡量、可追踪、可达成。

**设计模式来源**: Agentic Design Patterns Ch.11 Goal Setting & Monitoring (Gulli, 2025)
**架构归属**: Layer 4 Decision Signal + Layer 5 Review
**核心能力**: SMART目标设定、实时监控、偏差预警、自适应调整

## SMART目标框架

### SMART原则

| 维度 | 含义 | 投资场景示例 |
|------|------|--------------|
| **S**pecific | 具体明确 | "招商南油集中度降至50%"而非"降低风险" |
| **M**easurable | 可衡量 | 集中度精确到百分比 |
| **A**chievable | 可实现 | 基于当前持仓和市场流动性评估 |
| **R**elevant | 相关性 | 与整体风险管理目标一致 |
| **T**ime-bound | 有时限 | 09:15今日开盘执行 |

### 目标分层架构

```
Level 1: 战略目标 (Strategic Goals)
    └─ 归属: Chief Architect
    └─ 周期: 季度/年度
    └─ 例: "A5L系统健康度达到95%"
    
Level 2: 战术目标 (Tactical Goals)
    └─ 归属: Six-in-One管理者
    └─ 周期: 月度/周度
    └─ 例: "CIO月度胜率目标60%"
    
Level 3: 操作目标 (Operational Goals)
    └─ 归属: 各SKILL/系统
    └─ 周期: 日度/实时
    └─ 例: "美股数据API可用性99.9%"
    
Level 4: 任务目标 (Task Goals)
    └─ 归属: 单次任务
    └─ 周期: 任务执行期间
    └─ 例: "本次分析在5分钟内完成"
```

## 目标定义格式

### 标准目标模板

```json
{
  "goal_id": "goal_20260508_001",
  "name": "招商南油持仓集中度控制",
  "description": "降低招商南油跨账户持仓集中度至安全水平",
  
  "smart_criteria": {
    "specific": "招商南油持仓集中度从70.7%降至50%以下",
    "measurable": "通过SignalArena计算集中度百分比",
    "achievable": "通过减仓2-3个账户实现",
    "relevant": "符合P0级风险控制要求",
    "time_bound": "2026-05-08 09:15前执行完毕"
  },
  
  "target": {
    "metric": "concentration_ratio",
    "current_value": 70.7,
    "target_value": 50.0,
    "unit": "percent",
    "tolerance": 5.0
  },
  
  "owner": "CIO",
  "priority": "P0",
  "category": "risk_management",
  
  "milestones": [
    {
      "milestone_id": "M1",
      "name": "减仓方案确定",
      "target_date": "2026-05-08 09:00",
      "completion_criteria": "确定减仓数量和账户"
    },
    {
      "milestone_id": "M2", 
      "name": "减仓执行完毕",
      "target_date": "2026-05-08 09:15",
      "completion_criteria": "SignalArena确认交易完成"
    },
    {
      "milestone_id": "M3",
      "name": "集中度验证",
      "target_date": "2026-05-08 09:20",
      "completion_criteria": "集中度计算<50%"
    }
  ],
  
  "monitoring": {
    "check_frequency": "realtime",
    "alert_conditions": [
      {"condition": "current_value > 65", "severity": "warning", "message": "集中度仍然偏高"},
      {"condition": "milestone_overdue > 0", "severity": "critical", "message": "里程碑延期"}
    ],
    "escalation_path": ["CIO", "Chief Architect"]
  },
  
  "created_at": "2026-05-08T04:00:00Z",
  "deadline": "2026-05-08T09:15:00Z",
  "status": "active"
}
```

## 监控回路 (Monitoring Loop)

```
┌─────────────────────────────────────────────────────────────┐
│                    Goal Monitoring Loop                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │  Sensor  │───→│ Evaluate │───→│ Execute  │             │
│   │ (传感器)  │    │ (评估器)  │    │ (执行器)  │             │
│   └──────────┘    └──────────┘    └──────────┘             │
│        ↑                               │                    │
│        │                               ▼                    │
│        │                        ┌──────────┐               │
│        └────────────────────────│ Feedback │               │
│                                 │ (反馈)   │               │
│                                 └──────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 传感器 (Sensor)

**数据采集点**:
- 持仓数据: SignalArena交易记录
- 市场数据: 多源价格API
- 系统数据: 健康检查指标
- 分析数据: SKILL调用统计

**采样频率**:
| 指标类型 | 采样频率 | 说明 |
|----------|----------|------|
| 持仓风险 | 实时 | WebSocket推送 |
| 市场价格 | 分钟级 | 聚合后存储 |
| 系统健康 | 5分钟 | 定时探测 |
| 业务指标 | 日度 | 每日汇总 |

### 评估器 (Evaluator)

**评估逻辑**:
```python
def evaluate_goal(goal, current_state):
    progress = calculate_progress(goal.target, current_state)
    
    # 检查是否达成
    if is_achieved(goal.target, current_state):
        return {"status": "achieved", "progress": progress}
    
    # 检查是否偏离
    deviation = calculate_deviation(goal.target, current_state)
    if deviation > goal.tolerance:
        return {"status": "deviated", "progress": progress, "deviation": deviation}
    
    # 检查时间风险
    time_risk = calculate_time_risk(goal.deadline, progress)
    if time_risk > 0.7:
        return {"status": "at_risk", "progress": progress, "time_risk": time_risk}
    
    return {"status": "on_track", "progress": progress}
```

### 执行器 (Executor)

**响应动作**:
| 状态 | 动作 | 示例 |
|------|------|------|
| achieved | 记录成功，触发下一个目标 | 集中度达标，解除风控告警 |
| on_track | 继续监控 | 维持当前策略 |
| deviated | 触发纠偏措施 | 启动减仓程序 |
| at_risk | 升级告警 | 通知CIO和Chief |
| failed | 复盘分析 | 生成失败报告 |

## 目标类型与指标库

### 1. 风险控制目标

| 目标 | 指标 | 告警阈值 |
|------|------|----------|
| 持仓集中度 | 单标的占总资产比例 | > 50% Warning, > 70% Critical |
| 杠杆水平 | 融资负债/净资产 | > 150% Warning, > 200% Critical |
| 单账户亏损 | 单日亏损金额 | > 5% Warning, > 10% Critical |
| 跨市场敞口 | 相关性加权敞口 | > 80% Warning |

### 2. 系统健康目标

| 目标 | 指标 | 目标值 |
|------|------|--------|
| API可用性 | 成功调用率 | > 99.5% |
| 数据延迟 | 价格数据延迟 | < 5秒 |
| 分析准确率 | 预测准确率 | > 70% |
| SKILL成功率 | 调用成功率 | > 95% |

### 3. 业务绩效目标

| 目标 | 指标 | 目标值 |
|------|------|--------|
| 月度胜率 | 盈利交易/总交易 | > 55% |
| 盈亏比 | 平均盈利/平均亏损 | > 1.5 |
| 夏普比率 | 风险调整后收益 | > 1.0 |
| 最大回撤 | 峰值到谷底跌幅 | < 15% |

### 4. 运营效率目标

| 目标 | 指标 | 目标值 |
|------|------|--------|
| 日报生成时间 | 从收盘到发布 | < 30分钟 |
| 研报处理时间 | 从上传到归档 | < 10分钟 |
| SKILL响应时间 | 调用到输出 | < 10秒 |
| 知识库更新延迟 | 新信息到可检索 | < 1小时 |

## 自适应反馈机制

### 偏差响应策略

```
检测到偏离目标
    │
    ├─ 轻微偏离 (< 10%)
    │   └─ 自动微调: 调整执行参数
    │
    ├─ 中度偏离 (10-25%)
    │   └─ 策略调整: 修改执行方案
    │
    ├─ 严重偏离 (25-50%)
    │   └─ 方案重审: 重新规划路径
    │
    └─ 极度偏离 (> 50%)
        └─ 目标重评: 评估目标合理性
```

### 预测性调整

基于趋势预测提前调整:
```
当前进度: 40%
时间进度: 50%
趋势预测: 按当前速度只能完成70%

→ 提前告警: "目标达成风险高"
→ 建议措施: "增加资源投入"或"调整目标"
→ 自动执行: 启用备用资源
```

## 与Layer 5 Review集成

```
每日21:00自动Review流程:

1. Goal-Monitor收集当日所有目标状态
2. 生成分层报告:
   - 已达成目标
   - 进行中目标及进度
   - 偏离目标及原因
   - 新增风险目标

3. 与Planner联动:
   - 未完成目标自动延期
   - 偏离目标触发重规划
   - 达成目标归档并启动下一目标

4. 反馈到记忆系统:
   - 更新目标达成历史
   - 记录偏差模式
   - 优化预测模型
```

## 使用方式

### 触发指令

```
目标监控 [目标ID]
追踪目标 [目标描述]
检查进度
SMART目标 [具体目标]
目标达成检查
```

### 使用示例

**示例1: 设定并监控SMART目标**
```
用户: 设定SMART目标：降低招商南油集中度到50%

Goal-Monitor动作:
1. 解析并标准化目标:
   S: 招商南油集中度
   M: 从70.7%到50%
   A: 通过减仓实现
   R: 符合风险管理要求  
   T: 09:15今日

2. 创建监控实体:
   - 实时追踪集中度
   - 设置里程碑(方案/执行/验证)
   - 配置告警规则

3. 启动监控:
   - 每5分钟检查一次
   - 超标立即告警
   - 偏离时建议纠偏措施

4. 09:15执行后:
   - 验证集中度48.3% ✓
   - 标记目标达成
   - 归档到Layer 5 Review
```

**示例2: 多目标综合监控**
```
用户: 检查今日所有活跃目标

Goal-Monitor输出:
┌─────────────────────────────────────────┐
│ 今日目标监控看板 (2026-05-08)            │
├─────────────────────────────────────────┤
│ ✅ 已达成 (2)                           │
│   - 美股数据同步完成                     │
│   - 日报模板更新                         │
│                                         │
│ 🔄 进行中 (3)                           │
│   - 招商南油减仓 [████░░░░░░] 40%       │
│   - AI产业链图谱构建 [████████░░] 80%   │
│   - Finnhub集成测试 [██░░░░░░░░] 20%    │
│                                         │
│ ⚠️  偏离 (1)                            │
│   - 预测准确率目标 65% (目标70%)        │
│     建议: 检查数据源质量                 │
│                                         │
│ ⏰ 即将到期 (1)                         │
│   - 周报生成 (剩余2小时)                │
└─────────────────────────────────────────┘
```

**示例3: 自动纠偏**
```
场景: 美股API延迟突然升高到15秒

Goal-Monitor动作:
1. 检测偏离: 延迟15s > 目标5s (偏离200%)
2. 评估影响: 可能影响实时监控能力
3. 自动响应:
   - 启动备用数据源
   - 通知CIO
   - 记录事件日志
4. 追踪恢复:
   - 监控备用源性能
   - 主源恢复后自动切回
   - 生成故障报告
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-05-08 | 初始版本，SMART目标框架与实时监控 |

## 参考资料

- Gulli, A. (2025). *Agentic Design Patterns* Ch.11 Goal Setting & Monitoring. Springer.
- Doran, G. T. (1981). "There's a S.M.A.R.T. way to write management's goals and objectives"
- Locke, E. A., & Latham, G. P. (2002). "Building a practically useful theory of goal setting"
