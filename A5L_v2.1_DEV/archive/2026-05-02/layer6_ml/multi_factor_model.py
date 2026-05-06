#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多因子模型 (Multi-Factor Model)
Barra风格因子 + 因子有效性检验

功能:
- Barra风格因子计算
- 因子有效性检验 (IC测试、分层测试)
- 因子组合优化
- 因子风险分析
"""

import numpy as np
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, "/workspace/projects/workspace")

@dataclass
class FactorExposure:
    """因子暴露"""
    symbol: str
    date: str
    factors: Dict[str, float]

@dataclass
class FactorIC:
    """因子IC统计"""
    factor_name: str
    ic_mean: float
    ic_std: float
    ic_ir: float
    ic_positive_ratio: float
    t_statistic: float
    p_value: float

class MultiFactorModel:
    """多因子模型"""
    
    # Barra风格因子定义
    BARRA_FACTORS = {
        # 规模因子
        "size": "市值对数",
        "size_nonlinear": "市值非线性",
        
        # 价值因子
        "book_to_price": "账面市值比",
        "earnings_to_price": "盈利市值比",
        "sales_to_price": "营收市值比",
        "cash_to_price": "现金流市值比",
        "dividend_yield": "股息率",
        
        # 成长因子
        "earnings_growth": "盈利增长",
        "sales_growth": "营收增长",
        "profit_margin": "利润率",
        
        # 质量因子
        "roe": "净资产收益率",
        "roa": "总资产收益率",
        "debt_to_equity": "负债权益比",
        "current_ratio": "流动比率",
        
        # 动量因子
        "momentum_1m": "1个月动量",
        "momentum_3m": "3个月动量",
        "momentum_6m": "6个月动量",
        "momentum_12m": "12个月动量",
        
        # 波动因子
        "volatility_1m": "1个月波动率",
        "volatility_3m": "3个月波动率",
        "beta": "贝塔系数",
        "max_drawdown_6m": "6个月最大回撤",
        
        # 流动性因子
        "turnover_1m": "1个月换手率",
        "turnover_3m": "3个月换手率",
        "volume_ratio": "量比",
        "amihud_illiquidity": "Amihud非流动性",
        
        # 技术因子
        "rsi_14": "RSI(14)",
        "macd": "MACD",
        "bollinger_position": "布林带位置"
    }
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.factor_data: Dict[str, pd.DataFrame] = {}
        self.factor_ic: Dict[str, FactorIC] = {}
        
        print("🎯 多因子模型初始化")
        print(f"   Barra因子数量: {len(self.BARRA_FACTORS)}")
    
    def calculate_factors(self, price_data: pd.DataFrame, 
                         fundamentals: pd.DataFrame = None) -> pd.DataFrame:
        """
        计算所有Barra因子
        
        Args:
            price_data: 价格数据
            fundamentals: 基本面数据 (可选)
            
        Returns:
            因子DataFrame
        """
        df = price_data.copy()
        
        # 规模因子
        if 'market_cap' in df.columns:
            df['size'] = np.log(df['market_cap'])
        else:
            df['size'] = 0
        df['size_nonlinear'] = df['size'] ** 2
        
        # 价值因子 (使用价格和模拟数据)
        df['book_to_price'] = 1 / df['close']  # 简化
        df['earnings_to_price'] = df['close'].pct_change(252).fillna(0)  # 简化
        df['sales_to_price'] = df['volume'] / df['close']  # 简化
        
        # 成长因子
        df['earnings_growth'] = df['close'].pct_change(63).fillna(0)  # 季度收益增长近似
        df['sales_growth'] = df['volume'].pct_change(63).fillna(0)
        df['profit_margin'] = (df['close'] - df['close'].shift(1)) / df['close'].shift(1)
        df['profit_margin'] = df['profit_margin'].rolling(63).mean()
        
        # 质量因子
        returns = df['close'].pct_change()
        df['roe'] = returns.rolling(252).mean() * 252  # 简化
        df['roa'] = returns.rolling(252).mean() * 126  # 简化
        
        # 动量因子
        df['momentum_1m'] = df['close'].pct_change(20)
        df['momentum_3m'] = df['close'].pct_change(60)
        df['momentum_6m'] = df['close'].pct_change(120)
        df['momentum_12m'] = df['close'].pct_change(240)
        
        # 波动因子
        df['volatility_1m'] = returns.rolling(20).std() * np.sqrt(252)
        df['volatility_3m'] = returns.rolling(60).std() * np.sqrt(252)
        
        # 计算Beta (相对于市场，这里简化为相对于自身均值)
        market_return = returns.rolling(60).mean()
        covariance = returns.rolling(60).cov(market_return)
        market_variance = market_return.rolling(60).var()
        df['beta'] = covariance / (market_variance + 1e-8)
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        df['max_drawdown_6m'] = drawdown.rolling(120).min()
        
        # 流动性因子
        df['turnover_1m'] = (df['volume'] / df['volume'].rolling(20).mean()).fillna(0)
        df['turnover_3m'] = (df['volume'] / df['volume'].rolling(60).mean()).fillna(0)
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(5).mean()
        
        # Amihud非流动性
        df['amihud_illiquidity'] = (abs(returns) / (df['volume'] + 1)).fillna(0)
        
        # 技术因子
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-8)
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        
        # 布林带位置
        bb_middle = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        bb_upper = bb_middle + 2 * bb_std
        bb_lower = bb_middle - 2 * bb_std
        df['bollinger_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower + 1e-8)
        
        # 选择因子列
        factor_cols = [col for col in df.columns if col in self.BARRA_FACTORS]
        
        return df[factor_cols + ['close']].dropna()
    
    def calculate_ic(self, factor_data: pd.DataFrame, 
                     forward_period: int = 5) -> Dict[str, FactorIC]:
        """
        计算因子IC (信息系数)
        
        Args:
            factor_data: 因子数据
            forward_period: 前瞻期
            
        Returns:
            各因子的IC统计
        """
        print(f"\n{'='*70}")
        print(f"📊 因子IC分析 (前瞻{forward_period}期)")
        print(f"{'='*70}\n")
        
        # 计算未来收益
        factor_data['forward_return'] = factor_data['close'].pct_change(forward_period).shift(-forward_period)
        factor_data = factor_data.dropna()
        
        factor_cols = [col for col in factor_data.columns 
                      if col in self.BARRA_FACTORS and col != 'close']
        
        ic_results = {}
        
        for factor in factor_cols:
            # 计算IC序列 (Spearman秩相关系数)
            ic_series = []
            for i in range(0, len(factor_data) - forward_period, forward_period):
                window = factor_data.iloc[i:i+forward_period]
                if len(window) > 1:
                    ic, _ = stats.spearmanr(
                        window[factor],
                        window['forward_return']
                    )
                    if not np.isnan(ic):
                        ic_series.append(ic)
            
            if len(ic_series) > 0:
                ic_mean = np.mean(ic_series)
                ic_std = np.std(ic_series)
                ic_ir = ic_mean / (ic_std + 1e-8)
                ic_positive_ratio = sum([1 for x in ic_series if x > 0]) / len(ic_series)
                
                # T检验
                t_stat, p_value = stats.ttest_1samp(ic_series, 0)
                
                ic_results[factor] = FactorIC(
                    factor_name=factor,
                    ic_mean=ic_mean,
                    ic_std=ic_std,
                    ic_ir=ic_ir,
                    ic_positive_ratio=ic_positive_ratio,
                    t_statistic=t_stat,
                    p_value=p_value
                )
        
        return ic_results
    
    def select_effective_factors(self, ic_results: Dict[str, FactorIC],
                                 ic_threshold: float = 0.02,
                                 ir_threshold: float = 0.3) -> List[str]:
        """
        选择有效因子
        
        Args:
            ic_results: IC结果
            ic_threshold: IC均值阈值
            ir_threshold: IR阈值
            
        Returns:
            有效因子列表
        """
        effective = []
        
        for factor, ic in ic_results.items():
            # 选择标准: |IC| > 阈值 且 IR > 阈值 且 p值 < 0.05
            if (abs(ic.ic_mean) > ic_threshold and 
                abs(ic.ic_ir) > ir_threshold and 
                ic.p_value < 0.05):
                effective.append(factor)
        
        return effective
    
    def calculate_factor_weights(self, factor_data: pd.DataFrame,
                                  effective_factors: List[str],
                                  method: str = "ic_weighted") -> Dict[str, float]:
        """
        计算因子权重
        
        Args:
            factor_data: 因子数据
            effective_factors: 有效因子列表
            method: 权重方法 (ic_weighted, equal, risk_parity)
            
        Returns:
            因子权重
        """
        if method == "equal":
            # 等权
            weight = 1.0 / len(effective_factors)
            return {f: weight for f in effective_factors}
        
        elif method == "ic_weighted":
            # IC加权
            ic_means = []
            for f in effective_factors:
                if f in self.factor_ic:
                    ic_means.append(abs(self.factor_ic[f].ic_mean))
                else:
                    ic_means.append(0.01)
            
            total_ic = sum(ic_means)
            if total_ic > 0:
                return {f: ic / total_ic for f, ic in zip(effective_factors, ic_means)}
            else:
                weight = 1.0 / len(effective_factors)
                return {f: weight for f in effective_factors}
        
        elif method == "risk_parity":
            # 风险平价 (简化)
            volatilities = []
            for f in effective_factors:
                vol = factor_data[f].std()
                volatilities.append(1.0 / (vol + 1e-8))
            
            total_inv_vol = sum(volatilities)
            return {f: inv_vol / total_inv_vol 
                   for f, inv_vol in zip(effective_factors, volatilities)}
        
        else:
            weight = 1.0 / len(effective_factors)
            return {f: weight for f in effective_factors}
    
    def generate_factor_score(self, factor_data: pd.DataFrame,
                              weights: Dict[str, float]) -> pd.Series:
        """
        生成综合因子得分
        
        Args:
            factor_data: 因子数据
            weights: 因子权重
            
        Returns:
            综合得分
        """
        score = pd.Series(0, index=factor_data.index)
        
        for factor, weight in weights.items():
            if factor in factor_data.columns:
                # 标准化
                factor_std = (factor_data[factor] - factor_data[factor].mean()) / (factor_data[factor].std() + 1e-8)
                score += factor_std * weight
        
        return score
    
    def generate_report(self) -> str:
        """生成因子分析报告"""
        report = f"""# 多因子模型分析报告

## 模型概览

- **因子体系**: Barra风格因子
- **因子数量**: {len(self.BARRA_FACTORS)}
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Barra因子列表

"""
        
        # 分类显示因子
        categories = {
            "规模因子": ["size", "size_nonlinear"],
            "价值因子": ["book_to_price", "earnings_to_price", "sales_to_price", "cash_to_price", "dividend_yield"],
            "成长因子": ["earnings_growth", "sales_growth", "profit_margin"],
            "质量因子": ["roe", "roa", "debt_to_equity", "current_ratio"],
            "动量因子": ["momentum_1m", "momentum_3m", "momentum_6m", "momentum_12m"],
            "波动因子": ["volatility_1m", "volatility_3m", "beta", "max_drawdown_6m"],
            "流动性因子": ["turnover_1m", "turnover_3m", "volume_ratio", "amihud_illiquidity"],
            "技术因子": ["rsi_14", "macd", "bollinger_position"]
        }
        
        for category, factors in categories.items():
            report += f"### {category}\n\n"
            for f in factors:
                if f in self.BARRA_FACTORS:
                    report += f"- **{f}**: {self.BARRA_FACTORS[f]}\n"
            report += "\n"
        
        # IC分析结果
        if self.factor_ic:
            report += "## 因子有效性分析\n\n"
            report += "| 因子 | IC均值 | IC标准差 | IR | 正IC比例 | T统计量 | P值 | 有效性 |\n"
            report += "|------|--------|----------|-----|----------|---------|-----|--------|\n"
            
            for factor, ic in sorted(self.factor_ic.items(), 
                                    key=lambda x: abs(x[1].ic_mean), reverse=True):
                effective = "✅" if abs(ic.ic_mean) > 0.02 and abs(ic.ic_ir) > 0.3 and ic.p_value < 0.05 else "❌"
                report += f"| {factor} | {ic.ic_mean:.4f} | {ic.ic_std:.4f} | {ic.ic_ir:.4f} | {ic.ic_positive_ratio:.2%} | {ic.t_statistic:.4f} | {ic.p_value:.4f} | {effective} |\n"
        
        report += f"""

## 使用说明

### 因子暴露计算
```python
from ARCHITECT_5L.layer6_ml.multi_factor_model import MultiFactorModel

model = MultiFactorModel()
factors = model.calculate_factors(price_data)
```

### 因子有效性检验
```python
ic_results = model.calculate_ic(factor_data)
effective_factors = model.select_effective_factors(ic_results)
```

### 因子权重计算
```python
weights = model.calculate_factor_weights(
    factor_data, 
    effective_factors, 
    method="ic_weighted"
)
```

### 综合得分
```python
score = model.generate_factor_score(factor_data, weights)
```

---

**ARCHITECT-5L Multi-Factor Model** | v1.0
"""
        
        return report

def demo():
    """演示多因子模型"""
    print("="*70)
    print("🎯 多因子模型演示")
    print("="*70)
    print()
    
    # 创建模拟数据
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=500, freq='B')
    
    price = 100
    prices = []
    volumes = []
    for i in range(500):
        trend = 0.0003
        cycle = 0.005 * np.sin(i / 50)
        noise = np.random.normal(0, 0.012)
        price = price * (1 + trend + cycle + noise)
        prices.append(price)
        volumes.append(np.random.randint(1000000, 10000000))
    
    price_data = pd.DataFrame({
        'date': dates,
        'close': prices,
        'open': [p * (1 + np.random.normal(0, 0.003)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'volume': volumes,
        'market_cap': [p * 100000000 for p in prices]  # 模拟市值
    })
    
    # 初始化模型
    model = MultiFactorModel()
    
    # 计算因子
    print("📊 计算Barra因子...")
    factors = model.calculate_factors(price_data)
    print(f"   因子数量: {len([c for c in factors.columns if c != 'close'])}")
    print(f"   数据长度: {len(factors)}")
    print()
    
    # IC分析
    print("🔍 因子IC分析...")
    model.factor_ic = model.calculate_ic(factors, forward_period=5)
    
    # 显示IC结果
    print("\n因子IC统计:")
    print("-"*70)
    for factor, ic in sorted(model.factor_ic.items(), 
                            key=lambda x: abs(x[1].ic_mean), reverse=True)[:10]:
        effective = "✅" if abs(ic.ic_mean) > 0.02 and abs(ic.ic_ir) > 0.3 else "❌"
        print(f"   {factor:20s} IC={ic.ic_mean:+.4f} IR={ic.ic_ir:.4f} {effective}")
    print()
    
    # 选择有效因子
    effective_factors = model.select_effective_factors(model.factor_ic)
    print(f"✅ 有效因子数量: {len(effective_factors)}")
    if effective_factors:
        print(f"   {', '.join(effective_factors[:5])}")
    print()
    
    # 计算权重
    if effective_factors:
        print("⚖️ 计算因子权重 (IC加权)...")
        weights = model.calculate_factor_weights(factors, effective_factors, method="ic_weighted")
        
        print("\n因子权重:")
        for factor, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            print(f"   {factor}: {weight:.2%}")
        print()
        
        # 生成综合得分
        print("🎯 生成综合因子得分...")
        score = model.generate_factor_score(factors, weights)
        print(f"   得分均值: {score.mean():.4f}")
        print(f"   得分标准差: {score.std():.4f}")
    
    print()
    print("="*70)
    print("✅ 多因子模型演示完成!")
    print("="*70)

if __name__ == "__main__":
    demo()
