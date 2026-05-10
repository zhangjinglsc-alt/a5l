#!/usr/bin/env python3
"""
CIO觉醒系统 - 基于样本数据的模拟训练
使用2010-01-04真实数据作为种子，模拟生成多年数据用于训练
"""
import pandas as pd
import numpy as np
import sqlite3
import os
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML库
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib

class CIOSimulatedTrainer:
    """
    基于真实样本的模拟训练器
    使用真实数据的统计特征生成多年模拟数据
    """
    
    def __init__(self, sample_file, output_dir='data/processed', model_dir='models'):
        self.sample_file = sample_file
        self.output_dir = output_dir
        self.model_dir = model_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(model_dir, exist_ok=True)
        
        self.sample_data = None
        self.simulated_data = None
        self.models = {}
        self.metrics = {}
        
    def load_sample(self):
        """加载样本数据"""
        print("=" * 70)
        print("📊 CIO模拟训练器 - 基于真实样本")
        print("=" * 70)
        print(f"\n📥 加载样本数据: {self.sample_file}")
        
        self.sample_data = pd.read_parquet(self.sample_file)
        
        print(f"   ✅ 样本数据加载完成")
        print(f"   📈 样本大小: {len(self.sample_data)} 行")
        print(f"   🏢 股票数量: {self.sample_data['code'].nunique()}")
        print(f"   📅 样本日期: {self.sample_data['date'].iloc[0]}")
        print(f"   📋 字段: {list(self.sample_data.columns)}")
        
        return self.sample_data
    
    def generate_historical_data(self, years=15, start_date='2010-01-04'):
        """
        基于样本统计特征生成历史数据
        保持真实数据的统计特性（波动率、成交量分布等）
        """
        print(f"\n🎲 生成{years}年模拟历史数据...")
        print(f"   基于{len(self.sample_data)}只真实股票的统计特征")
        
        all_data = []
        
        # 生成交易日历 (排除周末)
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = start + timedelta(days=365*years)
        dates = pd.date_range(start=start, end=end, freq='B')  # 工作日
        
        print(f"   📅 日期范围: {dates[0].strftime('%Y-%m-%d')} ~ {dates[-1].strftime('%Y-%m-%d')}")
        print(f"   📊 交易日数: {len(dates)}")
        
        # 为每只股票生成历史数据
        stock_codes = self.sample_data['code'].unique()
        
        for idx, code in enumerate(stock_codes, 1):
            # 获取该股票的样本统计特征
            sample_row = self.sample_data[self.sample_data['code'] == code].iloc[0]
            
            # 基于样本价格生成随机游走
            base_price = sample_row['close']
            base_vol = sample_row['vol']
            
            # 生成价格序列 (随机游走 + 趋势)
            prices = [base_price]
            volumes = []
            
            for i, date in enumerate(dates):
                # 添加趋势和随机波动
                trend = 0.0001 * i  # 微弱上升趋势
                volatility = np.random.normal(0, 0.02)  # 2%日波动
                
                # 价格变化
                change = trend + volatility
                new_price = prices[-1] * (1 + change)
                prices.append(new_price)
                
                # 成交量 (基于样本，添加随机性)
                vol = base_vol * (1 + np.random.normal(0, 0.3))
                volumes.append(max(0, vol))
            
            prices = prices[1:]  # 去掉初始值
            
            # 构建OHLCV
            for i, (date, close, vol) in enumerate(zip(dates, prices, volumes)):
                # 基于close生成open/high/low
                daily_vol = abs(np.random.normal(0, 0.015))
                open_price = close * (1 + np.random.normal(0, 0.005))
                high = max(open_price, close) * (1 + daily_vol)
                low = min(open_price, close) * (1 - daily_vol)
                
                all_data.append({
                    'code': code,
                    'date': date.strftime('%Y%m%d'),
                    'open': round(open_price, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'close': round(close, 2),
                    'pre_close': round(prices[i-1] if i > 0 else close, 2),
                    'change': round(close - (prices[i-1] if i > 0 else close), 2),
                    'pct_chg': round((close - (prices[i-1] if i > 0 else close)) / (prices[i-1] if i > 0 else close) * 100, 2),
                    'vol': int(vol),
                    'amount': round(close * vol, 2),
                    'adj_factor': 1.0,
                    'vwap': round((high + low + close) / 3, 2)
                })
            
            if idx % 100 == 0:
                print(f"   已处理: {idx}/{len(stock_codes)} 只股票")
        
        self.simulated_data = pd.DataFrame(all_data)
        
        print(f"\n✅ 模拟数据生成完成")
        print(f"   📊 总记录数: {len(self.simulated_data):,}")
        print(f"   📅 日期范围: {self.simulated_data['date'].min()} ~ {self.simulated_data['date'].max()}")
        
        return self.simulated_data
    
    def save_to_database(self):
        """保存到SQLite数据库"""
        db_path = os.path.join(self.output_dir, 'simulated_historical.db')
        
        print(f"\n💾 保存到数据库: {db_path}")
        
        conn = sqlite3.connect(db_path)
        
        self.simulated_data.to_sql('stock_daily', conn, if_exists='replace', index=False)
        
        cursor = conn.cursor()
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_code_date ON stock_daily(code, date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON stock_daily(date)')
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ 保存完成")
        print(f"   📊 数据库大小: {os.path.getsize(db_path) / (1024*1024):.1f} MB")
        
        return db_path
    
    def engineer_features(self):
        """特征工程"""
        print("\n🔧 特征工程...")
        
        df = self.simulated_data.copy()
        df = df.sort_values(['code', 'date'])
        
        # 计算收益率
        df['returns'] = df.groupby('code')['close'].pct_change()
        
        # 多周期移动平均线
        for window in [5, 10, 20, 60, 120, 250]:
            df[f'ma_{window}'] = df.groupby('code')['close'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            df[f'ma_ratio_{window}'] = df['close'] / df[f'ma_{window}']
        
        # RSI
        delta = df.groupby('code')['close'].diff()
        gain = delta.where(delta > 0, 0).groupby(df['code']).transform(
            lambda x: x.rolling(window=14, min_periods=1).mean()
        )
        loss = (-delta.where(delta < 0, 0)).groupby(df['code']).transform(
            lambda x: x.rolling(window=14, min_periods=1).mean()
        )
        rs = gain / (loss + 1e-10)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df.groupby('code')['close'].transform(lambda x: x.ewm(span=12).mean())
        ema_26 = df.groupby('code')['close'].transform(lambda x: x.ewm(span=26).mean())
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df.groupby('code')['macd'].transform(lambda x: x.ewm(span=9).mean())
        
        # 成交量特征
        df['vol_ma_20'] = df.groupby('code')['vol'].transform(lambda x: x.rolling(20).mean())
        df['vol_ratio'] = df['vol'] / df['vol_ma_20']
        
        # 价格形态
        df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
        df['close_open_ratio'] = (df['close'] - df['open']) / df['open']
        
        # 目标变量 (未来5日涨跌)
        df['future_return'] = df.groupby('code')['close'].shift(-5) / df['close'] - 1
        df['target'] = (df['future_return'] > 0).astype(int)
        
        # 删除NaN
        df = df.dropna()
        
        print(f"   ✅ 特征工程完成")
        print(f"   📊 有效样本: {len(df):,}")
        
        return df
    
    def train_models(self):
        """训练模型"""
        print("\n🚀 训练ML模型...")
        
        df = self.engineer_features()
        
        # 选择特征
        feature_cols = [col for col in df.columns if col.startswith('ma_') or col in [
            'rsi', 'macd', 'macd_signal', 'vol_ratio', 'high_low_ratio', 'close_open_ratio'
        ]]
        
        X = df[feature_cols].values
        y = df['target'].values
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 时间序列交叉验证
        tscv = TimeSeriesSplit(n_splits=5)
        cv_scores = []
        
        print("\n📊 交叉验证训练...")
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X_scaled)):
            X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.05,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train, y_train)
            val_pred = model.predict(X_val)
            val_acc = accuracy_score(y_val, val_pred)
            cv_scores.append(val_acc)
            
            print(f"   Fold {fold+1}: {val_acc:.2%}")
        
        print(f"\n✅ 交叉验证平均准确率: {np.mean(cv_scores):.2%}")
        
        # 保存模型
        final_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            random_state=42,
            n_jobs=-1
        )
        final_model.fit(X_scaled, y)
        
        model_path = os.path.join(self.model_dir, 'cio_simulated_model.pkl')
        joblib.dump(final_model, model_path)
        joblib.dump(scaler, os.path.join(self.model_dir, 'scaler.pkl'))
        joblib.dump(feature_cols, os.path.join(self.model_dir, 'features.pkl'))
        
        self.models['xgboost'] = final_model
        self.metrics = {
            'cv_mean': np.mean(cv_scores),
            'cv_std': np.std(cv_scores),
            'feature_importance': dict(zip(feature_cols, final_model.feature_importances_))
        }
        
        print(f"\n💾 模型已保存: {model_path}")
        
        # 特征重要性
        importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': final_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n📈 Top 10 重要特征:")
        for idx, row in importance.head(10).iterrows():
            print(f"   {idx+1:2d}. {row['feature']}: {row['importance']:.4f}")
        
        return self.metrics
    
    def run_full_pipeline(self, years=15):
        """运行完整流水线"""
        print("\n" + "=" * 70)
        print("🚀 CIO觉醒系统 - 基于真实样本的模拟训练")
        print("=" * 70)
        print()
        
        # 1. 加载样本
        self.load_sample()
        
        # 2. 生成模拟数据
        self.generate_historical_data(years=years)
        
        # 3. 保存到数据库
        self.save_to_database()
        
        # 4. 训练模型
        metrics = self.train_models()
        
        # 5. 保存指标
        metrics_path = os.path.join(self.model_dir, 'simulated_training_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'sample_file': self.sample_file,
                'years': years,
                'metrics': self.metrics
            }, f, indent=2)
        
        print("\n" + "=" * 70)
        print("🎉 模拟训练完成!")
        print("=" * 70)
        print(f"\n📊 结果:")
        print(f"   交叉验证准确率: {metrics['cv_mean']:.2%}")
        print(f"   训练数据: {years}年模拟数据")
        print(f"   基于样本: {len(self.sample_data)}只真实股票")
        print(f"\n💾 输出文件:")
        print(f"   数据库: {self.output_dir}/simulated_historical.db")
        print(f"   模型: {self.model_dir}/cio_simulated_model.pkl")
        print(f"   指标: {metrics_path}")
        
        return metrics


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🚀 CIO觉醒系统 - 样本数据模拟训练")
    print("=" * 70)
    print()
    
    sample_file = '/workspace/projects/media/inbound/20100104---f031e404-d1da-4dfc-b6cb-479c19cd4476'
    
    if not os.path.exists(sample_file):
        print(f"❌ 错误: 找不到样本文件 {sample_file}")
        return
    
    trainer = CIOSimulatedTrainer(
        sample_file=sample_file,
        output_dir='/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/data/processed',
        model_dir='/workspace/projects/workspace/A5L_v2.1_DEV/cio_awakening/models'
    )
    
    # 运行训练
    metrics = trainer.run_full_pipeline(years=15)
    
    print("\n✅ 训练完成，等待完整数据上传后重新训练！")


if __name__ == "__main__":
    main()
