# 🏗️ 五层架构投资体系 - 工作流计划

**项目代号**: ARCHITECT-5L  
**目标**: 构建完整的数据→策略→分析→决策→复盘投资闭环  
**启动时间**: 2026-05-02 02:45  
**预计完成**: 分阶段迭代，核心框架24小时内完成

---

## 📋 整体工作流

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ARCHITECT-5L 实施路线图                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: 架构设计 (0-2小时)                                                  │
│  ├── 1.1 设计五层架构详细规格                                                  │
│  ├── 1.2 盘点现有Skill，识别缺口                                               │
│  └── 1.3 制定数据流和接口规范                                                  │
│                                                                             │
│  Phase 2: 数据层搭建 (2-6小时)                                                │
│  ├── 2.1 创建统一数据管理器 (Multi-Source Data Manager)                         │
│  ├── 2.2 集成AKShare、TuShare、东财、金十数据接口                               │
│  ├── 2.3 设计数据清洗和标准化流程                                              │
│  └── 2.4 建立数据存储和缓存机制                                                │
│                                                                             │
│  Phase 3: 策略层构建 (6-12小时)                                               │
│  ├── 3.1 创建策略引擎 (Strategy Engine)                                        │
│  ├── 3.2 实现股票魔法师策略                                                    │
│  ├── 3.3 实现海龟交易法则                                                      │
│  ├── 3.4 实现趋势突破+相对强度策略                                             │
│  ├── 3.5 实现量价分析策略                                                      │
│  └── 3.6 实现基本面增长策略                                                    │
│                                                                             │
│  Phase 4: 非结构化分析层 (12-18小时)                                          │
│  ├── 4.1 创建信息聚合器 (News & Announcement Aggregator)                       │
│  ├── 4.2 创建情绪分析引擎 (Sentiment Analysis)                                 │
│  ├── 4.3 创建研究报告生成器 (Research Report Generator)                        │
│  ├── 4.4 设计飞书云文档自动同步机制                                            │
│  └── 4.5 建立信息验证和可信度评分机制                                          │
│                                                                             │
│  Phase 5: 决策信号层 (18-20小时)                                              │
│  ├── 5.1 创建信号聚合器 (Signal Aggregator)                                    │
│  ├── 5.2 设计多因子决策模型                                                    │
│  ├── 5.3 创建观察池管理系统                                                    │
│  ├── 5.4 整合现有模拟交易系统                                                  │
│  └── 5.5 设计真实持仓辅助分析模式                                              │
│                                                                             │
│  Phase 6: 复盘进化层 (20-22小时)                                              │
│  ├── 6.1 创建复盘记录系统 (Review & Reflection System)                         │
│  ├── 6.2 设计每日复盘报告模板                                                  │
│  ├── 6.3 设置21:00自动复盘定时任务                                             │
│  ├── 6.4 建立飞书云文档复盘归档                                                │
│  └── 6.5 设计错误归因和学习机制                                                │
│                                                                             │
│  Phase 7: 递归自我改进 (22-24小时)                                            │
│  ├── 7.1 整合递归改进引擎到五层架构                                            │
│  ├── 7.2 设计跨层优化机制                                                      │
│  ├── 7.3 建立性能监控和反馈回路                                                │
│  └── 7.4 完整系统测试和验证                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Phase 1 详细任务清单

### 1.1 五层架构详细规格设计

#### Layer 1: 数据层 (Data Layer)
**输入**: 多源原始数据  
**输出**: 清洗后的标准化数据  
**核心组件**:
- `DataSourceManager` - 数据源管理器
- `DataPipeline` - 数据清洗管道
- `DataValidator` - 数据验证器
- `DataStore` - 数据存储

**数据源清单**:
| 数据源 | 类型 | 用途 | 优先级 |
|--------|------|------|--------|
| AKShare | A股数据 | 快速打样、实时行情 | P0 |
| TuShare | 结构化数据 | 核心数据源、财务数据 | P0 |
| 东方财富 | 补充数据 | 交叉验证、资金流向 | P1 |
| 金十数据 | 舆情数据 | 情绪监控、新闻事件 | P1 |
| Yahoo Finance | 美股数据 | 美股行情 | P0 |
| HKEX | 港股数据 | 港股官方数据 | P0 |

**数据类型**:
1. 行情数据: K线、实时价格、成交量、换手率
2. 财务数据: 财报、指标、业绩预告
3. 公告数据: 公司公告、重大事项
4. 宏观数据: 经济指标、利率、汇率
5. 行业数据: 二级行业分类、行业景气度
6. 另类数据: 情绪指标、资金流向、龙虎榜

**处理流程**:
```
原始数据 → 采集 → 清洗 → 标准化 → 验证 → 存储 → 策略筛选 → AI解读 → 复盘反馈
```

---

#### Layer 2: 策略层 (Strategy Layer)
**输入**: 标准化数据  
**输出**: 策略信号列表  
**核心组件**:
- `StrategyEngine` - 策略引擎
- `RuleEvaluator` - 规则评估器
- `SignalGenerator` - 信号生成器

**策略清单**:
1. **股票魔法师策略** (Stock Wizard)
   - 趋势模板: 股价>50日均线>150日均线>200日均线
   - 相对强度: RS Rating > 80
   - 成交量: 突破时放量

2. **海龟交易法则** (Turtle Trading)
   - 入场: 20日/55日突破
   - 仓位: 按ATR波动率调整
   - 止损: 2倍ATR
   - 退出: 10日/20日反向突破

3. **趋势突破+相对强度** (Trend + RS)
   - 价格突破: 20日/60日新高
   - 相对强度: 板块内排名前20%
   - 成交量确认: 突破时放量1.5倍

4. **量价分析策略** (Volume-Price)
   - 放量上涨: 量价齐升
   - 缩量回调: 量缩价稳
   - 异常放量: 警惕出货

5. **基本面增长策略** (Fundamental Growth)
   - 营收增长: 连续2季度>20%
   - 利润增长: 连续2季度>20%
   - ROE: >15%
   - 估值: PE < 行业均值

---

#### Layer 3: 非结构化分析层 (Unstructured Analysis Layer)
**输入**: 新闻、公告、研报、社交媒体  
**输出**: 结构化分析报告  
**核心组件**:
- `InfoAggregator` - 信息聚合器
- `SentimentAnalyzer` - 情绪分析器
- `ReportGenerator` - 报告生成器
- `FeishuSync` - 飞书同步

**信息源**:
- 公司公告: 交易所公告、重大事项
- 新闻舆情: 财经新闻、行业动态
- 研报观点: 券商研报、目标价
- 社交媒体: 雪球、股吧情绪
- 政策影响: 行业政策、监管动态

**输出格式**:
```
《YYYYMMDD-市场-板块分析》
├── 最新变化
├── 板块龙头
├── 信息渠道
├── 风险点
├── 机会点
└── 判断依据
```

---

#### Layer 4: 决策信号层 (Decision Layer)
**输入**: 策略信号 + 分析报告  
**输出**: 可执行交易信号  
**核心组件**:
- `SignalAggregator` - 信号聚合器
- `DecisionEngine` - 决策引擎
- `RiskEvaluator` - 风险评估
- `PositionManager` - 仓位管理

**决策类型**:
- 🔍 进入观察池
- 🧪 小仓试错
- 🟢 触发买入
- 🔴 触发止损
- 🟡 继续持有
- ⚠️ 风险等级评估

**模式区分**:
- **模拟交易模式**: 全权执行，自动交易
- **真实持仓辅助模式**: 提供分析，人工决策

---

#### Layer 5: 复盘进化层 (Review & Evolution Layer)
**输入**: 所有交易记录、决策记录  
**输出**: 复盘报告、改进建议  
**核心组件**:
- `TradeRecorder` - 交易记录器
- `ReviewEngine` - 复盘引擎
- `LearningSystem` - 学习系统
- `EvolutionTracker` - 进化追踪

**复盘问题清单**:
1. 当时为什么买？
2. 判断依据是什么？
3. 后来哪里对了？
4. 后来哪里错了？
5. 是策略问题、数据问题，还是执行问题？

**报告时间**: 每日21:00（交易日）
**报告内容**:
- 当日交易回顾
- 决策依据复盘
- 对错归因分析
- 模拟账户表现
- 真实持仓回顾
- 改进建议

---

## 🔧 Phase 1 立即执行任务

### 任务 1.1: 更新SOUL.md - 终极Goal宣言

### 任务 1.2: 创建五层架构核心文件结构

```
/workspace/projects/workspace/
├── ARCHITECT_5L/                    # 五层架构根目录
│   ├── layer1_data/                 # 数据层
│   │   ├── data_source_manager.py
│   │   ├── data_pipeline.py
│   │   ├── data_validator.py
│   │   └── config/
│   │       ├── akshare_config.json
│   │       ├── tushare_config.json
│   │       └── datasource_registry.json
│   ├── layer2_strategy/             # 策略层
│   │   ├── strategy_engine.py
│   │   ├── strategies/
│   │   │   ├── stock_wizard.py
│   │   │   ├── turtle_trading.py
│   │   │   ├── trend_rs.py
│   │   │   ├── volume_price.py
│   │   │   └── fundamental_growth.py
│   │   └── strategy_registry.json
│   ├── layer3_analysis/             # 非结构化分析层
│   │   ├── info_aggregator.py
│   │   ├── sentiment_analyzer.py
│   │   ├── report_generator.py
│   │   └── feishu_sync.py
│   ├── layer4_decision/             # 决策信号层
│   │   ├── signal_aggregator.py
│   │   ├── decision_engine.py
│   │   ├── risk_evaluator.py
│   │   └── position_manager.py
│   ├── layer5_review/               # 复盘进化层
│   │   ├── trade_recorder.py
│   │   ├── review_engine.py
│   │   ├── learning_system.py
│   │   └── evolution_tracker.py
│   └── orchestrator.py              # 架构编排器
├── skills/ARCHITECT_5L/             # 五层架构Skill
│   └── SKILL.md
├── data/architect_5l/               # 数据存储
│   ├── raw_data/                    # 原始数据
│   ├── processed_data/              # 处理后数据
│   ├── signals/                     # 信号数据
│   ├── reports/                     # 报告存档
│   └── review_logs/                 # 复盘记录
└── goals/G004-ARCHITECT-5L.md       # 终极Goal文档
```

### 任务 1.3: 盘点现有Skill映射

**已有Skill → 五层架构定位**:

| 现有Skill | 所属层 | 用途 |
|-----------|--------|------|
| `unified_stock_price` | Layer 1 | 统一价格数据 |
| `akshare_data` | Layer 1 | A股数据源 |
| `quant_analysis` | Layer 2 | 量化策略基础 |
| `technical_analysis` | Layer 2 | 技术分析策略 |
| `factor_investing` | Layer 2 | 因子策略 |
| `yangguan_daodao` | Layer 2 | 超短策略 |
| `buffett_value` | Layer 2 | 价值投资策略 |
| `stock_five_steps` | Layer 2 | 五步法分析 |
| `private_banker` | Layer 2 | 机构分析框架 |
| `coze_web_search` | Layer 3 | 信息搜索 |
| `unified_news` | Layer 3 | 新闻聚合 |
| `ai_news_aggregator` | Layer 3 | AI新闻分析 |
| `us_sim_trading` | Layer 4 | 美股模拟执行 |
| `cn_sim_trading` | Layer 4 | A股模拟执行 |
| `hk_sim_trading` | Layer 4 | 港股模拟执行 |
| `trading_rules_engine` | Layer 2/4 | 规则引擎 |
| `trading_analytics` | Layer 5 | 分析复盘 |
| `recursive_improvement_engine` | Layer 5 | 递归改进 |

**需要新建的Skill**:
- Layer 1: 多源数据管理器、数据清洗管道
- Layer 2: 股票魔法师策略、海龟交易法则
- Layer 3: 公告分析器、研报摘要器、情绪量化
- Layer 4: 信号聚合器、决策引擎
- Layer 5: 复盘引擎、学习系统

---

## ✅ Phase 1 完成标准

- [x] 五层架构详细规格文档
- [x] 文件目录结构创建
- [x] 现有Skill映射完成
- [x] 缺口Skill识别
- [x] SOUL.md更新 - 终极Goal
- [ ] GOAL系统更新
- [ ] 开始Phase 2: 数据层搭建

---

**下一步**: 用户确认后，开始Phase 1执行，更新SOUL.md和创建文件结构。
