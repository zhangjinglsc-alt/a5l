# SKILL.md - 大鸡腿压力支撑位分析 Skill

## Metadata
- **Name**: dajitui-support-resistance
- **Version**: v1.0.0
- **Layer**: Layer 2 (Strategy Engine)
- **Category**: Technical Analysis
- **Status**: Active
- **Created**: 2026-05-09

## Description
大鸡腿（DaJiTui）压力支撑位分析与形态研究系统。基于"局部高低点 + 分位数回归"实现量化分析，支持形态识别、通道分析、压力支撑计算，以及LightGBM模型训练。

## Capabilities

### 核心分析能力
| 能力 | 描述 | 输出 |
|------|------|------|
| **压力位计算** | 分位数回归拟合压力线 | 价格/概率 |
| **支撑位计算** | 分位数回归拟合支撑线 | 价格/概率 |
| **形态识别** | 上升/对称三角形、矩形、旗形、喇叭形 | 形态类型/置信度 |
| **通道识别** | 上升/下降/横盘/收敛/发散通道 | 通道类型/斜率 |
| **突破倾向** | 向上/向下突破概率评分 | breakout_up/down分数 |

### 数据支持
- 输入格式: CSV/JSON (日线数据)
- 必要字段: date, open, high, low, close, volume
- 支持市场: A股 (SH/SZ/BJ)
- 分析窗口: 可配置 (默认120日)

### 模型训练
- 算法: LightGBM
- 特征: 形态/通道/价格位置/距离支撑压力边界
- 标签: 未来5/10/20/60日收益率
- 输出: 特征重要性/预测概率

## Configuration

### 环境要求
```bash
Python >= 3.11
依赖: pandas, numpy, scipy, lightgbm, streamlit, plotly
```

### 安装
```bash
git clone https://github.com/YaoBa-Quant/dajitui-support-resistance.git
cd dajitui-support-resistance
pip install -r requirements.txt
```

## Usage

### 命令行分析
```bash
# 单票分析
python src/main.py --code 600519.SH --window 120

# 指定截止日期
python src/main.py --code 603993.SH --window 240 --end-date 2026-03-31

# 历史形态扫描
python src/main.py --code 603881.SH --window 240 --history-scan --output-dir outputs
```

### Streamlit可视化
```bash
streamlit run app.py
```
访问: http://localhost:8501

### 全市场研究流程
```bash
# 1. 生成特征与标签
python src/build_feature_labels.py --window 240

# 2. 关系分析
python src/analyze_feature_labels.py --input-file outputs/feature_labels_xxx.csv

# 3. 模型训练
python src/train_lgbm.py
```

## Integration with A5L

### 与阳关大道集成
```python
# 获取个股压力支撑分析
djt = DaJiTuiAnalyzer()
result = djt.analyze(code='000066.SZ', window=120)

# 提取关键信息
support_price = result['support_levels'][-1]  # 最近支撑位
resistance_price = result['resistance_levels'][-1]  # 最近压力位
pattern = result['pattern']['type']  # 识别形态
breakout_score = result['breakout_up']  # 向上突破倾向

# 结合浪主波浪理论
if pattern == 'ascending_triangle' and breakout_score > 0.7:
    # 上升三角形 + 高突破倾向 = 买入信号
    signal = 'BUY'
```

### 与技术分析集成
```python
# 结合技术指标综合判断
from yangguan_daodao import TechnicalAnalyzer
from dajitui import SupportResistanceAnalyzer

tech = TechnicalAnalyzer()
djt = SupportResistanceAnalyzer()

# 获取双重验证
tech_signal = tech.analyze('000066.SZ')
djt_signal = djt.analyze('000066.SZ')

# 共振确认
if tech_signal['trend'] == 'UP' and djt_signal['breakout_up'] > 0.7:
    confidence = 'HIGH'
```

### 与模拟交易系统集成
```python
# 持仓股票压力支撑监控
positions = ['000066.SZ', '601975.SH']

for code in positions:
    analysis = djt.analyze(code, window=60)
    current_price = analysis['current_price']
    resistance = analysis['nearest_resistance']
    support = analysis['nearest_support']
    
    # 接近压力位减仓
    if current_price > resistance * 0.98:
        alert(f"{code} 接近压力位 {resistance}, 考虑减仓")
    
    # 跌破支撑位止损
    if current_price < support * 0.98:
        alert(f"{code} 跌破支撑位 {support}, 触发止损")
```

## Data Schema

### 输入数据格式
```csv
date,open,high,low,close,volume
2025-01-01,100.0,105.0,99.0,104.0,1000000
...
```

### 输出结果结构
```json
{
  "code": "600519.SH",
  "current_price": 1500.0,
  "support_levels": [1450.0, 1400.0, 1350.0],
  "resistance_levels": [1550.0, 1600.0, 1650.0],
  "pattern": {
    "type": "ascending_triangle",
    "confidence": 0.82
  },
  "channel": {
    "type": "ascending",
    "slope": 0.15
  },
  "breakout_up": 0.75,
  "breakout_down": 0.25,
  "position_in_channel": 0.65
}
```

## Core Algorithms

### 1. 局部高低点识别
- 使用 `scipy.signal.argrelextrema`
- 可配置窗口大小 (默认5日)
- 识别局部极大值/极小值点

### 2. 分位数回归
- 拟合支撑线: 低分位数回归 (如10%分位)
- 拟合压力线: 高分位数回归 (如90%分位)
- 输出: 支撑/压力区间

### 3. 形态识别
| 形态 | 特征 | 信号 |
|------|------|------|
| 上升三角形 | 水平压力线+上升支撑线 | 看涨 |
| 对称三角形 | 收敛的支撑压力线 | 观望 |
| 矩形 | 水平支撑压力线 | 震荡 |
| 旗形 | 短暂反向通道 | 趋势延续 |
| 喇叭形 | 发散的支撑压力线 | 高波动 |

### 4. 通道识别
- 上升通道: 支撑压力线同向上倾斜
- 下降通道: 支撑压力线同向下倾斜
- 横盘通道: 支撑压力线接近水平
- 收敛通道: 支撑压力线夹角缩小
- 发散通道: 支撑压力线夹角扩大

## Parameters

### 主要参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--window` | 分析窗口(交易日) | 120 |
| `--extrema-window` | 局部高低点识别窗口 | 5 |
| `--end-date` | 分析截止日期 | 最近交易日 |
| `--quantile-low` | 支撑线分位数 | 0.1 |
| `--quantile-high` | 压力线分位数 | 0.9 |

## References
- [GitHub仓库](https://github.com/YaoBa-Quant/dajitui-support-resistance)
- [在线演示](https://sr.dajitui.vip/)
- [项目文档](references/README.md)

## Changelog
- **v1.0.0** (2026-05-09): 初始版本，集成大鸡腿压力支撑分析系统

## Owner
- **Role**: Chief Architect
- **System**: A5L (ARCHITECT-5L)
- **Original Author**: YaoBa-Quant
