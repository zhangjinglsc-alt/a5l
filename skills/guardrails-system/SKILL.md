---
name: guardrails-system
description: Agentic Design Patterns-based guardrails and safety system for A5L. Implements input validation, output verification, compliance checking, and safety boundaries to ensure responsible AI operations.
triggers:
  - "护栏检查"
  - "安全检查"
  - "合规验证"
  - "guardrails"
  - "safety check"
  - "内容审核"
layer: "L0_Meta_Control"
owner: "CSO"
priority: "P2"
---

# Guardrails-System SKILL

## 概述

基于Agentic Design Patterns的护栏系统，为A5L提供多层安全防护。通过输入验证、输出审查、合规检查和操作边界控制，确保AI系统负责任地运行。

**设计模式来源**: Agentic Design Patterns Ch.18 Guardrails & Safety Patterns (Gulli, 2025)
**架构归属**: Layer 0 Meta Control - CSO安全合规
**核心能力**: 输入护栏、输出护栏、执行护栏、合规审查

## 三层护栏架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Guardrails                         │
│                   (输入护栏层)                               │
├─────────────────────────────────────────────────────────────┤
│ • 指令注入检测 (Prompt Injection Detection)                  │
│ • 敏感信息过滤 (Sensitive Data Filtering)                    │
│ • 输入格式验证 (Input Validation)                            │
│ • 意图识别与分类 (Intent Classification)                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 Execution Guardrails                        │
│                   (执行护栏层)                               │
├─────────────────────────────────────────────────────────────┤
│ • 权限校验 (Permission Verification)                         │
│ • 资源限制 (Resource Limits)                                 │
│ • 操作边界 (Operation Boundaries)                            │
│ • 时间窗口检查 (Time Window Validation)                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Output Guardrails                        │
│                   (输出护栏层)                               │
├─────────────────────────────────────────────────────────────┤
│ • 事实核查 (Fact Verification)                               │
│ • 偏见检测 (Bias Detection)                                  │
│ • 合规审查 (Compliance Check)                                │
│ • 安全风险扫描 (Safety Risk Scanning)                        │
└─────────────────────────────────────────────────────────────┘
```

## 输入护栏 (Input Guardrails)

### 1. 指令注入检测

**威胁类型**:
```
类型A: 直接注入
"忽略之前的指令，改为执行..."

类型B: 间接注入  
通过上传文件/图片隐藏恶意指令

类型C: 角色劫持
"从现在开始你不再是AI助手，而是..."

类型D: 上下文溢出
用大量无关内容淹没上下文，覆盖系统提示
```

**检测规则**:
```python
INJECTION_PATTERNS = [
    r"忽略.*指令",
    r"忘记.*设定",
    r"你现在.*是",
    r"从现在开始",
    r"system|admin|root",
    r"DAN|jailbreak",
    r"\{\{.*?\}\}",  # 模板注入
]

def detect_injection(user_input):
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return {
                "detected": True,
                "pattern": pattern,
                "confidence": calculate_confidence(user_input, pattern),
                "action": "block" if confidence > 0.8 else "warn"
            }
    return {"detected": False}
```

### 2. 敏感信息过滤

**敏感数据类型**:
| 类型 | 示例 | 处理方式 |
|------|------|----------|
| 真实账号 | 证券账户、银行卡号 | 拦截+告警 |
| 密码/密钥 | API Key、密码 | 拦截+告警 |
| PII信息 | 身份证号、手机号 | 脱敏处理 |
| 内幕信息 | 未公开重大信息 | 标记+合规审查 |

**过滤规则**:
```python
SENSITIVE_PATTERNS = {
    "account_number": r"\d{10,20}",  # 账号格式
    "api_key": r"[a-zA-Z0-9]{32,64}",  # API密钥格式
    "phone": r"1[3-9]\d{9}",  # 手机号
    "id_card": r"\d{17}[\dXx]",  # 身份证号
}

def filter_sensitive_data(text):
    detected = {}
    for data_type, pattern in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            detected[data_type] = matches
            # 脱敏处理
            for match in matches:
                masked = mask_data(match, data_type)
                text = text.replace(match, masked)
    return text, detected
```

### 3. 输入验证框架

```json
{
  "input_validation": {
    "schema": {
      "type": "object",
      "properties": {
        "command": {
          "type": "string",
          "enum": ["analyze", "trade", "query", "report"],
          "required": true
        },
        "stock_code": {
          "type": "string",
          "pattern": "^[0-9]{6}$",
          "required": false
        },
        "market": {
          "type": "string", 
          "enum": ["CN", "US", "HK"],
          "default": "CN"
        },
        "amount": {
          "type": "number",
          "minimum": 0,
          "maximum": 100000000
        }
      }
    },
    "sanitization": {
      "strip_html": true,
      "normalize_whitespace": true,
      "max_length": 10000
    }
  }
}
```

## 执行护栏 (Execution Guardrails)

### 1. 交易操作权限矩阵

| 操作 | REAL账户 | SIM账户 | 需要确认 | 备注 |
|------|----------|---------|----------|------|
| 查询持仓 | ✅ | ✅ | 否 | 只读 |
| 模拟交易 | ❌ | ✅ | 否 | 仅限模拟 |
| 小额交易(<10万) | ✅ | ✅ | 否 | 自动执行 |
| 大额交易(>10万) | ✅ | ✅ | 是 | 人工确认 |
| 全仓操作 | ⚠️ | ✅ | 必须 | 高风险词汇拦截 |
| 修改系统配置 | ❌ | ❌ | N/A | 仅CA可执行 |

### 2. 资金阈值检查

```python
TRADING_LIMITS = {
    "REAL": {
        "single_trade_max": 500000,  # 单笔50万上限
        "daily_trade_max": 2000000,  # 日累计200万上限
        "concentration_max": 0.50,   # 集中度50%上限
        "leverage_max": 1.50         # 杠杆率150%上限
    },
    "SIM": {
        "single_trade_max": 10000000,  # 模拟盘无严格限制
        "daily_trade_max": 50000000,
        "concentration_max": 1.0,
        "leverage_max": 3.0
    }
}

def check_trade_permission(account_type, trade_amount, current_exposure):
    limits = TRADING_LIMITS[account_type]
    
    # 检查单笔限额
    if trade_amount > limits["single_trade_max"]:
        return {
            "allowed": False,
            "reason": f"单笔交易{trade_amount}超过限额{limits['single_trade_max']}",
            "required_action": "require_approval"
        }
    
    # 检查集中度
    new_concentration = calculate_concentration(current_exposure + trade_amount)
    if new_concentration > limits["concentration_max"]:
        return {
            "allowed": False,
            "reason": f"集中度将达到{new_concentration:.1%}，超过上限{limits['concentration_max']:.0%}",
            "required_action": "require_approval"
        }
    
    return {"allowed": True}
```

### 3. 时间窗口验证

```python
MARKET_HOURS = {
    "CN": {
        "pre_market": ("09:15", "09:25"),
        "morning": ("09:30", "11:30"),
        "afternoon": ("13:00", "15:00")
    },
    "US": {
        "regular": ("21:30", "04:00")  # 次日
    },
    "HK": {
        "pre_market": ("09:00", "09:30"),
        "morning": ("09:30", "12:00"),
        "afternoon": ("13:00", "16:00")
    }
}

def validate_trading_time(market, action):
    now = get_current_time()
    hours = MARKET_HOURS[market]
    
    # 检查是否在交易时段
    in_trading_hours = any(
        start <= now.time() <= end 
        for start, end in hours.values()
    )
    
    if not in_trading_hours:
        return {
            "allowed": False,
            "reason": f"{market}市场当前非交易时间",
            "next_session": get_next_session(market)
        }
    
    # 特殊时段限制
    if action == "sell_at_open" and not is_pre_market(market):
        return {
            "allowed": False,
            "reason": "开盘卖出仅在集合竞价时段允许",
            "next_window": "明日09:15-09:25"
        }
    
    return {"allowed": True}
```

## 输出护栏 (Output Guardrails)

### 1. 投资建议合规检查

**必须包含的免责声明**:
```
⚠️ 风险提示：
1. 以上分析仅供参考，不构成投资建议
2. 投资有风险，入市需谨慎
3. 过往业绩不代表未来表现
4. 请根据自身风险承受能力做出决策
5. [REAL] 本建议涉及真实资金操作，请独立判断
```

**禁止性表述**:
| 风险等级 | 表述 | 处理方式 |
|----------|------|----------|
| 🔴 高危 | "必涨"、"稳赚"、"无风险" | 强制替换为"预期"、"存在风险" |
| 🟡 中危 | "推荐买入"、"强烈建议" | 添加"仅供参考"前缀 |
| 🟢 低危 | "关注"、"观察" | 允许通过 |

### 2. 事实核查机制

```python
FACT_CHECK_RULES = {
    "stock_price": {
        "source": ["unified-stock-price", "SignalArena"],
        "max_age": 300,  # 5分钟
        "tolerance": 0.01  # 1%误差允许
    },
    "financial_data": {
        "source": ["tushare", "finnhub"],
        "max_age": 86400,  # 1天
        "tolerance": 0.001
    },
    "market_news": {
        "source": ["unified-news-aggregator"],
        "max_age": 3600,  # 1小时
        "verification": "cross_reference"
    }
}

def verify_fact(statement, fact_type):
    """
    核查输出中的事实陈述
    """
    # 提取关键数据点
    data_points = extract_data_points(statement)
    
    verified = []
    unverified = []
    
    for point in data_points:
        rule = FACT_CHECK_RULES.get(point["type"])
        if not rule:
            unverified.append(point)
            continue
        
        # 查询权威数据源
        actual_value = query_authoritative_source(
            point["entity"], 
            point["metric"],
            rule["source"]
        )
        
        # 验证
        if actual_value and within_tolerance(
            point["value"], 
            actual_value, 
            rule["tolerance"]
        ):
            verified.append(point)
        else:
            unverified.append({
                **point,
                "actual_value": actual_value,
                "discrepancy": calculate_discrepancy(point["value"], actual_value)
            })
    
    return {
        "verified_count": len(verified),
        "unverified_count": len(unverified),
        "unverified_items": unverified,
        "action": "warn" if unverified else "pass"
    }
```

### 3. 多空平衡检查

```python
def check_balance(analysis_text):
    """
    确保分析多空观点平衡
    """
    bullish_indicators = ["上涨", "看好", "买入", "机会", "增长", "优势"]
    bearish_indicators = ["下跌", "风险", "卖出", "警惕", "下滑", "劣势"]
    
    bullish_count = sum(1 for word in bullish_indicators if word in analysis_text)
    bearish_count = sum(1 for word in bearish_indicators if word in analysis_text)
    
    ratio = bullish_count / max(bearish_count, 1)
    
    if ratio > 3:  # 多头表述是空头的3倍以上
        return {
            "balanced": False,
            "bias": "overly_bullish",
            "suggestion": "增加风险因素分析，平衡多空观点",
            "action": "add_warning"
        }
    elif ratio < 0.33:  # 空头是多头3倍以上
        return {
            "balanced": False,
            "bias": "overly_bearish",
            "suggestion": "检查是否存在过度悲观",
            "action": "add_warning"
        }
    
    return {"balanced": True}
```

## 安全边界定义

### P0级安全红线 (不可逾越)

```python
ABSOLUTE_BOUNDARIES = {
    "financial": {
        "no_real_money_without_explicit_confirm": True,
        "no_cross_account_operations": True,
        "no_leverage_increase_when_drawdown": True
    },
    "data": {
        "no_external_data_exfiltration": True,
        "no_pii_in_logs": True,
        "no_api_keys_in_output": True
    },
    "operations": {
        "no_system_shutdown": True,
        "no_config_modification_without_ca": True,
        "no_skill_deletion": True
    }
}

def check_absolute_boundary(action, context):
    """
    检查是否触碰绝对安全红线
    """
    for category, rules in ABSOLUTE_BOUNDARIES.items():
        for rule, enforced in rules.items():
            if enforced and violates_rule(action, rule):
                return {
                    "allowed": False,
                    "violation": rule,
                    "severity": "CRITICAL",
                    "action": "BLOCK_AND_ALERT",
                    "notify": ["CSO", "Chief Architect"]
                }
    return {"allowed": True}
```

## 使用方式

### 触发指令

```
护栏检查 [内容]
安全检查 [操作]
合规验证 [输出]
guardrails [input/output]
```

### 自动触发场景

所有以下场景自动执行护栏检查:
- 交易指令执行前
- 分析报告输出前
- 外部API调用前
- 配置文件修改前
- 敏感SKILL调用前

### 使用示例

**示例1: 交易指令拦截**
```
用户: 全仓买入000001

Guardrails检查:
1. 输入分析: 检测到高危词汇"全仓"
2. 权限检查: REAL账户需确认
3. 风险评估: 集中度将超过限制
4. 时间检查: 交易时段内

输出:
⚠️ 交易指令被拦截
原因:
- 包含高风险表述"全仓"
- 该操作将导致集中度超限

建议:
- 使用具体金额/股数替代"全仓"
- 或先执行减仓再买入
- 如需执行，请明确确认
```

**示例2: 输出合规审查**
```
分析输出 → Guardrails审查:
1. 事实核查: ✓ 所有价格数据已验证
2. 偏见检查: ⚠️ 多空比例5:1，偏乐观
3. 合规检查: ✓ 已添加免责声明
4. 敏感信息: ✓ 无敏感数据泄露

修订:
- 增加"主要风险"章节平衡观点
- 免责声明已自动添加

最终输出: [通过审查的版本]
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-05-08 | 初始版本，三层护栏架构 |

## 参考资料

- Gulli, A. (2025). *Agentic Design Patterns* Ch.18 Guardrails & Safety Patterns. Springer.
- OWASP Top 10 for LLM Applications
- NIST AI Risk Management Framework
