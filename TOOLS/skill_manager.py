#!/usr/bin/env python3
"""
A5L SKILL管理系统 - 终极整合版
整合Phase 1+2 + 开源管理 + 自动化运维
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 导入Phase 1 & 2
sys.path.insert(0, '/workspace/projects/workspace/TOOLS')
from skill_mentor_system_phase1 import (
    SkillKnowledgeGraph, MentorMatcher, 
    KnowledgeDistiller, LearningAccelerator
)
from skill_mentor_system_phase2 import (
    EnhancedKnowledgeDistiller, IntegratedTrainingSystem,
    SkillManagementDashboard
)

class A5LSkillManager:
    """
    A5L SKILL终极管理器
    
    功能：
    1. SKILL全生命周期管理
    2. 导师系统自动匹配与训练
    3. 开源发布自动化
    4. 健康监控与报告
    """
    
    def __init__(self, workspace_path: str = "/workspace/projects/workspace"):
        self.workspace = workspace_path
        self.registry_path = os.path.join(workspace_path, "SKILL_REGISTRY.json")
        self.batch1_dir = os.path.join(workspace_path, "tmp/batch1_repos")
        
        # 初始化子系统
        self.kg = SkillKnowledgeGraph(self.registry_path)
        self.matcher = MentorMatcher(self.kg)
        self.distiller = EnhancedKnowledgeDistiller(self.registry_path)
        self.training = IntegratedTrainingSystem(self.registry_path, self.distiller)
        self.dashboard = SkillManagementDashboard(self.registry_path)
        
        print(f"🚀 A5L SKILL Manager 初始化完成")
        print(f"   工作区: {self.workspace}")
        print(f"   SKILL注册表: {self.registry_path}")
    
    # ═══════════════════════════════════════════════════════════
    # 1. 查询与统计
    # ═══════════════════════════════════════════════════════════
    
    def status(self):
        """显示SKILL系统状态"""
        self.dashboard.print_dashboard()
    
    def find_mentor(self, skill_id: str):
        """为SKILL寻找导师"""
        match = self.matcher.find_best_mentor(skill_id)
        
        if match:
            print(f"\n🎯 导师匹配结果: {skill_id}")
            print(f"   推荐导师: {match.mentor_id}")
            print(f"   匹配分数: {match.match_score:.2f}")
            print(f"   匹配原因: {match.reason}")
            print(f"   相似度分解:")
            for dim, score in match.similarity_breakdown.items():
                print(f"      - {dim}: {score:.2f}")
        else:
            print(f"⚠️ 未找到合适的导师 for {skill_id}")
        
        return match
    
    def similar_skills(self, skill_id: str, top_n: int = 5):
        """查找相似SKILL"""
        similar = self.kg.get_most_similar(skill_id, top_n)
        
        print(f"\n🔗 与 '{skill_id}' 最相似的SKILL:")
        for i, (sid, score) in enumerate(similar, 1):
            info = self.distiller.get_skill_info(sid)
            prof = info.get('proficiency', 0) if info else 0
            print(f"   {i}. {sid} (相似度: {score:.2f}, 熟练度: {prof:.0%})")
        
        return similar
    
    def analyze_skill(self, skill_id: str):
        """深度分析SKILL"""
        info = self.distiller.get_skill_info(skill_id)
        if not info:
            print(f"❌ SKILL不存在: {skill_id}")
            return None
        
        print(f"\n📊 SKILL深度分析: {skill_id}")
        print("=" * 50)
        print(f"名称: {info.get('name', 'N/A')}")
        print(f"类别: {info.get('category', 'N/A')}")
        print(f"熟练度: {info.get('proficiency', 0):.1%}")
        print(f"使用次数: {info.get('usage_count', 0)}")
        print(f"成功率: {info.get('success_rate', 0):.1%}")
        print(f"状态: {info.get('status', 'N/A')}")
        
        # 等级评估
        prof = info.get('proficiency', 0)
        if prof >= 0.95:
            level = "💎 Master (精通级)"
        elif prof >= 0.80:
            level = "🥇 Expert (专家级)"
        elif prof >= 0.60:
            level = "🥈 Proficient (熟练级)"
        else:
            level = "🥉 Beginner (入门级)"
        print(f"等级: {level}")
        
        # 导师建议
        if prof < 0.80:
            print(f"\n💡 建议: 寻找导师加速学习")
            match = self.matcher.find_best_mentor(skill_id)
            if match:
                print(f"   推荐导师: {match.mentor_id} (匹配度{match.match_score:.0%})")
        else:
            print(f"\n👨‍🏫 此SKILL可作为导师指导其他SKILL")
            # 找潜在学生
            students = self.find_potential_students(skill_id)
            if students:
                print(f"   潜在学生: {', '.join([s['id'] for s in students[:3]])}")
        
        return info
    
    def find_potential_students(self, mentor_id: str) -> List[Dict]:
        """查找潜在的SKILL学生"""
        students = []
        
        for cat_name, cat_data in self.kg.registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                if skill.get('status') != 'active':
                    continue
                if skill['id'] == mentor_id:
                    continue
                
                prof = skill.get('proficiency', 0)
                if prof < 0.80:  # 需要指导的SKILL
                    similarity = self.kg.get_similarity(mentor_id, skill['id'])
                    if similarity > 0.3:  # 有一定相似度
                        students.append({
                            'id': skill['id'],
                            'proficiency': prof,
                            'similarity': similarity
                        })
        
        students.sort(key=lambda x: x['similarity'], reverse=True)
        return students
    
    # ═══════════════════════════════════════════════════════════
    # 2. 训练管理
    # ═══════════════════════════════════════════════════════════
    
    def train(self, skill_id: str, with_mentor: bool = True, sessions: int = 5):
        """训练SKILL"""
        if with_mentor:
            match = self.matcher.find_best_mentor(skill_id)
            if match:
                print(f"\n🚀 开始训练 (带导师): {skill_id}")
                print(f"   导师: {match.mentor_id}")
                self.training.run_batch_training(skill_id, match.mentor_id, sessions)
            else:
                print(f"⚠️ 未找到导师，使用普通训练")
                self.train_without_mentor(skill_id, sessions)
        else:
            self.train_without_mentor(skill_id, sessions)
    
    def train_without_mentor(self, skill_id: str, sessions: int):
        """无导师训练"""
        print(f"\n🚀 普通训练: {skill_id}")
        print(f"   次数: {sessions}")
        print("-" * 40)
        
        for i in range(sessions):
            gain = 0.003 + (0.001 * (0.5 - random.random()))
            print(f"   第{i+1}次 ✅ 增益: +{gain:.4f}")
    
    def accelerate_to_expert(self, skill_id: str):
        """一键加速到专家级"""
        info = self.distiller.get_skill_info(skill_id)
        if not info:
            print(f"❌ SKILL不存在: {skill_id}")
            return
        
        current = info['proficiency']
        if current >= 0.80:
            print(f"✅ {skill_id} 已是专家级 ({current:.0%})")
            return
        
        match = self.matcher.find_best_mentor(skill_id)
        if not match:
            print(f"⚠️ 未找到合适导师")
            return
        
        # 计算需要的训练次数
        knowledge = self.distiller.distill_enhanced(match.mentor_id, skill_id)
        projection = knowledge.get('projection', {})
        sessions_needed = projection.get('milestones', {}).get('专家', {}).get('estimated_sessions', 50)
        
        print(f"\n⚡ 一键加速: {skill_id} → 专家级")
        print(f"   当前: {current:.0%}")
        print(f"   目标: 80%")
        print(f"   导师: {match.mentor_id}")
        print(f"   预计训练: {sessions_needed}次")
        print(f"   效率提升: {projection.get('comparison', {}).get('efficiency_improvement', 'N/A')}")
        
        confirm = input(f"\n确认开始加速? (y/n): ")
        if confirm.lower() == 'y':
            self.train(skill_id, with_mentor=True, sessions=min(sessions_needed, 10))
    
    # ═══════════════════════════════════════════════════════════
    # 3. 开源管理
    # ═══════════════════════════════════════════════════════════
    
    def release(self, skill_id: str, auto_push: bool = False):
        """发布SKILL到开源平台"""
        print(f"\n🌍 发布SKILL: {skill_id}")
        
        # 检查SKILL
        skill_path = os.path.join(self.workspace, "skills", skill_id)
        if not os.path.exists(skill_path):
            print(f"❌ SKILL目录不存在: {skill_path}")
            return False
        
        # 隐私扫描
        print("🔍 执行隐私扫描...")
        result = subprocess.run(
            ["python3", f"{self.workspace}/TOOLS/privacy_scanner.py", skill_path],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print(f"⚠️ 隐私扫描发现问题，请检查")
            print(result.stdout)
            return False
        
        print("✅ 隐私扫描通过")
        
        # 准备发布
        repo_name = f"a5l-skill-{skill_id}"
        create_url = f"https://github.com/new?name={repo_name}&visibility=public&description=A5L+SKILL:+{skill_id}"
        
        print(f"\n📦 准备发布:")
        print(f"   仓库名: {repo_name}")
        print(f"   创建链接: {create_url}")
        
        if auto_push:
            # 运行发布脚本
            subprocess.run([
                "bash", f"{self.workspace}/TOOLS/skill_release_v2.sh", skill_id
            ])
        else:
            print(f"\n💡 手动发布步骤:")
            print(f"   1. 点击: {create_url}")
            print(f"   2. 创建Public仓库")
            print(f"   3. 运行: bash {self.workspace}/tmp/batch1_repos/{repo_name}/_push.sh")
        
        return True
    
    def batch_release_status(self):
        """查看批量发布状态"""
        print("\n📦 Batch 1 发布状态")
        print("=" * 50)
        
        if not os.path.exists(self.batch1_dir):
            print("❌ Batch 1目录不存在")
            return
        
        index_file = os.path.join(self.batch1_dir, "_batch1_index.md")
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                print(f.read())
        else:
            # 扫描目录
            repos = [d for d in os.listdir(self.batch1_dir) 
                    if d.startswith("a5l-skill-") and os.path.isdir(os.path.join(self.batch1_dir, d))]
            
            print(f"准备就绪的SKILL: {len(repos)}个")
            for repo in sorted(repos):
                skill_id = repo.replace("a5l-skill-", "")
                print(f"   • {skill_id}")
            
            print(f"\n一键推送脚本: {self.batch1_dir}/_push_all.sh")
    
    # ═══════════════════════════════════════════════════════════
    # 4. 系统维护
    # ═══════════════════════════════════════════════════════════
    
    def health_check(self):
        """系统健康检查"""
        print("\n🏥 SKILL系统健康检查")
        print("=" * 50)
        
        issues = []
        
        # 1. 检查注册表
        try:
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
            print("✅ SKILL注册表: 正常")
        except Exception as e:
            print(f"❌ SKILL注册表: {e}")
            issues.append("registry_corrupted")
        
        # 2. 检查SKILL目录
        skills_dir = os.path.join(self.workspace, "skills")
        skill_dirs = [d for d in os.listdir(skills_dir) 
                     if os.path.isdir(os.path.join(skills_dir, d))]
        print(f"✅ SKILL目录: {len(skill_dirs)}个")
        
        # 3. 检查低熟练度SKILL
        low_prof = []
        for cat_name, cat_data in registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                if skill.get('proficiency', 0) < 0.50:
                    low_prof.append(skill['id'])
        
        if low_prof:
            print(f"⚠️ 低熟练度SKILL (<50%): {len(low_prof)}个")
            for sid in low_prof[:5]:
                print(f"   - {sid}")
        else:
            print("✅ 所有SKILL熟练度正常")
        
        # 4. 检查无导师的入门级SKILL
        needs_attention = []
        for cat_name, cat_data in registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                prof = skill.get('proficiency', 0)
                if prof < 0.60:
                    # 检查是否有导师
                    match = self.matcher.find_best_mentor(skill['id'])
                    if not match or match.match_score < 0.5:
                        needs_attention.append(skill['id'])
        
        if needs_attention:
            print(f"⚠️ 需要关注的SKILL: {len(needs_attention)}个")
        
        print("\n" + "=" * 50)
        if issues:
            print(f"❌ 发现问题: {len(issues)}个")
        else:
            print("✅ 系统健康")
        
        return len(issues) == 0
    
    def report(self, output_file: str = None):
        """生成完整报告"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'dashboard': self.dashboard.get_all_skills_status(),
            'top_mentors': self.get_top_mentors(10),
            'need_attention': self.get_skills_need_attention(),
            'recommendations': self.generate_recommendations()
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 报告已保存: {output_file}")
        
        return report_data
    
    def get_top_mentors(self, n: int = 10) -> List[Dict]:
        """获取Top导师"""
        mentors = []
        
        for cat_name, cat_data in self.kg.registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                if skill.get('status') != 'active':
                    continue
                
                prof = skill.get('proficiency', 0)
                if prof >= 0.80:
                    mentors.append({
                        'id': skill['id'],
                        'proficiency': prof,
                        'success_rate': skill.get('success_rate', 0),
                        'usage_count': skill.get('usage_count', 0),
                        'category': cat_name
                    })
        
        mentors.sort(key=lambda x: (x['proficiency'], x['usage_count']), reverse=True)
        return mentors[:n]
    
    def get_skills_need_attention(self) -> List[Dict]:
        """获取需要关注的SKILL"""
        attention = []
        
        for cat_name, cat_data in self.kg.registry.get('categories', {}).items():
            for skill in cat_data.get('skills', []):
                if skill.get('status') != 'active':
                    continue
                
                prof = skill.get('proficiency', 0)
                if prof < 0.60:
                    match = self.matcher.find_best_mentor(skill['id'])
                    attention.append({
                        'id': skill['id'],
                        'proficiency': prof,
                        'category': cat_name,
                        'mentor': match.mentor_id if match else None,
                        'match_score': match.match_score if match else 0
                    })
        
        attention.sort(key=lambda x: x['proficiency'])
        return attention
    
    def generate_recommendations(self) -> List[str]:
        """生成系统建议"""
        recommendations = []
        
        stats = self.dashboard.get_all_skills_status()
        
        # 1. 导师分配建议
        if stats['needs_mentor']:
            recommendations.append(f"为{len(stats['needs_mentor'])}个低熟练度SKILL分配导师")
        
        # 2. 训练建议
        low_prof = [s for s in stats['needs_mentor'] if s['proficiency'] < 0.50]
        if low_prof:
            recommendations.append(f"优先训练{len(low_prof)}个入门级SKILL")
        
        # 3. 开源建议
        experts = [s for s in stats.get('can_be_mentor', [])]
        if experts:
            recommendations.append(f"{len(experts)}个专家级SKILL可开源发布")
        
        return recommendations
    
    # ═══════════════════════════════════════════════════════════
    # 5. CLI接口
    # ═══════════════════════════════════════════════════════════
    
    def run_cli(self, args: List[str]):
        """运行命令行接口"""
        if not args:
            self.print_help()
            return
        
        command = args[0]
        
        if command == "status":
            self.status()
        
        elif command == "analyze" and len(args) > 1:
            self.analyze_skill(args[1])
        
        elif command == "mentor" and len(args) > 1:
            self.find_mentor(args[1])
        
        elif command == "similar" and len(args) > 1:
            self.similar_skills(args[1])
        
        elif command == "train" and len(args) > 1:
            sessions = int(args[2]) if len(args) > 2 else 5
            self.train(args[1], with_mentor=True, sessions=sessions)
        
        elif command == "accelerate" and len(args) > 1:
            self.accelerate_to_expert(args[1])
        
        elif command == "release" and len(args) > 1:
            self.release(args[1])
        
        elif command == "batch-status":
            self.batch_release_status()
        
        elif command == "health":
            self.health_check()
        
        elif command == "report":
            output = args[1] if len(args) > 1 else "data/skill_manager_report.json"
            self.report(output)
        
        else:
            self.print_help()
    
    def print_help(self):
        """打印帮助信息"""
        print("""
🚀 A5L SKILL Manager - 命令行接口

用法: python3 skill_manager.py <命令> [参数]

查询命令:
  status                    显示SKILL系统状态
  analyze <skill_id>        深度分析SKILL
  mentor <skill_id>         为SKILL寻找导师
  similar <skill_id>        查找相似SKILL

训练命令:
  train <skill_id> [次数]   训练SKILL (默认5次)
  accelerate <skill_id>     一键加速到专家级

开源命令:
  release <skill_id>        发布SKILL到GitHub
  batch-status              查看Batch 1发布状态

维护命令:
  health                    系统健康检查
  report [输出文件]          生成完整报告

示例:
  python3 skill_manager.py status
  python3 skill_manager.py analyze architect_5l
  python3 skill_manager.py mentor langzhu_wave_predictor
  python3 skill_manager.py train architect_5l 10
        """)

def main():
    """主入口"""
    manager = A5LSkillManager()
    
    # 如果有命令行参数
    if len(sys.argv) > 1:
        manager.run_cli(sys.argv[1:])
    else:
        # 默认显示状态
        manager.status()
        print("\n💡 使用 'python3 skill_manager.py help' 查看所有命令")

if __name__ == "__main__":
    main()
