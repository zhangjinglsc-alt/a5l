#!/usr/bin/env python3
"""
A5L-Prime 性能基准测试
测试大规模atom加载、查询、导出性能
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path

# 添加TOOLS目录到路径
sys.path.insert(0, '/workspace/projects/workspace/TOOLS')

from prime_poc import PrimeAtom, A5LKnowledgeGraph


class PerformanceBenchmark:
    """Prime性能基准测试"""
    
    def __init__(self):
        self.results = []
        
    def log(self, test_name: str, elapsed_ms: float, details: str = ""):
        """记录测试结果"""
        result = {
            "test": test_name,
            "elapsed_ms": round(elapsed_ms, 2),
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅" if elapsed_ms < 1000 else "⚠️"
        print(f"  {status} {test_name}: {elapsed_ms:.2f}ms")
        if details:
            print(f"     {details}")
        return result
    
    def test_1_bulk_load_small(self):
        """测试1: 小规模批量加载 (100 atoms)"""
        print("\n📦 Test 1: 小规模批量加载 (100 atoms)")
        
        start = time.time()
        kg = A5LKnowledgeGraph()
        
        # 创建100个atoms
        for i in range(100):
            atom = PrimeAtom(
                id=f"@test/atom-{i:04d}",
                kind="skill",
                version="1.0.0",
                domain="test"
            )
            atom.set_content(
                name=f"Test Skill {i}",
                description=f"Performance test atom {i}",
                index=i
            )
            kg.add_atom(atom)
        
        elapsed = (time.time() - start) * 1000
        return self.log("100 atoms创建", elapsed, f"内存atoms: {len(kg.atoms)}")
    
    def test_2_bulk_load_medium(self):
        """测试2: 中规模批量加载 (500 atoms)"""
        print("\n📦 Test 2: 中规模批量加载 (500 atoms)")
        
        start = time.time()
        kg = A5LKnowledgeGraph()
        
        # 创建500个atoms
        for i in range(500):
            atom = PrimeAtom(
                id=f"@test/medium-{i:04d}",
                kind="decision" if i % 3 == 0 else "signal",
                version="1.0.0",
                domain="trading" if i % 2 == 0 else "analysis"
            )
            atom.set_content(
                name=f"Test Atom {i}",
                value=i * 1.5,
                tags=["test", "performance", f"tag-{i % 10}"]
            )
            # 添加一些边关系
            if i > 0:
                atom.add_edge("related", f"@test/medium-{(i-1):04d}")
            kg.add_atom(atom)
        
        elapsed = (time.time() - start) * 1000
        return self.log("500 atoms创建", elapsed, f"内存atoms: {len(kg.atoms)}")
    
    def test_3_query_performance(self):
        """测试3: 查询性能"""
        print("\n📦 Test 3: 查询性能")
        
        # 先创建测试数据
        kg = A5LKnowledgeGraph()
        for i in range(1000):
            atom = PrimeAtom(
                id=f"@test/query-{i:04d}",
                kind="skill" if i % 5 == 0 else "signal",
                version="1.0.0",
                domain="test"
            )
            atom.set_content(value=i, category=f"cat-{i % 20}")
            kg.add_atom(atom)
        
        # 测试ID查询
        start = time.time()
        for i in range(100):
            atom = kg.get_atom(f"@test/query-{i:04d}")
        id_query_time = (time.time() - start) * 1000
        self.log("ID查询 (100次)", id_query_time, f"平均: {id_query_time/100:.2f}ms/次")
        
        # 测试类型过滤查询
        start = time.time()
        skills = [a for a in kg.atoms.values() if a.kind == "skill"]
        type_query_time = (time.time() - start) * 1000
        return self.log("类型过滤查询", type_query_time, f"找到 {len(skills)} 个skill")
    
    def test_4_save_load_performance(self):
        """测试4: 保存/加载性能"""
        print("\n📦 Test 4: 保存/加载性能")
        
        # 创建测试数据
        kg = A5LKnowledgeGraph()
        test_path = "/tmp/prime-perf-test"
        
        for i in range(100):
            atom = PrimeAtom(
                id=f"@test/io-{i:04d}",
                kind="skill",
                version="1.0.0",
                domain="test"
            )
            atom.set_content(data={"key": f"value-{i}", "index": i})
            kg.add_atom(atom)
        
        # 测试保存
        start = time.time()
        for atom in kg.atoms.values():
            atom.save(test_path)
        save_time = (time.time() - start) * 1000
        self.log("保存100 atoms", save_time, f"到 {test_path}")
        
        # 测试加载
        start = time.time()
        kg2 = A5LKnowledgeGraph(test_path)
        load_time = (time.time() - start) * 1000
        return self.log("加载100 atoms", load_time, f"从 {test_path}, 加载 {len(kg2.atoms)} 个")
    
    def test_5_export_performance(self):
        """测试5: 导出性能"""
        print("\n📦 Test 5: 导出性能")
        
        # 创建测试数据
        kg = A5LKnowledgeGraph()
        for i in range(200):
            atom = PrimeAtom(
                id=f"@test/export-{i:04d}",
                kind="decision",
                version="1.0.0",
                domain="trading"
            )
            atom.set_content(
                symbol=f"{i:06d}.SZ",
                action="BUY" if i % 2 == 0 else "SELL",
                price=10.0 + i * 0.1
            )
            kg.add_atom(atom)
        
        # 测试Prime格式导出
        start = time.time()
        export_data = {
            "metadata": {
                "source": "A5L-Prime",
                "version": "2.1.0",
                "timestamp": datetime.now().isoformat()
            },
            "atoms": [atom.to_dict() for atom in kg.atoms.values()],
            "statistics": {
                "total_atoms": len(kg.atoms),
                "by_kind": {}
            }
        }
        
        # 统计by_kind
        for atom in kg.atoms.values():
            kind = atom.kind
            export_data["statistics"]["by_kind"][kind] = \
                export_data["statistics"]["by_kind"].get(kind, 0) + 1
        
        # 保存到文件
        export_path = "/tmp/prime-export-perf.json"
        with open(export_path, 'w') as f:
            json.dump(export_data, f)
        
        elapsed = (time.time() - start) * 1000
        file_size = Path(export_path).stat().st_size / 1024
        return self.log("导出200 atoms", elapsed, f"文件大小: {file_size:.1f}KB")
    
    def test_6_real_world_simulation(self):
        """测试6: 真实场景模拟"""
        print("\n📦 Test 6: 真实场景模拟 (一日交易决策)")
        
        start = time.time()
        kg = A5LKnowledgeGraph()
        
        # 模拟一日交易产生的atoms
        # 1. 盘前分析 (5个SKILL调用)
        for i in range(5):
            atom = PrimeAtom(
                id=f"@a5l/skill-call-{i}",
                kind="skill_invocation",
                domain="a5l-core"
            )
            atom.set_content(skill=f"skill-{i}", result=f"result-{i}")
            kg.add_atom(atom)
        
        # 2. 买入决策 (3笔交易)
        for i in range(3):
            decision = PrimeAtom(
                id=f"@a5l/decision-buy-{i}",
                kind="decision",
                domain="trading"
            )
            decision.set_content(action="BUY", symbol=f"00000{i}.SZ")
            decision.add_edge("requires", "@a5l/skill-call-0")
            kg.add_atom(decision)
            
            # 每个决策关联信号和风险
            signal = PrimeAtom(
                id=f"@a5l/signal-{i}",
                kind="signal",
                domain="trading"
            )
            signal.add_edge("triggers", decision.id)
            kg.add_atom(signal)
            
            risk = PrimeAtom(
                id=f"@a5l/risk-{i}",
                kind="risk",
                domain="risk-control"
            )
            risk.add_edge("contradicts", decision.id)
            kg.add_atom(risk)
        
        # 3. 六管理者共识 (1次)
        consensus = PrimeAtom(
            id="@a5l/consensus-001",
            kind="consensus",
            domain="a5l-core"
        )
        for manager in ["ca", "cio", "coo", "cso", "kg", "rm"]:
            consensus.add_edge("contributed_by", f"@a5l/persona-{manager}")
        kg.add_atom(consensus)
        
        elapsed = (time.time() - start) * 1000
        total_atoms = len(kg.atoms)
        return self.log("一日交易模拟", elapsed, f"生成 {total_atoms} 个atoms")
    
    def run_all_benchmarks(self):
        """运行所有性能测试"""
        print("="*70)
        print("🚀 A5L-Prime 性能基准测试")
        print("="*70)
        
        tests = [
            self.test_1_bulk_load_small,
            self.test_2_bulk_load_medium,
            self.test_3_query_performance,
            self.test_4_save_load_performance,
            self.test_5_export_performance,
            self.test_6_real_world_simulation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"  ❌ {test.__name__}: {e}")
        
        # 生成报告
        print("\n" + "="*70)
        print("📊 性能基准报告")
        print("="*70)
        
        total_time = sum(r["elapsed_ms"] for r in self.results)
        print(f"总测试数: {len(self.results)}")
        print(f"总耗时: {total_time:.2f}ms ({total_time/1000:.2f}s)")
        print(f"平均耗时: {total_time/len(self.results):.2f}ms")
        
        # 保存报告
        report_path = "/workspace/projects/workspace/prime-atoms/performance-benchmark.json"
        with open(report_path, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": len(self.results),
                    "total_time_ms": total_time,
                    "avg_time_ms": total_time/len(self.results)
                },
                "results": self.results,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n💾 详细报告: {report_path}")
        
        return self.results


if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()
