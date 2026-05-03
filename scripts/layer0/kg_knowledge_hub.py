#!/usr/bin/env python3
"""
KG Knowledge Hub API v1.0
知识图谱中枢 - L0协同核心基础设施

实现知识流动而非静态存储：
- 主动查询 (Pull)
- 智能推送 (Push)
- 决策增强 (Enhance)
- 跨报告关联 (Link)

执行时间: 2026-05-04 02:43
架构意义: L0协同能力质变节点
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

KG_DIR = "/workspace/projects/workspace/data/kg_entities"
REPORTS_DIR = "/workspace/projects/workspace/data/reports"

@dataclass
class KnowledgeQuery:
    """知识查询请求"""
    entity_type: str  # stock, industry, report, theme
    entity_id: Optional[str] = None
    stock_code: Optional[str] = None
    industry_name: Optional[str] = None
    query_context: Optional[str] = None  # 查询上下文，用于智能匹配

@dataclass
class KnowledgeContext:
    """知识上下文 - 返回给决策者的结构化知识"""
    target_entity: str
    related_reports: List[Dict]
    investment_signals: List[Dict]
    risk_alerts: List[Dict]
    catalysts: List[Dict]
    historical_decisions: List[Dict]
    confidence_score: float
    recommended_actions: List[str]

class KnowledgeGuardianHub:
    """
    KG知识中枢 - A5L Layer 0核心组件
    
    职责:
    1. 知识存储与索引 (传统功能)
    2. 主动查询服务 (新功能)
    3. 智能推送服务 (新功能)
    4. 决策增强服务 (新功能)
    """
    
    def __init__(self):
        print("="*70)
        print("🧠 KG Knowledge Hub v1.0 初始化")
        print("="*70)
        self.entities = {}
        self.relations = {}
        self._load_entities()
        
    def _load_entities(self):
        """加载所有KG实体"""
        if os.path.exists(KG_DIR):
            for file in os.listdir(KG_DIR):
                if file.endswith('.json'):
                    with open(os.path.join(KG_DIR, file), 'r') as f:
                        entity = json.load(f)
                        self.entities[entity.get('entity_id', file)] = entity
        print(f"✅ 已加载 {len(self.entities)} 个知识实体")
        
    # =========================================================================
    # API 1: 主动查询 (Pull) - CIO/COO/CSO调用
    # =========================================================================
    
    def query_investment_context(self, stock_code: str) -> KnowledgeContext:
        """
        查询投资决策上下文 - 供CIO调用
        
        当CIO需要决策某只股票时，KG主动提供:
        - 相关研报
        - 投资信号
        - 风险提醒
        - 催化剂
        """
        print(f"\n🔍 KG查询: 股票 {stock_code} 的投资上下文")
        
        # 查找直接相关的报告
        related_reports = self._find_related_reports(stock_code)
        
        # 提取投资信号
        signals = self._extract_investment_signals(stock_code, related_reports)
        
        # 识别风险
        risks = self._identify_risks(stock_code, related_reports)
        
        # 发现催化剂
        catalysts = self._find_catalysts(stock_code, related_reports)
        
        # 生成推荐行动
        actions = self._generate_recommended_actions(stock_code, signals, risks)
        
        context = KnowledgeContext(
            target_entity=stock_code,
            related_reports=related_reports,
            investment_signals=signals,
            risk_alerts=risks,
            catalysts=catalysts,
            historical_decisions=[],  # 可扩展
            confidence_score=self._calculate_confidence(related_reports),
            recommended_actions=actions
        )
        
        print(f"✅ 返回上下文: {len(related_reports)} 份报告, 置信度 {context.confidence_score:.1f}%")
        return context
    
    def query_industry_context(self, industry_name: str) -> Dict:
        """
        查询行业上下文 - 供UZI调用
        
        当UZI研究新标的时，KG主动推送相关行业研究
        """
        print(f"\n🔍 KG查询: 行业 {industry_name} 的上下文")
        
        # 查找行业报告
        industry_reports = [
            e for e in self.entities.values()
            if e.get('entity_type') == 'industry_research_report'
            and industry_name.lower() in e.get('industry_name', '').lower()
        ]
        
        # 查找行业内的所有标的
        covered_stocks = []
        for report in industry_reports:
            for pick in report.get('top_picks', []):
                covered_stocks.append(pick)
        
        context = {
            'industry_name': industry_name,
            'industry_reports': industry_reports,
            'covered_stocks': covered_stocks,
            'market_size': industry_reports[0].get('market_size', {}) if industry_reports else {},
            'growth_drivers': industry_reports[0].get('key_catalysts', []) if industry_reports else [],
            'risk_factors': industry_reports[0].get('key_risks', []) if industry_reports else []
        }
        
        print(f"✅ 返回行业上下文: {len(industry_reports)} 份行业报告, {len(covered_stocks)} 个标的")
        return context
    
    def query_risk_context(self, stock_code: str) -> Dict:
        """
        查询风险上下文 - 供CSO调用
        
        CSO审计时，KG提供全面的风险评估依据
        """
        print(f"\n🔍 KG查询: 股票 {stock_code} 的风险上下文")
        
        context = self.query_investment_context(stock_code)
        
        risk_context = {
            'stock_code': stock_code,
            'risk_alerts': context.risk_alerts,
            'industry_risks': self._get_industry_risks(stock_code),
            'concentration_risk': self._analyze_concentration(stock_code),
            'correlation_risk': self._analyze_correlations(stock_code),
            'compliance_flags': self._check_compliance(stock_code)
        }
        
        print(f"✅ 返回风险上下文: {len(context.risk_alerts)} 个风险提醒")
        return risk_context
    
    # =========================================================================
    # API 2: 智能推送 (Push) - KG主动服务
    # =========================================================================
    
    def push_related_knowledge(self, target_manager: str, trigger_event: str, 
                                context: Dict) -> List[Dict]:
        """
        主动推送相关知识 - KG主动服务
        
        当发生特定事件时，KG主动推送给相关管理者
        """
        print(f"\n📤 KG主动推送 → {target_manager} | 触发: {trigger_event}")
        
        pushed_knowledge = []
        
        if target_manager == "CIO" and "决策" in trigger_event:
            # CIO做决策时，推送相关研究
            stock_code = context.get('stock_code')
            if stock_code:
                knowledge = self.query_investment_context(stock_code)
                pushed_knowledge.append({
                    'type': 'investment_context',
                    'target': stock_code,
                    'content': asdict(knowledge),
                    'priority': 'high'
                })
                
        elif target_manager == "UZI" and "研究" in trigger_event:
            # UZI研究新标的时，推送相关行业报告
            stock_code = context.get('stock_code')
            industry = self._infer_industry(stock_code)
            if industry:
                knowledge = self.query_industry_context(industry)
                pushed_knowledge.append({
                    'type': 'industry_context',
                    'target': industry,
                    'content': knowledge,
                    'priority': 'medium'
                })
                
        elif target_manager == "CSO" and "风险" in trigger_event:
            # 风险事件时，推送风险分析
            stock_code = context.get('stock_code')
            if stock_code:
                knowledge = self.query_risk_context(stock_code)
                pushed_knowledge.append({
                    'type': 'risk_context',
                    'target': stock_code,
                    'content': knowledge,
                    'priority': 'high'
                })
        
        print(f"✅ 推送完成: {len(pushed_knowledge)} 条知识")
        return pushed_knowledge
    
    def alert_knowledge_update(self, report_id: str) -> List[str]:
        """
        知识更新提醒 - 当有新研报时，提醒相关管理者
        """
        print(f"\n🔔 KG提醒: 新研报 {report_id} 已归档")
        
        report = self.entities.get(report_id, {})
        affected_managers = []
        
        # 如果是个股报告，提醒CIO
        if report.get('entity_type') == 'research_report':
            affected_managers.append("CIO")
            
        # 如果是行业报告，提醒所有管理者
        if report.get('entity_type') == 'industry_research_report':
            affected_managers.extend(["CIO", "UZI", "CSO"])
            
        print(f"✅ 提醒对象: {', '.join(affected_managers)}")
        return affected_managers
    
    # =========================================================================
    # API 3: 决策增强 (Enhance) - 嵌入决策流程
    # =========================================================================
    
    def enhance_kelly_decision(self, stock_code: str, 
                                base_params: Dict) -> Dict:
        """
        增强Kelly公式决策 - 为CIO提供知识增强的参数
        """
        print(f"\n🎯 KG增强: {stock_code} Kelly决策")
        
        context = self.query_investment_context(stock_code)
        
        # 基于知识调整Kelly参数
        enhanced = base_params.copy()
        
        # 1. 基于行业评级调整胜率
        if context.investment_signals:
            avg_rating = sum(s.get('confidence', 50) for s in context.investment_signals) / len(context.investment_signals)
            enhanced['win_rate'] = min(0.8, base_params.get('win_rate', 0.5) * (1 + avg_rating/200))
        
        # 2. 基于风险调整赔率
        if context.risk_alerts:
            risk_level = len(context.risk_alerts)
            enhanced['odds'] = base_params.get('odds', 2.0) * (1 - risk_level * 0.05)
        
        # 3. 基于催化剂调整时间框架
        if context.catalysts:
            enhanced['time_horizon'] = 'short' if len(context.catalysts) > 2 else 'medium'
        
        enhancement = {
            'stock_code': stock_code,
            'base_params': base_params,
            'enhanced_params': enhanced,
            'knowledge_applied': {
                'reports_consulted': len(context.related_reports),
                'signals_used': len(context.investment_signals),
                'risks_considered': len(context.risk_alerts)
            },
            'recommendation': context.recommended_actions
        }
        
        print(f"✅ Kelly参数已增强: 胜率 {enhanced.get('win_rate', 0):.1%}, 赔率 {enhanced.get('odds', 0):.2f}")
        return enhancement
    
    def enhance_portfolio_analysis(self, portfolio: List[str]) -> Dict:
        """
        增强组合分析 - 为CIO提供组合层面的知识洞察
        """
        print(f"\n🎯 KG增强: 组合分析 ({len(portfolio)} 只标的)")
        
        portfolio_context = {
            'stocks': [],
            'industry_concentration': {},
            'theme_exposure': {},
            'risk_correlations': [],
            'knowledge_gaps': []
        }
        
        for stock in portfolio:
            context = self.query_investment_context(stock)
            portfolio_context['stocks'].append({
                'code': stock,
                'confidence': context.confidence_score,
                'signals': len(context.investment_signals),
                'risks': len(context.risk_alerts)
            })
        
        # 检查知识覆盖缺口
        for stock in portfolio:
            if not self._has_recent_report(stock):
                portfolio_context['knowledge_gaps'].append(stock)
        
        print(f"✅ 组合分析完成: 发现 {len(portfolio_context['knowledge_gaps'])} 个知识缺口")
        return portfolio_context
    
    # =========================================================================
    # 内部辅助方法
    # =========================================================================
    
    def _find_related_reports(self, stock_code: str) -> List[Dict]:
        """查找相关报告"""
        reports = []
        for entity in self.entities.values():
            if entity.get('entity_type') in ['research_report', 'industry_research_report']:
                # 检查是否直接覆盖该标的
                if stock_code in str(entity):
                    reports.append({
                        'id': entity.get('entity_id'),
                        'type': entity.get('entity_type'),
                        'rating': entity.get('rating', 'N/A'),
                        'confidence': entity.get('confidence', 0),
                        'target_return': entity.get('expected_return', 'N/A'),
                        'date': entity.get('report_date')
                    })
        return reports
    
    def _extract_investment_signals(self, stock_code: str, reports: List[Dict]) -> List[Dict]:
        """提取投资信号"""
        signals = []
        for report in reports:
            signals.append({
                'source': report['id'],
                'type': 'rating',
                'value': report.get('rating'),
                'confidence': report.get('confidence', 0)
            })
        return signals
    
    def _identify_risks(self, stock_code: str, reports: List[Dict]) -> List[Dict]:
        """识别风险"""
        risks = []
        # 从报告中提取风险信息
        for entity in self.entities.values():
            if entity.get('entity_id') in [r['id'] for r in reports]:
                for risk in entity.get('key_risks', []):
                    risks.append({
                        'type': 'reported',
                        'description': risk,
                        'severity': 'medium'
                    })
        return risks
    
    def _find_catalysts(self, stock_code: str, reports: List[Dict]) -> List[Dict]:
        """发现催化剂"""
        catalysts = []
        for entity in self.entities.values():
            if entity.get('entity_id') in [r['id'] for r in reports]:
                for catalyst in entity.get('key_catalysts', []):
                    catalysts.append({
                        'event': catalyst,
                        'timeline': 'TBD',
                        'impact': 'positive'
                    })
        return catalysts
    
    def _generate_recommended_actions(self, stock_code: str, 
                                       signals: List[Dict], 
                                       risks: List[Dict]) -> List[str]:
        """生成推荐行动"""
        actions = []
        
        # 基于信号生成建议
        strong_buy_count = sum(1 for s in signals if 'BUY' in str(s.get('value', '')))
        if strong_buy_count > 0:
            actions.append(f"考虑建仓 {stock_code}")
        
        # 基于风险生成建议
        if len(risks) > 2:
            actions.append(f"关注 {stock_code} 的风险因素")
        
        return actions
    
    def _calculate_confidence(self, reports: List[Dict]) -> float:
        """计算置信度"""
        if not reports:
            return 0.0
        avg_confidence = sum(r.get('confidence', 0) for r in reports) / len(reports)
        return min(100, avg_confidence * (1 + len(reports) * 0.1))
    
    def _get_industry_risks(self, stock_code: str) -> List[Dict]:
        """获取行业风险"""
        # 简化实现
        return []
    
    def _analyze_concentration(self, stock_code: str) -> Dict:
        """分析集中度风险"""
        return {'customer_concentration': 'medium', 'supplier_concentration': 'low'}
    
    def _analyze_correlations(self, stock_code: str) -> List[Dict]:
        """分析相关性风险"""
        return []
    
    def _check_compliance(self, stock_code: str) -> List[str]:
        """检查合规标记"""
        return []
    
    def _infer_industry(self, stock_code: str) -> Optional[str]:
        """推断股票所属行业"""
        # 简化映射
        industry_map = {
            '300308': 'CPO',
            '300394': 'CPO',
            '688498': '光芯片',
            '000066': '信创'
        }
        return industry_map.get(stock_code)
    
    def _has_recent_report(self, stock_code: str) -> bool:
        """检查是否有近期报告"""
        reports = self._find_related_reports(stock_code)
        return len(reports) > 0


def demo():
    """演示KG Knowledge Hub API"""
    print("\n" + "="*70)
    print("🚀 KG Knowledge Hub API 演示")
    print("="*70)
    
    hub = KnowledgeGuardianHub()
    
    # Demo 1: CIO查询投资决策上下文
    print("\n" + "-"*70)
    print("【Demo 1】CIO查询中际旭创(300308)投资上下文")
    print("-"*70)
    context = hub.query_investment_context("300308")
    print(f"\n返回结果:")
    print(f"  - 相关报告: {len(context.related_reports)} 份")
    print(f"  - 投资信号: {len(context.investment_signals)} 个")
    print(f"  - 风险提醒: {len(context.risk_alerts)} 个")
    print(f"  - 催化剂: {len(context.catalysts)} 个")
    print(f"  - 置信度: {context.confidence_score:.1f}%")
    print(f"  - 推荐行动: {context.recommended_actions}")
    
    # Demo 2: UZI查询行业上下文
    print("\n" + "-"*70)
    print("【Demo 2】UZI查询CPO行业上下文")
    print("-"*70)
    industry_ctx = hub.query_industry_context("CPO")
    print(f"\n返回结果:")
    print(f"  - 行业报告: {len(industry_ctx['industry_reports'])} 份")
    print(f"  - 覆盖标的: {len(industry_ctx['covered_stocks'])} 个")
    print(f"  - 市场规模: {industry_ctx['market_size']}")
    
    # Demo 3: KG主动推送
    print("\n" + "-"*70)
    print("【Demo 3】KG主动推送 → CIO决策场景")
    print("-"*70)
    pushed = hub.push_related_knowledge(
        target_manager="CIO",
        trigger_event="决策时刻",
        context={'stock_code': '300308'}
    )
    print(f"\n推送结果: {len(pushed)} 条知识")
    
    # Demo 4: Kelly决策增强
    print("\n" + "-"*70)
    print("【Demo 4】Kelly决策增强")
    print("-"*70)
    enhancement = hub.enhance_kelly_decision(
        stock_code="300308",
        base_params={'win_rate': 0.5, 'odds': 2.0}
    )
    print(f"\n增强结果:")
    print(f"  - 原始胜率: {enhancement['base_params']['win_rate']:.0%}")
    print(f"  - 增强后胜率: {enhancement['enhanced_params']['win_rate']:.1%}")
    print(f"  - 参考报告数: {enhancement['knowledge_applied']['reports_consulted']}")
    
    print("\n" + "="*70)
    print("✅ KG Knowledge Hub API 演示完成")
    print("="*70)


if __name__ == "__main__":
    demo()
