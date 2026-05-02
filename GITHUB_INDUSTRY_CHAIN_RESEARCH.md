# 🔍 GitHub产业链分析项目调研报告

**调研时间**: 2026-05-02  
**调研目标**: 寻找成熟的产业链/行业分析开源项目，为A5L产业链分析器提供借鉴  
**调研方式**: GitHub搜索 + 开源社区分析  

---

## 📊 调研总结

直接匹配"产业链分析"的开源项目较少，但找到以下**可借鉴的相关项目**:

| 排名 | 项目 | 相关度 | 可借鉴点 |
|------|------|--------|----------|
| 1 | **NetworkX** | ⭐⭐⭐⭐⭐ | 网络图谱分析，产业链上下游关系建模 |
| 2 | **LangChain** | ⭐⭐⭐⭐ | 知识图谱构建，信息抽取 |
| 3 | **AI Hedge Fund** | ⭐⭐⭐⭐ | 多Agent协作分析架构 |
| 4 | **RAGFlow** | ⭐⭐⭐ | 文档解析与知识提取 |
| 5 | **LlamaIndex** | ⭐⭐⭐ | 知识库构建与检索 |

---

## 🏆 Top 5 可借鉴项目深度分析

### 1. NetworkX - 产业链关系建模神器

**GitHub**: https://github.com/networkx/networkx  
**Star**: 14k+  
**语言**: Python  

**核心能力**:
```python
# 创建产业链网络图
import networkx as nx

# 创建有向图 (上下游关系)
G = nx.DiGraph()

# 添加节点 (公司)
G.add_node("中际旭创", type="CPO", market_cap=1200)
G.add_node("英伟达", type="AI芯片", market_cap=30000)
G.add_node("润泽科技", type="AIDC", market_cap=800)

# 添加边 (供应关系)
G.add_edge("中际旭创", "英伟达", relationship="供应商", weight=0.8)
G.add_edge("润泽科技", "英伟达", relationship="客户", weight=0.6)

# 分析网络指标
print(f"网络密度: {nx.density(G)}")
print(f"中心性: {nx.degree_centrality(G)}")
print(f"关键路径: {nx.shortest_path(G, '中际旭创', '润泽科技')}")
```

**可借鉴点**:
- ✅ 使用**有向图**建模产业链上下游关系
- ✅ **中心性分析**找出产业链核心节点
- ✅ **社区发现**识别产业集群
- ✅ **路径分析**追踪价值链传导

---

### 2. AI Hedge Fund - 多Agent分析架构

**GitHub**: https://github.com/virattt/ai-hedge-fund  
**Star**: 51k+  
**语言**: Python  

**核心架构**:
```
┌─────────────────────────────────────┐
│        AI Hedge Fund Agents         │
├─────────────────────────────────────┤
│  📊 Analyst Agent (分析)            │
│     - 基本面分析                     │
│     - 技术面分析                     │
│     - 情绪分析                       │
├─────────────────────────────────────┤
│  🎯 Strategy Agent (策略)           │
│     - 投资策略制定                   │
│     - 风险评估                       │
├─────────────────────────────────────┤
│  🛡️ Risk Agent (风控)               │
│     - 风险监控                       │
│     - 预警系统                       │
├─────────────────────────────────────┤
│  💼 Portfolio Agent (组合)          │
│     - 仓位管理                       │
│     - 再平衡                         │
└─────────────────────────────────────┘
```

**可借鉴点**:
- ✅ **多Agent协作**模式 (分析师+策略师+风控)
- ✅ **工作流编排** (分析→策略→风控→执行)
- ✅ **决策投票机制** (多Agent共识决策)

---

### 3. LangChain - 知识图谱与信息抽取

**GitHub**: https://github.com/langchain-ai/langchain  
**Star**: 133k+  
**语言**: Python  

**产业链知识图谱构建**:
```python
from langchain import OpenAI, LLMChain, PromptTemplate

# 定义信息抽取模板
industry_template = """
从以下文本中提取产业链信息：

文本: {text}

请提取：
1. 细分领域名称
2. 龙头公司名称
3. 上下游关系
4. 关键技术/产品

以JSON格式输出：
{{
    "sector": "细分领域",
    "companies": ["公司1", "公司2"],
    "upstream": ["上游环节"],
    "downstream": ["下游环节"],
    "key_tech": ["关键技术"]
}}
"""

# 创建抽取链
llm = OpenAI()
prompt = PromptTemplate(template=industry_template, input_variables=["text"])
chain = LLMChain(llm=llm, prompt=prompt)

# 执行抽取
result = chain.run(text="AI算力产业链包括CPO、AI服务器、AI芯片...")
```

**可借鉴点**:
- ✅ **LLM信息抽取** (从文本自动提取结构化数据)
- ✅ **Chain-of-Thought** (分步骤推理)
- ✅ **知识图谱集成** (与Neo4j等图数据库结合)

---

### 4. RAGFlow - 文档解析与知识提取

**GitHub**: https://github.com/infiniflow/ragflow  
**Star**: 75k+  
**语言**: Python  

**核心能力**:
- 📄 **文档解析**: PDF、图片、网页内容提取
- 🔍 **知识检索**: 语义搜索 + 关键词搜索
- 🧠 **知识问答**: 基于检索结果的智能问答

**产业链分析场景**:
```python
# 上传产业链图谱PDF
ragflow.upload("ai_power_industry.pdf")

# 知识问答
answer = ragflow.query("AI算力产业链包含哪些细分领域？")
# 输出: "AI算力产业链包括CPO、AI服务器、AI芯片、存储芯片..."

# 关系提取
entities = ragflow.extract_entities("产业链上下游关系图")
```

**可借鉴点**:
- ✅ **多模态文档解析** (PDF、图片、网页)
- ✅ **实体关系抽取** (公司-产品-关系)
- ✅ **知识库构建** (结构化存储产业链知识)

---

### 5. Neo4j + Python - 图数据库方案

**虽然不是GitHub项目，但是行业标准方案**

**产业链图谱建模**:
```cypher
// 创建公司节点
CREATE (cpo:Company {name: "中际旭创", sector: "CPO", market_cap: 1200})
CREATE (server:Company {name: "浪潮信息", sector: "AI服务器", market_cap: 800})
CREATE (chip:Company {name: "海光信息", sector: "AI芯片", market_cap: 600})

// 创建关系
CREATE (cpo)-[:SUPPLIES {product: "光模块", volume: "高"}]->(server)
CREATE (chip)-[:SUPPLIES {product: "AI芯片", volume: "中"}]->(server)

// 查询上下游
MATCH (c:Company)-[:SUPPLIES]->(target:Company {name: "浪潮信息"})
RETURN c.name as 供应商, c.sector as 细分领域
```

**可借鉴点**:
- ✅ **图数据库存储** (高效的关系查询)
- ✅ **Cypher查询语言** (直观的关系分析)
- ✅ **可视化展示** (Bloom等工具)

---

## 💡 A5L产业链分析器设计建议

基于以上调研，建议A5L产业链分析器采用以下架构：

```
┌─────────────────────────────────────────────────────────────┐
│                 A5L 产业链分析器 (Industry Chain Analyzer)    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📥 输入层                                                   │
│  ├── 图片输入 (产业链图谱截图)                                │
│  ├── PDF输入 (研报中的产业链图)                               │
│  └── 文本输入 (文字描述的产业链信息)                           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🧠 处理层                                                   │
│  ├── OCR识别 (图片文字提取)                                   │
│  ├── LLM抽取 (信息结构化)                                     │
│  │   └── 使用LangChain/OpenAI API                            │
│  └── 关系建模 (NetworkX图构建)                                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 分析层                                                   │
│  ├── 网络分析 (中心性/密度/路径)                              │
│  ├── 估值对比 (PE/PB/PS横向对比)                              │
│  ├── 景气度分析 (上下游传导效应)                               │
│  └── 风险识别 (集中度/依赖度分析)                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  💾 存储层                                                   │
│  ├── KIWI知识归档 (产业链知识沉淀)                            │
│  └── 图数据库存储 (Neo4j/NetworkX)                           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📤 输出层                                                   │
│  ├── 产业链图谱 (可视化展示)                                  │
│  ├── 龙头公司列表 (带估值数据)                                │
│  ├── 投资策略建议 (买入/观望/风险提示)                         │
│  └── KIWI知识归档 (供后续查询)                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 推荐的技术栈

| 功能 | 推荐库 | 理由 |
|------|--------|------|
| **OCR识别** | PaddleOCR / Tesseract | 中文识别准确率高 |
| **信息抽取** | LangChain + OpenAI API | 结构化信息抽取 |
| **图建模** | NetworkX | Python标准库，生态成熟 |
| **图存储** | Neo4j (可选) | 专业图数据库 |
| **可视化** | Pyvis / Plotly | 交互式网络图 |
| **数据获取** | AKShare / Tushare | A股数据接口 |

---

## 🎯 下一步行动

**立即开始开发**: `industry_chain_analyzer.py`

```python
# 核心功能规划
class IndustryChainAnalyzer:
    """
    A5L产业链分析器
    """
    
    def analyze_image(self, image_path: str) -> dict:
        """分析产业链图片"""
        # 1. OCR提取文字
        # 2. LLM结构化
        # 3. 网络建模
        pass
    
    def analyze_pdf(self, pdf_path: str) -> dict:
        """分析研报PDF"""
        # 1. PDF解析
        # 2. 图表提取
        # 3. 信息抽取
        pass
    
    def build_network(self, data: dict) -> nx.DiGraph:
        """构建产业链网络"""
        # 1. 创建有向图
        # 2. 添加节点(公司)
        # 3. 添加边(关系)
        pass
    
    def generate_insights(self, graph: nx.DiGraph) -> dict:
        """生成投资洞察"""
        # 1. 中心性分析
        # 2. 估值对比
        # 3. 风险识别
        pass
```

**测试数据**: 你分享的AI算力产业链图谱 (20大细分领域)

**预期输出**:
```json
{
    "sectors": ["CPO", "AI服务器", "AI芯片", "存储芯片", ...],
    "companies": {
        "CPO": ["中际旭创", "新易盛", "天孚通信"],
        "AI服务器": ["浪潮信息", "工业富联"],
        ...
    },
    "network_metrics": {
        "density": 0.35,
        "central_nodes": ["AI芯片", "AI服务器"],
        "clusters": [...]
    },
    "investment_insights": {
        "recommendation": "重点关注CPO和AI芯片",
        "risks": ["估值偏高", "技术迭代风险"],
        "opportunities": ["国产替代", "AI算力需求爆发"]
    }
}
```

---

## 📚 参考资源

1. **NetworkX文档**: https://networkx.org/documentation/stable/
2. **LangChain文档**: https://python.langchain.com/docs/get_started/introduction
3. **Neo4j图数据库**: https://neo4j.com/developer/python/
4. **PaddleOCR**: https://github.com/PaddlePaddle/PaddleOCR

---

*调研完成时间: 2026-05-02*  
*调研结论: 可以借鉴NetworkX的图分析能力和LangChain的信息抽取能力，开发A5L产业链分析器*
