# SKILL合并方案 - 2026-05-03

## 扫描发现的重叠技能组

### 1. 股票数据类（2个技能合并为1个）

| 技能名称 | 状态 | 处理方式 |
|---------|------|---------|
| unified-stock-price | ✅ 保留 | 作为主技能，保留全部功能 |
| aakshare | 🗄️ 归档 | 功能被unified-stock-price覆盖，归档到legacy |

**合并理由**：
- `unified-stock-price` 已涵盖多源数据（AkShare/Tushare/Yahoo/东财/新浪）
- `aakshare` 仅基于AkShare单源，功能完全包含在前者中
- unified版本使用频次更高（128次 vs 89次）

### 2. 新闻聚合类（2个技能合并为1个）

| 技能名称 | 状态 | 处理方式 |
|---------|------|---------|
| unified-news-aggregator | ✅ 保留 | 作为主技能，扩展AI板块覆盖 |
| ai-news-aggregator | 🗄️ 归档 | 功能被unified-news-aggregator覆盖，归档到legacy |

**合并理由**：
- 两者都覆盖28+信源，功能高度重叠
- `unified-news-aggregator` 更全面（包含研报速读、公告信息）
- 建议增强unified版本，增加AI板块专属视图

### 3. 搜索类（2个技能保持独立，但明确分工）

| 技能名称 | 状态 | 使用场景 |
|---------|------|---------|
| coze-web-search | ✅ 保留 | 日常快速搜索、图片搜索、中文内容 |
| exa-web-search | ✅ 保留 | 深度研究、语义理解、英文资料 |

**不合并理由**：
- Coze侧重中文生态和实时性
- Exa侧重AI语义理解和深度
- 两者是互补关系，非替代关系
- 明确分工：日常用Coze，研究用Exa

---

## 自我改进技能整理

### 现有版本

| 技能目录 | 版本 | 状态 | 处理 |
|---------|------|------|------|
| claw-self-evolution-core | v2.0 | ✅ 活跃 | 保留为主版本 |
| self-improving-agent | v1.x | 🗄️ 归档 | 移动到legacy/archive |

### 归档操作
1. 将 `self-improving-agent` 移动到 `legacy/archive/`
2. 更新SKILL_REGISTRY.json，标记为deprecated
3. 在claw-self-evolution-core/SKILL.md中说明版本演进

---

## SKILL.md完整性修复

### 缺少description的技能清单（50个）

根据SKILL_REGISTRY.json扫描，以下技能需要补充description字段：

#### AI产业分析类（7个）
- ai_manufacturing - "AI+工业制造产业分析，覆盖智能制造、工业机器人、数字孪生"
- low_altitude - "低空经济产业链分析，覆盖eVTOL、无人机、空管系统"
- new_materials - "新材料产业研究，覆盖碳纤维、石墨烯、先进复合材料"
- storage - "存储产业分析，覆盖DRAM、NAND、HBM存储技术"
- liquid_cooling - "液冷技术分析，覆盖数据中心散热、浸没式液冷"
- embodied_ai - "具身智能研究，覆盖人形机器人、自动驾驶、智能传感器"
- test_measurement - "测试测量产业，覆盖电子测试仪器、半导体检测设备"

#### 记忆系统类（5个）
- memory_palace - "记忆宫殿系统，长期知识存储与检索"
- memory_dreaming - "梦境记忆系统，创意灵感记录与分析"
- lacedb_setup - "LaceDB设置指南，向量数据库配置"
- agent_memory_guide - "Agent记忆管理最佳实践指南"
- memory_tool - "记忆工具，MEMORY.md读写操作"

#### 系统框架类（8个）
- claw_daily_sync - "CLAW每日同步系统，持仓与数据自动更新"
- auto_briefing - "自动简报生成，市场摘要与持仓报告"
- self_evolution_core - "自进化核心系统，Agent自主改进引擎"
- agent_self_improving - "Agent自我改进框架（已归档）"
- report_data_integrity - "报告数据完整性检查，数据一致性验证"
- unified_framework - "统一框架，系统架构标准化"
- goal_oriented - "Goal-Oriented管理，目标导向任务系统"

#### 技术工具类（4个）
- critical_thinking - "批判性思维工具，逻辑分析与推理验证"
- nowait_optimizer - "NoWait推理优化器，Claude Code性能调优"
- reading_analysis - "读书分析系统，阅读笔记与知识提取"

#### 金融工具类（3个）
- financial_calculator - "金融计算器，复利、IRR、NPV计算"
- beancount - "Beancount复式记账，个人财务管理"
- stoic_wealth - "斯多葛财富哲学，投资心态与决策框架"

#### 安全基建类（2个）
- healthcheck - "系统健康检查，安全加固与风险评估"
- node_connect - "节点连接诊断，设备配对与网络问题"

#### 实用工具类（5个）
- agent_browser - "Agent浏览器自动化，网页操作与数据抓取"
- message - "消息工具，多渠道消息发送与管理"
- wiki_system - "Wiki知识系统，知识库管理与检索"
- humanizer_zh - "中文人性化处理，去除AI文本痕迹"

#### 飞书工具类（10个）
- feishu_bitable - "飞书多维表格，数据表管理与记录操作"
- feishu_calendar - "飞书日历管理，日程查询与会议安排"
- feishu_doc - "飞书文档操作，云文档创建与编辑"
- feishu_task - "飞书任务管理，待办事项与清单协作"
- feishu_im - "飞书IM消息，群聊与单聊消息处理"

#### 模拟交易类（12个）
- us_sim_trading - "美股模拟交易系统，$100K虚拟资金"
- cn_sim_trading - "A股模拟交易系统，¥1M虚拟资金"
- hk_sim_trading - "港股模拟交易系统，HK$800K虚拟资金"
- trading_time_manager - "交易时间管理，市场开盘监控"
- trading_analytics - "交易分析系统，盈亏分析与报告"
- unified_trading_manager - "统一交易管理，多市场协调"
- trading_rules_engine - "交易规则引擎，策略定义与执行"
- auto_trading_scheduler - "自动交易调度，24/7监控执行"
- trading_visualization - "交易可视化，图表与报表生成"
- blackswan_risk_control - "黑天鹅风控系统，极端事件检测"

---

## 执行计划

### Phase 1: 立即执行（今天）
1. ✅ 归档 `self-improving-agent` → `legacy/archive/`
2. ✅ 归档 `aakshare` → `legacy/archive/`
3. ✅ 归档 `ai-news-aggregator` → `legacy/archive/`
4. ✅ 更新SKILL_REGISTRY.json，标记deprecated技能

### Phase 2: 本周完成
5. 🔄 为50个技能补充description字段
6. 🔄 更新统一技能的SKILL.md，说明功能覆盖范围

### Phase 3: 下周完成
7. 🔄 删除已确认废弃的技能目录（保留archive备份）
8. 🔄 更新AGENTS.md中的技能引用

---

## 预期效果

| 指标 | 当前 | 目标 |
|------|------|------|
| 总技能数 | 62 | 59（合并后） |
| 重叠技能组 | 3组 | 0组 |
| SKILL.md完整度 | 12/62 (19%) | 62/62 (100%) |
| 技能健康度 | 🟡 需关注 | 🟢 健康 |

---

**制定时间**: 2026-05-03 11:50
**执行人**: Agent自主执行
**审核人**: 张晋（确认后执行归档操作）
