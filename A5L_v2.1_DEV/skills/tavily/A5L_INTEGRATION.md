# Tavily Search Integration for A5L
# 配置A5L全面调用tavily-search

## 安装状态
- ✅ tavily skill已安装: /workspace/projects/workspace/skills/tavily/
- ✅ Python包已安装: tavily-python

## API Key配置
需要在环境变量中设置TAVILY_API_KEY:
```bash
export TAVILY_API_KEY="tvly-YOUR_API_KEY"
```

## A5L集成使用方法

### 1. 基础搜索
```python
import sys
sys.path.insert(0, '/workspace/projects/workspace/skills/tavily/scripts')
from tavily_search import search

result = search(
    query="AI investing trends 2026",
    api_key="tvly-YOUR_KEY",
    search_depth="advanced",
    max_results=10
)
```

### 2. 在投资研究中的使用场景

#### 场景1: 个股新闻搜索
```python
search(query="NVDA NVIDIA stock news today", topic="news", max_results=10)
```

#### 场景2: 行业研究
```python
search(query="AI data center infrastructure market size", search_depth="advanced")
```

#### 场景3: 宏观经济
```python
search(query="Fed interest rate decision May 2026", topic="news")
```

### 3. 与现有工具的对比

| 工具 | 用途 | 优势 |
|:----:|:----:|:----:|
| coze_web_search | 一般搜索 | 集成简单 |
| tavily_search | AI优化搜索 | AI生成答案、结构化结果 |
| exa_web_search | 精准搜索 | 神经网络搜索 |

### 4. 推荐配置

在A5L工具中优先使用tavily的场景:
- ✅ 需要AI总结搜索结果
- ✅ 需要结构化数据
- ✅ 新闻和实时信息
- ✅ 深度研究分析

## ✅ API Key 已配置

```bash
export TAVILY_API_KEY="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"
```

**状态**: ✅ 已配置并测试成功

**测试结果**:
```
✅ API Key 已设置: tvly-dev-1...
测试搜索: 'AI investing trends 2026'
{
  "success": true,
  "answer": "AI investment will reach $3 trillion by 2028...",
  "results": [...]
}
```

## 🎉 A5L现在可以全面调用tavily-search！
