# A5L 知识图谱 SKILL

## 目录结构

```
skills/knowledge-graph/
├── SKILL.md                      # 本文件 - 设计文档
├── knowledge_graph_core.py       # 核心模块（SQLite + NetworkX）
├── entity_extractor.py           # 实体提取器（已完成）
├── relation_builder.py           # 关系构建器（待开发）
├── visualizer.py                 # 可视化模块（待开发）
├── requirements.txt              # 依赖包
├── data/                         # 数据目录
│   └── knowledge_graph.db        # SQLite数据库
└── tests/                        # 测试目录
    └── test_knowledge_graph.py   # 单元测试（待开发）
```

## 快速开始

### 1. 安装依赖

```bash
cd skills/knowledge-graph
pip install -r requirements.txt
```

### 2. 测试运行

```bash
python knowledge_graph_core.py
```

### 3. 使用示例

```python
from knowledge_graph_core import KnowledgeGraph, create_stock_entity

# 创建知识图谱实例
kg = KnowledgeGraph()

# 添加股票实体
nvda = create_stock_entity("NVDA", "NVIDIA", "半导体")
kg.add_entity(nvda)

# 查询关联
related = kg.get_related_entities("stock_NVDA")
print(related)
```

## API接口

详见 `knowledge_graph_core.py` 文档字符串

## 开发计划

- [x] Phase 1: 基础框架（SQLite+NetworkX架构）
- [x] Phase 2: 实体提取（规则-based NER）
- [ ] Phase 3: 关系构建（产业链/关联/持仓）
- [ ] Phase 4: 可视化（pyvis交互式图谱）
- [ ] Phase 5: 集成优化（KG集成+自动更新）
