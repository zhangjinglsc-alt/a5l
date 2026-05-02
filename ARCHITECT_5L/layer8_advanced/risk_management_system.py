#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险管理系统 (Risk Management System)
P3阶段 - 风险度量与控制

功能:
- VaR计算 (历史模拟法、参数法、蒙特卡洛)
- CVaR (条件VaR)
- 压力测试
- 风险报告生成
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from scipy import stats
import json
import os
import sys

sys.path.insert(0, "/workspace/projects/workspace")

class RiskCalculator:
    """风险计算器"""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
    
    def calculate_var_historical(self, returns: pd.Series,
                                  position_value: float) -> Dict:
        """
        历史模拟法计算VaR
        
        Args:
            returns: 收益率序列
            position_value: 持仓市值
            
        Returns:
            VaR结果
        """
        var_percentile = (1 - self.confidence_level) * 100
        var_return = np.percentile(returns.dropna(), var_percentile)
        var_amount = position_value * abs(var_return)
        
        return {
            "method": "historical",
            "confidence_level": self.confidence_level,
            "var_return": var_return,
            "var_amount": var_amount,
            "var_percentage": abs(var_return),
            "var_bps": abs(var_return) * 10000
        }
    
    def calculate_var_parametric(self, returns: pd.Series,
                                  position_value: float) -> Dict:
        """
        参数法计算VaR (假设正态分布)
        """
        mean = returns.mean()
        std = returns.std()
        
        z_score = stats.norm.ppf(1 - self.confidence_level)
        var_return = mean + z_score * std
        var_amount = position_value * abs(var_return)
        
        return {
            "method": "parametric",
            "confidence_level": self.confidence_level,
            "var_return": var_return,
            "var_amount": var_amount,
            "var_percentage": abs(var_return),
            "mean": mean,
            "std": std,
            "z_score": z_score
        }
    
    def calculate_var_montecarlo(self, returns: pd.Series,
                                  position_value: float,
                                  num_simulations: int = 10000) -> Dict:
        """
        蒙特卡洛模拟计算VaR
        """
        mean = returns.mean()
        std = returns.std()
        
        # 生成模拟收益率
        simulated_returns = np.random.normal(mean, std, num_simulations)
        
        var_percentile = (1 - self.confidence_level) * 100
        var_return = np.percentile(simulated_returns, var_percentile)
        var_amount = position_value * abs(var_return)
        
        return {
            "method": "monte_carlo",
            "confidence_level": self.confidence_level,
            "var_return": var_return,
            "var_amount": var_amount,
            "var_percentage": abs(var_return),
            "num_simulations": num_simulations
        }
    
    def calculate_cvar(self, returns: pd.Series,
                       position_value: float) -> Dict:
        """
        计算CVaR (条件VaR / Expected Shortfall)
        """
        var_result = self.calculate_var_historical(returns, position_value)
        var_threshold = var_result['var_return']
        
        # CVaR是超过VaR阈值的平均损失
        tail_losses = returns[returns <= var_threshold]
        cvar_return = tail_losses.mean() if len(tail_losses) > 0 else var_threshold
        cvar_amount = position_value * abs(cvar_return)
        
        return {
            "confidence_level": self.confidence_level,
            "cvar_return": cvar_return,
            "cvar_amount": cvar_amount,
            "cvar_percentage": abs(cvar_return),
            "tail_observations": len(tail_losses),
            "var_threshold": var_threshold
        }
    
    def calculate_all_var(self, returns: pd.Series,
                          position_value: float) -> Dict:
        """计算所有VaR方法"""
        return {
            "historical": self.calculate_var_historical(returns, position_value),
            "parametric": self.calculate_var_parametric(returns, position_value),
            "monte_carlo": self.calculate_var_montecarlo(returns, position_value),
            "cvar": self.calculate_cvar(returns, position_value)
        }

class StressTester:
    """压力测试器"""
    
    def __init__(self):
        # 预定义压力场景
        self.scenarios = {
            "market_crash": {
                "name": "市场崩盘",
                "description": "2008年金融危机级别",
                "market_shock": -0.30,
                "volatility_spike": 3.0
            },
            "correction": {
                "name": "市场调整",
                "description": "2020年3月级别",
                "market_shock": -0.15,
                "volatility_spike": 2.0
            },
            "interest_rate_hike": {
                "name": "加息周期",
                "description": "利率快速上升",
                "rate_change": 0.02,
                "bond_impact": -0.10
            },
            "liquidity_crisis": {
                "name": "流动性危机",
                "description": "市场流动性枯竭",
                "spread_widening": 5.0,
                "volume_drop": 0.70
            },
            "sector_rotation": {
                "name": "行业轮动",
                "description": "剧烈风格切换",
                "tech_impact": -0.20,
                "value_impact": 0.10
            }
        }
    
    def run_stress_test(self, portfolio: Dict,
                        scenario_name: str = None) -> Dict:
        """
        运行压力测试
        
        Args:
            portfolio: 持仓组合
            scenario_name: 场景名称 (None则测试所有场景)
            
        Returns:
            压力测试结果
        """
        results = {}
        
        scenarios_to_test = [scenario_name] if scenario_name else self.scenarios.keys()
        
        for scenario_key in scenarios_to_test:
            if scenario_key not in self.scenarios:
                continue
            
            scenario = self.scenarios[scenario_key]
            
            # 计算组合在该场景下的损失 (简化计算)
            portfolio_value = portfolio.get('total_value', 1000000)
            
            # 根据场景类型计算冲击
            if scenario_key == "market_crash":
                loss_pct = scenario['market_shock']
            elif scenario_key == "correction":
                loss_pct = scenario['market_shock']
            elif scenario_key == "interest_rate_hike":
                # 假设组合中30%是债券
                bond_allocation = portfolio.get('bond_allocation', 0.3)
                loss_pct = bond_allocation * scenario['bond_impact']
            elif scenario_key == "liquidity_crisis":
                loss_pct = -0.10  # 假设10%损失
            elif scenario_key == "sector_rotation":
                # 假设组合50% tech, 50% value
                loss_pct = 0.5 * scenario['tech_impact'] + 0.5 * scenario['value_impact']
            else:
                loss_pct = -0.05
            
            loss_amount = portfolio_value * loss_pct
            
            results[scenario_key] = {
                "scenario_name": scenario['name'],
                "description": scenario['description'],
                "portfolio_value": portfolio_value,
                "loss_percentage": loss_pct,
                "loss_amount": loss_amount,
                "remaining_value": portfolio_value + loss_amount
            }
        
        return results
    
    def add_custom_scenario(self, scenario_id: str, scenario: Dict):
        """添加自定义压力场景"""
        self.scenarios[scenario_id] = scenario

class RiskReportGenerator:
    """风险报告生成器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
    
    def generate_report(self, portfolio: Dict,
                       var_results: Dict,
                       stress_results: Dict) -> str:
        """生成风险报告"""
        report = f"""# 风险管理报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 组合概览

- **组合市值**: {portfolio.get('total_value', 0):,.2f}
- **股票数量**: {len(portfolio.get('holdings', {}))}

## VaR分析

### 历史模拟法
- VaR (95%): {var_results['historical']['var_percentage']:.2%}
- 损失金额: {var_results['historical']['var_amount']:,.2f}

### 参数法
- VaR (95%): {var_results['parametric']['var_percentage']:.2%}
- 损失金额: {var_results['parametric']['var_amount']:,.2f}
- 均值: {var_results['parametric']['mean']:.4f}
- 标准差: {var_results['parametric']['std']:.4f}

### 蒙特卡洛模拟
- VaR (95%): {var_results['monte_carlo']['var_percentage']:.2%}
- 损失金额: {var_results['monte_carlo']['var_amount']:,.2f}
- 模拟次数: {var_results['monte_carlo']['num_simulations']:,}

### CVaR (Expected Shortfall)
- CVaR (95%): {var_results['cvar']['cvar_percentage']:.2%}
- 损失金额: {var_results['cvar']['cvar_amount']:,.2f}
- 尾部观测数: {var_results['cvar']['tail_observations']}

## 压力测试

"""
        
        for scenario_id, result in stress_results.items():
            report += f"""### {result['scenario_name']}
- 描述: {result['description']}
- 损失: {result['loss_percentage']:.2%} ({result['loss_amount']:,.2f})
- 剩余价值: {result['remaining_value']:,.2f}

"""
        
        report += """## 风险建议

1. **VaR限额**: 建议单日VaR不超过组合价值的2%
2. **压力测试**: 确保在最坏场景下损失可控
3. **分散投资**: 降低单一资产集中度风险
4. **动态对冲**: 根据VaR动态调整对冲比例

---
**ARCHITECT-5L Risk Management System**
"""
        
        return report
    
    def save_report(self, report: str, filename: str = None):
        """保存报告"""
        if filename is None:
            filename = f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        filepath = f"{self.workspace}/data/risk_reports/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        print(f"💾 风险报告已保存: {filepath}")

class RiskManagementSystem:
    """风险管理系统"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.risk_calculator = RiskCalculator(confidence_level=0.95)
        self.stress_tester = StressTester()
        self.report_generator = RiskReportGenerator(workspace)
        
        print("🛡️ 风险管理系统初始化")
        print("   支持: VaR, CVaR, 压力测试")
    
    def analyze_portfolio(self, portfolio: Dict,
                         price_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        分析组合风险
        
        Args:
            portfolio: 持仓组合
            price_data: 各标的价格数据
            
        Returns:
            风险分析结果
        """
        print(f"\n{'='*70}")
        print(f"🛡️ 组合风险分析")
        print(f"{'='*70}")
        
        # 计算组合收益率
        portfolio_returns = self._calculate_portfolio_returns(
            portfolio, price_data
        )
        
        portfolio_value = portfolio.get('total_value', 1000000)
        
        # 计算VaR
        print("\n📊 计算VaR...")
        var_results = self.risk_calculator.calculate_all_var(
            portfolio_returns, portfolio_value
        )
        
        print(f"   历史VaR (95%): {var_results['historical']['var_percentage']:.2%}")
        print(f"   CVaR (95%): {var_results['cvar']['cvar_percentage']:.2%}")
        
        # 压力测试
        print("\n🔥 压力测试...")
        stress_results = self.stress_tester.run_stress_test(portfolio)
        
        for scenario_id, result in stress_results.items():
            print(f"   {result['scenario_name']}: {result['loss_percentage']:.2%}")
        
        # 生成报告
        report = self.report_generator.generate_report(
            portfolio, var_results, stress_results
        )
        
        return {
            "portfolio_value": portfolio_value,
            "var_results": var_results,
            "stress_results": stress_results,
            "report": report
        }
    
    def _calculate_portfolio_returns(self, portfolio: Dict,
                                    price_data: Dict[str, pd.DataFrame]) -> pd.Series:
        """计算组合收益率"""
        # 简化: 使用等权组合
        returns_list = []
        
        for symbol, data in price_data.items():
            if 'close' in data.columns:
                ret = data['close'].pct_change().dropna()
                returns_list.append(ret)
        
        if returns_list:
            # 等权平均
            portfolio_returns = pd.concat(returns_list, axis=1).mean(axis=1)
            return portfolio_returns
        else:
            # 模拟数据
            return pd.Series(np.random.normal(0.001, 0.02, 252))

def demo():
    """演示风险管理系统"""
    print("="*70)
    print("🛡️ 风险管理系统演示")
    print("="*70)
    print()
    
    # 初始化系统
    risk_system = RiskManagementSystem()
    
    # 模拟组合
    portfolio = {
        "total_value": 1000000,
        "cash": 100000,
        "holdings": {
            "000001.SZ": {"quantity": 1000, "price": 12.5},
            "000002.SZ": {"quantity": 500, "price": 25.0},
            "600519.SH": {"quantity": 10, "price": 1800.0}
        }
    }
    
    # 模拟价格数据
    np.random.seed(42)
    price_data = {}
    
    for symbol in portfolio['holdings'].keys():
        returns = np.random.normal(0.001, 0.02, 252)
        prices = 100 * (1 + returns).cumprod()
        price_data[symbol] = pd.DataFrame({
            'close': prices
        })
    
    # 分析组合
    result = risk_system.analyze_portfolio(portfolio, price_data)
    
    # 显示报告
    print("\n" + "="*70)
    print("📄 风险报告预览")
    print("="*70)
    print(result['report'][:1500])
    print("...")
    
    # 保存报告
    risk_system.report_generator.save_report(result['report'])
    
    print()
    print("="*70)
    print("✅ 风险管理系统演示完成!")
    print("="*70)

if __name__ == "__main__":
    demo()
