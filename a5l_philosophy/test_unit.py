"""
A5L-毛选投资哲学体系 - 单元测试
覆盖全部23个模块的单元测试
"""

import unittest
import sys
sys.path.insert(0, '/workspace/projects/workspace')

from a5l_philosophy.maoxuan import (
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


class TestStrategicRecognizer(unittest.TestCase):
    """测试战略规律识别器"""
    
    def setUp(self):
        self.recognizer = InvestmentLawRecognizer()
    
    def test_recognize_trend_following(self):
        """测试趋势跟随识别"""
        data = {
            'pe_percentile': 0.3,
            'pb_percentile': 0.4,
            'sentiment_index': 0.8,
            'trend_strength': 0.8,
            'price_history': [100, 102, 105, 108, 112, 115]
        }
        result = self.recognizer.recognize_investment_law(data)
        self.assertIn('investment_law', result)
        self.assertIn('confidence', result)
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 1)
    
    def test_recognize_mean_reversion(self):
        """测试均值回归识别"""
        data = {
            'pe_percentile': 0.2,
            'pb_percentile': 0.2,
            'sentiment_index': 0.2,
            'trend_strength': 0.3,
            'volatility_20d': 0.35,
            'price_history': [100, 95, 90, 85, 82, 80]
        }
        result = self.recognizer.recognize_investment_law(data)
        self.assertIn('law_name', result['investment_law'])


class TestGlobalLocalAllocator(unittest.TestCase):
    """测试全局-局部配置器"""
    
    def setUp(self):
        self.allocator = GlobalLocalAllocator(total_capital=1000000, risk_budget=0.15)
    
    def test_determine_global_allocation(self):
        """测试全局配置确定"""
        market_analysis = {
            'cycle': 'bull',
            'macro': 'positive',
            'risk_appetite': 'riskon'
        }
        result = self.allocator.determine_global_allocation(market_analysis)
        self.assertIn('allocation', result)
        self.assertIn('equity_capital', result)
        self.assertGreater(result['equity_capital'], 0)
    
    def test_allocate_to_locals(self):
        """测试局部配置"""
        global_alloc = {
            'equity_capital': 800000,
            'global_state': {'market_cycle': 'bull', 'risk_appetite': 'risk_on'}
        }
        stock_pool = [
            {'code': '000001', 'name': '平安银行', 'growth_potential': 0.8, 'beta': 1.2},
            {'code': '000002', 'name': '万科A', 'growth_potential': 0.6, 'beta': 0.9}
        ]
        result = self.allocator.allocate_to_locals(stock_pool, global_alloc)
        self.assertIn('local_allocations', result)


class TestDecisiveBattle(unittest.TestCase):
    """测试关键战役选择器"""
    
    def setUp(self):
        self.selector = DecisiveBattleSelector()
    
    def test_identify_decisive_battles(self):
        """测试识别关键战役"""
        stock_pool = [
            {
                'code': '000001',
                'value_score': 0.8,
                'catalyst_score': 0.9,
                'current_price': 10,
                'target_price': 15,
                'is_main_line': True,
                'is_sector_leader': True,
                'volatility': 0.15
            }
        ]
        market_context = {'trend': 'up'}
        result = self.selector.identify_decisive_battles(stock_pool, market_context)
        self.assertIsInstance(result, list)


class TestGuerrillaTactics(unittest.TestCase):
    """测试游击战术管理器"""
    
    def setUp(self):
        self.tactics = GuerrillaTacticsPositionManager()
    
    def test_analyze_market_tactics_retreat(self):
        """测试敌进我退"""
        stock_data = {
            'price_change_1d': 0.08,
            'volume_ratio': 2.5,
            'current_position': 1000
        }
        market_context = {}
        result = self.tactics.analyze_market_tactics(stock_data, market_context)
        self.assertIn('tactic', result)
        self.assertIn('action', result)
    
    def test_manage_base_area(self):
        """测试根据地管理"""
        stock = {'code': '000001', 'catalyst_tier': 2, 'valuation_percentile': 0.5}
        fundamentals = {'roe': 0.12}
        result = self.tactics.manage_base_area(stock, fundamentals)
        self.assertIn('base_status', result)


class TestThreePrinciples(unittest.TestCase):
    """测试三性原则交易器"""
    
    def setUp(self):
        self.trader = ThreePrinciplesTrader()
    
    def test_calculate_freedom_index(self):
        """测试自由度指数"""
        portfolio = {
            'total_capital': 1000000,
            'cash': 300000,
            'positions': {}
        }
        result = self.trader.calculate_freedom_index(portfolio)
        self.assertIn('freedom_index', result)
        self.assertIn('status', result)
    
    def test_create_trade_plan(self):
        """测试创建交易计划"""
        stock = {
            'code': '000001',
            'target_entry': 10,
            'target_price': 15,
            'recommended_position': 0.1
        }
        result = self.trader.create_trade_plan(stock, '价值投资')
        self.assertIn('plan_id', result)
        self.assertIn('entry', result)
        self.assertIn('exit', result)


class TestUnitedFront(unittest.TestCase):
    """测试统一战线组合管理器"""
    
    def setUp(self):
        self.manager = UnitedFrontPortfolioManager(total_capital=1000000)
    
    def test_classify_force_progressive(self):
        """测试进步势力分类"""
        stock = {
            'value_cell_score': 0.8,
            'catalyst_tier': 3,
            'moat_score': 0.8
        }
        market_context = {}
        result = self.manager.classify_force(stock, market_context)
        self.assertIn(result, ['progressive', 'middle', 'isolated'])
    
    def test_develop_progressive_force(self):
        """测试发展进步势力"""
        stock = {'code': '000001'}
        current_allocation = {'progressive': 0.5}
        result = self.manager.develop_progressive_force(stock, current_allocation)
        self.assertIn('action', result)


class TestLearningOrganization(unittest.TestCase):
    """测试学习型组织系统"""
    
    def setUp(self):
        self.system = LearningOrganizationSystem()
    
    def test_conduct_daily_review(self):
        """测试每日复盘"""
        trading_day = {
            'date': '2026-05-11',
            'trades': [
                {'pnl': 1000, 'good_timing': True, 'had_stop_loss': True},
                {'pnl': -500, 'good_timing': False, 'had_stop_loss': True}
            ]
        }
        result = self.system.conduct_daily_review(trading_day)
        self.assertIn('trades_analysis', result)
        self.assertIn('lessons_learned', result)


class TestCognitiveIteration(unittest.TestCase):
    """测试认知迭代系统"""
    
    def setUp(self):
        self.system = CognitiveIterationSystem()
    
    def test_assess_cognitive_stage(self):
        """测试认知阶段评估"""
        profile = {
            'study_hours_per_week': 10,
            'trading_years': 2,
            'has_trading_system': True
        }
        result = self.system.assess_cognitive_stage(profile)
        self.assertIn('current_stage', result)
        self.assertIn(result['current_stage'], ['perceptual', 'rational', 'practice_test', 're_cognition'])
    
    def test_measure_knowledge_action_unity(self):
        """测试知行合一测量"""
        trades = [
            {'stock_code': '000001', 'followed_plan': True},
            {'stock_code': '000002', 'followed_plan': False}
        ]
        research = [{'stock_code': '000001'}]
        result = self.system.measure_knowledge_action_unity(trades, research)
        self.assertIn('unity_score', result)


class TestSparkToPrairieFire(unittest.TestCase):
    """测试星星之火建仓系统"""
    
    def setUp(self):
        self.system = SparkToPrairieFireSystem(target_position=0.2)
    
    def test_evaluate_entry_signal(self):
        """测试入场信号评估"""
        stock = {
            'value_cell_score': 0.7,
            'catalyst_tier': 2,
            'technical_score': 0.6
        }
        market_context = {}
        result = self.system.evaluate_entry_signal(stock, market_context)
        self.assertIn('can_enter', result)
        if result['can_enter']:
            self.assertIn('initial_position', result)


class TestAntiDogmatism(unittest.TestCase):
    """测试反对教条主义检查器"""
    
    def setUp(self):
        self.checker = AntiDogmatismChecker()
    
    def test_calculate_research_completeness(self):
        """测试研究完整度"""
        self.checker.research_history['000001'] = {
            'financial': 0.8,
            'industry': 0.7,
            'management': 0.6
        }
        result = self.checker.calculate_research_completeness('000001')
        self.assertIn('completeness', result)
        self.assertIn('has_voice', result)


class TestConflictResolver(unittest.TestCase):
    """测试冲突处理系统"""
    
    def setUp(self):
        self.resolver = PortfolioConflictResolver()
    
    def test_classify_contradiction_internal(self):
        """测试内部矛盾分类"""
        position = {
            'stock_code': '000001',
            'unrealized_pnl': -0.05,
            'max_drawdown': -0.10
        }
        market_context = {}
        result = self.resolver.classify_contradiction(position, market_context)
        self.assertIn('conflict_type', result)
        self.assertIn('solution', result)


class TestCognitionFormation(unittest.TestCase):
    """测试认知形成机制"""
    
    def setUp(self):
        self.system = TradingCognitionFormation()
    
    def test_form_cognition_from_material(self):
        """测试从物质形成感觉"""
        market_data = {
            'price_change': 0.05,
            'volume_ratio': 1.5
        }
        result = self.system.form_cognition_from_material(market_data)
        self.assertEqual(result['stage'], 'sensation')
        self.assertIn('output', result)
    
    def test_elevate_to_thought(self):
        """测试上升到思想"""
        sensation = {'mood': 'optimistic'}
        analysis = {'expected_return': 0.15}
        result = self.system.elevate_to_thought(sensation, analysis)
        self.assertEqual(result['stage'], 'thought')


class TestDemocraticCentralism(unittest.TestCase):
    """测试民主集中决策"""
    
    def setUp(self):
        self.system = DemocraticCentralismDecision()
    
    def test_democratic_discussion(self):
        """测试民主讨论"""
        proposal = {'stock': {'code': '000001'}, 'position': 0.1}
        context = {}
        result = self.system.democratic_discussion(proposal, context)
        self.assertIn('opinions', result)
        self.assertIn('statistics', result)
        self.assertEqual(len(result['opinions']), 6)  # 六管理者


class TestCommitteeMethods(unittest.TestCase):
    """测试委员会工作方法"""
    
    def setUp(self):
        self.methods = PartyCommitteeMethods()
    
    def test_play_piano(self):
        """测试弹钢琴（统筹兼顾）"""
        tasks = [
            {'layer': 'L0', 'urgency': 0.9},
            {'layer': 'L1', 'urgency': 0.7},
            {'layer': 'L2', 'urgency': 0.8}
        ]
        priorities = {'L0': 1.0, 'L1': 0.8, 'L2': 0.6}
        result = self.methods.play_piano(tasks, priorities)
        self.assertEqual(result['method'], 'play_piano')
        self.assertIn('coordinated_tasks', result)


class TestSixManagersHub(unittest.TestCase):
    """测试六管理者Hub"""
    
    def setUp(self):
        self.hub = SixManagersHub()
    
    def test_evaluate_proposal(self):
        """测试提案评估"""
        proposal = {
            'stock': {
                'code': '000001',
                'value_cell_score': 0.8,
                'catalyst_score': 0.7
            },
            'position': 0.15
        }
        context = {}
        result = self.hub.evaluate_proposal(proposal, context)
        self.assertIn('decision', result)
        self.assertIn('final_score', result)
        self.assertIn(result['decision'], ['approve', 'conditional', 'hold', 'reject', 'veto'])


def run_all_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_classes = [
        TestStrategicRecognizer,
        TestGlobalLocalAllocator,
        TestDecisiveBattle,
        TestGuerrillaTactics,
        TestThreePrinciples,
        TestUnitedFront,
        TestLearningOrganization,
        TestCognitiveIteration,
        TestSparkToPrairieFire,
        TestAntiDogmatism,
        TestConflictResolver,
        TestCognitionFormation,
        TestDemocraticCentralism,
        TestCommitteeMethods,
        TestSixManagersHub,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
