---
name: a2a-protocol
description: Agentic Design Patterns-based Agent-to-Agent communication protocol for A5L. Implements standardized message formats, task delegation, and cross-session coordination for the Six-in-One Hub.
triggers:
  - "A2A通信"
  - "agent通信"
  - "委托任务"
  - "跨会话"
  - "a2a"
  - "inter-agent"
layer: "L0_Meta_Control"
owner: "COO"
priority: "P2"
---

# A2A-Protocol SKILL

## 概述

基于Agentic Design Patterns的A2A(Agent-to-Agent)通信协议，为A5L Six-in-One Hub提供标准化的智能体间通信机制。支持任务委托、状态同步、结果回传和跨会话协调。

**设计模式来源**: Agentic Design Patterns Ch.15 Inter-Agent Communication (Gulli, 2025)
**架构归属**: Layer 0 Meta Control - COO协调中心
**核心能力**: 标准化消息、任务委托、状态同步、跨会话通信

## A5L六管理者通信架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Chief Architect                          │
│                      (任务发起者)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │ 1.发布任务
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                     COO (Orchestrator)                      │
│                    (A2A协议协调中心)                         │
│                    ┌─────────────────┐                      │
│                    │  Message Router │                      │
│                    └────────┬────────┘                      │
└─────────────────────────────┼───────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│     CIO       │    │     CTO       │    │   Knowledge   │
│  (投资官)      │◄──►│  (技术官)      │◄──►│  Guardian    │
│               │    │               │    │  (知识官)      │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        │    ┌───────────────┘                    │
        │    │                                    │
        ▼    ▼                                    ▼
┌───────────────┐                        ┌───────────────┐
│     CSO       │◄──────────────────────►│     CFO       │
│  (安全官)      │                        │  (财务官)      │
└───────────────┘                        └───────────────┘
```

## 消息协议规范

### 标准消息格式

```json
{
  "a2a_version": "1.0",
  "message_id": "msg_20260508_001",
  "timestamp": "2026-05-08T08:30:00Z",
  "ttl": 300,
  
  "header": {
    "from": {
      "agent_id": "chief_architect",
      "agent_type": "meta_controller",
      "session_id": "session_xxx"
    },
    "to": {
      "agent_id": "cio",
      "agent_type": "investment_officer",
      "routing": "direct"
    },
    "cc": ["coo", "cso"],
    "priority": "high",
    "correlation_id": "task_20260508_001"
  },
  
  "body": {
    "message_type": "task_delegation",
    "content": {
      "task_id": "task_reduce_concentration",
      "task_name": "招商南油持仓集中度降低",
      "description": "将招商南油跨账户集中度从70.7%降至50%以下",
      "requirements": {
        "target_concentration": 0.50,
        "deadline": "2026-05-08T09:15:00Z",
        "constraints": ["保持持仓结构合理", "优先减少高杠杆账户"]
      },
      "deliverables": [
        "减仓执行方案",
        "交易执行确认",
        "集中度验证报告"
      ]
    }
  },
  
  "context": {
    "conversation_history": ["msg_20260508_000"],
    "shared_state": {
      "current_concentration": 0.707,
      "affected_accounts": ["WGB", "王力", "老娘"],
      "total_shares": 1220600
    },
    "metadata": {
      "security_level": "internal",
      "retention_days": 90
    }
  },
  
  "signature": {
    "algorithm": "ed25519",
    "value": "..."
  }
}
```

### 消息类型 (Message Types)

| 类型 | 用途 | 方向 | 示例 |
|------|------|------|------|
| `task_delegation` | 任务委托 | 上级→下级 | CA→CIO分配任务 |
| `task_response` | 任务响应 | 下级→上级 | CIO→CA接受/拒绝 |
| `task_progress` | 进度更新 | 下级→上级 | 定期汇报进度 |
| `task_complete` | 任务完成 | 下级→上级 | 提交完成报告 |
| `query_request` | 信息查询 | 任意→任意 | 查询知识库 |
| `query_response` | 查询响应 | 任意→任意 | 返回查询结果 |
| `event_notify` | 事件通知 | 广播 | 告警、状态变更 |
| `state_sync` | 状态同步 | 双向 | 持仓数据同步 |

## 任务委托协议

### 委托流程

```
1. 任务发布 (Task Publication)
   委托方: Chief Architect
   动作: 发布任务到COO消息总线
   消息类型: task_delegation
   
   ↓
   
2. 任务路由 (Task Routing)
   协调方: COO
   动作: 根据任务类型路由到合适Agent
   策略: 负载均衡 + 能力匹配
   
   ↓
   
3. 任务接受 (Task Acceptance)
   执行方: 目标Agent (如CIO)
   动作: 评估能力后接受或拒绝
   消息类型: task_response
   
   ↓
   
4. 任务执行 (Task Execution)
   执行方: 目标Agent
   动作: 执行任务，定期汇报
   消息类型: task_progress
   
   ↓
   
5. 任务完成 (Task Completion)
   执行方: 目标Agent
   动作: 提交完成报告
   消息类型: task_complete
   
   ↓
   
6. 结果确认 (Result Confirmation)
   委托方: Chief Architect
   动作: 验证结果，确认完成
   消息类型: task_ack
```

### 委托消息示例

**委托方发送**:
```json
{
  "header": {
    "from": {"agent_id": "chief_architect"},
    "to": {"agent_id": "cio"},
    "message_type": "task_delegation"
  },
  "body": {
    "task": {
      "id": "task_001",
      "type": "risk_management",
      "priority": "p0",
      "deadline": "2026-05-08T09:15:00Z",
      "description": "降低招商南油持仓集中度",
      "acceptance_criteria": [
        "集中度降至50%以下",
        "交易记录已确认",
        "风险报告已生成"
      ]
    }
  }
}
```

**执行方响应**:
```json
{
  "header": {
    "from": {"agent_id": "cio"},
    "to": {"agent_id": "chief_architect"},
    "correlation_id": "task_001",
    "message_type": "task_response"
  },
  "body": {
    "response": "accepted",
    "reason": "能力匹配，资源充足",
    "estimated_completion": "2026-05-08T09:20:00Z",
    "milestones": [
      {"name": "方案制定", "time": "09:00"},
      {"name": "交易执行", "time": "09:15"},
      {"name": "验证确认", "time": "09:20"}
    ]
  }
}
```

## 跨会话通信

### 场景: Cron任务通知主会话

```
[Cron会话] ──A2A──► [Main会话]
     │                    │
     │  1.监控任务触发      │
     │  2.生成日报         │
     │  3.A2A通知          │
     │                     │
     │────────────────────►│
     │  message_type:      │
     │  event_notify       │
     │  body: {            │
     │    "event":         │
     │    "daily_report",  │
     │    "report_id":     │
     │    "rpt_001"        │
     │  }                  │
     │                     │
     │                     ▼
     │               主会话接收
     │               通知Chief
```

### 会话间状态同步

```json
{
  "header": {
    "from": {"agent_id": "cio", "session_id": "session_a"},
    "to": {"agent_id": "cio", "session_id": "session_b"},
    "message_type": "state_sync"
  },
  "body": {
    "sync_type": "position_update",
    "data": {
      "account": "6662",
      "symbol": "000066",
      "change": "+10%",
      "new_position": 48000,
      "timestamp": "2026-05-08T09:30:00Z"
    },
    "sync_id": "sync_001",
    "expected_ack": true
  }
}
```

## Six-in-One Hub专用通道

### 管理者间标准通信模式

**CA ↔ CIO (战略-执行)**
```
CA: task_delegation → 投资目标/策略方向
CIO: task_progress → 执行进度/市场反馈
CIO: task_complete → 结果报告/收益归因
```

**CIO ↔ CFO (投资-财务)**
```
CIO: query_request → 资金可用额度查询
CFO: query_response → 资金状态/风险敞口
CIO: event_notify → 大额交易预告
```

**CTO ↔ CSO (技术-安全)**
```
CTO: event_notify → 系统变更通知
CSO: query_request → 安全审计查询
CSO: event_notify → 安全告警/事件
```

**KG ↔ ALL (知识-全角色)**
```
ALL: query_request → 知识库查询
KG: query_response → 知识检索结果
KG: event_notify → 知识更新通知
```

**COO ↔ ALL (协调-全角色)**
```
COO: task_delegation → 任务分配/协调
ALL: task_response → 任务响应
COO: event_notify → 系统状态广播
```

## 消息路由策略

### 路由规则引擎

```python
ROUTING_RULES = {
    "task_delegation": {
        "cio": ["investment", "trading", "risk_management"],
        "cto": ["technical", "infrastructure", "data_pipeline"],
        "cso": ["security", "compliance", "audit"],
        "cfo": ["financial", "accounting", "budget"],
        "kg": ["knowledge", "research", "documentation"]
    },
    "query_request": {
        "routing": "capability_based",
        "fallback": "kg"
    },
    "event_notify": {
        "routing": "broadcast",
        "filter": "subscription_based"
    }
}

def route_message(message):
    msg_type = message["header"]["message_type"]
    target = message["header"]["to"]["agent_id"]
    
    if target == "broadcast":
        return broadcast_to_subscribers(message)
    
    if target == "auto":
        # 自动路由
        content = message["body"]["content"]
        keywords = extract_keywords(content)
        return find_best_match(keywords, ROUTING_RULES[msg_type])
    
    return direct_send(message, target)
```

### 优先级处理

| 优先级 | 响应时间 | 处理方式 | 示例 |
|--------|----------|----------|------|
| CRITICAL | < 1s | 立即处理+告警 | 安全事件 |
| HIGH | < 5s | 优先队列 | P0任务委托 |
| NORMAL | < 30s | 标准队列 | 常规查询 |
| LOW | < 5min | 批量处理 | 日志同步 |

## 使用方式

### 触发指令

```
A2A发送 [目标] [消息]
委托任务 [目标] [任务描述]
跨会话通知 [会话ID] [消息]
agent通信 [from] [to] [内容]
```

### 编程接口

```python
# 发送任务委托
a2a.send(
    to="cio",
    message_type="task_delegation",
    body={
        "task_id": "task_001",
        "description": "降低持仓集中度",
        "deadline": "2026-05-08T09:15:00Z"
    },
    priority="high",
    require_ack=True
)

# 订阅事件
a2a.subscribe(
    event_types=["trade_executed", "risk_alert"],
    handler=handle_event
)

# 查询其他Agent
response = a2a.query(
    to="kg",
    query="查询中国长城的最新研报",
    timeout=10
)
```

### 使用示例

**示例1: CA委托CIO执行任务**
```
Chief Architect → A2A → CIO

消息:
{
  "type": "task_delegation",
  "task": "降低招商南油集中度至50%",
  "deadline": "09:15",
  "priority": "P0"
}

CIO响应:
{
  "type": "task_response", 
  "status": "accepted",
  "plan": "09:00方案 → 09:15执行 → 09:20确认"
}
```

**示例2: 跨会话通知**
```
Cron Job (17:30日报) → A2A → Main Session

消息:
{
  "type": "event_notify",
  "event": "daily_report_generated",
  "report_id": "rpt_20260508",
  "summary": "美股收盘 Summary..."
}

Main Session:
- 接收通知
- 显示给用户
- 归档到知识库
```

**示例3: KG知识查询**
```
任意Agent → A2A → Knowledge Guardian

查询: "AI产业链上下游关系"

KG响应:
{
  "type": "query_response",
  "results": [
    {"entity": "NVIDIA", "relation": "上游", "to": "服务器厂商"},
    {"entity": "服务器厂商", "relation": "中游", "to": "数据中心"},
    ...
  ],
  "source": "knowledge_graph",
  "confidence": 0.95
}
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-05-08 | 初始版本，Six-in-One Hub通信协议 |

## 参考资料

- Gulli, A. (2025). *Agentic Design Patterns* Ch.15 Inter-Agent Communication. Springer.
- FIPA ACL Specification
- Google A2A Protocol
