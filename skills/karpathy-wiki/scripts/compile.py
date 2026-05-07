#!/usr/bin/env python3
"""
Karpathy Wiki - 信息源摄入与编译脚本
基于Andrej Karpathy的Compilation-over-Retrieval理念
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

WIKI_ROOT = Path(__file__).parent.parent
WIKI_DIR = WIKI_ROOT / "wiki"
SOURCES_DIR = WIKI_ROOT / "sources"
TEMPLATES_DIR = WIKI_ROOT / "templates"

def ensure_dirs():
    """确保所有目录存在"""
    dirs = [
        WIKI_DIR / "concepts",
        WIKI_DIR / "companies", 
        WIKI_DIR / "industries",
        WIKI_DIR / "people",
        WIKI_DIR / "events",
        SOURCES_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

def compile_sources(date_str=None):
    """
    编译指定日期的信息源
    如果date_str为None，编译所有未处理的源
    """
    if date_str:
        source_dir = SOURCES_DIR / date_str
        if not source_dir.exists():
            print(f"❌ 未找到信息源: {source_dir}")
            return
        
        print(f"📁 编译信息源: {date_str}")
        # TODO: 实现具体的编译逻辑
        # 1. 读取所有源文件
        # 2. 提取实体和关系
        # 3. 生成/更新wiki页面
        # 4. 建立交叉引用
        
    else:
        # 查找所有未编译的源
        print("🔍 扫描所有信息源...")
        for date_dir in sorted(SOURCES_DIR.iterdir()):
            if date_dir.is_dir():
                print(f"  📅 发现: {date_dir.name}")

def update_index():
    """更新全局索引"""
    index_file = WIKI_DIR / "_index.md"
    
    content = """# Karpathy Wiki - 知识库索引

> **最后更新**: {date}

---

## 📊 统计

| 类别 | 数量 |
|:-----|:----:|
| 概念 | {concept_count} |
| 公司 | {company_count} |
| 行业 | {industry_count} |
| 人物 | {person_count} |
| 事件 | {event_count} |

---

## 🔍 快速导航

### 概念
{concept_links}

### 公司
{company_links}

### 行业
{industry_links}

### 近期事件
{event_links}

---

## ⏰ 时间线

查看最新动态: [[_timeline]]
""".format(
        date=datetime.now().strftime("%Y-%m-%d"),
        concept_count=len(list((WIKI_DIR / "concepts").glob("*.md"))),
        company_count=len(list((WIKI_DIR / "companies").glob("*.md"))),
        industry_count=len(list((WIKI_DIR / "industries").glob("*.md"))),
        person_count=len(list((WIKI_DIR / "people").glob("*.md"))),
        event_count=len(list((WIKI_DIR / "events").glob("*.md"))),
        concept_links="\n".join([f"- [[{f.stem}]]" for f in sorted((WIKI_DIR / "concepts").glob("*.md"))][:10]),
        company_links="\n".join([f"- [[{f.stem}]]" for f in sorted((WIKI_DIR / "companies").glob("*.md"))][:10]),
        industry_links="\n".join([f"- [[{f.stem}]]" for f in sorted((WIKI_DIR / "industries").glob("*.md"))][:10]),
        event_links="\n".join([f"- [[{f.stem}]]" for f in sorted((WIKI_DIR / "events").glob("*.md"), reverse=True)][:10]),
    )
    
    index_file.write_text(content, encoding='utf-8')
    print(f"✅ 索引已更新: {index_file}")

def main():
    ensure_dirs()
    
    if len(sys.argv) < 2:
        print("""
Karpathy Wiki - 编译脚本

用法:
  python3 compile.py all          # 编译所有信息源
  python3 compile.py 2026-05-08   # 编译指定日期
  python3 compile.py index        # 仅更新索引
        """)
        return
    
    command = sys.argv[1]
    
    if command == "all":
        compile_sources()
        update_index()
    elif command == "index":
        update_index()
    elif len(command) == 10 and command.count("-") == 2:  # 日期格式 YYYY-MM-DD
        compile_sources(command)
        update_index()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()
