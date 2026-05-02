# A5L CLI 使用指南

**A5L命令行工具** - 让A5L可以通过终端直接调用

---

## 🚀 快速开始

### 安装

```bash
# 方法1: 直接添加到PATH
export PATH="/workspace/projects/workspace/bin:$PATH"

# 方法2: 创建符号链接
sudo ln -s /workspace/projects/workspace/bin/a5l /usr/local/bin/a5l

# 方法3: 使用完整路径
python3 /workspace/projects/workspace/a5l_cli.py
```

### 验证安装

```bash
a5l --help
```

---

## 📖 命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| `analyze` | 分析股票 | `a5l analyze AAPL` |
| `trade` | 执行模拟交易 | `a5l trade buy AAPL 10 180.5` |
| `portfolio` | 查看投资组合 | `a5l portfolio` |
| `review` | 运行每日复盘 | `a5l review` |
| `kiwi` | KIWI知识中心 | `a5l kiwi query --query "宁德时代"` |
| `status` | 查看系统状态 | `a5l status` |

---

## 💡 使用示例

### 1. 分析股票

```bash
# 基础分析
a5l analyze AAPL

# 详细分析
a5l analyze 000001.SZ --detailed

# 港股
a5l analyze 0700.HK
```

**输出示例:**
```
🔍 分析股票: AAPL
------------------------------------------------------------
✅ A5L初始化完成

📊 分析结果:
  股票代码: AAPL
  分析时间: 2026-05-02T12:34:16

📈 Layer 1 - 数据感知:
    状态: success
    数据条数: 252

🎯 Layer 2 - 策略信号:
    信号数量: 5
    • turtle_trading: BUY (置信度: 85%)
    • trend_rs: BUY (置信度: 78%)
    • volume_price: HOLD (置信度: 72%)

🧠 Layer 3 - 认知分析:
    情绪得分: positive
    新闻数量: 15

⚡ Layer 4 - 决策执行:
    建议操作: BUY
    策略: turtle_trading
```

### 2. 执行模拟交易

```bash
# 买入
a5l trade buy AAPL 10 180.5

# 卖出
a5l trade sell AAPL 5 185.0

# 指定策略和账户
a5l trade buy NVDA 5 890.0 --strategy trend_rs --account US_SIM_001
```

**输出示例:**
```
🎮 执行模拟交易
------------------------------------------------------------
✅ A5L初始化完成
✅ 交易执行成功!
  交易ID: T20260502123456789
  标的: AAPL
  动作: BUY
  数量: 10
  价格: $180.50
  交易成本: $1.80
  可用现金: $99818.20
```

### 3. 查看投资组合

```bash
# 查看所有账户
a5l portfolio

# 查看指定账户
a5l portfolio --account US_SIM_001
```

**输出示例:**
```
📊 投资组合概况
------------------------------------------------------------
✅ A5L初始化完成

💼 美股模拟账户
  市场: US
  初始资金: $100,000.00
  可用现金: $86,024.89
  总资产: $100,420.79
  收益率: 0.42%
  持仓数: 4

  当前持仓:
    • AAPL: 10股 @ 均价$180.50
    • NVDA: 5股 @ 均价$890.00
    • TSLA: 8股 @ 均价$175.30
    • MSFT: 15股 @ 均价$420.25
```

### 4. 运行每日复盘

```bash
# 昨日复盘
a5l review

# 指定日期复盘
a5l review --date 2026-05-01

# 指定账户复盘
a5l review --account US_SIM_001
```

**输出示例:**
```
🔄 每日交易复盘
------------------------------------------------------------
✅ A5L初始化完成

📅 复盘日期: 2026-05-02
📊 交易统计:
  总交易数: 5
  盈利交易: 3
  亏损交易: 2
  胜率: 60.0%

💰 绩效指标:
  总盈亏: $1,250.50
  平均盈利: $650.33
  平均亏损: -$200.25
  盈亏比: 3.25

🎯 策略绩效:
  • turtle_trading: 3笔, 胜率67%
  • trend_rs: 2笔, 胜率50%

📝 复盘总结: 2026-05-02: 今日共5笔交易，胜率60.0%，盈利$1,250.50

✅ 行动项:
  1. 优化策略'turtle_trading': 胜率66.7%，建议继续保持
  2. 改进风险管理: 1笔交易风控不足
```

### 5. KIWI知识中心

```bash
# 归档知识
a5l kiwi archive --title "宁德时代Q1分析" --content "分析内容..." --type analysis

# 查询知识
a5l kiwi query --query "宁德时代" --limit 5

# 查看统计
a5l kiwi stats
```

**输出示例:**
```
📚 KIWI知识中心
------------------------------------------------------------
✅ A5L初始化完成
✅ 知识已归档: K20260502123456789

📚 KIWI知识中心
------------------------------------------------------------
🔍 查询结果: 8条
  • 宁德时代Q1财报分析 (相关度: 0.95)
  • 新能源车产业链研究 (相关度: 0.87)
  • 锂电池行业深度报告 (相关度: 0.82)
```

### 6. 查看系统状态

```bash
a5l status
```

**输出示例:**
```
🏗️ A5L系统状态
------------------------------------------------------------
版本: v1.0.0
架构: ARCHITECT-5L (7层)
初始化: ✅ 完成

各层状态:
  ✅ Layer 0: 元控制层 (七位一体)
  ✅ Layer 1: 数据感知层
  ✅ Layer 2: 策略决策层 (7策略)
  ✅ Layer 3: 认知分析层
  ✅ Layer 4: 执行控制层 (模拟交易)
  ✅ Layer 5: 元学习层 (自动复盘)

核心功能:
  • 模拟交易: 美股/A股/港股
  • 自动复盘: 每日21:00
  • 知识中心: KIWI
  • 多模态处理: 6种类型
```

---

## 🔧 高级用法

### 批量分析

```bash
# 创建股票列表文件
cat > stocks.txt << EOF
AAPL
NVDA
TSLA
MSFT
GOOGL
EOF

# 批量分析
while read stock; do
    a5l analyze "$stock"
done < stocks.txt
```

### 定时复盘

```bash
# 添加到crontab，每天21:30自动复盘
crontab -e
# 添加: 30 21 * * * /workspace/projects/workspace/bin/a5l review >> /tmp/a5l_review.log 2>&1
```

### 结合其他工具

```bash
# 结合jq处理JSON输出
a5l portfolio --account US_SIM_001 | jq '.total_equity'

# 结合grep过滤
a5l review | grep "总盈亏"

# 保存到文件
a5l analyze AAPL > aapl_analysis.txt
```

---

## 🛠️ 故障排除

### 问题1: 命令找不到

```bash
# 检查PATH
echo $PATH

# 使用完整路径
python3 /workspace/projects/workspace/a5l_cli.py --help
```

### 问题2: 初始化失败

```bash
# 检查依赖
pip list | grep -E "akshare|pandas|numpy"

# 重新安装
pip install -r /workspace/projects/workspace/requirements.txt
```

### 问题3: 交易执行失败

```bash
# 检查账户配置
ls -la /workspace/projects/workspace/data/sim_trading/accounts/

# 查看交易历史
 cat /workspace/projects/workspace/data/sim_trading/trades/trade_history.json
```

---

## 📚 相关文档

- [README.md](README.md) - 项目主页
- [SKILL.md](skills/ARCHITECT-5L-SUPER/SKILL.md) - 完整功能文档
- [SOUL.md](SOUL.md) - A5L灵魂宪章

---

## 🤝 贡献

欢迎改进CLI工具！可以添加的功能:
- [ ] 配置文件支持
- [ ] 交互式模式
- [ ] 结果导出(Excel/CSV)
- [ ] 图表生成
- [ ] 实时监控模式

---

*A5L CLI - 让投资分析更简单*
