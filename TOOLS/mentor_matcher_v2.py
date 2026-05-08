#!/usr/bin/env python3
"""
导师匹配算法 v2.0 - 修复版
改进点:
1. 增加tags功能相似度计算
2. 增加导师教学能力评分
3. 分层策略: Beginner/Proficient/Expert用不同权重
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class MentorMatch:
    mentor_id: str
    match_score: float
    reason: str
    similarity_breakdown: Dict[str, float]

class ImprovedMentorMatcher:
    """改进版导师匹配器"""
    
    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.load_registry()
        self.mentor_teaching_history = {}  # 导师教学历史
        
    def load_registry(self):
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)
    
    def get_skill_info(self, skill_id: str) -> Dict:
        """获取SKILL信息"""
        for cat_data in self.registry.get('categories', {}).values():
            for skill in cat_data.get('skills', []):
                if skill['id'] == skill_id:
                    return skill
        return None
    
    def calculate_tags_similarity(self, skill_a: Dict, skill_b: Dict) -> float:
        """计算tags功能相似度"""
        tags_a = set(skill_a.get('tags', []))
        tags_b = set(skill_b.get('tags', []))
        
        if not tags_a or not tags_b:
            return 0.0
        
        intersection = len(tags_a & tags_b)
        union = len(tags_a | tags_b)
        
        return round(intersection / union, 2) if union > 0 else 0.0
    
    def get_teaching_ability(self, mentor_id: str) -> float:
        """获取导师教学能力评分 (0-1)"""
        # 从教学历史计算
        history = self.mentor_teaching_history.get(mentor_id, [])
        if not history:
            return 0.8  # 默认值
        
        # 计算成功率
        success_rate = sum(1 for h in history if h['success']) / len(history)
        # 计算平均增益
        avg_gain = sum(h['gain'] for h in history) / len(history)
        
        # 综合评分
        return round(0.6 * success_rate + 0.4 * min(1.0, avg_gain / 0.005), 2)
    
    def get_proficiency_tier(self, proficiency: float) -> str:
        """获取熟练度层级"""
        if proficiency < 0.60:
            return 'beginner'
        elif proficiency < 0.80:
            return 'proficient'
        else:
            return 'expert'
    
    def find_best_mentor(self, student_id: str) -> MentorMatch:
        """寻找最佳导师 - v2.0改进版"""
        student = self.get_skill_info(student_id)
        if not student:
            return None
        
        student_prof = student.get('proficiency', 0)
        student_tier = self.get_proficiency_tier(student_prof)
        student_cat = student.get('category', '')
        
        best_match = None
        best_score = 0
        
        # 遍历所有可能的导师
        for cat_data in self.registry.get('categories', {}).values():
            for skill in cat_data.get('skills', []):
                if skill['id'] == student_id:
                    continue
                if skill.get('status') != 'active':
                    continue
                
                mentor_prof = skill.get('proficiency', 0)
                if mentor_prof < 0.80:  # 导师必须Expert级以上
                    continue
                
                # 计算各项相似度
                mentor_cat = skill.get('category', '')
                
                # 1. 类别相似度
                cat_sim = 1.0 if student_cat == mentor_cat else 0.0
                
                # 2. 功能tags相似度
                tags_sim = self.calculate_tags_similarity(student, skill)
                
                # 3. 能力差距 (导师应比学生强，但不能太强)
                prof_gap = mentor_prof - student_prof
                if prof_gap < 0.10:  # 导师必须明显强于学生
                    continue
                if prof_gap > 0.50:  # 差距太大也不好教
                    gap_score = 0.5
                else:
                    gap_score = 1.0 - (prof_gap - 0.20) * 0.5
                
                # 4. 导师教学能力
                teaching_ability = self.get_teaching_ability(skill['id'])
                
                # 5. 经验加成
                usage_count = skill.get('usage_count', 0)
                exp_score = min(1.0, usage_count / 50)  # 使用50次满经验
                
                # 根据学生层级调整权重
                if student_tier == 'beginner':
                    # Beginner: 重类别匹配，重教学能力
                    weights = {
                        'category': 0.35,
                        'tags': 0.25,
                        'gap': 0.15,
                        'teaching': 0.20,
                        'experience': 0.05
                    }
                    reason = f"同类专家导师({mentor_prof:.0%}), 教学能力强"
                elif student_tier == 'proficient':
                    # Proficient: 重功能匹配，重经验
                    weights = {
                        'category': 0.25,
                        'tags': 0.35,
                        'gap': 0.15,
                        'teaching': 0.10,
                        'experience': 0.15
                    }
                    reason = f"功能相似({tags_sim:.0%} tags匹配), 经验丰富"
                else:
                    # Expert: 重能力，重突破潜力
                    weights = {
                        'category': 0.20,
                        'tags': 0.20,
                        'gap': 0.25,
                        'teaching': 0.10,
                        'experience': 0.25
                    }
                    reason = f"Master级导师({mentor_prof:.0%}), 突破潜力大"
                
                # 计算综合得分
                total_score = (
                    weights['category'] * cat_sim +
                    weights['tags'] * tags_sim +
                    weights['gap'] * gap_score +
                    weights['teaching'] * teaching_ability +
                    weights['experience'] * exp_score
                )
                
                if total_score > best_score:
                    best_score = total_score
                    best_match = MentorMatch(
                        mentor_id=skill['id'],
                        match_score=round(total_score, 2),
                        reason=reason,
                        similarity_breakdown={
                            'category': round(cat_sim, 2),
                            'tags': round(tags_sim, 2),
                            'gap': round(gap_score, 2),
                            'teaching': teaching_ability,
                            'experience': round(exp_score, 2)
                        }
                    )
        
        return best_match
    
    def update_teaching_history(self, mentor_id: str, student_id: str, 
                                success: bool, gain: float):
        """更新导师教学历史"""
        if mentor_id not in self.mentor_teaching_history:
            self.mentor_teaching_history[mentor_id] = []
        
        self.mentor_teaching_history[mentor_id].append({
            'student': student_id,
            'success': success,
            'gain': gain
        })

# 测试新算法
if __name__ == '__main__':
    matcher = ImprovedMentorMatcher('/workspace/projects/workspace/SKILL_REGISTRY.json')
    
    print("🧪 测试改进版导师匹配算法 v2.0")
    print("="*70)
    
    test_skills = [
        'langzhu_wave_predictor',  # Beginner, 需要教学型导师
        'architect_5l',            # Beginner, 需要系统型导师
        'yangguan_daodao',         # Proficient, 需要功能相似导师
    ]
    
    for skill_id in test_skills:
        match = matcher.find_best_mentor(skill_id)
        if match:
            print(f"\n{skill_id}:")
            print(f"  推荐导师: {match.mentor_id}")
            print(f"  匹配分数: {match.match_score:.2f}")
            print(f"  匹配原因: {match.reason}")
            print(f"  相似度分解: {match.similarity_breakdown}")
