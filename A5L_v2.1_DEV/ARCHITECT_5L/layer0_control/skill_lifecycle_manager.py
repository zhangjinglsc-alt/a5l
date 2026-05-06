#!/usr/bin/env python3
"""
SKILL淘汰机制 + 月度审计系统
Phase 2/3/4 整合实现
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, '/workspace/projects/workspace')

class SkillLifecycleManager:
    """SKILL生命周期管理器"""
    
    # 淘汰规则
    DEPRECATION_RULES = {
        'warning_days': 90,    # 90天未使用 → 标记警告
        'deprecated_days': 180, # 180天未使用 → 标记废弃
        'removal_days': 365     # 365天未使用 → 准备移除
    }
    
    def __init__(self):
        self.registry_path = "/workspace/projects/workspace/SKILL_REGISTRY.json"
        self.audit_log_path = "/workspace/projects/workspace/reports/skill_audit_log.json"
        self.registry = self._load_registry()
        self.audit_results = []
        
    def _load_registry(self) -> dict:
        """加载SKILL注册表"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载注册表失败: {e}")
            return {}
    
    def run_lifecycle_audit(self):
        """运行生命周期审计"""
        print("=" * 80)
        print("🔄 SKILL生命周期审计")
        print("=" * 80)
        print(f"⏰ 审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📋 审计规则:")
        print(f"   • {self.DEPRECATION_RULES['warning_days']}天未使用 → 警告")
        print(f"   • {self.DEPRECATION_RULES['deprecated_days']}天未使用 → 废弃")
        print(f"   • {self.DEPRECATION_RULES['removal_days']}天未使用 → 移除")
        print("=" * 80)
        
        # 1. 检查所有SKILL的使用情况
        self._check_usage_status()
        
        # 2. 生成处理建议
        self._generate_recommendations()
        
        # 3. 保存审计报告
        self._save_audit_report()
        
        # 4. 打印总结
        self._print_summary()
    
    def _check_usage_status(self):
        """检查使用情况"""
        categories = self.registry.get('categories', {})
        today = datetime.now().date()
        
        for cat_id, cat_data in categories.items():
            for skill in cat_data.get('skills', []):
                skill_id = skill.get('id')
                skill_name = skill.get('name')
                last_used = skill.get('last_used')
                current_status = skill.get('status', 'active')
                
                audit_entry = {
                    'skill_id': skill_id,
                    'skill_name': skill_name,
                    'category': cat_data.get('name'),
                    'current_status': current_status,
                    'last_used': last_used,
                    'days_since_use': None,
                    'recommended_action': None,
                    'priority': None
                }
                
                if last_used:
                    try:
                        last_date = datetime.strptime(last_used, '%Y-%m-%d').date()
                        days_ago = (today - last_date).days
                        audit_entry['days_since_use'] = days_ago
                        
                        # 判断状态
                        if days_ago >= self.DEPRECATION_RULES['removal_days']:
                            audit_entry['recommended_action'] = 'remove'
                            audit_entry['priority'] = 'critical'
                        elif days_ago >= self.DEPRECATION_RULES['deprecated_days']:
                            audit_entry['recommended_action'] = 'deprecate'
                            audit_entry['priority'] = 'high'
                        elif days_ago >= self.DEPRECATION_RULES['warning_days']:
                            audit_entry['recommended_action'] = 'warn'
                            audit_entry['priority'] = 'medium'
                        else:
                            audit_entry['recommended_action'] = 'keep'
                            audit_entry['priority'] = 'low'
                    except:
                        audit_entry['recommended_action'] = 'unknown'
                        audit_entry['priority'] = 'low'
                else:
                    # 从未使用过
                    audit_entry['days_since_use'] = 999
                    audit_entry['recommended_action'] = 'review'
                    audit_entry['priority'] = 'high'
                
                self.audit_results.append(audit_entry)
    
    def _generate_recommendations(self):
        """生成处理建议"""
        print("\n📊 审计结果:")
        print("-" * 80)
        
        # 按优先级分组
        critical = [r for r in self.audit_results if r['priority'] == 'critical']
        high = [r for r in self.audit_results if r['priority'] == 'high']
        medium = [r for r in self.audit_results if r['priority'] == 'medium']
        low = [r for r in self.audit_results if r['priority'] == 'low']
        
        if critical:
            print(f"\n🔴 需要移除 ({len(critical)}个) - 超过{self.DEPRECATION_RULES['removal_days']}天未使用:")
            for r in critical:
                print(f"   • {r['skill_name']} ({r['days_since_use']}天)")
                print(f"     建议: 准备从系统中移除")
        
        if high:
            print(f"\n🟠 需要废弃 ({len(high)}个) - 超过{self.DEPRECATION_RULES['deprecated_days']}天未使用:")
            for r in high:
                print(f"   • {r['skill_name']} ({r['days_since_use']}天)")
                print(f"     建议: 标记为废弃，不再维护")
        
        if medium:
            print(f"\n🟡 需要警告 ({len(medium)}个) - 超过{self.DEPRECATION_RULES['warning_days']}天未使用:")
            for r in medium[:5]:  # 只显示前5个
                print(f"   • {r['skill_name']} ({r['days_since_use']}天)")
            if len(medium) > 5:
                print(f"     ... 还有{len(medium)-5}个")
        
        if low:
            print(f"\n🟢 正常使用 ({len(low)}个) - 活跃SKILL")
    
    def _save_audit_report(self):
        """保存审计报告"""
        report = {
            'audit_date': datetime.now().isoformat(),
            'version': 'v2.0.0-alpha',
            'rules': self.DEPRECATION_RULES,
            'summary': {
                'total_skills': len(self.audit_results),
                'critical': len([r for r in self.audit_results if r['priority'] == 'critical']),
                'high': len([r for r in self.audit_results if r['priority'] == 'high']),
                'medium': len([r for r in self.audit_results if r['priority'] == 'medium']),
                'low': len([r for r in self.audit_results if r['priority'] == 'low'])
            },
            'details': self.audit_results
        }
        
        # 保存到文件
        report_dir = Path(self.audit_log_path).parent
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 带时间戳的版本
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        timestamp_path = report_dir / f'skill_audit_{timestamp}.json'
        
        with open(timestamp_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 最新版本
        with open(self.audit_log_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 审计报告已保存:")
        print(f"   历史版本: {timestamp_path}")
        print(f"   最新版本: {self.audit_log_path}")
    
    def _print_summary(self):
        """打印总结"""
        summary = {
            'critical': len([r for r in self.audit_results if r['priority'] == 'critical']),
            'high': len([r for r in self.audit_results if r['priority'] == 'high']),
            'medium': len([r for r in self.audit_results if r['priority'] == 'medium']),
            'low': len([r for r in self.audit_results if r['priority'] == 'low'])
        }
        
        print("\n" + "=" * 80)
        print("📋 审计总结")
        print("=" * 80)
        print(f"总SKILL数: {len(self.audit_results)}")
        print(f"🔴 需移除: {summary['critical']}个")
        print(f"🟠 需废弃: {summary['high']}个")
        print(f"🟡 需警告: {summary['medium']}个")
        print(f"🟢 正常: {summary['low']}个")
        
        # 计算健康度
        healthy_ratio = summary['low'] / len(self.audit_results) if self.audit_results else 0
        print(f"\n生命周期健康度: {healthy_ratio:.1%}")
    
    def apply_deprecation(self, dry_run=True):
        """应用淘汰标记"""
        print("\n" + "=" * 80)
        print("⚠️ 应用淘汰标记" + (" (模拟运行)" if dry_run else ""))
        print("=" * 80)
        
        actions = {
            'remove': [],
            'deprecate': [],
            'warn': []
        }
        
        for result in self.audit_results:
            action = result['recommended_action']
            if action in actions:
                actions[action].append(result)
        
        # 模拟执行
        for action_type, items in actions.items():
            if items:
                print(f"\n{action_type.upper()} ({len(items)}个):")
                for item in items:
                    print(f"   • {item['skill_name']}")
                    if not dry_run:
                        # 这里实际修改registry
                        pass
        
        if dry_run:
            print("\n💡 这是模拟运行，使用 apply_deprecation(dry_run=False) 实际执行")


class MonthlySkillAuditor:
    """月度SKILL审计器"""
    
    def __init__(self):
        self.lifecycle_manager = SkillLifecycleManager()
        
    def run_monthly_audit(self):
        """运行月度审计"""
        print("\n" + "=" * 80)
        print("📅 A5L 月度SKILL审计")
        print("=" * 80)
        print(f"审计月份: {datetime.now().strftime('%Y年%m月')}")
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 生命周期审计
        self.lifecycle_manager.run_lifecycle_audit()
        
        # 2. 健康度评估
        self._health_assessment()
        
        # 3. 性能分析
        self._performance_analysis()
        
        # 4. 生成月度报告
        self._generate_monthly_report()
        
        print("\n" + "=" * 80)
        print("✅ 月度审计完成!")
        print("=" * 80)
    
    def _health_assessment(self):
        """健康度评估"""
        print("\n🏥 健康度评估:")
        print("-" * 80)
        
        summary = self.lifecycle_manager.registry.get('summary', {})
        total = summary.get('total_skills', 0)
        active = summary.get('active_skills', 0)
        avg_prof = summary.get('avg_proficiency', 0)
        
        active_rate = active / total if total > 0 else 0
        health_score = (active_rate * 0.3 + avg_prof * 0.7) * 100
        
        print(f"   健康度评分: {health_score:.0f}/100")
        
        if health_score >= 90:
            status = "🟢 优秀 - 系统运行良好"
        elif health_score >= 75:
            status = "🟡 良好 - 建议轻度优化"
        elif health_score >= 60:
            status = "🟠 一般 - 需要关注"
        else:
            status = "🔴 需改进 - 立即行动"
        
        print(f"   状态: {status}")
        print(f"   活跃率: {active_rate:.1%}")
        print(f"   熟练度: {avg_prof:.1%}")
    
    def _performance_analysis(self):
        """性能分析"""
        print("\n📈 性能分析:")
        print("-" * 80)
        
        categories = self.lifecycle_manager.registry.get('categories', {})
        
        # 统计各类别表现
        for cat_id, cat_data in categories.items():
            skills = cat_data.get('skills', [])
            if skills:
                avg_success = sum(s.get('success_rate', 0) for s in skills) / len(skills)
                total_usage = sum(s.get('usage_count', 0) for s in skills)
                
                print(f"   {cat_data.get('name')}:")
                print(f"      SKILL数: {len(skills)}, 平均成功率: {avg_success:.1%}, 总使用: {total_usage}次")
    
    def _generate_monthly_report(self):
        """生成月度报告"""
        report = {
            'audit_type': 'monthly',
            'audit_date': datetime.now().isoformat(),
            'month': datetime.now().strftime('%Y-%m'),
            'summary': {
                'total_skills': len(self.lifecycle_manager.audit_results),
                'lifecycle_status': {
                    'critical': len([r for r in self.lifecycle_manager.audit_results if r['priority'] == 'critical']),
                    'high': len([r for r in self.lifecycle_manager.audit_results if r['priority'] == 'high']),
                    'medium': len([r for r in self.lifecycle_manager.audit_results if r['priority'] == 'medium']),
                    'low': len([r for r in self.lifecycle_manager.audit_results if r['priority'] == 'low'])
                }
            },
            'recommendations': [
                '定期检查低使用频率SKILL',
                '优化低成功率SKILL算法',
                '更新废弃SKILL文档',
                '考虑移除长期未使用SKILL'
            ]
        }
        
        # 保存月度报告
        report_dir = Path('/workspace/projects/workspace/reports/monthly')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        month_str = datetime.now().strftime('%Y%m')
        report_path = report_dir / f'skill_monthly_audit_{month_str}.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 月度报告已保存: {report_path}")


if __name__ == "__main__":
    # 运行月度审计
    auditor = MonthlySkillAuditor()
    auditor.run_monthly_audit()
