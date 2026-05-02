# Memory LaceDB Setup SKILL

## 描述

OpenClaw/Codex长期记忆搭建指南，MEMORY.md三层架构、SESSION-STATE恢复机制，适用于记忆系统搭建、知识库检索、Session恢复。

## 使用方法

触发此 Skill 的指令：
- `记忆系统` - 搭建记忆系统
- `知识库检索` - 检索知识库
- `Session恢复` - 恢复会话状态

## 三层架构

### 1. SESSION层
- 当前对话上下文
- 临时变量
- 会话配置

### 2. DAILY层
- memory/YYYY-MM-DD.md
- 每日记录
- 待办事项

### 3. LONG-TERM层
- MEMORY.md
- AGENTS.md
- USER.md
- TOOLS.md

## LaceDB集成

### 向量存储
- 文本向量化
- 语义检索
- 相似度匹配

### 混合检索
- 关键词检索
- 语义检索
- 时间过滤

## Session恢复

### 状态保存
```python
save_session_state(session_id, state)
```

### 状态恢复
```python
restore_session_state(session_id)
```

### 自动恢复
- 会话中断检测
- 状态自动保存
- 会话续接
