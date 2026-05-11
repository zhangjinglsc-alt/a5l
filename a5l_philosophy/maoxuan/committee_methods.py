"""
《党委会的工作方法》 - 投资决策委员会运作机制
对应毛选：党委书记要善于当班长，学会弹钢琴，胸中有数
"""

from typing import Dict, List
from datetime import datetime


class PartyCommitteeMethods:
    """
    投资决策委员会运作机制
    
    十二条工作方法（投资版）：
    1. 党委书记要善于当班长 - CA要善于领导六管理者
    2. 要把问题摆到桌面上来 - 透明沟通
    3. 互通情报 - 信息共享
    4. 不懂得和不了解的东西要问下级 - 向SKILL学习
    5. 学会弹钢琴 - 统筹兼顾各层级
    6. 要抓紧 - 关键任务不拖延
    7. 胸中有数 - 数据驱动决策
    8. 安民告示 - 提前通知重要事项
    9. 精兵简政 - 精简流程提高效率
    10. 注意团结 - 维护团队和谐
    11. 力戒骄傲 - 保持谦逊
    12. 划清界限 - 明确职责边界
    """
    
    def __init__(self):
        self.methods = [
            'be_good_captain',      # 善于当班长
            'put_issues_on_table',  # 摆到桌面上
            'share_intelligence',   # 互通情报
            'ask_subordinates',     # 问下级
            'play_piano',          # 弹钢琴
            'grasp_tightly',       # 抓紧
            'have_numbers',        # 胸中有数
            'advance_notice',      # 安民告示
            'streamline',          # 精兵简政
            'maintain_unity',      # 注意团结
            'avoid_arrogance',     # 力戒骄傲
            'clear_boundaries'     # 划清界限
        ]
    
    def lead_as_captain(self, committee_members: list, agenda: dict) -> dict:
        """党委书记要善于当班长"""
        return {
            'method': 'be_good_captain',
            'ca_role': '班长/协调者/最终决策者',
            'leadership_principles': [
                '团结六管理者',
                '发挥各自特长',
                '统一目标方向'
            ]
        }
    
    def put_issues_on_table(self, issues: list) -> dict:
        """要把问题摆到桌面上来"""
        return {
            'method': 'put_issues_on_table',
            'transparent_issues': issues,
            'communication_principle': '不隐瞒分歧，公开讨论'
        }
    
    def share_intelligence(self, data_sources: list) -> dict:
        """互通情报"""
        shared_data = {}
        for source in data_sources:
            shared_data[source['manager']] = source['data']
        
        return {
            'method': 'share_intelligence',
            'shared_knowledge': shared_data,
            'update_frequency': 'real_time'
        }
    
    def ask_subordinates(self, question: str, skill_modules: list) -> dict:
        """不懂得和不了解的东西要问下级（SKILL）"""
        answers = []
        for skill in skill_modules:
            answer = self._consult_skill(skill, question)
            answers.append({
                'skill': skill,
                'answer': answer
            })
        
        return {
            'method': 'ask_subordinates',
            'question': question,
            'consulted_skills': answers,
            'principle': '向下级学习，不耻下问'
        }
    
    def play_piano(self, tasks: list, priorities: dict) -> dict:
        """学会弹钢琴 - 统筹兼顾"""
        # 按优先级和依赖关系排序
        sorted_tasks = sorted(tasks, 
                             key=lambda t: (priorities.get(t['layer'], 0), t['urgency']),
                             reverse=True)
        
        return {
            'method': 'play_piano',
            'coordinated_tasks': sorted_tasks,
            'principle': '抓住重点，统筹兼顾，各层级协调'
        }
    
    def grasp_tightly(self, critical_tasks: list) -> dict:
        """要抓紧 - 关键任务不拖延"""
        return {
            'method': 'grasp_tightly',
            'critical_milestones': critical_tasks,
            'tracking_mechanism': 'daily_checkin',
            'escalation_rule': 'delayed_>1day_escalate_to_CA'
        }
    
    def have_numbers(self, metrics: dict) -> dict:
        """胸中有数 - 数据驱动"""
        return {
            'method': 'have_numbers',
            'key_metrics': {
                'portfolio_pnl': metrics.get('pnl', 0),
                'risk_exposure': metrics.get('risk', 0),
                'position_count': metrics.get('positions', 0),
                'cash_ratio': metrics.get('cash', 0)
            },
            'decision_basis': '数据而非感觉'
        }
    
    def advance_notice(self, important_events: list, notice_days: int = 3) -> dict:
        """安民告示 - 提前通知"""
        return {
            'method': 'advance_notice',
            'upcoming_events': important_events,
            'notice_period_days': notice_days,
            'notification_channels': ['dashboard', 'alert', 'email']
        }
    
    def streamline(self, processes: list) -> dict:
        """精兵简政 - 精简流程"""
        optimized = [p for p in processes if not p.get('redundant', False)]
        
        return {
            'method': 'streamline',
            'original_count': len(processes),
            'optimized_count': len(optimized),
            'efficiency_gain': f'{(1 - len(optimized)/len(processes))*100:.0f}%'
        }
    
    def maintain_unity(self, conflicts: list) -> dict:
        """注意团结 - 维护和谐"""
        resolution = self._resolve_conflicts(conflicts)
        
        return {
            'method': 'maintain_unity',
            'conflicts_resolved': resolution,
            'team_morale': 'high',
            'unity_principle': '团结-批评-团结'
        }
    
    def avoid_arrogance(self, performance: dict) -> dict:
        """力戒骄傲 - 保持谦逊"""
        recent_wins = performance.get('consecutive_wins', 0)
        
        if recent_wins >= 3:
            warning = '连续盈利，警惕过度自信'
        else:
            warning = None
        
        return {
            'method': 'avoid_arrogance',
            'humility_check': warning,
            'continuous_learning': True
        }
    
    def clear_boundaries(self, responsibilities: dict) -> dict:
        """划清界限 - 明确职责"""
        return {
            'method': 'clear_boundaries',
            'role_definitions': responsibilities,
            'accountability': '明确到个人'
        }
    
    def execute_all_methods(self, context: dict) -> dict:
        """执行全部十二条工作方法"""
        results = []
        
        method_mapping = {
            'be_good_captain': self.lead_as_captain,
            'put_issues_on_table': self.put_issues_on_table,
            'share_intelligence': self.share_intelligence,
            'ask_subordinates': self.ask_subordinates,
            'play_piano': self.play_piano,
            'grasp_tightly': self.grasp_tightly,
            'have_numbers': self.have_numbers,
            'advance_notice': self.advance_notice,
            'streamline': self.streamline,
            'maintain_unity': self.maintain_unity,
            'avoid_arrogance': self.avoid_arrogance,
            'clear_boundaries': self.clear_boundaries
        }
        
        for method_key in self.methods:
            method_func = method_mapping.get(method_key)
            if method_func:
                result = method_func(context.get(method_key, {}))
                results.append(result)
        
        return {
            'all_methods_executed': results,
            'effectiveness': '委员会运作高效有序'
        }
    
    def _consult_skill(self, skill: str, question: str) -> str:
        """咨询SKILL"""
        return f'{skill}回答：{question}'
    
    def _resolve_conflicts(self, conflicts: list) -> list:
        """解决冲突"""
        return [{'resolved': True} for _ in conflicts]
