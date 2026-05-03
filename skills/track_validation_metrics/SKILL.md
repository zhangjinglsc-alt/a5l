---
name: track_validation_metrics
description: Track and validate prediction accuracy, backtest performance, and system metrics. Use for performance attribution and strategy effectiveness measurement.
---

# Track Validation Metrics SKILL

## 描述

验证指标跟踪脚本，计算胜率、盈亏比、夏普比率，跟踪持仓盈亏、更新验证数据库、生成验证报告，适用于验证指标、盈亏跟踪、风险控制。

## 使用方法

触发此 Skill 的指令：
- `验证指标` - 查看验证指标
- `盈亏跟踪` - 跟踪持仓盈亏
- `风险控制` - 风险控制分析

## 指标计算

### 收益指标
- **总收益率** - 累计收益百分比
- **年化收益率** - 年化后的收益率
- **超额收益** - 相对基准的超额

### 风险指标
- **最大回撤** - 最大资金回撤幅度
- **波动率** - 收益率标准差
- **VaR** - 风险价值

### 风险调整收益
- **夏普比率** - 风险调整后收益
- **索提诺比率** - 下行风险调整后收益
- **卡玛比率** - 收益与最大回撤比

### 交易统计
- **胜率** - 盈利交易占比
- **盈亏比** - 平均盈利/平均亏损
- **期望收益** - 每笔交易期望收益

## 报告输出

```
================验证报告================
统计周期: YYYY-MM-DD 至 YYYY-MM-DD

【收益指标】
├─ 总收益率: XX.XX%
├─ 年化收益率: XX.XX%
└─ 超额收益: XX.XX%

【风险指标】
├─ 最大回撤: -XX.XX%
├─ 年化波动率: XX.XX%
└─ VaR(95%): -X.XX%

【风险调整收益】
├─ 夏普比率: X.XX
├─ 索提诺比率: X.XX
└─ 卡玛比率: X.XX

【交易统计】
├─ 总交易次数: XXX
├─ 盈利次数: XXX
├─ 亏损次数: XXX
├─ 胜率: XX.XX%
└─ 盈亏比: X.XX
```
