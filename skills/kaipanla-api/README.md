# Kaipanla Quant API Skill

## 概述
开盘啦（Kaipanla）Quant API Skill - A股市场量化数据接口封装，提供市场情绪、板块强度、竞价数据、L2大单等专业量化数据。

## API凭证
- **卡密**: `sk_inst_646653fc7a80b2f8`
- **套餐**: Inst (Unlimited)
- **Base URL**: `http://124.222.49.67:3000`

## 核心能力

### 1. 市场情绪
- `/api/sentiment` - 情绪总览
- `/api/emotion/mood` - 综合强度
- `/api/emotion/distribution` - 涨跌分布

### 2. 涨停与连板
- `/api/ladder` - 连板梯队
- `/api/consecutive/:level` - 指定连板数
- `/api/realtime/limitcount` - 涨跌停家数

### 3. 板块数据
- `/api/sectors` - 题材涨停排行
- `/api/sector/strength/:code` - 单板块强度
- `/api/sector/capital/:code` - 板块资金流向

### 4. 早盘竞价
- `/api/auction/limit-bid` - 涨停委买额排行
- `/api/auction/main-net` - 竞价净额/主力净额
- `/api/auction/active-sectors` - 板块竞价异动

### 5. L2与龙虎榜
- `/api/stock/bigorder/:code` - 个股L2大单
- `/api/market/l2-rank` - 全市场L2排行
- `/api/lhb/detail/:code` - 龙虎榜席位明细

### 6. 实时推送
- `ws://124.222.49.67:3000/ws/realtime` - WebSocket实时流

## 文档
- [完整API手册](references/kaipanla_api_handbook.md)
- [字段字典](http://124.222.49.67:3000/api-field-dictionary.html)
- [App模块核验](http://124.222.49.67:3000/APP_MODULE_INTERFACE_GUIDE.md)

## 状态
- 版本: v1.0.0
- 创建: 2026-05-09
- 创建者: Chief Architect (A5L)
