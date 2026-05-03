---
name: REPORT-MANAGER
description: Report Manager for research document management and classification. Use for organizing investment reports and research workflows.
---

# Research Report Manager SKILL

专业的投研文档管理系统，实现研报的自动分类、全文检索、标签管理和飞书云文档同步。

## 功能特性

### 📁 自动分类归档
- **按股票分类**: 每只股票独立文件夹
- **按行业分类**: 新能源/半导体/医药生物等
- **按日期分类**: 年月维度归档
- **按评级分类**: 买入/增持/中性/减持
- **按来源分类**: 券商/机构分组

### 🔍 全文检索
- 关键词搜索（标题/内容）
- 多维度筛选（股票/行业/评级/日期）
- 标签过滤
- 结果排序（时间/相关性）

### 🏷️ 标签管理
- 自定义标签
- 行业标签
- 评级标签
- 主题标签

### ☁️ 飞书集成
- 自动上传云文档
- 文件夹同步
- 链接管理
- 权限控制

### 📊 统计分析
- 研报数量统计
- 行业分布分析
- 评级分布分析
- 覆盖股票统计

## 快速开始

```python
from skills.REPORT-MANAGER.SKILL import ResearchReportManager

# 初始化管理器
manager = ResearchReportManager()

# 添加研报
report = manager.add_report(
    file_path="report.pdf",
    title="宁德时代深度报告",
    stock_code="300750.SZ",
    source="中金公司",
    rating="买入",
    industry="新能源"
)

# 搜索研报
results = manager.search_reports(
    stock_code="300750.SZ",
    rating="买入"
)

# 获取统计
stats = manager.get_statistics()
```

## API参考

### ResearchReportManager

#### 初始化
```python
manager = ResearchReportManager(base_path="/path/to/reports")
```

#### 添加研报
```python
report = manager.add_report(
    file_path: str,           # 文件路径
    title: str,               # 标题
    stock_code: str,          # 股票代码
    stock_name: str,          # 股票名称
    author: str,              # 分析师
    source: str,              # 来源
    report_date: str,         # 日期 (YYYY-MM-DD)
    rating: str,              # 评级
    target_price: float,      # 目标价
    industry: str,            # 行业
    tags: List[str],          # 标签
    auto_organize: bool       # 自动归档
)
```

#### 搜索研报
```python
results = manager.search_reports(
    keyword: str,             # 关键词
    stock_code: str,          # 股票代码
    industry: str,            # 行业
    rating: str,              # 评级
    source: str,              # 来源
    start_date: str,          # 开始日期
    end_date: str,            # 结束日期
    tags: List[str]           # 标签
)
```

#### 获取统计
```python
stats = manager.get_statistics()
# Returns:
# {
#     "total_reports": 100,
#     "by_industry": {"新能源": 30, "半导体": 20},
#     "by_rating": {"买入": 50, "增持": 30},
#     "stocks_covered": 80
# }
```

## 目录结构

```
output/reports/
├── by_stock/              # 按股票分类
│   ├── 300750.SZ/
│   ├── 600519.SH/
│   └── ...
├── by_industry/           # 按行业分类
│   ├── 新能源/
│   ├── 半导体/
│   └── ...
├── by_date/               # 按日期分类
│   ├── 2024-05/
│   ├── 2024-04/
│   └── ...
├── by_rating/             # 按评级分类
│   ├── 买入/
│   ├── 增持/
│   └── ...
├── by_source/             # 按来源分类
│   ├── 中金公司/
│   ├── 中信证券/
│   └── ...
├── .metadata/             # 元数据
└── .index/                # 索引
    └── reports.json       # 研报索引
```

## 预定义分类

### 行业分类
- 半导体、新能源、医药生物
- 消费电子、人工智能、金融科技
- 新能源汽车、光伏、军工
- 化工、食品饮料、银行
- 房地产、传媒、通信

### 评级分类
- 买入、增持、中性、减持、卖出

### 来源分类
- 中金公司、中信证券、华泰证券
- 国泰君安、招商证券、广发证券
- 海通证券、兴业证券、天风证券

## 集成到A5L

```python
# 在A5L中使用
from ARCHITECT_5L.layer0_control.report_manager_integration import ReportManagerPlugin

# 初始化插件
report_plugin = ReportManagerPlugin()

# 分析完成后自动归档
result = analyze_stock("300750.SZ")
report_plugin.auto_archive(result)

# 搜索历史研报
reports = report_plugin.search("宁德时代", days=30)
```

## 飞书同步

```python
# 同步到飞书云文档
from skills.REPORT-MANAGER.feishu_sync import FeishuSync

sync = FeishuSync()
sync.upload_report(report, folder_token="your_folder_token")

# 批量同步
sync.sync_all_reports()
```

## 版本历史

- v1.0.0 (2024-05-02): 初始版本
  - 基础分类归档
  - 全文检索
  - 统计分析
  - 飞书集成

## 未来规划

- [ ] AI摘要生成
- [ ] 研报去重
- [ ] 评分对比
- [ ] 智能推荐
- [ ] 研报订阅
