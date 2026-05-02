#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XGBoost涨跌分类模型
用于预测股票涨跌方向

功能:
- 特征工程 (技术指标、统计特征)
- XGBoost分类器
- 模型评估 (准确率、召回率、F1)
- 特征重要性分析
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

# 尝试导入XGBoost
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("⚠️ XGBoost未安装，将使用模拟模式")

sys.path.insert(0, "/workspace/projects/workspace")

class FeatureEngineer:
    """特征工程器"""
    
    def __init__(self):
        self.feature_names = []
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建技术指标特征
        
        Args:
            df: 股票数据，包含open/high/low/close/volume
            
        Returns:
            添加了特征的DataFrame
        """
        df = df.copy()
        
        # 价格特征
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # 移动平均线
        for window in [5, 10, 20, 60]:
            df[f'ma_{window}'] = df['close'].rolling(window=window).mean()
            df[f'ma_ratio_{window}'] = df['close'] / df[f'ma_{window}']
        
        # 波动率
        for window in [5, 20]:
            df[f'volatility_{window}'] = df['returns'].rolling(window=window).std()
        
        # 价格位置
        df['high_low_ratio'] = (df['close'] - df['low']) / (df['high'] - df['low'] + 1e-8)
        
        # 成交量特征
        df['volume_ma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma_20']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-8)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # 布林带
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + 2 * bb_std
        df['bb_lower'] = df['bb_middle'] - 2 * bb_std
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'] + 1e-8)
        
        # 统计特征
        for window in [5, 10, 20]:
            df[f'skew_{window}'] = df['returns'].rolling(window=window).skew()
            df[f'kurt_{window}'] = df['returns'].rolling(window=window).kurt()
        
        self.feature_names = [col for col in df.columns if col not in ['date', 'open', 'high', 'low', 'close', 'volume']]
        
        return df.dropna()
    
    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性 (需要训练后调用)"""
        return {}

class XGBoostClassifier:
    """XGBoost涨跌分类器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.feature_names = []
        
        print(f"🚀 XGBoost分类器初始化")
    
    def prepare_data(self, df: pd.DataFrame, prediction_horizon: int = 5) -> Tuple[pd.DataFrame, pd.Series]:
        """
        准备训练和测试数据
        
        Args:
            df: 股票数据
            prediction_horizon: 预测周期 (几天后涨跌)
            
        Returns:
            (特征DataFrame, 标签Series)
        """
        # 特征工程
        df_features = self.feature_engineer.create_features(df)
        self.feature_names = self.feature_engineer.feature_names
        
        # 创建标签 (未来N天涨跌)
        future_returns = df_features['close'].shift(-prediction_horizon) / df_features['close'] - 1
        df_features['target'] = (future_returns > 0).astype(int)
        
        # 删除缺失值
        df_clean = df_features.dropna()
        
        X = df_clean[self.feature_names]
        y = df_clean['target']
        
        return X, y
    
    def train(self, df: pd.DataFrame, prediction_horizon: int = 5,
              test_size: float = 0.2) -> Dict:
        """
        训练模型
        
        Args:
            df: 训练数据
            prediction_horizon: 预测周期
            test_size: 测试集比例
            
        Returns:
            训练结果
        """
        print(f"🎯 开始训练XGBoost分类器...")
        print(f"   预测周期: {prediction_horizon}天")
        
        # 准备数据
        X, y = self.prepare_data(df, prediction_horizon)
        
        if len(X) < 100:
            print("⚠️ 数据量不足")
            return {"status": "error", "message": "数据量不足"}
        
        # 划分训练集和测试集
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        print(f"   训练样本: {len(X_train)}, 测试样本: {len(X_test)}")
        print(f"   特征数量: {len(self.feature_names)}")
        
        if XGB_AVAILABLE:
            # 使用XGBoost
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
            
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                early_stopping_rounds=10,
                verbose=False
            )
            
            # 预测
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            
        else:
            # 模拟模式
            print("   使用模拟模式 (随机预测)")
            y_pred = np.random.randint(0, 2, len(y_test))
            y_pred_proba = np.random.uniform(0, 1, len(y_test))
        
        # 计算指标
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "auc": roc_auc_score(y_test, y_pred_proba) if len(set(y_test)) > 1 else 0.5
        }
        
        print(f"\n📊 模型评估结果:")
        print(f"   准确率 (Accuracy): {metrics['accuracy']:.4f}")
        print(f"   精确率 (Precision): {metrics['precision']:.4f}")
        print(f"   召回率 (Recall): {metrics['recall']:.4f}")
        print(f"   F1分数: {metrics['f1']:.4f}")
        print(f"   AUC: {metrics['auc']:.4f}")
        
        # 特征重要性
        if XGB_AVAILABLE and self.model is not None:
            importance = self.model.feature_importances_
            feature_importance = dict(zip(self.feature_names, importance))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            
            print(f"\n🔝 Top 10 重要特征:")
            for feat, imp in top_features:
                print(f"   {feat}: {imp:.4f}")
        
        return {
            "status": "success",
            "metrics": metrics,
            "feature_count": len(self.feature_names),
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        }
    
    def predict(self, recent_data: pd.DataFrame) -> Dict:
        """
        预测涨跌
        
        Args:
            recent_data: 最近的历史数据
            
        Returns:
            预测结果
        """
        # 特征工程
        df_features = self.feature_engineer.create_features(recent_data)
        
        if len(df_features) < 1:
            return {"status": "error", "message": "数据不足"}
        
        # 取最后一天
        X = df_features[self.feature_names].iloc[-1:]
        
        if XGB_AVAILABLE and self.model is not None:
            prediction = self.model.predict(X)[0]
            probability = self.model.predict_proba(X)[0]
        else:
            prediction = np.random.randint(0, 2)
            probability = [0.5, 0.5] if prediction == 1 else [0.5, 0.5]
        
        return {
            "status": "success",
            "prediction": "上涨" if prediction == 1 else "下跌",
            "confidence": max(probability),
            "up_probability": probability[1] if len(probability) > 1 else 0.5,
            "down_probability": probability[0] if len(probability) > 1 else 0.5
        }
    
    def save_model(self, filepath: str = None):
        """保存模型"""
        if filepath is None:
            filepath = f"{self.workspace}/data/ml_models/xgb_classifier.json"
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if XGB_AVAILABLE and self.model is not None:
            self.model.save_model(filepath)
            
            # 保存特征名
            meta_path = filepath.replace('.json', '_meta.json')
            with open(meta_path, 'w') as f:
                json.dump({
                    'feature_names': self.feature_names,
                    'timestamp': datetime.now().isoformat()
                }, f)
            
            print(f"💾 模型已保存: {filepath}")
    
    def load_model(self, filepath: str = None):
        """加载模型"""
        if not XGB_AVAILABLE:
            return False
        
        if filepath is None:
            filepath = f"{self.workspace}/data/ml_models/xgb_classifier.json"
        
        if not os.path.exists(filepath):
            print(f"⚠️ 模型文件不存在: {filepath}")
            return False
        
        self.model = xgb.XGBClassifier()
        self.model.load_model(filepath)
        
        # 加载特征名
        meta_path = filepath.replace('.json', '_meta.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
                self.feature_names = meta.get('feature_names', [])
        
        print(f"📂 模型已加载: {filepath}")
        return True

def demo():
    """演示XGBoost分类器"""
    print("="*70)
    print("🚀 XGBoost涨跌分类模型演示")
    print("="*70)
    print()
    
    # 创建模拟数据
    np.random.seed(42)
    dates = pd.date_range(start='2025-01-01', periods=500, freq='B')
    
    # 生成模拟股票数据
    price = 100
    prices = []
    for i in range(500):
        # 添加一些趋势和周期
        trend = 0.0005
        cycle = 0.01 * np.sin(i / 50)
        noise = np.random.normal(0, 0.015)
        price = price * (1 + trend + cycle + noise)
        prices.append(price)
    
    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.015))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.015))) for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, 500)
    })
    
    print(f"📊 模拟数据: {len(df)} 条记录")
    print(f"   生成特征...")
    
    # 初始化分类器
    classifier = XGBoostClassifier()
    
    # 查看生成的特征
    df_features = classifier.feature_engineer.create_features(df)
    print(f"   原始特征: 5个 (open/high/low/close/volume)")
    print(f"   工程特征: {len(classifier.feature_engineer.feature_names)}个")
    print(f"   总特征: {len(df_features.columns)}个")
    print()
    
    # 训练模型
    print("🎯 训练XGBoost分类器...")
    result = classifier.train(df, prediction_horizon=5)
    print()
    
    # 预测
    print("🔮 预测未来5天涨跌...")
    prediction = classifier.predict(df)
    
    if prediction['status'] == 'success':
        print(f"   预测结果: {prediction['prediction']}")
        print(f"   置信度: {prediction['confidence']:.2%}")
        print(f"   上涨概率: {prediction['up_probability']:.2%}")
        print(f"   下跌概率: {prediction['down_probability']:.2%}")
    
    print()
    print("="*70)
    print("✅ XGBoost分类模型演示完成!")
    print("="*70)

if __name__ == "__main__":
    demo()
