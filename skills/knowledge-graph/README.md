# A5L 知识图谱 SKILL

## 目录结构

```
skills/knowledge-graph/
├── SKILL.md                      # 本文件 - 设计文档
├── knowledge_graph_core.py       # 核心模块（SQLite + NetworkX）
├── entity_extractor.py           # 实体提取器（已完成）
├── relation_builder.py           # 关系构建器（已完成）
├── visualizer.py                 # 可视化模块（已完成）
├── kg_integration.py             # 集成与自动化（已完成）
├── kg_analyzer.py                # A5L深度分析模块（新增）
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

## 🧠 A5L深度分析（新增）

让A5L"进去思考"，基于知识图谱进行深度投资分析：

```python
from kg_analyzer import KGAnalyzer

# 创建分析器
analyzer = KGAnalyzer()

# 分析研报（自动：提取实体 → 构建关系 → A5L思考 → 生成洞察）
result = analyzer.analyze_document(
    doc_content="研报内容...",
    doc_id="report_001",
    doc_title="半导体行业分析"
)

# 查看A5L思考过程
print("观察:", result['thinking']['observation'])
print("分析:", result['thinking']['analysis'])
print("推理:", result['thinking']['reasoning'])
print("判断:", result['thinking']['judgment'])

# 查看投资信号
for signal in result['signals']:
    print(f"{signal['entity_name']}: {signal['signal_type']} (置信度: {signal['confidence']})")

# 查看操作建议
for rec in result['recommendations']:
    print(f"建议: {rec['action']}")
```

### A5L分析流程

```
研报输入
    ↓
[Step 1] 提取实体
[Step 2] 构建关系
[Step 3] A5L深度思考（观察→分析→推理→判断）
[Step 4] 生成投资信号（看多/看空/观望）
[Step 5] 多维度分析（UZI风格评分）
[Step 6] 知识推理（结合已有图谱）
[Step 7] 生成操作建议
[Step 8] 归档思考结果
    ↓
输出：洞察报告 + 可视化图谱 + 投资信号
```

## 开发计划

- [x] Phase 1: 基础框架（SQLite+NetworkX架构）
- [x] Phase 2: 实体提取（规则-based NER）
- [x] Phase 3: 关系构建（产业链/关联/持仓）
- [x] Phase 4: 可视化（pyvis交互式图谱）
- [x] Phase 5: 集成优化（KG集成+自动更新）
- [x] Phase 6: A5L深度分析（思考→信号→建议）✨新增
