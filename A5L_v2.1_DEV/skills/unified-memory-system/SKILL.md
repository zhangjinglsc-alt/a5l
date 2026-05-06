---
name: unified-memory-system
description: Unified memory system integration across all memory types. Use for comprehensive memory management and retrieval.
---

# 统一记忆系统 SKILL

## 描述

统一的记忆系统，四层记忆架构（会话-日常-长期-进化），适用于记忆系统、知识库检索、Session恢复。

## 使用方法

触发此 Skill 的指令：
- `记忆系统` - 启动记忆系统
- `知识库检索` - 检索知识库
- `Session恢复` - 恢复会话状态

## 四层记忆架构

### 1. 会话记忆 (Session Memory)
- 当前对话上下文
- 临时变量和状态
- 会话级配置

### 2. 日常记忆 (Daily Memory)
- 每日记录 (memory/YYYY-MM-DD.md)
- 当天的事件和决策
- 待办事项

### 3. 长期记忆 (Long-term Memory)
- MEMORY.md - 重要信息和经验
- AGENTS.md - 身份和行为准则
- USER.md - 用户信息
- TOOLS.md - 工具配置

### 4. 进化记忆 (Evolution Memory)
- 错误记录和修复
- 成功案例固化
- Skill改进记录
- 系统迭代日志

## 记忆操作

### 写入记忆
```python
write_memory(content, level="daily")
```

### 读取记忆
```python
read_memory(query, level="all")
```

### 搜索记忆
```python
search_memory(query, n_results=5)
```

## 记忆同步

- **Git备份** - 版本控制
- **飞书同步** - 云端备份
- **本地优先** - 本地为主，云端为辅
