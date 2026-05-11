#!/usr/bin/env python3
"""
Prime Registry V2.2 - 集成SQLite持久化
Wave 1 Phase 1.3 完成版

核心改进:
- ✅ 从内存存储迁移到SQLite持久化
- ✅ 数据重启后不丢失
- ✅ 支持复杂查询
- ✅ 自动索引管理
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich import box

from database import get_db_manager, save_analysis, Atom

console = Console()


class PrimeRegistryV2:
    """
    Prime Registry V2.2 - SQLite持久化版本
    
    数据流:
        Atom对象 → SQLite DB → 持久化存储
                  ↓
              查询/更新
    """
    
    def __init__(self):
        self.db = get_db_manager()
        self._cache = {}  # 轻量级缓存
        console.print("[dim]📦 Prime Registry V2.2 - SQLite模式[/dim]")
    
    def init_registry(self):
        """初始化Registry - 使用数据库"""
        console.print("[bold cyan]📦 Prime Registry V2.2 - 初始化[/bold cyan]\n")
        
        # 检查是否已有数据
        stats = self.db.get_stats()
        if stats.get('total_atoms', 0) > 0:
            console.print(f"[yellow]⚠️ 数据库已有 {stats['total_atoms']} 个Atoms[/yellow]")
            console.print("[dim]使用现有数据，跳过初始化[/dim]\n")
            return
        
        # 生成样本Atoms
        atom_types = ["decision", "analysis", "signal", "memo", "tag", "risk"]
        squads = ["prime_council", "intelligence_core", "execution_force", 
                  "validation_guard", "research_lab", "integration_hub"]
        
        console.print("[dim]生成样本Atoms到数据库...[/dim]\n")
        
        with Progress() as progress:
            task = progress.add_task("[cyan]创建Atoms...", total=100)
            
            for i in range(100):
                atom = Atom(
                    id=f"@a5l/{atom_types[i % 6]}-{i:04d}",
                    kind=atom_types[i % 6],
                    title=f"Sample {atom_types[i % 6]} #{i}",
                    content=f"This is a sample {atom_types[i % 6]} atom for testing.",
                    squad_id=squads[i % 6],
                    author="system",
                    tags=[atom_types[i % 6], squads[i % 6]],
                    metadata={'version': f'1.0.{i % 10}', 'sample': True}
                )
                self.db.save_atom(atom)
                progress.update(task, advance=1)
        
        stats = self.db.get_stats()
        console.print(f"[green]✅ {stats['total_atoms']} 个Atoms创建完成[/green]\n")
    
    def fast_query(self, query_type: str, key: str) -> List[Dict]:
        """
        快速查询 - 使用数据库索引
        
        Args:
            query_type: 查询类型 ('kind', 'squad', 'id', 'search')
            key: 查询键值
            
        Returns:
            Atom列表
        """
        start_time = time.time()
        
        if query_type == "id":
            atom = self.db.get_atom(key)
            results = [atom] if atom else []
            
        elif query_type == "kind":
            atoms = self.db.get_atoms_by_kind(key)
            results = atoms
            
        elif query_type == "squad":
            atoms = self.db.get_atoms_by_squad(key)
            results = atoms
            
        elif query_type == "search":
            atoms = self.db.search_atoms(key)
            results = atoms
            
        else:
            results = []
        
        elapsed = (time.time() - start_time) * 1000
        
        # 转换为Dict格式
        return [{
            'id': a.id,
            'kind': a.kind,
            'title': a.title,
            'squad': a.squad_id,
            'status': a.status,
            'created': a.created_at
        } for a in results]
    
    def save_atom(self, atom_data: Dict) -> str:
        """
        保存Atom到Registry
        
        Args:
            atom_data: Atom数据字典
            
        Returns:
            Atom ID
        """
        atom = Atom(
            id=atom_data.get('id', f"@a5l/atom-{int(time.time()*1000)}"),
            kind=atom_data.get('kind', 'memo'),
            title=atom_data.get('title'),
            content=atom_data.get('content', ''),
            author=atom_data.get('author', 'system'),
            squad_id=atom_data.get('squad_id'),
            tags=atom_data.get('tags', []),
            metadata=atom_data.get('metadata', {})
        )
        
        self.db.save_atom(atom)
        return atom.id
    
    def get_stats(self) -> Dict:
        """获取Registry统计"""
        return self.db.get_stats()
    
    def show_dashboard(self):
        """显示Registry仪表板"""
        from database.db_utils import print_dashboard
        print_dashboard()
    
    def export_to_json(self, filepath: str):
        """
        导出所有Atoms到JSON
        
        Args:
            filepath: 输出文件路径
        """
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        
        rows = conn.execute('SELECT * FROM atoms WHERE status = "active"').fetchall()
        atoms = [dict(row) for row in rows]
        
        conn.close()
        
        with open(filepath, 'w') as f:
            json.dump(atoms, f, indent=2, default=str)
        
        console.print(f"[green]✅ 导出完成: {filepath} ({len(atoms)} atoms)[/green]")


def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold cyan]Prime Registry V2.2[/bold cyan]\n"
        "[dim]SQLite持久化版本[/dim]",
        title="A5L Wave 1",
        border_style="cyan"
    ))
    
    registry = PrimeRegistryV2()
    
    # 初始化
    registry.init_registry()
    
    # 查询演示
    console.print("\n[bold]⚡ 查询演示[/bold]\n")
    
    console.print("[dim]1. 按类型查询 'analysis':[/dim]")
    results = registry.fast_query("kind", "analysis")
    console.print(f"   找到 {len(results)} 个Atoms")
    
    console.print("\n[dim]2. 按Squad查询 'execution_force':[/dim]")
    results = registry.fast_query("squad", "execution_force")
    console.print(f"   找到 {len(results)} 个Atoms")
    
    console.print("\n[dim]3. 搜索关键词 'Sample':[/dim]")
    results = registry.fast_query("search", "Sample")
    console.print(f"   找到 {len(results)} 个Atoms")
    
    # 显示仪表板
    console.print("\n")
    registry.show_dashboard()
    
    console.print("[bold green]\n✅ Wave 1 Phase 1.3 完成![/bold green]")
    console.print("[dim]数据已持久化到SQLite，重启后不会丢失[/dim]")


if __name__ == '__main__':
    main()
