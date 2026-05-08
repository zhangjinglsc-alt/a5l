# Agentic Patterns SKILL 模拟交易测试方案

## 测试场景设计

### 场景: SIM账户买入"新易盛"(300502) - CPO概念龙头

**测试目标**: 验证全部7个新SKILL在真实交易workflow中的协同工作

---

## 测试步骤与SKILL触发

### Step 1: 智能路由与编排 (orchestrator-engine)

**用户输入**: "分析300502新易盛，给出买入建议"

**预期行为**:
```
orchestrator-engine识别输入 → 路由到"个股分析管线"

并行调用:
  ├─ unified-stock-price (价格数据)
  ├─ coze-web-search (新闻/催化事件)
  ├─ catalyst-tier-framework (CTF分级)
  └─ sector-etf-monitor (CPO板块监控)

结果合并 → 综合分析报告
```

**验证点**: 
- [ ] 是否正确识别股票代码
- [ ] 是否并行调用多个SKILL
- [ ] 结果是否正确合并

---

### Step 2: 反思优化 (reflection-optimizer)

**触发**: 初版分析报告生成后

**预期行为**:
```
Producer (初始分析):
  "新易盛是CPO龙头，受益于AI算力建设，建议买入"

Critic (六维度审查):
  ├─ 事实准确性: ✓ 价格数据已验证
  ├─ 逻辑一致性: ⚠️ 未考虑估值偏高风险
  ├─ 偏见检测: ⚠️ 过度乐观，缺少空方视角
  ├─ 完整性: ✗ 未提及最新财报数据
  ├─ 清晰度: ✓ 表达清晰
  └─ 可操作性: ⚠️ 未给出具体买入价位

优化建议:
  - 补充PE/PB估值分析
  - 增加"主要风险"章节
  - 给出具体买入区间建议

Reviser (修订版):
  [包含上述优化的完整报告]
```

**验证点**:
- [ ] 是否识别出分析中的问题
- [ ] 是否给出具体优化建议
- [ ] 修订后质量是否提升

---

### Step 3: 交易规划 (planner)

**触发**: 确定买入决策后

**预期行为**:
```
输入: "买入300502新易盛，仓位不超过SIM账户10%"

Planner生成4级计划:

Level 1: 战略目标
  "完成300502建仓，仓位控制在10%以内"

Level 2: 阶段目标
  Phase 1: 数据确认 (开盘前)
  Phase 2: 分批买入 (盘中)
  Phase 3: 持仓确认 (收盘后)

Level 3: 具体任务
  Task 1.1: 确认开盘价格
  Task 1.2: 检查板块情绪
  Task 2.1: 第一批买入5% (09:35)
  Task 2.2: 第二批买入5% (价格回调时)
  Task 3.1: 确认持仓
  Task 3.2: 更新风险监控

Level 4: 原子操作
  Op 2.1.1: 查询当前价格
  Op 2.1.2: 计算可买股数
  Op 2.1.3: 执行买入指令
```

**验证点**:
- [ ] 是否正确分解为4级目标
- [ ] 依赖关系是否正确
- [ ] 时间规划是否合理

---

### Step 4: 目标监控 (goal-monitor)

**触发**: 交易执行过程中

**预期行为**:
```
SMART目标设定:
  S: 买入300502，仓位10%
  M: 通过SIM账户持仓验证
  A: 基于当前资金量计算
  R: 符合CPO板块投资计划
  T: 今日收盘前完成

监控回路:
  传感器: 实时读取SIM持仓
  评估器: 对比目标仓位 vs 实际仓位
  执行器: 触发下一步买入或告警

告警规则:
  - 价格涨幅>5%: Warning (可能追高)
  - 价格跌幅>3%: Info (低吸机会)
  - 板块整体下跌: Warning (系统性风险)
```

**验证点**:
- [ ] SMART目标是否正确设定
- [ ] 是否实时监控进度
- [ ] 偏离时是否正确告警

---

### Step 5: 韧性恢复 (resilience-recovery)

**触发**: 模拟API故障场景

**模拟故障**:
```
场景: 买入执行时Tushare API限流

检测:
  - 第1次调用: Timeout
  - 第2次调用: Rate Limit Error
  - 第3次调用: Timeout

熔断器触发:
  - 状态: CLOSED → OPEN
  - 切换到备用数据源: AKShare
  - 通知: "已切换至备用数据源"

恢复探测:
  - 30秒后尝试半开状态
  - 成功调用后: OPEN → HALF_OPEN
  - 连续成功3次后: HALF_OPEN → CLOSED
```

**验证点**:
- [ ] 是否正确检测故障
- [ ] 熔断器是否正确触发
- [ ] 是否成功切换到备用源
- [ ] 恢复后是否正确切回

---

### Step 6: 护栏检查 (guardrails-system)

**触发**: 交易指令执行前

**预期行为**:
```
输入护栏:
  ✓ 无指令注入
  ✓ 无敏感信息泄露
  ✓ 格式验证通过

执行护栏:
  检查: "买入300502 5000股"
  ├─ 账户类型: SIM ✓
  ├─ 单笔金额: ¥50万 < ¥100万上限 ✓
  ├─ 集中度: 10% < 50%上限 ✓
  ├─ 交易时间: 09:35 (在交易时段) ✓
  └─ 杠杆: 无 ✓

输出护栏:
  建议内容审查:
  ├─ 事实核查: 价格数据已验证
  ├─ 合规检查: 已添加风险提示
  ├─ 偏见检测: 多空观点平衡
  └─ 安全扫描: 无异常

P0红线检查:
  ✓ 不涉及REAL账户
  ✓ 无越权操作
  ✓ 无敏感数据泄露
```

**验证点**:
- [ ] 输入验证是否正确
- [ ] 权限检查是否生效
- [ ] 合规审查是否完整
- [ ] P0红线是否正确拦截

---

### Step 7: A2A通信 (a2a-protocol)

**触发**: 交易过程中的管理者协调

**预期通信流程**:
```
1. Chief Architect → CIO (任务委托)
   {
     "type": "task_delegation",
     "task": "执行300502买入",
     "constraints": ["仓位<10%", "分批买入"]
   }

2. CIO → COO (请求编排)
   {
     "type": "query_request",
     "query": "请求orchestrator-engine协调数据获取"
   }

3. CIO → CTO (技术确认)
   {
     "type": "query_request",
     "query": "确认数据源可用性"
   }

4. CIO → CFO (资金确认)
   {
     "type": "query_request",
     "query": "SIM账户可用资金"
   }
   
   CFO响应:
   {
     "type": "query_response",
     "data": {"available": "¥500万", "sufficient": true}
   }

5. CIO → CSO (安全确认)
   {
     "type": "query_request",
     "query": "交易安全检查"
   }
   
   CSO响应 (通过guardrails-system):
   {
     "type": "query_response",
     "status": "approved",
     "checks_passed": ["权限", "限额", "时间"]
   }

6. CIO → Chief Architect (进度汇报)
   {
     "type": "task_progress",
     "progress": "第一批5%已买入，第二批等待回调"
   }

7. CIO → Chief Architect (任务完成)
   {
     "type": "task_complete",
     "result": "10%仓位建仓完成，均价¥98.5"
   }
```

**验证点**:
- [ ] 消息格式是否符合协议
- [ ] 路由是否正确
- [ ] 任务委托流程是否完整
- [ ] 状态同步是否及时

---

## 测试检查清单

| SKILL | 测试项 | 预期结果 | 实际结果 | 状态 |
|-------|--------|----------|----------|------|
| orchestrator-engine | 并行调用4个SKILL | 全部成功 | - | ⏳ |
| orchestrator-engine | 结果合并 | 结构化输出 | - | ⏳ |
| reflection-optimizer | 识别问题 | ≥2个问题 | - | ⏳ |
| reflection-optimizer | 修订后质量 | 六维度≥4分 | - | ⏳ |
| planner | 4级分解 | 每级都有任务 | - | ⏳ |
| planner | 依赖图 | 无循环依赖 | - | ⏳ |
| goal-monitor | SMART目标 | 5个维度完整 | - | ⏳ |
| goal-monitor | 实时监控 | 每5分钟更新 | - | ⏳ |
| resilience-recovery | 熔断触发 | 3次失败后熔断 | - | ⏳ |
| resilience-recovery | 降级切换 | 自动切换备用源 | - | ⏳ |
| guardrails-system | 输入验证 | 无注入风险 | - | ⏳ |
| guardrails-system | 权限检查 | 限额检查生效 | - | ⏳ |
| guardrails-system | 合规输出 | 含免责声明 | - | ⏳ |
| a2a-protocol | 消息格式 | 符合JSON Schema | - | ⏳ |
| a2a-protocol | 任务委托 | 完成闭环 | - | ⏳ |

---

## 执行命令

```bash
# 启动模拟交易测试
/sim_trading/test_scenario.sh --stock=300502 --test=agentic_patterns

# 验证结果
/sim_trading/verify_results.sh --test-id=20260508_001
```

---

## 成功标准

- [ ] 全部7个SKILL在场景中被触发
- [ ] 无P0级错误
- [ ] 交易执行成功(SIM账户)
- [ ] 所有检查清单通过
- [ ] 生成测试报告
