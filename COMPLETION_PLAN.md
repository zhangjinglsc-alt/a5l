# A5L v2.2 完整完成计划
# Chief要求: 全部完成
# 当前完成度: 45% → 目标: 95%
# 预计总用时: 8-10小时

## 📋 任务清单与详细步骤

---

## 🔴 P0 最高优先级 (必须完成)

### 任务1: 飞书API真实连接 [2-3小时]

**现状:** 有框架但无真实调用
**目标:** 能真正发送/接收飞书消息

#### 步骤1.1: 检查飞书授权状态 [10分钟]
```bash
# 检查当前授权文件
ls -la /workspace/projects/workspace/config/feishu*

# 检查token是否有效
curl -X GET "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\": \"YOUR_APP_ID\", \"app_secret\": \"YOUR_APP_SECRET\"}"
```

#### 步骤1.2: 创建飞书真实API客户端 [30分钟]
创建文件: `integrations/feishu_real_client.py`

核心功能:
- 获取tenant_access_token
- 发送文本消息到群聊
- 发送富文本(卡片)消息
- 接收消息回调处理

#### 步骤1.3: 测试真实消息发送 [20分钟]
- 发送测试消息到指定群
- 验证消息到达
- 错误处理测试

#### 步骤1.4: 集成到A5L核心 [60分钟]
- 修改 `hub_v2_global_sync.py`
- 真实跨域通知 → 飞书消息
- 决策完成 → 飞书卡片推送

---

### 任务2: SQLite持久化存储 [3-4小时]

**现状:** 所有数据内存存储，重启丢失
**目标:** 关键数据持久化

#### 步骤2.1: 设计数据库Schema [30分钟]
创建文件: `database/schema.sql`

表结构:
```sql
-- Atoms表
CREATE TABLE atoms (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    title TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 决策记录表
CREATE TABLE decisions (
    id TEXT PRIMARY KEY,
    type TEXT,
    symbol TEXT,
    action TEXT,
    status TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chain_json TEXT -- 决策链JSON
);

-- 信号记录表
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    signal_type TEXT,
    strength REAL,
    context_json TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 同步日志表
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT, -- KIWI→Prime 或 Prime→KIWI
    item_id TEXT,
    action TEXT,
    status TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 步骤2.2: 创建数据库管理类 [60分钟]
创建文件: `database/db_manager.py`

核心方法:
- `init_db()` - 初始化数据库
- `save_atom(atom)` - 保存Atom
- `get_atom(id)` - 获取Atom
- `save_decision(decision)` - 保存决策
- `get_decisions(limit=100)` - 获取决策列表
- `save_signal(signal)` - 保存信号

#### 步骤2.3: 迁移现有代码 [90分钟]
修改文件:
- `wave1/prime_registry_v2.py` - 使用SQLite存储
- `wave2/autonomous_decision_system.py` - 决策持久化
- `wave2/recursive_improvement.py` - 改进循环记录
- `wave3/kiwi_prime_sync.py` - 同步日志

#### 步骤2.4: 数据迁移和测试 [30分钟]
- 创建数据库文件
- 测试CRUD操作
- 验证重启后数据保留

---

## 🟡 P1 高优先级 (应该完成)

### 任务3: Prime MCP协议真实对接 [4-6小时]

**现状:** 仅模拟
**目标:** 真正与Prime官方协议兼容

#### 步骤3.1: 研究Prime官方协议 [60分钟]
- 阅读Prime MCP规范
- 理解Tool Registration流程
- 理解Call Tool流程

#### 步骤3.2: 实现真实MCP Server [120分钟]
基于 `mcp` Python SDK:
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("a5l-mcp-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    # 返回A5L SKILL作为Tools
    pass

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # 调用真实SKILL
    pass
```

#### 步骤3.3: 测试与Prime集成 [60-120分钟]
- 注册到Prime Registry
- 测试Tool调用
- 延迟测试

---

### 任务4: 真正的语义搜索 [3-4小时]

**现状:** 关键词匹配
**目标:** 基于向量嵌入的语义搜索

#### 步骤4.1: 选择Embedding方案 [20分钟]
选项:
- OpenAI Embedding API (需要API Key)
- 本地模型 (sentence-transformers)
- Coze Embedding

推荐: 本地模型 `sentence-transformers/all-MiniLM-L6-v2`

#### 步骤4.2: 实现向量存储 [60分钟]
使用 `chromadb` 或 `faiss`:
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("a5l_knowledge")

# 添加文档
for atom in atoms:
    embedding = model.encode(atom['content'])
    collection.add(
        ids=[atom['id']],
        embeddings=[embedding],
        documents=[atom['content']]
    )

# 语义搜索
results = collection.query(
    query_embeddings=[model.encode("AI算力投资")],
    n_results=5
)
```

#### 步骤4.3: 集成到搜索系统 [60分钟]
修改 `wave3/prime_intelligent_search.py`

---

### 任务5: 真正的并行执行 [2-3小时]

**现状:** 流程演示
**目标:** 真正的多线程/异步并行

#### 步骤5.1: 实现并行Squad执行 [90分钟]
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def execute_squad_parallel(squads, task):
    """并行执行多个Squad"""
    with ThreadPoolExecutor(max_workers=10) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, squad.execute, task)
            for squad in squads
        ]
        results = await asyncio.gather(*futures)
    return results
```

#### 步骤5.2: 性能基准测试 [30-60分钟]
- 串行 vs 并行对比
- 线程数优化

---

## 🟢 P2 中等优先级 (可以后续)

### 任务6: 单元测试 [4-6小时]

#### 步骤6.1: 设置测试框架 [30分钟]
```bash
pip install pytest pytest-asyncio pytest-cov
```

#### 步骤6.2: 为核心模块编写测试 [3-4小时]
- `test_tushare_client.py`
- `test_decision_system.py`
- `test_squad_dispatch.py`

#### 步骤6.3: 测试覆盖率检查 [30分钟]
```bash
pytest --cov=. --cov-report=html
```

---

### 任务7: Docker部署 [2-3小时]

#### 步骤7.1: 创建Dockerfile [30分钟]
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "a5l_main.py"]
```

#### 步骤7.2: Docker Compose [30分钟]
```yaml
version: '3.8'
services:
  a5l:
    build: .
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - TUSHARE_TOKEN=${TUSHARE_TOKEN}
  
  sqlite:
    image: nouchka/sqlite3
    volumes:
      - ./data:/data
```

#### 步骤7.3: 测试部署 [60-90分钟]

---

## 📅 建议执行顺序

### 今晚 (剩余~4小时):
1. ✅ Tushare集成 (已完成)
2. 🔄 SQLite持久化 (3-4小时) ← **现在开始做**
3. 🔄 飞书API连接 (2-3小时) ← **明早做**

### 明晚 (4-5小时):
4. 🔄 Prime MCP真实对接 (4-6小时)
5. 🔄 语义搜索 (3-4小时)

### 后续:
6. 并行执行优化
7. 单元测试
8. Docker部署

---

## 🎯 完成度预测

| 阶段 | 完成后度 | 说明 |
|:---|:---:|:---|
| 现在 | 45% | Tushare✅ |
| +SQLite | 60% | 数据持久化 |
| +飞书 | 70% | 完整通知闭环 |
| +Prime MCP | 80% | 协议兼容 |
| +语义搜索 | 85% | 智能检索 |
| +测试+部署 | 95% | 生产就绪 |

---

## 🚀 立即开始

Chief，选择你的下一步：

**A. 现在开始SQLite持久化 [3-4小时]**
- 最长但最关键
- 完成后数据不再丢失

**B. 先完成飞书API [2-3小时]**
- 快速见效
- 可以真正收到通知

**C. 明早09:15前快速完成飞书 [1小时简化版]**
- 仅发送功能
- 足够支撑盘前通知

**你的选择？**
