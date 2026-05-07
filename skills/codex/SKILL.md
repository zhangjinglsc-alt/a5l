# Codex - 代码生成与策略编程助手

> **版本**: v1.0.0  
> **代号**: Codex  
> **定位**: A5L Layer 2 策略引擎 - 代码级策略实现  
> **创建时间**: 2026-05-08

**描述**: Codex是A5L系统的代码生成与策略编程助手，将投资逻辑自动转化为可执行代码。核心能力：(1) 自然语言策略描述→Python代码；(2) CTF框架规则→自动化交易脚本；(3) 数据分析需求→可视化代码；(4) 策略回测→完整回测框架代码。让Chief用自然语言描述策略，Codex生成可直接运行的代码。

---

## 🎯 核心问题

### 原有问题

| 问题 | 现象 | 解决方案 |
|:-----|:-----|:---------|
| **策略到代码鸿沟** | 有投资逻辑但不会写代码 | **自然语言→代码**: 描述即代码 |
| **重复造轮子** | 每次策略都要重写基础框架 | **模板化生成**: 标准模板+自定义逻辑 |
| **代码质量不一** | 不同人写的代码风格各异 | **标准化输出**: 统一代码规范 |
| **回测繁琐** | 策略验证要写大量代码 | **一键生成**: 策略+回测完整框架 |

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│  输入层 (Input)                                             │
│  ├── 自然语言策略描述                                       │
│  ├── CTF框架规则 (Tier/仓位/操作)                           │
│  ├── 数据分析需求                                           │
│  └── 现有代码优化请求                                       │
├─────────────────────────────────────────────────────────────┤
│  Codex 代码引擎                                             │
│  ├── 意图理解 (NLU)                                         │
│  │   └── 提取: 标的/条件/操作/时间                          │
│  ├── 模板选择 (Template Selection)                          │
│  │   ├── 策略模板 (策略类)                                  │
│  │   ├── 回测模板 (回测框架)                                │
│  │   ├── 数据模板 (数据分析)                                │
│  │   └── 监控模板 (自动化监控)                              │
│  ├── 代码生成 (Code Generation)                             │
│  │   └── 模板 + 参数 → 完整代码                             │
│  └── 验证优化 (Validation)                                  │
│      └── 语法检查/风格统一/注释生成                         │
├─────────────────────────────────────────────────────────────┤
│  输出层 (Output)                                            │
│  ├── 策略代码 (Strategy)                                    │
│  ├── 回测框架 (Backtest)                                    │
│  ├── 数据脚本 (Data)                                        │
│  ├── 监控脚本 (Monitor)                                     │
│  └── 测试用例 (Tests)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 代码模板库

### 模板1: CTF策略执行器

**输入**: "中国长城，Tier 1，20-25%仓位，4连板后减仓"

**输出**:
```python
# strategy_ctf_cgw_000066.py
# 生成时间: 2026-05-08
# 策略来源: CTF框架 + Chief指令

from a5l.trading import Strategy, Position
from a5l.risk import CTFPositionSizer

class ChinaGreatWallStrategy(Strategy):
    """
    中国长城 (000066) Tier 1策略执行器
    
    CTF分级:
    - Tier: 1 (范式级)
    - 仓位上限: 20-25%
    - 当前仓位: 99.5% (严重超限)
    - 触发条件: 4连板后减仓
    """
    
    def __init__(self):
        super().__init__()
        self.symbol = "000066.SZ"
        self.name = "中国长城"
        self.ctf_tier = 1
        self.position_limit = 0.25  # 25%上限
        self.current_position = 0.995  # 当前99.5%
        
    def on_market_open(self):
        """开盘前检查"""
        if self.is_limit_up(days=4):
            self.plan_reduction(
                from_pct=self.current_position,
                to_pct=self.position_limit,
                method="gradual"
            )
    
    def on_limit_up_broken(self):
        """开板时执行"""
        self.reduce_position(
            target_pct=self.position_limit,
            urgency="immediate"
        )
```

### 模板2: 回测框架生成

**输入**: "回测：中国长城，Tier 1，4连板后减仓策略"

**输出**:
```python
# backtest_cgw_tier1.py

from a5l.backtest import BacktestEngine
from a5l.data import StockData
from strategies.strategy_ctf_cgw_000066 import ChinaGreatWallStrategy

class CGWTier1Backtest:
    """
    中国长城 Tier 1策略回测
    
    回测区间: 2026-01-01 至 2026-05-08
    初始资金: ¥1,000,000
    策略: 4连板后减仓至25%
    """
    
    def __init__(self):
        self.engine = BacktestEngine(
            initial_capital=1_000_000,
            start_date="2026-01-01",
            end_date="2026-05-08",
            commission=0.0003
        )
        self.strategy = ChinaGreatWallStrategy()
        self.data = StockData.load("000066.SZ")
    
    def run(self):
        """执行回测"""
        results = self.engine.run(
            strategy=self.strategy,
            data=self.data
        )
        
        print(f"总收益率: {results.total_return:.2%}")
        print(f"最大回撤: {results.max_drawdown:.2%}")
        print(f"夏普比率: {results.sharpe_ratio:.2f}")
        
        return results

if __name__ == "__main__":
    backtest = CGWTier1Backtest()
    results = backtest.run()
```

### 模板3: 数据监控脚本

**输入**: "监控：中国长城，如果开板就通知"

**输出**:
```python
# monitor_cgw_limit_up.py

import time
from a5l.market import MarketData
from a5l.notify import Hermes

class LimitUpMonitor:
    """
    中国长城开板监控
    
    监控逻辑:
    - 实时监控000066.SZ价格
    - 4连板状态下，如打开涨停立即通知
    """
    
    def __init__(self):
        self.symbol = "000066.SZ"
        self.name = "中国长城"
        self.consecutive_limits = 4
        self.hermes = Hermes()
        
    def check_limit_up_status(self):
        """检查涨停状态"""
        data = MarketData.get_realtime(self.symbol)
        
        # 判断是否打开涨停
        if data["limit_up_broken"]:
            self.hermes.send(
                content=f"🚨 {self.name}({self.symbol}) 打开涨停！",
                priority="P0",
                source="codex_monitor"
            )
            return True
        
        return False
    
    def run(self, interval=5):
        """持续监控"""
        print(f"开始监控 {self.name}，每{interval}秒检查一次...")
        
        while True:
            if self.check_limit_up_status():
                break
            time.sleep(interval)

if __name__ == "__main__":
    monitor = LimitUpMonitor()
    monitor.run()
```

---

## 🚀 使用方式

### Python API

```python
from codex import Codex

codex = Codex()

# 生成策略代码
strategy_code = codex.generate_strategy(
    description="中国长城，Tier 1，4连板后减仓至25%",
    template="ctf_executor",
    output_file="strategy_cgw.py"
)

# 生成回测框架
backtest_code = codex.generate_backtest(
    strategy_file="strategy_cgw.py",
    period="2026-01-01 to 2026-05-08",
    initial_capital=1_000_000
)

# 生成监控脚本
monitor_code = codex.generate_monitor(
    symbol="000066.SZ",
    condition="limit_up_broken",
    notification="P0_immediate"
)

# 自然语言→代码
code = codex.natural_to_code(
    "每天收盘后，检查持仓盈亏，如果亏损超过5%就发送警报"
)
```

### 命令行

```bash
# 生成策略
python3 -m codex strategy "中国长城Tier1策略" --output strategy_cgw.py

# 生成回测
python3 -m codex backtest strategy_cgw.py --period 2026-01-01:2026-05-08

# 生成监控
python3 -m codex monitor 000066.SZ --condition "open_limit_up" --notify P0

# 自然语言转代码
python3 -m codex code "每天9:15检查涨跌停股票数量"
```

---

## 🔄 与现有系统集成

### 与CTF框架集成

```python
# Chief描述CTF策略
ctf_rule = {
    "tier": 1,
    "symbol": "000066.SZ",
    "position_limit": 0.25,
    "action": "reduce_on_limit_up_broken"
}

# Codex生成执行代码
strategy_code = codex.from_ctf(ctf_rule)
```

### 与Hermes集成

```python
# 生成带通知的代码
monitor = codex.generate_monitor(
    symbol="000066.SZ",
    condition="price_drop > 5%",
    notify_via="hermes",
    priority="P1"
)
# 自动集成Hermes.send()
```

### 与Karpathy Wiki集成

```python
# 从wiki页面生成策略
wiki_page = "wiki/companies/中国长城.md"
strategy = codex.from_wiki(wiki_page)
# 提取Tier级别、仓位建议、关键催化
```

---

## 📊 核心能力对比

| 能力 | 传统方式 | Codex方式 | 效率提升 |
|:-----|:---------|:----------|:--------:|
| 策略代码编写 | 2-4小时 | 5分钟 | **30-50x** |
| 回测框架搭建 | 4-8小时 | 5分钟 | **50-100x** |
| 监控脚本编写 | 1-2小时 | 2分钟 | **30-60x** |
| 代码调试 | 2-4小时 | 几乎为零 | 质量提升 |

---

## 🎯 代码质量保证

### 自动检查项

- ✅ 语法检查 (Python AST验证)
- ✅ 导入检查 (依赖项存在性)
- ✅ 类型提示 (Type hints)
- ✅ 文档字符串 (Docstrings)
- ✅ 注释生成 (关键点说明)
- ✅ 异常处理 (Try-except)
- ✅ 日志记录 (Logging)

### 代码风格

- PEP 8 规范
- Google Python Style
- A5L内部规范

---

## 📁 文件结构

```
skills/codex/
├── SKILL.md                  # 本文档
├── codex.py                  # 核心引擎
├── templates/                # 代码模板库
│   ├── strategy_template.py
│   ├── backtest_template.py
│   ├── monitor_template.py
│   └── data_analysis_template.py
├── examples/                 # 示例代码
│   ├── strategy_cgw.py
│   └── backtest_cgw.py
└── tests/                    # 测试用例
    └── test_codex.py
```

---

## 🏷️ 标签

#codex #代码生成 #策略编程 #自动化 #layer2 #策略引擎

---

> **Chief指导**: *"描述你的投资逻辑，Codex帮你实现。"*
