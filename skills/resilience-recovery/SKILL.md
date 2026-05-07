---
name: resilience-recovery
description: Agentic Design Patterns-based exception handling and recovery system for A5L. Implements circuit breaker, graceful degradation, and automated recovery strategies to ensure system reliability.
triggers:
  - "韧性恢复"
  - "异常处理"
  - "故障恢复"
  - "熔断"
  - "降级"
  - "resilience"
  - "circuit breaker"
layer: "L0_Meta_Control"
owner: "CSO"
priority: "P1"
---

# Resilience-Recovery SKILL

## 概述

基于Agentic Design Patterns的韧性恢复系统，为A5L提供异常处理、故障恢复和 graceful degradation 能力。确保系统在部分组件失效时仍能持续提供服务。

**设计模式来源**: Agentic Design Patterns Ch.12 Exception Handling & Recovery (Gulli, 2025)
**架构归属**: Layer 0 Meta Control - CSO安全保障
**核心能力**: 异常分类、熔断机制、优雅降级、自动恢复

## 异常分类体系

### 四级严重程度

| 级别 | 名称 | 定义 | 响应时间 | 示例 |
|------|------|------|----------|------|
| P0 | 致命 (Fatal) | 系统核心功能中断 | 立即 | 数据库完全不可访问 |
| P1 | 严重 (Critical) | 关键功能受损 | < 1分钟 | 主要数据源全部失效 |
| P2 | 一般 (Major) | 重要功能受影响 | < 5分钟 | 单个API限流 |
| P3 | 轻微 (Minor) | 非核心功能异常 | < 30分钟 | 日志写入延迟 |

### 异常类型矩阵

| 类型 | 描述 | 典型场景 | 恢复策略 |
|------|------|----------|----------|
| **网络异常** | 连接超时/断开 | API调用失败 | 重试+切换备用 |
| **数据异常** | 格式错误/缺失 | 解析失败 | 清洗+默认值 |
| **资源异常** | 限流/配额耗尽 | API限流 | 队列+降级 |
| **逻辑异常** | 业务规则冲突 | 数据不一致 | 回滚+告警 |
| **系统异常** | 内存/CPU不足 | OOM错误 | 扩容+限流 |
| **外部异常** | 第三方服务故障 | 飞书API不可用 | 缓存+异步 |

## 熔断器模式 (Circuit Breaker)

### 熔断器状态机

```
                    ┌─────────────┐
         失败阈值   │   CLOSED    │ ← 正常状态
        ┌──────────→│   (关闭)    │   请求正常通过
        │           └──────┬──────┘
        │                  │ 失败计数
        │                  ▼ 超过阈值
        │           ┌─────────────┐
        │           │    OPEN     │ ← 熔断状态
        └───────────│   (开启)    │   请求快速失败
            超时     └──────┬──────┘
        ┌───────────────────┘
        │
        ▼
┌─────────────┐
│  HALF_OPEN  │ ← 半开状态
│  (半开)     │   允许测试请求
└─────────────┘
```

### 熔断策略配置

```json
{
  "circuit_breaker": {
    "name": "finnhub_api",
    "failure_threshold": 5,
    "recovery_timeout": 30,
    "half_open_max_calls": 3,
    "success_threshold": 2,
    
    "failure_types": [
      "timeout",
      "connection_error",
      "rate_limit",
      "server_error_5xx"
    ],
    
    "on_open": {
      "action": "switch_to_backup",
      "backup": "yahoo_finance_api",
      "alert": true
    },
    
    "on_half_open": {
      "action": "probe_with_limit",
      "limit": 3
    },
    
    "on_close": {
      "action": "resume_normal",
      "alert": false
    }
  }
}
```

### A5L数据层熔断示例

```python
# 美股数据源熔断配置
CIRCUIT_BREAKERS = {
    "finnhub_ws": {
        "failure_threshold": 3,
        "timeout": 60,
        "backup": ["finnhub_rest", "yahoo_api"]
    },
    "tushare": {
        "failure_threshold": 5,
        "timeout": 300,
        "backup": ["akshare", "manual_fetch"]
    },
    "feishu_api": {
        "failure_threshold": 3,
        "timeout": 60,
        "backup": ["local_cache", "github_backup"]
    }
}
```

## 优雅降级策略 (Graceful Degradation)

### 降级层级

```
Level 0: 完整功能 (Full Functionality)
    └─ 所有组件正常运行
    
    ↓ 检测到异常
    
Level 1: 有限功能 (Limited Functionality)
    ├─ 核心功能可用
    ├─ 非核心功能禁用
    └─ 例: 只读模式，暂停写入
    
    ↓ 异常持续
    
Level 2: 最小功能 (Minimal Functionality)
    ├─ 仅保留最关键功能
    ├─ 例: 只显示持仓，停止分析
    
    ↓ 严重故障
    
Level 3: 维护模式 (Maintenance Mode)
    ├─ 完全停止服务
    ├─ 显示维护页面
    └─ 保留监控通道
```

### 按功能降级矩阵

| 功能 | 完整模式 | Level 1降级 | Level 2降级 | Level 3降级 |
|------|----------|-------------|-------------|-------------|
| 数据获取 | 多源实时 | 单源轮询 | 缓存数据 | 暂停更新 |
| 分析功能 | 全SKILL | 核心SKILL | 只读查询 | 完全禁用 |
| 报告生成 | 自动化 | 半自动 | 手动触发 | 暂停生成 |
| 通知推送 | 多渠道 | 单渠道 | 仅关键告警 | 仅系统日志 |
| 归档同步 | 实时同步 | 定时批量 | 仅本地 | 暂停同步 |

### 数据源自动切换

```python
class DataSourceManager:
    SOURCES = {
        "us_stock_price": {
            "primary": "finnhub_ws",
            "fallback_1": "finnhub_rest",
            "fallback_2": "yahoo_api",
            "fallback_3": "cached_data"
        },
        "cn_stock_price": {
            "primary": "tushare",
            "fallback_1": "akshare",
            "fallback_2": "manual_fetch"
        }
    }
    
    def fetch(self, data_type, symbol):
        sources = self.SOURCES[data_type]
        
        for source_name in sources.values():
            if self.is_available(source_name):
                try:
                    return self.call_source(source_name, symbol)
                except Exception as e:
                    self.record_failure(source_name, e)
                    continue
        
        raise AllSourcesFailed(f"All sources failed for {data_type}")
```

## 自动恢复机制

### 恢复策略库

| 策略 | 适用场景 | 恢复时间 | 风险 |
|------|----------|----------|------|
| **立即重试** | 瞬时网络抖动 | < 1秒 | 低 |
| **指数退避** | API限流/临时故障 | 几秒-几分钟 | 低 |
| **切换到备用** | 主源持续故障 | 立即 | 中 |
| **数据补偿** | 数据缺失/错误 | 分钟级 | 中 |
| **状态回滚** | 事务失败 | 秒级 | 高 |
| **人工介入** | 复杂/未知故障 | 不确定 | - |

### 指数退避重试

```python
def retry_with_backoff(func, max_retries=3, base_delay=1):
    """
    指数退避重试策略
    第1次: 1秒后重试
    第2次: 2秒后重试  
    第3次: 4秒后重试
    """
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableException as e:
            if attempt == max_retries - 1:
                raise
            
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            time.sleep(delay)
```

### 健康检查与自愈

```python
class SelfHealingSystem:
    HEALTH_CHECKS = {
        "database": {
            "check": "SELECT 1",
            "interval": 30,
            "timeout": 5
        },
        "api_connectivity": {
            "check": "ping finnhub.io",
            "interval": 60,
            "timeout": 10
        },
        "disk_space": {
            "check": "df -h /workspace",
            "interval": 300,
            "threshold": "80%"
        }
    }
    
    def run_health_check(self, component):
        check = self.HEALTH_CHECKS[component]
        try:
            result = self.execute_check(check)
            if result.status == "healthy":
                self.record_healthy(component)
                return True
            else:
                self.trigger_healing(component, result)
                return False
        except Exception as e:
            self.trigger_healing(component, error=e)
            return False
    
    def trigger_healing(self, component, result=None, error=None):
        healing_actions = {
            "database": self.restart_connection_pool,
            "api_connectivity": self.switch_to_backup_api,
            "disk_space": self.clean_old_logs,
            # ...
        }
        
        action = healing_actions.get(component)
        if action:
            action()
```

## 异常处理工作流

### 标准异常处理流程

```
1. 异常捕获 (Catch)
   └─ 捕获所有异常，避免系统崩溃

2. 异常分类 (Classify)
   └─ 根据类型和上下文确定严重程度

3. 日志记录 (Log)
   └─ 详细记录异常信息，便于后续分析

4. 告警通知 (Alert)
   └─ 根据级别通知相关人员

5. 恢复尝试 (Recover)
   └─ 执行预定义的恢复策略

6. 状态更新 (Update)
   └─ 更新系统状态，记录故障历史

7. 后续监控 (Monitor)
   └─ 持续监控恢复后的稳定性
```

### 异常升级路径

```
Level 1: 自动处理
    ├─ SKILL级别重试
    ├─ 数据源切换
    └─ 缓存返回
    
Level 2: 系统调整
    ├─ 熔断器触发
    ├─ 降级策略启动
    └─ 资源重新分配
    
Level 3: 人工介入
    ├─ 通知CSO
    ├─ 启动应急预案
    └─ 可能需要重启服务
    
Level 4: 架构调整
    ├─ 通知Chief Architect
    ├─ 评估是否需要架构调整
    └─ 长期修复方案
```

## 故障隔离

### 舱壁模式 (Bulkhead)

将系统划分为独立舱室，防止故障扩散:

```
┌─────────────────────────────────────────┐
│           A5L System                    │
├─────────────────┬───────────────────────┤
│  数据获取舱室    │     分析处理舱室       │
│  (Data Layer)   │  (Analysis Layer)     │
│                 │                       │
│  ┌───────────┐  │   ┌───────────────┐   │
│  │ Finnhub   │  │   │ UZI-Skill     │   │
│  │ Tushare   │  │   │ Value Cell    │   │
│  │ AKShare   │  │   │ 产业链分析     │   │
│  └───────────┘  │   └───────────────┘   │
├─────────────────┼───────────────────────┤
│  输出舱室       │     监控舱室          │
│  (Output)      │   (Monitoring)        │
│                 │                       │
│  ┌───────────┐  │   ┌───────────────┐   │
│  │ 飞书推送   │  │   │ 健康检查      │   │
│  │ GitHub备份 │  │   │ 告警系统      │   │
│  └───────────┘  │   └───────────────┘   │
└─────────────────┴───────────────────────┘

故障隔离: 数据获取故障不影响分析层继续处理已有数据
```

## 灾难恢复预案

### RTO/RPO目标

| 场景 | RTO (恢复时间目标) | RPO (恢复点目标) |
|------|-------------------|------------------|
| 单个API故障 | < 1分钟 | 0 (实时切换) |
| 主数据源故障 | < 5分钟 | < 5分钟 |
| 系统部分故障 | < 15分钟 | < 15分钟 |
| 全系统故障 | < 1小时 | < 30分钟 |

### 灾难恢复流程

```
1. 故障检测
   └─ 自动监控/人工报告

2. 影响评估
   └─ 确定影响范围和严重程度

3. 应急响应
   ├─ 启动降级模式
   ├─ 通知相关人员
   └─ 激活备用系统

4. 故障恢复
   ├─ 修复根本原因
   ├─ 逐步恢复服务
   └─ 验证功能完整

5. 事后复盘
   ├─ 生成故障报告
   ├─ 更新应急预案
   └─ 优化监控指标
```

## 使用方式

### 触发指令

```
韧性恢复 [异常描述]
异常处理 [error]
熔断检查
降级模式 [level]
恢复服务 [component]
resilience status
```

### 使用示例

**示例1: API故障自动处理**
```
场景: Finnhub WebSocket断开

Resilience-Recovery动作:
1. 异常捕获: 检测到WebSocket连接断开
2. 分类: P2级 - 网络异常
3. 自动响应:
   - 立即重试连接 (1次)
   - 失败 → 指数退避重试 (最多3次)
   - 仍失败 → 触发熔断器
   - 切换到Finnhub REST API备用
4. 通知: 发送降级通知到CIO
5. 监控: 持续探测WebSocket恢复
6. 自动恢复: WebSocket恢复后自动切回
```

**示例2: 手动触发降级**
```
用户: 降级模式 level1

Resilience-Recovery动作:
1. 验证权限: CSO级别可执行
2. 启动Level 1降级:
   - 暂停非核心分析SKILL
   - 切换数据源到本地缓存
   - 暂停飞书归档(保留本地)
   - 仅保留关键告警通道
3. 通知: 通知所有管理者
4. 监控: 降级模式下持续监控系统负载
5. 等待: 等待人工恢复指令
```

**示例3: 故障复盘**
```
用户: 查看本周故障报告

Resilience-Recovery输出:
┌─────────────────────────────────────────┐
│ 本周故障统计 (2026-05-01 ~ 2026-05-08)   │
├─────────────────────────────────────────┤
│ 总故障数: 12                            │
│ 自动恢复: 10 (83%)                      │
│ 需人工介入: 2 (17%)                     │
│ 平均恢复时间: 3.5分钟                    │
│                                         │
│ Top 3 故障类型:                         │
│ 1. API限流 (5次) - 已增加队列缓冲        │
│ 2. 网络超时 (4次) - 已优化超时配置       │
│ 3. 内存不足 (2次) - 已增加清理频率       │
│                                         │
│ 改进建议:                               │
│ - 考虑增加第三备用数据源                 │
│ - 优化高频SKILL内存使用                  │
└─────────────────────────────────────────┘
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-05-08 | 初始版本，熔断器+降级+自动恢复 |

## 参考资料

- Gulli, A. (2025). *Agentic Design Patterns* Ch.12 Exception Handling & Recovery. Springer.
- Nygard, M. T. (2018). "Release It!" (2nd Edition)
- Newman, S. (2015). "Building Microservices"
