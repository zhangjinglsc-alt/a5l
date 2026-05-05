# Tushare新闻数据接口使用指南

> 会员等级: 新闻包年会员  
> 更新时间: 2026-05-05 23:48

---

## 📰 新闻数据来源

Tushare提供以下新闻数据源:

| 来源代码 | 来源名称 | 说明 |
|----------|----------|------|
| `sina` | 新浪财经 | 主流财经媒体 |
| `10jqka` | 同花顺 | 专业金融数据 |
| `eastmoney` | 东方财富 | 综合财经门户 |
| `yuncaijing` | 云财经 | 财经快讯 |
| `财联社` | 财联社 | 电报式快讯 |

---

## 🔧 使用方法

### 基础调用

```python
from tools.data_unified import get_data_source

ds = get_data_source()

# 获取新浪财经重大新闻
news = ds.get_major_news(
    src='sina',
    start_date='2026-05-04 00:00:00',
    end_date='2026-05-05 23:59:59'
)
```

### 获取新闻内容

```python
# 获取带内容的新闻
news = ds.get_major_news_with_content(
    src='sina',
    start_date='2026-05-04 00:00:00',
    end_date='2026-05-05 23:59:59'
)

# 访问内容
for _, row in news.iterrows():
    print(f"标题: {row['title']}")
    print(f"内容: {row['content'][:200]}...")
    print(f"时间: {row['datetime']}")
```

### 多源新闻聚合

```python
# 聚合多个来源的新闻
sources = ['sina', 'eastmoney', '10jqka']
all_news = []

for src in sources:
    df = ds.get_major_news(src=src)
    if len(df) > 0:
        df['source'] = src
        all_news.append(df)

# 合并所有来源
if all_news:
    combined_news = pd.concat(all_news, ignore_index=True)
    # 按时间排序
    combined_news = combined_news.sort_values('datetime', ascending=False)
```

---

## 📊 返回字段说明

### major_news 接口

| 字段 | 类型 | 说明 |
|------|------|------|
| `datetime` | string | 新闻时间 |
| `title` | string | 新闻标题 |
| `content` | string | 新闻内容(需指定fields) |
| `src` | string | 来源 |

### news 接口 (个股新闻)

| 字段 | 类型 | 说明 |
|------|------|------|
| `datetime` | string | 发布时间 |
| `title` | string | 标题 |
| `content` | string | 内容 |
| `ts_code` | string | 股票代码 |

---

## ⚠️ 使用注意事项

### 1. 日期格式
必须使用正确的时间格式:
```python
# ✅ 正确
start_date='2026-05-04 00:00:00'

# ❌ 错误
start_date='20260504'
```

### 2. 数据时效性
- 重大新闻: 实时更新
- 个股新闻: 延迟约15-30分钟
- 新闻内容: 部分来源可能需要额外权限

### 3. 积分消耗
- 重大新闻: 每次调用消耗积分
- 建议: 合理控制调用频次，避免频繁请求

---

## 💡 A5L应用场景

### 场景1: 持仓股新闻监控
```python
def monitor_portfolio_news(portfolio):
    """监控持仓股新闻"""
    for stock in portfolio:
        news = ds.get_stock_news(stock['code'], limit=10)
        # 分析新闻情感
        # 如有负面新闻，发送预警
```

### 场景2: 重大新闻自动摘要
```python
def generate_news_summary():
    """生成每日新闻摘要"""
    # 获取当天重大新闻
    news = ds.get_major_news_with_content()
    
    # 使用AI生成摘要
    summary = ai_summarize(news['content'].tolist())
    
    return summary
```

### 场景3: 新闻驱动交易策略
```python
def news_based_strategy():
    """新闻驱动交易策略"""
    # 获取实时新闻
    news = ds.get_major_news()
    
    # 关键词匹配
    for _, row in news.iterrows():
        if '人工智能' in row['title'] or 'AI' in row['title']:
            # AI相关新闻，关注AI概念股
            pass
```

---

## 🔍 故障排查

### 问题1: 返回空数据
**可能原因**:
- 指定时间段内确实无新闻
- 新闻源维护
- 会员权限不足

**解决方法**:
```python
# 尝试不同日期
for i in range(7):  # 最近7天
    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d 00:00:00')
    news = ds.get_major_news(start_date=date)
    if len(news) > 0:
        break
```

### 问题2: 缺少content字段
**解决方法**:
```python
# 使用带内容的接口
news = ds.get_major_news_with_content()
```

---

## 📈 会员特权

作为**新闻包年会员**，您享有:
- ✅ 无限制访问重大新闻
- ✅ 个股新闻实时获取
- ✅ 多源新闻聚合
- ✅ 新闻内容全文获取

---

*新闻数据接口使用指南*  
*A5L实时行情互联系统*
