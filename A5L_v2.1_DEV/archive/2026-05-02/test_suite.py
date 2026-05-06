#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCHITECT-5L 单元测试套件
目标覆盖率: 70%

测试模块:
- Layer 1: 数据连接器
- Layer 2: 策略引擎
- Layer 3: 分析器
- Layer 4: 决策引擎
- Layer 5: 复盘系统
- Super Skill: 整合测试
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, "/workspace/projects/workspace")
sys.path.insert(0, "/workspace/projects/workspace/ARCHITECT_5L")

# ============================================================================
# Layer 1 测试 - 数据底座
# ============================================================================

class TestLayer1DataSource(unittest.TestCase):
    """测试数据层组件"""
    
    def setUp(self):
        """测试前准备"""
        self.workspace = "/workspace/projects/workspace"
    
    def test_data_source_manager_exists(self):
        """测试数据源管理器文件存在"""
        manager_path = f"{self.workspace}/ARCHITECT_5L/layer1_data/data_source_manager.py"
        self.assertTrue(os.path.exists(manager_path), "数据源管理器文件应存在")
    
    def test_data_pipeline_exists(self):
        """测试数据管道文件存在"""
        pipeline_path = f"{self.workspace}/ARCHITECT_5L/layer1_data/data_pipeline.py"
        self.assertTrue(os.path.exists(pipeline_path), "数据管道文件应存在")
    
    def test_akshare_connector_exists(self):
        """测试AKShare连接器存在"""
        connector_path = f"{self.workspace}/ARCHITECT_5L/layer1_data/connectors/akshare_real_connector.py"
        self.assertTrue(os.path.exists(connector_path), "AKShare连接器应存在")
    
    def test_datasource_registry_valid(self):
        """测试数据源注册表有效"""
        registry_path = f"{self.workspace}/ARCHITECT_5L/layer1_data/config/datasource_registry.json"
        if os.path.exists(registry_path):
            import json
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            # 检查connectors字段（实际使用的字段名）
            self.assertIn("connectors", registry, "注册表应包含connectors字段")
            self.assertGreater(len(registry["connectors"]), 0, "应至少有一个数据源")

# ============================================================================
# Layer 2 测试 - 策略引擎
# ============================================================================

class TestLayer2Strategy(unittest.TestCase):
    """测试策略层组件"""
    
    def setUp(self):
        self.workspace = "/workspace/projects/workspace"
    
    def test_strategy_engine_exists(self):
        """测试策略引擎文件存在"""
        engine_path = f"{self.workspace}/ARCHITECT_5L/layer2_strategy/strategy_engine.py"
        self.assertTrue(os.path.exists(engine_path), "策略引擎文件应存在")
    
    def test_strategy_registry_valid(self):
        """测试策略注册表有效"""
        registry_path = f"{self.workspace}/ARCHITECT_5L/layer2_strategy/strategy_registry.json"
        self.assertTrue(os.path.exists(registry_path), "策略注册表应存在")
        
        import json
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # 策略注册表是字典格式，键是策略ID
        self.assertGreaterEqual(len(registry), 7, "应至少有7个策略")
    
    def test_backtest_engine_exists(self):
        """测试回测引擎存在"""
        backtest_path = f"{self.workspace}/ARCHITECT_5L/layer2_strategy/backtester/backtest_engine.py"
        self.assertTrue(os.path.exists(backtest_path), "回测引擎应存在")
    
    def test_all_strategies_have_required_fields(self):
        """测试所有策略都有必需字段"""
        registry_path = f"{self.workspace}/ARCHITECT_5L/layer2_strategy/strategy_registry.json"
        
        import json
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        required_fields = ["name", "description", "market", "style"]
        for strategy_id, strategy in registry.items():
            for field in required_fields:
                self.assertIn(field, strategy, f"策略 {strategy_id} 应有 {field} 字段")

# ============================================================================
# Layer 3 测试 - 非结构化分析
# ============================================================================

class TestLayer3Analysis(unittest.TestCase):
    """测试分析层组件"""
    
    def setUp(self):
        self.workspace = "/workspace/projects/workspace"
    
    def test_info_aggregator_exists(self):
        """测试信息聚合器存在"""
        aggregator_path = f"{self.workspace}/ARCHITECT_5L/layer3_analysis/aggregators/info_aggregator.py"
        self.assertTrue(os.path.exists(aggregator_path), "信息聚合器应存在")
    
    def test_sentiment_analyzer_exists(self):
        """测试情绪分析器存在"""
        analyzer_path = f"{self.workspace}/ARCHITECT_5L/layer3_analysis/analyzers/sentiment_analyzer.py"
        self.assertTrue(os.path.exists(analyzer_path), "情绪分析器应存在")
    
    def test_report_generator_exists(self):
        """测试报告生成器存在"""
        generator_path = f"{self.workspace}/ARCHITECT_5L/layer3_analysis/report_generator.py"
        self.assertTrue(os.path.exists(generator_path), "报告生成器应存在")
    
    def test_real_info_connectors_exists(self):
        """测试真实信息连接器存在"""
        connectors_path = f"{self.workspace}/ARCHITECT_5L/layer3_analysis/connectors/real_info_connectors.py"
        self.assertTrue(os.path.exists(connectors_path), "真实信息连接器应存在")

# ============================================================================
# Layer 4 测试 - 决策信号
# ============================================================================

class TestLayer4Decision(unittest.TestCase):
    """测试决策层组件"""
    
    def setUp(self):
        self.workspace = "/workspace/projects/workspace"
    
    def test_signal_aggregator_exists(self):
        """测试信号聚合器存在"""
        aggregator_path = f"{self.workspace}/ARCHITECT_5L/layer4_decision/signal_aggregator.py"
        self.assertTrue(os.path.exists(aggregator_path), "信号聚合器应存在")
    
    def test_position_manager_exists(self):
        """测试仓位管理器存在"""
        manager_path = f"{self.workspace}/ARCHITECT_5L/layer4_decision/position_manager.py"
        self.assertTrue(os.path.exists(manager_path), "仓位管理器应存在")
    
    def test_decision_engine_exists(self):
        """测试决策引擎存在"""
        engine_path = f"{self.workspace}/ARCHITECT_5L/layer4_decision/decision_engine.py"
        self.assertTrue(os.path.exists(engine_path), "决策引擎应存在")

# ============================================================================
# Layer 5 测试 - 复盘进化
# ============================================================================

class TestLayer5Review(unittest.TestCase):
    """测试复盘层组件"""
    
    def setUp(self):
        self.workspace = "/workspace/projects/workspace"
    
    def test_review_engine_exists(self):
        """测试复盘引擎存在"""
        engine_path = f"{self.workspace}/ARCHITECT_5L/layer5_review/review_engine.py"
        self.assertTrue(os.path.exists(engine_path), "复盘引擎应存在")
    
    def test_learning_system_exists(self):
        """测试学习系统存在"""
        system_path = f"{self.workspace}/ARCHITECT_5L/layer5_review/learning_system.py"
        self.assertTrue(os.path.exists(system_path), "学习系统应存在")

# ============================================================================
# Super Skill 测试 - 整合测试
# ============================================================================

class TestSuperSkill(unittest.TestCase):
    """测试超级SKILL"""
    
    def setUp(self):
        self.workspace = "/workspace/projects/workspace"
    
    def test_super_skill_main_exists(self):
        """测试超级SKILL主文件存在"""
        skill_path = f"{self.workspace}/skills/ARCHITECT-5L-SUPER/SKILL.py"
        self.assertTrue(os.path.exists(skill_path), "超级SKILL主文件应存在")
    
    def test_super_skill_doc_exists(self):
        """测试超级SKILL文档存在"""
        doc_path = f"{self.workspace}/skills/ARCHITECT-5L-SUPER/SKILL.md"
        self.assertTrue(os.path.exists(doc_path), "超级SKILL文档应存在")
    
    def test_super_skill_registered(self):
        """测试超级SKILL已注册"""
        registry_path = f"{self.workspace}/SKILL_REGISTRY.json"
        
        import json
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        found = False
        for category in registry["categories"].values():
            for skill in category.get("skills", []):
                if skill.get("id") == "architect_5l_super":
                    found = True
                    break
        
        self.assertTrue(found, "超级SKILL应在注册表中")
    
    def test_all_layers_accessible(self):
        """测试所有层都可访问"""
        try:
            sys.path.insert(0, f"{self.workspace}/skills/ARCHITECT-5L-SUPER")
            from SKILL import Architect5LSuperSkill
            
            skill = Architect5LSuperSkill()
            
            # 检查所有层都存在
            self.assertIsNotNone(skill.layer1, "Layer 1应可访问")
            self.assertIsNotNone(skill.layer2, "Layer 2应可访问")
            self.assertIsNotNone(skill.layer3, "Layer 3应可访问")
            self.assertIsNotNone(skill.layer4, "Layer 4应可访问")
            self.assertIsNotNone(skill.layer5, "Layer 5应可访问")
            
        except Exception as e:
            self.fail(f"初始化SuperSkill失败: {e}")

# ============================================================================
# 工具函数测试
# ============================================================================

class TestUtilityFunctions(unittest.TestCase):
    """测试工具函数"""
    
    def test_workspace_structure(self):
        """测试工作空间结构完整"""
        required_dirs = [
            "/workspace/projects/workspace/ARCHITECT_5L",
            "/workspace/projects/workspace/skills",
            "/workspace/projects/workspace/data",
            "/workspace/projects/workspace/memory",
        ]
        
        for dir_path in required_dirs:
            self.assertTrue(os.path.exists(dir_path), f"目录 {dir_path} 应存在")
    
    def test_goals_file_valid(self):
        """测试目标文件有效"""
        goals_path = "/workspace/projects/workspace/data/goals/goals.json"
        
        import json
        with open(goals_path, 'r') as f:
            goals = json.load(f)
        
        self.assertIsInstance(goals, list, "目标应为列表")
        self.assertGreater(len(goals), 0, "应至少有一个目标")
        
        # 检查G006存在
        g006 = [g for g in goals if g.get("id") == "G006-ARCHITECT-5L"]
        self.assertEqual(len(g006), 1, "应有G006-ARCHITECT-5L目标")

# ============================================================================
# 主函数
# ============================================================================

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestLayer1DataSource,
        TestLayer2Strategy,
        TestLayer3Analysis,
        TestLayer4Decision,
        TestLayer5Review,
        TestSuperSkill,
        TestUtilityFunctions,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 生成报告
    print("\n" + "="*70)
    print("📊 测试报告")
    print("="*70)
    print(f"测试总数: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过!")
    else:
        print("\n⚠️ 部分测试未通过")
    
    # 计算覆盖率（简化版）
    total_tests = result.testsRun
    passed_tests = result.testsRun - len(result.failures) - len(result.errors)
    coverage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"测试通过率: {coverage:.1f}%")
    print("="*70)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()
