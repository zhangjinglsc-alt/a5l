# A5L 知识图谱构建工具 v1.0

**SKILL名称**: knowledge-graph  
**层级**: Layer2 - Strategy Engine（交易策略层）  
**目录**: `/skills/knowledge-graph/`  
**版本**: v1.0  
**状态**: ✅ Phase 1完成，Phase 2开发中  
**优先级**: P0 - 立即开发

---

## 🎯 功能概述

从A5L归档的研报、文档、投资记录中提取实体和关系，构建投资知识图谱，支持关联分析和可视化。

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│  Input Layer - 数据源                                        │
│  - 飞书知识库文档 (空间2)                                     │
│  - 研报批注                                                  │
│  - 投资记录                                                  │
│  - 新闻资讯                                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Extraction Layer - 实体关系提取                             │
│  - 命名实体识别 (NER)                                        │
│  - 关系抽取                                                  │
│  - 实体链接/消歧                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Graph Layer - 图存储                                        │
│  - 实体节点库                                                │
│  - 关系边库                                                  │
│  - 图数据库 (NetworkX)                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Application Layer - 应用接口                                │
│  - 关联查询 API                                              │
│  - 路径分析                                                  │
│  - 可视化展示                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 实体类型

| 实体类型 | 示例 | 属性 |
|----------|------|------|
| **Stock** | NVDA, 中国长城 | 代码、名称、行业、市值 |
| **Industry** | 半导体, AI算力 | 名称、产业链位置 |
| **Concept** | ChatGPT, 国产替代 | 名称、热度、关联股票 |
| **Event** | 美联储议息, 财报季 | 名称、时间、影响 |
| **Person** | 黄仁勋, 巴菲特 | 姓名、职位、关联公司 |
| **Report** | 高盛周报, 行业研报 | 标题、日期、来源 |

---

## 🔗 关系类型

| 关系类型 | 示例 | 说明 |
|----------|------|------|
| **belongs_to** | NVDA → 半导体 | 股票属于行业 |
| **industry_chain** | 中芯国际 → 上游 → 阿斯麦 | 产业链上下游 |
| **competes_with** | NVDA ↔ AMD | 竞争关系 |
| **correlates_with** | 中国长城 ↔ 信创概念 | 概念关联 |
| **affected_by** | 科技股 → 美联储政策 | 事件影响 |
| **mentioned_in** | NVDA → 高盛周报 | 文档提及 |
| **holds** | A5L → NVDA | 持仓关系 |

---

## 🛠️ 核心模块

### 1. 实体提取器 (entity_extractor.py)

```python
class EntityExtractor:
    def extract_from_text(self, text: str) -> List[Entity]:
        """从文本中提取实体"""
        pass
    
    def extract_from_document(self, doc_id: str) -> List[Entity]:
        """从飞书文档中提取实体"""
        pass
```

### 2. 关系构建器 (relation_builder.py)

```python
class RelationBuilder:
    def build_industry_chain(self) -> List[Relation]:
        """构建产业链关系"""
        pass
    
    def build_correlations(self) -> List[Relation]:
        """构建股票关联关系"""
        pass
```

### 3. 图谱存储 (graph_store.py)

```python
class GraphStore:
    def add_entity(self, entity: Entity) -> None:
        pass
    
    def add_relation(self, relation: Relation) -> None:
        pass
    
    def query_related(self, entity_id: str, depth: int = 2) -> Graph:
        """查询关联实体"""
        pass
```

### 4. 可视化 (visualizer.py)

```python
class KGVisualizer:
    def render_graph(self, graph: Graph, output_path: str) -> None:
        """渲染图谱为HTML/图片"""
        pass
    
    def render_path(self, start: str, end: str) -> None:
        """渲染两点间的路径"""
        pass
```

---

## 📡 API接口

### 供其他SKILL调用

```python
# 获取关联股票
get_related_stocks(stock_code: str, relation_type: str = "all") -> List[str]

# 获取产业链
get_industry_chain(stock_code: str, direction: str = "both") -> Dict

# 获取概念关联
get_concept_stocks(concept: str) -> List[str]

# 获取事件影响
get_event_impact(event_id: str) -> Dict

# 路径分析
find_path(start: str, end: str, max_depth: int = 3) -> List[Path]

# 可视化
visualize_subgraph(center: str, depth: int = 2, output: str = "html")
```

---

## 📊 输出示例

### 实体查询结果

```json
{
  "entity": {
    "id": "stock_NVDA",
    "type": "Stock",
    "name": "NVIDIA",
    "code": "NVDA",
    "industry": "半导体",
    "market_cap": "2.3T"
  },
  "relations": [
    {"type": "belongs_to", "target": "industry_semiconductor"},
    {"type": "competes_with", "target": "stock_AMD"},
    {"type": "correlates_with", "target": "concept_AI"},
    {"type": "mentioned_in", "target": "report_gs_20260503"}
  ]
}
```

### 产业链图谱

```
阿斯麦 (光刻机) → 台积电 (代工) → NVIDIA (设计) → 数据中心
     ↑                                              ↓
中芯国际 (追赶)                                  AI应用
```

---

## 🔄 更新流程

### 周度更新（每周日22:00）

1. **增量提取**: 从本周新归档文档提取实体关系
2. **实体消歧**: 解决新增实体与已有实体的歧义
3. **关系更新**: 更新实体间关系（新增/删除/修改）
4. **图谱生成**: 生成最新可视化图谱
5. **质量检查**: 检查图谱完整性和一致性

### 实时更新（可选）

- 重大事件发生时立即更新
- 新持仓建立时更新

---

## 📈 应用场景

### 1. 选股辅助
```
输入: 中国长城
输出: 关联股票[浪潮信息, 中科曙光], 关联概念[信创, 国产替代]
→ 发现整个信创板块机会
```

### 2. 风险识别
```
输入: NVDA
输出: 依赖供应商[台积电], 竞争[AMD, Intel], 政策风险[出口管制]
→ 识别供应链风险
```

### 3. 产业链分析
```
输入: AI算力
输出: 上游[芯片设计], 中游[代工], 下游[数据中心, AI应用]
→ 找到产业链各环节机会
```

### 4. 事件影响
```
输入: 美联储降息
输出: 影响[科技股↑, 银行股↓, 黄金↑]
→ 提前布局受益板块
```

---

## 📝 开发计划

### Phase 1: 基础功能 (1-2周)
- [ ] 实体提取器（基于规则+关键词）
- [ ] 基础关系构建
- [ ] 图存储（NetworkX）
- [ ] 简单可视化

### Phase 2: 智能提取 (2-3周)
- [ ] 集成LLM进行实体识别
- [ ] 关系抽取优化
- [ ] 实体消歧
- [ ] 自动化更新流程

### Phase 3: 高级功能 (3-4周)
- [ ] 路径分析算法
- [ ] 知识推理
- [ ] 交互式可视化
- [ ] API接口完善

---

## 🎯 待决策事项

1. **层级归属**: Layer2(策略层) vs Layer3(分析层)?
2. **开发优先级**: 立即开发 / 本月开发 / 下月开发?
3. **技术选型**: NetworkX vs Neo4j vs 其他?
4. **数据源**: 先支持哪些数据源?

---

*本设计文档待Chief Architect和Knowledge Guardian决策后启动开发*
