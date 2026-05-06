---
name: memory
description: Persistent memory management including long-term, working, and episodic memory. Use for storing user preferences, project context, and learning from interactions.
---

# Memory SKILL

## 描述

记忆工具，支持读写MEMORY.md和memory/*.md，适用于记忆、文档管理、知识库检索、Session恢复。

## 使用方法

触发此 Skill 的指令：
- `记忆` - 管理记忆
- `文档管理` - 管理文档
- `知识库检索` - 检索知识库
- `Session恢复` - 恢复会话

## 功能

### 读写MEMORY.md
- 读取长期记忆
- 更新重要信息
- 记录经验教训
- 保存用户偏好

### 读写memory/*.md
- 创建每日记录
- 归档历史记录
- 搜索历史信息
- 时间线管理

### 知识库检索
- 语义搜索
- 关键词搜索
- 时间范围过滤
- 分类检索

### Session恢复
- 保存会话状态
- 恢复对话上下文
- 续接中断会话
- 状态迁移

## 使用示例

```python
# 写入记忆
write_memory(content="重要信息", file="MEMORY.md")

# 读取记忆
memory = read_memory(file="MEMORY.md")

# 每日记录
daily_note(date="2024-01-01", content="今日记录")

# 搜索记忆
results = search_memory(query="关键词", n=5)
```
