#!/usr/bin/env python3
"""
A5L SKILL导师系统 - Phase 2 实现
知识蒸馏优化 + 训练集成 + 效果评估
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class TrainingSession:
    """训练会话"""
    session_id: str
    skill_id: str
    mentor_id: Optional[str]
    timestamp: str
    base_gain: float
    accelerated_gain: float
    multiplier: float
    success: bool
    knowledge_applied: List[str]

@dataclass
class SkillLearningState:
    """SKILL学习状态"""
    skill_id: str
    current_proficiency: float
    target_proficiency: float
    mentor_id: Optional[str]
    sessions_with_mentor: int
    total_gain_with_mentor: float
    avg_multiplier: float
    estimated_sessions_to_target: int

class EnhancedKnowledgeDistiller:
    """增强版知识蒸馏引擎"""
    
    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.load_registry()
        self.training_history = []
        
    def load_registry(self):
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)
    
    def distill_enhanced(self, mentor_id: str, student_id: str) -> Dict:
        """增强版知识蒸馏 - 考虑学生特点"""
        
        mentor_info = self.get_skill_info(mentor_id)
        student_info = self.get_skill_info(student_id)
        
        if not mentor_info or not student_info:
            return {'error': 'Skill not found'}
        
        # 1. 个性化模板
        templates = self.generate_personalized_templates(
            mentor_id, student_id, mentor_info, student_info
        )
        
        # 2. 针对性场景
        scenarios = self.generate_targeted_scenarios(
            mentor_id, student_id, mentor_info, student_info
        )
        
        # 3. 定制化建议
        tips = self.generate_customized_tips(
            mentor_id, student_id, mentor_info, student_info
        )
        
        # 4. 预期效果分析
        projection = self.project_learning_curve(
            student_info, mentor_info, templates, scenarios, tips
        )
        
        return {
            'mentor_id': mentor_id,
            'student_id': student_id,
            'personalized_templates': templates,
            'targeted_scenarios': scenarios,
            'customized_tips': tips,
            'projection': projection,
            'knowledge_depth_score': self.calculate_knowledge_depth(mentor_info),
            'transfer_readiness': self.calculate_transfer_readiness(mentor_info, student_info)
        }
    
    def generate_personalized_templates(self, mentor_id: str, student_id: str,
                                       mentor_info: Dict, student_info: Dict) -> List[Dict]:
        """生成个性化模板"""
        templates = []
        
        prof_gap = mentor_info['proficiency'] - student_info['proficiency']
        
        # 基础模板
        templates.append({
            'type': 'foundation',
            'name': f'{mentor_id}_基础流程',
            'content': f'从{student_info["proficiency"]:.0%}到{mentor_info["proficiency"]:.0%}的学习路径',
            'priority': 'high',
            'estimated_sessions': int(prof_gap / 0.003)
        })
        
        # 进阶模板
        if prof_gap > 0.3:
            templates.append({
                'type': 'advanced',
                'name': f'{mentor_id}_进阶优化',
                'content': '性能调优与边界处理策略',
                'priority': 'medium',
                'prerequisite': '完成基础流程'
            })
        
        # 专家模板
        if mentor_info['proficiency'] >= 0.95:
            templates.append({
                'type': 'expert',
                'name': f'{mentor_id}_专家技巧',
                'content': '精通级操作秘诀与常见陷阱',
                'priority': 'low',
                'prerequisite': '达到80%熟练度'
            })
        
        return templates
    
    def generate_targeted_scenarios(self, mentor_id: str, student_id: str,
                                   mentor_info: Dict, student_info: Dict) -> List[Dict]:
        """生成针对性训练场景"""
        scenarios = []
        category = mentor_info.get('category', 'general')
        
        # 基于学生当前水平生成场景
        current_prof = student_info['proficiency']
        
        if current_prof < 0.3:
            difficulty = 'beginner'
            scenario_types = ['基础练习', '简单应用', '概念理解']
        elif current_prof < 0.6:
            difficulty = 'intermediate'
            scenario_types = ['标准场景', '变体处理', '组合应用']
        else:
            difficulty = 'advanced'
            scenario_types = ['复杂场景', '边界情况', '性能优化']
        
        for i, scenario_type in enumerate(scenario_types):
            scenarios.append({
                'id': f'{student_id}_scenario_{i+1}',
                'type': scenario_type,
                'difficulty': difficulty,
                'mentor_guidance': f'参考{mentor_id}的执行模式',
                'expected_gain': 0.003 + (mentor_info['proficiency'] * 0.002),
                'validation_criteria': f'成功率>{mentor_info["success_rate"]*100:.0f}%'
            })
        
        return scenarios
    
    def generate_customized_tips(self, mentor_id: str, student_id: str,
                                mentor_info: Dict, student_info: Dict) -> List[Dict]:
        """生成定制化建议"""
        tips = []
        
        # 基于学生弱点的建议
        if student_info['success_rate'] < 0.7:
            tips.append({
                'category': 'reliability',
                'priority': 'critical',
                'tip': f'参考{mentor_id}的错误处理机制',
                'action': '重点练习异常场景'
            })
        
        if student_info['usage_count'] < 10:
            tips.append({
                'category': 'practice',
                'priority': 'high',
                'tip': '增加使用频率以积累经验',
                'action': '每天至少调用5次'
            })
        
        # 基于导师优势的建议
        if mentor_info['proficiency'] >= 0.90:
            tips.append({
                'category': 'optimization',
                'priority': 'medium',
                'tip': f'学习{mentor_id}的高效执行模式',
                'action': '对比输入输出差异'
            })
        
        # 通用建议
        tips.append({
            'category': 'methodology',
            'priority': 'medium',
            'tip': '遵循导师的最佳实践流程',
            'action': '先模仿，再创新'
        })
        
        return tips
    
    def project_learning_curve(self, student_info: Dict, mentor_info: Dict,
                               templates: List, scenarios: List, tips: List) -> Dict:
        """预测学习曲线"""
        
        current = student_info['proficiency']
        target = 0.80  # 专家级
        
        # 计算加速因子
        base_gain = 0.003
        template_bonus = len(templates) * 0.0005
        scenario_bonus = len(scenarios) * 0.0003
        mentor_bonus = (mentor_info['proficiency'] - 0.8) * 0.005 if mentor_info['proficiency'] > 0.8 else 0
        
        accelerated_gain = base_gain + template_bonus + scenario_bonus + mentor_bonus
        
        # 预测达到各阶段需要的次数
        milestones = {}
        for milestone, level in [('熟练', 0.60), ('进阶', 0.70), ('专家', 0.80), ('精通', 0.95)]:
            if current < level:
                gap = level - current
                sessions = int(gap / accelerated_gain)
                milestones[milestone] = {
                    'target_level': level,
                    'estimated_sessions': sessions,
                    'with_mentor': True
                }
        
        # 对比无导师的情况
        no_mentor_sessions = int((target - current) / base_gain) if current < target else 0
        with_mentor_sessions = milestones.get('专家', {}).get('estimated_sessions', 0)
        
        time_saved = no_mentor_sessions - with_mentor_sessions
        
        return {
            'current_level': current,
            'milestones': milestones,
            'accelerated_gain_per_session': round(accelerated_gain, 4),
            'comparison': {
                'without_mentor_sessions': no_mentor_sessions,
                'with_mentor_sessions': with_mentor_sessions,
                'time_saved_sessions': time_saved,
                'efficiency_improvement': f'{((no_mentor_sessions / with_mentor_sessions - 1) * 100):.0f}%' if with_mentor_sessions > 0 else 'N/A'
            }
        }
    
    def calculate_knowledge_depth(self, mentor_info: Dict) -> float:
        """计算知识深度分数"""
        prof_score = mentor_info['proficiency'] * 0.4
        success_score = mentor_info.get('success_rate', 0) * 0.3
        experience_score = min(mentor_info.get('usage_count', 0) / 100, 1.0) * 0.3
        return round(prof_score + success_score + experience_score, 3)
    
    def calculate_transfer_readiness(self, mentor_info: Dict, student_info: Dict) -> float:
        """计算知识转移准备度"""
        # 导师能力强 + 学生有基础 = 高转移准备度
        mentor_strength = mentor_info['proficiency']
        student_readiness = min(student_info['proficiency'] * 2, 1.0)  # 有基础的学生更容易接受
        return round((mentor_strength + student_readiness) / 2, 3)
    
    def get_skill_info(self, skill_id: str) -> Optional[Dict]:
        """获取SKILL信息"""
        for cat_name, cat_data in self.registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                if skill['id'] == skill_id:
                    info = dict(skill)
                    info['category'] = cat_name
                    return info
        return None

class IntegratedTrainingSystem:
    """集成训练系统 - 导师+训练一体化"""
    
    def __init__(self, registry_path: str, distiller: EnhancedKnowledgeDistiller):
        self.registry_path = registry_path
        self.distiller = distiller
        self.sessions = []
        self.load_registry()
    
    def load_registry(self):
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)
    
    def train_with_mentor(self, skill_id: str, mentor_id: str) -> TrainingSession:
        """在导师指导下训练"""
        
        # 1. 获取知识包
        knowledge = self.distiller.distill_enhanced(mentor_id, skill_id)
        
        # 2. 计算基础增益
        base_gain = random.uniform(0.002, 0.004)
        
        # 3. 应用导师加速
        multiplier = self.calculate_multiplier(knowledge)
        accelerated_gain = base_gain * multiplier
        
        # 4. 模拟训练成功
        success_rate = self.get_success_rate(skill_id)
        success = random.random() < (success_rate + 0.1)  # 导师提升10%成功率
        
        # 5. 如果成功，应用增益
        if success:
            self.update_proficiency(skill_id, accelerated_gain)
        
        # 6. 记录会话
        session = TrainingSession(
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}",
            skill_id=skill_id,
            mentor_id=mentor_id,
            timestamp=datetime.now().isoformat(),
            base_gain=base_gain,
            accelerated_gain=accelerated_gain if success else 0,
            multiplier=multiplier,
            success=success,
            knowledge_applied=[t['name'] for t in knowledge.get('personalized_templates', [])]
        )
        
        self.sessions.append(session)
        return session
    
    def calculate_multiplier(self, knowledge: Dict) -> float:
        """计算加速倍数"""
        base = 1.0
        
        # 模板加成
        templates = knowledge.get('personalized_templates', [])
        base += len(templates) * 0.15
        
        # 场景加成
        scenarios = knowledge.get('targeted_scenarios', [])
        base += len(scenarios) * 0.1
        
        # 建议加成
        tips = knowledge.get('customized_tips', [])
        base += len(tips) * 0.05
        
        # 深度加成
        depth = knowledge.get('knowledge_depth_score', 0)
        base += depth * 0.3
        
        return round(base, 2)
    
    def get_success_rate(self, skill_id: str) -> float:
        """获取SKILL成功率"""
        info = self.distiller.get_skill_info(skill_id)
        return info.get('success_rate', 0.85) if info else 0.85
    
    def update_proficiency(self, skill_id: str, gain: float):
        """更新SKILL熟练度"""
        for cat_data in self.registry.get('categories', {}).values():
            for skill in cat_data.get('skills', []):
                if skill['id'] == skill_id:
                    current = skill.get('proficiency', 0)
                    skill['proficiency'] = round(min(1.0, current + gain), 3)
                    skill['usage_count'] = skill.get('usage_count', 0) + 1
                    return
    
    def get_learning_state(self, skill_id: str) -> SkillLearningState:
        """获取SKILL学习状态"""
        info = self.distiller.get_skill_info(skill_id)
        if not info:
            return None
        
        # 统计该SKILL的训练记录
        skill_sessions = [s for s in self.sessions if s.skill_id == skill_id]
        
        with_mentor = [s for s in skill_sessions if s.mentor_id]
        total_gain = sum(s.accelerated_gain for s in with_mentor)
        avg_mult = sum(s.multiplier for s in with_mentor) / len(with_mentor) if with_mentor else 1.0
        
        current = info['proficiency']
        target = 0.80
        gap = max(0, target - current)
        avg_gain = total_gain / len(with_mentor) if with_mentor else 0.003
        
        return SkillLearningState(
            skill_id=skill_id,
            current_proficiency=current,
            target_proficiency=target,
            mentor_id=with_mentor[-1].mentor_id if with_mentor else None,
            sessions_with_mentor=len(with_mentor),
            total_gain_with_mentor=total_gain,
            avg_multiplier=round(avg_mult, 2),
            estimated_sessions_to_target=int(gap / avg_gain) if avg_gain > 0 else 999
        )
    
    def run_batch_training(self, skill_id: str, mentor_id: str, num_sessions: int = 5) -> List[TrainingSession]:
        """批量训练"""
        sessions = []
        
        print(f"\n🚀 批量训练: {skill_id} (导师: {mentor_id})")
        print(f"   计划训练次数: {num_sessions}")
        print("-" * 50)
        
        for i in range(num_sessions):
            session = self.train_with_mentor(skill_id, mentor_id)
            sessions.append(session)
            
            status = "✅" if session.success else "❌"
            print(f"   第{i+1}次 {status} 增益: +{session.accelerated_gain:.4f} "
                  f"(加速{session.multiplier}x)")
        
        # 显示训练后状态
        state = self.get_learning_state(skill_id)
        print(f"\n   训练后熟练度: {state.current_proficiency:.1%}")
        print(f"   预计达专家级: 还需{state.estimated_sessions_to_target}次")
        
        return sessions

class SkillManagementDashboard:
    """SKILL管理仪表盘"""
    
    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.load_registry()
    
    def load_registry(self):
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)
    
    def get_all_skills_status(self) -> Dict:
        """获取所有SKILL状态"""
        stats = {
            'total': 0,
            'by_level': {'master': 0, 'expert': 0, 'proficient': 0, 'beginner': 0},
            'by_category': {},
            'needs_mentor': [],
            'can_be_mentor': [],
            'avg_proficiency': 0
        }
        
        total_prof = 0
        
        for cat_name, cat_data in self.registry.get('categories', {}).items():
            stats['by_category'][cat_name] = {'count': 0, 'avg_prof': 0}
            cat_prof_sum = 0
            
            for skill in cat_data.get('skills', []):
                if skill.get('status') != 'active':
                    continue
                
                prof = skill.get('proficiency', 0)
                stats['total'] += 1
                total_prof += prof
                cat_prof_sum += prof
                
                # 分级统计
                if prof >= 0.95:
                    stats['by_level']['master'] += 1
                    stats['can_be_mentor'].append(skill['id'])
                elif prof >= 0.80:
                    stats['by_level']['expert'] += 1
                    stats['can_be_mentor'].append(skill['id'])
                elif prof >= 0.60:
                    stats['by_level']['proficient'] += 1
                else:
                    stats['by_level']['beginner'] += 1
                    if prof < 0.80:
                        stats['needs_mentor'].append({
                            'id': skill['id'],
                            'proficiency': prof,
                            'gap': 0.80 - prof
                        })
                
                stats['by_category'][cat_name]['count'] += 1
            
            if stats['by_category'][cat_name]['count'] > 0:
                stats['by_category'][cat_name]['avg_prof'] = round(
                    cat_prof_sum / stats['by_category'][cat_name]['count'], 2
                )
        
        if stats['total'] > 0:
            stats['avg_proficiency'] = round(total_prof / stats['total'], 2)
        
        # 排序需要导师的SKILL
        stats['needs_mentor'].sort(key=lambda x: x['gap'], reverse=True)
        
        return stats
    
    def print_dashboard(self):
        """打印仪表盘"""
        stats = self.get_all_skills_status()
        
        print("\n" + "=" * 60)
        print("📊 A5L SKILL管理仪表盘")
        print("=" * 60)
        
        print(f"\n📈 总体统计:")
        print(f"   总SKILL数: {stats['total']}")
        print(f"   平均熟练度: {stats['avg_proficiency']:.0%}")
        
        print(f"\n🏆 等级分布:")
        for level, count in stats['by_level'].items():
            icon = {'master': '💎', 'expert': '🥇', 'proficient': '🥈', 'beginner': '🥉'}.get(level, '')
            pct = count / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"   {icon} {level.capitalize()}: {count} ({pct:.1f}%)")
        
        print(f"\n📁 分类统计:")
        for cat, data in stats['by_category'].items():
            print(f"   {cat}: {data['count']}个 (平均{data['avg_prof']:.0%})")
        
        print(f"\n👨‍🏫 可担任导师: {len(stats['can_be_mentor'])}个")
        print(f"   示例: {', '.join(stats['can_be_mentor'][:5])}")
        
        print(f"\n📚 需要导师指导 (Top 5):")
        for skill in stats['needs_mentor'][:5]:
            print(f"   • {skill['id']}: {skill['proficiency']:.1%} (差距{skill['gap']:.1%})")
        
        print("\n" + "=" * 60)

def main():
    """测试Phase 2"""
    print("🧠 A5L SKILL导师系统 - Phase 2 测试")
    print("=" * 60)
    
    registry_path = "/workspace/projects/workspace/SKILL_REGISTRY.json"
    
    # 初始化组件
    distiller = EnhancedKnowledgeDistiller(registry_path)
    training_system = IntegratedTrainingSystem(registry_path, distiller)
    dashboard = SkillManagementDashboard(registry_path)
    
    # 1. 显示仪表盘
    dashboard.print_dashboard()
    
    # 2. 测试增强知识蒸馏
    print("\n🎯 增强知识蒸馏测试:")
    print("-" * 60)
    
    test_pairs = [
        ('architect_5l', 'stock_five_steps'),
        ('langzhu_wave_predictor', 'catalyst_tier_framework'),
    ]
    
    for student, mentor in test_pairs:
        knowledge = distiller.distill_enhanced(mentor, student)
        projection = knowledge.get('projection', {})
        
        print(f"\n📚 {student} ← {mentor}")
        print(f"   个性化模板: {len(knowledge.get('personalized_templates', []))}个")
        print(f"   针对性场景: {len(knowledge.get('targeted_scenarios', []))}个")
        print(f"   定制化建议: {len(knowledge.get('customized_tips', []))}个")
        
        comp = projection.get('comparison', {})
        print(f"   加速效果: 无导师需{comp.get('without_mentor_sessions', 'N/A')}次 → "
              f"有导师需{comp.get('with_mentor_sessions', 'N/A')}次")
        print(f"   效率提升: {comp.get('efficiency_improvement', 'N/A')}")
    
    # 3. 测试批量训练
    print("\n\n🏃 批量训练测试:")
    print("-" * 60)
    
    training_system.run_batch_training(
        'architect_5l', 
        'stock_five_steps', 
        num_sessions=3
    )
    
    print("\n" + "=" * 60)
    print("✅ Phase 2 测试完成")

if __name__ == "__main__":
    main()
