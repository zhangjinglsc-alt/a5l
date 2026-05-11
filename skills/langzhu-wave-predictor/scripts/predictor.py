#!/usr/bin/env python3
"""
A5L 浪主波浪理论预测系统 v1.0
Langzhu Wave Theory Predictor

预测-验证-学习-升级闭环系统
"""

import os
import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple
from pathlib import Path

# 添加TOOLS路径
sys.path.insert(0, '/workspace/projects/workspace/TOOLS')
sys.path.insert(0, '/workspace/projects/workspace')
from process_manager import log_execution_start, log_execution_complete

# 导入 A5L 统一数据管理器
from tools.a5l_data_manager import get_index_daily, get_data_manager

# 数据目录
DATA_DIR = Path("/workspace/projects/workspace/skills/langzhu-wave-predictor/data")
LOGS_DIR = Path("/workspace/projects/workspace/skills/langzhu-wave-predictor/logs")
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

@dataclass
class WavePrediction:
    """预测记录"""
    prediction_id: str
    timestamp: str
    session: str  # 'morning' | 'afternoon'
    index_code: str  # 'sh000001' 上证指数
    index_name: str
    
    # 浪型分析
    current_wave: str  # 当前浪型位置
    wave_structure: str  # 浪型结构描述
    days_in_wave: int  # 当前浪已运行天数
    
    # 关键点位
    resistance_level: float  # 阻力位
    support_level_1: float  # 支撑位1（长4浪）
    support_level_2: float  # 支撑位2（4浪）
    current_price: float
    
    # 时间周期
    time_15min_count: int  # 当前15分钟计数
    time_left_threshold: int  # 左侧判断阈值（23）
    time_right_threshold: int  # 右侧确认阈值（32）
    
    # 预测结论
    prediction: str  # 'up' | 'down' | 'consolidation'
    confidence: float  # 置信度 0-1
    key_scenarios: List[str]  # 关键情景
    
    # 验证字段（后续填充）
    verified: bool = False
    actual_result: Optional[str] = None
    accuracy_score: Optional[float] = None
    verification_notes: Optional[str] = None

class IndexDataFetcher:
    """指数数据获取器"""
    
    INDEX_MAP = {
        'sh000001': {'name': '上证指数', 'ak_code': '000001'},
        'sz399001': {'name': '深证成指', 'ak_code': '399001'},
        'sz399006': {'name': '创业板指', 'ak_code': '399006'},
        'sh000016': {'name': '上证50', 'ak_code': '000016'},
        'sh000300': {'name': '沪深300', 'ak_code': '000300'},
        'sh000905': {'name': '中证500', 'ak_code': '000905'},
    }
    
    def fetch_intraday(self, index_code: str, period: str = "15") -> pd.DataFrame:
        """获取日内15分钟数据"""
        try:
            # 获取当日日线数据，从中推算日内情况
            # 使用 A5LDataManager (自动故障转移: Tushare > AKShare > Cache)
            today_str = datetime.now().strftime("%Y-%m-%d")
            df_daily = get_index_daily(index_code, start_date=today_str, end_date=today_str)
            if not df_daily.empty:
                current_hour = datetime.now().hour
                # 根据当前时间估算15分钟K线数量
                # 9:30-11:30, 13:00-15:00 为交易时间
                if current_hour < 9:
                    count = 0
                elif current_hour < 11:
                    count = (current_hour - 9) * 4 + (datetime.now().minute - 30) // 15 + 1
                elif current_hour == 11 and datetime.now().minute <= 30:
                    count = 8
                elif current_hour < 13:
                    count = 8  # 午休
                elif current_hour < 15:
                    count = 8 + (current_hour - 13) * 4 + datetime.now().minute // 15 + 1
                else:
                    count = 16
                
                return pd.DataFrame({
                    '时间': [datetime.now().strftime("%H:%M")],
                    '收盘': [float(df_daily.iloc[0]['收盘'])],
                    '开盘': [float(df_daily.iloc[0]['开盘'])],
                    '最高': [float(df_daily.iloc[0]['最高'])],
                    '最低': [float(df_daily.iloc[0]['最低'])],
                }), count
            return pd.DataFrame(), 0
        except Exception as e:
            print(f"获取日内数据失败: {e}")
            return pd.DataFrame(), 0
    
    def fetch_daily(self, index_code: str, days: int = 60) -> pd.DataFrame:
        """获取日线数据"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 使用 A5LDataManager (自动故障转移: Tushare > AKShare > Cache)
            df = get_index_daily(
                index_code,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            return df
        except Exception as e:
            print(f"获取日线数据失败: {e}")
            # 降级：尝试直接从数据管理器获取
            try:
                dm = get_data_manager()
                df = dm.get_index_daily(index_code)
                return df
            except Exception as e2:
                print(f"降级获取也失败: {e2}")
                return pd.DataFrame()
    
    def get_current_price(self, index_code: str) -> float:
        """获取当前价格"""
        try:
            df = self.fetch_daily(index_code, days=1)
            if not df.empty:
                return float(df.iloc[-1]['收盘'])
            return 0.0
        except:
            return 0.0

from wave_pattern_recognizer import WavePatternRecognizer, WaveStructure, WaveType

class LangzhuWaveAnalyzer:
    """浪主波浪理论分析器"""
    
    def __init__(self):
        self.time_left_threshold = 23  # 左侧判断：23个15分钟
        self.time_right_threshold = 32  # 右侧确认：32个15分钟
        self.wave_lifecycle = 30  # 微浪型寿命约30天
        self.wave_recognizer = WavePatternRecognizer()  # 新增浪型识别器
    
    def analyze(self, df_daily: pd.DataFrame, df_15min: pd.DataFrame) -> Dict:
        """
        执行浪主波浪理论分析（增强版）
        """
        if df_daily.empty:
            return {"error": "无数据"}
        
        latest = df_daily.iloc[-1]
        current_price = float(latest['收盘'])
        
        # 计算15分钟K线数量（当天）
        time_15min_count = len(df_15min) if not df_15min.empty else 0
        
        # 关键点位（动态计算或从配置读取）
        resistance = 4197.23
        support_1 = 4143.56  # 长4浪低点
        support_2 = 4061.15  # 4浪低点
        
        # ===== 增强：使用浪型识别器 =====
        # 从3794低点开始分析（根据浪主文章）
        wave_structure = self.wave_recognizer.identify_5wave_structure(
            df_daily,
            significant_low=3794,
            significant_low_date="2025-04-07"  # 3794低点日期
        )
        
        # 格式化浪型结构
        wave_structure_text = self.wave_recognizer.format_wave_structure(wave_structure)
        
        # 获取当前浪型信息
        current_wave = f"{wave_structure.current_wave.value} (第{wave_structure.current_wave_num}浪)"
        wave_structure_desc = " | ".join(wave_structure.key_features[:3])  # 取前3个特征
        
        # 检测扁担型结构
        is_carrying_pole = wave_structure.is_carrying_pole
        carrying_pole_warning = wave_structure.carrying_pole_desc if is_carrying_pole else None
        
        # ===== 时间周期判断 =====
        if time_15min_count >= self.time_right_threshold:
            time_status = f"✅ 右侧确认（{time_15min_count}个15分钟 > {self.time_right_threshold}）"
            adjustment_confirmed = True
        elif time_15min_count >= self.time_left_threshold:
            time_status = f"⚠️ 左侧判断（{time_15min_count}个15分钟 > {self.time_left_threshold}）"
            adjustment_confirmed = False
        else:
            time_status = f"⏳ 观察中（{time_15min_count}/{self.time_left_threshold}个15分钟）"
            adjustment_confirmed = False
        
        # ===== 空间判断 =====
        if current_price < support_2:
            space_status = f"✅ 跌破4浪低点{support_2}，调整确认"
            space_confirmed = True
        elif current_price < support_1:
            space_status = f"⚠️ 跌破长4浪低点{support_1}，观察是否破{support_2}"
            space_confirmed = False
        else:
            space_status = f"⏳ 在长4浪低点{support_1}之上运行"
            space_confirmed = False
        
        # 综合预测（结合浪型结构）
        if is_carrying_pole:
            prediction = "down"
            confidence = 0.80
            key_scenarios = [
                f"⚠️ 扁担型结构预警：{carrying_pole_warning}",
                "破长4浪低点后再创新高=小末浪，通常是诱多",
                "建议减仓观望，防范大跌风险"
            ]
        elif adjustment_confirmed or space_confirmed:
            prediction = "down"
            confidence = 0.75
            key_scenarios = [
                "调整已确认，关注下方支撑",
                f"当前处于{current_wave}，调整概率大",
                "时间验证优先于空间判断"
            ]
        elif wave_structure.lifecycle_stage == "end":
            prediction = "consolidation"
            confidence = 0.70
            key_scenarios = [
                f"处于{current_wave}末端，即将变盘",
                f"微浪型已运行{wave_structure.total_days}天，接近寿命极限",
                "等待方向确认，控制仓位"
            ]
        elif time_15min_count >= 15:  # 接近左侧判断
            prediction = "consolidation"
            confidence = 0.60
            key_scenarios = [
                "处于调整临界点，观望为主",
                f"再需{self.time_left_threshold - time_15min_count}个15分钟可左侧判断",
                "下午或下周一确认"
            ]
        else:
            prediction = "consolidation"
            confidence = 0.50
            key_scenarios = [
                f"当前处于{current_wave}，等待确认信号",
                "时间周期尚未满足",
                f"空间上关注{support_1}支撑"
            ]
        
        return {
            "current_price": current_price,
            "current_wave": current_wave,
            "wave_structure": wave_structure_desc,
            "wave_structure_detail": wave_structure_text,  # 新增详细浪型结构
            "wave_lifecycle": wave_structure.lifecycle_stage,
            "wave_confidence": wave_structure.structure_confidence,
            "days_in_wave": wave_structure.total_days,
            "is_carrying_pole": is_carrying_pole,  # 扁担型标记
            "carrying_pole_warning": carrying_pole_warning,
            "resistance_level": resistance,
            "support_level_1": support_1,
            "support_level_2": support_2,
            "time_15min_count": time_15min_count,
            "time_status": time_status,
            "space_status": space_status,
            "prediction": prediction,
            "confidence": confidence,
            "key_scenarios": key_scenarios,
            "waves_detail": [  # 新增各浪详情
                {
                    "num": w.wave_num,
                    "type": w.wave_type.value,
                    "amplitude": round(w.amplitude * 100, 2),
                    "duration": w.duration_days,
                    "length": w.length_type.value
                } for w in wave_structure.waves
            ] if wave_structure.waves else []
        }

class PredictionDatabase:
    """预测记录数据库"""
    
    def __init__(self):
        self.db_path = DATA_DIR / "predictions.db"
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                session TEXT NOT NULL,
                index_code TEXT NOT NULL,
                index_name TEXT NOT NULL,
                current_wave TEXT,
                wave_structure TEXT,
                days_in_wave INTEGER,
                resistance_level REAL,
                support_level_1 REAL,
                support_level_2 REAL,
                current_price REAL,
                time_15min_count INTEGER,
                time_left_threshold INTEGER,
                time_right_threshold INTEGER,
                prediction TEXT,
                confidence REAL,
                key_scenarios TEXT,
                verified BOOLEAN DEFAULT 0,
                actual_result TEXT,
                accuracy_score REAL,
                verification_notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_prediction(self, pred: WavePrediction):
        """保存预测"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO predictions VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            pred.prediction_id,
            pred.timestamp,
            pred.session,
            pred.index_code,
            pred.index_name,
            pred.current_wave,
            pred.wave_structure,
            pred.days_in_wave,
            pred.resistance_level,
            pred.support_level_1,
            pred.support_level_2,
            pred.current_price,
            pred.time_15min_count,
            pred.time_left_threshold,
            pred.time_right_threshold,
            pred.prediction,
            pred.confidence,
            json.dumps(pred.key_scenarios, ensure_ascii=False),
            pred.verified,
            pred.actual_result,
            pred.accuracy_score,
            pred.verification_notes
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_prediction(self, index_code: str, session: str) -> Optional[WavePrediction]:
        """获取最新预测"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE index_code = ? AND session = ?
            ORDER BY timestamp DESC LIMIT 1
        ''', (index_code, session))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return WavePrediction(
                prediction_id=row[0],
                timestamp=row[1],
                session=row[2],
                index_code=row[3],
                index_name=row[4],
                current_wave=row[5],
                wave_structure=row[6],
                days_in_wave=row[7],
                resistance_level=row[8],
                support_level_1=row[9],
                support_level_2=row[10],
                current_price=row[11],
                time_15min_count=row[12],
                time_left_threshold=row[13],
                time_right_threshold=row[14],
                prediction=row[15],
                confidence=row[16],
                key_scenarios=json.loads(row[17]),
                verified=bool(row[18]),
                actual_result=row[19],
                accuracy_score=row[20],
                verification_notes=row[21]
            )
        return None
    
    def get_unverified_predictions(self, date: str) -> List[WavePrediction]:
        """获取指定日期未验证的预测"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE date(timestamp) = ? AND verified = 0
        ''', (date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            predictions.append(WavePrediction(
                prediction_id=row[0],
                timestamp=row[1],
                session=row[2],
                index_code=row[3],
                index_name=row[4],
                current_wave=row[5],
                wave_structure=row[6],
                days_in_wave=row[7],
                resistance_level=row[8],
                support_level_1=row[9],
                support_level_2=row[10],
                current_price=row[11],
                time_15min_count=row[12],
                time_left_threshold=row[13],
                time_right_threshold=row[14],
                prediction=row[15],
                confidence=row[16],
                key_scenarios=json.loads(row[17]),
                verified=bool(row[18]),
                actual_result=row[19],
                accuracy_score=row[20],
                verification_notes=row[21]
            ))
        return predictions

class PredictionVerifier:
    """预测验证器"""
    
    def __init__(self, db: PredictionDatabase):
        self.db = db
        self.fetcher = IndexDataFetcher()
    
    def verify_prediction(self, pred: WavePrediction) -> Dict:
        """验证单个预测"""
        
        # 获取当前实际价格
        current_price = self.fetcher.get_current_price(pred.index_code)
        
        # 验证逻辑
        verification_result = {
            "prediction_id": pred.prediction_id,
            "predicted": pred.prediction,
            "predicted_price": pred.current_price,
            "actual_price": current_price,
            "price_change": current_price - pred.current_price,
            "price_change_pct": (current_price - pred.current_price) / pred.current_price * 100 if pred.current_price else 0
        }
        
        # 判断预测准确性
        if pred.prediction == "up":
            if verification_result["price_change"] > 0:
                verification_result["correct"] = True
                verification_result["accuracy_score"] = min(abs(verification_result["price_change_pct"]) / 2, 1.0)
            else:
                verification_result["correct"] = False
                verification_result["accuracy_score"] = 0.0
        elif pred.prediction == "down":
            if verification_result["price_change"] < 0:
                verification_result["correct"] = True
                verification_result["accuracy_score"] = min(abs(verification_result["price_change_pct"]) / 2, 1.0)
            else:
                verification_result["correct"] = False
                verification_result["accuracy_score"] = 0.0
        else:  # consolidation
            if abs(verification_result["price_change_pct"]) < 0.5:
                verification_result["correct"] = True
                verification_result["accuracy_score"] = 0.8
            else:
                verification_result["correct"] = False
                verification_result["accuracy_score"] = 0.3
        
        return verification_result
    
    def verify_session(self, session: str, date: str = None):
        """验证某时段的所有预测"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        predictions = self.db.get_unverified_predictions(date)
        results = []
        
        for pred in predictions:
            if pred.session == session or session == "all":
                result = self.verify_prediction(pred)
                results.append(result)
                
                # 更新数据库
                pred.verified = True
                pred.actual_result = "correct" if result["correct"] else "wrong"
                pred.accuracy_score = result["accuracy_score"]
                pred.verification_notes = json.dumps(result, ensure_ascii=False)
                self.db.save_prediction(pred)
        
        return results

class LangzhuPredictor:
    """浪主预测系统主控制器"""
    
    def __init__(self):
        self.fetcher = IndexDataFetcher()
        self.analyzer = LangzhuWaveAnalyzer()
        self.db = PredictionDatabase()
        self.verifier = PredictionVerifier(self.db)
    
    def predict(self, index_code: str = 'sh000001', session: str = 'morning') -> WavePrediction:
        """
        执行预测
        
        Args:
            index_code: 指数代码
            session: 'morning'（早盘）或 'afternoon'（午盘）
        """
        # 记录执行
        exec_record = log_execution_start(
            task_name=f"langzhu_predict_{session}",
            task_version="1.0.0",
            inputs={"index_code": index_code, "session": session}
        )
        
        # 获取数据
        df_daily = self.fetcher.fetch_daily(index_code, days=60)
        df_15min, time_count = self.fetcher.fetch_intraday(index_code, period="15")
        
        # 执行分析
        analysis = self.analyzer.analyze(df_daily, df_15min)
        
        # 生成预测ID
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prediction_id = f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{index_code}"
        
        # 创建预测记录
        pred = WavePrediction(
            prediction_id=prediction_id,
            timestamp=timestamp,
            session=session,
            index_code=index_code,
            index_name=self.fetcher.INDEX_MAP.get(index_code, {}).get('name', '未知'),
            current_wave=analysis.get('current_wave', ''),
            wave_structure=analysis.get('wave_structure', ''),
            days_in_wave=analysis.get('days_in_wave', 0),
            resistance_level=analysis.get('resistance_level', 0),
            support_level_1=analysis.get('support_level_1', 0),
            support_level_2=analysis.get('support_level_2', 0),
            current_price=analysis.get('current_price', 0),
            time_15min_count=analysis.get('time_15min_count', 0),
            time_left_threshold=self.analyzer.time_left_threshold,
            time_right_threshold=self.analyzer.time_right_threshold,
            prediction=analysis.get('prediction', 'consolidation'),
            confidence=analysis.get('confidence', 0.5),
            key_scenarios=analysis.get('key_scenarios', [])
        )
        
        # 保存预测
        self.db.save_prediction(pred)
        
        # 完成执行记录
        log_execution_complete(
            exec_record,
            status="success",
            outputs={"prediction_id": prediction_id, "prediction": pred.prediction},
            metrics={"confidence": pred.confidence}
        )
        
        return pred, analysis
    
    def verify(self, session: str = 'morning') -> List[Dict]:
        """验证预测"""
        return self.verifier.verify_session(session)
    
    def generate_report(self, pred: WavePrediction, analysis: Dict = None) -> str:
        """生成预测报告（增强版）"""
        
        direction_map = {
            'up': '看涨',
            'down': '看跌',
            'consolidation': '震荡'
        }
        
        # 获取详细浪型结构
        wave_detail_text = ""
        if analysis and 'wave_structure_detail' in analysis:
            wave_detail_text = analysis.get('wave_structure_detail', '')
        
        # 获取扁担型预警
        carrying_pole_warning = analysis.get('carrying_pole_warning', '') if analysis else ''
        
        # 获取各浪详情
        waves_detail = analysis.get('waves_detail', []) if analysis else []
        waves_table = ""
        if waves_detail:
            waves_table = "\n| 浪号 | 类型 | 幅度 | 时长 | 长度 |\n"
            waves_table += "|------|------|------|------|------|\n"
            for w in waves_detail:
                waves_table += f"| {w['num']}浪 | {w['type']} | {w['amplitude']:+.1f}% | {w['duration']}天 | {w['length']} |\n"
        
        report = f"""# 🌊 浪主波浪理论预测报告

## 📊 基本信息
- **指数**: {pred.index_name} ({pred.index_code})
- **时间**: {pred.timestamp}
- **时段**: {'早盘' if pred.session == 'morning' else '午盘'}
- **预测ID**: {pred.prediction_id}

## 🌊 浪型结构分析
- **当前位置**: {pred.current_wave}
- **浪型结构**: {pred.wave_structure}
- **运行天数**: {pred.days_in_wave}天
- **生命周期**: {(analysis.get('wave_lifecycle', 'unknown') if analysis else 'unknown')}
- **结构置信度**: {(analysis.get('wave_confidence', 0) * 100 if analysis else 0):.0f}%

### 各浪详情
{waves_table if waves_table else '暂无详细浪型数据'}

## 🎯 关键点位
```
阻力位:   {pred.resistance_level:.2f}
    ↑
现价:     {pred.current_price:.2f}
    ↓
支撑1:    {pred.support_level_1:.2f} (长4浪)
    ↓
支撑2:    {pred.support_level_2:.2f} (4浪)
```

## ⏱️ 时间周期
- **当前计数**: {pred.time_15min_count}个15分钟
- **左侧阈值**: {pred.time_left_threshold}个15分钟
- **右侧阈值**: {pred.time_right_threshold}个15分钟

## 📈 预测结论
- **方向**: {direction_map.get(pred.prediction, pred.prediction)}
- **置信度**: {pred.confidence * 100:.1f}%

### 关键情景
"""
        for i, scenario in enumerate(pred.key_scenarios, 1):
            report += f"{i}. {scenario}\n"
        
        # 添加扁担型预警
        if carrying_pole_warning:
            report += f"\n## ⚠️ 扁担型结构预警\n\n> {carrying_pole_warning}\n\n**风险提示**: 破长4浪低点后再创新高通常是诱多信号，建议减仓防范。\n"
        
        # 添加详细浪型结构
        if wave_detail_text:
            report += f"\n## 📋 详细浪型结构\n\n```\n{wave_detail_text}\n```\n"
        
        report += f"""
## 📝 操作建议
- 时间周期验证优先于空间判断
- 重点关注{pred.support_level_1:.2f}支撑
- 超过{pred.time_left_threshold}个15分钟可左侧判断

---
*基于浪主波浪理论分析，仅供参考*
"""
        return report

# 主函数入口
def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='浪主波浪理论预测系统')
    parser.add_argument('action', choices=['predict', 'verify'], help='动作')
    parser.add_argument('--session', '-s', choices=['morning', 'afternoon'], 
                        default='morning', help='时段')
    parser.add_argument('--index', '-i', default='sh000001', help='指数代码')
    
    args = parser.parse_args()
    
    predictor = LangzhuPredictor()
    
    if args.action == 'predict':
        pred, analysis = predictor.predict(args.index, args.session)
        report = predictor.generate_report(pred, analysis)
        print(report)
        
        # 保存报告
        report_file = LOGS_DIR / f"report_{pred.prediction_id}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存: {report_file}")
        
    elif args.action == 'verify':
        results = predictor.verify(args.session)
        print(f"验证完成: {len(results)}条预测")
        for r in results:
            status = "✅" if r['correct'] else "❌"
            print(f"{status} {r['prediction_id']}: 预测{r['predicted']} -> 实际变化{r['price_change_pct']:.2f}%")

if __name__ == "__main__":
    main()
