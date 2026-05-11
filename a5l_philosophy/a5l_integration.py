"""
A5L-毛选投资哲学体系 - 主集成模块
将毛选哲学与工程控制论整合到A5L主系统
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# 导入毛选哲学模块
from .maoxuan import (
    InvestmentLawRecognizer,
    GlobalLocalAllocator,
    DecisiveBattleSelector,
    StrategicPhaseManager,
    ConcentratedPositionAllocator,
    ProtractedWarPhaseIdentifier,
    ContradictionAnalyzer,
    GuerrillaTacticsPositionManager,
    ThreePrinciplesTrader,
    UnitedFrontPortfolioManager,
    LearningOrganizationSystem,
    CognitiveIterationSystem,
    SparkToPrairieFireSystem,
    AntiDogmatismChecker,
    PortfolioStageEvolution,
    InvestmentPolicyFlexibility,
    TenDimensionsBalanceChecker,
    InvestmentResearchExpression,
    PortfolioConflictResolver,
    TradingCognitionFormation,
    DemocraticCentralismDecision,
    PartyCommitteeMethods,
    SixManagersHub,
)

# 导入工程控制论
from .engineering_control import (
    EngineeringControlSystem,
    SystemState,
    ControlSignal
)


@dataclass
class A5LInvestmentDecision:
    """A5L投资决策"""
    timestamp: str
    decision_type: str  # 'buy', 'sell', 'hold', 'rebalance'
    target_stock: Optional[str]
    target_position: float
    confidence: float
    philosophy_basis: List[str]  # 决策依据的哲学/理论
    risk_assessment: dict
    execution_plan: dict


class A5LMaoXuanIntegration:
    """
    A5L-毛选投资哲学集成器
    
    整合流程：
    1. 毛选哲学层：战略分析、战术执行、组织管理
    2. 工程控制论层：反馈、前馈、最优、自适应、鲁棒控制
    3. 六管理者层：民主集中决策
    4. 最终决策：综合输出
    """
    
    def __init__(self, total_capital: float = 1000000):
        self.total_capital = total_capital
        
        # 初始化毛选哲学模块
        self._init_maoxuan_modules()
        
        # 初始化工程控制论
        self.control_system = EngineeringControlSystem()
        
        # 六管理者Hub
        self.six_managers = SixManagersHub()
        
        # 决策历史
        self.decision_history = []
    
    def _init_maoxuan_modules(self):
        """初始化毛选哲学模块"""
        self.strategic_recognizer = InvestmentLawRecognizer()
        self.global_allocator = GlobalLocalAllocator(self.total_capital, 0.15)
        self.battle_selector = DecisiveBattleSelector()
        self.phase_manager = StrategicPhaseManager()
        self.position_allocator = ConcentratedPositionAllocator(self.total_capital)
        self.protracted_war = ProtractedWarPhaseIdentifier()
        self.contradiction_analyzer = ContradictionAnalyzer()
        self.guerrilla_tactics = GuerrillaTacticsPositionManager()
        self.three_principles = ThreePrinciplesTrader()
        self.united_front = UnitedFrontPortfolioManager(self.total_capital)
        self.learning_org = LearningOrganizationSystem()
        self.cognitive_iteration = CognitiveIterationSystem()
        self.spark_system = SparkToPrairieFireSystem()
        self.anti_dogmatism = AntiDogmatismChecker()
        self.portfolio_stage = PortfolioStageEvolution()
        self.policy_flexibility = InvestmentPolicyFlexibility()
        self.ten_dimensions = TenDimensionsBalanceChecker()
        self.research_expression = InvestmentResearchExpression()
        self.conflict_resolver = PortfolioConflictResolver()
        self.cognition_formation = TradingCognitionFormation()
        self.democratic_centralism = DemocraticCentralismDecision()
        self.committee_methods = PartyCommitteeMethods()
    
    def analyze_and_decide(self,
                          market_data: dict,
                          portfolio: dict,
                          stock_candidates: list) -> A5LInvestmentDecision:
        """
        综合分析并生成投资决策
        
        五层决策流程：
        L1: 战略层 - 全局判断
        L2: 战术层 - 具体执行
        L3: 控制层 - 工程控制论
        L4: 组织层 - 六管理者决策
        L5: 输出层 - 最终决策
        """
        
        # ========== L1: 战略层分析 ==========
        strategic_analysis = self._strategic_layer_analysis(market_data, portfolio)
        
        # ========== L2: 战术层分析 ==========
        tactical_analysis = self._tactical_layer_analysis(stock_candidates, market_data)
        
        # ========== L3: 控制层分析 ==========
        system_state = SystemState(
            portfolio_value=portfolio.get('total_value', self.total_capital),
            cash_ratio=portfolio.get('cash_ratio', 0.3),
            risk_exposure=portfolio.get('risk_exposure', 0.15),
            current_positions=portfolio.get('positions', {}),
            market_regime=strategic_analysis.get('market_regime', 'neutral')
        )
        
        performance = {
            'ytd_return': portfolio.get('ytd_return', 0),
            'portfolio_volatility': portfolio.get('volatility', 0.15),
            'sharpe_ratio': portfolio.get('sharpe', 1.0)
        }
        
        control_decision = self.control_system.generate_control_decision(
            system_state, market_data, performance
        )
        
        # ========== L4: 六管理者决策 ==========
        top_candidate = tactical_analysis.get('top_candidate')
        proposal = {
            'stock': top_candidate.get('stock', {}) if top_candidate else {},
            'position': control_decision['final_decision']['target_position'],
            'strategic_analysis': strategic_analysis,
            'tactical_analysis': tactical_analysis
        }
        
        six_managers_decision = self.six_managers.evaluate_proposal(proposal, {
            'market_data': market_data,
            'portfolio': portfolio
        })
        
        # ========== L5: 综合决策输出 ==========
        final_decision = self._synthesize_final_decision(
            strategic_analysis,
            tactical_analysis,
            control_decision,
            six_managers_decision
        )
        
        self.decision_history.append(final_decision)
        
        return final_decision
    
    def _strategic_layer_analysis(self, market_data: dict, portfolio: dict) -> dict:
        """战略层分析"""
        # 1. 投资规律识别
        law_recognition = self.strategic_recognizer.recognize_investment_law(market_data)
        
        # 2. 战略阶段评估
        phase = self.phase_manager.evaluate_strategic_phase(market_data, portfolio)
        
        # 3. 矛盾分析
        contradictions = self.contradiction_analyzer.analyze_contradictions(
            market_data.get('index_data', {}),
            market_data
        )
        
        # 4. 全局配置
        global_alloc = self.global_allocator.determine_global_allocation({
            'cycle': phase['current_phase'],
            'risk_appetite': 'risk_on' if phase['target_position'] > 0.6 else 'risk_off'
        })
        
        return {
            'investment_law': law_recognition,
            'strategic_phase': phase,
            'contradictions': contradictions,
            'global_allocation': global_alloc,
            'market_regime': self._determine_market_regime(law_recognition, phase)
        }
    
    def _tactical_layer_analysis(self, stock_candidates: list, market_data: dict) -> dict:
        """战术层分析"""
        # 1. 关键战役选择
        battles = self.battle_selector.identify_decisive_battles(stock_candidates, market_data)
        
        # 2. 集中兵力分配
        if battles:
            allocation = self.position_allocator.allocate_concentrated_positions(battles)
        else:
            allocation = {'core_positions': [], 'satellite_positions': []}
        
        # 3. 统一战线分类
        force_classification = []
        for stock in stock_candidates[:5]:
            force_type = self.united_front.classify_force(stock, market_data)
            force_classification.append({'stock': stock, 'force_type': force_type})
        
        return {
            'decisive_battles': battles,
            'position_allocation': allocation,
            'force_classification': force_classification,
            'top_candidate': battles[0] if battles else None
        }
    
    def _determine_market_regime(self, law: dict, phase: dict) -> str:
        """确定市场状态"""
        law_name = law.get('investment_law', {}).get('law_name', '')
        phase_name = phase.get('current_phase', '')
        
        if '趋势' in law_name and phase_name == 'offense':
            return 'strong_trend'
        elif phase_name == 'defense':
            return 'weak_market'
        return 'neutral'
    
    def _synthesize_final_decision(self,
                                   strategic: dict,
                                   tactical: dict,
                                   control: dict,
                                   six_managers: dict) -> A5LInvestmentDecision:
        """综合最终决策"""
        
        # 决策类型
        if six_managers['decision'] == 'veto':
            decision_type = 'hold'
        elif tactical.get('top_candidate'):
            decision_type = 'buy'
        else:
            decision_type = 'hold'
        
        # 目标仓位
        target_position = control['final_decision']['target_position']
        
        # 哲学依据
        philosophy_basis = [
            f"战略规律: {strategic['investment_law']['investment_law']['law_name']}",
            f"战略阶段: {strategic['strategic_phase']['current_phase']}",
            f"控制论: 反馈+前馈+最优控制",
            f"六管理者: {six_managers['decision']}"
        ]
        
        # 风险评估
        risk_assessment = {
            'concentration_risk': tactical.get('position_allocation', {}).get('concentration_coefficient', 0),
            'market_risk': 1 - strategic['investment_law']['confidence'],
            'decision_uncertainty': 1 - six_managers['final_score']
        }
        
        return A5LInvestmentDecision(
            timestamp=datetime.now().isoformat(),
            decision_type=decision_type,
            target_stock=tactical.get('top_candidate', {}).get('stock', {}).get('code') if tactical.get('top_candidate') else None,
            target_position=target_position,
            confidence=control['final_decision']['confidence'],
            philosophy_basis=philosophy_basis,
            risk_assessment=risk_assessment,
            execution_plan={
                'strategic_allocation': strategic['global_allocation'],
                'tactical_positions': tactical.get('position_allocation', {}),
                'control_signal': control['final_decision']
            }
        )
    
    def get_decision_summary(self) -> dict:
        """获取决策汇总"""
        if not self.decision_history:
            return {'message': '暂无决策记录'}
        
        recent = self.decision_history[-10:]
        
        return {
            'total_decisions': len(self.decision_history),
            'recent_decisions': [
                {
                    'timestamp': d.timestamp,
                    'type': d.decision_type,
                    'stock': d.target_stock,
                    'confidence': d.confidence
                }
                for d in recent
            ],
            'philosophy_coverage': '毛选19篇 + 工程控制论5类控制',
            'integration_status': 'fully_operational'
        }
