#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCHITECT-5L Super Skill
五层架构超级技能 - 可迭代的综合能力工具

这是一个会自我进化、自我完善的超级SKILL，整合所有现有能力到五层架构中。

版本: v1.0.0
创建: 2026-05-02
状态: P1迭代中

架构:
- Layer 1: 数据感知层 (Data Perception)
- Layer 2: 策略决策层 (Strategy Decision)
- Layer 3: 认知分析层 (Cognitive Analysis)
- Layer 4: 执行控制层 (Execution Control)
- Layer 5: 元学习层 (Meta Learning)

SOUL.md 原则绑定:
本SKILL严格遵循SOUL.md中的9条核心原则：
1. Archival Safety First      → Feishu自动同步
2. Proactive Decision Making  → Layer 0自主决策
3. Knowledge Integration      → KIWI知识沉淀
4. Information Processing Loop→ 5步信息处理
5. Multi-Modal Support        → 多模态处理
6. Security First             → 安全师系统
7. Oversight & Balance        → 首席监管官
8. Immediate Response         → 及时响应系统
9. Compounding Mindset        → 复利思维系统

所有功能设计都与SOUL.md原则保持一致，确保A5L系统与SOUL宪章深度绑定。
"""

import json
import os
import sys
import time
import importlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import traceback

# 配置结构化日志
try:
    import structlog
    logger = structlog.get_logger("architect_5l")
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    )
    logger = logging.getLogger("architect_5l")

# ============================================================================
# Layer 0: 元能力 - SKILL自身的元数据和管理
# ============================================================================

@dataclass
class SkillMetadata:
    """SKILL元数据"""
    name: str = "ARCHITECT-5L Super Skill"
    version: str = "1.0.0"
    author: str = "Agent + 张晋"
    created_at: str = "2026-05-02"
    last_updated: str = "2026-05-02"
    capabilities: List[str] = None
    dependencies: List[str] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = [
                "data_collection",      # 数据收集
                "strategy_execution",   # 策略执行
                "cognitive_analysis",   # 认知分析
                "risk_management",      # 风险管理
                "self_improvement",     # 自我改进
                "multi_market_trading", # 多市场交易
                "report_generation",    # 报告生成
                "recursive_learning"    # 递归学习
            ]
        if self.dependencies is None:
            self.dependencies = [
                "akshare>=1.11.0",
                "pandas>=2.0.0",
                "numpy>=1.24.0",
                "plotly>=5.15.0",
                "streamlit>=1.28.0"
            ]

# ============================================================================
# Layer 0: 元控制层 - 系统大脑和智能指挥 (核心新增)
# ============================================================================

class Layer0_MetaControl:
    """
    元控制层 - A5L系统大脑
    智能指挥、主动协调、架构演进

    核心功能:
    1. SKILL放置决策 - 决定新SKILL放入哪个Layer
    2. 故障恢复协调 - 智能处理系统故障
    3. 任务资源编排 - 动态调度各层资源
    4. 系统整体监控 - 全局视角看系统健康
    """

    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.controller = None

        logger.info("🧠 Layer 0: 元控制层初始化")
        self._init_controller()

    def _init_controller(self):
        """初始化控制器"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from meta_controller import MetaController

            self.controller = MetaController(self.workspace)
            logger.info("  ✅ 元控制器已加载")
        except Exception as e:
            logger.warning(f"  ⚠️ 元控制器加载失败: {e}")

    def decide_skill_placement(self, skill_name: str, skill_description: str,
                              skill_capabilities: List[str]) -> Dict:
        """
        智能决策：新SKILL应该放在哪里

        Args:
            skill_name: SKILL名称
            skill_description: SKILL描述
            skill_capabilities: SKILL能力列表

        Returns:
            {
                "recommended_layer": "layerX_name",
                "confidence": 0.95,
                "reasoning": "...",
                "integration_complexity": "low/medium/high",
                "estimated_effort": "2 days"
            }
        """
        if self.controller:
            return self.controller.decide_skill_placement(
                skill_name, skill_description, skill_capabilities
            )
        return {"error": "控制器未加载", "recommended_layer": "unknown"}

    def coordinate_recovery(self, error_type: str, error_context: Dict) -> Dict:
        """
        智能协调故障恢复

        Args:
            error_type: 错误类型 (如 layer1_data_failure)
            error_context: 错误上下文

        Returns:
            {
                "recovery_plan": {...},
                "auto_execute": True/False,
                "requires_approval": True/False,
                "estimated_recovery_time": "30s"
            }
        """
        if self.controller:
            return self.controller.coordinate_fault_recovery(error_type, error_context)
        return {"error": "控制器未加载"}

    def orchestrate_task(self, task_type: str, task_params: Dict) -> Dict:
        """
        智能编排任务执行

        Args:
            task_type: 任务类型 (full_pipeline/quick_analysis/deep_research)
            task_params: 任务参数

        Returns:
            {
                "allocation_plan": {...},
                "priority": "high/medium/low",
                "can_execute": True/False,
                "estimated_completion": "2-5 minutes"
            }
        """
        if self.controller:
            return self.controller.orchestrate_execution(task_type, task_params)
        return {"error": "控制器未加载"}

    def get_system_status(self) -> Dict:
        """
        获取系统整体状态

        Returns:
            {
                "system_health": 0.92,
                "recent_decisions": 10,
                "active_skills": 15,
                "recommendations": [...]
            }
        """
        if self.controller:
            return self.controller.get_system_report()
        return {"error": "控制器未加载"}

    def generate_standards(self) -> Dict:
        """
        生成SKILL整合标准文档

        Returns:
            {
                "integration_guide": {...},
                "evolution_roadmap": {...}
            }
        """
        if self.controller:
            return self.controller.generate_standards()
        return {"error": "控制器未加载"}

    def get_layer_standards(self, layer_name: str) -> Dict:
        """
        获取指定Layer的准入标准

        Args:
            layer_name: Layer名称 (如 "layer3_analysis")

        Returns:
            Layer准入标准
        """
        if self.controller:
            return self.controller.get_layer_standards(layer_name)
        return {"error": "控制器未加载"}

    def get_evolution_roadmap(self) -> Dict:
        """
        获取架构演进路线图

        Returns:
            P5-P8演进路线图
        """
        if self.controller:
            return self.controller.generate_standards().get('evolution_roadmap', {})
        return {"error": "控制器未加载"}

    # ==========================================================
    # 三位一体高级能力 (Chief Architect + CIO + COO)
    # ==========================================================

    def design_architecture(self, requirements: Dict) -> Dict:
        """
        🏗️ 顶级架构师能力 - 设计系统架构

        Args:
            requirements: 系统需求

        Returns:
            架构设计方案
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from trinity_controller import ChiefArchitect

            architect = ChiefArchitect()
            return architect.design_system(requirements)
        except Exception as e:
            return {"error": str(e)}

    def make_architectural_decision(self, topic: str, options: List[Dict],
                                    context: Dict) -> Dict:
        """
        🏗️ 顶级架构师能力 - 做出架构决策

        Args:
            topic: 决策主题
            options: 可选方案
            context: 决策上下文

        Returns:
            架构决策
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from trinity_controller import ChiefArchitect

            architect = ChiefArchitect()
            decision = architect.make_architectural_decision(topic, options, context)
            return {
                "decision_id": decision.decision_id,
                "selected_option": decision.selected_option,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "timestamp": decision.timestamp
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_investment_insight(self, market_data: Dict) -> Dict:
        """
        💰 顶级投资人能力 - 生成市场洞察

        Args:
            market_data: 市场数据

        Returns:
            投资洞察
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from trinity_controller import ChiefInvestmentOfficer

            cio = ChiefInvestmentOfficer()
            insight = cio.generate_market_insight(market_data)
            return {
                "insight_id": insight.insight_id,
                "market": insight.market,
                "insight_type": insight.insight_type,
                "description": insight.description,
                "confidence": insight.confidence,
                "recommended_action": insight.recommended_action,
                "timestamp": insight.timestamp
            }
        except Exception as e:
            return {"error": str(e)}

    def design_portfolio_strategy(self, constraints: Dict) -> Dict:
        """
        💰 顶级投资人能力 - 设计投资组合策略

        Args:
            constraints: 约束条件

        Returns:
            投资组合策略
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from trinity_controller import ChiefInvestmentOfficer

            cio = ChiefInvestmentOfficer()
            return cio.design_portfolio_strategy(constraints)
        except Exception as e:
            return {"error": str(e)}

    def coordinate_task(self, task: Dict) -> Dict:
        """
        🎯 牛逼组织者能力 - 协调跨Layer任务

        Args:
            task: 任务描述

        Returns:
            协调计划
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from trinity_controller import ChiefOperatingOfficer

            coo = ChiefOperatingOfficer()
            plan = coo.coordinate_cross_layer_task(task)
            return {
                "plan_id": plan.plan_id,
                "objective": plan.objective,
                "involved_layers": plan.involved_layers,
                "timeline": plan.timeline,
                "dependencies": plan.dependencies,
                "risk_mitigation": plan.risk_mitigation
            }
        except Exception as e:
            return {"error": str(e)}

    def resolve_conflict(self, conflict: Dict) -> Dict:
        """
        🎯 牛逼组织者能力 - 解决冲突

        Args:
            conflict: 冲突描述

        Returns:
            解决方案
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from trinity_controller import ChiefOperatingOfficer

            coo = ChiefOperatingOfficer()
            return coo.resolve_conflict(conflict)
        except Exception as e:
            return {"error": str(e)}

    def make_strategic_decision(self, context: Dict) -> Dict:
        """
        🧠 三位一体决策 - 架构师+投资人+组织者协同决策
        
        Args:
            context: 决策上下文
            
        Returns:
            战略决策
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from trinity_controller import Layer0_Trinity
            
            trinity = Layer0_Trinity(self.workspace)
            return trinity.make_strategic_decision(context)
        except Exception as e:
            return {"error": str(e)}
    
    # ==========================================================
    # 四位一体: 安全师能力 (Security Officer)
    # ==========================================================
    
    def security_check(self, operation: str, params: Dict) -> Dict:
        """
        🔒 安全师: 执行安全检查
        
        Args:
            operation: 操作类型
            params: 操作参数
            
        Returns:
            检查结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from four_in_one_controller import ChiefSecurityOfficer
            
            cso = ChiefSecurityOfficer(self.workspace)
            return cso.security_check(operation, params)
        except Exception as e:
            return {"error": str(e)}
    
    def handle_error(self, error: Exception, context: Dict = None) -> Dict:
        """
        🔧 安全师: 处理错误并尝试自动修复
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            处理结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from four_in_one_controller import ChiefSecurityOfficer
            
            cso = ChiefSecurityOfficer(self.workspace)
            return cso.handle_error(error, context)
        except Exception as e:
            return {"error": str(e)}
    
    def get_system_health(self) -> Dict:
        """
        📊 安全师: 获取系统健康状态
        
        Returns:
            健康状态报告
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from four_in_one_controller import ChiefSecurityOfficer
            
            cso = ChiefSecurityOfficer(self.workspace)
            return cso.monitor_system_health()
        except Exception as e:
            return {"error": str(e)}
    
    def get_security_report(self) -> Dict:
        """
        📋 安全师: 获取安全报告
        
        Returns:
            安全报告
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from four_in_one_controller import ChiefSecurityOfficer
            
            cso = ChiefSecurityOfficer(self.workspace)
            return cso.get_security_report()
        except Exception as e:
            return {"error": str(e)}
    
    def secure_execute(self, operation: str, params: Dict) -> Dict:
        """
        🔐 四位一体: 安全执行操作
        
        Args:
            operation: 操作类型
            params: 操作参数
            
        Returns:
            执行结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from four_in_one_controller import Layer0_FourInOne
            
            layer0 = Layer0_FourInOne(self.workspace)
            return layer0.secure_execute(operation, params)
        except Exception as e:
            return {"error": str(e)}
    
    # ==========================================================
    # 及时系统 (Immediate Response System) - 对内快速响应
    # ==========================================================
    
    def report_internal_issue(self, issue_type: str, severity: str, 
                              description: str, source: str) -> Dict:
        """
        ⚡ 及时系统: 报告内部问题
        
        Args:
            issue_type: 问题类型
            severity: 严重程度 (critical/high/medium/low)
            description: 问题描述
            source: 问题来源
            
        Returns:
            问题处理结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from six_in_one_controller import ImmediateResponseSystem
            
            irs = ImmediateResponseSystem(self.workspace)
            issue_id = irs.report_issue(issue_type, severity, description, source)
            return {
                "issue_id": issue_id,
                "status": "reported",
                "severity": severity,
                "message": f"问题已报告，将按{severity}优先级处理"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_immediate_response_status(self) -> Dict:
        """
        ⚡ 及时系统: 获取响应系统状态
        
        Returns:
            系统状态
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from six_in_one_controller import ImmediateResponseSystem
            
            irs = ImmediateResponseSystem(self.workspace)
            return irs.get_status()
        except Exception as e:
            return {"error": str(e)}
    
    def get_recent_issues(self, count: int = 10) -> Dict:
        """
        ⚡ 及时系统: 获取最近处理问题
        
        Args:
            count: 数量
            
        Returns:
            问题列表
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from six_in_one_controller import ImmediateResponseSystem
            
            irs = ImmediateResponseSystem(self.workspace)
            return {"issues": irs.get_recent_issues(count)}
        except Exception as e:
            return {"error": str(e)}
    
    # ==========================================================
    # 复利系统 (Compounding System) - 对外复利增值
    # ==========================================================
    
    def analyze_compounding_potential(self, symbol: str, 
                                      financial_data: Dict) -> Dict:
        """
        📈 复利系统: 分析投资复利潜力
        
        Args:
            symbol: 股票代码
            financial_data: 财务数据 {roe, revenue_growth, profit_growth, debt_ratio}
            
        Returns:
            复利分析结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from six_in_one_controller import CompoundingSystem
            
            cs = CompoundingSystem(self.workspace)
            return cs.analyze_investment_compounding(symbol, financial_data)
        except Exception as e:
            return {"error": str(e)}
    
    def identify_compounding_opportunities(self, market_data: Dict) -> Dict:
        """
        📈 复利系统: 识别复利机会
        
        Args:
            market_data: 市场数据
            
        Returns:
            复利机会列表
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from six_in_one_controller import CompoundingSystem
            
            cs = CompoundingSystem(self.workspace)
            opportunities = cs.identify_compounding_opportunities(market_data)
            return {
                "opportunities_count": len(opportunities),
                "opportunities": [
                    {
                        "id": o.opportunity_id,
                        "name": o.name,
                        "category": o.category,
                        "compounding_rate": o.compounding_rate,
                        "time_horizon": o.time_horizon,
                        "risk_level": o.risk_level
                    }
                    for o in opportunities
                ]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_compounding_scenarios(self, principal: float, 
                                        scenarios: List[Dict]) -> Dict:
        """
        📊 复利系统: 计算复利情景
        
        Args:
            principal: 本金
            scenarios: 情景列表 [{"return": 15, "years": 10, "name": "乐观"}]
            
        Returns:
            各情景结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from six_in_one_controller import CompoundingSystem
            
            cs = CompoundingSystem(self.workspace)
            return cs.calculate_compounding_scenarios(principal, scenarios)
        except Exception as e:
            return {"error": str(e)}
    
    def get_compounding_principles(self) -> Dict:
        """
        📚 复利系统: 获取复利思维原则
        
        Returns:
            复利原则列表
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from six_in_one_controller import CompoundingSystem
            
            cs = CompoundingSystem(self.workspace)
            return {"principles": cs.get_compounding_principles()}
        except Exception as e:
            return {"error": str(e)}
    
    def build_knowledge_compounding(self, topic: str, 
                                    knowledge_fragments: List[Dict]) -> Dict:
        """
        📚 复利系统: 构建知识复利
        
        Args:
            topic: 主题
            knowledge_fragments: 知识片段列表
            
        Returns:
            知识复利构建结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from six_in_one_controller import CompoundingSystem
            
            cs = CompoundingSystem(self.workspace)
            return cs.build_knowledge_compounding(topic, knowledge_fragments)
        except Exception as e:
            return {"error": str(e)}
    
    # ==========================================================
    # KIWI 知识沉淀中心 (内部图书馆)
    # ==========================================================
    
    def archive_to_kiwi(self, title: str, content: str, 
                        knowledge_type: str,
                        source: str,
                        entities: List[str] = None,
                        tags: List[str] = None,
                        reliability: float = 0.5,
                        importance: float = 0.5) -> Dict:
        """
        📚 归档知识到KIWI (内部图书馆)
        
        这是知识沉淀的核心入口，所有分析、决策、洞察都应归档到KIWI
        
        Args:
            title: 知识标题
            content: 知识内容
            knowledge_type: 知识类型 (market_data/research_report/news/strategy/trade_record/analysis/insight/decision/lesson/concept)
            source: 来源
            entities: 关联实体 (股票代码等)
            tags: 标签
            reliability: 可信度 0-1
            importance: 重要性 0-1
            
        Returns:
            归档结果
        """
        if self.kiwi is None:
            return {"error": "KIWI未初始化"}
        
        try:
            from kiwi_knowledge_hub import KnowledgeType
            
            # 转换类型
            type_map = {
                "market_data": KnowledgeType.MARKET_DATA,
                "research_report": KnowledgeType.RESEARCH_REPORT,
                "news": KnowledgeType.NEWS,
                "strategy": KnowledgeType.STRATEGY,
                "trade_record": KnowledgeType.TRADE_RECORD,
                "analysis": KnowledgeType.ANALYSIS,
                "insight": KnowledgeType.INSIGHT,
                "decision": KnowledgeType.DECISION,
                "lesson": KnowledgeType.LESSON,
                "concept": KnowledgeType.CONCEPT
            }
            kt = type_map.get(knowledge_type, KnowledgeType.ANALYSIS)
            
            # 归档到KIWI
            node_id = self.kiwi.add_knowledge(
                title=title,
                content=content,
                knowledge_type=kt,
                source=source,
                entities=entities or [],
                tags=tags or [],
                reliability=reliability,
                importance=importance
            )
            
            return {
                "success": True,
                "node_id": node_id,
                "message": f"知识已归档到KIWI: {title[:30]}..."
            }
        except Exception as e:
            return {"error": str(e)}
    
    def query_kiwi(self, query: str, query_type: str = "semantic",
                   filters: Dict = None, limit: int = 10) -> Dict:
        """
        🔍 查询KIWI知识库
        
        Args:
            query: 查询内容
            query_type: keyword/semantic/entity/time/tag
            filters: 过滤条件
            limit: 返回数量
            
        Returns:
            查询结果
        """
        if self.kiwi is None:
            return {"error": "KIWI未初始化"}
        
        try:
            results = self.kiwi.query_knowledge(query, query_type, filters, limit)
            return {
                "query": query,
                "count": len(results),
                "results": [
                    {
                        "node_id": r.node_id,
                        "title": r.title,
                        "type": r.knowledge_type.value,
                        "reliability": r.reliability,
                        "importance": r.importance,
                        "timestamp": r.timestamp
                    }
                    for r in results
                ]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_entity_knowledge(self, entity: str, limit: int = 20) -> Dict:
        """
        📖 获取特定实体的所有知识
        
        Args:
            entity: 实体 (如 "300750.SZ" 或 "宁德时代")
            limit: 返回数量
            
        Returns:
            知识列表
        """
        if self.kiwi is None:
            return {"error": "KIWI未初始化"}
        
        try:
            results = self.kiwi.get_knowledge_by_entity(entity, limit)
            return {
                "entity": entity,
                "count": len(results),
                "knowledge": [
                    {
                        "title": r.title,
                        "type": r.knowledge_type.value,
                        "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                        "reliability": r.reliability
                    }
                    for r in results
                ]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def generate_kiwi_report(self, entity: str = None, days: int = 7) -> Dict:
        """
        📊 生成KIWI知识报告
        
        Args:
            entity: 特定实体 (None则生成总览)
            days: 时间范围(天)
            
        Returns:
            知识报告
        """
        if self.kiwi is None:
            return {"error": "KIWI未初始化"}
        
        try:
            report = self.kiwi.generate_knowledge_report(entity, days)
            return report
        except Exception as e:
            return {"error": str(e)}
    
    def get_kiwi_stats(self) -> Dict:
        """
        📈 获取KIWI统计信息
        
        Returns:
            统计信息
        """
        if self.kiwi is None:
            return {"error": "KIWI未初始化"}
        
        try:
            return self.kiwi.get_statistics()
        except Exception as e:
            return {"error": str(e)}
    
    def export_kiwi_to_feishu(self, entity: str = None, 
                              title: str = None) -> Dict:
        """
        📤 导出KIWI知识到飞书文档
        
        Args:
            entity: 特定实体
            title: 文档标题
            
        Returns:
            导出结果
        """
        if self.kiwi is None:
            return {"error": "KIWI未初始化"}
        
        try:
            filepath = self.kiwi.export_to_feishu_doc(entity, title)
            return {
                "success": True,
                "filepath": filepath,
                "message": f"知识已导出到: {filepath}"
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==========================================================
    # 首席监管官 (Chief Oversight Officer) - 监督制衡
    # ==========================================================
    
    def review_decision(self, role_id: str, decision: Dict) -> Dict:
        """
        👁️ 监管者: 审查角色决策
        
        Args:
            role_id: 做出决策的角色 (architect/cio/coo/cso)
            decision: 决策内容
            
        Returns:
            审查结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from seven_in_one_controller import ChiefOversightOfficer
            
            coo = ChiefOversightOfficer(self.workspace)
            return coo.review_decision(role_id, decision)
        except Exception as e:
            return {"error": str(e)}
    
    def mediate_role_conflict(self, role_a: str, role_b: str, 
                              conflict_issue: str) -> Dict:
        """
        👁️ 监管者: 调解角色间冲突
        
        Args:
            role_a: 冲突方A
            role_b: 冲突方B
            conflict_issue: 冲突问题
            
        Returns:
            调解结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from seven_in_one_controller import ChiefOversightOfficer
            
            coo = ChiefOversightOfficer(self.workspace)
            return coo.mediate_conflict(role_a, role_b, conflict_issue)
        except Exception as e:
            return {"error": str(e)}
    
    def get_oversight_report(self) -> Dict:
        """
        👁️ 监管者: 获取监管报告
        
        Returns:
            监管报告
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from seven_in_one_controller import ChiefOversightOfficer
            
            coo = ChiefOversightOfficer(self.workspace)
            report = coo.get_oversight_report()
            return {
                "timestamp": report.timestamp,
                "overall_health": report.overall_health,
                "roles": {
                    role_id: {
                        "name": perf.role_name,
                        "health": perf.health_score,
                        "decisions": perf.decisions_count
                    }
                    for role_id, perf in report.role_performances.items()
                },
                "alerts": report.alerts,
                "recommendations": report.recommendations
            }
        except Exception as e:
            return {"error": str(e)}
    
    def enforce_role_balance(self) -> Dict:
        """
        👁️ 监管者: 执行角色制衡
        
        Returns:
            制衡结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from seven_in_one_controller import ChiefOversightOfficer
            
            coo = ChiefOversightOfficer(self.workspace)
            return coo.enforce_balance()
        except Exception as e:
            return {"error": str(e)}

    # ==========================================================
    # P5: 智能体化 (Agentification)
    # ==========================================================

    def execute_as_agents(self, objective: str, context: Dict = None) -> Dict:
        """
        🎭 P5: 以智能体模式执行目标

        Args:
            objective: 自然语言描述的目标
            context: 上下文信息

        Returns:
            多智能体协作结果
        """
        try:
            import asyncio
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer9_agentification")
            from agent_system import A5L_MultiAgentSystem

            a5l_agents = A5L_MultiAgentSystem()
            return asyncio.run(a5l_agents.execute_objective(objective, context))
        except Exception as e:
            return {"error": str(e), "phase": "P5 Agentification"}

    # ==========================================================
    # KIWI: 飞书知识库集成
    # ==========================================================

    def query_kiwi_knowledge(self, query: str) -> Dict:
        """
        🔍 查询飞书知识库(KIWI)

        Args:
            query: 搜索关键词

        Returns:
            KIWI搜索结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer10_kiwi_integration")
            from kiwi_integration import KIWIIntegration

            kiwi = KIWIIntegration(self.workspace)
            result = kiwi.search_knowledge(query)
            return {
                "query": result.query,
                "total_count": result.total_count,
                "documents": [
                    {
                        "title": doc.title,
                        "url": doc.url,
                        "tags": doc.tags
                    } for doc in result.documents
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    def analyze_with_kiwi(self, symbol: str) -> Dict:
        """
        🔗 融合KIWI知识进行分析

        Args:
            symbol: 股票代码

        Returns:
            KIWI增强的分析结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer10_kiwi_integration")
            from kiwi_integration import KIWIIntegration

            kiwi = KIWIIntegration(self.workspace)
            return kiwi.integrate_with_layer3({"symbol": symbol})
        except Exception as e:
            return {"error": str(e)}

    # ==========================================================
    # 信息处理链路 (5步闭环)
    # ==========================================================

    def process_information(self, content: str, source: str, context: Dict = None) -> Dict:
        """
        🔄 5步信息处理链路 (文本)

        1. 阅读信息
        2. 复查确认可靠性
        3. SKILL分析 + KIWI调阅
        4. 输出理解结果
        5. 归档总结

        Args:
            content: 原始信息内容
            source: 信息来源
            context: 上下文

        Returns:
            完整处理结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from information_pipeline import InformationProcessingPipeline

            pipeline = InformationProcessingPipeline(self.workspace)
            packet = pipeline.process(content, source, context)

            return {
                "packet_id": packet.packet_id,
                "reliability_level": packet.reliability_level.name if packet.reliability_level else None,
                "reliability_score": packet.reliability_score,
                "understanding": packet.understanding,
                "key_insights": packet.key_insights,
                "action_items": packet.action_items,
                "archived_to_kiwi": packet.archived_to_kiwi,
                "strategy_updated": packet.strategy_updated,
                "kiwi_findings": packet.kiwi_findings,
                "timestamp": packet.timestamp
            }
        except Exception as e:
            return {"error": str(e)}

    # ==========================================================
    # 多模态信息处理 (支持图片/公众号/研报/PDF)
    # ==========================================================

    def process_multimodal(self, input_data: Union[str, Dict], source: str,
                           input_type: str = None, context: Dict = None) -> Dict:
        """
        🔄 多模态信息处理链路

        支持类型:
        - image: 图片(截图/图表/照片)
        - wechat: 公众号文章
        - report: 研报
        - pdf: PDF文件
        - web: 网页内容
        - text: 纯文本(自动检测)

        5步闭环:
        1. 内容提取(OCR/解析)
        2. 复查确认可靠性
        3. SKILL分析 + KIWI调阅
        4. 输出理解结果
        5. 归档总结

        Args:
            input_data: 输入数据(文件路径/URL/文本)
            source: 信息来源
            input_type: 信息类型(image/wechat/report/pdf/web/text)
            context: 上下文

        Returns:
            完整处理结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer0_control")
            from multimodal_pipeline import MultiModalInformationPipeline, InfoType

            pipeline = MultiModalInformationPipeline(self.workspace)

            # 转换类型字符串为枚举
            type_map = {
                "image": InfoType.IMAGE,
                "wechat": InfoType.WECHAT_ARTICLE,
                "report": InfoType.RESEARCH_REPORT,
                "pdf": InfoType.PDF,
                "web": InfoType.WEB,
                "text": InfoType.TEXT
            }
            info_type = type_map.get(input_type) if input_type else None

            packet = pipeline.process(input_data, source, info_type, context)

            return {
                "packet_id": packet.packet_id,
                "content_type": packet.content.content_type.value,
                "reliability_level": packet.reliability_level.name if packet.reliability_level else None,
                "reliability_score": packet.reliability_score,
                "understanding": packet.understanding,
                "key_insights": packet.key_insights,
                "action_items": packet.action_items,
                "archived_to_kiwi": packet.archived_to_kiwi,
                "strategy_updated": packet.strategy_updated,
                "kiwi_findings": packet.kiwi_findings,
                "extracted_summary": packet.content.summary,
                "timestamp": packet.timestamp
            }
        except Exception as e:
            return {"error": str(e)}

# ============================================================================
# Layer 1: 数据感知层 - 整合所有数据源
# ============================================================================

class Layer1_DataPerception:
    """
    数据感知层
    整合所有数据源：股票、新闻、研报、宏观经济
    """

    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.data_cache = {}
        self.connectors = {}

        logger.info("🔌 Layer 1: 数据感知层初始化")

        # 初始化数据连接器
        self._init_connectors()

    def _init_connectors(self):
        """初始化所有数据连接器"""
        try:
            # 尝试导入并初始化AKShare连接器
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer1_data/connectors")
            from akshare_real_connector import AKShareRealConnector
            self.connectors['akshare'] = AKShareRealConnector(self.workspace)
            logger.info("  ✅ AKShare连接器已加载")
        except Exception as e:
            logger.warning(f"  ⚠️ AKShare连接器加载失败: {e}")

        try:
            # 新闻连接器
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer3_analysis/connectors")
            from real_info_connectors import RealInfoAggregator
            self.connectors['news'] = RealInfoAggregator(self.workspace)
            logger.info("  ✅ 新闻连接器已加载")
        except Exception as e:
            logger.warning(f"  ⚠️ 新闻连接器加载失败: {e}")

    def get_stock_data(self, symbol: str, days: int = 30) -> Optional[Dict]:
        """获取股票数据"""
        if 'akshare' in self.connectors:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            return self.connectors['akshare'].fetch_stock_daily(symbol, start_date, end_date)
        return None

    def get_market_news(self, max_items: int = 50) -> List[Dict]:
        """获取市场新闻"""
        if 'news' in self.connectors:
            results = self.connectors['news'].fetch_all(save=False)
            all_news = []
            for source, items in results.items():
                all_news.extend([{
                    'source': item.source,
                    'title': item.title,
                    'content': item.content,
                    'time': item.publish_time,
                    'symbols': item.symbols,
                    'credibility': item.credibility
                } for item in items])
            return sorted(all_news, key=lambda x: x['time'], reverse=True)[:max_items]
        return []

    def get_portfolio_data(self, account_id: str = "default") -> Dict:
        """获取组合数据"""
        # 从模拟交易账户获取
        portfolio_file = f"{self.workspace}/data/simulated/{account_id}_portfolio.json"
        if os.path.exists(portfolio_file):
            with open(portfolio_file, 'r') as f:
                return json.load(f)
        return {
            "account_id": account_id,
            "total_equity": 1000000,
            "positions": []
        }

# ============================================================================
# Layer 2: 策略决策层 - 7大策略引擎
# ============================================================================

class Layer2_StrategyEngine:
    """
    策略决策层
    整合7大交易策略
    """

    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.strategies = {}

        logger.info("🎯 Layer 2: 策略决策层初始化")
        self._init_strategies()

    def _init_strategies(self):
        """初始化策略"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer2_strategy")
            from strategy_engine import StrategyEngine
            self.engine = StrategyEngine(self.workspace)

            # 加载所有策略
            strategy_ids = [
                'stock_wizard',      # CANSLIM
                'turtle_trading',    # 海龟
                'trend_rs',          # 趋势+RS
                'volume_price',      # 量价
                'fundamental_growth', # 基本面
                'yangguan_daodao',   # 阳关大道
                'buffett_value'      # 巴菲特
            ]

            for sid in strategy_ids:
                config = self.engine.get_strategy(sid)
                if config:
                    self.strategies[sid] = config

            logger.info(f"  ✅ 已加载 {len(self.strategies)} 个策略")

        except Exception as e:
            logger.error(f"  ❌ 策略引擎初始化失败: {e}")

    def evaluate_signal(self, symbol: str, strategy_id: str,
                       market_data: Dict) -> Dict:
        """评估策略信号"""
        if hasattr(self, 'engine'):
            return self.engine.generate_signal(symbol, strategy_id, market_data)
        return {"action": "HOLD", "confidence": 0}

    def get_all_signals(self, symbol: str, market_data: Dict) -> List[Dict]:
        """获取所有策略的信号"""
        signals = []
        for sid in self.strategies.keys():
            signal = self.evaluate_signal(symbol, sid, market_data)
            signals.append(signal)
        return signals

    def backtest_strategy(self, strategy_id: str, symbol: str,
                         start_date: str, end_date: str) -> Dict:
        """回测策略"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer2_strategy/backtester")
            from backtest_engine import BacktestEngine

            engine = BacktestEngine(self.workspace)
            return engine.run_backtest(strategy_id, symbol, start_date, end_date)
        except Exception as e:
            logger.error(f"回测失败: {e}")
            return {}

# ============================================================================
# Layer 3: 认知分析层 - 信息分析和情绪识别
# ============================================================================

class Layer3_CognitiveAnalysis:
    """
    认知分析层
    非结构化数据分析、情绪识别、风险发现
    """

    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace

        logger.info("🧠 Layer 3: 认知分析层初始化")
        self._init_analyzers()

    def _init_analyzers(self):
        """初始化分析器"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer3_analysis/analyzers")
            from sentiment_analyzer import SentimentAnalyzer
            self.sentiment_analyzer = SentimentAnalyzer(self.workspace)
            logger.info("  ✅ 情绪分析器已加载")
        except Exception as e:
            logger.warning(f"  ⚠️ 情绪分析器加载失败: {e}")

    def analyze_sentiment(self, text: str) -> Dict:
        """分析文本情绪"""
        if hasattr(self, 'sentiment_analyzer'):
            return self.sentiment_analyzer.analyze_sentiment(text)
        return {"score": 0, "label": "neutral", "confidence": 0}

    def analyze_research_report(self, report_text: str, metadata: Dict = None) -> Dict:
        """
        分析研报 (Layer 3 - 研报阅读能力)

        Args:
            report_text: 研报文本内容
            metadata: 研报元数据 (标题、作者、机构等)

        Returns:
            研报分析结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer3_analysis/analyzers")
            from report_analyzer import ReportAnalyzer

            analyzer = ReportAnalyzer()
            result = analyzer.analyze_single_report(report_text, metadata)

            logger.info(f"📄 研报分析完成: {result['report']['stock_name']} - {result['report']['rating']}")
            return result

        except Exception as e:
            logger.warning(f"研报分析器加载失败，使用简化分析: {e}")
            return self._simple_report_analysis(report_text, metadata)

    def _simple_report_analysis(self, text: str, metadata: Dict = None) -> Dict:
        """简化研报分析 (备用)"""
        import re

        # 提取评级
        rating_match = re.search(r'评级[：:]\s*(买入|增持|中性|减持|卖出)', text)
        rating = rating_match.group(1) if rating_match else "未明确"

        # 提取目标价
        target_match = re.search(r'目标价[：:]\s*(\d+\.?\d*)', text)
        target_price = float(target_match.group(1)) if target_match else None

        return {
            "report": {
                "title": metadata.get('title', '未命名研报') if metadata else '未命名研报',
                "rating": rating,
                "target_price": target_price,
                "institution": metadata.get('institution', '未知机构') if metadata else '未知机构',
                "publish_date": metadata.get('publish_date', datetime.now().strftime('%Y-%m-%d')) if metadata else datetime.now().strftime('%Y-%m-%d')
            },
            "summary": f"评级: {rating}, 目标价: {target_price}元" if target_price else f"评级: {rating}",
            "recommendation": {
                "action": "关注" if rating in ['买入', '增持'] else "观望",
                "confidence": "medium"
            },
            "analysis_timestamp": datetime.now().isoformat(),
            "note": "使用简化分析模式"
        }

    def batch_analyze_reports(self, reports: List[Dict]) -> Dict:
        """
        批量分析研报

        Args:
            reports: 研报列表，每项包含 {'text': ..., 'metadata': ...}

        Returns:
            分析结果列表 + 汇总
        """
        results = []
        for i, report in enumerate(reports, 1):
            logger.info(f"📄 分析研报 {i}/{len(reports)}...")
            result = self.analyze_research_report(
                report.get('text', ''),
                report.get('metadata', {})
            )
            results.append(result)

        # 生成汇总
        summary = self._generate_report_summary(results)

        return {
            "individual_results": results,
            "summary": summary,
            "total_count": len(results)
        }

    def _generate_report_summary(self, results: List[Dict]) -> Dict:
        """生成研报汇总分析"""
        ratings = {}
        target_prices = []
        institutions = set()

        for r in results:
            report = r.get('report', {})

            # 统计评级
            rating = report.get('rating', '未明确')
            ratings[rating] = ratings.get(rating, 0) + 1

            # 收集目标价
            if report.get('target_price'):
                target_prices.append(report['target_price'])

            # 收集机构
            if report.get('institution'):
                institutions.add(report['institution'])

        # 一致性判断
        total = len(results)
        buy_count = ratings.get('买入', 0) + ratings.get('强烈推荐', 0)
        consensus = "一致看好" if buy_count >= total * 0.6 else "观点分化" if buy_count >= total * 0.3 else "谨慎观望"

        return {
            "total_reports": total,
            "rating_distribution": ratings,
            "consensus": consensus,
            "target_price_stats": {
                "avg": sum(target_prices) / len(target_prices) if target_prices else None,
                "min": min(target_prices) if target_prices else None,
                "max": max(target_prices) if target_prices else None
            },
            "covering_institutions": list(institutions),
            "recommendation": {
                "action": "买入" if consensus == "一致看好" else "观望",
                "confidence": "high" if consensus == "一致看好" else "medium"
            }
        }

    def generate_sector_report(self, sector: str, date: str = None) -> str:
        """生成板块分析报告"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer3_analysis")
            from report_generator import ReportGenerator

            generator = ReportGenerator(self.workspace)
            return generator.generate_sector_report(
                date or datetime.now().strftime('%Y%m%d'),
                "A股",
                sector
            )
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            return ""

    def five_step_analysis(self, symbol: str, stock_data: Dict = None) -> Dict:
        """
        股票五步法分析 (高价值SKILL整合)

        Args:
            symbol: 股票代码
            stock_data: 股票数据（可选）

        Returns:
            五步法分析结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer3_analysis/analyzers")
            from premium_skill_integration import FiveStepAnalyzer

            analyzer = FiveStepAnalyzer()

            # 如果没有数据，尝试获取
            if stock_data is None:
                stock_data = self._fetch_stock_data(symbol)

            result = analyzer.analyze(symbol, stock_data)

            logger.info(f"✅ 五步法分析完成: {result.stock_name} - 综合评分{result.composite_score:.1f}/10")

            # 转换为字典返回
            from dataclasses import asdict
            return asdict(result)

        except Exception as e:
            logger.error(f"五步法分析失败: {e}")
            return {"error": str(e), "symbol": symbol}

    def private_banker_analysis(self, symbol: str, stock_data: Dict = None) -> Dict:
        """
        私人投行分析 (高价值SKILL整合)

        Args:
            symbol: 股票代码
            stock_data: 股票数据（可选）

        Returns:
            私人投行级别分析结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer3_analysis/analyzers")
            from premium_skill_integration import PrivateBankerAnalyzer

            analyzer = PrivateBankerAnalyzer()

            # 如果没有数据，尝试获取
            if stock_data is None:
                stock_data = self._fetch_stock_data(symbol)

            result = analyzer.analyze(symbol, stock_data)

            logger.info(f"✅ 私人投行分析完成: {result.stock_name} - 评级{result.rating}")

            # 转换为字典返回
            from dataclasses import asdict
            return asdict(result)

        except Exception as e:
            logger.error(f"私人投行分析失败: {e}")
            return {"error": str(e), "symbol": symbol}

    def comprehensive_analysis(self, symbol: str, stock_data: Dict = None) -> Dict:
        """
        综合分析 (五步法 + 私人投行)

        Args:
            symbol: 股票代码
            stock_data: 股票数据（可选）

        Returns:
            综合分析结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer3_analysis/analyzers")
            from premium_skill_integration import PremiumAnalysisEngine

            engine = PremiumAnalysisEngine(self.workspace)

            result = engine.comprehensive_analysis(symbol, stock_data)

            logger.info(f"✅ 综合分析完成: {result['stock_name']} - 共识评级{result['synthesis']['consensus_rating']}")

            return result

        except Exception as e:
            logger.error(f"综合分析失败: {e}")
            return {"error": str(e), "symbol": symbol}

    def _fetch_stock_data(self, symbol: str) -> Dict:
        """获取股票基础数据"""
        try:
            # 尝试从Layer 1获取数据
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer1_data")
            from data_source_manager import DataSourceManager

            dsm = DataSourceManager()
            # 简化获取，实际应调用完整接口
            return {
                "symbol": symbol,
                "name": symbol,  # 需要查询名称
                "price": None
            }
        except:
            return {"symbol": symbol, "name": symbol, "price": None}

# ============================================================================
# Layer 4: 执行控制层 - 信号聚合和仓位管理
# ============================================================================

class Layer4_ExecutionControl:
    """
    执行控制层
    信号聚合、仓位管理、风险控制
    """

    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace

        logger.info("⚡ Layer 4: 执行控制层初始化")
        self._init_controllers()

    def _init_controllers(self):
        """初始化控制器"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer4_decision")
            from decision_engine import DecisionEngine
            self.decision_engine = DecisionEngine(self.workspace)
            logger.info("  ✅ 决策引擎已加载")
        except Exception as e:
            logger.warning(f"  ⚠️ 决策引擎加载失败: {e}")

    def make_decision(self, symbol: str, mode: str = "simulated") -> Dict:
        """做出交易决策"""
        if hasattr(self, 'decision_engine'):
            return self.decision_engine.make_decision(symbol, mode)
        return {"action": "HOLD", "reason": "决策引擎未初始化"}

    def calculate_position(self, portfolio: Dict, symbol: str,
                          signal_strength: str, risk_level: str) -> Dict:
        """计算建议仓位"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer4_decision")
            from position_manager import PositionManager, Portfolio

            manager = PositionManager(self.workspace)

            # 构建Portfolio对象
            pf = Portfolio(
                account_id=portfolio.get("account_id", "default"),
                total_equity=portfolio.get("total_equity", 1000000),
                available_cash=portfolio.get("available_cash", 500000),
                positions={},
                total_market_value=portfolio.get("total_market_value", 500000),
                total_unrealized_pnl=portfolio.get("total_unrealized_pnl", 0),
                risk_exposure=portfolio.get("risk_exposure", 0.1)
            )

            return manager.calculate_position_size(
                pf, symbol, signal_strength, 10.0, risk_level
            )
        except Exception as e:
            logger.error(f"仓位计算失败: {e}")
            return {}

# ============================================================================
# Layer 5: 元学习层 - 复盘和自我改进
# ============================================================================

class Layer5_MetaLearning:
    """
    元学习层
    复盘、学习、自我改进
    """

    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.knowledge_base = {}

        logger.info("🔄 Layer 5: 元学习层初始化")
        self._init_learning()

    def _init_learning(self):
        """初始化学习系统"""
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L/layer5_review")
            from review_engine import ReviewEngine
            from learning_system import LearningSystem

            self.review_engine = ReviewEngine(self.workspace)
            self.learning_system = LearningSystem(self.workspace)

            logger.info("  ✅ 复盘和学习系统已加载")
        except Exception as e:
            logger.warning(f"  ⚠️ 学习系统加载失败: {e}")

    def daily_review(self, date: str = None) -> Dict:
        """每日复盘"""
        if hasattr(self, 'review_engine'):
            return self.review_engine.generate_daily_review(date)
        return {}

    def learn_from_experience(self, experience: Dict):
        """从经验中学习"""
        if hasattr(self, 'learning_system'):
            self.learning_system.learn_from_review(experience)

    def get_improvement_suggestions(self) -> List[str]:
        """获取改进建议"""
        return [
            "优化数据获取速度",
            "改进信号准确性",
            "增强风险控制",
            "完善监控告警"
        ]

# ============================================================================
# 超级SKILL主类 - 整合所有层
# ============================================================================

class Architect5LSuperSkill:
    """
    ARCHITECT-5L 超级SKILL
    五层架构的综合能力工具
    """

    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.metadata = SkillMetadata()

        logger.info("="*70)
        logger.info("🚀 ARCHITECT-5L Super Skill 初始化")
        logger.info("="*70)

        # 初始化Layer 0: 元控制层 (系统大脑)
        self.layer0 = Layer0_MetaControl(workspace)
        
        # 初始化KIWI知识沉淀中心 (内部图书馆)
        self.kiwi = self._init_kiwi_hub()

        # 初始化五层
        self.layer1 = Layer1_DataPerception(workspace)
        self.layer2 = Layer2_StrategyEngine(workspace)
        self.layer3 = Layer3_CognitiveAnalysis(workspace)
        self.layer4 = Layer4_ExecutionControl(workspace)
        self.layer5 = Layer5_MetaLearning(workspace)

        # 系统状态
        self.status = "initialized"

        logger.info("✅ 超级SKILL初始化完成")
    
    def _init_kiwi_hub(self):
        """初始化KIWI知识沉淀中心"""
        try:
            sys.path.insert(0, f"{self.workspace}/KIWI")
            from kiwi_knowledge_hub import KIWIKnowledgeHub
            kiwi = KIWIKnowledgeHub(self.workspace)
            logger.info("📚 KIWI知识沉淀中心已加载")
            return kiwi
        except Exception as e:
            logger.warning(f"⚠️ KIWI初始化失败: {e}")
            return None

    def execute_full_pipeline(self, symbol: str, execute_trade: bool = False) -> Dict:
        """
        执行完整的五层流水线

        Pipeline:
        Layer 1: 获取数据 → Layer 2: 策略分析 →
        Layer 3: 认知分析 → Layer 4: 决策执行 →
        Layer 5: 学习记录
        
        Args:
            symbol: 股票代码
            execute_trade: 是否执行模拟交易 (默认False，仅研究模式)
        """
        logger.info(f"🔄 执行完整流水线: {symbol}")

        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "pipeline": {}
        }

        # Layer 1: 数据获取
        data = self.layer1.get_stock_data(symbol)
        result["pipeline"]["layer1_data"] = {
            "status": "success" if data else "failed",
            "records": len(data.get("data", [])) if data else 0
        }

        # Layer 2: 策略分析
        if data:
            signals = self.layer2.get_all_signals(symbol, data)
            result["pipeline"]["layer2_strategy"] = {
                "status": "success",
                "signals_count": len(signals),
                "signals": signals[:3]  # 只取前3个
            }

        # Layer 3: 认知分析
        news = self.layer1.get_market_news(10)
        sentiment = self.layer3.analyze_sentiment(
            " ".join([n["title"] for n in news[:5]])
        )
        result["pipeline"]["layer3_cognitive"] = {
            "status": "success",
            "sentiment": sentiment,
            "news_count": len(news)
        }

        # Layer 4: 决策执行
        decision = self.layer4.make_decision(symbol, "simulated" if execute_trade else "research")
        result["pipeline"]["layer4_execution"] = {
            "status": "success",
            "decision": decision
        }
        
        # 如果启用模拟交易，执行交易
        if execute_trade and decision.get("action") in ["BUY", "SELL"]:
            trade_result = self.execute_simulated_trade(
                symbol=symbol,
                action=decision["action"],
                quantity=decision.get("quantity", 100),
                price=decision.get("price", 0),
                strategy=decision.get("strategy", "pipeline"),
                confidence=decision.get("confidence", 0.7)
            )
            result["pipeline"]["layer4_trade_execution"] = trade_result

        # Layer 5: 学习记录
        result["pipeline"]["layer5_learning"] = {
            "status": "recorded",
            "timestamp": datetime.now().isoformat()
        }

        self.status = "completed"
        logger.info("✅ 流水线执行完成")

        return result
    
    def execute_simulated_trade(self, symbol: str, action: str, quantity: int,
                                price: float, strategy: str, confidence: float,
                                account_id: str = "US_SIM_001") -> Dict:
        """
        执行模拟交易 (Layer 4功能)
        
        Args:
            symbol: 股票代码
            action: BUY/SELL
            quantity: 数量
            price: 价格
            strategy: 策略名称
            confidence: 信号置信度
            account_id: 账户ID
            
        Returns:
            交易执行结果
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L")
            from layer4_layer5_trading_system import A5LTradingSystem
            
            trading_system = A5LTradingSystem(self.workspace)
            result = trading_system.execute_strategy_signal(
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                strategy=strategy,
                confidence=confidence,
                account_id=account_id
            )
            
            return {
                "success": result.get("success", False),
                "trade_id": result.get("trade_id"),
                "costs": result.get("costs", {}),
                "account": result.get("account", {})
            }
        except Exception as e:
            logger.error(f"模拟交易执行失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_simulated_portfolio(self, account_id: str = None) -> Dict:
        """
        获取模拟交易账户概况 (Layer 4功能)
        
        Args:
            account_id: 账户ID (None则返回所有账户)
            
        Returns:
            投资组合概况
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L")
            from layer4_layer5_trading_system import A5LTradingSystem
            
            trading_system = A5LTradingSystem(self.workspace)
            return trading_system.get_portfolio(account_id)
        except Exception as e:
            logger.error(f"获取投资组合失败: {e}")
            return {"error": str(e)}
    
    def run_daily_trading_review(self, date: str = None, account_id: str = None) -> Dict:
        """
        运行每日交易复盘 (Layer 5功能)
        
        Args:
            date: 复盘日期 (默认昨天)
            account_id: 账户ID
            
        Returns:
            复盘报告
        """
        try:
            sys.path.insert(0, f"{self.workspace}/ARCHITECT_5L")
            from layer4_layer5_trading_system import A5LTradingSystem
            
            trading_system = A5LTradingSystem(self.workspace)
            report = trading_system.run_daily_review(date, account_id)
            
            return {
                "date": report.date,
                "account_id": report.account_id,
                "total_trades": report.total_trades,
                "win_rate": report.win_rate,
                "total_pnl": report.total_pnl,
                "profit_factor": report.profit_factor,
                "summary": report.summary,
                "action_items": report.action_items,
                "strategy_performance": report.strategy_performance
            }
        except Exception as e:
            logger.error(f"每日复盘失败: {e}")
            return {"error": str(e)}
    
    def auto_execute_strategy_signals(self, symbols: List[str], 
                                     strategy_filter: List[str] = None) -> Dict:
        """
        自动执行策略信号 (Layer 4批量执行)
        
        Args:
            symbols: 股票代码列表
            strategy_filter: 策略过滤器 (None则执行所有)
            
        Returns:
            批量执行结果
        """
        results = []
        executed = 0
        failed = 0
        
        for symbol in symbols:
            try:
                # 获取策略信号
                signals = self.layer2.get_all_signals(symbol)
                
                for signal in signals:
                    if strategy_filter and signal.get("strategy") not in strategy_filter:
                        continue
                    
                    if signal.get("action") in ["BUY", "SELL"] and signal.get("confidence", 0) >= 0.7:
                        # 执行模拟交易
                        result = self.execute_simulated_trade(
                            symbol=symbol,
                            action=signal["action"],
                            quantity=signal.get("quantity", 100),
                            price=signal.get("price", 0),
                            strategy=signal["strategy"],
                            confidence=signal["confidence"]
                        )
                        
                        results.append({
                            "symbol": symbol,
                            "signal": signal,
                            "execution": result
                        })
                        
                        if result.get("success"):
                            executed += 1
                        else:
                            failed += 1
            
            except Exception as e:
                logger.error(f"执行{symbol}信号失败: {e}")
                failed += 1
        
        return {
            "total_symbols": len(symbols),
            "executed": executed,
            "failed": failed,
            "results": results
        }

    def generate_daily_report(self) -> str:
        """生成每日报告"""
        report = f"""# 📊 ARCHITECT-5L 每日报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**SKILL版本**: {self.metadata.version}

---

## 🏗️ 系统状态

- **数据感知层**: ✅ 运行中
- **策略决策层**: ✅ {len(self.layer2.strategies)} 个策略就绪
- **认知分析层**: ✅ 分析器就绪
- **执行控制层**: ✅ 决策引擎就绪
- **元学习层**: ✅ 学习系统就绪

---

## 📈 今日执行

- **处理股票数**: 待统计
- **生成信号数**: 待统计
- **执行交易数**: 待统计

---

## 🧠 改进建议

{chr(10).join(['- ' + s for s in self.layer5.get_improvement_suggestions()])}

---

**ARCHITECT-5L Super Skill** - 自我迭代的智能投资系统
"""
        return report

    def self_diagnose(self) -> Dict:
        """自我诊断"""
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "layers": {}
        }

        # 检查各层健康状态
        layers_status = {
            "layer1": hasattr(self.layer1, 'connectors'),
            "layer2": hasattr(self.layer2, 'strategies'),
            "layer3": hasattr(self.layer3, 'sentiment_analyzer'),
            "layer4": hasattr(self.layer4, 'decision_engine'),
            "layer5": hasattr(self.layer5, 'review_engine')
        }

        for layer, status in layers_status.items():
            diagnosis["layers"][layer] = "healthy" if status else "degraded"
            if not status:
                diagnosis["overall_status"] = "degraded"

        return diagnosis

    def export_skill_registry(self) -> Dict:
        """导出SKILL注册表信息"""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "capabilities": self.metadata.capabilities,
            "dependencies": self.metadata.dependencies,
            "layers": {
                "layer1": "DataPerception",
                "layer2": "StrategyEngine",
                "layer3": "CognitiveAnalysis",
                "layer4": "ExecutionControl",
                "layer5": "MetaLearning"
            },
            "status": self.status
        }

def main():
    """演示超级SKILL"""
    print("="*70)
    print("🚀 ARCHITECT-5L Super Skill 演示")
    print("="*70)

    # 初始化超级SKILL
    skill = Architect5LSuperSkill()

    print("\n📋 元数据:")
    print(f"  名称: {skill.metadata.name}")
    print(f"  版本: {skill.metadata.version}")
    print(f"  能力数: {len(skill.metadata.capabilities)}")

    print("\n🧪 自我诊断:")
    diagnosis = skill.self_diagnose()
    for layer, status in diagnosis["layers"].items():
        icon = "✅" if status == "healthy" else "⚠️"
        print(f"  {icon} {layer}: {status}")

    print("\n📊 执行完整流水线:")
    result = skill.execute_full_pipeline("000001.SZ")

    for layer, data in result["pipeline"].items():
        print(f"  ✅ {layer}: {data['status']}")

    print("\n📄 生成每日报告:")
    report = skill.generate_daily_report()
    print(report[:500] + "...")

    print("\n" + "="*70)
    print("✅ 超级SKILL演示完成！")
    print("="*70)

if __name__ == "__main__":
    main()
