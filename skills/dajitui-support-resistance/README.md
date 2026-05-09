# 大鸡腿压力支撑位分析系统 (DaJiTui Support/Resistance)

基于"局部高低点 + 分位数回归"的量化研究工具，支持单票分析、全市场特征生成、形态/通道关系统计，以及 Streamlit 可视化展示。

## 功能概览

- 📊 自动计算最近 N 日**支撑位**、**压力位**
- 🔺 **形态识别**: 上升三角形、对称三角形、矩形、旗形、喇叭形等
- 📈 **通道分析**: 上升/下降/横盘/收敛/发散通道识别
- 🎯 **突破倾向评分**: 向上/向下突破概率量化
- 🌐 **Streamlit可视化**: 交互式图表展示
- 🤖 **LightGBM训练**: 形态特征与未来收益关系建模

## 快速开始

### 安装
```bash
git clone https://github.com/YaoBa-Quant/dajitui-support-resistance.git
cd dajitui-support-resistance
pip install -r requirements.txt
```

### 命令行分析
```bash
# 单票分析
python src/main.py --code 600519.SH --window 120

# 历史形态扫描(5年)
python src/main.py --code 603881.SH --window 240 --history-scan --output-dir outputs
```

### 可视化界面
```bash
streamlit run app.py
```

访问 http://localhost:8501

## 项目结构

```
dajitui-support-resistance/
├── app.py                          # Streamlit可视化入口
├── src/
│   ├── main.py                     # 命令行分析入口
│   ├── indicators.py               # 核心指标计算(支撑/压力/形态/通道)
│   ├── data_loader.py              # 数据读取与清洗
│   ├── build_feature_labels.py     # 全市场特征生成
│   ├── analyze_feature_labels.py   # 形态与收益关系分析
│   └── train_lgbm.py               # LightGBM模型训练
├── tests/
│   └── test_indicators.py          # 单元测试
├── data/                           # 行情数据目录
└── outputs/                        # 输出结果目录
```

## 核心算法

### 1. 局部高低点识别
- 使用 `scipy.signal.argrelextrema`
- 滑动窗口识别局部极值点

### 2. 分位数回归
- **支撑线**: 低分位数回归 (10%分位)
- **压力线**: 高分位数回归 (90%分位)

### 3. 形态识别
| 形态 | 特征描述 | 交易含义 |
|------|----------|----------|
| 上升三角形 | 水平压力+上升支撑 | 看涨形态 |
| 对称三角形 | 收敛的支撑压力 | 突破前夕 |
| 矩形 | 水平通道 | 震荡整理 |
| 旗形 | 短暂反向通道 | 趋势延续 |
| 喇叭形 | 发散通道 | 高波动预警 |

### 4. 突破倾向评分
- `breakout_up`: 向上突破倾向 (0-1)
- `breakout_down`: 向下突破倾向 (0-1)
- 基于形态、通道斜率、成交量综合计算

## 数据格式

支持 CSV/JSON，字段要求:
- date: 日期
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- volume: 成交量

## 与A5L集成

### 阳关大道超短线
```python
# 结合浪主波浪理论
djt = DaJiTuiAnalyzer()
result = djt.analyze('000066.SZ', window=120)

if result['pattern']['type'] == 'ascending_triangle':
    if result['breakout_up'] > 0.7:
        # 上升三角形+高突破倾向 = 买入信号
        execute_buy('000066.SZ')
```

### 技术分析
```python
# 双重验证机制
tech = TechnicalAnalyzer()  # 均线/RSI/MACD
djt = SupportResistanceAnalyzer()

if tech.trend == 'UP' and djt.breakout_up > 0.7:
    confidence = 'HIGH'  # 共振确认
```

## 参考链接

- 🔗 **GitHub**: https://github.com/YaoBa-Quant/dajitui-support-resistance
- 🌐 **在线演示**: https://sr.dajitui.vip/

## 状态

- **版本**: v1.0.0
- **创建**: 2026-05-09
- **集成**: A5L Layer 2 (Strategy Engine)
