---
name: auto-briefing
description: Automated briefing generation for daily market summaries. Use for creating personalized market briefings and investment updates.
---

# Auto Briefing SKILL

## 描述

数据获取模块，为现有报告系统提供实时数据获取能力（大盘指数、持仓盈亏、自选股排行），适用于大盘分析、持仓跟踪、自选股排序。

## 使用方法

触发此 Skill 的指令：
- `大盘分析` - 分析大盘走势
- `持仓跟踪` - 跟踪持仓盈亏
- `自选股排序` - 自选股排行

## 功能

### 1. 大盘指数
- 上证指数、深证成指、创业板指
- 涨跌幅、成交量
- 市场情绪指标
- 北向资金流向

### 2. 持仓盈亏
- 实时盈亏计算
- 持仓收益率
- 市值变动
- 盈亏归因

### 3. 自选股排行
- 涨跌幅排行
- 资金流向排行
- 技术指标排行
- 自定义排序

## 简报生成

```
📊 市场简报 (HH:MM)

【大盘】
├─ 上证: XXXX.XX (+X.XX%)
├─ 深证: XXXX.XX (+X.XX%)
└─ 创业: XXXX.XX (+X.XX%)

【我的持仓】
├─ 总盈亏: +XX.XX%
├─ 今日盈亏: +X.XX%
└─ 持仓市值: XXXX万

【自选股TOP5】
1. XXXXXX +X.XX%
2. XXXXXX +X.XX%
...
```
