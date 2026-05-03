# A5L 知识图谱使用指南

**版本**: v1.0  
**位置**: `/skills/knowledge-graph/`  
**适用**: 投资决策、行业研究、关系分析

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /workspace/projects/workspace/skills/knowledge-graph
pip install -r requirements.txt
```

依赖包：
- `networkx` - 图计算
- `pyvis` - 可视化（可选）

---

## 📖 使用方式

### 方式1: 处理飞书文档（推荐）

自动提取实体、构建关系、更新图谱：

```python
from skills.knowledge-graph.kg_integration import KGIntegration

# 创建集成器
kg = KGIntegration()

# 处理飞书文档
result = kg.process_feishu_document(
    doc_content="""
    NVIDIA (NVDA)是AI算力龙头，与AMD竞争激烈。
    半导体行业包括芯片设计、晶圆代工等环节。
    """,
    doc_id="report_001",
    doc_title="半导体行业分析"
)

print(f"添加了 {result['entities_added']} 个实体")
print(f"添加了 {result['relations_added']} 个关系")
```

---

### 方式2: 手动添加实体和关系

```python
from skills.knowledge-graph.knowledge_graph_core import (
    KnowledgeGraph, create_stock_entity, create_industry_entity
)
from skills.knowledge-graph.knowledge_graph_core import Relation

# 创建知识图谱
kg = KnowledgeGraph()

# 添加股票
nvda = create_stock_entity("NVDA", "NVIDIA", "半导体")
kg.add_entity(nvda)

# 添加行业
semiconductor = create_industry_entity("半导体")
kg.add_entity(semiconductor)

# 添加关系（NVIDIA属于半导体行业）
relation = Relation(
    id="stock_NVDA_belongs_to_industry_半导体",
    source_id="stock_NVDA",
    target_id="industry_半导体",
    type="belongs_to"
)
kg.add_relation(relation)
```

---

### 方式3: 批量处理多个文档

```python
from skills.knowledge-graph.kg_integration import KGIntegration

kg = KGIntegration()

# 准备文档列表
documents = [
    {
        'content': '文档1内容...',
        'id': 'doc_001',
        'title': '文档1标题'
    },
    {
        'content': '文档2内容...',
        'id': 'doc_002',
        'title': '文档2标题'
    }
]

# 批量处理
stats = kg.weekly_update(documents)

print(f"处理文档: {stats['documents_processed']}")
print(f"新增实体: {stats['total_entities']}")
print(f"新增关系: {stats['total_relations']}")
```

---

## 🔍 查询接口

### 查询关联实体

```python
# 获取NVDA关联的所有实体（1跳）
related = kg.kg.get_related_entities("stock_NVDA", depth=1)

for r in related:
    print(f"{r['entity_name']} ({r['entity_type']}) - {r['relation_type']}")

# 输出:
# 半导体 (Industry) - belongs_to
# AMD (Stock) - competes_with
# AI算力 (Concept) - correlates_with
```

### 查找路径

```python
# 查找从NVDA到AI算力的路径
paths = kg.kg.find_path("stock_NVDA", "concept_AI算力", max_depth=3)

for path in paths:
    print(" -> ".join([p.get('entity_name', p.get('relation_type')) for p in path]))

# 输出:
# NVIDIA -> correlates_with -> AI算力
```

### 获取产业链

```python
# 获取NVDA所在的产业链
chain = kg.kg.get_industry_chain("stock_NVDA")

print("上游:", [s['entity_name'] for s in chain['upstream']])
print("下游:", [s['entity_name'] for s in chain['downstream']])
```

### 分析股票关系网络

```python
from skills.knowledge-graph.kg_integration import analyze_stock

# 分析NVDA的完整关系网络
analysis = analyze_stock("NVDA")

print(f"竞争对手: {len(analysis['competitors'])}")
print(f"关联概念: {len(analysis['related_concepts'])}")
print(f"提及文档: {len(analysis['mentioned_in'])}")
```

---

## 📊 可视化

### 生成完整图谱

```python
# 生成完整知识图谱HTML
output_path = kg.visualizer.render_full_graph()
print(f"图谱已保存: {output_path}")

# 在浏览器中打开查看
```

### 生成子图

```python
# 生成以NVDA为中心的子图（2跳深度）
output_path = kg.visualizer.render_subgraph(
    center_node="stock_NVDA",
    depth=2
)
```

### 路径可视化

```python
# 可视化NVDA到AI算力的路径
path_data = kg.visualizer.get_path_visualization_data(
    start_id="stock_NVDA",
    end_id="concept_AI算力"
)
```

---

## 🎯 实际应用场景

### 场景1: 选股辅助

```python
from skills.knowledge-graph.kg_integration import find_investment_opportunities

# 查找"AI算力"概念下的所有投资机会
opportunities = find_investment_opportunities("AI算力")

for opp in opportunities:
    stock = opp['stock']
    analysis = opp['analysis']
    print(f"股票: {stock['entity_name']}")
    print(f"  竞争对手: {len(analysis['competitors'])}")
    print(f"  供应链: {len(analysis['industry_chain']['suppliers'])} 上游, {len(analysis['industry_chain']['customers'])} 下游")
```

### 场景2: 产业链分析

```python
# 分析半导体产业链
from skills.knowledge-graph.relation_builder import IndustryChainBuilder

builder = IndustryChainBuilder()
relations = builder.build_from_industry(kg.kg, "半导体")

print(f"半导体产业链关系: {len(relations)}")
for r in relations:
    print(f"  {r.source_id} -> {r.target_id}")
```

### 场景3: 竞争分析

```python
# 分析NVDA的竞争格局
analysis = kg.query_api('stock_analysis', stock_id='stock_NVDA')

print("竞争对手:")
for competitor in analysis['competitors']:
    print(f"  - {competitor['name']}")
```

### 场景4: 研报归档自动处理

```python
# 当Knowledge Guardian归档研报时，自动更新知识图谱

def process_report_for_kg(doc_content, doc_id, doc_title):
    """处理研报并更新知识图谱"""
    kg = KGIntegration()
    
    # 提取实体和关系
    result = kg.process_feishu_document(doc_content, doc_id, doc_title)
    
    # 生成可视化
    kg.visualizer.render_subgraph(
        center_node=f"report_{doc_id}",
        depth=1
    )
    
    return result

# 使用示例
result = process_report_for_kg(
    doc_content="高盛周报内容...",
    doc_id="gs_20260503",
    doc_title="高盛美股周报"
)
```

---

## 📈 查看统计

```python
# 获取知识图谱统计信息
stats = kg.kg.get_stats()

print(f"实体总数: {stats['total_entities']}")
print(f"关系总数: {stats['total_relations']}")
print(f"实体类型分布: {stats['entity_types']}")
print(f"关系类型分布: {stats['relation_types']}")
```

---

## 📄 导出报告

```python
# 导出知识图谱报告
report_path = kg.export_report("kg_report_20260503.json")

# 报告内容包括:
# - 图谱统计
# - 实体分布
# - 关系分布
# - PageRank中心性Top 10
```

---

## 🔧 CLI命令行

```bash
# 生成可视化
cd /workspace/projects/workspace/skills/knowledge-graph
python kg_integration.py --visualize

# 导出报告
python kg_integration.py --report

# 查询
python kg_integration.py --query related --entity stock_NVDA
```

---

## 💡 最佳实践

### 1. 定期更新

建议每周运行一次更新，处理本周新归档的研报：

```python
# 在周会前更新知识图谱
documents = fetch_this_week_reports()  # 获取本周研报
kg.weekly_update(documents)
```

### 2. 结合投资分析

在分析个股时，先查询知识图谱获取关联信息：

```python
def analyze_stock_with_kg(stock_code):
    # 1. 获取基础信息
    stock_info = get_stock_info(stock_code)
    
    # 2. 查询知识图谱
    kg_analysis = analyze_stock(stock_code)
    
    # 3. 综合分析
    return {
        'stock': stock_info,
        'kg_analysis': kg_analysis,
        'recommendation': generate_recommendation(stock_info, kg_analysis)
    }
```

### 3. 发现隐藏关系

利用路径查找发现间接关联：

```python
# 查找NVIDIA和特斯拉的隐藏关联
paths = kg.kg.find_path("stock_NVDA", "stock_TSLA", max_depth=3)

if paths:
    print(f"发现 {len(paths)} 条关联路径:")
    for path in paths:
        print(path)
else:
    print("未发现直接关联")
```

---

## 📞 获取帮助

查看设计文档：
```bash
cat /workspace/projects/workspace/skills/knowledge-graph/SKILL.md
```

运行测试：
```bash
cd /workspace/projects/workspace/skills/knowledge-graph
python knowledge_graph_core.py  # 测试基础框架
python entity_extractor.py      # 测试实体提取
python relation_builder.py      # 测试关系构建
python visualizer.py            # 测试可视化
```

---

**开始使用知识图谱，让投资决策更有依据！** 🚀
