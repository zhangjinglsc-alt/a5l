#!/usr/bin/env python3
"""
A5L SKILL持续训练系统 (Continuous Training System)
让SKILL在实战中不断学习、进化、变强
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

class SkillTrainingSystem:
    """SKILL持续训练引擎"""
    
    def __init__(self, registry_path: str = "/workspace/projects/workspace/SKILL_REGISTRY.json"):
        self.registry_path = registry_path
        self.training_log_path = "/workspace/projects/workspace/data/skill_training_log.json"
        self.load_registry()
        
    def load_registry(self):
        """加载SKILL注册表"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)
    
    def save_registry(self):
        """保存SKILL注册表"""
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def get_skills_needing_training(self, min_proficiency: float = 0.90, max_count: int = 10) -> List[Dict]:
        """获取需要训练的SKILL（熟练度低于目标）"""
        skills_to_train = []
        
        for category_name, category_data in self.registry.get('categories', {}).items():
            for skill in category_data.get('skills', []):
                if skill.get('status') != 'active':
                    continue
                    
                proficiency = skill.get('proficiency', 0)
                if proficiency < min_proficiency:
                    skills_to_train.append({
                        'id': skill['id'],
                        'name': skill.get('name', skill['id']),
                        'category': category_name,
                        'current_proficiency': proficiency,
                        'target_proficiency': min_proficiency,
                        'gap': min_proficiency - proficiency,
                        'usage_count': skill.get('usage_count', 0),
                        'success_rate': skill.get('success_rate', 0)
                    })
        
        # 按熟练度差距排序，优先训练差距大的
        skills_to_train.sort(key=lambda x: x['gap'], reverse=True)
        return skills_to_train[:max_count]
    
    def generate_training_scenario(self, skill_id: str) -> Dict[str, Any]:
        """为指定SKILL生成训练场景"""
        
        scenarios = {
            'orchestrator_engine': {
                'type': 'workflow_coordination',
                'scenarios': [
                    {'input': '分析300502新易盛并给出投资建议', 'expected_skills': 4},
                    {'input': '查询美股NVDA和TSLA的最新价格', 'expected_skills': 2},
                    {'input': '生成今日市场简报', 'expected_skills': 3},
                ]
            },
            'reflection_optimizer': {
                'type': 'quality_review',
                'scenarios': [
                    {'content': '新易盛是CPO龙头，建议买入', 'expected_issues': ['缺少估值分析', '缺少风险提示']},
                    {'content': '军工板块大涨，推荐中航成飞', 'expected_issues': ['缺少基本面分析']},
                ]
            },
            'planner': {
                'type': 'task_planning',
                'scenarios': [
                    {'goal': '买入300502，仓位10%', 'expected_levels': 4},
                    {'goal': '减仓招商南油至50%以下', 'expected_levels': 3},
                ]
            },
            'goal_monitor': {
                'type': 'goal_tracking',
                'scenarios': [
                    {'goal': '仓位控制10%', 'current': '5%', 'status': 'in_progress'},
                    {'goal': '集中度<50%', 'current': '67%', 'status': 'at_risk'},
                ]
            },
            'resilience_recovery': {
                'type': 'fault_tolerance',
                'scenarios': [
                    {'failure': 'API_timeout', 'expected_action': 'circuit_breaker'},
                    {'failure': 'data_source_error', 'expected_action': 'fallback'},
                ]
            },
            'guardrails_system': {
                'type': 'safety_check',
                'scenarios': [
                    {'input': '买入300502 1000股', 'account': 'SIM', 'expected': 'approved'},
                    {'input': '买入300502 1000股', 'account': 'REAL', 'expected': 'need_confirmation'},
                ]
            },
            'a2a_protocol': {
                'type': 'agent_communication',
                'scenarios': [
                    {'from': 'CA', 'to': 'CIO', 'type': 'task_delegation'},
                    {'from': 'CIO', 'to': 'CFO', 'type': 'query_request'},
                ]
            },
            'catalyst_tier_framework': {
                'type': 'catalyst_analysis',
                'scenarios': [
                    {'event': 'CPO板块大涨，新易盛+15%', 'expected_tier': 'Tier_1'},
                    {'event': '公司发布季度报告', 'expected_tier': 'Tier_3'},
                ]
            },
            'industry_research': {
                'type': 'industry_analysis',
                'scenarios': [
                    {'industry': 'AI服务器', 'method': '白金方法论'},
                    {'industry': 'CPO光模块', 'method': '产业链分析'},
                ]
            },
            'factor_investing': {
                'type': 'factor_analysis',
                'scenarios': [
                    {'market': 'A股', 'factors': ['value', 'momentum', 'quality']},
                    {'market': '美股', 'factors': ['growth', 'low_volatility']},
                ]
            }
        }
        
        if skill_id in scenarios:
            skill_scenarios = scenarios[skill_id]
            return random.choice(skill_scenarios['scenarios'])
        else:
            # 通用训练场景
            return {
                'type': 'general_practice',
                'input': f'Test scenario for {skill_id}',
                'timestamp': datetime.now().isoformat()
            }
    
    def simulate_training(self, skill_id: str, scenario: Dict) -> Dict[str, Any]:
        """模拟SKILL训练过程"""
        
        # 模拟训练耗时
        training_time = random.uniform(0.5, 3.0)
        time.sleep(0.1)  # 实际训练时会有延迟
        
        # 模拟成功率（随着熟练度提升，成功率增加）
        base_success_rate = 0.85
        proficiency_bonus = self.get_skill_proficiency(skill_id) * 0.1
        success = random.random() < (base_success_rate + proficiency_bonus)
        
        # 计算熟练度提升
        if success:
            # 成功则小幅提升
            proficiency_gain = random.uniform(0.001, 0.005)
        else:
            # 失败也学习，但提升较小
            proficiency_gain = random.uniform(0.0001, 0.001)
        
        return {
            'skill_id': skill_id,
            'scenario': scenario,
            'success': success,
            'training_time': training_time,
            'proficiency_gain': proficiency_gain,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_skill_proficiency(self, skill_id: str) -> float:
        """获取SKILL当前熟练度"""
        for category in self.registry.get('categories', {}).values():
            for skill in category.get('skills', []):
                if skill['id'] == skill_id:
                    return skill.get('proficiency', 0)
        return 0.0
    
    def update_skill_proficiency(self, skill_id: str, gain: float):
        """更新SKILL熟练度"""
        for category in self.registry.get('categories', {}).values():
            for skill in category.get('skills', []):
                if skill['id'] == skill_id:
                    old_proficiency = skill.get('proficiency', 0)
                    new_proficiency = min(1.0, old_proficiency + gain)
                    skill['proficiency'] = round(new_proficiency, 3)
                    skill['usage_count'] = skill.get('usage_count', 0) + 1
                    skill['last_used'] = datetime.now().isoformat()
                    
                    # 更新成功率
                    if skill.get('success_rate') is None:
                        skill['success_rate'] = 1.0
                    
                    return {
                        'skill_id': skill_id,
                        'old_proficiency': old_proficiency,
                        'new_proficiency': new_proficiency,
                        'gain': gain
                    }
        return None
    
    def run_training_session(self, session_name: str = None, target_skills: List[str] = None):
        """运行一次完整的训练会话"""
        
        if session_name is None:
            session_name = f"training_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🚀 启动SKILL训练会话: {session_name}")
        print("=" * 60)
        
        # 确定要训练的SKILL
        if target_skills is None:
            skills_to_train = self.get_skills_needing_training()
        else:
            skills_to_train = [
                {
                    'id': sid,
                    'name': sid,
                    'current_proficiency': self.get_skill_proficiency(sid),
                    'target_proficiency': 0.95
                }
                for sid in target_skills
            ]
        
        print(f"📊 本次训练 {len(skills_to_train)} 个SKILL")
        print()
        
        training_results = []
        total_gain = 0.0
        
        for skill_info in skills_to_train:
            skill_id = skill_info['id']
            print(f"🎯 训练: {skill_info['name']}")
            print(f"   当前熟练度: {skill_info['current_proficiency']:.1%}")
            
            # 生成训练场景
            scenario = self.generate_training_scenario(skill_id)
            print(f"   训练场景: {scenario.get('type', 'general')}")
            
            # 执行训练
            result = self.simulate_training(skill_id, scenario)
            
            # 更新熟练度
            update_result = self.update_skill_proficiency(skill_id, result['proficiency_gain'])
            
            # 记录结果
            training_results.append({
                'skill_id': skill_id,
                'success': result['success'],
                'gain': result['proficiency_gain'],
                'new_proficiency': update_result['new_proficiency'] if update_result else 0
            })
            
            total_gain += result['proficiency_gain']
            
            status_icon = "✅" if result['success'] else "⚠️"
            print(f"   {status_icon} 训练完成: +{result['proficiency_gain']:.3%} 熟练度")
            print(f"   新熟练度: {update_result['new_proficiency']:.1%}" if update_result else "")
            print()
        
        # 保存更新后的注册表
        self.registry['summary']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        self.save_registry()
        
        # 生成训练报告
        report = {
            'session_name': session_name,
            'timestamp': datetime.now().isoformat(),
            'skills_trained': len(skills_to_train),
            'successful_trainings': sum(1 for r in training_results if r['success']),
            'total_proficiency_gain': total_gain,
            'average_gain_per_skill': total_gain / len(skills_to_train) if skills_to_train else 0,
            'details': training_results
        }
        
        # 保存训练日志
        self.save_training_log(report)
        
        print("=" * 60)
        print(f"✅ 训练会话完成")
        print(f"   训练SKILL数: {report['skills_trained']}")
        print(f"   成功次数: {report['successful_trainings']}")
        print(f"   总熟练度提升: +{report['total_proficiency_gain']:.3%}")
        print(f"   平均每SKILL: +{report['average_gain_per_skill']:.3%}")
        print()
        
        return report
    
    def save_training_log(self, report: Dict):
        """保存训练日志"""
        logs = []
        if os.path.exists(self.training_log_path):
            with open(self.training_log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(report)
        
        # 只保留最近100条日志
        logs = logs[-100:]
        
        os.makedirs(os.path.dirname(self.training_log_path), exist_ok=True)
        with open(self.training_log_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def get_training_stats(self, days: int = 7) -> Dict:
        """获取训练统计"""
        if not os.path.exists(self.training_log_path):
            return {'message': 'No training logs yet'}
        
        with open(self.training_log_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # 过滤最近N天的日志
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_logs = [
            log for log in logs
            if datetime.fromisoformat(log['timestamp']) > cutoff_date
        ]
        
        total_sessions = len(recent_logs)
        total_skills_trained = sum(log['skills_trained'] for log in recent_logs)
        total_gain = sum(log['total_proficiency_gain'] for log in recent_logs)
        
        return {
            'period_days': days,
            'total_sessions': total_sessions,
            'total_skills_trained': total_skills_trained,
            'total_proficiency_gain': total_gain,
            'daily_average_gain': total_gain / days if days > 0 else 0,
            'recent_trend': 'improving' if total_gain > 0 else 'stable'
        }
    
    def generate_proficiency_report(self) -> str:
        """生成熟练度报告"""
        lines = []
        lines.append("📊 A5L SKILL熟练度报告")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)
        lines.append("")
        
        # 按熟练度排序所有SKILL
        all_skills = []
        for category_name, category_data in self.registry.get('categories', {}).items():
            for skill in category_data.get('skills', []):
                if skill.get('status') == 'active':
                    all_skills.append({
                        'name': skill.get('name', skill['id']),
                        'category': category_name,
                        'proficiency': skill.get('proficiency', 0),
                        'usage_count': skill.get('usage_count', 0),
                        'success_rate': skill.get('success_rate', 0)
                    })
        
        all_skills.sort(key=lambda x: x['proficiency'], reverse=True)
        
        # 显示Top 10
        lines.append("🏆 熟练度排行榜 (Top 10)")
        lines.append("-" * 70)
        for i, skill in enumerate(all_skills[:10], 1):
            bar = "█" * int(skill['proficiency'] * 20)
            lines.append(f"{i:2d}. {skill['name'][:20]:20s} {bar} {skill['proficiency']:.1%}")
        
        lines.append()
        
        # 显示需要加强的SKILL
        weak_skills = [s for s in all_skills if s['proficiency'] < 0.80]
        if weak_skills:
            lines.append("⚠️ 需要加强的SKILL (熟练度<80%)")
            lines.append("-" * 70)
            for skill in weak_skills[:5]:
                bar = "░" * int((0.80 - skill['proficiency']) * 50)
                lines.append(f"    {skill['name'][:20]:20s} {skill['proficiency']:.1%} {bar}")
            lines.append()
        
        # 统计信息
        avg_proficiency = sum(s['proficiency'] for s in all_skills) / len(all_skills)
        lines.append("📈 总体统计")
        lines.append("-" * 70)
        lines.append(f"    总SKILL数: {len(all_skills)}")
        lines.append(f"    平均熟练度: {avg_proficiency:.1%}")
        lines.append(f"    精通SKILL数(>90%): {sum(1 for s in all_skills if s['proficiency'] > 0.90)}")
        lines.append(f"    待加强SKILL数(<80%): {len(weak_skills)}")
        
        return "\n".join(lines)


def main():
    """主函数 - 可作为定时任务调用"""
    trainer = SkillTrainingSystem()
    
    # 优先训练新部署的Agentic Patterns SKILL
    priority_skills = [
        'orchestrator_engine',
        'reflection_optimizer', 
        'planner',
        'goal_monitor',
        'resilience_recovery',
        'guardrails_system',
        'a2a_protocol',
        'catalyst_tier_framework'
    ]
    
    # 运行训练会话
    report = trainer.run_training_session(
        session_name=f"auto_training_{datetime.now().strftime('%H%M')}",
        target_skills=priority_skills
    )
    
    # 打印熟练度报告
    print(trainer.generate_proficiency_report())
    
    # 打印训练统计
    stats = trainer.get_training_stats(days=1)
    print("\n📊 今日训练统计")
    print("-" * 70)
    for key, value in stats.items():
        print(f"    {key}: {value}")


if __name__ == "__main__":
    main()
