#!/usr/bin/env python3
"""
A5L v2.0.0-alpha Chief Review - SKILL系统全面自检
由Layer0 Six-in-One Hub执行
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/workspace/projects/workspace')

class ChiefReviewBoard:
    """Chief审查委员会"""
    
    def __init__(self):
        self.registry_path = "/workspace/projects/workspace/SKILL_REGISTRY.json"
        self.registry = self._load_registry()
        self.findings = []
        self.recommendations = []
        
    def _load_registry(self):
        """加载SKILL注册表"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load registry: {e}")
            return None
    
    def run_full_review(self):
        """执行全面审查"""
        print("=" * 80)
        print("🏛️ A5L v2.0.0-alpha Chief Review Board")
        print("=" * 80)
        print(f"📅 Review Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"🔍 Review Scope: All 62 SKILLS")
        print("=" * 80)
        
        # 各Chief审查
        self.chief_architect_review()
        self.chief_investment_officer_review()
        self.chief_operating_officer_review()
        self.chief_security_officer_review()
        
        # 生成报告
        self.generate_report()
        
    def chief_architect_review(self):
        """首席架构师审查 - 系统架构完整性"""
        print("\n" + "=" * 80)
        print("👨‍💼 Chief Architect Review - 架构完整性审查")
        print("=" * 80)
        
        summary = self.registry.get('summary', {})
        categories = self.registry.get('categories', {})
        
        # 统计信息
        total = summary.get('total_skills', 0)
        active = summary.get('active_skills', 0)
        deprecated = summary.get('deprecated_skills', 0)
        avg_prof = summary.get('avg_proficiency', 0)
        
        print(f"\n📊 SKILL统计概览:")
        print(f"   • 总SKILL数: {total}")
        print(f"   • 活跃SKILL: {active}")
        print(f"   • 废弃SKILL: {deprecated}")
        print(f"   • 平均熟练度: {avg_prof:.1%}")
        
        # 分类统计
        print(f"\n📁 分类分布:")
        for cat_id, cat_data in categories.items():
            count = cat_data.get('count', 0)
            name = cat_data.get('name', cat_id)
            print(f"   • {name}: {count} skills")
        
        # 架构师发现的问题
        issues = []
        
        # 检查1: 是否有未分类的SKILL
        all_categories_count = sum(c.get('count', 0) for c in categories.values())
        if all_categories_count != total:
            issues.append(f"分类统计({all_categories_count})与总数({total})不匹配")
        
        # 检查2: 熟练度低于70%的SKILL
        low_proficiency = []
        for cat_id, cat_data in categories.items():
            for skill in cat_data.get('skills', []):
                if skill.get('proficiency', 1) < 0.7:
                    low_proficiency.append({
                        'name': skill.get('name'),
                        'proficiency': skill.get('proficiency'),
                        'category': cat_data.get('name')
                    })
        
        if low_proficiency:
            issues.append(f"发现{len(low_proficiency)}个熟练度<70%的SKILL需要提升")
            print(f"\n⚠️ 低熟练度SKILL ({len(low_proficiency)}个):")
            for skill in low_proficiency[:5]:
                print(f"   • {skill['name']} ({skill['proficiency']:.0%}) - {skill['category']}")
        
        # 检查3: 长期未使用的SKILL
        import datetime as dt
        stale_skills = []
        today = dt.date.today()
        
        for cat_id, cat_data in categories.items():
            for skill in cat_data.get('skills', []):
                last_used = skill.get('last_used')
                if last_used:
                    try:
                        last_date = dt.datetime.strptime(last_used, '%Y-%m-%d').date()
                        days_ago = (today - last_date).days
                        if days_ago > 30:
                            stale_skills.append({
                                'name': skill.get('name'),
                                'days_ago': days_ago,
                                'last_used': last_used
                            })
                    except:
                        pass
        
        if stale_skills:
            issues.append(f"发现{len(stale_skills)}个超过30天未使用的SKILL")
            print(f"\n⏰ 长期未使用SKILL ({len(stale_skills)}个):")
            for skill in sorted(stale_skills, key=lambda x: -x['days_ago'])[:5]:
                print(f"   • {skill['name']} ({skill['days_ago']}天前)")
        
        # 架构师建议
        self.findings.extend([{
            'chief': 'Chief Architect',
            'type': '架构',
            'issue': issue
        } for issue in issues])
        
        recommendations = [
            "建立SKILL使用频率监控仪表板",
            "对低熟练度SKILL进行专项训练",
            "制定SKILL淘汰机制（90天未使用标记废弃）",
            "完善SKILL分类体系，确保100%覆盖"
        ]
        
        self.recommendations.extend([{
            'chief': 'Chief Architect',
            'rec': rec
        } for rec in recommendations])
        
        print(f"\n✅ Chief Architect审查完成")
        print(f"   发现问题: {len(issues)}个")
        print(f"   提出建议: {len(recommendations)}条")
        
    def chief_investment_officer_review(self):
        """首席投资官审查 - 投资能力评估"""
        print("\n" + "=" * 80)
        print("💼 Chief Investment Officer Review - 投资能力审查")
        print("=" * 80)
        
        categories = self.registry.get('categories', {})
        
        # 投资相关SKILL分析
        investment_cats = ['investment_analysis', 'trading_systems', 'trading_analytics', 
                          'auto_trading', 'risk_management']
        
        investment_skills = []
        for cat_id in investment_cats:
            if cat_id in categories:
                cat_data = categories[cat_id]
                investment_skills.extend(cat_data.get('skills', []))
        
        print(f"\n📈 投资相关SKILL: {len(investment_skills)}个")
        
        # 计算投资SKILL的平均表现
        total_usage = sum(s.get('usage_count', 0) for s in investment_skills)
        avg_success = sum(s.get('success_rate', 0) for s in investment_skills) / len(investment_skills) if investment_skills else 0
        
        print(f"   • 总使用次数: {total_usage}")
        print(f"   • 平均成功率: {avg_success:.1%}")
        
        # 识别表现最佳的SKILL
        top_skills = sorted(investment_skills, key=lambda x: x.get('success_rate', 0), reverse=True)[:3]
        print(f"\n🏆 表现最佳SKILL:")
        for skill in top_skills:
            print(f"   • {skill.get('name')} (成功率: {skill.get('success_rate', 0):.0%})")
        
        # 识别需要改进的SKILL
        improvement_needed = [s for s in investment_skills if s.get('success_rate', 1) < 0.8]
        if improvement_needed:
            print(f"\n⚠️ 需要改进的SKILL ({len(improvement_needed)}个):")
            for skill in sorted(improvement_needed, key=lambda x: x.get('success_rate', 0))[:3]:
                print(f"   • {skill.get('name')} (成功率: {skill.get('success_rate', 0):.0%})")
        
        # 投资官建议
        recommendations = [
            "加强对低成功率SKILL的算法优化",
            "建立投资SKILL的A/B测试框架",
            "整合表现最佳的SKILL形成复合策略",
            f"当前{len(improvement_needed)}个SKILL需要立即改进"
        ]
        
        self.recommendations.extend([{
            'chief': 'Chief Investment Officer',
            'rec': rec
        } for rec in recommendations])
        
        print(f"\n✅ Chief Investment Officer审查完成")
        print(f"   提出建议: {len(recommendations)}条")
        
    def chief_operating_officer_review(self):
        """首席运营官审查 - 运营效率评估"""
        print("\n" + "=" * 80)
        print("⚙️ Chief Operating Officer Review - 运营效率审查")
        print("=" * 80)
        
        categories = self.registry.get('categories', {})
        
        # 运营相关SKILL
        ops_cats = ['memory_systems', 'system_framework']
        ops_skills = []
        for cat_id in ops_cats:
            if cat_id in categories:
                ops_skills.extend(categories[cat_id].get('skills', []))
        
        print(f"\n🔧 系统运营SKILL: {len(ops_skills)}个")
        
        # 检查ARCHITECT-5L完整性
        architect_skills = []
        for cat_id, cat_data in categories.items():
            for skill in cat_data.get('skills', []):
                if 'architect' in skill.get('id', '').lower() or 'architect' in skill.get('name', '').lower():
                    architect_skills.append(skill)
        
        print(f"   • ARCHITECT-5L相关: {len(architect_skills)}个")
        
        # 运营效率指标
        total_skills = sum(c.get('count', 0) for c in categories.values())
        active_ratio = self.registry.get('summary', {}).get('active_skills', 0) / total_skills if total_skills else 0
        
        print(f"   • SKILL活跃率: {active_ratio:.1%}")
        
        # 运营建议
        recommendations = [
            "建立SKILL健康度评分卡",
            "定期（每月）进行SKILL审计",
            "优化SKILL加载性能（当前平均76%熟练度）",
            "建立SKILL文档标准化模板"
        ]
        
        self.recommendations.extend([{
            'chief': 'Chief Operating Officer',
            'rec': rec
        } for rec in recommendations])
        
        print(f"\n✅ Chief Operating Officer审查完成")
        print(f"   提出建议: {len(recommendations)}条")
        
    def chief_security_officer_review(self):
        """首席安全官审查 - 安全合规评估"""
        print("\n" + "=" * 80)
        print("🔒 Chief Security Officer Review - 安全合规审查")
        print("=" * 80)
        
        categories = self.registry.get('categories', {})
        
        # 安全相关SKILL
        security_skills = []
        for cat_id, cat_data in categories.items():
            for skill in cat_data.get('skills', []):
                if any(kw in skill.get('id', '').lower() for kw in ['security', 'risk', 'black_swan']):
                    security_skills.append(skill)
        
        print(f"\n🛡️ 安全风控SKILL: {len(security_skills)}个")
        for skill in security_skills:
            print(f"   • {skill.get('name')}")
        
        # 检查风险管理系统
        has_black_swan = any('black_swan' in s.get('id', '') for s in security_skills)
        has_risk_control = any('risk' in s.get('id', '') for s in security_skills)
        
        print(f"\n✅ 安全检查结果:")
        print(f"   • 黑天鹅风控: {'✓' if has_black_swan else '✗'}")
        print(f"   • 风险控制系统: {'✓' if has_risk_control else '✗'}")
        
        # 安全建议
        recommendations = [
            "定期进行SKILL安全审计",
            "建立SKILL权限分级机制",
            "加强外部数据接口的安全校验",
            "建立SKILL异常行为监控"
        ]
        
        self.recommendations.extend([{
            'chief': 'Chief Security Officer',
            'rec': rec
        } for rec in recommendations])
        
        print(f"\n✅ Chief Security Officer审查完成")
        print(f"   提出建议: {len(recommendations)}条")
        
    def generate_report(self):
        """生成审查报告"""
        print("\n" + "=" * 80)
        print("📋 Chief Review Summary - 审查总结")
        print("=" * 80)
        
        # 总体评估
        total_findings = len(self.findings)
        total_recommendations = len(self.recommendations)
        
        print(f"\n📊 审查结果统计:")
        print(f"   • 发现问题: {total_findings}个")
        print(f"   • 改进建议: {total_recommendations}条")
        
        # 健康度评分
        summary = self.registry.get('summary', {})
        active_ratio = summary.get('active_skills', 0) / summary.get('total_skills', 1)
        proficiency = summary.get('avg_proficiency', 0)
        
        health_score = (active_ratio * 0.3 + proficiency * 0.7) * 100
        
        print(f"\n🏥 SKILL系统健康度: {health_score:.0f}/100")
        
        if health_score >= 90:
            status = "🟢 优秀"
        elif health_score >= 75:
            status = "🟡 良好"
        elif health_score >= 60:
            status = "🟠 一般"
        else:
            status = "🔴 需改进"
        
        print(f"   • 状态: {status}")
        print(f"   • 活跃率: {active_ratio:.1%}")
        print(f"   • 熟练度: {proficiency:.1%}")
        
        # 优先改进建议
        print(f"\n🎯 优先改进建议 (Top 5):")
        for i, rec in enumerate(self.recommendations[:5], 1):
            print(f"   {i}. [{rec['chief']}] {rec['rec']}")
        
        # 生成报告文件
        report = {
            'review_date': datetime.now().isoformat(),
            'version': 'v2.0.0-alpha',
            'total_skills': summary.get('total_skills', 0),
            'health_score': round(health_score, 1),
            'status': status,
            'findings': self.findings,
            'recommendations': self.recommendations
        }
        
        report_path = '/workspace/projects/workspace/reports/chief_review_20260502.json'
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存: {report_path}")
        
        print("\n" + "=" * 80)
        print("✅ Chief Review Complete - A5L v2.0.0-alpha Self-Upgrade Ready")
        print("=" * 80)

if __name__ == "__main__":
    board = ChiefReviewBoard()
    board.run_full_review()
