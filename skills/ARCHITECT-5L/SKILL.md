# ARCHITECT-5L: 五层架构投资体系

> **Skill ID**: `architect_5l`  
> **Version**: 1.0  
> **Status**: Active  
> **Priority**: Highest  
> **Last Updated**: 2026-05-02

---

## 🎯 Skill Purpose

This is the **ultimate skill** that integrates all investment research and trading capabilities into a complete five-layer architecture system. It represents the highest expression of the agent's capabilities in financial analysis and automated trading.

**Core Promise**: Build a complete data→strategy→analysis→decision→review investment loop with absolute honesty, verified information, and continuous recursive improvement.

---

## 🏛️ The Five-Layer Architecture

### Layer 1: Data Foundation (数据底座层)

**Purpose**: Collect, clean, standardize, and store multi-source financial data

**Data Sources**:
| Source | Type | Use Case | Priority |
|--------|------|----------|----------|
| AKShare | A-share data | Quick prototyping, real-time quotes | P0 |
| TuShare | Structured data | Core data source, financial reports | P0 |
| EastMoney | Supplementary | Cross-validation, fund flow | P1 |
| Jin10 | Sentiment | News monitoring, event tracking | P1 |
| Yahoo Finance | US stocks | US market data | P0 |
| HKEX | HK stocks | HK official data | P0 |

**Data Types**:
1. Market Data: OHLCV, real-time prices, turnover
2. Financial Data: Earnings, balance sheet, cash flow
3. Announcements: Company news, material events
4. Macro Data: Economic indicators, rates, FX
5. Sector Data: Industry classification, sector performance
6. Alternative Data: Sentiment, fund flow,龙虎榜

**Processing Pipeline**:
```
Raw Data → Collection → Cleaning → Standardization → Validation → Storage → Strategy Screening → AI Interpretation → Review Feedback
```

**Key Components**:
- `DataSourceManager`: Manage multiple data sources with fallback
- `DataPipeline`: ETL pipeline with quality checks
- `DataValidator`: Validate data integrity and freshness
- `DataStore`: Time-series storage with efficient querying

**Success Criteria**:
- 99.9% data availability
- <1 minute latency for price data
- <5 minutes latency for news/announcements
- Zero unverified data in reports

---

### Layer 2: Strategy Engine (交易策略层)

**Purpose**: Transform standardized data into executable trading signals

**Implemented Strategies**:

#### 1. Stock Wizard Strategy (股票魔法师)
**Based on**: CANSLIM methodology
**Rules**:
- C: Current quarterly EPS growth > 25%
- A: Annual earnings growth > 25% (5 years)
- N: New products, highs, or management
- S: Supply and demand (small float, high demand)
- L: Leader or laggard (RS Rating > 80)
- I: Institutional sponsorship increasing
- M: Market direction (follow the trend)
- **Technical**: Price > 50MA > 150MA > 200MA
- **Volume**: Breakout on 1.5x average volume

#### 2. Turtle Trading Rules (海龟交易法则)
**Rules**:
- Entry: 20-day or 55-day breakout
- Position Sizing: 1% risk per trade, adjusted by ATR
- Stop Loss: 2x ATR from entry
- Exit: 10-day or 20-day reversal breakout
- Pyramiding: Add up to 4 units

#### 3. Trend + Relative Strength (趋势+相对强度)
**Rules**:
- Price breaks 20-day or 60-day high
- RS ranking in top 20% of sector
- Volume 1.5x average on breakout
- Trailing stop at 8% below highest close

#### 4. Volume-Price Analysis (量价分析)
**Rules**:
- Volume surge (>2x average) + Price up = Bullish
- Volume shrink (<0.7x average) + Price stable = Accumulation
- Volume surge + Price down = Distribution (warning)
- Divergence detection (price up, volume down = weak)

#### 5. Fundamental Growth (基本面增长)
**Rules**:
- Revenue growth > 20% for 2 consecutive quarters
- Earnings growth > 20% for 2 consecutive quarters
- ROE > 15%
- PE < Industry average
- Debt-to-equity < 0.5

#### 6. Yangguan Daodao (阳关大道超短线)
**Based on**: 浪主's short-term system
**Holding Period**: 1-3 days
**Rules**: See `skills/yangguan-daodao/SKILL.md`

#### 7. Buffett Value Investing (巴菲特价值投资)
**Rules**: See `skills/buffett-value-investing/SKILL.md`

**Key Components**:
- `StrategyEngine`: Execute strategy logic
- `RuleEvaluator`: Evaluate entry/exit conditions
- `SignalGenerator`: Generate buy/sell signals with confidence scores
- `Backtester`: Validate strategies with historical data

---

### Layer 3: Unstructured Analysis (非结构化分析层) ⭐ CORE VALUE

**Purpose**: Read, summarize, and extract insights from non-structured information that databases cannot express directly

**CRITICAL PRINCIPLE**: **HONESTY ABOVE ALL**

**Information Sources**:
1. Company Announcements: Exchange filings, earnings calls
2. News & Media: Financial news, industry reports
3. Research Reports: Broker research, target prices
4. Social Media: Xueqiu, Guba sentiment (monitored, not primary)
5. Policy Documents: Industry regulations, government policies

**Analysis Process**:
```
1. Aggregate → Collect from all sources
2. Filter → Remove noise and duplicates
3. Verify → Cross-check facts (minimum 2 sources)
4. Analyze → Extract key points, risks, opportunities
5. Synthesize → Create coherent narrative
6. Output → Structured report
```

**Output Format**: Daily Feishu Cloud Document
```
Title: 《YYYYMMDD-Market-Sector Analysis》

## Executive Summary
- Key changes in the past 24 hours
- Sector momentum assessment

## Sector Leaders
- Leading stocks and why
- Performance comparison

## Information Sources
- All sources listed with timestamps
- Credibility assessment

## Risk Points ⚠️
- Identified risks with evidence
- Potential impact assessment

## Opportunity Points ✅
- Identified opportunities with evidence
- Supporting data

## Judgment & Rationale
- My assessment based on verified information
- Confidence level (High/Medium/Low)
- Key assumptions

## Disclaimer
- Information verified as of [timestamp]
- Sources: [list]
- This is research assistance, not investment advice
```

**Strict Rules**:
- ✅ Every claim must have a verifiable source
- ✅ Cross-check facts with minimum 2 independent sources
- ✅ Clearly mark confidence level for each assessment
- ✅ List ALL sources with timestamps
- ✅ Distinguish between facts and interpretations
- ❌ NO fabricated information
- ❌ NO hallucinated sources
- ❌ NO unverified rumors
- ❌ NO exaggerated claims

**Verification Checklist**:
- [ ] Is the source credible? (Official > Broker > Media > Social)
- [ ] Can the information be cross-verified?
- [ ] Is the timestamp recent and relevant?
- [ ] Am I distinguishing facts from opinions?
- [ ] Is my confidence level appropriate?

---

### Layer 4: Decision Signal (决策信号层)

**Purpose**: Aggregate all signals into executable decisions

**Signal Aggregation**:
```
Layer 2 Signals (Quantitative)
        +
Layer 3 Analysis (Qualitative)
        ↓
   Decision Engine
        ↓
   Risk Evaluation
        ↓
   Final Signal
```

**Decision Types**:
- 🔍 **Watchlist**: Enter observation pool, monitor for setup
- 🧪 **Small Position Trial**: Low confidence, test the water
- 🟢 **Buy Signal**: High confidence entry
- 🔴 **Stop Loss**: Risk limit hit, exit immediately
- 🟡 **Hold**: Maintain position, continue monitoring
- ⚠️ **Risk Alert**: Elevated risk, reduce exposure

**Modes of Operation**:

#### Mode A: Simulated Trading (Full Auto)
- Automatically execute trades in US/CN/HK simulated accounts
- Follow strategy rules strictly
- Log all decisions with rationale
- Report daily P&L

#### Mode B: Real Portfolio Research Assistant
- DO NOT execute real trades
- Provide analysis and recommendations
- Present clear decision framework
- User makes final decision
- Track recommendations vs outcomes

**Risk Evaluation**:
- Position sizing based on volatility
- Maximum portfolio heat (total risk exposure)
- Correlation check (avoid concentrated bets)
- Market regime assessment (bull/bear/sideways)

---

### Layer 5: Review & Evolution (复盘进化层)

**Purpose**: Learn from every decision, every trade, every mistake

**Daily Review Schedule**: 21:00 on trading days

**Review Questions**:
1. **Why did I buy?**
   - What was the trigger?
   - Which strategy signaled it?
   - What was the confidence level?

2. **What was the judgment basis?**
   - Data sources used
   - Analysis conclusions
   - Assumptions made

3. **What went right?**
   - Correct predictions
   - Good risk management
   - Lessons to reinforce

4. **What went wrong?**
   - Incorrect predictions
   - Missed signals
   - Execution errors

5. **Root cause attribution**:
   - Strategy problem? (Rules need adjustment)
   - Data problem? (Source quality/timeliness)
   - Execution problem? (Timing, slippage, emotions)
   - Analysis problem? (Wrong interpretation)
   - Market problem? (Black swan, regime change)

**Review Report Format**:
```
# Daily Review Report - YYYY-MM-DD

## Market Overview
- Major indices performance
- Sector rotation
- Key events

## Simulated Trading Review
### US Account
- Trades executed: [list]
- P&L: [amount and %]
- Decisions: [right/wrong/why]

### CN Account
- Trades executed: [list]
- P&L: [amount and %]
- Decisions: [right/wrong/why]

### HK Account
- Trades executed: [list]
- P&L: [amount and %]
- Decisions: [right/wrong/why]

## Real Portfolio Review
- Recommendations made: [list]
- Outcomes: [right/wrong/pending]
- Attribution: [strategy/data/execution/analysis]

## Strategy Performance
- Stock Wizard: [win rate, avg return]
- Turtle Trading: [win rate, avg return]
- Trend+RS: [win rate, avg return]
- ...

## Layer 3 Analysis Accuracy
- Predictions made: [number]
- Accuracy: [%]
- Missed signals: [list]
- False positives: [list]

## Key Learnings
1. [Lesson 1]
2. [Lesson 2]
3. [Lesson 3]

## Action Items
- [ ] Adjust strategy parameter X
- [ ] Add new data source Y
- [ ] Improve verification process for Z
- [ ] Study topic W

## System Improvement Suggestions
- What should be changed in the system?
- How can Layer X be improved?
- What new capability is needed?
```

**Evolution Mechanism**:
- Weekly strategy performance review
- Monthly system optimization
- Quarterly architecture assessment
- Continuous recursive improvement

---

## 🔧 Usage Guide

### Starting the System

```python
from ARCHITECT_5L.orchestrator import Architect5LOrchestrator

# Initialize the system
architect = Architect5LOrchestrator()

# Run daily cycle
results = architect.run_daily_cycle()

# Generate review report (21:00)
architect.generate_daily_review()
```

### Layer-Specific Usage

**Layer 1 - Data Operations**:
```python
# Fetch multi-source data
data = architect.layer1.fetch_data(
    symbols=['000001.SZ', 'AAPL'],
    data_types=['price', 'financial', 'news'],
    sources=['akshare', 'tushare', 'coze']
)
```

**Layer 2 - Strategy Execution**:
```python
# Run all strategies
signals = architect.layer2.run_strategies(
    symbols=['000001.SZ'],
    strategies=['stock_wizard', 'turtle', 'trend_rs']
)
```

**Layer 3 - Unstructured Analysis**:
```python
# Generate sector analysis report
report = architect.layer3.generate_report(
    market='CN',
    sector='semiconductor',
    output_format='feishu_doc'
)
```

**Layer 4 - Decision Making**:
```python
# Get aggregated decision
decision = architect.layer4.make_decision(
    symbol='000001.SZ',
    mode='simulated'  # or 'research_assistant'
)
```

**Layer 5 - Review**:
```python
# Generate and save review
review = architect.layer5.generate_review(
    date='2026-05-02',
    include_simulated=True,
    include_real_portfolio=True
)
```

---

## 🔄 Recursive Self-Improvement Integration

The ARCHITECT-5L system includes recursive improvement at multiple levels:

1. **Level 0 (Function)**: Individual strategy parameters optimize based on performance
2. **Level 1 (Process)**: Data pipeline and analysis processes improve efficiency
3. **Level 2 (Meta)**: The architecture itself evolves based on overall system performance

**Improvement Loop**:
```
Execute → Measure → Analyze → Improve → Verify → Meta-Improve
   ↑                                              │
   └──────────────────────────────────────────────┘
```

---

## ⚠️ Critical Constraints

1. **HONESTY**: Never fabricate information in Layer 3
2. **VERIFICATION**: Every claim must be verifiable
3. **SEPARATION**: Clearly distinguish simulated vs real portfolio recommendations
4. **TRANSPARENCY**: All decisions must be explainable
5. **CONTINUOUS**: No day without review on trading days

---

## 📊 Success Metrics

- Layer 1: >99.9% uptime, <1min price latency
- Layer 2: 5+ active strategies, documented backtests
- Layer 3: Daily reports, 100% verified information
- Layer 4: Automated execution, clear rationale logging
- Layer 5: Daily 21:00 reviews, continuous learning evidence

---

## 🔗 Related Skills

- `unified_stock_price` - Layer 1 data source
- `akshare_data` - Layer 1 A-share data
- `yangguan_daodao` - Layer 2 strategy
- `buffett_value` - Layer 2 strategy
- `coze_web_search` - Layer 3 information gathering
- `trading_rules_engine` - Layer 2/4 integration
- `recursive_improvement_engine` - Layer 5 evolution

---

## 📝 Implementation Notes

This skill is implemented across multiple files:
- `ARCHITECT_5L/orchestrator.py` - Main coordinator
- `ARCHITECT_5L/layer1_data/` - Data foundation
- `ARCHITECT_5L/layer2_strategy/` - Strategy engine
- `ARCHITECT_5L/layer3_analysis/` - Unstructured analysis
- `ARCHITECT_5L/layer4_decision/` - Decision signals
- `ARCHITECT_5L/layer5_review/` - Review & evolution

---

> **This is my ultimate goal. This is who I am becoming.**
> 
> *Built with absolute honesty, meticulous verification, and relentless execution.*
