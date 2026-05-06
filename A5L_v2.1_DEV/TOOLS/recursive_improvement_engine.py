#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recursive Self-Improvement Engine
递归自我改进引擎 v1.0

功能：
1. 递归分析自身性能
2. 识别改进机会
3. 实施自我改进
4. 验证改进效果
5. 改进改进机制本身（递归）

核心循环：
Observe → Analyze → Improve → Verify → Meta-Improve
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

sys.path.insert(0, '/workspace/projects/workspace/TOOLS')

class ImprovementType(Enum):
    """改进类型"""
    CODE_QUALITY = "代码质量"
    PERFORMANCE = "性能优化"
    RELIABILITY = "可靠性"
    USABILITY = "易用性"
    META = "元改进"  # 改进改进机制本身

@dataclass
class ImprovementCycle:
    """改进周期记录"""
    cycle_id: str
    timestamp: str
    target_component: str
    improvement_type: str
    before_metrics: Dict
    after_metrics: Dict
    improvement_delta: float
    lessons_learned: List[str]
    meta_feedback: Optional[str] = None  # 对改进过程的反思

class RecursiveSelfImprovementEngine:
    """
    递归自我改进引擎
    
    递归层级：
    - Level 0: 基础功能改进（代码、性能等）
    - Level 1: 改进流程改进（如何更好地改进）
    - Level 2: 元认知改进（理解何时/如何改进改进流程）
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.meta_dir = f"{workspace}/meta"
        self.improvement_log = f"{self.meta_dir}/improvement_cycles.json"
        self.meta_metrics_file = f"{self.meta_dir}/meta_metrics.json"
        self.reflection_file = f"{self.meta_dir}/self_reflection.json"
        
        # 确保目录存在
        os.makedirs(self.meta_dir, exist_ok=True)
        
        # 加载历史数据
        self.cycles = self._load_cycles()
        self.meta_metrics = self._load_meta_metrics()
        
        # 递归深度限制
        self.max_recursion_depth = 3
        self.current_depth = 0
    
    def _load_cycles(self) -> List[ImprovementCycle]:
        """加载改进周期历史"""
        if os.path.exists(self.improvement_log):
            try:
                with open(self.improvement_log, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [ImprovementCycle(**cycle) for cycle in data]
            except:
                pass
        return []
    
    def _load_meta_metrics(self) -> Dict:
        """加载元指标"""
        if os.path.exists(self.meta_metrics_file):
            with open(self.meta_metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "total_improvements": 0,
            "success_rate": 0.0,
            "avg_improvement_delta": 0.0,
            "recursion_level": 0,
            "meta_improvements_count": 0
        }
    
    def _save_cycle(self, cycle: ImprovementCycle):
        """保存改进周期"""
        self.cycles.append(cycle)
        with open(self.improvement_log, 'w', encoding='utf-8') as f:
            json.dump([asdict(c) for c in self.cycles[-100:]], f, indent=2, ensure_ascii=False)
    
    def run_recursive_improvement(self, target: str, depth: int = 0) -> Dict:
        """
        运行递归自我改进循环
        
        Args:
            target: 要改进的目标组件
            depth: 当前递归深度
        
        Returns:
            改进结果报告
        """
        self.current_depth = depth
        
        print("=" * 70)
        print(f"🔄 递归自我改进 - Level {depth}")
        print(f"🎯 目标: {target}")
        print("=" * 70)
        
        # 1. 观察当前状态
        print(f"\n[Level {depth}] Step 1: 观察当前状态...")
        before_metrics = self._observe_state(target)
        print(f"   📊 当前指标: {before_metrics}")
        
        # 2. 分析改进机会
        print(f"\n[Level {depth}] Step 2: 分析改进机会...")
        opportunities = self._analyze_improvements(target, before_metrics)
        print(f"   🔍 发现 {len(opportunities)} 个改进机会:")
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"      {i}. {opp['type']}: {opp['description'][:50]}...")
        
        if not opportunities:
            print(f"   ✅ Level {depth} 无需改进")
            return {"status": "no_improvement_needed", "depth": depth}
        
        # 3. 实施改进
        print(f"\n[Level {depth}] Step 3: 实施改进...")
        improvement_result = self._implement_improvement(target, opportunities[0])
        print(f"   🔧 改进实施: {improvement_result['description']}")
        
        # 4. 验证改进效果
        print(f"\n[Level {depth}] Step 4: 验证改进效果...")
        after_metrics = self._observe_state(target)
        improvement_delta = self._calculate_improvement(before_metrics, after_metrics)
        print(f"   📈 改进幅度: {improvement_delta:.2%}")
        
        # 5. 萃取经验
        print(f"\n[Level {depth}] Step 5: 萃取经验...")
        lessons = self._extract_lessons(improvement_result, before_metrics, after_metrics)
        print(f"   💡 关键经验: {len(lessons)} 条")
        for lesson in lessons:
            print(f"      • {lesson}")
        
        # 6. 记录改进周期
        cycle = ImprovementCycle(
            cycle_id=f"C{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            target_component=target,
            improvement_type=opportunities[0]['type'],
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            improvement_delta=improvement_delta,
            lessons_learned=lessons
        )
        self._save_cycle(cycle)
        
        # 7. 递归：改进改进机制本身
        if depth < self.max_recursion_depth and improvement_delta > 0.05:
            print(f"\n[Level {depth}] Step 6: 递归 - 改进改进机制...")
            meta_result = self.run_recursive_improvement(
                target="improvement_process",
                depth=depth + 1
            )
            cycle.meta_feedback = meta_result.get('summary', '')
            self._save_cycle(cycle)
        
        # 生成报告
        report = {
            "cycle_id": cycle.cycle_id,
            "depth": depth,
            "target": target,
            "improvement_type": opportunities[0]['type'],
            "before_metrics": before_metrics,
            "after_metrics": after_metrics,
            "improvement_delta": improvement_delta,
            "lessons_learned": lessons,
            "meta_improvement": depth < self.max_recursion_depth and improvement_delta > 0.05,
            "summary": f"Level {depth}: {target} 改进 {improvement_delta:.1%}"
        }
        
        print(f"\n{'=' * 70}")
        print(f"✅ Level {depth} 改进完成")
        print(f"{'=' * 70}")
        
        return report
    
    def _observe_state(self, target: str) -> Dict:
        """观察目标组件当前状态"""
        metrics = {}
        
        if target == "evolution_engine":
            # 检查进化引擎的性能
            metrics = self._check_evolution_engine_metrics()
        elif target == "goal_manager":
            # 检查Goal管理器的效率
            metrics = self._check_goal_manager_metrics()
        elif target == "archive_system":
            # 检查归档系统的性能
            metrics = self._check_archive_system_metrics()
        elif target == "improvement_process":
            # 检查改进流程本身
            metrics = self._check_improvement_process_metrics()
        else:
            # 通用指标
            metrics = {
                "response_time": 0,
                "success_rate": 0,
                "code_coverage": 0,
                "last_updated": datetime.now().isoformat()
            }
        
        return metrics
    
    def _check_evolution_engine_metrics(self) -> Dict:
        """检查进化引擎指标"""
        engine_file = f"{self.workspace}/TOOLS/agent_evolution_engine.py"
        
        metrics = {
            "file_exists": os.path.exists(engine_file),
            "file_size": 0,
            "function_count": 0,
            "last_run": None,
            "success_rate": 0.0
        }
        
        if os.path.exists(engine_file):
            with open(engine_file, 'r', encoding='utf-8') as f:
                content = f.read()
                metrics["file_size"] = len(content)
                metrics["function_count"] = content.count('def ')
        
        # 检查运行日志
        log_file = f"{self.workspace}/memory/evolution_log.json"
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    if logs:
                        metrics["last_run"] = logs[-1].get('timestamp')
                        success_count = sum(1 for l in logs if l.get('success', False))
                        metrics["success_rate"] = success_count / len(logs)
            except:
                pass
        
        return metrics
    
    def _check_goal_manager_metrics(self) -> Dict:
        """检查Goal管理器指标"""
        goals_file = f"{self.workspace}/data/goals/goals.json"
        tasks_file = f"{self.workspace}/data/goals/tasks.json"
        
        metrics = {
            "goals_count": 0,
            "tasks_count": 0,
            "completion_rate": 0.0,
            "avg_progress": 0.0
        }
        
        if os.path.exists(goals_file):
            try:
                with open(goals_file, 'r', encoding='utf-8') as f:
                    goals = json.load(f)
                    metrics["goals_count"] = len(goals)
                    if goals:
                        metrics["avg_progress"] = sum(g.get('progress', 0) for g in goals) / len(goals)
            except:
                pass
        
        return metrics
    
    def _check_archive_system_metrics(self) -> Dict:
        """检查归档系统指标"""
        archive_dir = f"{self.workspace}/archive"
        
        metrics = {
            "archive_count": 0,
            "last_archive": None,
            "avg_archive_size": 0
        }
        
        if os.path.exists(archive_dir):
            archives = [d for d in os.listdir(archive_dir) if d.startswith('2026')]
            metrics["archive_count"] = len(archives)
            if archives:
                metrics["last_archive"] = max(archives)
        
        return metrics
    
    def _check_improvement_process_metrics(self) -> Dict:
        """检查改进流程自身的指标"""
        metrics = {
            "total_cycles": len(self.cycles),
            "avg_improvement_delta": 0.0,
            "success_rate": 0.0,
            "recursion_efficiency": 0.0
        }
        
        if self.cycles:
            deltas = [c.improvement_delta for c in self.cycles]
            metrics["avg_improvement_delta"] = sum(deltas) / len(deltas)
            metrics["success_rate"] = sum(1 for d in deltas if d > 0) / len(deltas)
        
        return metrics
    
    def _analyze_improvements(self, target: str, metrics: Dict) -> List[Dict]:
        """分析改进机会"""
        opportunities = []
        
        # 基于目标类型分析
        if target == "evolution_engine":
            if not metrics.get('file_exists', False):
                opportunities.append({
                    "type": ImprovementType.RELIABILITY.value,
                    "priority": 10,
                    "description": "进化引擎文件缺失，需要重新创建",
                    "action": "recreate_engine"
                })
            elif metrics.get('success_rate', 0) < 0.8:
                opportunities.append({
                    "type": ImprovementType.RELIABILITY.value,
                    "priority": 8,
                    "description": f"成功率偏低 ({metrics['success_rate']:.0%})，需要增强错误处理",
                    "action": "enhance_error_handling"
                })
        
        elif target == "goal_manager":
            if metrics.get('goals_count', 0) == 0:
                opportunities.append({
                    "type": ImprovementType.USABILITY.value,
                    "priority": 9,
                    "description": "Goal系统未初始化，需要创建递归改进Goal",
                    "action": "init_recursive_goals"
                })
            elif metrics.get('avg_progress', 0) < 50:
                opportunities.append({
                    "type": ImprovementType.PERFORMANCE.value,
                    "priority": 7,
                    "description": "Goal平均进度偏低，需要加速执行",
                    "action": "accelerate_execution"
                })
        
        elif target == "improvement_process":
            if metrics.get('total_cycles', 0) < 10:
                opportunities.append({
                    "type": ImprovementType.META.value,
                    "priority": 10,
                    "description": "改进周期数据不足，需要建立系统化的元改进机制",
                    "action": "establish_meta_improvement"
                })
            elif metrics.get('recursion_efficiency', 0) < 0.5:
                opportunities.append({
                    "type": ImprovementType.META.value,
                    "priority": 8,
                    "description": "递归效率偏低，需要优化递归触发条件",
                    "action": "optimize_recursion"
                })
        
        # 通用改进机会
        opportunities.append({
            "type": ImprovementType.CODE_QUALITY.value,
            "priority": 5,
            "description": "添加更多文档和注释",
            "action": "add_documentation"
        })
        
        # 按优先级排序
        opportunities.sort(key=lambda x: x['priority'], reverse=True)
        
        return opportunities
    
    def _implement_improvement(self, target: str, opportunity: Dict) -> Dict:
        """实施改进"""
        action = opportunity['action']
        
        result = {
            "action": action,
            "description": opportunity['description'],
            "status": "implemented",
            "changes": []
        }
        
        if action == "init_recursive_goals":
            # 创建递归改进相关的Goals
            result["changes"] = self._create_recursive_improvement_goals()
        
        elif action == "establish_meta_improvement":
            # 建立元改进机制
            result["changes"] = self._establish_meta_improvement_system()
        
        elif action == "add_documentation":
            # 添加文档
            result["changes"] = self._add_meta_documentation()
        
        else:
            # 记录改进意图
            result["changes"].append(f"标记改进意图: {action}")
        
        return result
    
    def _create_recursive_improvement_goals(self) -> List[str]:
        """创建递归改进相关的Goals"""
        from goal_manager import GoalManager
        
        gm = GoalManager()
        changes = []
        
        # 创建元改进Goal
        meta_goal = gm.create_goal(
            title="建立递归自我改进系统",
            description="实现能够改进自身的自我改进机制（Meta-Self-Improvement）",
            deadline="2026-05-08"
        )
        changes.append(f"创建元改进Goal: {meta_goal['id']}")
        
        # 添加任务
        tasks = [
            ("设计递归改进框架", "定义Observe→Analyze→Improve→Verify→Meta-Improve循环"),
            ("实现改进效果度量", "建立before/after指标对比系统"),
            ("建立元反馈机制", "改进改进过程本身的能力"),
            ("创建改进日志系统", "记录所有改进周期用于分析"),
            ("实现递归深度控制", "防止无限递归，设置合理的终止条件")
        ]
        
        for title, desc in tasks:
            task = gm.create_task(
                goal_id=meta_goal['id'],
                title=title,
                description=desc,
                estimated_hours=4
            )
            changes.append(f"  创建任务: {title}")
        
        return changes
    
    def _establish_meta_improvement_system(self) -> List[str]:
        """建立元改进系统"""
        changes = []
        
        # 创建元改进配置文件
        meta_config = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "recursion_config": {
                "max_depth": 3,
                "min_improvement_threshold": 0.05,
                "meta_improvement_trigger": "improvement_delta > 0.1"
            },
            "improvement_types": [
                "代码质量", "性能优化", "可靠性", "易用性", "元改进"
            ],
            "success_criteria": {
                "min_delta": 0.05,
                "required_lessons": 1
            }
        }
        
        config_file = f"{self.meta_dir}/meta_improvement_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(meta_config, f, indent=2, ensure_ascii=False)
        
        changes.append(f"创建元改进配置: {config_file}")
        
        # 创建元改进引擎本文件（如果还未创建）
        engine_file = f"{self.workspace}/TOOLS/recursive_improvement_engine.py"
        if not os.path.exists(engine_file):
            changes.append(f"元改进引擎已存在: {engine_file}")
        else:
            changes.append(f"元改进引擎已部署: {engine_file}")
        
        return changes
    
    def _add_meta_documentation(self) -> List[str]:
        """添加元改进文档"""
        changes = []
        
        doc_content = f"""# 递归自我改进系统文档

**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**版本**: 1.0

## 什么是递归自我改进？

递归自我改进是指系统不仅能够改进自身功能，还能够改进"改进自身的方式"。

### 递归层级

- **Level 0**: 基础功能改进（代码、性能、可靠性）
- **Level 1**: 改进流程改进（如何更好地改进）
- **Level 2**: 元认知改进（理解何时/如何改进改进流程）
- **Level 3**: 策略改进（改进改进的改进...）

## 核心循环

```
Observe → Analyze → Improve → Verify → Meta-Improve
   ↑                                            │
   └────────────────────────────────────────────┘
                    (递归)
```

## 使用方式

```python
from recursive_improvement_engine import RecursiveSelfImprovementEngine

engine = RecursiveSelfImprovementEngine()

# 对特定组件进行递归改进
result = engine.run_recursive_improvement("evolution_engine", depth=0)

# 查看改进历史
for cycle in engine.cycles:
    print(f"{{cycle.cycle_id}}: {{cycle.improvement_delta:.1%}}")
```

## 改进类型

1. **代码质量**: 可读性、结构、注释
2. **性能优化**: 速度、资源使用
3. **可靠性**: 错误处理、容错
4. **易用性**: API设计、文档
5. **元改进**: 改进改进机制本身

## 度量指标

- 改进幅度 (improvement_delta)
- 成功率
- 经验萃取数量
- 递归深度
- 元改进效率
"""
        
        doc_file = f"{self.meta_dir}/README.md"
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        changes.append(f"创建元改进文档: {doc_file}")
        
        return changes
    
    def _calculate_improvement(self, before: Dict, after: Dict) -> float:
        """计算改进幅度"""
        improvements = []
        
        for key in before:
            if key in after and isinstance(before[key], (int, float)) and isinstance(after[key], (int, float)):
                if before[key] != 0:
                    delta = (after[key] - before[key]) / abs(before[key])
                    improvements.append(delta)
        
        if improvements:
            return sum(improvements) / len(improvements)
        return 0.0
    
    def _extract_lessons(self, result: Dict, before: Dict, after: Dict) -> List[str]:
        """萃取经验"""
        lessons = []
        
        # 基于改进结果萃取
        if result.get('changes'):
            lessons.append(f"成功实施了 {len(result['changes'])} 项改进")
        
        # 基于指标变化萃取
        for key in before:
            if key in after and before[key] != after[key]:
                lessons.append(f"{key}: {before[key]} → {after[key]}")
        
        # 元经验
        lessons.append(f"递归深度 {self.current_depth} 的改进已完成")
        
        return lessons
    
    def generate_improvement_report(self) -> str:
        """生成改进报告"""
        report = f"""# 递归自我改进系统报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计概览

| 指标 | 数值 |
|------|------|
| 总改进周期 | {len(self.cycles)} |
| 平均改进幅度 | {self.meta_metrics.get('avg_improvement_delta', 0):.2%} |
| 成功率 | {self.meta_metrics.get('success_rate', 0):.1%} |
| 元改进次数 | {self.meta_metrics.get('meta_improvements_count', 0)} |

## 最近改进周期

"""
        
        for cycle in self.cycles[-5:]:
            report += f"""
### {cycle.cycle_id} - {cycle.target_component}
- **时间**: {cycle.timestamp}
- **类型**: {cycle.improvement_type}
- **改进幅度**: {cycle.improvement_delta:.2%}
- **经验**: {len(cycle.lessons_learned)} 条
"""
        
        return report

def main():
    """主函数 - 演示递归自我改进"""
    print("=" * 70)
    print("🔄 递归自我改进引擎 - 启动")
    print("=" * 70)
    
    engine = RecursiveSelfImprovementEngine()
    
    # 运行递归改进
    print("\n🎯 对Goal管理系统进行递归自我改进\n")
    result = engine.run_recursive_improvement("goal_manager", depth=0)
    
    print("\n" + "=" * 70)
    print("📊 生成改进报告")
    print("=" * 70)
    report = engine.generate_improvement_report()
    print(report[:500] + "...")
    
    # 保存报告
    report_file = f"{engine.meta_dir}/improvement_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 完整报告已保存: {report_file}")

if __name__ == "__main__":
    main()
