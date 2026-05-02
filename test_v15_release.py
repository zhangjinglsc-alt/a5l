#!/usr/bin/env python3
"""
A5L v1.5.0 发布测试套件
Phase 2 Day 5: 测试验证
"""

import sys
sys.path.insert(0, '/workspace/projects/workspace')

import unittest
from datetime import datetime


class TestA5LIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_config_loading(self):
        """测试配置加载"""
        from ARCHITECT_5L.layer0_control.config_manager import config
        
        self.assertIsNotNone(config)
        self.assertEqual(config.get_system('name'), 'A5L')
        self.assertEqual(config.get_system('version'), '1.5.0')
    
    def test_unified_api_initialization(self):
        """测试统一API初始化"""
        from ARCHITECT_5L.layer0_control.unified_api import A5LUnifiedAPI
        
        api = A5LUnifiedAPI()
        self.assertIsNotNone(api)
    
    def test_integration_engine_initialization(self):
        """测试整合引擎初始化"""
        from ARCHITECT_5L.layer0_control.integration_engine import A5LIntegrationEngine
        
        engine = A5LIntegrationEngine()
        self.assertIsNotNone(engine)
        self.assertFalse(engine.integrated)  # 尚未整合
    
    def test_super_skill_v15_initialization(self):
        """测试Super SKILL v1.5初始化"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("SKILL_v15", 
            "/workspace/projects/workspace/skills/ARCHITECT-5L-SUPER/SKILL_v15.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        A5LSuperSkillV15 = module.A5LSuperSkillV15
        
        super_skill = A5LSuperSkillV15()
        
        self.assertEqual(super_skill.version, '1.5.0')
        self.assertEqual(len(super_skill.integration_engine.skills), 35)
        self.assertTrue(super_skill.integration_engine.integrated)
    
    def test_skill_distribution(self):
        """测试SKILL分布"""
        from skills.ARCHITECT_5L_SUPER.SKILL_v15 import A5LSuperSkillV15
        
        super_skill = A5LSuperSkillV15()
        
        # 每层7个SKILL
        for layer in [1, 2, 3, 4, 5]:
            layer_skills = [s for s in super_skill.integration_engine.skills if s.layer == layer]
            self.assertEqual(len(layer_skills), 7, f"L{layer}应该有7个skill")
    
    def test_no_conflicts(self):
        """测试无冲突"""
        from skills.ARCHITECT_5L_SUPER.SKILL_v15 import A5LSuperSkillV15
        
        super_skill = A5LSuperSkillV15()
        
        # 整合后应该没有冲突
        self.assertEqual(len(super_skill.integration_engine.conflict_detector.conflicts), 0)


class TestA5LAPI(unittest.TestCase):
    """API测试"""
    
    def test_quick_analysis(self):
        """测试快速分析"""
        from skills.ARCHITECT_5L_SUPER.SKILL_v15 import A5LSuperSkillV15
        
        super_skill = A5LSuperSkillV15()
        result = super_skill.quick_analysis("600519.SH")
        
        self.assertEqual(result['symbol'], '600519.SH')
        self.assertIn('score', result)
        self.assertIn('recommendation', result)
    
    def test_health_check(self):
        """测试健康检查"""
        from skills.ARCHITECT_5L_SUPER.SKILL_v15 import A5LSuperSkillV15
        
        super_skill = A5LSuperSkillV15()
        health = super_skill.health_check()
        
        self.assertEqual(health['status'], 'healthy')
        self.assertEqual(health['skills_count'], 35)


def run_tests():
    """运行测试"""
    print("=" * 80)
    print("🧪 A5L v1.5.0 测试套件")
    print("=" * 80)
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestA5LIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestA5LAPI))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 80)
    
    if result.wasSuccessful():
        print("🎉 所有测试通过！v1.5.0 可以发布！")
        return True
    else:
        print("❌ 测试失败，需要修复")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
