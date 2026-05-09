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

**核心价值**: 8年历史数据积淀，支持2017年以来的A股全市场数据回测！

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

### 🏛️ 历史数据宝藏（2017-至今）

**Chief特别指示**: 开盘啦拥有过去8年所有A股的分时逐笔委托数据！这是CIO模拟交易的核武器！

| 数据类型 | 接口 | 历史范围 | 用途 |
|---------|------|---------|------|
| **个股历史K线** | `/api/stock/kline/:code` | 2017-至今 | 长期趋势分析、回测 |
| **指数历史K线** | `/api/index/kline/:code` | 2017-至今 | 大盘环境判断 |
| **指数分时明细** | `/api/intraday/index/:code` | 历史交易日 | 日内波动规律 |
| **分时成交量** | `/api/intraday/volume/:code` | 历史交易日 | 量能分析、资金流向 |
| **概念历史热度** | `/api/conception/history` | 历史序列 | 题材轮动规律 |
| **历史竞价数据** | `/api/auction/limit-bid` | 历史交易日 | 早盘强势标的研究 |
| **历史龙虎榜** | `/api/lhb/detail/:code` | 历史交易日 | 游资行为模式分析 |

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

### 历史数据调用示例
```python
# 获取2020年以来上证指数K线（8年历史）
kline = call_api("/api/index/kline/SH000001", {
    "begin": "20200101",
    "end": "20260509",
    "type": "day"
})

# 获取某历史交易日的指数分时明细
intraday = call_api("/api/intraday/index/SH000001", {
    "date": "20240430"
})

# 获取概念历史热度序列
concept_history = call_api("/api/conception/history")
```

## Integration with A5L

### 🔥 与CIO模拟交易系统深度集成（重点！）

**Chief指示**: 利用8年历史数据，让CIO模拟交易如虎添翼！

#### 1. 策略回测验证
```python
class CIOBacktestEngine:
    """CIO策略回测引擎 - 基于开盘啦8年历史数据"""
    
    def __init__(self):
        self.kaipanla = KaipanlaAPI()
        
    def backtest_strategy(self, strategy, start_date, end_date):
        """
        回测策略在历史数据上的表现
        
        Args:
            strategy: 策略函数 (买入/卖出信号生成器)
            start_date: 回测开始日期 (如 "20230101")
            end_date: 回测结束日期 (如 "20241231")
        """
        results = []
        
        # 获取历史交易日列表
        trading_days = self.get_trading_days(start_date, end_date)
        
        for date in trading_days:
            # 获取当日市场情绪
            sentiment = self.kaipanla.get_sentiment(date=date)
            
            # 获取当日连板梯队
            ladder = self.kaipanla.get_ladder(date=date)
            
            # 获取当日板块强度
            sectors = self.kaipanla.get_sectors(date=date)
            
            # 执行策略生成信号
            signals = strategy(sentiment, ladder, sectors, date)
            
            # 记录结果
            results.append({
                'date': date,
                'signals': signals,
                'sentiment': sentiment['mood'],
                'limit_up_count': sentiment['limitUpCount']
            })
            
        return self.calculate_performance(results)
    
    def calculate_performance(self, results):
        """计算回测绩效指标"""
        # 胜率、盈亏比、最大回撤、夏普比率等
        pass
```

#### 2. 早盘竞价策略验证
```python
def verify_auction_strategy():
    """
    验证早盘竞价策略在历史数据上的表现
    
    策略逻辑: 竞价涨停委买额前10 + 竞价净额>5000W
    """
    kaipanla = KaipanlaAPI()
    
    # 获取过去1年的竞价数据
    for date in get_past_trading_days(252):  # 约1年
        auction_data = kaipanla.get_auction_limit_bid(date=date, limit=20)
        
        # 筛选强势标的
        strong_stocks = [
            stock for stock in auction_data['list']
            if stock['limitBidAmount'] > 1000000000  # 10亿+
            and stock['auctionNetAmount'] > 50000000  # 5000万+
        ]
        
        # 记录当日表现（与次日涨幅对比）
        for stock in strong_stocks:
            next_day_return = get_next_day_return(stock['code'], date)
            record_performance(stock, next_day_return)
```

#### 3. 情绪周期量化
```python
class SentimentCycleAnalyzer:
    """市场情绪周期量化分析器"""
    
    def __init__(self):
        self.kaipanla = KaipanlaAPI()
        
    def analyze_8year_sentiment(self):
        """
        分析8年市场情绪周期规律
        
        输出:
        - 情绪冰点/高潮识别模型
        - 情绪转折点预测
        - 不同情绪阶段的胜率分布
        """
        # 获取2017-2025完整情绪数据
        sentiment_data = []
        for year in range(2017, 2026):
            year_data = self.kaipanla.get_sentiment_history(year=year)
            sentiment_data.extend(year_data)
            
        # 分析情绪周期
        cycles = self.identify_sentiment_cycles(sentiment_data)
        
        return {
            'ice_point_threshold': 30,      # 情绪冰点阈值
            'euphoria_threshold': 85,       # 情绪高潮阈值
            'cycle_duration_avg': 22,       # 平均周期长度(交易日)
            'win_rate_by_mood': {...}       # 不同情绪区间胜率
        }
```

#### 4. 板块轮动规律挖掘
```python
def analyze_sector_rotation():
    """
    基于8年历史数据挖掘板块轮动规律
    
    应用场景:
    - 识别当前市场处于轮动周期的哪个阶段
    - 预测下一个可能轮动的板块
    - 验证产业链传导逻辑
    """
    kaipanla = KaipanlaAPI()
    
    # 获取概念历史热度序列
    concept_history = kaipanla.get_conception_history()
    
    # 分析板块轮动模式
    rotation_patterns = {
        'AI算力 -> CPO -> 光模块 -> 服务器': [...],
        '政策催化 -> 游资炒作 -> 机构接力': [...],
        '上游材料 -> 中游制造 -> 下游应用': [...]
    }
    
    return rotation_patterns
```

#### 5. 实时模拟交易信号生成
```python
class CIOSignalGenerator:
    """CIO实时交易信号生成器"""
    
    def __init__(self):
        self.kaipanla = KaipanlaAPI()
        
    def generate_pre_market_signals(self):
        """盘前信号生成 (09:15-09:25)"""
        # 1. 获取竞价数据
        auction = self.kaipanla.get_auction_limit_bid(limit=20)
        
        # 2. 获取市场情绪
        sentiment = self.kaipanla.get_sentiment()
        
        # 3. 获取连板梯队
        ladder = self.kaipanla.get_ladder()
        
        # 4. 生成交易信号
        signals = []
        
        # 信号1: 竞价涨停委买额前5 + 情绪>60
        if sentiment['mood'] > 60:
            for stock in auction['list'][:5]:
                signals.append({
                    'code': stock['code'],
                    'signal': 'BUY_AUCTION',
                    'confidence': 0.85,
                    'reason': f"竞价强势+情绪良好: {stock['limitBidAmount']/1e8:.1f}亿"
                })
                
        return signals
    
    def generate_intraday_signals(self):
        """盘中信号生成 (09:30-15:00)"""
        # 实时监控L2大单
        # 监控板块资金流向
        # 监控市场情绪变化
        pass
```

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

### 历史K线数据 (/api/stock/kline/:code)
```json
{
  "code": "000001.SZ",
  "klines": [
    {
      "date": "20260509",
      "open": 11.20,
      "high": 11.45,
      "low": 11.15,
      "close": 11.38,
      "volume": 152345600,
      "amount": 1723456789,
      "changePct": 1.61
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
- **v1.0.0** (2026-05-09): 初始版本，集成开盘啦Inst套餐API，8年历史数据支持

## 🔥 与开盘啦API的联合使用（推荐！）

**Chief战略指示**: 大鸡腿（技术分析）+ 开盘啦（数据获取）= 黄金组合！

### 完美互补架构

```
┌─────────────────────────────────────────────────────────────┐
│                    A5L CIO模拟交易引擎                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │   开盘啦API       │ ───> │   大鸡腿分析      │           │
│  │   (数据层L1)      │      │   (策略层L2)      │           │
│  └──────────────────┘      └──────────────────┘           │
│         │                           │                      │
│         ▼                           ▼                      │
│  • 8年历史K线数据          • 压力支撑计算                  │
│  • 实时行情数据            • 形态识别                      │
│  • 市场情绪数据            • 通道分析                      │
│  • 板块强度数据            • 突破评分                      │
│                                                             │
│                    ↓ 联合输出 ↓                            │
│                                                             │
│  "600519在压力位¥1520遇阻，开盘啦显示白酒板块                 │
│   资金净流出-5.2亿，建议观望"                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 联合使用场景

#### 场景1: 强势股技术分析
```python
# 步骤1: 从开盘啦获取强势股列表
kaipanla = KaipanlaAPI()
ladder = kaipanla.get_ladder(limit=20)  # 连板梯队

# 步骤2: 用大鸡腿做技术分析
from dajitui import DaJiTuiAnalyzer
djt = DaJiTuiAnalyzer()

for stock in ladder['stocks']:
    # 获取历史K线数据
    kline = kaipanla.get_stock_kline(stock['code'], days=120)
    
    # 大鸡腿技术分析
    analysis = djt.analyze(kline_data=kline)
    
    # 综合判断
    if analysis['breakout_up'] > 0.7:
        print(f"{stock['name']} 强势突破，可追涨")
    elif analysis['position_in_channel'] > 0.8:
        print(f"{stock['name']} 接近通道上轨，注意回调风险")
```

#### 场景2: 板块龙头筛选
```python
# 步骤1: 获取热门板块
sectors = kaipanla.get_sectors()
hot_sector = sectors[0]  # 最强板块

# 步骤2: 获取板块成分股
sector_stocks = kaipanla.get_sector_stocks(hot_sector['code'])

# 步骤3: 大鸡腿技术筛选
candidates = []
for stock in sector_stocks:
    kline = kaipanla.get_stock_kline(stock['code'], days=60)
    analysis = djt.analyze(kline_data=kline)
    
    # 筛选条件: 上升通道 + 突破倾向>0.6
    if (analysis['channel']['type'] == 'ascending' and 
        analysis['breakout_up'] > 0.6):
        candidates.append({
            'code': stock['code'],
            'pattern': analysis['pattern']['type'],
            'breakout_score': analysis['breakout_up']
        })

# 按突破评分排序
candidates.sort(key=lambda x: x['breakout_score'], reverse=True)
```

#### 场景3: 历史策略回测
```python
# 结合开盘啦8年数据 + 大鸡腿技术分析
class CombinedBacktest:
    def __init__(self):
        self.kaipanla = KaipanlaAPI()
        self.djt = DaJiTuiAnalyzer()
    
    def backtest_pattern_strategy(self, start_date, end_date):
        """
        回测形态策略: 识别上升三角形后的表现
        """
        results = []
        
        # 遍历所有交易日
        for date in get_trading_days(start_date, end_date):
            # 获取当日所有股票
            all_stocks = self.kaipanla.get_all_stocks(date=date)
            
            for stock in all_stocks:
                # 获取前120日K线
                kline = self.kaipanla.get_stock_kline(
                    stock['code'], 
                    end_date=date,
                    days=120
                )
                
                # 大鸡腿形态识别
                analysis = self.djt.analyze(kline_data=kline)
                
                # 识别上升三角形
                if analysis['pattern']['type'] == 'ascending_triangle':
                    # 记录后续5日收益
                    future_return = self.get_future_return(
                        stock['code'], 
                        date, 
                        days=5
                    )
                    
                    results.append({
                        'date': date,
                        'code': stock['code'],
                        'pattern': 'ascending_triangle',
                        'breakout_score': analysis['breakout_up'],
                        'future_return_5d': future_return
                    })
        
        # 统计分析
        avg_return = sum(r['future_return_5d'] for r in results) / len(results)
        win_rate = len([r for r in results if r['future_return_5d'] > 0]) / len(results)
        
        return {
            'total_signals': len(results),
            'avg_return_5d': avg_return,
            'win_rate': win_rate
        }
```

### 数据流向图

```
开盘啦API                    大鸡腿分析                  CIO决策
    │                            │                          │
    ├─> 个股K线数据 ────────────>├─> 压力支撑计算 ────┐     │
    │                            │                     │     │
    ├─> 市场情绪数据 ───────────>├─> 形态识别 ────────┼────>│
    │                            │                     │     │
    ├─> 板块资金流向 ───────────>├─> 通道分析 ────────┘     │
    │                            │                          │
    └─> 连板梯队数据 ───────────>└─> 突破评分               │
                                                              │
                         联合输出:                            │
         "形态 + 资金 + 情绪 = 高置信度交易信号"                │
                                                              ▼
                                                    ┌─────────────────┐
                                                    │   买入/卖出决策  │
                                                    └─────────────────┘
```

### 最佳实践建议

| 使用场景 | 开盘啦数据 | 大鸡腿分析 | 输出 |
|---------|-----------|-----------|------|
| **超短线** | 竞价数据 + L2大单 | 60分钟形态 | 早盘强势突破标 |
| **短线** | 日线 + 板块强度 | 日线形态 + 通道 | 板块龙头候选 |
| **中线** | 周线 + 资金流向 | 周线趋势 + 支撑 | 波段操作点位 |
| **策略回测** | 8年历史K线 | 形态识别统计 | 策略胜率验证 |

## Owner
- **Role**: Chief Architect
- **System**: A5L (ARCHITECT-5L)
- **Priority**: P0 (CIO模拟交易核心数据源)
