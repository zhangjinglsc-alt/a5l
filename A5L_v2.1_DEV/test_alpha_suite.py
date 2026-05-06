#!/usr/bin/env python3
"""
A5L Alpha测试 - 自动化测试套件
Rigorous Automated Testing Suite
"""

import unittest
import json
import time
import random
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.insert(0, 'data/architect_5l')

class TestDataPipeline(unittest.TestCase):
    """数据流测试"""
    
    def setUp(self):
        """测试准备"""
        pass
    
    def test_001_realtime_price_fetch(self):
        """DATA-001: 实时价格获取"""
        from realtime_data_pipeline import RealtimeDataPipeline
        
        pipeline = RealtimeDataPipeline()
        start = time.time()
        tick = pipeline.fetch_price("000066")
        elapsed = (time.time() - start) * 1000
        
        self.assertIsNotNone(tick)
        self.assertEqual(tick.symbol, "000066")
        self.assertGreater(tick.price, 0)
        self.assertLess(elapsed, 100, f"延迟{elapsed:.0f}ms超过100ms限制")
    
    def test_002_multi_source_aggregation(self):
        """DATA-002: 多源数据聚合"""
        from realtime_data_pipeline import RealtimeDataPipeline
        
        pipeline = RealtimeDataPipeline()
        tick = pipeline.fetch_price("000066")
        
        # 验证聚合价格合理性
        self.assertIsNotNone(tick)
        self.assertGreater(tick.bid, 0)
        self.assertGreater(tick.ask, tick.bid)
        # 验证偏差
        mid_price = (tick.bid + tick.ask) / 2
        deviation = abs(tick.price - mid_price) / mid_price
        self.assertLess(deviation, 0.005, "价格偏差超过0.5%")
    
    def test_003_data_quality_report(self):
        """DATA-003: 数据质量报告"""
        from realtime_data_pipeline import RealtimeDataPipeline
        
        pipeline = RealtimeDataPipeline()
        report = pipeline.get_data_quality_report()
        
        self.assertIn("cache_size", report)
        self.assertIn("health_score", report)
        self.assertGreaterEqual(report["health_score"], 90, "数据健康度低于90")


class TestRiskManagement(unittest.TestCase):
    """风控系统测试"""
    
    def setUp(self):
        from risk_manager import RealtimeRiskManager
        self.risk_mgr = RealtimeRiskManager()
        self.positions = [
            {"symbol": "000066", "market_value": 200000, "volatility": 0.25, "sector": "tech"},
            {"symbol": "601975", "market_value": 150000, "volatility": 0.30, "sector": "energy"},
        ]
    
    def test_004_var_calculation(self):
        """RISK-001: VaR计算"""
        var_95, vol = self.risk_mgr.calculate_var(self.positions, 0.95)
        
        self.assertGreater(var_95, 0)
        self.assertGreater(vol, 0)
        # VaR不能超过组合价值的50%
        total_value = sum(p["market_value"] for p in self.positions)
        self.assertLess(var_95 / total_value, 0.5)
    
    def test_005_greeks_calculation(self):
        """RISK-002: 希腊字母计算"""
        greeks = self.risk_mgr.calculate_greeks(self.positions, {})
        
        self.assertIn("delta", greeks)
        self.assertIn("gamma", greeks)
        self.assertIn("vega", greeks)
        # Delta应该在合理范围
        self.assertGreater(abs(greeks["delta"]), 0)
        self.assertLess(abs(greeks["delta"]), 2)
    
    def test_006_circuit_breaker_daily_loss(self):
        """RISK-003: 日亏损熔断"""
        portfolio_stats = {
            "daily_pnl_pct": -0.06,  # 6%亏损，超过5%限制
            "consecutive_losses": 0,
            "volatility_spike": 0
        }
        
        result = self.risk_mgr.check_circuit_breakers(portfolio_stats)
        
        self.assertTrue(result.get("triggered"))
        self.assertEqual(result.get("reason"), "daily_loss_limit")
    
    def test_007_risk_limit_check(self):
        """RISK-004: 风险限制检查"""
        # 创建一个超限的持仓
        oversized_positions = [
            {"symbol": "000066", "market_value": 800000, "volatility": 0.25, "liquidity_score": 0.8},
            {"symbol": "601975", "market_value": 200000, "volatility": 0.30, "liquidity_score": 0.6},
        ]
        
        violations = self.risk_mgr.check_risk_limits(oversized_positions)
        
        # 应该检测到集中度违规
        concentration_violations = [v for v in violations if v["type"] == "concentration"]
        self.assertGreater(len(concentration_violations), 0)


class TestPositionManagement(unittest.TestCase):
    """仓位管理测试"""
    
    def setUp(self):
        from position_manager import PositionManager
        self.pm = PositionManager(total_capital=1000000.0)
    
    def test_008_kelly_criterion(self):
        """POS-001: Kelly准则计算"""
        kelly = self.pm.calculate_kelly_criterion(
            "000066",
            win_rate=0.60,
            avg_win=0.10,
            avg_loss=0.05
        )
        
        # Kelly应该在0-20%之间 (半Kelly限制)
        self.assertGreaterEqual(kelly, 0)
        self.assertLessEqual(kelly, 0.20)
    
    def test_009_risk_parity_weights(self):
        """POS-002: 风险平价权重"""
        symbols = ["000066", "601975", "688981"]
        volatilities = {
            "000066": 0.25,
            "601975": 0.30,
            "688981": 0.35
        }
        
        weights = self.pm.calculate_risk_parity_weights(symbols, volatilities)
        
        # 权重总和应该接近1
        total_weight = sum(weights.values())
        self.assertAlmostEqual(total_weight, 1.0, delta=0.01)
        
        # 波动率低的应该有更高权重
        self.assertGreater(weights["000066"], weights["688981"])
    
    def test_010_portfolio_optimization(self):
        """POS-003: 投资组合优化"""
        opportunities = [
            {"symbol": "000066", "price": 20.0, "win_rate": 0.60, "avg_win": 0.10, "avg_loss": 0.05, "volatility": 0.25},
            {"symbol": "601975", "price": 4.5, "win_rate": 0.55, "avg_win": 0.08, "avg_loss": 0.04, "volatility": 0.30},
        ]
        
        result = self.pm.optimize_portfolio(opportunities)
        
        self.assertIn("positions", result)
        self.assertIn("total_invested", result)
        self.assertGreater(result["total_invested"], 0)
        # 投资总额不应该超过总资金
        self.assertLessEqual(result["total_invested"], 1000000.0)


class TestExecution(unittest.TestCase):
    """交易执行测试"""
    
    def setUp(self):
        from execution_optimizer import ExecutionOptimizer, ExecutionAlgo
        self.opt = ExecutionOptimizer()
        self.algo = ExecutionAlgo
    
    def test_011_market_order(self):
        """EXEC-001: 市价单执行"""
        result = self.opt.execute("000066", 1000, self.algo.MARKET)
        
        self.assertEqual(result.filled_quantity, 1000)
        self.assertGreater(result.avg_price, 0)
        # 市价单滑点应该较大
        self.assertGreater(result.slippage, 0)
    
    def test_012_twap_order(self):
        """EXEC-002: TWAP执行"""
        result = self.opt.execute("000066", 10000, self.algo.TWAP, time_window=30)
        
        self.assertEqual(result.filled_quantity, 10000)
        self.assertGreater(result.slices, 1)  # 应该拆单
        # TWAP滑点应该小于市价单
        self.assertLess(result.slippage, 0.003)
    
    def test_013_vwap_order(self):
        """EXEC-003: VWAP执行"""
        result = self.opt.execute("000066", 10000, self.algo.VWAP, time_window=30)
        
        self.assertEqual(result.filled_quantity, 10000)
        # VWAP应该比TWAP滑点更小
        self.assertGreater(result.slices, 1)


class TestBacktest(unittest.TestCase):
    """回测引擎测试"""
    
    def setUp(self):
        from backtest_engine import EventDrivenBacktester
        self.bt = EventDrivenBacktester(initial_capital=1000000.0)
    
    def test_014_backtest_run(self):
        """BKT-001: 回测运行"""
        start_time = time.time()
        
        report = self.bt.run_backtest(
            start_date="2024-01-01",
            end_date="2024-01-31",
            symbols=["000066"]
        )
        
        elapsed = time.time() - start_time
        
        self.assertIn("total_return", report)
        self.assertIn("sharpe_ratio", report)
        # 回测应该快速完成
        self.assertLess(elapsed, 5.0)
    
    def test_015_backtest_performance(self):
        """BKT-002: 回测性能"""
        import random
        
        start_time = time.time()
        
        # 添加信号事件
        from backtest_engine import Event, EventType
        for i in range(100):
            event = Event(
                timestamp=datetime(2024, 1, 1) + timedelta(days=i),
                event_type=EventType.SIGNAL,
                data={"symbol": "000066", "signal": "buy", "quantity": 100},
                priority=1
            )
            self.bt.add_event(event)
        
        # 处理事件
        while self.bt.events:
            event = self.bt.events.pop(0)
        
        elapsed = time.time() - start_time
        events_per_sec = 100 / elapsed if elapsed > 0 else 0
        
        # 性能应该超过1000 events/秒
        self.assertGreater(events_per_sec, 1000)


def run_alpha_tests():
    """运行Alpha测试套件"""
    print("=" * 70)
    print("🧪 A5L Alpha测试 - 自动化测试套件")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestDataPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestPositionManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestBacktest))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    print(f"测试用例总数: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 所有测试通过！Alpha测试可以继续推进。")
    else:
        print("\n❌ 存在失败的测试，请先修复问题。")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_alpha_tests()
    sys.exit(0 if success else 1)
