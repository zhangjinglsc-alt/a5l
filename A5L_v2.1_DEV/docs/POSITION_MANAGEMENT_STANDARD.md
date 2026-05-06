# 📊 A5L 持仓管理系统规范 v1.0

## 核心原则
**真实持仓 = SignalArena交易记录 (唯一真相源)**
**模拟持仓 = A5L三市场模拟交易 (试错实验场)**

---

## 文件结构区分

```
/workspace/projects/workspace/
├── 📁 memory/
│   ├── 📁 portfolio/                 # 真实持仓 (SignalArena)
│   │   ├── REAL_POSITION_MASTER.md   # 真实持仓主档案 ⭐
│   │   ├── REAL_2026-05-05.md        # 每日真实持仓快照
│   │   ├── REAL_2026-05-04.md
│   │   └── README.md                 # 真实持仓说明
│   │
│   └── 📁 simulation/                # 模拟持仓 (A5L实验)
│       ├── SIM_POSITION_MASTER.md    # 模拟持仓总览 ⭐
│       ├── US_SIM_001/               # 美股模拟
│       ├── CN_SIM_001/               # A股模拟
│       └── HK_SIM_001/               # 港股模拟
│
├── 📁 data/simulation/               # 模拟交易数据 (JSON)
│   ├── US_SIM_001.json               # [SIMULATION] 美股模拟账户
│   ├── CN_SIM_001.json               # [SIMULATION] A股模拟账户
│   ├── HK_SIM_001.json               # [SIMULATION] 港股模拟账户
│   └── plans/                        # 模拟交易计划
│
└── 📁 config/
    └── position_mapping.json         # 持仓文件映射配置
```

---

## 命名规范

| 类型 | 前缀 | 示例 | 说明 |
|:-----|:-----|:-----|:-----|
| **真实持仓** | `REAL_` | `REAL_POSITION_MASTER.md` | SignalArena真实交易 |
| **模拟持仓** | `SIM_` | `SIM_POSITION_MASTER.md` | A5L模拟交易 |
| **美股模拟** | `US_SIM_` | `US_SIM_001.json` | 美股实验账户 |
| **A股模拟** | `CN_SIM_` | `CN_SIM_001.json` | A股实验账户 |
| **港股模拟** | `HK_SIM_` | `HK_SIM_001.json` | 港股实验账户 |

---

## 标记系统

### 文件头标记

#### 真实持仓文件头
```markdown
---
type: REAL_POSITION
source: SignalArena
account_type: 真实账户
accounts: [自有, WGB, 王力, 老娘]
currency: CNY
last_sync: 2026-05-05 11:37:56
---

# [🔴 REAL] 真实持仓报告 2026-05-05

⚠️ **警告：这是真实资金持仓！**
- 所有数据来自SignalArena交易记录
- 涉及真实盈亏
- 操作前必须二次确认

---
```

#### 模拟持仓文件头
```markdown
---
type: SIMULATION_POSITION
source: A5L_Simulation
account_type: 模拟账户
account_id: US_SIM_001
currency: USD
initial_capital: 1000000
last_sync: 2026-05-06 00:49:00
---

# [🔵 SIM] 美股模拟持仓 US_SIM_001

ℹ️ **提示：这是模拟交易账户**
- 用于策略试错和实验
- 不涉及真实资金
- 大胆测试，全面记录

---
```

---

## 数据流向

```
真实持仓流向:
SignalArena交易 → portfolio_report_YYYYMMDD.md → REAL_POSITION_MASTER.md → MEMORY.md

模拟持仓流向:
A5L交易执行 → US/CN/HK_SIM_001.json → SIM_POSITION_MASTER.md → 飞书模拟交易文档
```

---

## 快速查询命令

```bash
# 查看最新真实持仓
cat /workspace/projects/workspace/memory/portfolio/REAL_POSITION_MASTER.md

# 查看最新模拟持仓
cat /workspace/projects/workspace/memory/simulation/SIM_POSITION_MASTER.md

# 查看美股模拟持仓
cat /workspace/projects/workspace/data/simulation/US_SIM_001.json | jq '.positions'

# 查看A股模拟持仓
cat /workspace/projects/workspace/data/simulation/CN_SIM_001.json | jq '.positions'
```

---

## 飞书文档区分

| 文档类型 | 标题格式 | 示例 |
|:---------|:---------|:-----|
| 真实持仓 | `[REAL] 真实持仓报告 YYYYMMDD` | `[REAL] 真实持仓报告 20260505` |
| 美股模拟 | `[SIM-US] 美股模拟交易计划` | `[SIM-US] CIO美股模拟交易计划` |
| A股模拟 | `[SIM-CN] A股模拟交易计划` | `[SIM-CN] CIO A股模拟交易计划` |
| 港股模拟 | `[SIM-HK] 港股模拟交易计划` | `[SIM-HK] CIO港股模拟交易计划` |

---

## 禁止事项

❌ **严禁行为**:
1. 将模拟持仓写入真实持仓文档
2. 将真实持仓与模拟持仓合并统计
3. 在MEMORY.md中混淆两种持仓
4. 向真实持仓文档添加模拟交易记录

---

*最后更新: 2026-05-06*
*版本: v1.0*
