# SKILL.md - Kaipanla Quant API Skill

## Metadata
- **Name**: kaipanla-api
- **Version**: v1.0.0
- **Layer**: Layer 1 (Data Foundation)
- **Category**: Data Acquisition
- **Status**: Active
- **Created**: 2026-05-09

## Description
开盘啦（Kaipanla）Quant API 数据获取技能。提供A股市场量化数据接口封装，包括市场情绪、板块强度、竞价数据、L2大单、龙虎榜等专业量化数据。

## Capabilities

### 核心数据类型
| 数据类型 | 接口路径 | 用途 |
|---------|---------|------|
| 市场情绪 | `/api/sentiment` | 涨跌家数、综合强度、涨跌停统计 |
| 连板梯队 | `/api/ladder` | 涨停股票连板梯队排行 |
| 板块排行 | `/api/sectors` | 题材涨停数量排行 |
| 板块资金 | `/api/sector/capital/:code` | 单板块盘口资金、主力买卖 |
| 早盘竞价 | `/api/auction/limit-bid` | 涨停委买额排行 |
| 竞价净额 | `/api/auction/main-net` | 主力净额 >1000W排行 |
| L2大单 | `/api/stock/bigorder/:code` | 个股大单资金流向 |
| 龙虎榜 | `/api/lhb/detail/:code` | 席位明细、机构买卖 |
| 人气榜 | `/api/hot/rank` | App人气榜单 |

### 实时数据
- WebSocket实时推送: `ws://124.222.49.67:3000/ws/realtime`
- 支持频道: index, sentiment, auction, l2Rank, lhb, hot, tail

## Configuration

### API凭证
```json
{
  "api_key": "sk_inst_646653fc7a80b2f8",
  "base_url": "http://124.222.49.67:3000",
  "tier": "Inst",
  "quota": "unlimited"
}
```

### 鉴权方式
- 请求头: `x-api-key: YOUR_API_KEY`
- 或: `Authorization: Bearer YOUR_API_KEY`

## Usage

### Python调用示例
```python
import requests

BASE_URL = "http://124.222.49.67:3000"
API_KEY = "sk_inst_646653fc7a80b2f8"

def call_api(path, params=None):
    url = BASE_URL + path
    headers = {"x-api-key": API_KEY}
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()

# 获取市场情绪
data = call_api("/api/sentiment")

# 获取历史竞价数据
auction_data = call_api("/api/auction/limit-bid", {"date": "20260509", "limit": 20})

# 获取板块资金
sector_data = call_api("/api/sector/capital/801571", {"date": "20260509"})
```

### 日期参数规则
- 支持格式: `YYYYMMDD` 或 `YYYY-MM-DD`
- 不传`date`: 默认请求今天或最新可用数据
- 响应字段检查: `requestedDate`, `dataDate`, `isFallback`
- `isFallback=true`: 表示返回了其他日期的数据

## Integration with A5L

### 与阳关大道集成
```python
# 获取早盘竞价数据用于超短策略
auction_data = call_api("/api/auction/limit-bid", {"limit": 10})
# 分析涨停委买额排行，识别强势标的
```

### 与产业链分析集成
```python
# 获取板块强度
sectors = call_api("/api/sectors")
# 获取热门板块资金流向
for sector in sectors['sectors'][:5]:
    capital = call_api(f"/api/sector/capital/{sector['code']}")
    # 分析主力资金流向
```

### 与CTF催化剂监控集成
```python
# 实时监控市场情绪
sentiment = call_api("/api/sentiment")
# 监控涨停家数变化，识别情绪转折点
```

## Data Schema

### 市场情绪 (/api/sentiment)
```json
{
  "requestedDate": "20260509",
  "dataDate": "20260509",
  "isFallback": false,
  "upCount": 2500,           // 上涨家数
  "downCount": 1500,         // 下跌家数
  "limitUpCount": 80,        // 涨停家数
  "limitDownCount": 5,       // 跌停家数
  "mood": 62,                // 综合强度(0-100)
  "brokenCount": 12          // 炸板数量
}
```

### 板块资金 (/api/sector/capital/:code)
```json
{
  "code": "801571",
  "capital": {
    "turnoverAmount": 1788085381627,   // 成交额(元)
    "changePct": 2.64,                  // 涨跌幅(%)
    "mainBuyAmount": 85812683820,       // 主力买入(元)
    "mainSellAmount": -77480578662,     // 主力卖出(元)
    "mainNetAmount": 8332105158,        // 主力净额(元)
    "upCount": 1200,                    // 上涨家数
    "downCount": 1008                   // 下跌家数
  }
}
```

### 竞价数据 (/api/auction/limit-bid)
```json
{
  "list": [
    {
      "code": "300857",
      "name": "协创数据",
      "limitBidAmount": 1234567890,  // 涨停委买额
      "auctionChangePct": 19.99,      // 竞价涨幅
      "auctionNetAmount": 50000000    // 竞价净额
    }
  ]
}
```

## Rate Limits
- Inst套餐: Unlimited调用
- WebSocket: 最多6条并发连接

## Error Handling
| 状态码 | 含义 | 处理建议 |
|-------|------|---------|
| 401 | API Key无效 | 检查密钥配置 |
| 403 | 权限不足 | 升级套餐 |
| 422 | 参数错误或日期无数据 | 检查日期是否为交易日 |
| 429 | 频率限制 | 降低请求频率 |

## References
- [完整API手册](references/kaipanla_api_handbook.md)
- [字段字典](http://124.222.49.67:3000/api-field-dictionary.html)
- [App模块核验](http://124.222.49.67:3000/APP_MODULE_INTERFACE_GUIDE.md)

## Changelog
- **v1.0.0** (2026-05-09): 初始版本，集成开盘啦Inst套餐API

## Owner
- **Role**: Chief Architect
- **System**: A5L (ARCHITECT-5L)
