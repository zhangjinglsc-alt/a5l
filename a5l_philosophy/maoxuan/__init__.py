"""
A5L-毛选投资哲学体系 - 核心模块
对应Phase 1-3所有理论映射的可运行实现

作者: A5L System
创建时间: 2026-05-11
版本: v3.0
"""

__version__ = '3.0.0'
__author__ = 'A5L System'

# Phase 1: 战略思想层
from .strategic_recognizer import InvestmentLawRecognizer
from .global_local_allocator import GlobalLocalAllocator
from .decisive_battle import DecisiveBattleSelector
from .strategic_phase import StrategicPhaseManager
from .concentrated_position import ConcentratedPositionAllocator
from .protracted_war import ProtractedWarPhaseIdentifier
from .contradiction_analyzer import ContradictionAnalyzer

# Phase 2: 战术执行层
from .guerrilla_tactics import GuerrillaTacticsPositionManager
from .three_principles import ThreePrinciplesTrader
from .united_front import UnitedFrontPortfolioManager
from .learning_organization import LearningOrganizationSystem

# Phase 3 Part A: 广度扩展
from .cognitive_iteration import CognitiveIterationSystem
from .spark_to_prairie_fire import SparkToPrairieFireSystem
from .anti_dogmatism import AntiDogmatismChecker
from .portfolio_stage import PortfolioStageEvolution
from .policy_flexibility import InvestmentPolicyFlexibility
from .ten_dimensions import TenDimensionsBalanceChecker

# Phase 3 Part B: 深度挖掘
from .research_expression import InvestmentResearchExpression
from .conflict_resolver import PortfolioConflictResolver
from .cognition_formation import TradingCognitionFormation
from .democratic_centralism import DemocraticCentralismDecision
from .committee_methods import PartyCommitteeMethods

# 六管理者Hub
from .six_managers import SixManagersHub

# 工程控制论
from ..engineering_control import (
    EngineeringControlSystem,
    FeedbackController,
    FeedforwardController,
    OptimalController,
    AdaptiveController,
    RobustController,
    SystemState,
    ControlSignal
)

# A5L集成
from ..a5l_integration import (
    A5LMaoXuanIntegration,
    A5LInvestmentDecision
)

__all__ = [
    # Phase 1
    'InvestmentLawRecognizer',
    'GlobalLocalAllocator',
    'DecisiveBattleSelector',
    'StrategicPhaseManager',
    'ConcentratedPositionAllocator',
    'ProtractedWarPhaseIdentifier',
    'ContradictionAnalyzer',
    # Phase 2
    'GuerrillaTacticsPositionManager',
    'ThreePrinciplesTrader',
    'UnitedFrontPortfolioManager',
    'LearningOrganizationSystem',
    # Phase 3 Part A
    'CognitiveIterationSystem',
    'SparkToPrairieFireSystem',
    'AntiDogmatismChecker',
    'PortfolioStageEvolution',
    'InvestmentPolicyFlexibility',
    'TenDimensionsBalanceChecker',
    # Phase 3 Part B
    'InvestmentResearchExpression',
    'PortfolioConflictResolver',
    'TradingCognitionFormation',
    'DemocraticCentralismDecision',
    'PartyCommitteeMethods',
    # Hub
    'SixManagersHub',
    # 工程控制论
    'EngineeringControlSystem',
    'FeedbackController',
    'FeedforwardController',
    'OptimalController',
    'AdaptiveController',
    'RobustController',
    'SystemState',
    'ControlSignal',
    # A5L集成
    'A5LMaoXuanIntegration',
    'A5LInvestmentDecision',
]
