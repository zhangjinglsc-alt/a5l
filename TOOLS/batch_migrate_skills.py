#!/usr/bin/env python3
"""
A5L-Prime 批量迁移工具
将76个SKILL迁移为Prime Atom格式
"""

import json
import re
from pathlib import Path
from typing import Dict, List
from prime_poc import PrimeAtom, A5LKnowledgeGraph  # 复用POC的基础类


def extract_skill_info(skill_path: Path) -> Dict:
    """从SKILL.md提取关键信息"""
    content = skill_path.read_text(encoding='utf-8')
    
    # 提取名称（从文件名或第一行）
    skill_name = skill_path.parent.name
    
    # 提取描述（从description或第一段）
    description = ""
    if "description:" in content:
        match = re.search(r'description:\s*([^\n]+)', content)
        if match:
            description = match.group(1).strip()
    
    if not description:
        # 取第一段非空行
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        for line in lines:
            if not line.startswith('#') and not line.startswith('---'):
                description = line[:200]
                break
    
    # 判断SKILL类型
    kind = "tool"
    if "data" in skill_name or "source" in skill_name:
        kind = "data"
    elif "strategy" in skill_name:
        kind = "strategy"
    elif "analysis" in skill_name or "analy" in skill_name:
        kind = "analysis"
    elif "memory" in skill_name or "storage" in skill_name:
        kind = "memory"
    elif "risk" in skill_name or "guard" in skill_name:
        kind = "risk-control"
    
    # 判断领域
    domain = "general"
    if any(x in skill_name for x in ["invest", "stock", "factor", "value", "buffett"]):
        domain = "investment-analysis"
    elif any(x in skill_name for x in ["ai", "llm", "manufacturing", "embodied", "storage", "cooling"]):
        domain = "ai-industry"
    elif any(x in skill_name for x in ["memory", "dream", "palace"]):
        domain = "memory-system"
    elif any(x in skill_name for x in ["architect", "a5l", "layer", "orchestrator"]):
        domain = "a5l-core"
    elif any(x in skill_name for x in ["backtest", "trade", "signal", "market"]):
        domain = "trading"
    elif any(x in skill_name for x in ["feishu", "lark", "msg", "message"]):
        domain = "integration"
    
    # 提取触发词
    trigger_words = []
    if "## 使用方法" in content or "## Usage" in content:
        section = re.search(r'## 使用方法.*?(?=##|$)', content, re.DOTALL)
        if section:
            triggers = re.findall(r'`([^`]+)`', section.group())
            trigger_words.extend(triggers[:5])  # 最多5个
    
    return {
        "name": skill_name,
        "description": description,
        "kind": kind,
        "domain": domain,
        "trigger_words": trigger_words,
        "raw_content": content
    }


def infer_dependencies(skill_info: Dict, all_skills: Dict[str, Dict]) -> List[str]:
    """推断SKILL依赖关系"""
    deps = []
    content = skill_info["raw_content"].lower()
    
    # 关键词映射到依赖
    dep_keywords = {
        "stock-data": ["股票数据", "股价", "行情", "akshare", "tushare"],
        "backtest-engine": ["回测", "backtest", "策略回测"],
        "factor-investing": ["因子", "factor", "多因子"],
        "technical-analysis": ["技术指标", "macd", "rsi", "k线"],
        "fundamental-analysis": ["基本面", "财报", "财务数据"],
        "memory-palace": ["memory", "记忆", "记住"],
        "knowledge-graph": ["知识图谱", "kg", "entity"],
        "feishu-api": ["feishu", "飞书", "lark"],
        "messaging": ["message", "消息", "通知"],
    }
    
    for dep_name, keywords in dep_keywords.items():
        if any(kw in content for kw in keywords):
            dep_id = f"@a5l/skill-{dep_name}"
            if dep_id != f"@a5l/skill-{skill_info['name']}":
                deps.append(dep_id)
    
    return deps[:5]  # 最多5个依赖


def infer_enhancements(skill_info: Dict) -> List[str]:
    """推断SKILL增强的能力"""
    enhances = []
    content = skill_info["raw_content"].lower()
    
    if "回测" in content or "backtest" in content:
        enhances.append("@a5l/strategy-validation")
    
    if "因子" in content or "factor" in content:
        enhances.append("@a5l/portfolio-construction")
    
    if "ai" in content or "分析" in content:
        enhances.append("@a5l/decision-support")
    
    return enhances


def batch_migrate_skills():
    """批量迁移所有SKILL"""
    
    print("="*70)
    print("🚀 A5L-Prime 批量迁移")
    print("="*70)
    
    skills_dir = Path("/workspace/projects/workspace/skills")
    kg = A5LKnowledgeGraph()
    
    # 扫描所有SKILL
    skill_paths = list(skills_dir.glob("*/SKILL.md"))
    print(f"\n📊 发现 {len(skill_paths)} 个SKILL")
    
    # 第一遍：提取所有SKILL信息
    all_skills: Dict[str, Dict] = {}
    for skill_path in skill_paths:
        info = extract_skill_info(skill_path)
        all_skills[info["name"]] = info
    
    # 第二遍：创建Atom并推断关系
    stats = {"tool": 0, "data": 0, "strategy": 0, "analysis": 0, "memory": 0, "risk-control": 0}
    domain_stats = {}
    
    for skill_name, info in all_skills.items():
        atom_id = f"@a5l/skill-{skill_name}"
        
        atom = PrimeAtom(
            id=atom_id,
            kind=info["kind"],
            version="2.1.0",
            domain=info["domain"]
        )
        
        # 设置内容
        atom.set_content(
            name=skill_name,
            description=info["description"],
            trigger_words=info["trigger_words"],
            source_path=f"skills/{skill_name}/SKILL.md"
        )
        
        # 添加依赖关系
        deps = infer_dependencies(info, all_skills)
        for dep in deps:
            atom.add_edge("requires", dep)
        
        # 添加增强关系
        enhances = infer_enhancements(info)
        for enh in enhances:
            atom.add_edge("enhances", enh)
        
        # 添加相关关系（同domain的其他SKILL）
        for other_name, other_info in all_skills.items():
            if other_name != skill_name and other_info["domain"] == info["domain"]:
                atom.add_edge("related", f"@a5l/skill-{other_name}")
        
        # 保存
        kg.add_atom(atom)
        atom.save()
        
        # 统计
        stats[info["kind"]] = stats.get(info["kind"], 0) + 1
        domain_stats[info["domain"]] = domain_stats.get(info["domain"], 0) + 1
        
        print(f"  ✅ {atom_id}")
    
    # 构建索引
    print("\n📊 构建知识图谱索引...")
    kg.build_index()
    
    # 生成统计报告
    print("\n" + "="*70)
    print("📈 迁移统计")
    print("="*70)
    
    print("\n按类型分布:")
    for kind, count in sorted(stats.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {kind}: {count}")
    
    print("\n按领域分布:")
    for domain, count in sorted(domain_stats.items(), key=lambda x: -x[1]):
        print(f"  {domain}: {count}")
    
    # 保存完整注册表
    registry = {
        "version": "2.1.0-prime",
        "total_atoms": len(kg.atoms),
        "kinds": stats,
        "domains": domain_stats,
        "atoms": {k: v.to_dict() for k, v in kg.atoms.items()},
        "index": kg.index
    }
    
    registry_path = Path("/workspace/projects/workspace/prime-atoms/registry.json")
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"\n💾 完整注册表: {registry_path}")
    print(f"   大小: {registry_path.stat().st_size / 1024:.1f}KB")
    
    print("\n" + "="*70)
    print("✅ 批量迁移完成！")
    print("="*70)
    
    return kg


if __name__ == "__main__":
    kg = batch_migrate_skills()
    
    # 演示查询
    print("\n🔍 查询示例:")
    print(f"  投资分析SKILL: {len(kg.query(domain='investment-analysis'))}个")
    print(f"  数据类SKILL: {len(kg.query(kind='data'))}个")
    
    # 显示依赖关系示例
    print("\n📊 依赖关系示例:")
    sample_atoms = list(kg.atoms.values())[:3]
    for atom in sample_atoms:
        deps = atom.edges.get("requires", [])
        if deps:
            print(f"  {atom.id} -> {deps}")
