#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Layer0 预测验证闭环系统 v4.0

核心能力:
1. 投资信号追踪 (1周/1月/3月)
2. 准确率计算与评级
3. 回测验证
4. 反馈优化 (权重调整)
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class ValidationPeriod(Enum):
    WEEK_1 = "week_1"
    MONTH_1 = "month_1"
    MONTH_3 = "month_3"

class AccuracyRating(Enum):
    EXCELLENT = "excellent"  # >= 80%
    GOOD = "good"  # >= 65%
    ACCEPTABLE = "acceptable"  # >= 50%
    POOR = "poor"  # < 50%

@dataclass
class SignalPrediction:
    """信号预测记录"""
    signal_id: str
    entity_id: str  # 股票代码
    signal_type: str  # bullish / bearish
    confidence: float
    predicted_return: float  # 预测收益率
    predicted_direction: str  # up / down / neutral
    generated_at: str
    valid_until: str

@dataclass
class ValidationResult:
    """验证结果"""
    period: str
    actual_price: float
    actual_return: float
    actual_direction: str
    predicted_direction: str
    correct: bool
    error_pct: float  # 预测误差百分比
    verified_at: str

@dataclass
class SignalTrack:
    """信号追踪记录"""
    signal_id: str
    entity_id: str
    signal_type: str
    confidence: float
    generated_at: str
    valid_until: str
    
    # 预测内容
    predictions: Dict[str, any]  # 包含各周期的预测
    
    # 验证结果
    validations: Dict[str, ValidationResult]  # period -> result
    
    # 综合评分
    overall_accuracy: float = None
    rating: str = None
    
    # 状态
    status: str = "active"  # active / verified / expired

class PredictionValidationEngine:
    """预测验证引擎"""
    
    VALIDATION_PERIODS = {
        "week_1": {"days": 7, "tolerance": 3.0},
        "month_1": {"days": 30, "tolerance": 5.0},
        "month_3": {"days": 90, "tolerance": 10.0}
    }
    
    ACCURACY_THRESHOLDS = {
        "excellent": 80.0,
        "good": 65.0,
        "acceptable": 50.0,
        "poor": 30.0
    }
    
    def __init__(self, data_dir: str = "/workspace/projects/workspace/data/architect_5l"):
        self.data_dir = data_dir
        self.signals_file = f"{data_dir}/signals/tracked_signals.json"
        self.validation_file = f"{data_dir}/signals/validation_results.json"
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        try:
            with open(self.signals_file, 'r') as f:
                data = json.load(f)
                self.signals = [SignalTrack(**s) for s in data.get("signals", [])]
        except FileNotFoundError:
            self.signals = []
        
        try:
            with open(self.validation_file, 'r') as f:
                self.validations = json.load(f)
        except FileNotFoundError:
            self.validations = {"results": [], "summary": {}}
    
    def _save_data(self):
        """保存数据"""
        import os
        os.makedirs(os.path.dirname(self.signals_file), exist_ok=True)
        
        with open(self.signals_file, 'w') as f:
            json.dump({
                "signals": [asdict(s) for s in self.signals]
            }, f, indent=2, ensure_ascii=False, default=str)
        
        with open(self.validation_file, 'w') as f:
            json.dump(self.validations, f, indent=2, ensure_ascii=False)
    
    def create_signal(self, signal_data: Dict) -> SignalTrack:
        """创建追踪信号"""
        signal = SignalTrack(
            signal_id=signal_data.get("signal_id", self._generate_id()),
            entity_id=signal_data["entity_id"],
            signal_type=signal_data["signal_type"],
            confidence=signal_data["confidence"],
            generated_at=datetime.now().isoformat(),
            valid_until=(datetime.now() + timedelta(days=90)).isoformat(),
            predictions={
                "week_1": {
                    "predicted_return": signal_data.get("week_1_return", 5.0),
                    "predicted_direction": signal_data.get("week_1_direction", "up")
                },
                "month_1": {
                    "predicted_return": signal_data.get("month_1_return", 10.0),
                    "predicted_direction": signal_data.get("month_1_direction", "up")
                },
                "month_3": {
                    "predicted_return": signal_data.get("month_3_return", 20.0),
                    "predicted_direction": signal_data.get("month_3_direction", "up")
                }
            },
            validations={}
        )
        
        self.signals.append(signal)
        self._save_data()
        return signal
    
    def _generate_id(self) -> str:
        """生成ID"""
        return f"SIG_{datetime.now().strftime('%Y%m%d')}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8].upper()}"
    
    def validate_signal(self, signal_id: str, period: str, 
                        actual_price: float, entry_price: float) -> ValidationResult:
        """验证信号"""
        signal = self._find_signal(signal_id)
        if not signal:
            raise ValueError(f"Signal {signal_id} not found")
        
        # 计算实际收益
        actual_return = (actual_price - entry_price) / entry_price * 100
        actual_direction = "up" if actual_return > 0 else "down" if actual_return < 0 else "neutral"
        
        # 获取预测
        prediction = signal.predictions.get(period, {})
        predicted_direction = prediction.get("predicted_direction", "up")
        predicted_return = prediction.get("predicted_return", 0)
        
        # 判断是否准确
        tolerance = self.VALIDATION_PERIODS[period]["tolerance"]
        direction_correct = actual_direction == predicted_direction
        return_error = abs(actual_return - predicted_return)
        return_correct = return_error <= tolerance
        
        correct = direction_correct and return_correct
        
        result = ValidationResult(
            period=period,
            actual_price=actual_price,
            actual_return=actual_return,
            actual_direction=actual_direction,
            predicted_direction=predicted_direction,
            correct=correct,
            error_pct=return_error,
            verified_at=datetime.now().isoformat()
        )
        
        signal.validations[period] = result
        
        # 更新整体准确率
        self._update_signal_accuracy(signal)
        
        self._save_data()
        return result
    
    def _find_signal(self, signal_id: str) -> Optional[SignalTrack]:
        """查找信号"""
        for s in self.signals:
            if s.signal_id == signal_id:
                return s
        return None
    
    def _update_signal_accuracy(self, signal: SignalTrack):
        """更新信号准确率"""
        if not signal.validations:
            return
        
        correct_count = sum(1 for v in signal.validations.values() if v.correct)
        total_count = len(signal.validations)
        
        signal.overall_accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
        signal.rating = self._get_rating(signal.overall_accuracy)
    
    def _get_rating(self, accuracy: float) -> str:
        """获取评级"""
        if accuracy >= self.ACCURACY_THRESHOLDS["excellent"]:
            return "excellent"
        elif accuracy >= self.ACCURACY_THRESHOLDS["good"]:
            return "good"
        elif accuracy >= self.ACCURACY_THRESHOLDS["acceptable"]:
            return "acceptable"
        else:
            return "poor"
    
    def calculate_system_accuracy(self) -> Dict:
        """计算系统整体准确率"""
        if not self.signals:
            return {"overall": 0, "by_period": {}, "by_entity": {}}
        
        # 按周期统计
        period_stats = {p: {"correct": 0, "total": 0} for p in self.VALIDATION_PERIODS.keys()}
        
        # 按标的统计
        entity_stats = {}
        
        for signal in self.signals:
            entity = signal.entity_id
            if entity not in entity_stats:
                entity_stats[entity] = {"correct": 0, "total": 0, "signals": 0}
            entity_stats[entity]["signals"] += 1
            
            for period, result in signal.validations.items():
                period_stats[period]["total"] += 1
                entity_stats[entity]["total"] += 1
                # Handle both dict and object
                is_correct = result.get("correct") if isinstance(result, dict) else result.correct
                if is_correct:
                    period_stats[period]["correct"] += 1
                    entity_stats[entity]["correct"] += 1
        
        # 计算准确率
        by_period = {}
        for period, stats in period_stats.items():
            accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            by_period[period] = {
                "accuracy": round(accuracy, 1),
                "correct": stats["correct"],
                "total": stats["total"]
            }
        
        by_entity = {}
        for entity, stats in entity_stats.items():
            accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            by_entity[entity] = {
                "accuracy": round(accuracy, 1),
                "signals": stats["signals"]
            }
        
        # 整体准确率
        total_correct = sum(s["correct"] for s in by_period.values())
        total_count = sum(s["total"] for s in by_period.values())
        overall = (total_correct / total_count * 100) if total_count > 0 else 0
        
        return {
            "overall": round(overall, 1),
            "rating": self._get_rating(overall),
            "by_period": by_period,
            "by_entity": by_entity,
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_feedback(self) -> Dict:
        """生成反馈优化建议"""
        accuracy_report = self.calculate_system_accuracy()
        overall_rating = accuracy_report["rating"]
        
        feedback_actions = {
            "excellent": {
                "action": "increase_confidence",
                "weight_adjustment": 0.05,
                "recommendation": "系统表现优异，可适当提高置信度阈值"
            },
            "good": {
                "action": "maintain",
                "weight_adjustment": 0.0,
                "recommendation": "系统表现良好，保持当前参数"
            },
            "acceptable": {
                "action": "review_parameters",
                "weight_adjustment": -0.02,
                "recommendation": "系统表现一般，建议审查预测模型参数"
            },
            "poor": {
                "action": "recalibrate",
                "weight_adjustment": -0.05,
                "recommendation": "系统表现不佳，需要重新校准模型"
            }
        }
        
        feedback = feedback_actions.get(overall_rating, feedback_actions["acceptable"])
        feedback["current_accuracy"] = accuracy_report["overall"]
        feedback["current_rating"] = overall_rating
        
        # 识别问题标的
        poor_performers = [
            entity for entity, stats in accuracy_report["by_entity"].items()
            if stats["accuracy"] < 50 and stats["signals"] >= 2
        ]
        
        if poor_performers:
            feedback["poor_performers"] = poor_performers
            feedback["recommendation"] += f"；特别关注表现不佳的标的: {', '.join(poor_performers)}"
        
        return feedback
    
    def get_pending_validations(self) -> List[Dict]:
        """获取待验证的信号"""
        pending = []
        now = datetime.now()
        
        for signal in self.signals:
            # 检查哪些周期需要验证
            for period, config in self.VALIDATION_PERIODS.items():
                if period not in signal.validations:
                    # 检查是否到达验证时间
                    generated = datetime.fromisoformat(signal.generated_at)
                    due_date = generated + timedelta(days=config["days"])
                    
                    if now >= due_date:
                        pending.append({
                            "signal_id": signal.signal_id,
                            "entity_id": signal.entity_id,
                            "signal_type": signal.signal_type,
                            "period": period,
                            "due_date": due_date.isoformat(),
                            "overdue_days": (now - due_date).days
                        })
        
        return pending
    
    def get_signal_summary(self, signal_id: str) -> Dict:
        """获取信号摘要"""
        signal = self._find_signal(signal_id)
        if not signal:
            return {}
        
        return {
            "signal_id": signal.signal_id,
            "entity_id": signal.entity_id,
            "signal_type": signal.signal_type,
            "confidence": signal.confidence,
            "generated_at": signal.generated_at,
            "predictions": signal.predictions,
            "validations": {
                period: {
                    "correct": v.correct,
                    "actual_return": v.actual_return,
                    "predicted_direction": v.predicted_direction,
                    "actual_direction": v.actual_direction,
                    "error_pct": v.error_pct
                }
                for period, v in signal.validations.items()
            },
            "overall_accuracy": signal.overall_accuracy,
            "rating": signal.rating,
            "status": signal.status
        }


# 演示函数
def demo_prediction_validation():
    """演示预测验证系统"""
    engine = PredictionValidationEngine()
    
    print("=" * 70)
    print("🔄 Week 4: 预测验证闭环系统 v4.0")
    print("=" * 70)
    
    # Step 1: 创建模拟信号
    print("\n📡 Step 1: 创建投资信号")
    print("-" * 70)
    
    signals_data = [
        {
            "entity_id": "NVDA",
            "signal_type": "bullish",
            "confidence": 85.0,
            "week_1_return": 5.0,
            "week_1_direction": "up",
            "month_1_return": 12.0,
            "month_1_direction": "up"
        },
        {
            "entity_id": "AAPL",
            "signal_type": "bullish",
            "confidence": 72.0,
            "week_1_return": 3.0,
            "week_1_direction": "up",
            "month_1_return": 8.0,
            "month_1_direction": "up"
        },
        {
            "entity_id": "TSLA",
            "signal_type": "bearish",
            "confidence": 68.0,
            "week_1_return": -4.0,
            "week_1_direction": "down",
            "month_1_return": -10.0,
            "month_1_direction": "down"
        }
    ]
    
    created_signals = []
    for data in signals_data:
        signal = engine.create_signal(data)
        created_signals.append(signal)
        print(f"✅ 创建信号: {signal.signal_id}")
        print(f"   标的: {signal.entity_id} | 类型: {signal.signal_type} | 置信度: {signal.confidence}%")
        print(f"   预测(1周): {signal.predictions['week_1']['predicted_return']}% {signal.predictions['week_1']['predicted_direction']}")
    
    # Step 2: 模拟验证
    print("\n📊 Step 2: 模拟信号验证")
    print("-" * 70)
    
    # NVDA - 准确预测
    result1 = engine.validate_signal(
        created_signals[0].signal_id, "week_1",
        actual_price=945.0, entry_price=890.0  # +6.18%
    )
    print(f"\n🎯 NVDA 1周验证:")
    print(f"   预测: +5% up | 实际: +6.18% up")
    print(f"   方向: {'✅ 正确' if result1.correct else '❌ 错误'}")
    print(f"   误差: {result1.error_pct:.2f}%")
    
    # AAPL - 方向错误
    result2 = engine.validate_signal(
        created_signals[1].signal_id, "week_1",
        actual_price=875.0, entry_price=890.0  # -1.69%
    )
    print(f"\n🎯 AAPL 1周验证:")
    print(f"   预测: +3% up | 实际: -1.69% down")
    print(f"   方向: {'✅ 正确' if result2.correct else '❌ 错误'}")
    print(f"   误差: {result2.error_pct:.2f}%")
    
    # TSLA - 准确预测
    result3 = engine.validate_signal(
        created_signals[2].signal_id, "week_1",
        actual_price=168.0, entry_price=175.0  # -4.0%
    )
    print(f"\n🎯 TSLA 1周验证:")
    print(f"   预测: -4% down | 实际: -4.0% down")
    print(f"   方向: {'✅ 正确' if result3.correct else '❌ 错误'}")
    print(f"   误差: {result3.error_pct:.2f}%")
    
    # Step 3: 系统准确率报告
    print("\n📈 Step 3: 系统准确率报告")
    print("-" * 70)
    
    report = engine.calculate_system_accuracy()
    
    print(f"\n🎯 整体准确率: {report['overall']}%")
    print(f"📊 评级: {report['rating'].upper()}")
    
    print(f"\n📅 按周期统计:")
    for period, stats in report['by_period'].items():
        emoji = "✅" if stats['accuracy'] >= 65 else "🟡" if stats['accuracy'] >= 50 else "❌"
        print(f"   {emoji} {period}: {stats['accuracy']}% ({stats['correct']}/{stats['total']})")
    
    print(f"\n📋 按标的统计:")
    for entity, stats in report['by_entity'].items():
        emoji = "✅" if stats['accuracy'] >= 65 else "🟡" if stats['accuracy'] >= 50 else "❌"
        print(f"   {emoji} {entity}: {stats['accuracy']}% ({stats['signals']}个信号)")
    
    # Step 4: 反馈优化建议
    print("\n🎛️ Step 4: 反馈优化建议")
    print("-" * 70)
    
    feedback = engine.generate_feedback()
    
    print(f"\n📊 当前准确率: {feedback['current_accuracy']}%")
    print(f"📈 当前评级: {feedback['current_rating'].upper()}")
    print(f"🔧 建议操作: {feedback['action']}")
    print(f"⚖️ 权重调整: {feedback['weight_adjustment']:+.2f}")
    print(f"💡 优化建议: {feedback['recommendation']}")
    
    if 'poor_performers' in feedback:
        print(f"\n⚠️ 需关注标的: {', '.join(feedback['poor_performers'])}")
    
    # Step 5: 待验证列表
    print("\n⏰ Step 5: 待验证信号")
    print("-" * 70)
    
    pending = engine.get_pending_validations()
    if pending:
        for p in pending:
            print(f"⏳ {p['entity_id']} - {p['period']} (逾期{p['overdue_days']}天)")
    else:
        print("✅ 无待验证信号")
    
    print("\n" + "=" * 70)
    print("✨ Week 4 预测验证闭环演示完成!")
    print("=" * 70)
    
    return created_signals


if __name__ == "__main__":
    demo_prediction_validation()
