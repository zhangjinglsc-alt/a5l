"""
A5L-毛选投资哲学体系测试脚本
验证所有模块可以正常导入和运行
"""

import sys
sys.path.insert(0, '/workspace/projects/workspace')

def test_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("A5L-毛选投资哲学体系 - 模块导入测试")
    print("=" * 60)
    
    modules = [
        # Phase 1
        ('战略规律识别器', 'a5l_philosophy.maoxuan.strategic_recognizer', 'InvestmentLawRecognizer'),
        ('全局-局部配置器', 'a5l_philosophy.maoxuan.global_local_allocator', 'GlobalLocalAllocator'),
        ('关键战役选择器', 'a5l_philosophy.maoxuan.decisive_battle', 'DecisiveBattleSelector'),
        ('战略阶段管理器', 'a5l_philosophy.maoxuan.strategic_phase', 'StrategicPhaseManager'),
        ('集中兵力分配器', 'a5l_philosophy.maoxuan.concentrated_position', 'ConcentratedPositionAllocator'),
        ('持久战阶段识别', 'a5l_philosophy.maoxuan.protracted_war', 'ProtractedWarPhaseIdentifier'),
        ('矛盾分析器', 'a5l_philosophy.maoxuan.contradiction_analyzer', 'ContradictionAnalyzer'),
        # Phase 2
        ('游击战术管理', 'a5l_philosophy.maoxuan.guerrilla_tactics', 'GuerrillaTacticsPositionManager'),
        ('三性原则交易', 'a5l_philosophy.maoxuan.three_principles', 'ThreePrinciplesTrader'),
        ('统一战线组合', 'a5l_philosophy.maoxuan.united_front', 'UnitedFrontPortfolioManager'),
        ('学习型组织', 'a5l_philosophy.maoxuan.learning_organization', 'LearningOrganizationSystem'),
        # Phase 3 Part A
        ('认知迭代系统', 'a5l_philosophy.maoxuan.cognitive_iteration', 'CognitiveIterationSystem'),
        ('星星之火建仓', 'a5l_philosophy.maoxuan.spark_to_prairie_fire', 'SparkToPrairieFireSystem'),
        ('反对教条主义', 'a5l_philosophy.maoxuan.anti_dogmatism', 'AntiDogmatismChecker'),
        ('投资组合阶段', 'a5l_philosophy.maoxuan.portfolio_stage', 'PortfolioStageEvolution'),
        ('政策灵活性', 'a5l_philosophy.maoxuan.policy_flexibility', 'InvestmentPolicyFlexibility'),
        ('十维度平衡', 'a5l_philosophy.maoxuan.ten_dimensions', 'TenDimensionsBalanceChecker'),
        # Phase 3 Part B
        ('研究表达系统', 'a5l_philosophy.maoxuan.research_expression', 'InvestmentResearchExpression'),
        ('冲突处理系统', 'a5l_philosophy.maoxuan.conflict_resolver', 'PortfolioConflictResolver'),
        ('认知形成机制', 'a5l_philosophy.maoxuan.cognition_formation', 'TradingCognitionFormation'),
        ('民主集中决策', 'a5l_philosophy.maoxuan.democratic_centralism', 'DemocraticCentralismDecision'),
        ('委员会工作法', 'a5l_philosophy.maoxuan.committee_methods', 'PartyCommitteeMethods'),
        # Hub
        ('六管理者Hub', 'a5l_philosophy.maoxuan.six_managers', 'SixManagersHub'),
    ]
    
    passed = 0
    failed = 0
    
    for name, module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {name}: {class_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"测试结果: {passed}/{len(modules)} 通过, {failed}/{len(modules)} 失败")
    print("=" * 60)
    
    return failed == 0

def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "=" * 60)
    print("基本功能测试")
    print("=" * 60)
    
    from a5l_philosophy.maoxuan import InvestmentLawRecognizer
    
    # 测试投资规律识别器
    recognizer = InvestmentLawRecognizer()
    mock_data = {
        'pe_percentile': 0.3,
        'pb_percentile': 0.4,
        'sentiment_index': 0.6,
        'trend_strength': 0.8,
        'price_history': [100, 102, 105, 103, 108, 110]
    }
    
    result = recognizer.recognize_investment_law(mock_data)
    print(f"✅ 投资规律识别: {result['investment_law']['law_name']}")
    
    from a5l_philosophy.maoxuan import SixManagersHub
    
    # 测试六管理者Hub
    hub = SixManagersHub()
    proposal = {
        'stock': {'code': '000001', 'value_cell_score': 0.8, 'catalyst_score': 0.7},
        'position': 0.2
    }
    context = {}
    
    result = hub.evaluate_proposal(proposal, context)
    print(f"✅ 六管理者决策: {result['decision']}")
    
    print("=" * 60)
    print("基本功能测试完成")
    print("=" * 60)

if __name__ == '__main__':
    success = test_imports()
    if success:
        test_basic_functionality()
        print("\n🎉 所有测试通过！A5L-毛选投资哲学体系已就绪。")
    else:
        print("\n⚠️ 部分模块导入失败，请检查代码。")
