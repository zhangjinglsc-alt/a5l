# Kaipanla Quant API 全量技术手册
本文档用于给开发者或 AI Agent 快速接入 Kaipanla Quant API。把本文档完整提供给 AI 后，AI 应该能够知道基础地址、鉴权方式、日期参数、常用接口、返回日期判断方式，以及如何写代码调用接口。
更新时间：2026-05-06
生产环境 Base URL：`http://124.222.49.67:3000`
说明：域名备案完成前，所有示例统一使用 IP 地址 `http://124.222.49.67:3000`，不要使用旧域名。

## 0. 快速接入与阅读路径
这份手册按"先找接口，再看参数，再查字段"的顺序组织，避免客户必须从头读到尾。

最快接入路径：
1. 用 `http://124.222.49.67:3000` 作为 Base URL。
2. 把 API Key 放在请求头：`x-api-key: YOUR_API_KEY`。
3. 先查"全量公共接口清单"，定位接口路径和权限。
4. 再看"关键接口示例"，确认请求参数、返回字段和日期语义。
5. 字段很多时，直接打开字段字典搜索字段名或接口路径。

常用场景入口：
| 场景 | 推荐入口 |
| --- | --- |
| 市场情绪、涨跌停、连板梯队 | `/api/sentiment`、`/api/ladder`、`/api/consecutive/:level` |
| 板块强度、板块资金、题材事件 | `/api/sectors`、`/api/sector/capital/:code`、`/api/market/theme-events` |
| 早盘竞价、竞价净额、板块竞价 | `/api/auction/limit-bid`、`/api/auction/main-net`、`/api/auction/active-sectors` |
| L2 大单、实时龙虎榜、席位明细 | `/api/stock/bigorder/:code`、`/api/market/l2-rank`、`/api/lhb/detail/:code` |
| 高频实时推送 | `ws://124.222.49.67:3000/ws/realtime` |

配套页面：
- 网页版全量文档：`http://124.222.49.67:3000/docs.html`
- 字段字典搜索版：`http://124.222.49.67:3000/api-field-dictionary.html`
- App 模块化核验：`http://124.222.49.67:3000/APP_MODULE_INTERFACE_GUIDE.md`

## 1. App 模块化核验入口
2026-05-02 起，核心卖点接口文档按开盘啦 App 页面重排：先定位 App 模块，再看接口、字段、实时/历史口径和截图核验结果。

网页端的 API 全景清单继续保留原表格样式，方便按接口路径快速检索；App 模块化核验手册用于业务场景和截图对账。

优先阅读：
```text
http://124.222.49.67:3000/APP_MODULE_INTERFACE_GUIDE.md
```

配套核验基准：
```text
/docs/APP_SCREENSHOT_BASELINE_2026-05-02.md
```

当前已按 2026-04-30 App 历史快照核验的模块：
| App 模块 | 推荐接口 | 核验状态 |
| --- | --- | --- |
| 早盘竞价——涨停委买额 | `/api/auction/limit-bid?date=20260430` | 涨停委买额、竞价涨幅已对齐；20 分后涨停委买待补 |
| 早盘竞价——竞价净额/主力净额 >1000W | `/api/auction/main-net?date=20260430` | 读取 `auctionNetAmount`；2026-04-30 截图可见 Top 行已校准，完整 62 条仍按 partial 标注 |
| 市场情绪——综合强度/涨跌分布 | `/api/sentiment`、`/api/emotion/mood`、`/api/emotion/distribution` | 涨跌家数、综合强度 62、涨跌分布、量能已对齐 |
| 涨停表现——连板梯队/涨停原因 | `/api/ladder`、`/api/consecutive/:level` | 连板数量、涨停时间、原因、封单已对齐 |
| 打板——涨停跌停炸板统计 | `/api/sentiment`、`/api/broken`、`/api/auction/limit-bid` | 涨停板、跌停股、炸板、涨停委买可核验 |
| 尾盘抢筹——抢筹金额排行 | `/api/market/auction/rank?type=1` | 抢筹金额 Top 已对齐 |
| 人气榜——App 人气榜 / 最强风口榜单 | `/api/hot/rank` | `hotStocks` 为截图榜单主体；`fullRank` 为最强风口榜单 |
| 行情板块/板块竞价/实时龙虎榜——核心缺口说明 | 见模块化手册 | 实时龙虎榜当日已切官方 socket 榜单，历史 2026-04-30 盘后 Top10 已对齐；板块竞价 Top3 原生摘要已对齐 |

## 2. AI 调用规则
如果你是 AI Agent，请按以下规则调用：
1. 所有 API 都从 `http://124.222.49.67:3000` 开始拼接。
2. 推荐把 API Key 放在请求头：`x-api-key: YOUR_API_KEY`。
3. 股票代码通常传 6 位裸码，例如 `300857`、`688411`；指数接口可传 `SH000001`、`SZ399001` 等带市场前缀代码。
4. 日期参数支持 `YYYYMMDD` 或 `YYYY-MM-DD`，例如 `date=20260430` 或 `date=2026-04-30`。
5. `date` 表示锁定请求日期，不是强制历史源开关；传今天日期时，部分实时/盘后快照接口仍会走实时源。
6. 不传 `date` 时，接口默认请求今天或最新可用数据；如果今天数据源未产出，部分接口会回退到最近有数据的交易日。
7. 判断是否回退和数据来源时，必须读取响应里的 `requestedDate`、`dataDate`、`isFallback`、`source` 或 `_source`：
   - `requestedDate`：本次请求期望日期。
   - `dataDate`：实际返回数据所属日期。
   - `isFallback=true`：实际返回了其他日期的数据。
   - `isFallback=false`：实际返回的就是请求日期数据。
8. 如果显式传了今天日期，但上游当天数据不存在，部分历史结算类接口会返回 `422`，不会静默伪装成今天数据。
9. 竞价历史数据优先使用 `/api/auction/limit-bid?date=YYYYMMDD` 或别名 `/api/auction/morning-bidding?date=YYYYMMDD`；如核验 App「主力净额 >1000W」，使用 `/api/auction/main-net?date=YYYYMMDD` 并读取 `auctionNetAmount`，默认结果已按 2026-04-30 截图可见行校准。
10. 机构 L2 大单使用 `/api/stock/bigorder/:code`，支持实时和历史双模式；不传 `date` 或传今天日期时走当天实时/盘后快照源，传历史交易日时走历史源。
11. 需要长连接推送时使用 `ws://124.222.49.67:3000/ws/realtime?api_key=YOUR_API_KEY&channels=index,sentiment,auction,tail`；服务端推送的是缓存后的实时快照，避免客户自己高频 HTTP 轮询。

全接口字段字典：
- HTML 搜索版：`http://124.222.49.67:3000/api-field-dictionary.html`
- Markdown 版：`http://124.222.49.67:3000/API_FIELD_DICTIONARY.md`
- JSON 源：`http://124.222.49.67:3000/api-field-dictionary.json`

字段字典覆盖 API 全景清单中的全部公开接口条目，按"指标名称 / 接口路径 / 请求参数 / 返回字段 / 类型 / 单位 / 样例值"组织。客户如果只问字段含义，优先把字段字典链接发给他；如果问 App 模块核验，再结合 `APP_MODULE_INTERFACE_GUIDE.md`。

## 3. 接口条目规范
本文档按"指标接口"方式描述每个数据能力，结构参考专业数据接口文档的常见写法：

| 栏目 | 说明 |
| --- | --- |
| 指标名称 | 客户识别该接口的业务名称，例如"市场情绪——情绪总览""早盘竞价——涨停委买额" |
| 接口路径 | 实际请求路径，例如 `/api/sentiment` |
| 指标说明 | 说明该接口解决什么核查问题、对应 App 哪个模块 |
| 请求参数 | 列明必填、可选、格式、默认值和日期语义 |
| 返回字段 | 列明字段名、类型、单位和业务含义 |
| 返回示例 | 核心示例统一使用 2026-04-30 快照，便于和本轮 App 截图对账 |

网页端的 API 全景清单已为每个接口补充"指标名称"和"说明"两列；核心接口详细区继续给出请求参数、返回字段和 2026-04-30 样例。

## 4. 鉴权方式
所有 API 请求必须携带有效 API Key。

推荐方式：
```http
GET /api/sentiment HTTP/1.1
Host: 124.222.49.67:3000
x-api-key: YOUR_API_KEY
```

兼容常见 AI/HTTP 客户端的 Bearer 写法：
```http
GET /api/sentiment HTTP/1.1
Host: 124.222.49.67:3000
Authorization: Bearer YOUR_API_KEY
```

也支持 URL 参数方式：
```http
GET /api/sentiment?api_key=YOUR_API_KEY HTTP/1.1
Host: 124.222.49.67:3000
```

套餐说明：
| 套餐 | 每日额度 | 常见权限 |
| --- | ---: | --- |
| Free | 50 | 基础行情、情绪、新闻等 |
| Pro | 2000 | 情绪、板块、梯队、分时、题材新闻等 |
| Inst | 5000 / 永久 Inst 为 unlimited | Pro 全部能力，加 L2 大单、龙虎榜穿透、竞价异动等 |

说明：普通 Inst 仍按发卡时长和额度控制；永久 Inst 与 Lifetime 的 `quotaPolicy=unlimited`，接口会继续记录调用量，但不会因为当日计数超过 5000 返回 429。

### 4.1 WebSocket 实时推送
WebSocket 入口：
```text
ws://124.222.49.67:3000/ws/realtime?api_key=YOUR_API_KEY&channels=index,sentiment,auction,tail&interval=5000
```

可订阅频道：
| channel | 对应 HTTP 指标接口 | 说明 |
| --- | --- | --- |
| `index` | `/api/index` | 大盘指数快照 |
| `sentiment` | `/api/sentiment` | 市场情绪总览 |
| `mood` | `/api/emotion/mood` | 综合强度 |
| `distribution` | `/api/emotion/distribution` | 涨跌分布 |
| `limitcount` | `/api/realtime/limitcount` | 涨跌停家数 |
| `auction` | `/api/auction/limit-bid` | 早盘竞价涨停委买额 |
| `auctionMainNet` | `/api/auction/main-net` | 早盘竞价竞价净额/主力净额 |
| `activeSectors` | `/api/auction/active-sectors` | 板块竞价异动 |
| `tail` | `/api/market/tail-rush` | 尾盘抢筹快照 |
| `hot` | `/api/hot/rank` | 人气榜 |
| `l2Rank` | `/api/market/l2-rank` | 全市场 L2 实时/历史榜，Inst 权限 |
| `lhb` | `/api/lhb/realtime` | 实时龙虎榜候选榜，Inst 权限 |

WebSocket 风控说明：单个 API Key 默认最多同时保持 6 条 WebSocket 连接，服务端总连接默认上限 200 条。频道请求会透传 `date`，并按频道透传 `limit`、`time`、`minAmount`、`sortBy` 等白名单参数；不建议用多个连接模拟高频轮询。

返回消息格式：
```json
{
  "type": "snapshot",
  "ts": "2026-05-02T15:00:00.000Z",
  "intervalMs": 5000,
  "channels": {
    "sentiment": {
      "ok": true,
      "path": "/api/sentiment",
      "data": {}
    }
  }
}
```

## 5. 通用请求示例

### curl
```bash
curl "http://124.222.49.67:3000/api/sentiment?date=20260430" \
  -H "x-api-key: YOUR_API_KEY"
```

### Python
```python
import sys
import requests
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://124.222.49.67:3000"
API_KEY = "YOUR_API_KEY"

def call_api(path, params=None):
    url = BASE_URL + path
    headers = {"x-api-key": API_KEY}
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    print("HTTP", resp.status_code, resp.url)
    resp.raise_for_status()
    return resp.json()

data = call_api("/api/sentiment", {"date": "20260430"})
print(data)
if data.get("isFallback"):
    print("注意：返回数据发生日期回退", data.get("requestedDate"), "->", data.get("dataDate"))
```

### JavaScript / Node.js
```js
const BASE_URL = "http://124.222.49.67:3000";
const API_KEY = "YOUR_API_KEY";

async function callApi(path, params = {}) {
  const url = new URL(BASE_URL + path);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) url.searchParams.set(key, value);
  }
  const resp = await fetch(url, { headers: { "x-api-key": API_KEY } });
  const text = await resp.text();
  if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${text}`);
  return JSON.parse(text);
}

const data = await callApi("/api/auction/limit-bid", { date: "20260430", limit: 10 });
console.log(data);
```

## 6. 日期语义与回退机制
所有支持日期语义的接口尽量返回以下字段：
```json
{
  "requestedDate": "20260430",
  "dataDate": "20260430",
  "isFallback": false
}
```

常见场景：
| 请求方式 | 行为 |
| --- | --- |
| 不传 `date` | 默认请求今天或最新可用数据；若今天数据源未产出，可能回退最近有数据的交易日，并返回 `isFallback=true` |
| 传今天日期 | 锁定今天；实时/盘后快照接口通常仍走实时源，历史结算类接口若今天无数据，可能返回 `422` |
| 传历史交易日 | 返回该交易日数据；如果源数据缺失，按接口策略返回错误或回退标记 |

重点说明：
- `/api/intraday/stock/:code`：支持 `date`，个股分时可查历史。
- `/api/stock/bigorder/:code`：支持 `date`，不传或传今天走实时/盘后快照源，传历史交易日走历史源。
- `/api/auction/limit-bid`：支持历史竞价榜；传 `date` 强制走 VIP 历史早盘竞价榜，不传则竞价时段实时、盘后自动补最近数据日完整历史榜。
- `/api/sector/strength/:code`：单板块强度接口，支持按日期请求；是否能返回取决于上游该板块该日是否有数据。
- `/api/sectors` 与 `/api/sector/ranking`：题材涨停数量排行接口，`count` 表示对应题材/板块的涨停数量；传历史交易日时返回 `history-derived` 派生口径，不应只返回 3 条。

完整日期机制和竞价/L2说明也可访问：
```text
http://124.222.49.67:3000/API_DATE_SEMANTICS_2026-04-30.md
http://124.222.49.67:3000/API_REALTIME_HISTORY_L2_AUCTION_GUIDE.md
```

## 7. 关键接口示例

### 7.1 题材涨停数量排行
```http
GET /api/sectors?date=20260430
GET /api/sector/ranking?date=20260430
```
用途：获取 App"涨停原因/题材涨停数量"口径的题材排行。历史日期由 `HisHomeDingPan.DailyLimitPerformance` 派生，响应 `_source=history-derived`、`basis=HisHomeDingPan.DailyLimitPerformance`；该接口不是 App 行情页"强度/主力净额/机构增仓"完整列表。

请求示例：
```bash
curl "http://124.222.49.67:3000/api/sectors?date=20260430" \
  -H "x-api-key: YOUR_API_KEY"
```

典型返回结构：
```json
{
  "requestedDate": "20260430",
  "dataDate": "20260430",
  "isFallback": false,
  "date": "2026-04-30",
  "sectors": [
    {
      "code": "801571",
      "name": "一季报增长",
      "count": 25
    },
    {
      "code": "801001",
      "name": "芯片",
      "count": 13
    },
    {
      "code": "801159",
      "name": "机器人概念",
      "count": 7
    }
  ],
  "_source": "history-derived",
  "basis": "HisHomeDingPan.DailyLimitPerformance"
}
```
说明：`sectors` 是完整榜单数组；文档或客服回复里只展示前几条时，通常只是为了节省篇幅。实时/今日查询仍可能走实时上游；历史交易日查询会锁定请求日期，需以 `requestedDate/dataDate/isFallback/_source` 判断实际口径。

### 7.2 单板块强度
```http
GET /api/sector/strength/:code?date=20260430
```
示例：
```bash
curl "http://124.222.49.67:3000/api/sector/strength/801571?date=20260430" \
  -H "x-api-key: YOUR_API_KEY"
```
用途：查询单个板块的强度打分与明细。该接口属于 Pro 及以上权限。

### 7.3 单板块盘口资金
```http
GET /api/sector/capital/:code?date=20260430
```
示例：
```bash
curl "http://124.222.49.67:3000/api/sector/capital/801571?date=20260430" \
  -H "x-api-key: YOUR_API_KEY"
```
用途：查询单个板块的盘口资金、主力买卖、涨跌家数、市值等数据。`code` 必须使用 6 位板块代码，例如 `801571`、`801807`；不要传同花顺 `BKxxxx` 格式。

典型返回结构：
```json
{
  "requestedDate": "20260430",
  "dataDate": "20260430",
  "isFallback": false,
  "code": "801571",
  "pankou": [
    1788085381627,
    2.64202,
    141.045,
    85812683820,
    -77480578662,
    8332105158,
    1200,
    1008,
    46,
    67678829949856,
    83573649077376
  ],
  "capital": {
    "turnoverAmount": 1788085381627,
    "changePct": 2.64202,
    "activityMetric": 141.045,
    "mainBuyAmount": 85812683820,
    "mainSellAmount": -77480578662,
    "mainNetAmount": 8332105158,
    "upCount": 1200,
    "downCount": 1008,
    "flatCount": 46,
    "circulatingMarketValue": 67678829949856,
    "totalMarketValue": 83573649077376
  },
  "_source": "history"
}
```

字段说明：
| 原始字段 | 结构化字段 | 含义 |
| --- | --- | --- |
| `pankou[0]` | `capital.turnoverAmount` | 成交额，单位元 |
| `pankou[1]` | `capital.changePct` | 板块涨跌幅，单位 `%` |
| `pankou[2]` | `capital.activityMetric` | 上游盘口活跃/比率类指标；不是 App 列表页的"当前强度" |
| `pankou[3]` | `capital.mainBuyAmount` | 主力买入金额，单位元 |
| `pankou[4]` | `capital.mainSellAmount` | 主力卖出金额，单位元，通常为负数 |
| `pankou[5]` | `capital.mainNetAmount` | 主力净额/净流入，等于 `pankou[3] + pankou[4]` |
| `pankou[6]` | `capital.upCount` | 板块内上涨家数 |
| `pankou[7]` | `capital.downCount` | 板块内下跌家数 |
| `pankou[8]` | `capital.flatCount` | 板块内平盘家数 |
| `pankou[9]` | `capital.circulatingMarketValue` | 流通市值，单位元 |
| `pankou[10]` | `capital.totalMarketValue` | 总市值，单位元 |

注意：App 截图里的板块列表列名"当前强度 / 区间净额 / 区间成交"属于板块排行/区间统计口径，不能直接用 `/api/sector/capital/:code` 的 `pankou` 数组替代。该接口是单板块盘口资金接口，适合看主力买卖与资金净额。

### 7.4 竞价涨停委买额排行
```http
GET /api/auction/limit-bid?limit=20
GET /api/auction/limit-bid?date=20260430&limit=10
GET /api/auction/morning-bidding?date=20260430&limit=10
```
用途：查询早盘集合竞价涨停委买额排行。别名 `/api/auction/morning-bidding` 与 `/api/auction/limit-bid` 返回同一类数据。

机制：
- 只要传 `date`，就强制走 VIP 历史早盘竞价榜；指定非交易日或上游未生成数据时返回 `422`。
- 不传 `date` 时，竞价时段走实时模块；收盘后如果实时模块只剩少量快照，会自动按返回的 `dataDate` 补拉完整历史榜，`source=history-from-snapshot`。
- 实时模块已统一补齐历史同名字段：`auctionChangePct` 等同旧字段 `changePct`；实时源未返回的 `auctionNetAmount`、`auctionAmount`、`auctionTurnoverRate`、`bidAmountAfter20` 会稳定返回 `null`，并通过 `fieldCoverage` / `realtimeMissingFields` 说明。
- 历史"涨停委买"榜已按 App 早盘竞价页口径对齐：`PidType=8`、`Type=18`、`Is_st=0`，默认包含 ST；如需排除 ST，可传 `excludeST=1`。
- `/api/auction/active-sectors` 默认优先返回 `JJYDBK` 原生板块竞价摘要；仅在 `source=derived` 或无原生摘要时使用股票榜聚合视角。

请求参数：
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `date` | String | 否 | 最近可用数据日 | 交易日，支持 `YYYYMMDD` 或 `YYYY-MM-DD`；传入后锁定历史早盘竞价榜 |
| `limit` | Number | 否 | 50 | 返回条数，最大 100 |
| `excludeST` | Boolean | 否 | false | 是否排除 ST 股票 |

返回示例：
```json
{
  "requestedDate": "20260430",
  "dataDate": "20260430",
  "isFallback": false,
  "date": "2026-04-30",
  "list": [
    {
      "code": "300857",
      "name": "协创数据",
      "limitBidAmount": 1234567890,
      "auctionChangePct": 19.99,
      "previousClose": 45.50
    }
  ],
  "_source": "history"
}
```

### 7.5 市场情绪总览
```http
GET /api/sentiment?date=20260430
```
用途：获取市场整体情绪数据，包括涨跌家数、涨跌停数量、综合强度等。

返回示例：
```json
{
  "requestedDate": "20260430",
  "dataDate": "20260430",
  "isFallback": false,
  "date": "2026-04-30",
  "upCount": 2500,
  "downCount": 1500,
  "limitUpCount": 80,
  "limitDownCount": 5,
  "mood": 62,
  "brokenCount": 12
}
```

### 7.6 连板梯队
```http
GET /api/ladder?date=20260430
```
用途：获取涨停股票的连板梯队排行。

### 7.7 个股L2大单
```http
GET /api/stock/bigorder/:code?date=20260430
```
示例：
```bash
curl "http://124.222.49.67:3000/api/stock/bigorder/300857?date=20260430" \
  -H "x-api-key: YOUR_API_KEY"
```
用途：查询个股L2大单数据，包括大单买入/卖出金额、大单净额等。

### 7.8 实时龙虎榜
```http
GET /api/lhb/detail/:code?date=20260430
```
用途：查询个股龙虎榜席位明细，包括营业部买卖金额、机构专用席位等。

## 8. 完整接口清单

访问以下链接获取完整接口清单：
- HTML版本：`http://124.222.49.67:3000/docs.html`
- Markdown版本：`http://124.222.49.67:3000/kaipanla_api_handbook.md`

## 9. 附录

### 9.1 错误码说明
| HTTP状态码 | 说明 |
| --- | --- |
| 200 | 请求成功 |
| 401 | API Key无效或已过期 |
| 403 | 权限不足，当前套餐不支持该接口 |
| 422 | 请求参数错误，或指定日期无数据 |
| 429 | 请求频率超限或当日额度已用完 |
| 500 | 服务器内部错误 |

### 9.2 数据更新时间
- 实时数据：交易时间内每秒更新
- 盘后数据：当日收盘后30分钟内更新
- 历史数据：T+1日更新完整历史数据

### 9.3 支持的市场
- 上交所 (SH)
- 深交所 (SZ)
- 北交所 (BJ)
- 可转债 ( convertible bonds )

---
**文档版本**: 2026-05-06
**API版本**: v1.0
**更新者**: Chief Architect (A5L)
