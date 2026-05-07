#!/usr/bin/env python3
"""
KW-Feishu 双向联动引擎 v1.0
实现本地wiki与飞书云文档的深度集成

核心功能:
1. KW → 飞书: 自动推送成熟知识到飞书归档
2. 飞书 → KW: 提取飞书文档关键insight回流到本地
3. 统一索引: 跨平台一站式检索
4. 链接映射: 双向引用建立
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

class KWFeishuIntegrationEngine:
    """KW-Feishu联动引擎"""
    
    def __init__(self, workspace="/workspace/projects/workspace"):
        self.workspace = Path(workspace)
        self.kw_dir = self.workspace / "skills/karpathy-wiki"
        self.feishu_export_dir = self.workspace / "data/feishu_export"
        self.link_map_file = self.workspace / "memory/kw_feishu_link_map.json"
        
        self.feishu_export_dir.mkdir(parents=True, exist_ok=True)
    
    def kw_to_feishu(self, wiki_page, feishu_folder="20_个股档案"):
        """
        KW页面 → 飞书文档
        
        Args:
            wiki_page: wiki页面路径 (如 "wiki/companies/中国长城.md")
            feishu_folder: 飞书目标文件夹
        
        Returns:
            生成的飞书文档路径
        """
        page_path = self.kw_dir / wiki_page
        if not page_path.exists():
            print(f"❌ Wiki页面不存在: {page_path}")
            return None
        
        # 读取wiki内容
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 转换格式 (markdown → 飞书兼容)
        feishu_content = self._convert_to_feishu_format(content, wiki_page)
        
        # 生成文件名
        page_name = page_path.stem
        date_str = datetime.now().strftime("%Y%m%d")
        
        if "companies" in wiki_page:
            feishu_title = f"个股分析_{date_str}_{page_name}"
        elif "events" in wiki_page:
            feishu_title = f"事件分析_{date_str}_{page_name}"
        elif "concepts" in wiki_page:
            feishu_title = f"概念研究_{date_str}_{page_name}"
        else:
            feishu_title = f"知识归档_{date_str}_{page_name}"
        
        # 保存到导出目录
        export_file = self.feishu_export_dir / f"{feishu_title}.md"
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(feishu_content)
        
        # 记录链接映射
        self._update_link_map(wiki_page, feishu_title, feishu_folder)
        
        print(f"✅ KW → 飞书: {wiki_page}")
        print(f"   导出文件: {export_file}")
        print(f"   飞书标题: {feishu_title}")
        print(f"   目标位置: 空间2/{feishu_folder}/")
        
        return export_file
    
    def _convert_to_feishu_format(self, wiki_content, wiki_path):
        """转换为飞书格式"""
        # 替换wiki链接 [[xxx]] 为飞书格式
        content = wiki_content
        
        # [[公司/中国长城]] → [中国长城](kw:companies/中国长城)
        content = re.sub(
            r'\[\[公司/([^\]]+)\]\]',
            r'[\1](kw:companies/\1)',
            content
        )
        
        # [[事件/xxx]] → [xxx](kw:events/xxx)
        content = re.sub(
            r'\[\[事件/([^\]]+)\]\]',
            r'[\1](kw:events/\1)',
            content
        )
        
        # [[概念/xxx]] → [xxx](kw:concepts/xxx)
        content = re.sub(
            r'\[\[概念/([^\]]+)\]\]',
            r'[\1](kw:concepts/\1)',
            content
        )
        
        # 添加来源标注
        header = f"""> 📚 **来源**: Karpathy Wiki  
> **原始页面**: `{wiki_path}`  
> **编译时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
> **更新方式**: 系统自动同步

---

"""
        
        return header + content
    
    def extract_from_feishu(self, feishu_doc_path, extract_type="insight"):
        """
        从飞书文档提取关键信息 → KW
        
        Args:
            feishu_doc_path: 飞书文档路径
            extract_type: 提取类型 (insight/entity/event)
        
        Returns:
            提取的内容块列表
        """
        # 读取飞书文档 (假设已下载到本地)
        doc_path = Path(feishu_doc_path)
        if not doc_path.exists():
            print(f"❌ 飞书文档不存在: {doc_path}")
            return []
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取关键段落 (标记为 💡 或 📌 的部分)
        insights = []
        
        # 匹配 💡 开头的段落
        insight_pattern = r'💡\s*([^\n]+(?:\n(?![💡📌#])[^\n]+)*)'
        for match in re.finditer(insight_pattern, content):
            insights.append({
                "type": "insight",
                "content": match.group(1).strip(),
                "source": doc_path.name
            })
        
        # 匹配 📌 开头的段落
        highlight_pattern = r'📌\s*([^\n]+(?:\n(?![💡📌#])[^\n]+)*)'
        for match in re.finditer(highlight_pattern, content):
            insights.append({
                "type": "highlight",
                "content": match.group(1).strip(),
                "source": doc_path.name
            })
        
        print(f"✅ 飞书 → KW: 从 {doc_path.name} 提取 {len(insights)} 条insight")
        
        # 保存到KW sources目录
        if insights:
            self._save_insights_to_kw(insights, doc_path.stem)
        
        return insights
    
    def _save_insights_to_kw(self, insights, source_name):
        """保存提取的insight到KW sources"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        source_dir = self.kw_dir / f"sources/{date_str}"
        source_dir.mkdir(parents=True, exist_ok=True)
        
        insights_file = source_dir / f"feishu_extract_{source_name}.json"
        with open(insights_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        print(f"   保存到: {insights_file}")
    
    def _update_link_map(self, wiki_page, feishu_title, feishu_folder):
        """更新链接映射"""
        if self.link_map_file.exists():
            with open(self.link_map_file, 'r', encoding='utf-8') as f:
                link_map = json.load(f)
        else:
            link_map = {"kw_to_feishu": [], "feishu_to_kw": []}
        
        link_map["kw_to_feishu"].append({
            "wiki_page": str(wiki_page),
            "feishu_title": feishu_title,
            "feishu_folder": feishu_folder,
            "sync_time": datetime.now().isoformat()
        })
        
        with open(self.link_map_file, 'w', encoding='utf-8') as f:
            json.dump(link_map, f, indent=2, ensure_ascii=False)
    
    def sync_all_companies(self):
        """同步所有公司页面到飞书"""
        companies_dir = self.kw_dir / "wiki/companies"
        if not companies_dir.exists():
            print("❌ 公司目录不存在")
            return
        
        print("🚀 批量同步公司页面到飞书...")
        for company_file in companies_dir.glob("*.md"):
            wiki_path = f"wiki/companies/{company_file.name}"
            self.kw_to_feishu(wiki_path, "20_个股档案")
        
        print(f"\n✅ 同步完成: 共 {len(list(companies_dir.glob('*.md')))} 个公司")
    
    def unified_search(self, keyword):
        """
        统一搜索 (本地KW + 飞书映射)
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            搜索结果列表
        """
        results = []
        
        # 1. 搜索本地KW
        wiki_dir = self.kw_dir / "wiki"
        for md_file in wiki_dir.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if keyword in content:
                results.append({
                    "source": "KW",
                    "type": "wiki",
                    "path": str(md_file.relative_to(self.kw_dir)),
                    "title": md_file.stem
                })
        
        # 2. 搜索飞书映射
        if self.link_map_file.exists():
            with open(self.link_map_file, 'r', encoding='utf-8') as f:
                link_map = json.load(f)
            for link in link_map.get("kw_to_feishu", []):
                if keyword in link["feishu_title"]:
                    results.append({
                        "source": "Feishu",
                        "type": "archived_doc",
                        "title": link["feishu_title"],
                        "folder": link["feishu_folder"]
                    })
        
        print(f"🔍 统一搜索结果: '{keyword}'")
        print(f"   本地KW: {sum(1 for r in results if r['source']=='KW')} 条")
        print(f"   飞书: {sum(1 for r in results if r['source']=='Feishu')} 条")
        
        return results
    
    def show_link_map(self):
        """显示当前链接映射"""
        if not self.link_map_file.exists():
            print("📭 暂无链接映射")
            return
        
        with open(self.link_map_file, 'r', encoding='utf-8') as f:
            link_map = json.load(f)
        
        print("🔗 KW ↔ 飞书 链接映射")
        print("=" * 60)
        
        print(f"\nKW → 飞书 ({len(link_map.get('kw_to_feishu', []))}条):")
        for link in link_map.get("kw_to_feishu", []):
            print(f"   • {link['wiki_page']} → 空间2/{link['feishu_folder']}/{link['feishu_title']}")

def main():
    engine = KWFeishuIntegrationEngine()
    
    import sys
    if len(sys.argv) < 2:
        print("""
KW-Feishu 联动引擎

用法:
  python3 kw_feishu_engine.py sync <wiki_page> [folder]  # 同步单个页面
  python3 kw_feishu_engine.py sync-all                   # 同步所有公司
  python3 kw_feishu_engine.py extract <feishu_doc>       # 提取insight
  python3 kw_feishu_engine.py search <keyword>           # 统一搜索
  python3 kw_feishu_engine.py map                        # 显示链接映射
        """)
        return
    
    command = sys.argv[1]
    
    if command == "sync" and len(sys.argv) >= 3:
        wiki_page = sys.argv[2]
        folder = sys.argv[3] if len(sys.argv) >= 4 else "20_个股档案"
        engine.kw_to_feishu(wiki_page, folder)
    
    elif command == "sync-all":
        engine.sync_all_companies()
    
    elif command == "extract" and len(sys.argv) >= 3:
        feishu_doc = sys.argv[2]
        engine.extract_from_feishu(feishu_doc)
    
    elif command == "search" and len(sys.argv) >= 3:
        keyword = sys.argv[2]
        engine.unified_search(keyword)
    
    elif command == "map":
        engine.show_link_map()
    
    else:
        print("❌ 未知命令")

if __name__ == "__main__":
    main()
