#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习管道 (ML Pipeline)
整合LSTM和XGBoost的统一接口

功能:
- 模型训练管理
- 预测结果整合
- 模型评估对比
- 自动模型选择
"""

import numpy as np
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, "/workspace/projects/workspace")
sys.path.insert(0, "/workspace/projects/workspace/ARCHITECT_5L/layer6_ml")

# 导入模型
from lstm_predictor import LSTMPredictor, TORCH_AVAILABLE
from xgboost_classifier import XGBoostClassifier, XGB_AVAILABLE

class MLPipeline:
    """机器学习管道"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.models = {
            'lstm': LSTMPredictor(workspace),
            'xgboost': XGBoostClassifier(workspace)
        }
        self.model_performance = {}
        
        print("🤖 ML Pipeline初始化")
        print(f"   LSTM可用: {TORCH_AVAILABLE}")
        print(f"   XGBoost可用: {XGB_AVAILABLE}")
    
    def train_all_models(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> Dict:
        """
        训练所有模型
        
        Args:
            df: 训练数据
            symbol: 股票代码
            
        Returns:
            各模型训练结果
        """
        print(f"\n{'='*70}")
        print(f"🚀 训练所有ML模型: {symbol}")
        print(f"{'='*70}\n")
        
        results = {}
        
        # 训练LSTM
        print("📊 1. LSTM价格预测模型")
        print("-"*70)
        try:
            lstm_result = self.models['lstm'].train(df, epochs=30, batch_size=16)
            results['lstm'] = lstm_result
            if lstm_result['status'] == 'success':
                self.model_performance['lstm'] = lstm_result.get('best_val_loss', float('inf'))
        except Exception as e:
            print(f"⚠️ LSTM训练失败: {e}")
            results['lstm'] = {'status': 'error', 'message': str(e)}
        
        print()
        
        # 训练XGBoost
        print("📊 2. XGBoost涨跌分类模型")
        print("-"*70)
        try:
            xgb_result = self.models['xgboost'].train(df, prediction_horizon=5)
            results['xgboost'] = xgb_result
            if xgb_result['status'] == 'success':
                # 使用F1分数作为性能指标
                self.model_performance['xgboost'] = 1 - xgb_result['metrics'].get('f1', 0)
        except Exception as e:
            print(f"⚠️ XGBoost训练失败: {e}")
            results['xgboost'] = {'status': 'error', 'message': str(e)}
        
        # 保存训练结果
        self._save_training_results(symbol, results)
        
        return results
    
    def predict(self, recent_data: pd.DataFrame, days: int = 5) -> Dict:
        """
        综合预测
        
        Args:
            recent_data: 最近的历史数据
            days: 预测天数
            
        Returns:
            综合预测结果
        """
        predictions = {
            'timestamp': datetime.now().isoformat(),
            'models': {}
        }
        
        # LSTM预测
        try:
            lstm_pred = self.models['lstm'].predict(recent_data, days=days)
            predictions['models']['lstm'] = {
                'status': 'success',
                'prices': lstm_pred
            }
        except Exception as e:
            predictions['models']['lstm'] = {
                'status': 'error',
                'message': str(e)
            }
        
        # XGBoost预测
        try:
            xgb_pred = self.models['xgboost'].predict(recent_data)
            predictions['models']['xgboost'] = xgb_pred
        except Exception as e:
            predictions['models']['xgboost'] = {
                'status': 'error',
                'message': str(e)
            }
        
        # 综合判断
        predictions['ensemble'] = self._ensemble_prediction(predictions['models'])
        
        return predictions
    
    def _ensemble_prediction(self, model_predictions: Dict) -> Dict:
        """集成预测 (简单投票)"""
        votes = []
        confidences = []
        
        # XGBoost投票
        if 'xgboost' in model_predictions and model_predictions['xgboost'].get('status') == 'success':
            pred = model_predictions['xgboost']
            if pred['prediction'] == '上涨':
                votes.append(1)
            else:
                votes.append(0)
            confidences.append(pred['confidence'])
        
        # LSTM投票 (基于价格趋势)
        if 'lstm' in model_predictions and model_predictions['lstm'].get('status') == 'success':
            prices = model_predictions['lstm'].get('prices', [])
            if len(prices) >= 2 and prices[-1] > prices[0]:
                votes.append(1)
            else:
                votes.append(0)
            confidences.append(0.6)  # LSTM默认置信度
        
        if not votes:
            return {'status': 'error', 'message': '没有可用预测'}
        
        # 加权投票
        avg_vote = np.average(votes, weights=confidences)
        avg_confidence = np.mean(confidences)
        
        return {
            'status': 'success',
            'prediction': '上涨' if avg_vote > 0.5 else '下跌',
            'confidence': avg_confidence,
            'up_probability': avg_vote,
            'down_probability': 1 - avg_vote,
            'models_used': len(votes)
        }
    
    def backtest(self, df: pd.DataFrame, train_size: float = 0.8) -> Dict:
        """
        回测模型
        
        Args:
            df: 历史数据
            train_size: 训练集比例
            
        Returns:
            回测结果
        """
        print(f"\n{'='*70}")
        print("📈 ML模型回测")
        print(f"{'='*70}\n")
        
        split_idx = int(len(df) * train_size)
        train_data = df.iloc[:split_idx]
        test_data = df.iloc[split_idx:]
        
        print(f"训练集: {len(train_data)}条, 测试集: {len(test_data)}条")
        
        # 训练模型
        self.train_all_models(train_data)
        
        # 在测试集上预测
        predictions = []
        actuals = []
        
        # 滑动窗口预测
        window_size = 60
        for i in range(window_size, len(test_data)):
            window = test_data.iloc[i-window_size:i]
            pred = self.predict(window, days=1)
            
            if pred['ensemble'].get('status') == 'success':
                predictions.append(1 if pred['ensemble']['prediction'] == '上涨' else 0)
                actual_return = (test_data['close'].iloc[i] / test_data['close'].iloc[i-1]) - 1
                actuals.append(1 if actual_return > 0 else 0)
        
        # 计算回测指标
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        if len(predictions) > 0:
            backtest_metrics = {
                'accuracy': accuracy_score(actuals, predictions),
                'precision': precision_score(actuals, predictions, zero_division=0),
                'recall': recall_score(actuals, predictions, zero_division=0),
                'f1': f1_score(actuals, predictions, zero_division=0),
                'total_predictions': len(predictions),
                'correct_predictions': sum([1 for p, a in zip(predictions, actuals) if p == a])
            }
            
            print(f"\n回测结果:")
            print(f"   预测次数: {backtest_metrics['total_predictions']}")
            print(f"   正确次数: {backtest_metrics['correct_predictions']}")
            print(f"   准确率: {backtest_metrics['accuracy']:.4f}")
            print(f"   F1分数: {backtest_metrics['f1']:.4f}")
        else:
            backtest_metrics = {'status': 'error', 'message': '预测失败'}
        
        return backtest_metrics
    
    def _save_training_results(self, symbol: str, results: Dict):
        """保存训练结果"""
        results_dir = f"{self.workspace}/data/ml_results"
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"{results_dir}/training_{symbol}_{timestamp}.json"
        
        with open(filepath, 'w') as f:
            json.dump({
                'symbol': symbol,
                'timestamp': timestamp,
                'results': results
            }, f, indent=2, default=str)
        
        print(f"\n💾 训练结果已保存: {filepath}")
    
    def generate_report(self, symbol: str) -> str:
        """生成ML报告"""
        report = f"""# 🤖 机器学习模型报告

**股票代码**: {symbol}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 模型状态

| 模型 | 状态 | 性能 |
|------|------|------|
| LSTM价格预测 | {'✅ 已训练' if 'lstm' in self.model_performance else '❌ 未训练'} | {'N/A' if 'lstm' not in self.model_performance else f"Val Loss: {self.model_performance['lstm']:.4f}"} |
| XGBoost分类 | {'✅ 已训练' if 'xgboost' in self.model_performance else '❌ 未训练'} | {'N/A' if 'xgboost' not in self.model_performance else f"F1: {1-self.model_performance['xgboost']:.4f}"} |

---

## 🎯 使用说明

### LSTM价格预测
```python
predictions = ml_pipeline.models['lstm'].predict(data, days=5)
```

### XGBoost涨跌分类
```python
result = ml_pipeline.models['xgboost'].predict(data)
# result: {'prediction': '上涨', 'confidence': 0.75}
```

### 集成预测
```python
result = ml_pipeline.predict(data)
# 综合LSTM和XGBoost的结果
```

---

## 📁 文件位置

- 模型文件: `data/ml_models/`
- 训练结果: `data/ml_results/`

---

**ARCHITECT-5L ML Pipeline** | v1.0
"""
        
        return report

def demo():
    """演示ML Pipeline"""
    print("="*70)
    print("🤖 ML Pipeline演示")
    print("="*70)
    print()
    
    # 创建模拟数据
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=300, freq='B')
    
    price = 100
    prices = []
    for i in range(300):
        trend = 0.0005
        cycle = 0.01 * np.sin(i / 30)
        noise = np.random.normal(0, 0.015)
        price = price * (1 + trend + cycle + noise)
        prices.append(price)
    
    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.015))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.015))) for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 300)
    })
    
    print(f"📊 模拟数据: {len(df)} 条记录")
    print()
    
    # 初始化Pipeline
    pipeline = MLPipeline()
    
    # 训练所有模型
    results = pipeline.train_all_models(df, symbol="DEMO")
    
    # 预测
    print(f"\n{'='*70}")
    print("🔮 集成预测")
    print(f"{'='*70}\n")
    
    predictions = pipeline.predict(df, days=5)
    
    if predictions['ensemble'].get('status') == 'success':
        ensemble = predictions['ensemble']
        print(f"综合预测结果:")
        print(f"   方向: {ensemble['prediction']}")
        print(f"   置信度: {ensemble['confidence']:.2%}")
        print(f"   上涨概率: {ensemble['up_probability']:.2%}")
        print(f"   模型数量: {ensemble['models_used']}")
    
    # 生成报告
    print(f"\n{'='*70}")
    print("✅ ML Pipeline演示完成!")
    print(f"{'='*70}")

if __name__ == "__main__":
    demo()
