#!/usr/bin/env python3
"""
A5L-Prime Integration POC
简化版Prime Atom实现，验证概念可行性
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class PrimeAtom:
    """Prime Atom基类 - 模仿Prime System的typed atom"""
    
    def __init__(self, 
                 id: str,
                 kind: str,
                 version: str = "1.0.0",
                 domain: str = "general"):
        self.id = id
        self.kind = kind
        self.version = version
        self.domain = domain
        self.created_at = datetime.now().isoformat()
        self.edges: Dict[str, List[str]] = {
            "requires": [],
            "enhances": [],
            "validates_with": [],
            "contradicts": [],
            "related": [],
            "derived_from": []
        }
        self.content: Dict[str, Any] = {}
    
    def add_edge(self, verb: str, target_id: str):
        """添加边关系"""
        if verb in self.edges:
            self.edges[verb].append(target_id)
        return self
    
    def set_content(self, **kwargs):
        """设置内容字段"""
        self.content.update(kwargs)
        return self
    
    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            "id": self.id,
            "kind": self.kind,
            "version": self.version,
            "domain": self.domain,
            "created_at": self.created_at,
            "edges": self.edges,
            "content": self.content
        }
    
    def save(self, base_path: str = "/workspace/projects/workspace/prime-atoms"):
        """保存到文件"""
        path = Path(base_path) / self.domain / f"{self.id.replace('/', '_')}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        return path


class A5LKnowledgeGraph:
    """A5L知识图谱 - Prime-style实现"""
    
    def __init__(self, base_path: str = "/workspace/projects/workspace/prime-atoms"):
        self.base_path = Path(base_path)
        self.atoms: Dict[str, PrimeAtom] = {}
        self.index: Dict[str, Dict] = {}  # 轻量级索引
    
    def add_atom(self, atom: PrimeAtom):
        """添加原子"""
        self.atoms[atom.id] = atom
        # 更新索引（只存关键元数据）
        self.index[atom.id] = {
            "kind": atom.kind,
            "domain": atom.domain,
            "version": atom.version,
            "edges_count": sum(len(v) for v in atom.edges.values())
        }
    
    def get_atom(self, atom_id: str) -> Optional[PrimeAtom]:
        """懒加载获取原子"""
        if atom_id in self.atoms:
            return self.atoms[atom_id]
        
        # 从文件加载
        for domain_dir in self.base_path.iterdir():
            if domain_dir.is_dir():
                atom_file = domain_dir / f"{atom_id.replace('/', '_')}.json"
                if atom_file.exists():
                    with open(atom_file) as f:
                        data = json.load(f)
                    atom = PrimeAtom(data['id'], data['kind'], data['version'], data['domain'])
                    atom.edges = data.get('edges', {})
                    atom.content = data.get('content', {})
                    self.atoms[atom_id] = atom
                    return atom
        return None
    
    def query(self, kind: Optional[str] = None, domain: Optional[str] = None) -> List[str]:
        """查询原子（基于索引，快速）"""
        results = []
        for atom_id, meta in self.index.items():
            if kind and meta['kind'] != kind:
                continue
            if domain and meta['domain'] != domain:
                continue
            results.append(atom_id)
        return results
    
    def get_dependencies(self, atom_id: str) -> List[str]:
        """获取依赖关系"""
        atom = self.get_atom(atom_id)
        if atom:
            return atom.edges.get("requires", [])
        return []
    
    def get_dependents(self, atom_id: str) -> List[str]:
        """获取被依赖关系（反向查询）"""
        dependents = []
        for other_id, other_atom in self.atoms.items():
            if atom_id in other_atom.edges.get("requires", []):
                dependents.append(other_id)
        return dependents
    
    def build_index(self):
        """构建轻量级索引（~3KB理念）"""
        index_path = self.base_path / "index.json"
        with open(index_path, 'w') as f:
            json.dump(self.index, f, indent=2)
        print(f"索引构建完成: {index_path}")
        print(f"总原子数: {len(self.index)}")
        print(f"索引大小: ~{len(json.dumps(self.index))/1024:.1f}KB")


def migrate_skill_to_atom(skill_name: str, skill_content: str) -> PrimeAtom:
    """将SKILL.md迁移为Prime Atom"""
    
    # 解析SKILL内容（简化版）
    atom = PrimeAtom(
        id=f"@a5l/skill-{skill_name}",
        kind="tool",  # SKILL主要作为工具
        version="2.1.0",
        domain="investment-analysis"
    )
    
    # 从内容提取关键信息
    if "回测" in skill_content:
        atom.add_edge("requires", "@a5l/data-stock-price")
        atom.add_edge("requires", "@a5l/lib-quant")
    
    if "因子" in skill_content:
        atom.add_edge("enhances", "@a5l/strategy-momentum")
        atom.add_edge("enhances", "@a5l/strategy-value")
    
    # 设置内容摘要（非全文，懒加载理念）
    atom.set_content(
        name=skill_name,
        summary=skill_content[:200] + "..." if len(skill_content) > 200 else skill_content,
        trigger_words=["回测", "策略", "因子"],
        interfaces=["run_backtest", "get_signals"]
    )
    
    return atom


if __name__ == "__main__":
    print("="*60)
    print("🚀 A5L-Prime Integration POC")
    print("="*60)
    
    # 1. 创建知识图谱
    kg = A5LKnowledgeGraph()
    
    # 2. 迁移示例SKILL
    print("\n📦 迁移示例SKILL...")
    
    # 模拟回测引擎SKILL
    backtest_skill = """
    统一回测引擎，支持多策略（双均线/RSI/MACD/突破）、
    多数据源（AkShare/TQ/CSV）、回测报告、实盘模拟
    """
    atom1 = migrate_skill_to_atom("backtest-engine", backtest_skill)
    atom1.add_edge("validates_with", "@a5l/test-backtest-accuracy")
    kg.add_atom(atom1)
    atom1.save()
    print(f"✅ {atom1.id}")
    
    # 模拟因子投资SKILL
    factor_skill = """
    量化因子分析，支持价值、成长、动量、质量、低波动因子
    多因子股票筛选、因子回测、组合构建
    """
    atom2 = migrate_skill_to_atom("factor-investing", factor_skill)
    atom2.add_edge("requires", "@a5l/skill-backtest-engine")
    kg.add_atom(atom2)
    atom2.save()
    print(f"✅ {atom2.id}")
    
    # 模拟数据服务
    data_atom = PrimeAtom("@a5l/data-stock-price", "data", "1.0.0", "infrastructure")
    data_atom.set_content(sources=["tushare", "akshare", "yahoo"])
    kg.add_atom(data_atom)
    data_atom.save()
    print(f"✅ {data_atom.id}")
    
    # 3. 构建索引
    print("\n📊 构建知识图谱索引...")
    kg.build_index()
    
    # 4. 查询演示
    print("\n🔍 查询演示:")
    print(f"  所有tool类型: {kg.query(kind='tool')}")
    print(f"  投资分析域: {kg.query(domain='investment-analysis')}")
    print(f"  backtest-engine依赖: {kg.get_dependencies('@a5l/skill-backtest-engine')}")
    print(f"  data-stock-price被依赖: {kg.get_dependents('@a5l/data-stock-price')}")
    
    # 5. 懒加载演示
    print("\n💾 懒加载演示:")
    # 清空内存
    kg.atoms.clear()
    print(f"  内存中原子数: {len(kg.atoms)}")
    # 从文件加载
    atom = kg.get_atom("@a5l/skill-factor-investing")
    print(f"  懒加载后: {atom.id if atom else 'Not found'}")
    print(f"  内存中原子数: {len(kg.atoms)}")
    
    print("\n" + "="*60)
    print("✅ POC完成！概念验证成功")
    print("="*60)
    print("\n核心验证点:")
    print("  ✅ Typed Atom数据结构")
    print("  ✅ 边关系管理（requires/enhances/validates_with）")
    print("  ✅ ~3KB轻量索引")
    print("  ✅ 懒加载机制")
    print("  ✅ SKILL→Atom自动迁移")
