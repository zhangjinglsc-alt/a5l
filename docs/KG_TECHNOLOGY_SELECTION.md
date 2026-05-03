# 知识图谱技术选型方案

**SKILL**: knowledge-graph  
**层级**: Layer2 - Strategy Engine  
**日期**: 2026-05-03  
**状态**: 待决策后启动开发

---

## 🎯 选型维度

| 维度 | 权重 | 说明 |
|------|------|------|
| **性能** | 30% | 查询速度、构建速度、并发能力 |
| **易用性** | 25% | 学习曲线、API友好度、文档质量 |
| **功能** | 25% | 支持的图算法、可视化能力、扩展性 |
| **生态** | 10% | 社区活跃度、第三方工具支持 |
| **运维** | 10% | 部署难度、维护成本、数据备份 |

---

## 🏆 候选方案对比

### 方案1: NetworkX + JSON (轻量级)

**技术栈**: Python NetworkX库 + 本地JSON存储

**优点**:
- ✅ 零部署成本，纯Python
- ✅ API极其友好，学习曲线低
- ✅ 丰富的图算法（最短路径、PageRank等）
- ✅ 与A5L现有Python生态完美集成
- ✅ 易于版本控制（JSON文本存储）

**缺点**:
- ❌ 内存存储，数据量大时性能下降
- ❌ 无持久化，需手动保存/加载
- ❌ 不支持并发写入
- ❌ 无分布式能力

**适用场景**:
- 实体数量 < 10,000
- 关系数量 < 100,000
- 单用户访问
- 快速原型验证

**性能预估**:
- 构建: 1,000实体/秒
- 查询: <100ms（2跳内）
- 内存占用: ~500MB（10,000实体）

---

### 方案2: Neo4j Community (专业级)

**技术栈**: Neo4j图数据库 + Cypher查询语言

**优点**:
- ✅ 企业级图数据库，性能优秀
- ✅ ACID事务支持，数据安全
- ✅ 强大的Cypher查询语言
- ✅ 内置可视化工具(Bloom)
- ✅ 支持数十亿节点
- ✅ 活跃的社区和生态

**缺点**:
- ❌ 需要独立部署（Java）
- ❌ 学习曲线较高（Cypher语言）
- ❌ 社区版有功能限制
- ❌ 增加系统复杂度

**适用场景**:
- 实体数量 > 100,000
- 多用户并发访问
- 需要企业级可靠性
- 复杂的图查询需求

**性能预估**:
- 构建: 10,000实体/秒
- 查询: <50ms（多跳）
- 存储: 磁盘持久化

---

### 方案3: SQLite + NetworkX (混合式) ⭐ 推荐

**技术栈**: SQLite数据库存储 + NetworkX内存计算

**优点**:
- ✅ 持久化存储（SQLite文件）
- ✅ 计算时用NetworkX（速度快）
- ✅ 零部署（SQLite内置于Python）
- ✅ 支持SQL查询（简单场景）
- ✅ 数据可版本控制

**缺点**:
- ❌ 需要维护两套接口
- ❌ 数据同步逻辑增加复杂度

**架构设计**:
```
┌─────────────────────────────────────────┐
│  SQLite (持久化存储)                     │
│  - entities table                        │
│  - relations table                       │
└─────────────────────────────────────────┘
                    ↓ 加载
┌─────────────────────────────────────────┐
│  NetworkX (内存计算)                     │
│  - 图算法                                 │
│  - 路径分析                               │
└─────────────────────────────────────────┘
                    ↓ 保存
┌─────────────────────────────────────────┐
│  SQLite (持久化存储)                     │
└─────────────────────────────────────────┘
```

**适用场景**:
- 实体数量 10,000 - 100,000
- 需要持久化但不想部署独立数据库
- 希望平衡性能和复杂度

**性能预估**:
- 加载: <5秒（10,000实体）
- 查询: <100ms（2跳内）
- 保存: <2秒

---

### 方案4: RDFLib (语义网)

**技术栈**: RDFLib + Turtle/JSON-LD格式

**优点**:
- ✅ 支持语义网标准（RDF、OWL）
- ✅ 强大的知识推理能力
- ✅ 标准化的知识表示

**缺点**:
- ❌ 学习曲线极高
- ❌ 性能一般
- ❌ 生态相对小众
- ❌ 过度设计

**适用场景**:
- 需要复杂的知识推理
- 与其他语义网系统集成
- 学术研究

**不推荐**: 对于A5L投资场景过度复杂

---

### 方案5: Dgraph (云原生)

**技术栈**: Dgraph分布式图数据库

**优点**:
- ✅ 云原生设计，水平扩展
- ✅ 高性能（Go语言编写）
- ✅ GraphQL+-查询语言

**缺点**:
- ❌ 需要独立部署（复杂）
- ❌ 学习成本高
- ❌ 对于A5L场景过于重型

**适用场景**:
- 超大规模图谱（亿级节点）
- 分布式系统

**不推荐**: A5L当前规模不需要

---

## 📊 综合评分

| 方案 | 性能 | 易用性 | 功能 | 生态 | 运维 | 总分 | 推荐度 |
|------|------|--------|------|------|------|------|--------|
| **NetworkX+JSON** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 85 | 🥈 |
| **Neo4j** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 88 | 🥉 |
| **SQLite+NetworkX** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **91** | 🥇 |
| **RDFLib** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 55 | ❌ |
| **Dgraph** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 70 | ❌ |

---

## 💡 Six-in-One Hub 推荐

**首选**: **SQLite + NetworkX（混合式）**

**理由**:
1. **持久化**: SQLite提供可靠的数据持久化
2. **性能**: NetworkX提供优秀的内存计算性能
3. **零部署**: 无需额外安装数据库服务
4. **可维护**: 数据文件可版本控制，易于备份
5. **可扩展**: 未来可无缝迁移到Neo4j

**备选**: **NetworkX + JSON（纯内存）**
- 如果实体数量预估<5,000，可选择更简单的纯内存方案

**未来升级路径**:
```
Phase 1: SQLite + NetworkX（当前）
    ↓ 数据量增长
Phase 2: Neo4j Community（单机）
    ↓ 数据量进一步增长
Phase 3: Neo4j Enterprise（集群）
```

---

## 🔧 技术细节

### SQLite 表结构

```sql
-- 实体表
CREATE TABLE entities (
    id TEXT PRIMARY KEY,          -- 实体唯一ID
    type TEXT NOT NULL,           -- 实体类型: Stock/Industry/Concept/Event/Person
    name TEXT NOT NULL,           -- 实体名称
    code TEXT,                    -- 股票代码等
    properties JSON,              -- 其他属性(JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 关系表
CREATE TABLE relations (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,      -- 源实体ID
    target_id TEXT NOT NULL,      -- 目标实体ID
    type TEXT NOT NULL,           -- 关系类型
    properties JSON,              -- 关系属性(JSON)
    confidence REAL DEFAULT 1.0,  -- 关系置信度
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES entities(id),
    FOREIGN KEY (target_id) REFERENCES entities(id)
);

-- 索引
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_relations_source ON relations(source_id);
CREATE INDEX idx_relations_target ON relations(target_id);
CREATE INDEX idx_relations_type ON relations(type);
```

### NetworkX 图结构

```python
import networkx as nx

# 创建有向图（支持双向关系）
G = nx.DiGraph()

# 添加节点
G.add_node("stock_NVDA", 
           type="Stock", 
           name="NVIDIA", 
           code="NVDA",
           industry="半导体")

# 添加边
G.add_edge("stock_NVDA", "industry_semiconductor", 
           type="belongs_to",
           weight=1.0)

# 查询
related = nx.neighbors(G, "stock_NVDA")
path = nx.shortest_path(G, "stock_NVDA", "stock_AMD")
```

---

## 📅 开发计划（基于SQLite+NetworkX）

### Phase 1: 基础框架（第1周）
- [ ] SQLite数据库设计
- [ ] 实体/关系模型定义
- [ ] 基础CRUD接口
- [ ] NetworkX图加载/保存

### Phase 2: 实体提取（第2周）
- [ ] 规则-based实体识别
- [ ] 股票代码提取
- [ ] 行业/概念关键词匹配
- [ ] 实体消歧（基础版）

### Phase 3: 关系构建（第3周）
- [ ] 产业链关系（从研报提取）
- [ ] 关联关系（同概念/同行业）
- [ ] 持仓关系（从投资记录）
- [ ] 关系置信度计算

### Phase 4: 可视化（第4周）
- [ ] pyvis可视化
- [ ] 交互式图谱
- [ ] 路径高亮
- [ ] 导出HTML

### Phase 5: 集成优化（第5周）
- [ ] 与Knowledge Guardian集成
- [ ] 周度自动更新
- [ ] API接口完善
- [ ] 性能优化

---

## 🚀 立即启动开发

请确认以下决策后启动开发：

1. ✅ **技术方案**: SQLite + NetworkX（混合式）
2. ✅ **目录位置**: `/skills/knowledge-graph/`
3. ✅ **开发启动**: 立即开始Phase 1
4. ⏳ **待确认**: 是否需要我先创建基础框架代码？

---

*本方案等待最终确认后启动开发*
