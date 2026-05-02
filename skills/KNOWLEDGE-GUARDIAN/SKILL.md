# Knowledge Guardian SKILL

A5L Layer0 知识库守护者 - 统一管理所有投研资料和交易记录

## 定位

**Layer**: Layer0 - Meta Control Layer  
**Role**: Chief Librarian / Knowledge Guardian  
**职责**: 知识的采集、组织、检索、同步和维护

## 核心功能

### 📚 知识采集
- **研报存储**: 券商研报自动归档
- **分析归档**: A5L生成的行业/个股分析
- **原始资料**: 图片/PDF/文章/公众号统一管理
- **交易记录**: 真实/模拟交易完整记录

### 🗂️ 知识组织
- **5维分类**: 类型/股票/行业/日期/来源
- **标签系统**: 灵活标签管理
- **重要性标记**: 关键知识高亮
- **归档机制**: 历史知识整理

### 🔍 知识检索
- **全文搜索**: 标题/内容关键词
- **多维筛选**: 股票/行业/类型/日期
- **快速调阅**: ID直接访问
- **访问统计**: 热门知识追踪

### ☁️ 知识同步
- **飞书同步**: 云文档自动上传
- **KIWI归档**: 知识库长期沉淀
- **批量导出**: 一键同步所有内容

### 📊 知识维护
- **统计分析**: 知识库全景视图
- **定期清理**: 过期内容归档
- **版本管理**: 知识更新追踪

## 目录结构

```
knowledge_base/
├── research/              # 投研资料
│   ├── reports/          # 券商研报
│   ├── industry/         # 行业分析
│   ├── stock/            # 个股分析
│   └── market/           # 市场点评
├── raw/                   # 原始资料
│   ├── pdf/              # PDF文档
│   ├── images/           # 图片资料
│   ├── articles/         # 网络文章
│   ├── wechat/           # 公众号文章
│   └── news/             # 新闻资讯
├── trades/                # 交易记录
│   ├── real/             # 真实交易
│   ├── simulated/        # 模拟交易
│   └── portfolio/        # 持仓快照
├── system/                # 系统生成
│   ├── strategy/         # 策略报告
│   ├── review/           # 复盘报告
│   └── alerts/           # 告警记录
└── .index/                # 索引数据
    ├── knowledge.json    # 知识索引
    └── trades.json       # 交易索引
```

## 快速开始

### 初始化
```python
from ARCHITECT_5L.layer0_control.knowledge_guardian import KnowledgeGuardian

guardian = KnowledgeGuardian()
```

### 存储研报
```python
# 用户上传的研报
report = guardian.store_research_report(
    file_path="report.pdf",
    title="宁德时代深度报告",
    stock_code="300750.SZ",
    source="中金公司",
    rating="买入",
    industry="新能源"
)
```

### 存储A5L分析
```python
# A5L生成的分析报告
analysis = guardian.store_analysis_report(
    file_path="analysis.md",
    title="宁德时代 - A5L智能分析",
    analysis_type="stock",
    stock_code="300750.SZ"
)
```

### 存储交易记录
```python
# 真实交易
trade = guardian.store_trade_record({
    "account_id": "REAL_001",
    "symbol": "300750.SZ",
    "trade_date": "2024-05-02",
    "action": "BUY",
    "quantity": 100,
    "price": 185.50,
    "strategy": "价值投资"
}, trade_type="real")

# 模拟交易
trade = guardian.store_trade_record({
    "account_id": "US_SIM_001",
    "symbol": "AAPL",
    "trade_date": "2024-05-02",
    "action": "SELL",
    "quantity": 10,
    "price": 180.00
}, trade_type="simulated")
```

### 搜索知识
```python
# 搜索宁德时代相关研报
results = guardian.search_knowledge(
    stock_code="300750.SZ",
    content_type=ContentType.RESEARCH_REPORT
)

# 搜索所有交易记录
trades = guardian.search_trades(
    symbol="300750.SZ",
    trade_type="real"
)
```

### 统计分析
```python
# 知识库统计
kb_stats = guardian.get_knowledge_stats()
print(f"总知识条目: {kb_stats['total_items']}")
print(f"覆盖股票数: {kb_stats['stocks_covered']}")

# 交易统计
trade_stats = guardian.get_trade_stats(trade_type="real")
print(f"总交易数: {trade_stats['total_trades']}")
print(f"总盈亏: {trade_stats['total_pnl']}")
```

## 内容类型

| 类型 | 说明 | 存储路径 |
|------|------|----------|
| RESEARCH_REPORT | 券商研报 | research/reports/ |
| INDUSTRY_ANALYSIS | 行业分析 | research/industry/ |
| STOCK_ANALYSIS | 个股分析 | research/stock/ |
| PDF_DOCUMENT | PDF文档 | raw/pdf/ |
| IMAGE | 图片资料 | raw/images/ |
| ARTICLE | 网络文章 | raw/articles/ |
| WECHAT_ARTICLE | 公众号 | raw/wechat/ |
| REAL_TRADE | 真实交易 | trades/real/ |
| SIMULATED_TRADE | 模拟交易 | trades/simulated/ |

## 集成到A5L

### 在分析工作流中使用
```python
from ARCHITECT_5L.layer0_control.knowledge_guardian import KnowledgeGuardian

guardian = KnowledgeGuardian()

# 分析完成后自动归档
def analyze_and_archive(stock_code):
    # 执行分析
    result = analyze_stock(stock_code)
    
    # 自动存储到知识库
    analysis = guardian.store_analysis_report(
        file_path=result['report_path'],
        title=result['title'],
        analysis_type="stock",
        stock_code=stock_code
    )
    
    return analysis
```

### 在交易系统中使用
```python
# 交易执行后记录
def execute_trade(trade_data):
    # 执行交易
    result = broker.execute(trade_data)
    
    # 记录到知识库
    guardian.store_trade_record({
        "account_id": trade_data['account_id'],
        "symbol": trade_data['symbol'],
        "trade_date": datetime.now().strftime('%Y-%m-%d'),
        "action": trade_data['action'],
        "quantity": trade_data['quantity'],
        "price": trade_data['price'],
        "strategy": trade_data.get('strategy'),
        "reason": trade_data.get('reason')
    }, trade_type="real")
```

### 在飞书同步中使用
```python
# 自动同步研报到飞书
report = guardian.store_research_report(
    file_path="report.pdf",
    title="...",
    stock_code="300750.SZ",
    auto_sync_feishu=True  # 自动同步
)
```

## API参考

### KnowledgeGuardian

#### 存储接口
- `store_knowledge()` - 通用存储
- `store_research_report()` - 存储研报
- `store_analysis_report()` - 存储分析报告
- `store_raw_content()` - 存储原始内容
- `store_trade_record()` - 存储交易记录

#### 检索接口
- `search_knowledge()` - 搜索知识
- `search_trades()` - 搜索交易
- `get_knowledge_by_id()` - ID获取知识
- `get_trade_by_id()` - ID获取交易

#### 组织接口
- `tag_knowledge()` - 添加标签
- `mark_important()` - 标记重要
- `archive_knowledge()` - 归档知识

#### 统计接口
- `get_knowledge_stats()` - 知识库统计
- `get_trade_stats()` - 交易统计

## 飞书集成

```python
# 同步单个知识条目
guardian._sync_to_feishu(item)

# 批量导出到飞书
guardian.export_to_feishu(item_ids=['id1', 'id2'])

# 全部导出
guardian.export_to_feishu()
```

## KIWI集成

```python
# 同步到KIWI知识库
guardian._sync_to_kiwi(item)
```

## 版本历史

- v1.0.0 (2026-05-02): 初始版本
  - 知识采集与存储
  - 5维分类体系
  - 全文检索
  - 交易记录管理
  - 飞书/KIWI同步框架

## 未来规划

- [ ] AI内容摘要生成
- [ ] 知识图谱构建
- [ ] 智能推荐系统
- [ ] 版本控制
- [ ] 协作编辑
