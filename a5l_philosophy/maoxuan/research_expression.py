"""
《在延安文艺座谈会上的讲话》 - 投资研究与表达系统
对应毛选：研究问题从实际出发，表达要服务于对象
"""

from typing import Dict, List
from datetime import datetime


class InvestmentResearchExpression:
    """
    投资研究与表达系统
    
    核心思想：
    - 研究从实际出发：从市场实际出发，而非从书本/愿望出发
    - 表达服务于对象：报告要服务于投资决策，而非自我表达
    - 普及与提高：基础研究普及化，深度研究专业化
    """
    
    def __init__(self):
        self.research_standards = {
            'source_verification': True,
            'data_traceability': True,
            'logic_clarity': True
        }
    
    def conduct_research_from_reality(self, topic: str, market_data: dict) -> dict:
        """从实际出发进行研究"""
        # 避免从书本/愿望出发的常见错误
        pitfalls = {
            'wishful_thinking': self._check_wishful_thinking(topic),
            'bookishness': self._check_bookishness(topic),
            'subjective_assumptions': self._check_subjective_assumptions(topic)
        }
        
        research = {
            'topic': topic,
            'start_from': 'market_reality',
            'data_sources': self._identify_data_sources(topic, market_data),
            'pitfalls_avoided': [k for k, v in pitfalls.items() if v],
            'research_plan': self._create_research_plan(topic, market_data)
        }
        
        return research
    
    def express_for_audience(self, research: dict, audience: str) -> dict:
        """根据受众进行表达"""
        templates = {
            'cio': {'detail_level': 'high', 'focus': 'actionable_signals'},
            'cao': {'detail_level': 'medium', 'focus': 'risk_factors'},
            'cso': {'detail_level': 'high', 'focus': 'compliance_risks'},
            'public': {'detail_level': 'low', 'focus': 'key_insights'}
        }
        
        template = templates.get(audience, templates['cio'])
        
        return {
            'audience': audience,
            'expression_format': template,
            'content': self._adapt_content(research, template),
            'serving_purpose': f'服务于{audience}的投资决策'
        }
    
    def _check_wishful_thinking(self, topic: str) -> bool:
        """检查是否陷入一厢情愿"""
        wishful_keywords = ['肯定会', '一定会', '必然上涨']
        return any(kw in topic for kw in wishful_keywords)
    
    def _check_bookishness(self, topic: str) -> bool:
        """检查是否陷入教条"""
        return '理论' in topic and '实际' not in topic
    
    def _check_subjective_assumptions(self, topic: str) -> bool:
        """检查主观臆断"""
        return '我觉得' in topic or '我认为' in topic
    
    def _identify_data_sources(self, topic: str, market_data: dict) -> list:
        """识别数据来源"""
        return [
            {'type': 'market_data', 'reliability': 0.95},
            {'type': 'financial_reports', 'reliability': 0.90},
            {'type': 'industry_research', 'reliability': 0.80}
        ]
    
    def _create_research_plan(self, topic: str, market_data: dict) -> dict:
        """创建研究计划"""
        return {
            'phases': [
                {'name': '数据收集', 'duration_days': 3},
                {'name': '分析验证', 'duration_days': 5},
                {'name': '报告撰写', 'duration_days': 2}
            ]
        }
    
    def _adapt_content(self, research: dict, template: dict) -> dict:
        """根据模板调整内容"""
        return {
            'summary': '核心发现摘要',
            'detail_level': template['detail_level'],
            'focus_areas': template['focus']
        }
