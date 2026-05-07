# Karpathy Wiki - Compilation-over-Retrieval Knowledge System

> **版本**: v1.0.0  
> **创建时间**: 2026-05-08  
> **模式来源**: Andrej Karpathy's LLM Wiki Pattern  
> **框架层级**: A5L Layer 3 知识管理层

**描述**: 基于Andrej Karpathy的"Compilation-over-Retrieval"理念构建的知识 wiki 系统。将零散的信息源（研报、新闻、聊天记录）自动编译成结构化、交叉引用的知识页面。知识通过持续积累而非消失，形成复利效应。替代简单的RAG检索，实现真正的知识沉淀。

---

## 🎯 核心理念

> **"Don't retrieve, compile."** — Andrej Karpathy

传统RAG的问题：
- 每次查询独立，知识不积累
- 重复处理相同信息源
- 缺乏跨文档的关联和洞察

Karpathy Wiki的解决：
- 信息源一旦摄入，永久转化为结构化知识
- 新知识自动关联现有知识网络
- 知识像复利一样持续增长

---

## 📁 系统架构

```
karpathy-wiki/
├── SKILL.md                    # 本文件
├── wiki/                       # 编译后的知识库
│   ├── _index.md              # 知识库总目录
│   ├── _concepts_index.md     # 概念索引
│   ├── _timeline.md           # 时间线视图
│   ├── concepts/              # 概念页面
│   │   ├── catalyst_tier_framework.md
│   │   ├── cpu_server_cycle.md
│   │   └── ...
│   ├── companies/             # 公司页面
│   │   ├── amd.md
│   │   ├── nvidia.md
│   │   └── ...
│   ├── industries/            # 行业页面
│   │   ├── ai_computing.md
│   │   ├── semiconductors.md
│   │   └── ...
│   ├── people/                # 人物/角色页面
│   │   ├── jie_ge.md
│   │   └── ...
│   └── events/                # 事件页面
│       ├── 2026-05-06_cpu_tam_doubling.md
│       └── ...
├── sources/                    # 原始信息源（只读归档）
│   ├── 2026-05-08/
│   │   ├── gs_us_equities_weekly.pdf
│   │   └── amd_earnings_call.txt
│   └── ...
├── templates/                  # 页面模板
│   ├── concept_template.md
│   ├── company_template.md
│   ├── industry_template.md
│   └── event_template.md
└── scripts/                    # 自动化脚本
    ├── ingest.py              # 信息源摄入
    ├── compile.py             # 编译生成wiki页面
    ├── link.py                # 自动建立交叉引用
    └── update_index.py        # 更新索引
```

---

## 🔄 工作流程

### 1. 信息源摄入 (Ingest)

将原始信息源放入 `sources/YYYY-MM-DD/` 目录：
- PDF研报
- 新闻文章
- 聊天记录
- 音频转录
- 视频字幕
- 任何文本内容

### 2. 知识编译 (Compile)

运行编译脚本，将原始信息转化为结构化页面：

```bash
python3 skills/karpathy-wiki/scripts/compile.py
```

编译过程：
1. **实体提取** - 识别公司、人物、概念、事件
2. **关系映射** - 建立实体间的关联
3. **摘要生成** - 提取核心观点和证据
4. **冲突检测** - 标记信息源中的矛盾点
5. **页面生成** - 创建/更新wiki页面

### 3. 交叉引用 (Link)

自动在页面间建立双向链接：

```markdown
AMD在[[公司/AMD]]页中被讨论，
同时出现在[[概念/CPU服务器大周期]]和[[行业/AI算力]]中。
```

### 4. 索引更新 (Index)

更新全局索引，确保可发现性：
- 按时间线浏览
- 按概念网络浏览
- 按相关度搜索

---

## 📄 页面类型

### 概念页面 (Concept)

定义：抽象的投资概念、框架、模式

示例：
- [[概念/催化剂层级框架]]
- [[概念/一致性高潮]]
- [[概念/预期差识别]]

模板结构：
```markdown
# 概念名称

## 定义
简明扼要的定义

## 核心要素
- 要素1
- 要素2

## 实战应用
具体投资场景中的应用

## 相关概念
- [[概念/相关概念1]]
- [[概念/相关概念2]]

## 信息源
- [研报标题](sources/日期/文件名.pdf)
- [新闻标题](sources/日期/新闻.md)

## 更新历史
- 2026-05-08: 初始版本，基于...创建
```

### 公司页面 (Company)

定义：具体上市公司的深度档案

示例：
- [[公司/AMD]]
- [[公司/中国长城]]
- [[公司/盈峰环境]]

模板结构：
```markdown
# 公司名称 (股票代码)

## 基本信息
- 行业: 
- 市值: 
- 主要业务: 

## 投资逻辑
### 看多逻辑
### 看空逻辑

## 关键催化
- [[事件/催化事件1]]
- [[事件/催化事件2]]

## 持仓关联
- 张晋账户: X股
- 模拟盘: X股

## 相关概念
- [[概念/相关概念]]

## 更新历史
```

### 行业页面 (Industry)

定义：产业链全景分析

示例：
- [[行业/AI算力]]
- [[行业/半导体设备]]
- [[行业/光模块]]

### 事件页面 (Event)

定义：具体的投资催化事件

示例：
- [[事件/2026-05-06_AMD_CPU_TAM翻倍]]
- [[事件/2026-05-07_盈峰环境2连板]]

### 人物页面 (Person)

定义：关键人物、角色、交易者

示例：
- [[人物/杰哥]]
- [[人物/首席]]

---

## 🚀 使用示例

### 示例1: 摄入研报

```bash
# 1. 将研报放入sources目录
cp "高盛美股周报.pdf" skills/karpathy-wiki/sources/2026-05-08/

# 2. 运行编译
python3 skills/karpathy-wiki/scripts/compile.py

# 3. 查看生成的页面
cat skills/karpathy-wiki/wiki/concepts/ai_cycle.md
```

### 示例2: 查询知识

```markdown
问题: "当前AI算力产业链的投资逻辑是什么？"

查询路径:
1. 打开 [[行业/AI算力]]
2. 查看关联概念:
   - [[概念/CPU服务器大周期]] (Tier 1)
   - [[概念/存储超级周期]] (Tier 2)
   - [[概念/光模块涨价]] (Tier 2)
3. 查看持仓关联:
   - [[公司/中国长城]] - 张晋账户48,000股
   - [[公司/AMD]] - 模拟盘22股
4. 查看最新事件:
   - [[事件/2026-05-06_AMD_CPU_TAM翻倍]]
```

### 示例3: 更新现有页面

新信息源自动关联到现有页面：

```markdown
# 概念/CPU服务器大周期

## 新增催化 (2026-05-08)
根据[[事件/2026-05-07_中国长城4连板]]，
AMD服务器CPU TAM翻倍催化持续验证...

## 更新关联
- 新增关联: [[公司/盈峰环境]] (智算转型)
- 新增关联: [[概念/催化剂层级框架]]
```

---

## 🔄 与现有系统集成

### 与CTF框架集成

```
[[概念/催化剂层级框架]]
├── Tier 1: [[概念/CPU服务器大周期]]
│   └── [[公司/中国长城]]
├── Tier 2: [[概念/存储超级周期]]
│   └── [[公司/闪迪]]
└── ...
```

### 与Knowledge Guardian集成

KG负责：
- 信息源归档 (sources/)
- 触发编译流程
- 审核知识质量

Karpathy Wiki负责：
- 结构化知识生成 (wiki/)
- 交叉引用建立
- 知识网络维护

### 与Report Manager集成

研报阅读 → 自动摄入 → 编译为wiki页面 → 关联相关持仓/概念

---

## 📊 与简单RAG对比

| 维度 | 简单RAG | Karpathy Wiki |
|:-----|:--------|:--------------|
| 知识积累 | ❌ 每次重新检索 | ✅ 编译后永久保存 |
| 结构化 | ❌ 原始文本 | ✅ 实体-关系-摘要 |
| 交叉引用 | ❌ 无 | ✅ 自动双向链接 |
| 冲突检测 | ❌ 无 | ✅ 多源对比标记 |
| 版本历史 | ❌ 无 | ✅ 更新历史追踪 |
| 发现性 | ❌ 依赖查询 | ✅ 索引+网络浏览 |

---

## 🏷️ 标签

#karpathy-wiki #知识管理 #compilation-over-retrieval #知识复利 #wiki-system #layer3

---

> **Chief指导**: *"知识应该像投资一样产生复利，而不是每次都从零开始。"*
