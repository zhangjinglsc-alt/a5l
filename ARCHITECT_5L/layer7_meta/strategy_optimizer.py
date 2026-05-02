#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略参数优化器
支持网格搜索和遗传算法优化
"""

import json
import os
import sys
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

sys.path.insert(0, "/workspace/projects/workspace")

@dataclass
class OptimizationResult:
    """优化结果"""
    strategy_id: str
    best_params: Dict[str, Any]
    best_score: float
    optimization_method: str
    iterations: int
    improvement: float  # 相对于默认参数的改进

class StrategyOptimizer:
    """策略参数优化器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.results_cache = []
        
    def grid_search(self, strategy_id: str, 
                   param_grid: Dict[str, List],
                   symbol: str = "000001.SZ",
                   start_date: str = None,
                   end_date: str = None) -> OptimizationResult:
        """
        网格搜索优化
        
        Args:
            strategy_id: 策略ID
            param_grid: 参数网格 {参数名: [候选值列表]}
            symbol: 回测标的
            start_date: 回测开始日期
            end_date: 回测结束日期
            
        Returns:
            OptimizationResult: 优化结果
        """
        print(f"🔍 开始网格搜索优化: {strategy_id}")
        print(f"   参数空间: {param_grid}")
        
        # 生成所有参数组合
        import itertools
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        all_combinations = list(itertools.product(*param_values))
        print(f"   总组合数: {len(all_combinations)}")
        
        best_score = -float('inf')
        best_params = None
        
        # 遍历所有组合
        for i, values in enumerate(all_combinations):
            params = dict(zip(param_names, values))
            
            # 模拟回测评分 (实际应调用回测引擎)
            score = self._simulate_backtest(strategy_id, params, symbol, start_date, end_date)
            
            if score > best_score:
                best_score = score
                best_params = params
                
            if (i + 1) % 10 == 0:
                print(f"   进度: {i+1}/{len(all_combinations)}, 当前最佳: {best_score:.4f}")
        
        # 计算改进幅度
        default_score = self._simulate_backtest(strategy_id, {}, symbol, start_date, end_date)
        improvement = (best_score - default_score) / abs(default_score) * 100 if default_score != 0 else 0
        
        result = OptimizationResult(
            strategy_id=strategy_id,
            best_params=best_params,
            best_score=best_score,
            optimization_method="grid_search",
            iterations=len(all_combinations),
            improvement=improvement
        )
        
        self.results_cache.append(result)
        
        print(f"✅ 网格搜索完成")
        print(f"   最佳参数: {best_params}")
        print(f"   最佳评分: {best_score:.4f}")
        print(f"   改进幅度: {improvement:.2f}%")
        
        return result
    
    def genetic_optimize(self, strategy_id: str,
                        param_bounds: Dict[str, Tuple[float, float]],
                        symbol: str = "000001.SZ",
                        population_size: int = 20,
                        generations: int = 10,
                        mutation_rate: float = 0.1) -> OptimizationResult:
        """
        遗传算法优化
        
        Args:
            strategy_id: 策略ID
            param_bounds: 参数范围 {参数名: (最小值, 最大值)}
            symbol: 回测标的
            population_size: 种群大小
            generations: 迭代代数
            mutation_rate: 变异率
            
        Returns:
            OptimizationResult: 优化结果
        """
        print(f"🧬 开始遗传算法优化: {strategy_id}")
        print(f"   参数范围: {param_bounds}")
        print(f"   种群大小: {population_size}, 迭代代数: {generations}")
        
        # 初始化种群
        population = self._init_population(param_bounds, population_size)
        
        best_score = -float('inf')
        best_params = None
        total_iterations = 0
        
        for gen in range(generations):
            # 评估种群
            scores = []
            for individual in population:
                score = self._simulate_backtest(strategy_id, individual, symbol)
                scores.append((score, individual))
                total_iterations += 1
            
            # 排序
            scores.sort(reverse=True)
            
            # 更新最佳
            if scores[0][0] > best_score:
                best_score = scores[0][0]
                best_params = scores[0][1]
            
            print(f"   第{gen+1}代: 最佳={best_score:.4f}, 平均={np.mean([s[0] for s in scores]):.4f}")
            
            # 选择、交叉、变异
            population = self._evolve_population(scores, param_bounds, population_size, mutation_rate)
        
        # 计算改进幅度
        default_score = self._simulate_backtest(strategy_id, {}, symbol)
        improvement = (best_score - default_score) / abs(default_score) * 100 if default_score != 0 else 0
        
        result = OptimizationResult(
            strategy_id=strategy_id,
            best_params=best_params,
            best_score=best_score,
            optimization_method="genetic",
            iterations=total_iterations,
            improvement=improvement
        )
        
        self.results_cache.append(result)
        
        print(f"✅ 遗传算法优化完成")
        print(f"   最佳参数: {best_params}")
        print(f"   最佳评分: {best_score:.4f}")
        print(f"   改进幅度: {improvement:.2f}%")
        
        return result
    
    def _simulate_backtest(self, strategy_id: str, params: Dict,
                          symbol: str, start_date: str = None, end_date: str = None) -> float:
        """
        模拟回测 (简化版)
        实际应调用回测引擎
        """
        # 模拟评分计算 (实际应使用真实回测结果)
        base_score = random.gauss(0.12, 0.05)  # 基准收益12%
        
        # 参数调整影响
        param_bonus = 0
        for key, value in params.items():
            if 'stop_loss' in key:
                param_bonus += (value - 5) * 0.002  # 止损优化
            elif 'take_profit' in key:
                param_bonus += (value - 10) * 0.001  # 止盈优化
            elif 'period' in key:
                param_bonus += (20 - abs(value - 20)) * 0.001  # 周期优化
        
        return base_score + param_bonus + random.gauss(0, 0.02)
    
    def _init_population(self, param_bounds: Dict, size: int) -> List[Dict]:
        """初始化种群"""
        population = []
        for _ in range(size):
            individual = {}
            for param, (min_val, max_val) in param_bounds.items():
                if isinstance(min_val, int):
                    individual[param] = random.randint(min_val, max_val)
                else:
                    individual[param] = random.uniform(min_val, max_val)
            population.append(individual)
        return population
    
    def _evolve_population(self, scored_population: List[Tuple[float, Dict]],
                          param_bounds: Dict,
                          population_size: int,
                          mutation_rate: float) -> List[Dict]:
        """进化种群"""
        # 精英保留
        elite_size = max(2, population_size // 5)
        new_population = [ind for _, ind in scored_population[:elite_size]]
        
        # 生成后代
        while len(new_population) < population_size:
            # 选择父母
            parent1 = random.choice(scored_population[:len(scored_population)//2])[1]
            parent2 = random.choice(scored_population[:len(scored_population)//2])[1]
            
            # 交叉
            child = {}
            for param in param_bounds.keys():
                if random.random() < 0.5:
                    child[param] = parent1[param]
                else:
                    child[param] = parent2[param]
                
                # 变异
                if random.random() < mutation_rate:
                    min_val, max_val = param_bounds[param]
                    if isinstance(min_val, int):
                        child[param] = random.randint(min_val, max_val)
                    else:
                        child[param] = random.uniform(min_val, max_val)
            
            new_population.append(child)
        
        return new_population
    
    def save_results(self, filepath: str = None):
        """保存优化结果"""
        if filepath is None:
            filepath = f"{self.workspace}/data/optimization/strategy_optimization_results.json"
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        results_data = []
        for result in self.results_cache:
            results_data.append({
                "strategy_id": result.strategy_id,
                "best_params": result.best_params,
                "best_score": result.best_score,
                "optimization_method": result.optimization_method,
                "iterations": result.iterations,
                "improvement": result.improvement,
                "timestamp": datetime.now().isoformat()
            })
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 优化结果已保存: {filepath}")

def demo():
    """演示优化器"""
    print("="*70)
    print("🎯 策略参数优化器演示")
    print("="*70)
    print()
    
    optimizer = StrategyOptimizer()
    
    # 网格搜索示例
    print("📊 示例1: 网格搜索优化海龟交易法则")
    print("-"*70)
    param_grid = {
        "entry_period": [10, 20, 30, 40],
        "exit_period": [5, 10, 15],
        "stop_loss_pct": [2.0, 3.0, 4.0, 5.0]
    }
    
    result1 = optimizer.grid_search(
        strategy_id="turtle_trading",
        param_grid=param_grid,
        symbol="000001.SZ",
        start_date="2025-01-01",
        end_date="2025-12-31"
    )
    print()
    
    # 遗传算法示例
    print("📊 示例2: 遗传算法优化趋势突破策略")
    print("-"*70)
    param_bounds = {
        "breakout_period": (10, 60),
        "stop_loss_pct": (2.0, 8.0),
        "take_profit_pct": (5.0, 20.0),
        "position_size": (0.05, 0.2)
    }
    
    result2 = optimizer.genetic_optimize(
        strategy_id="trend_breakout",
        param_bounds=param_bounds,
        symbol="000858.SZ",
        population_size=15,
        generations=8
    )
    print()
    
    # 保存结果
    optimizer.save_results()
    
    print("="*70)
    print("✅ 优化演示完成!")
    print("="*70)

if __name__ == "__main__":
    demo()
