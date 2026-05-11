"""
A5L-工程控制论投资控制系统
对应钱学森《工程控制论》核心理论

核心控制原理：
1. 反馈控制 - 根据输出调整输入
2. 前馈控制 - 预测干扰提前补偿
3. 最优控制 - 在约束条件下求极值
4. 自适应控制 - 系统参数自动调整
5. 鲁棒控制 - 在不确定性下保持稳定
"""

from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class ControlSignal:
    """控制信号"""
    timestamp: str
    target_position: float
    action: str
    reasoning: str
    confidence: float


@dataclass
class SystemState:
    """系统状态"""
    portfolio_value: float
    cash_ratio: float
    risk_exposure: float
    current_positions: Dict[str, float]
    market_regime: str


class FeedbackController:
    """
    反馈控制器
    
    核心思想：根据投资组合实际表现与目标的偏差进行调整
    - 负反馈：偏差过大时反向调整
    - 比例控制：调整幅度与偏差成正比
    - 积分控制：消除稳态误差
    - 微分控制：预测趋势提前响应
    """
    
    def __init__(self, 
                 kp: float = 0.5,  # 比例系数
                 ki: float = 0.1,  # 积分系数
                 kd: float = 0.2):  # 微分系数
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error_integral = 0
        self.last_error = 0
        self.history = []
    
    def calculate_control_signal(self, 
                                  target_return: float,
                                  actual_return: float,
                                  current_position: float) -> ControlSignal:
        """计算PID控制信号"""
        # 计算误差
        error = target_return - actual_return
        
        # 比例项
        proportional = self.kp * error
        
        # 积分项
        self.error_integral += error
        integral = self.ki * self.error_integral
        
        # 微分项
        derivative = self.kd * (error - self.last_error)
        self.last_error = error
        
        # PID输出
        pid_output = proportional + integral + derivative
        
        # 转换为仓位调整
        position_adjustment = np.clip(pid_output, -0.2, 0.2)
        new_position = np.clip(current_position + position_adjustment, 0, 1)
        
        signal = ControlSignal(
            timestamp=datetime.now().isoformat(),
            target_position=new_position,
            action='increase' if position_adjustment > 0 else 'decrease',
            reasoning=f'PID控制: P={proportional:.3f}, I={integral:.3f}, D={derivative:.3f}',
            confidence=min(abs(pid_output) / 0.2, 1.0)
        )
        
        self.history.append({
            'error': error,
            'pid_output': pid_output,
            'adjustment': position_adjustment
        })
        
        return signal


class FeedforwardController:
    """
    前馈控制器
    
    核心思想：预测已知干扰，提前补偿
    - 识别可预测的市场事件
    - 提前调整仓位应对
    - 减少反馈控制的滞后
    """
    
    def __init__(self):
        self.known_disturbances = []
        self.compensation_rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict:
        """初始化补偿规则"""
        return {
            'earnings_season': {
                'detector': lambda ctx: ctx.get('is_earnings_season', False),
                'compensation': {'volatility_adjustment': 0.8, 'position_cap': 0.7}
            },
            'fed_meeting': {
                'detector': lambda ctx: ctx.get('fed_meeting_within_week', False),
                'compensation': {'reduce_beta': True, 'increase_cash': 0.1}
            },
            'options_expiry': {
                'detector': lambda ctx: ctx.get('options_expiry_this_week', False),
                'compensation': {'volatility_adjustment': 1.2}
            }
        }
    
    def predict_and_compensate(self, 
                                current_state: SystemState,
                                market_context: dict) -> Optional[ControlSignal]:
        """预测干扰并生成补偿信号"""
        compensations = []
        
        for disturbance_name, rules in self.compensation_rules.items():
            if rules['detector'](market_context):
                compensations.append({
                    'disturbance': disturbance_name,
                    'action': rules['compensation']
                })
        
        if not compensations:
            return None
        
        # 合并补偿措施
        total_adjustment = self._merge_compensations(compensations)
        
        return ControlSignal(
            timestamp=datetime.now().isoformat(),
            target_position=current_state.cash_ratio + total_adjustment.get('position_delta', 0),
            action='feedforward_adjust',
            reasoning=f'前馈补偿: {[c["disturbance"] for c in compensations]}',
            confidence=0.8
        )
    
    def _merge_compensations(self, compensations: list) -> dict:
        """合并多个补偿措施"""
        merged = {'position_delta': 0}
        for comp in compensations:
            if 'increase_cash' in comp['action']:
                merged['position_delta'] += comp['action']['increase_cash']
        return merged


class OptimalController:
    """
    最优控制器
    
    核心思想：在约束条件下最大化目标函数
    - 目标：夏普比率最大化
    - 约束：最大回撤、集中度、流动性
    - 方法：二次规划求解
    """
    
    def __init__(self):
        self.constraints = {
            'max_drawdown': 0.20,
            'max_single_position': 0.25,
            'min_cash_ratio': 0.05
        }
    
    def optimize_portfolio(self,
                          expected_returns: np.ndarray,
                          covariance_matrix: np.ndarray,
                          current_weights: np.ndarray) -> ControlSignal:
        """
        投资组合优化（简化版马科维茨）
        
        Args:
            expected_returns: 预期收益率向量
            covariance_matrix: 协方差矩阵
            current_weights: 当前权重
        """
        n_assets = len(expected_returns)
        
        # 简化：使用风险平价作为启发式解
        inv_vol = 1 / np.sqrt(np.diag(covariance_matrix))
        risk_parity_weights = inv_vol / inv_vol.sum()
        
        # 应用约束
        optimal_weights = self._apply_constraints(risk_parity_weights)
        
        # 计算调整量
        weight_changes = optimal_weights - current_weights
        max_change = np.max(np.abs(weight_changes))
        
        return ControlSignal(
            timestamp=datetime.now().isoformat(),
            target_position=optimal_weights[0] if len(optimal_weights) > 0 else 0,
            action='rebalance',
            reasoning=f'最优控制: 风险平价权重调整，最大变化{max_change:.2%}',
            confidence=0.75
        )
    
    def _apply_constraints(self, weights: np.ndarray) -> np.ndarray:
        """应用约束条件"""
        # 单一仓位上限
        weights = np.clip(weights, 0, self.constraints['max_single_position'])
        # 归一化
        weights = weights / weights.sum() if weights.sum() > 0 else weights
        return weights


class AdaptiveController:
    """
    自适应控制器
    
    核心思想：根据市场环境自动调整控制参数
    - 波动率高时降低仓位敏感度
    - 趋势强时增加趋势跟踪权重
    - 持续学习优化参数
    """
    
    def __init__(self):
        self.base_parameters = {
            'trend_following_weight': 0.5,
            'mean_reversion_weight': 0.3,
            'momentum_lookback': 20
        }
        self.current_parameters = self.base_parameters.copy()
        self.adaptation_history = []
    
    def adapt_parameters(self, market_regime: str, performance: dict) -> dict:
        """根据市场环境调整参数"""
        volatility = performance.get('portfolio_volatility', 0.15)
        sharpe = performance.get('sharpe_ratio', 1.0)
        
        # 高波动环境：降低敏感度
        if volatility > 0.25:
            self.current_parameters['trend_following_weight'] *= 0.8
            self.current_parameters['mean_reversion_weight'] *= 1.2
            adaptation_reason = '高波动环境，降低趋势跟踪权重'
        
        # 低夏普环境：增加均值回归
        elif sharpe < 0.5:
            self.current_parameters['mean_reversion_weight'] *= 1.3
            adaptation_reason = '夏普比率低，增加均值回归权重'
        
        # 强趋势环境：增加趋势跟踪
        elif market_regime == 'strong_trend':
            self.current_parameters['trend_following_weight'] *= 1.2
            self.current_parameters['momentum_lookback'] = 10
            adaptation_reason = '强趋势环境，增加趋势跟踪敏感度'
        
        else:
            adaptation_reason = '市场环境稳定，维持当前参数'
        
        self.adaptation_history.append({
            'timestamp': datetime.now().isoformat(),
            'regime': market_regime,
            'new_parameters': self.current_parameters.copy(),
            'reason': adaptation_reason
        })
        
        return {
            'adapted_parameters': self.current_parameters,
            'adaptation_reason': adaptation_reason,
            'performance_trigger': performance
        }


class RobustController:
    """
    鲁棒控制器
    
    核心思想：在模型不确定性和外部扰动下保持系统稳定
    - H∞控制：最坏情况优化
    - 滑模控制：快速响应切换
    - 容错控制：部分失效仍可用
    """
    
    def __init__(self):
        self.uncertainty_bounds = {
            'return_estimate': 0.30,  # 预期收益率±30%不确定性
            'volatility_estimate': 0.20  # 波动率±20%不确定性
        }
        self.safety_margin = 0.15
    
    def robust_position_sizing(self,
                               nominal_position: float,
                               uncertainty_level: float) -> ControlSignal:
        """鲁棒仓位计算"""
        # 最坏情况分析
        worst_case_return = -self.uncertainty_bounds['return_estimate']
        
        # 应用安全边界
        robust_position = nominal_position * (1 - self.safety_margin)
        
        # 不确定性越高，仓位越保守
        uncertainty_adjustment = 1 - min(uncertainty_level, 0.5)
        final_position = robust_position * uncertainty_adjustment
        
        return ControlSignal(
            timestamp=datetime.now().isoformat(),
            target_position=final_position,
            action='robust_adjust',
            reasoning=f'鲁棒控制: 名义仓位{nominal_position:.1%}，'
                     f'不确定性{uncertainty_level:.1%}，'
                     f'调整后{final_position:.1%}',
            confidence=1 - uncertainty_level
        )
    
    def fault_tolerant_control(self,
                               primary_signal: ControlSignal,
                               backup_signals: List[ControlSignal]) -> ControlSignal:
        """容错控制：主信号失效时启用备用"""
        if primary_signal.confidence > 0.5:
            return primary_signal
        
        # 选择置信度最高的备用信号
        best_backup = max(backup_signals, key=lambda s: s.confidence)
        
        if best_backup.confidence > 0.3:
            return ControlSignal(
                timestamp=datetime.now().isoformat(),
                target_position=best_backup.target_position,
                action='fault_tolerant_backup',
                reasoning=f'主信号失效，启用备用: {best_backup.reasoning}',
                confidence=best_backup.confidence * 0.8
            )
        
        # 所有信号都不可靠，保持现状
        return ControlSignal(
            timestamp=datetime.now().isoformat(),
            target_position=0,  # 清仓观望
            action='safe_mode',
            reasoning='所有控制信号不可靠，进入安全模式',
            confidence=0.5
        )


class EngineeringControlSystem:
    """
    工程控制论投资控制系统（主控器）
    
    整合所有控制器的综合控制系统
    """
    
    def __init__(self):
        self.feedback = FeedbackController()
        self.feedforward = FeedforwardController()
        self.optimal = OptimalController()
        self.adaptive = AdaptiveController()
        self.robust = RobustController()
        
        self.controller_weights = {
            'feedback': 0.35,
            'feedforward': 0.20,
            'optimal': 0.25,
            'adaptive': 0.15,
            'robust': 0.05
        }
    
    def generate_control_decision(self,
                                  system_state: SystemState,
                                  market_context: dict,
                                  performance: dict) -> dict:
        """生成综合控制决策"""
        # 1. 反馈控制
        feedback_signal = self.feedback.calculate_control_signal(
            target_return=0.15,
            actual_return=performance.get('ytd_return', 0),
            current_position=1 - system_state.cash_ratio
        )
        
        # 2. 前馈控制
        feedforward_signal = self.feedforward.predict_and_compensate(
            system_state, market_context
        )
        
        # 3. 最优控制（简化示例）
        optimal_signal = self.optimal.optimize_portfolio(
            expected_returns=np.array([0.10, 0.15, 0.12]),
            covariance_matrix=np.eye(3) * 0.02,
            current_weights=np.array([0.3, 0.4, 0.3])
        )
        
        # 4. 自适应调整
        adaptive_params = self.adaptive.adapt_parameters(
            market_context.get('regime', 'neutral'),
            performance
        )
        
        # 5. 鲁棒控制
        robust_signal = self.robust.robust_position_sizing(
            nominal_position=feedback_signal.target_position,
            uncertainty_level=market_context.get('uncertainty', 0.2)
        )
        
        # 综合决策（加权融合）
        signals = [
            (feedback_signal, self.controller_weights['feedback']),
            (feedforward_signal, self.controller_weights['feedforward']) if feedforward_signal else (None, 0),
            (optimal_signal, self.controller_weights['optimal']),
            (robust_signal, self.controller_weights['robust'])
        ]
        
        valid_signals = [(s, w) for s, w in signals if s is not None]
        total_weight = sum(w for _, w in valid_signals)
        
        if total_weight > 0:
            final_position = sum(s.target_position * w for s, w in valid_signals) / total_weight
        else:
            final_position = 0.5
        
        return {
            'timestamp': datetime.now().isoformat(),
            'control_signals': {
                'feedback': feedback_signal,
                'feedforward': feedforward_signal,
                'optimal': optimal_signal,
                'adaptive': adaptive_params,
                'robust': robust_signal
            },
            'final_decision': {
                'target_position': final_position,
                'action': 'composite_control',
                'confidence': np.mean([s.confidence for s, _ in valid_signals])
            },
            'control_philosophy': '工程控制论：反馈+前馈+最优+自适应+鲁棒'
        }
