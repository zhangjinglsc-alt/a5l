#!/usr/bin/env python3
"""
SKILL自主学习系统 - 自动化版
自动从真实数据中提取洞察并更新知识库
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict

class SkillAutoLearning:
    """SKILL自主学习引擎"""
    
    def __init__(self, workspace_path: str = "/workspace/projects/workspace"):
        self.workspace = workspace_path
        self.log_dir = os.path.join(workspace_path, "data/skill_learning_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
    def load_training_logs(self, date: str = None) -> List[Dict]:
        """加载训练日志"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        log_path = os.path.join(self.workspace, "data/skill_training_log.json")
        if not os.path.exists(log_path):
            return []
            
        with open(log_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            
        # 过滤今日日志
        return [l for l in logs if l['timestamp'].startswith(date)]
    
    def load_skill_registry(self) -> Dict:
        """加载SKILL注册表"""
        registry_path = os.path.join(self.workspace, "SKILL_REGISTRY.json")
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_insights(self, training_logs: List[Dict], registry: Dict) -> List[str]:
        """从训练数据中提取洞察"""
        insights = []
        
        # 1. 分析训练效果最好的SKILL
        if training_logs:
            gains = []
            for log in training_logs:
                for detail in log.get('details', []):
                    gains.append({
                        'skill_id': detail['skill_id'],
                        'gain': detail['gain'],
                        'new_proficiency': detail.get('new_proficiency', 0)
                    })
            
            # 排序找出效果最好的
            gains.sort(key=lambda x: x['gain'], reverse=True)
            top_performers = gains[:3]
            
            if top_performers:
                top_names = [g['skill_id'] for g in top_performers]
                top_gains = [f"+{g['gain']:.3f}%" for g in top_performers]
                insights.append(f"高训练效果SKILL: {', '.join(top_names)} ({', '.join(top_gains)})")
        
        # 2. 找出接近突破的SKILL
        all_skills = []
        for cat in registry.get('categories', {}).values():
            for skill in cat.get('skills', []):
                if skill.get('status') == 'active':
                    prof = skill.get('proficiency', 0)
                    if 0.78 <= prof < 0.80:  # 接近80%
                        all_skills.append(f"{skill['id']}({prof:.1%})")
        
        if all_skills:
            insights.append(f"接近专家级突破: {', '.join(all_skills[:3])}")
        
        # 3. 统计今日训练成果
        if training_logs:
            total_sessions = len(training_logs)
            total_skills = sum(l['skills_trained'] for l in training_logs)
            total_gain = sum(l['total_proficiency_gain'] for l in training_logs)
            insights.append(f"今日训练统计: {total_sessions}次会话，{total_skills}个SKILL，+{total_gain:.2f}%熟练度")
        
        return insights
    
    def generate_action_items(self, insights: List[str]) -> List[str]:
        """生成行动项"""
        actions = []
        
        # 从洞察中生成行动
        for insight in insights:
            if "接近专家级突破" in insight:
                actions.append("重点监控接近80%的SKILL，安排额外训练")
            if "高训练效果" in insight:
                actions.append("分析高效果SKILL的训练模式，复用到低熟练度SKILL")
        
        # 通用行动
        actions.append("持续追踪SKILL熟练度变化趋势")
        actions.append("更新SKILL_REGISTRY.json中的学习记录")
        
        return actions
    
    def save_learning_log(self, insights: List[str], actions: List[str]):
        """保存学习日志"""
        learning_log = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'insights_extracted': insights,
            'action_items': actions,
            'learning_count': len(insights),
            'action_count': len(actions)
        }
        
        log_file = os.path.join(
            self.log_dir, 
            f"learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(learning_log, f, indent=2, ensure_ascii=False)
            
        return log_file
    
    def run(self):
        """执行自主学习"""
        print("🧠 启动SKILL自主学习...")
        print("=" * 50)
        
        # 1. 加载数据
        training_logs = self.load_training_logs()
        registry = self.load_skill_registry()
        
        # 2. 提取洞察
        insights = self.extract_insights(training_logs, registry)
        
        # 3. 生成行动
        actions = self.generate_action_items(insights)
        
        # 4. 保存日志
        log_file = self.save_learning_log(insights, actions)
        
        # 5. 输出报告
        print(f"\n📚 提取洞察 ({len(insights)} 条):")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
        
        print(f"\n🎯 行动项 ({len(actions)} 条):")
        for i, action in enumerate(actions, 1):
            print(f"   {i}. {action}")
        
        print(f"\n💾 学习日志: {log_file}")
        print("=" * 50)
        print("✅ 自主学习完成")
        
        return {
            'insights': insights,
            'actions': actions,
            'log_file': log_file
        }

if __name__ == "__main__":
    learner = SkillAutoLearning()
    result = learner.run()
    sys.exit(0)
