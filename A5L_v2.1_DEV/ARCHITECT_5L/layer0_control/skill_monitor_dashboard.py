#!/usr/bin/env python3
"""
A5L SKILL监控仪表板
实时监控所有62个SKILL的健康状态
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, '/workspace/projects/workspace')

class SKILLMonitorDashboard:
    """SKILL监控仪表板"""
    
    def __init__(self):
        self.registry_path = "/workspace/projects/workspace/SKILL_REGISTRY.json"
        self.registry = self._load_registry()
        self.alerts = []
        self.metrics = {}
        
    def _load_registry(self) -> dict:
        """加载SKILL注册表"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载注册表失败: {e}")
            return {}
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """生成监控仪表板"""
        print("=" * 80)
        print("📊 A5L SKILL监控仪表板")
        print("=" * 80)
        print(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 总体健康度
        self._check_overall_health()
        
        # 2. 低熟练度SKILL监控
        self._check_low_proficiency()
        
        # 3. 长期未使用SKILL监控
        self._check_stale_skills()
        
        # 4. 低成功率SKILL监控
        self._check_low_success_rate()
        
        # 5. 生成告警
        self._generate_alerts()
        
        # 6. 保存报告
        return self._save_dashboard()
    
    def _check_overall_health(self):
        """检查总体健康度"""
        summary = self.registry.get('summary', {})
        
        total = summary.get('total_skills', 0)
        active = summary.get('active_skills', 0)
        deprecated = summary.get('deprecated_skills', 0)
        avg_prof = summary.get('avg_proficiency', 0)
        
        active_rate = active / total if total > 0 else 0
        health_score = (active_rate * 0.3 + avg_prof * 0.7) * 100
        
        self.metrics['overall'] = {
            'total_skills': total,
            'active_skills': active,
            'deprecated_skills': deprecated,
            'active_rate': active_rate,
            'avg_proficiency': avg_prof,
            'health_score': health_score
        }
        
        print(f"\n🏥 总体健康度: {health_score:.0f}/100")
        
        if health_score >= 90:
            status = "🟢 优秀"
        elif health_score >= 75:
            status = "🟡 良好"
        elif health_score >= 60:
            status = "🟠 一般"
        else:
            status = "🔴 需改进"
        
        print(f"   状态: {status}")
        print(f"   SKILL总数: {total}")
        print(f"   活跃SKILL: {active} ({active_rate:.1%})")
        print(f"   废弃SKILL: {deprecated}")
        print(f"   平均熟练度: {avg_prof:.1%}")
    
    def _check_low_proficiency(self):
        """检查低熟练度SKILL"""
        categories = self.registry.get('categories', {})
        
        low_proficiency = []
        for cat_id, cat_data in categories.items():
            for skill in cat_data.get('skills', []):
                prof = skill.get('proficiency', 1)
                if prof < 0.7:
                    low_proficiency.append({
                        'id': skill.get('id'),
                        'name': skill.get('name'),
                        'proficiency': prof,
                        'category': cat_data.get('name'),
                        'target': 0.8,
                        'gap': 0.8 - prof
                    })
        
        # 按熟练度排序
        low_proficiency.sort(key=lambda x: x['proficiency'])
        
        self.metrics['low_proficiency'] = low_proficiency
        
        print(f"\n⚠️ 低熟练度SKILL监控 ({len(low_proficiency)}个需提升):")
        
        for skill in low_proficiency:
            bar_length = int(skill['proficiency'] * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            status = "🔴" if skill['proficiency'] < 0.5 else "🟠" if skill['proficiency'] < 0.7 else "🟡"
            print(f"   {status} {skill['name']}")
            print(f"      [{bar}] {skill['proficiency']:.0%} (目标: {skill['target']:.0%}, 差距: {skill['gap']:.0%})")
            print(f"      分类: {skill['category']}")
    
    def _check_stale_skills(self):
        """检查长期未使用的SKILL"""
        categories = self.registry.get('categories', {})
        
        today = datetime.now().date()
        stale_skills = []
        
        for cat_id, cat_data in categories.items():
            for skill in cat_data.get('skills', []):
                last_used = skill.get('last_used')
                if last_used:
                    try:
                        last_date = datetime.strptime(last_used, '%Y-%m-%d').date()
                        days_ago = (today - last_date).days
                        
                        if days_ago > 30:
                            stale_skills.append({
                                'id': skill.get('id'),
                                'name': skill.get('name'),
                                'days_ago': days_ago,
                                'last_used': last_used,
                                'category': cat_data.get('name'),
                                'status': 'warning' if days_ago > 90 else 'caution'
                            })
                    except:
                        pass
        
        # 按天数排序
        stale_skills.sort(key=lambda x: -x['days_ago'])
        
        self.metrics['stale_skills'] = stale_skills
        
        if stale_skills:
            print(f"\n⏰ 长期未使用SKILL监控 ({len(stale_skills)}个):")
            
            for skill in stale_skills:
                status = "🔴" if skill['status'] == 'warning' else "🟡"
                print(f"   {status} {skill['name']}")
                print(f"      未使用: {skill['days_ago']}天 (最后使用: {skill['last_used']})")
                print(f"      分类: {skill['category']}")
                if skill['status'] == 'warning':
                    print(f"      ⚠️ 建议: 考虑标记为废弃或移除")
        else:
            print(f"\n✅ 所有SKILL都在30天内使用过")
    
    def _check_low_success_rate(self):
        """检查低成功率SKILL"""
        categories = self.registry.get('categories', {})
        
        low_success = []
        for cat_id, cat_data in categories.items():
            for skill in cat_data.get('skills', []):
                success_rate = skill.get('success_rate', 1)
                usage_count = skill.get('usage_count', 0)
                
                # 只检查使用次数>10的SKILL
                if usage_count >= 10 and success_rate < 0.8:
                    low_success.append({
                        'id': skill.get('id'),
                        'name': skill.get('name'),
                        'success_rate': success_rate,
                        'usage_count': usage_count,
                        'category': cat_data.get('name'),
                        'target': 0.85,
                        'gap': 0.85 - success_rate
                    })
        
        # 按成功率排序
        low_success.sort(key=lambda x: x['success_rate'])
        
        self.metrics['low_success'] = low_success
        
        if low_success:
            print(f"\n📉 低成功率SKILL监控 ({len(low_success)}个需优化):")
            
            for skill in low_success:
                bar_length = int(skill['success_rate'] * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                print(f"   🟠 {skill['name']}")
                print(f"      成功率: [{bar}] {skill['success_rate']:.0%} (使用{skill['usage_count']}次)")
                print(f"      目标: {skill['target']:.0%}, 差距: {skill['gap']:.0%}")
                print(f"      分类: {skill['category']}")
        else:
            print(f"\n✅ 所有SKILL成功率都>=80%")
    
    def _generate_alerts(self):
        """生成告警"""
        alerts = []
        
        # 健康度告警
        health_score = self.metrics['overall']['health_score']
        if health_score < 75:
            alerts.append({
                'level': 'warning',
                'type': 'health',
                'message': f'系统健康度{health_score:.0f}低于75，需要关注'
            })
        
        # 低熟练度告警
        low_prof = self.metrics.get('low_proficiency', [])
        if len(low_prof) > 0:
            alerts.append({
                'level': 'warning',
                'type': 'proficiency',
                'message': f'发现{len(low_prof)}个低熟练度SKILL需要训练'
            })
        
        # 长期未使用告警
        stale = self.metrics.get('stale_skills', [])
        warning_stale = [s for s in stale if s['status'] == 'warning']
        if len(warning_stale) > 0:
            alerts.append({
                'level': 'critical',
                'type': 'stale',
                'message': f'发现{len(warning_stale)}个超过90天未使用的SKILL建议移除'
            })
        
        # 低成功率告警
        low_success = self.metrics.get('low_success', [])
        if len(low_success) > 0:
            alerts.append({
                'level': 'warning',
                'type': 'success_rate',
                'message': f'发现{len(low_success)}个低成功率SKILL需要算法优化'
            })
        
        self.alerts = alerts
        
        print(f"\n🚨 告警通知 ({len(alerts)}个):")
        for alert in alerts:
            icon = "🔴" if alert['level'] == 'critical' else "🟠" if alert['level'] == 'warning' else "🟡"
            print(f"   {icon} [{alert['type'].upper()}] {alert['message']}")
    
    def _save_dashboard(self) -> Dict[str, Any]:
        """保存仪表板数据"""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'version': 'v2.0.0-alpha',
            'metrics': self.metrics,
            'alerts': self.alerts,
            'summary': {
                'health_score': self.metrics['overall']['health_score'],
                'total_skills': self.metrics['overall']['total_skills'],
                'low_proficiency_count': len(self.metrics.get('low_proficiency', [])),
                'stale_skills_count': len(self.metrics.get('stale_skills', [])),
                'low_success_count': len(self.metrics.get('low_success', [])),
                'alert_count': len(self.alerts)
            }
        }
        
        # 保存JSON报告
        report_dir = Path('/workspace/projects/workspace/reports/dashboards')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = report_dir / f'skill_dashboard_{timestamp}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, ensure_ascii=False, indent=2)
        
        # 保存最新仪表板
        latest_path = report_dir / 'skill_dashboard_latest.json'
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 仪表板已保存:")
        print(f"   历史版本: {report_path}")
        print(f"   最新版本: {latest_path}")
        
        return dashboard
    
    def get_training_plan(self) -> List[Dict]:
        """生成训练计划"""
        training_plan = []
        
        # 低熟练度SKILL训练
        for skill in self.metrics.get('low_proficiency', []):
            training_plan.append({
                'skill_id': skill['id'],
                'skill_name': skill['name'],
                'current_proficiency': skill['proficiency'],
                'target_proficiency': skill['target'],
                'priority': 'high' if skill['proficiency'] < 0.5 else 'medium',
                'action': '专项训练',
                'estimated_time': '3-5天'
            })
        
        # 低成功率SKILL优化
        for skill in self.metrics.get('low_success', []):
            training_plan.append({
                'skill_id': skill['id'],
                'skill_name': skill['name'],
                'current_success_rate': skill['success_rate'],
                'target_success_rate': skill['target'],
                'priority': 'high',
                'action': '算法优化',
                'estimated_time': '5-7天'
            })
        
        return training_plan

if __name__ == "__main__":
    dashboard = SKILLMonitorDashboard()
    result = dashboard.generate_dashboard()
    
    print("\n" + "=" * 80)
    print("📋 训练计划建议:")
    print("=" * 80)
    
    training_plan = dashboard.get_training_plan()
    high_priority = [t for t in training_plan if t['priority'] == 'high']
    medium_priority = [t for t in training_plan if t['priority'] == 'medium']
    
    print(f"\n🔴 高优先级 ({len(high_priority)}个):")
    for item in high_priority:
        print(f"   • {item['skill_name']}")
        print(f"     动作: {item['action']}, 预计: {item['estimated_time']}")
    
    print(f"\n🟡 中优先级 ({len(medium_priority)}个):")
    for item in medium_priority:
        print(f"   • {item['skill_name']}")
        print(f"     动作: {item['action']}, 预计: {item['estimated_time']}")
    
    print("\n" + "=" * 80)
    print("✅ SKILL监控仪表板生成完成!")
    print("=" * 80)
