---
name: catalyst-monitor-auto
description: 自动催化事件监控系统 - 主动抓取市场催化事件，自动应用CTF框架分析，并推送提醒。支持新闻聚合、智能分级、定时监控、推送通知。Use when: (1) 需要自动监控市场催化事件，(2) 需要定时获取AI/算力/存储等行业新闻，(3) 需要自动识别催化级别(Tier1-4)，(4) 需要推送重要催化事件提醒。
---

# Catalyst Monitor Auto - 自动催化事件监控系统

> **版本**: v1.0.0  
> **创建时间**: 2026-05-07  
> **所属框架**: A5L Layer 2 策略引擎  
> **配套SKILL**: CTF催化剂分级框架  

---

## 🎯 系统功能

自动催化事件监控系统主动抓取市场信息，自动应用CTF框架进行分级分析，并推送重要事件提醒。

### 核心能力
1. **定时新闻抓取** - 每30分钟扫描28+高价值信源
2. **智能催化识别** - 自动识别Tier 1-4级别催化事件
3. **CTF自动分析** - 应用催化剂分级框架生成分析报告
4. **推送通知** - 重要事件自动推送到飞书
5. **历史归档** - 所有事件自动归档到知识库

---

## 📡 监控数据源

| 数据源 | 类型 | 频率 | 覆盖内容 |
|:-------|:-----|:----:|:---------|
| 统一新闻聚合 | 财经新闻 | 30分钟 | 28+高价值信源 |
| Coze网页搜索 | 实时搜索 | 1小时 | 特定主题深度搜索 |
| Tavily搜索 | AI搜索 | 2小时 | 深度研究与英文资料 |
| 股票异动监控 | 价格/成交量 | 实时 | 涨停/异动自动触发 |

### 监控主题 (可配置)
- AI算力/服务器CPU/GPU
- 存储芯片/HBM/DDR
- 光模块/CPO/光通信
- 半导体设备/材料
- 低空经济/eVTOL
- 人形机器人/具身智能

---

## ⚙️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│  定时任务层 (Cron)                                           │
│  ├── 每30分钟: 新闻抓取 + 基础分析                           │
│  ├── 每1小时: 深度搜索 + CTF分级                             │
│  ├── 每2小时: Tavily深度研究                                 │
│  └── 实时: 股票异动监控                                      │
├─────────────────────────────────────────────────────────────┤
│  分析引擎层                                                   │
│  ├── 事件提取器: 从新闻中提取催化事件                        │
│  ├── CTF分级器: 自动判定Tier 1-4级别                       │
│  ├── 影响评估器: 评估对持仓的影响                            │
│  └── 重复过滤: 去重与相关性分析                              │
├─────────────────────────────────────────────────────────────┤
│  推送通知层                                                   │
│  ├── Tier 1: 立即推送 + 声音提醒                             │
│  ├── Tier 2: 立即推送                                        │
│  ├── Tier 3: 每小时汇总推送                                  │
│  └── Tier 4: 每日汇总推送                                    │
├─────────────────────────────────────────────────────────────┤
│  知识库存档层                                                 │
│  └── 自动归档到: 概念/催化事件-YYYYMMDD                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 使用方法

### 启动监控

```bash
# 启动完整监控
python3 skills/catalyst-monitor-auto/scripts/monitor.py start

# 启动特定主题监控
python3 skills/catalyst-monitor-auto/scripts/monitor.py start --topic "AI算力"

# 仅监控特定股票相关
python3 skills/catalyst-monitor-auto/scripts/monitor.py start --stocks "000066,601975"
```

### 手动触发分析

```bash
# 立即执行一次完整扫描
python3 skills/catalyst-monitor-auto/scripts/monitor.py scan

# 分析特定主题
python3 skills/catalyst-monitor-auto/scripts/monitor.py analyze "存储芯片涨价"

# 生成日报
python3 skills/catalyst-monitor-auto/scripts/monitor.py daily-report
```

### 查看监控状态

```bash
# 查看当前监控状态
python3 skills/catalyst-monitor-auto/scripts/monitor.py status

# 查看今日已识别事件
python3 skills/catalyst-monitor-auto/scripts/monitor.py events --today

# 查看特定级别事件
python3 skills/catalyst-monitor-auto/scripts/monitor.py events --tier 1
```

---

## 📋 CTF自动分级逻辑

系统自动应用CTF框架进行催化事件分级：

### Tier 1 - 范式级 识别规则
- TAM上修关键词: "TAM上调", "市场规模翻倍", "需求超预期"
- 技术主流化: "成为主流", "确立标准", "行业采用"
- 供需结构: "政策永久", "格局改变", "不可逆"

### Tier 2 - 周期确认级 识别规则
- 长协锁定: "LTA", "长协", "锁定产能", "订单排至20XX"
- 订单上修: "订单超预期", "指引上调", "产能满载"

### Tier 3 - 资金驱动级 识别规则
- 大额订单: "XX亿订单", "XX亿合同", "战略签约"
- 政策发布: "政策出台", "补贴", "规划发布"
- 战略合作: "战略合作", "收购", "合并"

### Tier 4 - 补涨扩散级 识别规则
- 涨价叙事: "涨价", "价格上调", "供不应求"
- 补涨关键词: "补涨", "扩散", "关联"

---

## 🔔 推送规则

| 级别 | 触发条件 | 推送方式 | 内容 |
|:----:|:---------|:---------|:-----|
| **Tier 1** | 自动识别 | 飞书即时消息 + 声音 | 事件+CTF分析+持仓影响+操作建议 |
| **Tier 2** | 自动识别 | 飞书即时消息 | 事件+CTF分析+关注建议 |
| **Tier 3** | 自动识别 | 每小时汇总 | 事件列表+简要分析 |
| **Tier 4** | 自动识别 | 每日汇总 | 事件列表 |
| **持仓相关** | 持有股票相关新闻 | 即时推送 | 事件+影响评估 |

---

## 📁 文件结构

```
skills/catalyst-monitor-auto/
├── SKILL.md                          # 本文件
├── scripts/
│   ├── monitor.py                    # 主监控脚本
│   ├── analyzer.py                   # CTF分析器
│   ├── notifier.py                   # 推送通知器
│   └── config.py                     # 配置文件
├── references/
│   ├── tier_keywords.json            # 分级关键词库
│   ├── monitored_topics.json         # 监控主题配置
│   └── api_keys.template             # API密钥模板
└── data/                             # 数据存储 (自动生成)
    ├── events/                       # 事件档案
    └── logs/                         # 运行日志
```

---

## 🔧 配置说明

### API密钥配置

复制模板并填入密钥:
```bash
cp references/api_keys.template references/api_keys.json
# 编辑 references/api_keys.json 填入密钥
```

### 监控主题配置

编辑 `references/monitored_topics.json`:
```json
{
  "topics": [
    "AI算力",
    "服务器CPU",
    "存储芯片",
    "光模块",
    "半导体设备"
  ],
  "stocks": ["000066", "601975", "688981"],
  "min_tier": 2
}
```

---

## 📊 与CTF框架集成

本系统与CTF催化剂分级框架无缝集成:

1. **自动调用CTF分析** - 识别的事件自动应用CTF分级
2. **仓位建议** - 根据Tier级别生成仓位配置建议
3. **一致性高潮检测** - 监控涨停潮信号
4. **预期差识别** - 提示预期差入口

当系统识别到事件后，会:
1. 自动调用CTF框架进行分级
2. 生成完整的分析报告
3. 推送到飞书
4. 归档到知识库

---

## 🏷️ 标签

#自动监控 #催化事件 #CTF #实时推送 #新闻聚合 #A5L #Layer2

---

> **使用提示**: 首次使用请先配置API密钥和监控主题，然后运行 `python3 scripts/monitor.py start` 启动监控。
