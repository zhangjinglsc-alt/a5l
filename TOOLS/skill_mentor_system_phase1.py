#!/usr/bin/env python3
"""
A5L SKILL导师系统 - Phase 1 实现
导师匹配引擎 + 知识蒸馏引擎
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class SkillProfile:
    """SKILL档案"""
    id: str
    name: str
    category: str
    proficiency: float
    usage_count: int
    success_rate: float
    description: str = ""
    
@dataclass
class MentorMatch:
    """导师匹配结果"""
    student_id: str
    mentor_id: str
    match_score: float
    similarity_breakdown: Dict[str, float]
    reason: str

@dataclass
class KnowledgePackage:
    """知识包"""
    mentor_id: str
    templates: List[str]
    scenarios: List[str]
    tips: List[str]
    effectiveness_score: float

class SkillKnowledgeGraph:
    """SKILL知识图谱"""
    
    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.similarity_matrix = {}
        self.dependency_graph = {}
        self.load_data()
    
    def load_data(self):
        """加载SKILL数据"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)
        
        # 构建相似度矩阵
        self.build_similarity_matrix()
    
    def build_similarity_matrix(self):
        """构建SKILL相似度矩阵"""
        skills = []
        for cat_name, cat_data in self.registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                if skill.get('status') == 'active':
                    skills.append({
                        'id': skill['id'],
                        'category': cat_name,
                        'proficiency': skill.get('proficiency', 0),
                        'description': skill.get('description', '')
                    })
        
        # 计算两两相似度
        for skill_a in skills:
            self.similarity_matrix[skill_a['id']] = {}
            for skill_b in skills:
                if skill_a['id'] != skill_b['id']:
                    similarity = self.calculate_similarity(skill_a, skill_b)
                    self.similarity_matrix[skill_a['id']][skill_b['id']] = similarity
    
    def calculate_similarity(self, skill_a: Dict, skill_b: Dict) -> float:
        """计算两个SKILL的相似度 (0-1)"""
        scores = []
        
        # 1. 类别相似度 (40%)
        if skill_a['category'] == skill_b['category']:
            scores.append(0.4)
        else:
            # 检查是否有共同关键词
            cat_a_words = set(skill_a['category'].replace('_', ' ').replace('-', ' ').split())
            cat_b_words = set(skill_b['category'].replace('_', ' ').replace('-', ' ').split())
            overlap = len(cat_a_words & cat_b_words)
            scores.append(0.4 * (overlap / max(len(cat_a_words), len(cat_b_words), 1)))
        
        # 2. 描述相似度 (30%) - 简单关键词匹配
        desc_a = set(skill_a.get('description', '').lower().split())
        desc_b = set(skill_b.get('description', '').lower().split())
        if desc_a and desc_b:
            overlap = len(desc_a & desc_b)
            scores.append(0.3 * (overlap / max(len(desc_a), len(desc_b), 1)))
        else:
            scores.append(0)
        
        # 3. 熟练度互补性 (20%) - 高熟练度更适合指导
        prof_diff = skill_b['proficiency'] - skill_a['proficiency']
        if prof_diff > 0:
            scores.append(0.2 * min(prof_diff * 2, 1.0))  # 熟练度差距越大，指导价值越高
        else:
            scores.append(0)
        
        # 4. 命名相似度 (10%)
        name_a = skill_a['id'].replace('_', '').replace('-', '').lower()
        name_b = skill_b['id'].replace('_', '').replace('-', '').lower()
        common_chars = set(name_a) & set(name_b)
        scores.append(0.1 * (len(common_chars) / max(len(name_a), len(name_b), 1)))
        
        return min(sum(scores), 1.0)
    
    def get_similarity(self, skill_a: str, skill_b: str) -> float:
        """获取两个SKILL的相似度"""
        return self.similarity_matrix.get(skill_a, {}).get(skill_b, 0)
    
    def get_most_similar(self, skill_id: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """获取最相似的SKILL"""
        similarities = self.similarity_matrix.get(skill_id, {})
        sorted_skills = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        return sorted_skills[:top_n]

class MentorMatcher:
    """导师匹配引擎"""
    
    def __init__(self, knowledge_graph: SkillKnowledgeGraph, min_mentor_proficiency: float = 0.80):
        self.kg = knowledge_graph
        self.min_proficiency = min_mentor_proficiency
        self.match_history = []
    
    def get_eligible_mentors(self, student_id: str) -> List[SkillProfile]:
        """获取有资格作为导师的SKILL"""
        mentors = []
        
        for cat_name, cat_data in self.kg.registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                if skill.get('status') != 'active':
                    continue
                if skill['id'] == student_id:
                    continue
                
                proficiency = skill.get('proficiency', 0)
                if proficiency >= self.min_proficiency:
                    mentors.append(SkillProfile(
                        id=skill['id'],
                        name=skill.get('name', skill['id']),
                        category=cat_name,
                        proficiency=proficiency,
                        usage_count=skill.get('usage_count', 0),
                        success_rate=skill.get('success_rate', 0),
                        description=skill.get('description', '')
                    ))
        
        return mentors
    
    def calculate_match_score(self, mentor: SkillProfile, student_id: str) -> Tuple[float, Dict]:
        """计算匹配分数"""
        breakdown = {}
        
        # 1. 类别相似度 (40%)
        student_category = self.get_skill_category(student_id)
        if mentor.category == student_category:
            breakdown['category'] = 0.4
        else:
            similarity = self.kg.get_similarity(mentor.id, student_id)
            breakdown['category'] = 0.4 * similarity
        
        # 2. 功能相似度 - 基于知识图谱 (30%)
        func_similarity = self.kg.get_similarity(mentor.id, student_id)
        breakdown['functional'] = 0.3 * func_similarity
        
        # 3. 导师能力加成 (20%)
        # 熟练度越高、成功率越高，指导能力越强
        ability_score = (mentor.proficiency * 0.5 + mentor.success_rate * 0.5)
        breakdown['mentor_ability'] = 0.2 * ability_score
        
        # 4. 使用频率权重 (10%)
        # 使用越多，经验越丰富
        usage_score = min(mentor.usage_count / 100, 1.0)
        breakdown['experience'] = 0.1 * usage_score
        
        total_score = sum(breakdown.values())
        return total_score, breakdown
    
    def find_best_mentor(self, student_id: str) -> Optional[MentorMatch]:
        """为学习SKILL寻找最佳导师"""
        candidates = self.get_eligible_mentors(student_id)
        
        if not candidates:
            return None
        
        matches = []
        for mentor in candidates:
            score, breakdown = self.calculate_match_score(mentor, student_id)
            matches.append((mentor, score, breakdown))
        
        # 排序选择最佳
        matches.sort(key=lambda x: x[1], reverse=True)
        best_mentor, best_score, best_breakdown = matches[0]
        
        # 生成推荐理由
        reason = self.generate_reason(best_mentor, student_id, best_breakdown)
        
        match_result = MentorMatch(
            student_id=student_id,
            mentor_id=best_mentor.id,
            match_score=best_score,
            similarity_breakdown=best_breakdown,
            reason=reason
        )
        
        # 记录匹配历史
        self.match_history.append({
            'timestamp': datetime.now().isoformat(),
            'student': student_id,
            'mentor': best_mentor.id,
            'score': best_score
        })
        
        return match_result
    
    def generate_reason(self, mentor: SkillProfile, student_id: str, breakdown: Dict) -> str:
        """生成推荐理由"""
        reasons = []
        
        if breakdown.get('category', 0) > 0.3:
            reasons.append(f"同属{mentor.category}类别")
        
        if breakdown.get('functional', 0) > 0.2:
            reasons.append("功能高度相似")
        
        if mentor.proficiency >= 0.95:
            reasons.append(f"精通级导师({mentor.proficiency:.0%})")
        elif mentor.proficiency >= 0.80:
            reasons.append(f"专家级导师({mentor.proficiency:.0%})")
        
        if mentor.usage_count > 50:
            reasons.append(f"经验丰富({mentor.usage_count}次使用)")
        
        return "; ".join(reasons) if reasons else "综合匹配度最高"
    
    def get_skill_category(self, skill_id: str) -> str:
        """获取SKILL所属类别"""
        for cat_name, cat_data in self.kg.registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                if skill['id'] == skill_id:
                    return cat_name
        return ""
    
    def get_match_history(self, skill_id: str = None) -> List[Dict]:
        """获取匹配历史"""
        if skill_id:
            return [m for m in self.match_history if m['student'] == skill_id or m['mentor'] == skill_id]
        return self.match_history

class KnowledgeDistiller:
    """知识蒸馏引擎"""
    
    def __init__(self, knowledge_graph: SkillKnowledgeGraph):
        self.kg = knowledge_graph
    
    def distill(self, mentor_id: str) -> KnowledgePackage:
        """从精通SKILL提取可转移知识"""
        
        # 获取导师信息
        mentor_info = self.get_skill_info(mentor_id)
        if not mentor_info:
            return KnowledgePackage(mentor_id=mentor_id, templates=[], scenarios=[], tips=[], effectiveness_score=0)
        
        # 1. 提取最佳实践模板
        templates = self.extract_templates(mentor_id, mentor_info)
        
        # 2. 生成训练场景
        scenarios = self.generate_scenarios(mentor_id, mentor_info)
        
        # 3. 编译优化建议
        tips = self.compile_tips(mentor_id, mentor_info)
        
        # 4. 计算知识包效果分数
        effectiveness = self.calculate_effectiveness(mentor_info)
        
        return KnowledgePackage(
            mentor_id=mentor_id,
            templates=templates,
            scenarios=scenarios,
            tips=tips,
            effectiveness_score=effectiveness
        )
    
    def extract_templates(self, skill_id: str, skill_info: Dict) -> List[str]:
        """提取最佳实践模板"""
        templates = []
        
        # 基于熟练度和成功率生成模板
        proficiency = skill_info.get('proficiency', 0)
        
        if proficiency >= 0.95:
            templates.append(f"精通级工作流: {skill_id}的标准执行流程")
            templates.append(f"高级优化: {skill_id}的性能调优模式")
            templates.append(f"错误处理: {skill_id}的异常恢复策略")
        elif proficiency >= 0.80:
            templates.append(f"标准流程: {skill_id}的核心执行步骤")
            templates.append(f"最佳实践: {skill_id}的常见应用场景")
        
        return templates
    
    def generate_scenarios(self, skill_id: str, skill_info: Dict) -> List[str]:
        """生成训练场景"""
        scenarios = []
        category = skill_info.get('category', 'general')
        
        # 基于类别生成场景
        scenario_map = {
            'investment_analysis': [
                '市场分析场景',
                '股票筛选场景', 
                '风险评估场景',
                '趋势预测场景'
            ],
            'data_research': [
                '数据获取场景',
                '数据清洗场景',
                '数据验证场景',
                '数据报告场景'
            ],
            'trading_systems': [
                '交易信号场景',
                '仓位管理场景',
                '止损止盈场景',
                '组合调仓场景'
            ],
            'default': [
                '标准执行场景',
                '边界处理场景',
                '性能优化场景',
                '错误恢复场景'
            ]
        }
        
        scenarios = scenario_map.get(category, scenario_map['default'])
        return scenarios[:4]  # 最多4个场景
    
    def compile_tips(self, skill_id: str, skill_info: Dict) -> List[str]:
        """编译优化建议"""
        tips = []
        
        usage_count = skill_info.get('usage_count', 0)
        success_rate = skill_info.get('success_rate', 0)
        
        if usage_count > 100:
            tips.append(f"高频使用优化: 基于{usage_count}次调用的性能建议")
        
        if success_rate > 0.9:
            tips.append(f"高可靠性策略: 成功率{success_rate:.0%}的秘诀")
        elif success_rate < 0.7:
            tips.append(f"稳定性改进: 从当前{success_rate:.0%}提升的方法")
        
        tips.append(f"输入优化: 如何为{skill_id}准备最佳输入")
        tips.append(f"输出处理: 高效利用{skill_id}的结果")
        
        return tips
    
    def calculate_effectiveness(self, skill_info: Dict) -> float:
        """计算知识包效果分数"""
        proficiency = skill_info.get('proficiency', 0)
        success_rate = skill_info.get('success_rate', 0)
        usage_count = skill_info.get('usage_count', 0)
        
        # 效果 = 熟练度 * 0.4 + 成功率 * 0.4 + 使用经验 * 0.2
        experience_score = min(usage_count / 200, 1.0)
        
        effectiveness = (
            proficiency * 0.4 +
            success_rate * 0.4 +
            experience_score * 0.2
        )
        
        return round(effectiveness, 3)
    
    def get_skill_info(self, skill_id: str) -> Optional[Dict]:
        """获取SKILL信息"""
        for cat_name, cat_data in self.kg.registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                if skill['id'] == skill_id:
                    info = dict(skill)
                    info['category'] = cat_name
                    return info
        return None

class LearningAccelerator:
    """学习加速器"""
    
    def __init__(self, matcher: MentorMatcher, distiller: KnowledgeDistiller):
        self.matcher = matcher
        self.distiller = distiller
    
    def accelerate_learning(self, student_id: str) -> Dict:
        """加速指定SKILL的学习"""
        
        # 1. 找到导师
        match = self.matcher.find_best_mentor(student_id)
        if not match:
            return {
                'student_id': student_id,
                'status': 'no_mentor_available',
                'message': '没有找到合适的导师SKILL'
            }
        
        # 2. 获取知识包
        knowledge = self.distiller.distill(match.mentor_id)
        
        # 3. 计算加速效果
        acceleration = self.calculate_acceleration(student_id, knowledge)
        
        return {
            'student_id': student_id,
            'mentor_id': match.mentor_id,
            'match_score': match.match_score,
            'match_reason': match.reason,
            'knowledge_package': {
                'templates_count': len(knowledge.templates),
                'scenarios_count': len(knowledge.scenarios),
                'tips_count': len(knowledge.tips),
                'effectiveness': knowledge.effectiveness_score
            },
            'acceleration': acceleration,
            'status': 'accelerated'
        }
    
    def calculate_acceleration(self, student_id: str, knowledge: KnowledgePackage) -> Dict:
        """计算学习加速效果"""
        
        # 基础增益 (每次训练的正常增益)
        base_gain = 0.003  # 约0.3%
        
        # 知识包加成
        knowledge_bonus = (
            len(knowledge.templates) * 0.1 +
            len(knowledge.scenarios) * 0.05 +
            len(knowledge.tips) * 0.03
        )
        
        # 效果分数加成
        effectiveness_multiplier = 1.0 + (knowledge.effectiveness_score * 0.5)
        
        # 总加速倍数
        total_multiplier = (1.0 + knowledge_bonus) * effectiveness_multiplier
        
        # 加速后增益
        accelerated_gain = base_gain * total_multiplier
        
        return {
            'base_gain': base_gain,
            'accelerated_gain': round(accelerated_gain, 4),
            'multiplier': round(total_multiplier, 2),
            'estimated_sessions_to_expert': self.estimate_sessions(student_id, accelerated_gain),
            'time_saved_percentage': round((1 - 1/total_multiplier) * 100, 1)
        }
    
    def estimate_sessions(self, student_id: str, gain_per_session: float) -> int:
        """估计达到专家级需要的训练次数"""
        # 获取当前熟练度
        current_prof = self.get_current_proficiency(student_id)
        target_prof = 0.80  # 专家级
        
        if current_prof >= target_prof:
            return 0
        
        gap = target_prof - current_prof
        sessions = int(gap / gain_per_session)
        
        return max(sessions, 1)
    
    def get_current_proficiency(self, skill_id: str) -> float:
        """获取SKILL当前熟练度"""
        for cat_data in self.matcher.kg.registry.get('categories', {}).values():
            for skill in cat_data.get('skills', []):
                if skill['id'] == skill_id:
                    return skill.get('proficiency', 0)
        return 0

def main():
    """测试导师系统"""
    print("🧠 A5L SKILL导师系统 - Phase 1 测试")
    print("=" * 60)
    
    # 初始化
    registry_path = "/workspace/projects/workspace/SKILL_REGISTRY.json"
    kg = SkillKnowledgeGraph(registry_path)
    matcher = MentorMatcher(kg)
    distiller = KnowledgeDistiller(kg)
    accelerator = LearningAccelerator(matcher, distiller)
    
    # 测试案例1: 为低熟练度SKILL找导师
    test_skills = [
        "architect_5l",  # 熟练度很低
        "langzhu_wave_predictor",  # 中等熟练度
        "technical_analysis",  # 接近专家级
    ]
    
    print("\n🎯 导师匹配测试:")
    print("-" * 60)
    
    for skill_id in test_skills:
        result = accelerator.accelerate_learning(skill_id)
        
        if result['status'] == 'accelerated':
            print(f"\n📚 SKILL: {skill_id}")
            print(f"   匹配导师: {result['mentor_id']}")
            print(f"   匹配分数: {result['match_score']:.2f}")
            print(f"   推荐理由: {result['match_reason']}")
            print(f"   知识包: {result['knowledge_package']['templates_count']}模板, "
                  f"{result['knowledge_package']['scenarios_count']}场景, "
                  f"{result['knowledge_package']['tips_count']}建议")
            print(f"   加速效果: {result['acceleration']['multiplier']}x")
            print(f"   预计达到专家级: {result['acceleration']['estimated_sessions_to_expert']}次训练")
        else:
            print(f"\n⚠️ {skill_id}: {result['message']}")
    
    # 显示相似度矩阵示例
    print("\n\n🔗 SKILL相似度示例 (technical_analysis):")
    print("-" * 60)
    similar = kg.get_most_similar("technical_analysis", 5)
    for skill_id, similarity in similar:
        print(f"   {skill_id}: {similarity:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ 导师系统 Phase 1 测试完成")

if __name__ == "__main__":
    main()
