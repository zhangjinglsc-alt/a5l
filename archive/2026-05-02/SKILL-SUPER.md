# ARCHITECT-5L Super Skill

**五层架构超级技能 - 可迭代的综合能力工具**

---

## 概述

这是一个**会自我进化、自我完善**的超级SKILL，整合所有现有能力到五层架构中。它不是简单的功能堆砌，而是一个**有机的、递归的、可学习**的智能系统。

**核心特性**:
- 🏗️ **五层架构**: 数据→策略→认知→执行→学习
- 🔄 **自我迭代**: 自动复盘、自动改进、自动优化
- 🧠 **认知能力**: 情绪分析、风险识别、机会发现
- ⚡ **执行能力**: 信号聚合、仓位管理、风险控制
- 📊 **可视化**: Web仪表板、实时监控、报告生成

---

## 五层架构详解

### Layer 1: 数据感知层 (Data Perception)

**职责**: 收集和预处理所有数据

**数据源**:
- 📈 **股票数据**: AKShare (A股)、Yahoo Finance (美股)
- 📰 **新闻数据**: 财新网、东方财富、华尔街日报
- 📄 **研报数据**: 东方财富研报、慧博投研
- 📢 **公告数据**: 上交所、深交所、港交所
- 🌐 **宏观数据**: 经济数据、政策信息

**输出**: 标准化的数据流

### Layer 2: 策略决策层 (Strategy Engine)

**职责**: 运行和评估交易策略

**7大策略**:
1. 🎯 **股票魔法师 (CANSLIM)**: 成长股动量策略
2. 🐢 **海龟交易法则**: 趋势跟踪突破策略
3. 📈 **趋势突破+相对强度**: 强势股策略
4. 📊 **量价分析策略**: 成交量确认策略
5. 💎 **基本面增长策略**: 价值投资策略
6. ⚡ **阳关大道超短线**: 短线交易模式
7. 🏛️ **巴菲特价值投资**: 长期价值投资

**输出**: 策略信号（BUY/SELL/HOLD + 置信度）

### Layer 3: 认知分析层 (Cognitive Analysis)

**职责**: 非结构化数据分析和洞察生成

**能力**:
- 🎭 **情绪分析**: 新闻/公告情绪识别
- ⚠️ **风险识别**: 自动发现潜在风险点
- ✅ **机会发现**: 识别投资机会
- 📝 **报告生成**: 每日板块分析报告
- 🔍 **信息验证**: 交叉验证信息真实性

**核心原则**: **绝对诚实** - 不编造信息，所有结论有来源

**输出**: 分析报告、情绪得分、风险提示

### Layer 4: 执行控制层 (Execution Control)

**职责**: 信号聚合、决策执行、风险控制

**功能**:
- 🔗 **信号聚合**: 多策略信号加权整合
- 💰 **仓位管理**: 动态仓位计算和止损止盈
- ⚖️ **风险控制**: 单日亏损/回撤/集中度检查
- 🤖 **双模式执行**:
  - 模拟交易模式: 全自动执行
  - 研究助手模式: 提供建议，人工决策

**输出**: 交易决策、仓位建议、风险警告

### Layer 5: 元学习层 (Meta Learning)

**职责**: 复盘、学习、自我改进

**能力**:
- 📊 **每日复盘**: 21:00自动生成复盘报告
- 🧠 **知识沉淀**: 错误模式学习、经验总结
- 🔄 **自动改进**: 基于复盘结果优化策略
- 📈 **归因分析**: 收益来源分析（选股/择时/行业）
- 🎯 **递归优化**: 改进改进过程本身

**输出**: 改进建议、知识库更新、策略优化

---

## 使用方式

### 1. 基础使用

```python
from SKILL import Architect5LSuperSkill

# 初始化超级SKILL
skill = Architect5LSuperSkill()

# 执行完整流水线
result = skill.execute_full_pipeline("000001.SZ")

# 生成每日报告
report = skill.generate_daily_report()
```

### 2. 分层调用

```python
# Layer 1: 获取数据
data = skill.layer1.get_stock_data("000001.SZ", days=30)
news = skill.layer1.get_market_news(max_items=10)

# Layer 2: 策略分析
signals = skill.layer2.get_all_signals("000001.SZ", data)

# Layer 3: 认知分析
sentiment = skill.layer3.analyze_sentiment(news[0]["content"])
report = skill.layer3.generate_sector_report("半导体")

# Layer 4: 决策执行
decision = skill.layer4.make_decision("000001.SZ", mode="research")

# Layer 5: 学习复盘
review = skill.layer5.daily_review()
```

### 3. Web界面

```bash
# 启动Web仪表板
cd ARCHITECT_5L/dashboard
./start_dashboard.sh

# 访问 http://localhost:8501
```

---

## 文件结构

```
skills/ARCHITECT-5L-SUPER/
├── SKILL.py              # 主入口（19KB）
├── SKILL.md              # 本文档
├── config/
│   └── skill_config.json # SKILL配置
└── tests/
    └── test_skill.py     # 单元测试

ARCHITECT_5L/             # 五层架构实现
├── layer1_data/          # 数据层
│   ├── connectors/       # 数据连接器
│   └── ...
├── layer2_strategy/      # 策略层
│   ├── strategies/       # 策略实现
│   └── backtester/       # 回测引擎
├── layer3_analysis/      # 分析层
│   ├── aggregators/      # 信息聚合
│   ├── analyzers/        # 分析器
│   └── connectors/       # 真实信息抓取
├── layer4_decision/      # 决策层
│   └── ...
├── layer5_review/        # 学习层
│   └── ...
├── layer7_meta/          # 元层
│   ├── self_healing_monitor.py  # 自愈监控
│   └── dashboard_generator.py   # 仪表板生成
└── dashboard/            # Web界面
    ├── app.py
    └── requirements.txt
```

---

## 依赖安装

```bash
# 基础依赖
pip install akshare pandas numpy plotly streamlit

# 完整依赖
cd ARCHITECT_5L/dashboard
pip install -r requirements.txt
```

---

## 配置说明

### 环境变量

```bash
# 工作目录
export ARCHITECT_WORKSPACE="/workspace/projects/workspace"

# 日志级别
export ARCHITECT_LOG_LEVEL="INFO"

# 数据源配置
export AKSHARE_ENABLED="true"
export TUSHARE_TOKEN="your_token"

# 飞书配置
export FEISHU_FOLDER_TOKEN="your_token"
```

### 配置文件

`config/skill_config.json`:
```json
{
  "version": "1.0.0",
  "layers": {
    "layer1": {
      "data_sources": ["akshare", "yahoo", "caixin"],
      "cache_enabled": true
    },
    "layer2": {
      "active_strategies": ["stock_wizard", "turtle_trading"],
      "backtest_enabled": true
    },
    "layer3": {
      "sentiment_model": "keyword",
      "verify_sources": true
    },
    "layer4": {
      "mode": "research_assistant",
      "risk_limits": {
        "max_daily_loss": 0.1,
        "max_drawdown": 0.15
      }
    },
    "layer5": {
      "review_time": "21:00",
      "auto_optimize": true
    }
  }
}
```

---

## 迭代路线图

### P1 - 本周（精装修）
- [ ] Web仪表板完善
- [ ] 单元测试覆盖（70%）
- [ ] 策略参数自动优化
- [ ] 组合归因分析

### P2 - 本月（智能化）
- [ ] 机器学习模块（LSTM/XGBoost）
- [ ] 实时推送系统
- [ ] A/B测试框架
- [ ] 多因子模型

### P3 - 本季度（专业化）
- [ ] 另类数据接入
- [ ] 算法交易优化
- [ ] 风险管理增强
- [ ] NLP情感分析
- [ ] 知识图谱

---

## 核心优势

### 1. 架构优势
- ✅ **五层分离**: 职责清晰，易于维护
- ✅ **递归改进**: Layer 5反馈到各层，持续进化
- ✅ **模块化**: 各层可独立开发、测试、部署

### 2. 能力优势
- ✅ **多市场**: A股/美股/港股全覆盖
- ✅ **多策略**: 7种策略适应不同市场环境
- ✅ **认知能力**: 不仅执行，还能分析、理解、学习

### 3. 工程优势
- ✅ **自愈能力**: 自动检测和修复常见问题
- ✅ **可视化**: Web仪表板实时监控
- ✅ **可观测**: 完整日志、监控、告警

### 4. 安全优势
- ✅ **诚实原则**: 不编造信息，所有结论可溯源
- ✅ **风险控制**: 多层风控，保护本金
- ✅ **模拟优先**: 先模拟验证，再实盘执行

---

## 使用场景

### 场景1: 每日研究
```
早上9:00 - 启动系统，查看隔夜新闻
上午10:00 - 运行策略扫描，发现机会
下午15:00 - 生成复盘报告，记录信号
晚上21:00 - 自动复盘，学习改进
```

### 场景2: 策略回测
```
选择策略 → 选择标的 → 设定回测区间
↓
系统自动获取历史数据
↓
运行回测，计算绩效指标
↓
生成回测报告，对比策略
```

### 场景3: 模拟交易
```
系统监控市场
↓
发现交易信号（BUY/SELL）
↓
自动计算仓位和止损
↓
模拟执行交易
↓
记录到交易日志
↓
每日复盘盈亏
```

---

## 注意事项

### ⚠️ 风险提示
1. **不要现在投产** - 当前是框架，需要P1/P2完善
2. **模拟优先** - 至少模拟运行1个月再考虑实盘
3. **小资金测试** - 实盘初期只用1-5%资金
4. **人工复核** - 重要决策需要人工确认

### 📋 使用建议
1. **先理解架构** - 了解五层如何协作
2. **从Layer 1开始** - 确保数据准确
3. **多观察少操作** - 先观察信号质量
4. **持续学习** - 查看每日复盘和改进建议

---

## 联系方式

**开发者**: Agent + 张晋  
**创建时间**: 2026-05-02  
**版本**: v1.0.0 (P1迭代中)  
**状态**: 框架完成，精装修进行中

---

## 许可

内部使用 | 投资有风险，入市需谨慎

---

*这是一个会自我进化的超级SKILL。每一天，它都在学习、改进、变得更强。*
