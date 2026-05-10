#!/usr/bin/env python3
"""
CIO觉醒系统 - 优化版ML训练器
集成XGBoost + LSTM + Ensemble模型
"""
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML库
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib

# TensorFlow/Keras for LSTM
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, Model, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Input, Concatenate
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
    from tensorflow.keras.optimizers import Adam
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️ TensorFlow未安装，LSTM模型不可用")

class CIOMLTrainer:
    """CIO ML模型训练器"""
    
    def __init__(self, model_dir='models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.models = {}
        self.scalers = {}
        self.metrics = {}
        
    def prepare_features(self, df):
        """特征工程 - 生成技术指标"""
        data = df.copy()
        
        # 价格特征
        data['returns'] = data['close'].pct_change()
        data['log_returns'] = np.log(data['close'] / data['close'].shift(1))
        
        # 移动平均线
        for window in [5, 10, 20, 60]:
            data[f'ma_{window}'] = data['close'].rolling(window=window).mean()
            data[f'ma_ratio_{window}'] = data['close'] / data[f'ma_{window}']
        
        # 波动率
        for window in [5, 20]:
            data[f'volatility_{window}'] = data['returns'].rolling(window=window).std()
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = data['close'].ewm(span=12, adjust=False).mean()
        ema_26 = data['close'].ewm(span=26, adjust=False).mean()
        data['macd'] = ema_12 - ema_26
        data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
        data['macd_hist'] = data['macd'] - data['macd_signal']
        
        # 成交量特征
        data['volume_ma_5'] = data['volume'].rolling(window=5).mean()
        data['volume_ratio'] = data['volume'] / data['volume_ma_5']
        
        # 高低价特征
        data['high_low_ratio'] = (data['high'] - data['low']) / data['close']
        data['close_open_ratio'] = (data['close'] - data['open']) / data['open']
        
        # 目标变量 - 未来1日涨跌
        data['target'] = (data['close'].shift(-1) > data['close']).astype(int)
        
        # 删除NaN
        data = data.dropna()
        
        return data
    
    def train_xgboost(self, X_train, y_train, X_test, y_test, feature_names):
        """训练XGBoost模型"""
        print("\n🚀 训练XGBoost模型...")
        
        # 基础模型
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # 评估
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        
        print(f"   训练集准确率: {train_acc:.2%}")
        print(f"   测试集准确率: {test_acc:.2%}")
        
        # 特征重要性
        importance = pd.DataFrame({
            'feature': feature_names,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n   Top 5 重要特征:")
        for idx, row in importance.head(5).iterrows():
            print(f"   - {row['feature']}: {row['importance']:.3f}")
        
        # 保存
        model_path = os.path.join(self.model_dir, 'xgboost_model.pkl')
        joblib.dump(model, model_path)
        
        self.models['xgboost'] = model
        self.metrics['xgboost'] = {
            'train_acc': train_acc,
            'test_acc': test_acc,
            'feature_importance': importance.head(10).to_dict('records')
        }
        
        return model
    
    def train_lstm(self, X_train, y_train, X_test, y_test, seq_length=10):
        """训练LSTM模型"""
        if not TF_AVAILABLE:
            print("\n⚠️ 跳过LSTM训练（TensorFlow未安装）")
            return None
        
        print("\n🧠 训练LSTM模型...")
        
        # 构建序列数据
        def create_sequences(X, y, seq_length):
            X_seq, y_seq = [], []
            for i in range(len(X) - seq_length):
                X_seq.append(X[i:i+seq_length])
                y_seq.append(y[i+seq_length])
            return np.array(X_seq), np.array(y_seq)
        
        X_train_seq, y_train_seq = create_sequences(X_train, y_train, seq_length)
        X_test_seq, y_test_seq = create_sequences(X_test, y_test, seq_length)
        
        # 构建LSTM模型
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(seq_length, X_train.shape[1])),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # 回调
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(factor=0.5, patience=5)
        ]
        
        # 训练
        history = model.fit(
            X_train_seq, y_train_seq,
            validation_split=0.2,
            epochs=50,
            batch_size=32,
            callbacks=callbacks,
            verbose=0
        )
        
        # 评估
        train_loss, train_acc = model.evaluate(X_train_seq, y_train_seq, verbose=0)
        test_loss, test_acc = model.evaluate(X_test_seq, y_test_seq, verbose=0)
        
        print(f"   训练集准确率: {train_acc:.2%}")
        print(f"   测试集准确率: {test_acc:.2%}")
        
        # 保存
        model_path = os.path.join(self.model_dir, 'lstm_model.h5')
        model.save(model_path)
        
        self.models['lstm'] = model
        self.metrics['lstm'] = {
            'train_acc': train_acc,
            'test_acc': test_acc,
            'train_loss': train_loss,
            'test_loss': test_loss
        }
        
        return model
    
    def train_ensemble(self, X_train, y_train, X_test, y_test):
        """训练集成模型"""
        print("\n🎯 训练集成模型...")
        
        # 获取各模型预测
        xgb_pred = self.models['xgboost'].predict_proba(X_test)[:, 1]
        
        if 'lstm' in self.models and TF_AVAILABLE:
            seq_length = 10
            X_test_seq = []
            for i in range(len(X_test) - seq_length):
                X_test_seq.append(X_test[i:i+seq_length])
            X_test_seq = np.array(X_test_seq)
            lstm_pred = self.models['lstm'].predict(X_test_seq, verbose=0).flatten()
            # 补齐长度
            lstm_pred = np.pad(lstm_pred, (seq_length, 0), mode='edge')
        else:
            lstm_pred = xgb_pred  # 如果没有LSTM，只用XGBoost
        
        # 简单加权融合
        weights = {'xgb': 0.6, 'lstm': 0.4}
        ensemble_pred = weights['xgb'] * xgb_pred + weights['lstm'] * lstm_pred[:len(xgb_pred)]
        ensemble_label = (ensemble_pred > 0.5).astype(int)
        
        acc = accuracy_score(y_test[:len(ensemble_label)], ensemble_label)
        print(f"   集成模型准确率: {acc:.2%}")
        print(f"   权重: XGBoost {weights['xgb']*100:.0f}% + LSTM {weights['lstm']*100:.0f}%")
        
        self.metrics['ensemble'] = {
            'test_acc': acc,
            'weights': weights
        }
        
        return ensemble_pred
    
    def train_all(self, df):
        """训练所有模型"""
        print("=" * 60)
        print("🚀 CIO ML模型训练 - 优化版")
        print("=" * 60)
        
        # 特征工程
        print("\n📊 执行特征工程...")
        data = self.prepare_features(df)
        print(f"   样本数量: {len(data)}")
        print(f"   特征数量: {len(data.columns) - 1}")
        
        # 准备特征和标签
        feature_cols = [col for col in data.columns if col not in ['target', 'date']]
        X = data[feature_cols].values
        y = data['target'].values
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['standard'] = scaler
        
        # 保存特征名
        self.feature_names = feature_cols
        joblib.dump(feature_cols, os.path.join(self.model_dir, 'feature_names.pkl'))
        
        # 划分数据集
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, shuffle=False
        )
        
        print(f"\n   训练集: {len(X_train)} 样本")
        print(f"   测试集: {len(X_test)} 样本")
        
        # 训练各模型
        self.train_xgboost(X_train, y_train, X_test, y_test, feature_cols)
        
        if TF_AVAILABLE:
            self.train_lstm(X_train, y_train, X_test, y_test)
        
        self.train_ensemble(X_train, y_train, X_test, y_test)
        
        # 保存指标
        self.save_metrics()
        
        return self.metrics
    
    def save_metrics(self):
        """保存训练指标"""
        metrics_path = os.path.join(self.model_dir, 'training_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'metrics': self.metrics
            }, f, indent=2)
        print(f"\n💾 指标已保存: {metrics_path}")
    
    def predict(self, X_new):
        """使用集成模型预测"""
        # 加载模型
        if 'xgboost' not in self.models:
            model_path = os.path.join(self.model_dir, 'xgboost_model.pkl')
            if os.path.exists(model_path):
                self.models['xgboost'] = joblib.load(model_path)
        
        if not self.models:
            raise ValueError("没有可用的模型")
        
        # 标准化
        if 'standard' in self.scalers:
            X_scaled = self.scalers['standard'].transform(X_new)
        else:
            X_scaled = X_new
        
        # 预测
        xgb_pred = self.models['xgboost'].predict_proba(X_scaled)[:, 1]
        
        # 生成信号
        signals = []
        for pred in xgb_pred:
            if pred > 0.65:
                signals.append('STRONG_BUY')
            elif pred > 0.55:
                signals.append('BUY')
            elif pred < 0.35:
                signals.append('SELL')
            else:
                signals.append('HOLD')
        
        return signals, xgb_pred


def main():
    """主函数 - 生成模拟数据并训练"""
    print("🧠 CIO觉醒系统 - ML优化训练器\n")
    
    # 生成模拟K线数据
    np.random.seed(42)
    n_days = 252 * 2  # 2年数据
    
    dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')
    
    # 模拟股价
    price = 100
    prices = []
    for _ in range(n_days):
        change = np.random.normal(0.001, 0.02)  # 日均收益0.1%，波动2%
        price *= (1 + change)
        prices.append(price)
    
    # 构建DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': [int(np.random.randint(1000000, 10000000)) for _ in range(n_days)]
    })
    
    # 确保high >= low
    df['high'] = np.maximum(df['high'], df[['open', 'close']].max(axis=1) * 1.01)
    df['low'] = np.minimum(df['low'], df[['open', 'close']].min(axis=1) * 0.99)
    
    print(f"📊 生成模拟数据: {len(df)} 条K线")
    print(f"   日期范围: {df['date'].min()} ~ {df['date'].max()}")
    
    # 训练模型
    trainer = CIOMLTrainer(model_dir='/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/models')
    metrics = trainer.train_all(df)
    
    # 输出总结
    print("\n" + "=" * 60)
    print("🎉 模型训练完成!")
    print("=" * 60)
    print("\n📈 模型性能:")
    for model_name, model_metrics in metrics.items():
        if 'test_acc' in model_metrics:
            print(f"   • {model_name}: {model_metrics['test_acc']:.2%}")
    
    print("\n💾 模型保存位置:")
    print(f"   /workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/models/")
    
    return trainer


if __name__ == "__main__":
    trainer = main()
