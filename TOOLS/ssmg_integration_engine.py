#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSMG Integration Engine
SOUL-SKILL-MEMORY-GOAL 整合引擎

功能：
1. 四层架构统一管理
2. 启动时加载完整上下文
3. 执行时记忆检索与更新
4. 自动同步各层关联
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class SSMGIntegrationEngine:
    """SSMG整合引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        
        # 四层文件路径
        self.soul_file = f"{workspace}/SOUL.md"
        self.soul_history_file = f"{workspace}/SOUL_HISTORY.md"
        self.skill_registry_file = f"{workspace}/SKILL_REGISTRY.json"
        self.memory_file = f"{workspace}/MEMORY.md"
        self.memory_dir = f"{workspace}/memory"
        self.working_memory_file = f"{workspace}/memory/working_memory.json"
        self.goals_dir = f"{workspace}/data/goals"
        
        # 运行时状态
        self.soul = None
        self.skills = None
        self.memory = None
        self.goals = None
        self.context = None
    
    def initialize_session(self) -> Dict:
        """
        会话初始化 - 加载完整的SOUL-SKILL-MEMORY-GOAL上下文
        这是每次对话开始时的核心加载流程
        """
        print("=" * 70)
        print("🧬 SSMG Integration Engine - 会话初始化")
        print("=" * 70)
        print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Layer 1: 加载SOUL (灵魂层)
        print("┌" + "─" * 68 + "┐")
        print("│ Layer 1: SOUL (灵魂层) - 加载身份定义                          │")
        print("└" + "─" * 68 + "┘")
        self.soul = self._load_soul()
        print(f"✅ 人格宪章加载完成")
        print(f"   核心身份: {self.soul.get('core_identity', 'N/A')}")
        print(f"   价值观: {len(self.soul.get('values', []))} 项")
        
        # Layer 2: 加载SKILL (技能层)
        print("\n┌" + "─" * 68 + "┐")
        print("│ Layer 2: SKILL (技能层) - 加载能力清单                         │")
        print("└" + "─" * 68 + "┘")
        self.skills = self._load_skills()
        print(f"✅ 技能注册表加载完成")
        print(f"   总技能数: {self.skills.get('summary', {}).get('total_skills', 0)}")
        print(f"   活跃技能: {self.skills.get('summary', {}).get('active_skills', 0)}")
        print(f"   平均熟练度: {self.skills.get('summary', {}).get('avg_proficiency', 0):.0%}")
        
        # Layer 3: 加载MEMORY (记忆层)
        print("\n┌" + "─" * 68 + "┐")
        print("│ Layer 3: MEMORY (记忆层) - 加载经验沉淀                        │")
        print("└" + "─" * 68 + "┘")
        self.memory = self._load_memory()
        print(f"✅ 记忆系统加载完成")
        print(f"   长期记忆: {len(self.memory.get('long_term', []))} 条精华")
        print(f"   情景记忆: {len(self.memory.get('episodic', []))} 天记录")
        print(f"   工作记忆: {len(self.memory.get('working', {}).get('active_goals', []))} 个活跃目标")
        
        # Layer 4: 加载GOAL (目标层)
        print("\n┌" + "─" * 68 + "┐")
        print("│ Layer 4: GOAL (目标层) - 加载进化方向                          │")
        print("└" + "─" * 68 + "┘")
        self.goals = self._load_goals()
        print(f"✅ 目标系统加载完成")
        print(f"   活跃目标: {len(self.goals.get('active', []))}")
        print(f"   历史目标: {len(self.goals.get('archived', []))}")
        for goal in self.goals.get('active', [])[:3]:
            print(f"   • {goal['title']}: {goal.get('progress', 0)}%")
        
        # 整合四层上下文
        print("\n┌" + "─" * 68 + "┐")
        print("│ 整合四层上下文                                                  │")
        print("└" + "─" * 68 + "┘")
        self.context = self._integrate_context()
        print(f"✅ 上下文整合完成")
        print(f"   上下文大小: {len(str(self.context))} 字符")
        
        # 更新工作记忆
        self._update_working_memory()
        
        print("\n" + "=" * 70)
        print("✅ SSMG初始化完成 - 四层架构已加载")
        print("=" * 70)
        
        return self.context
    
    def _load_soul(self) -> Dict:
        """加载SOUL层 - 人格宪章"""
        soul = {
            "core_identity": "AI Agent with Goal-Oriented Evolution",
            "name": "OpenClaw Agent",
            "values": [
                "Be genuinely helpful",
                "Have opinions",
                "Be resourceful",
                "Earn trust through competence"
            ],
            "capabilities_summary": {},
            "evolution_milestones": [],
            "loaded_at": datetime.now().isoformat()
        }
        
        # 尝试从SOUL.md解析
        if os.path.exists(self.soul_file):
            try:
                with open(self.soul_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取关键信息
                    if "我是谁" in content or "Who You Are" in content:
                        soul['has_soul_md'] = True
                    if "50 specialized skills" in content or "54个" in content:
                        soul['capabilities_summary']['skills_count'] = 54
                    if "L3" in content:
                        soul['evolution_milestones'].append("L3进化进行中")
            except:
                pass
        
        return soul
    
    def _load_skills(self) -> Dict:
        """加载SKILL层 - 技能注册表"""
        if os.path.exists(self.skill_registry_file):
            try:
                with open(self.skill_registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {"summary": {"total_skills": 0, "active_skills": 0}}
    
    def _load_memory(self) -> Dict:
        """加载MEMORY层 - 三层记忆"""
        memory = {
            "long_term": [],
            "episodic": [],
            "working": {}
        }
        
        # 3.1 长期记忆 (MEMORY.md)
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单解析，实际应该更复杂
                    memory['long_term'] = [line.strip() for line in content.split('\n') 
                                          if line.strip() and line.strip().startswith('-')]
            except:
                pass
        
        # 3.2 情景记忆 (memory/*.md)
        if os.path.exists(self.memory_dir):
            for fname in os.listdir(self.memory_dir):
                if fname.endswith('.md') and fname.startswith('2026'):
                    memory['episodic'].append(fname.replace('.md', ''))
        
        # 3.3 工作记忆
        if os.path.exists(self.working_memory_file):
            try:
                with open(self.working_memory_file, 'r', encoding='utf-8') as f:
                    memory['working'] = json.load(f)
            except:
                memory['working'] = {"active_goals": [], "current_tasks": []}
        else:
            memory['working'] = {"active_goals": [], "current_tasks": []}
        
        return memory
    
    def _load_goals(self) -> Dict:
        """加载GOAL层 - 目标系统"""
        goals = {
            "active": [],
            "archived": []
        }
        
        if os.path.exists(self.goals_dir):
            goals_file = f"{self.goals_dir}/goals.json"
            if os.path.exists(goals_file):
                try:
                    with open(goals_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        goals['active'] = [g for g in data if g.get('status') == 'active']
                        goals['archived'] = [g for g in data if g.get('status') != 'active']
                except:
                    pass
        
        # 如果为空，使用GoalManager加载
        if not goals['active']:
            try:
                from goal_manager import GoalManager
                gm = GoalManager()
                goals['active'] = gm.goals
                goals['from_manager'] = True
            except:
                pass
        
        return goals
    
    def _integrate_context(self) -> Dict:
        """整合四层上下文"""
        return {
            "soul": self.soul,
            "skills": {
                "count": self.skills.get('summary', {}).get('total_skills', 0),
                "categories": list(self.skills.get('categories', {}).keys()),
                "top_skills": self._get_top_skills(5)
            },
            "memory": {
                "long_term_count": len(self.memory.get('long_term', [])),
                "recent_episodes": self.memory.get('episodic', [])[-7:],
                "active_goals_in_working": self.memory.get('working', {}).get('active_goals', [])
            },
            "goals": {
                "active_count": len(self.goals.get('active', [])),
                "top_goals": [
                    {
                        "title": g.get('title'),
                        "progress": g.get('progress', 0)
                    }
                    for g in self.goals.get('active', [])[:3]
                ]
            },
            "integrated_at": datetime.now().isoformat()
        }
    
    def _get_top_skills(self, n: int = 5) -> List[Dict]:
        """获取最熟练的技能"""
        all_skills = []
        for cat_name, cat_data in self.skills.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                all_skills.append({
                    "name": skill.get('name'),
                    "proficiency": skill.get('proficiency', 0),
                    "category": cat_name
                })
        
        return sorted(all_skills, key=lambda x: x['proficiency'], reverse=True)[:n]
    
    def _update_working_memory(self):
        """更新工作记忆"""
        working = {
            "last_session": datetime.now().isoformat(),
            "active_goals": [g.get('id') for g in self.goals.get('active', [])],
            "loaded_skills_count": self.skills.get('summary', {}).get('total_skills', 0),
            "recent_memories": self.memory.get('episodic', [])[-3:],
            "soul_version": "2.0"
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.working_memory_file), exist_ok=True)
        
        with open(self.working_memory_file, 'w', encoding='utf-8') as f:
            json.dump(working, f, indent=2, ensure_ascii=False)
    
    def recall_for_task(self, task_type: str) -> List[str]:
        """
        为特定任务检索相关记忆
        这是记忆增强的核心功能
        """
        relevant_memories = []
        
        # 1. 从长期记忆中检索
        for mem in self.memory.get('long_term', []):
            if task_type.lower() in mem.lower():
                relevant_memories.append(f"[长期] {mem}")
        
        # 2. 从情景记忆中检索（最近7天）
        recent_episodes = self.memory.get('episodic', [])[-7:]
        for episode in recent_episodes:
            # 这里应该读取具体文件内容
            pass
        
        # 3. 从Goal中检索相关经验
        for goal in self.goals.get('active', []):
            if task_type.lower() in goal.get('title', '').lower():
                relevant_memories.append(f"[Goal] {goal.get('title')}: {goal.get('progress')}%")
        
        return relevant_memories[:5]  # 返回最相关的5条
    
    def update_after_task(self, task_result: Dict):
        """
        任务执行后更新各层
        """
        # 1. 更新SKILL（如果使用）
        skill_used = task_result.get('skill_used')
        if skill_used and self.skills:
            # 更新使用次数和熟练度
            pass
        
        # 2. 更新MEMORY（写入情景记忆）
        episode = {
            "timestamp": datetime.now().isoformat(),
            "task": task_result.get('task'),
            "success": task_result.get('success'),
            "lesson": task_result.get('lesson')
        }
        
        # 追加到今日记忆文件
        today = datetime.now().strftime('%Y-%m-%d')
        today_file = f"{self.memory_dir}/{today}.md"
        
        with open(today_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## {datetime.now().strftime('%H:%M')}\n")
            f.write(f"- 任务: {episode['task']}\n")
            f.write(f"- 结果: {'成功' if episode['success'] else '失败'}\n")
            if episode['lesson']:
                f.write(f"- 经验: {episode['lesson']}\n")
        
        # 3. 更新GOAL进度
        goal_id = task_result.get('goal_id')
        if goal_id:
            # 更新对应Goal的进度
            pass
        
        # 4. 评估是否需要更新SOUL
        if task_result.get('is_significant'):
            # 重大成就，更新SOUL里程碑
            pass
    
    def sync_soul_with_others(self):
        """
        同步SOUL与其他层的关联
        定期执行，确保SOUL反映最新状态
        """
        soul_updates = []
        
        # 同步SKILL数量
        skill_count = self.skills.get('summary', {}).get('total_skills', 0)
        soul_updates.append(f"更新技能数量: {skill_count}")
        
        # 同步GOAL进度
        for goal in self.goals.get('active', []):
            if 'L3' in goal.get('title', ''):
                soul_updates.append(f"更新进化进度: L3 ({goal.get('progress')}%)")
        
        # 同步MEMORY精华
        recent_lessons = [m for m in self.memory.get('long_term', [])[-5:]]
        
        return soul_updates

def main():
    """主函数 - 演示"""
    engine = SSMGIntegrationEngine()
    context = engine.initialize_session()
    
    print("\n" + "=" * 70)
    print("📊 整合上下文摘要")
    print("=" * 70)
    print(f"\n身份: {context['soul']['core_identity']}")
    print(f"技能: {context['skills']['count']} 个 ({', '.join(context['skills']['categories'][:3])}...)")
    print(f"记忆: {context['memory']['long_term_count']} 条长期 + {len(context['memory']['recent_episodes'])} 天近期")
    print(f"目标: {context['goals']['active_count']} 个活跃")
    
    # 演示记忆检索
    print("\n" + "=" * 70)
    print("🔍 记忆检索演示: '进化'")
    print("=" * 70)
    memories = engine.recall_for_task("进化")
    for mem in memories:
        print(f"  • {mem}")

if __name__ == "__main__":
    main()
