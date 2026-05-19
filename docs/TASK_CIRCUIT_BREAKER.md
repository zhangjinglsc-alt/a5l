# 任务熔断机制使用说明

## 概述
任务熔断机制用于防止定时任务反复执行失败消耗系统资源，当任务连续失败达到阈值时自动暂停执行，冷却后自动恢复或手动恢复。

## 核心特性
- ✅ 自动熔断：任务连续失败达到阈值后自动暂停执行
- ✅ 自动恢复：冷却时间过后自动恢复任务执行
- ✅ 手动管理：支持手动查看熔断状态、恢复任务
- ✅ 失败记录：记录每次失败的时间和错误信息
- ✅ 规则配置：支持全局默认规则和单任务自定义规则
- ✅ 通知提醒：熔断触发时自动发送飞书通知

## 配置文件
路径: `/workspace/projects/workspace/.circuit_breaker/config/default.json`

### 全局默认规则
```json
{
  "failure_threshold": 3,        // 连续失败次数阈值
  "time_window_minutes": 60,     // 时间窗口（统计多久内的失败）
  "cool_down_minutes": 120,      // 熔断冷却时间
  "notify_on_trigger": true,     // 熔断时是否发送通知
  "notify_channel": "feishu_dm"  // 通知渠道
}
```

### 单任务自定义规则
在`task_overrides`中配置，示例：
```json
"task_overrides": {
  "backup.sh": {
    "failure_threshold": 2,
    "cool_down_minutes": 60
  }
}
```

## 管理命令
使用`/workspace/projects/workspace/TOOLS/task_circuit_breaker.py`进行管理：

### 1. 查看所有任务状态
```bash
python3 TOOLS/task_circuit_breaker.py status
```
输出示例：
```
=== 任务熔断状态 ===
test_failure_task                        🔴 熔断中 失败次数: 3
  熔断时间: 2026-05-19 12:54
  预计恢复: 2026-05-19 14:54
test_task                                🟢 正常 失败次数: 0
```

### 2. 列出所有熔断的任务
```bash
python3 TOOLS/task_circuit_breaker.py fused
```

### 3. 手动恢复熔断的任务
```bash
python3 TOOLS/task_circuit_breaker.py recover <任务名>
```

### 4. 手动记录任务成功/失败
```bash
# 记录成功
python3 TOOLS/task_circuit_breaker.py record_success <任务名>

# 记录失败
python3 TOOLS/task_circuit_breaker.py record_failure <任务名> [错误信息]
```

## 任务执行包装脚本
所有定时任务已经通过`run_with_fuse.sh`包装执行，自动集成熔断检查和状态记录，无需手动修改任务逻辑。

手动执行任务时也可以使用包装脚本：
```bash
TOOLS/run_with_fuse.sh <任务标识名> <实际执行命令>
```

## 存储路径
- 状态文件: `/workspace/projects/workspace/.circuit_breaker/state/`
- 日志文件: `/workspace/projects/workspace/.circuit_breaker/logs/`
- 配置文件: `/workspace/projects/workspace/.circuit_breaker/config/`

## 已覆盖的定时任务
所有系统定时任务已全部集成熔断机制，包括：
- 核心任务：备份、飞书同步、复盘分析
- 维护任务：内存管理、健康检查、会话存档
- 交易任务：三市场交易执行、周末报告、数据收集
- 自动化任务：收盘更新、交易计划更新、盘前分析