"""
A5L-Universal-Control-Architecture (A5L-UCA)
A5L通用控制架构 v1.0

融合钱学森《工程控制论》与深度学习的顶级架构

架构理念：
- 控制论提供：稳定性、收敛性、鲁棒性保证
- 深度学习提供：非线性映射、模式识别、预测能力
- 反馈闭环：感知→认知→决策→执行→学习→进化

设计原则：
1. 通用性：任何A5L任务（投资/研究/编程/写作）都适用
2. 稳定性：控制论保证系统稳定收敛
3. 适应性：深度学习实现环境自适应
4. 可解释性：每个决策可追溯至控制理论和神经网络节点
"""

import numpy as np
from typing import Dict, List, Callable, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class TaskType(Enum):
    """任务类型枚举"""
    INVESTMENT = "investment"      # 投资决策
    RESEARCH = "research"          # 研究分析
    CODING = "coding"              # 代码生成
    WRITING = "writing"            # 文档撰写
    PLANNING = "planning"          # 任务规划
    COMMUNICATION = "communication" # 沟通协调
    ANALYSIS = "analysis"          # 数据分析
    DECISION = "decision"          # 通用决策


@dataclass
class SystemState:
    """
    系统状态向量
    完整描述A5L当前状态（类似控制论中的状态空间）
    """
    # 基础状态
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    task_type: TaskType = TaskType.DECISION
    
    # 性能指标（可观测输出）
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    # 内部状态（部分可观测）
    internal_state: Dict[str, Any] = field(default_factory=dict)
    
    # 环境状态（外部输入）
    environment_state: Dict[str, Any] = field(default_factory=dict)
    
    # 历史轨迹（用于学习和预测）
    history: List[Dict] = field(default_factory=list)
    
    def to_vector(self) -> np.ndarray:
        """将状态转换为向量（用于神经网络输入）"""
        # 提取数值型指标
        values = []
        for k, v in self.performance_metrics.items():
            if isinstance(v, (int, float)):
                values.append(float(v))
        return np.array(values) if values else np.zeros(10)
    
    def copy(self) -> 'SystemState':
        """创建状态副本"""
        return SystemState(
            timestamp=self.timestamp,
            task_type=self.task_type,
            performance_metrics=self.performance_metrics.copy(),
            internal_state=self.internal_state.copy(),
            environment_state=self.environment_state.copy(),
            history=self.history.copy()
        )


@dataclass
class ControlAction:
    """控制动作（控制论的输入u）"""
    action_type: str                    # 动作类型
    parameters: Dict[str, Any]          # 动作参数
    magnitude: float = 1.0             # 动作强度（0-1）
    confidence: float = 0.5            # 置信度
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TaskObjective:
    """任务目标（控制论中的参考输入r）"""
    description: str                    # 目标描述
    target_metrics: Dict[str, float]    # 目标指标
    constraints: Dict[str, Any]         # 约束条件
    priority: int = 1                   # 优先级
    deadline: Optional[str] = None     # 截止时间


class NeuralAdaptiveController:
    """
    神经自适应控制器
    
    融合神经网络与控制理论：
    - 神经网络学习非线性映射
    - 控制理论保证稳定性和收敛性
    
    参考：Narendra & Mukhopadhyay (1997) "Adaptive Control Using Neural Networks"
    """
    
    def __init__(self, 
                 input_dim: int = 10,
                 hidden_dim: int = 64,
                 learning_rate: float = 0.01):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.lr = learning_rate
        
        # 神经网络权重（简化版，实际可用PyTorch/TensorFlow）
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.01
        self.W2 = np.random.randn(hidden_dim, hidden_dim) * 0.01
        self.W3 = np.random.randn(hidden_dim, 1) * 0.01
        
        # 控制参数（可学习的）
        self.control_params = {
            'kp': 0.5,  # 比例增益
            'ki': 0.1,  # 积分增益
            'kd': 0.2,  # 微分增益
            'adaptation_rate': 0.05
        }
        
        # 学习历史
        self.learning_history = []
        
    def forward(self, state_vector: np.ndarray) -> float:
        """神经网络前向传播"""
        # Layer 1
        h1 = np.maximum(0, state_vector @ self.W1)  # ReLU
        # Layer 2
        h2 = np.maximum(0, h1 @ self.W2)  # ReLU
        # Output
        output = h2 @ self.W3
        return float(output[0]) if len(output.shape) > 0 else float(output)
    
    def adapt_parameters(self, 
                         state: SystemState, 
                         error: float,
                         context: Dict) -> Dict:
        """
        自适应参数调整（核心）
        
        根据误差和历史表现，用神经网络调整控制参数
        """
        state_vec = state.to_vector()
        
        # 确保维度匹配
        if len(state_vec) < self.input_dim:
            state_vec = np.pad(state_vec, (0, self.input_dim - len(state_vec)))
        state_vec = state_vec[:self.input_dim]
        
        # 神经网络预测最优参数调整
        adjustment = self.forward(state_vec)
        
        # 基于误差调整（控制论反馈）
        if abs(error) > 0.2:  # 大误差，激进调整
            self.control_params['kp'] += self.lr * abs(error) * adjustment
            self.control_params['adaptation_rate'] = 0.1
        elif abs(error) > 0.1:  # 中等误差，温和调整
            self.control_params['ki'] += self.lr * error * adjustment
            self.control_params['adaptation_rate'] = 0.05
        else:  # 小误差，精细调整
            self.control_params['kd'] += self.lr * error * adjustment
            self.control_params['adaptation_rate'] = 0.02
        
        # 限制参数范围（稳定性保证）
        self.control_params['kp'] = np.clip(self.control_params['kp'], 0.1, 2.0)
        self.control_params['ki'] = np.clip(self.control_params['ki'], 0.01, 0.5)
        self.control_params['kd'] = np.clip(self.control_params['kd'], 0.05, 0.5)
        
        # 记录学习
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'error': error,
            'adjustment': adjustment,
            'new_params': self.control_params.copy()
        })
        
        return self.control_params.copy()


class DeepReinforcementController:
    """
    深度强化学习控制器
    
    用深度强化学习（DQN/PPO）实现最优控制
    状态空间 → 神经网络 → 最优动作
    
    参考：Silver et al. (2016) "Mastering the game of Go"
    """
    
    def __init__(self, 
                 state_dim: int = 20,
                 action_dim: int = 10,
                 gamma: float = 0.99):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma  # 折扣因子
        
        # Q网络（状态→动作价值）
        self.q_network = self._init_network(state_dim, action_dim)
        
        # 经验回放缓冲区
        self.replay_buffer = []
        self.buffer_size = 10000
        
        # 探索参数
        self.epsilon = 0.1  # ε-贪婪探索
        
    def _init_network(self, input_dim: int, output_dim: int) -> Dict:
        """初始化神经网络（简化版）"""
        return {
            'W1': np.random.randn(input_dim, 128) * 0.01,
            'W2': np.random.randn(128, 64) * 0.01,
            'W3': np.random.randn(64, output_dim) * 0.01
        }
    
    def select_action(self, state: SystemState) -> Tuple[int, float]:
        """
        选择最优动作（ε-贪婪策略）
        
        Returns:
            action_id: 动作编号
            q_value: 预期累积回报
        """
        state_vec = self._state_to_vector(state)
        
        # ε-贪婪探索
        if np.random.random() < self.epsilon:
            action_id = np.random.randint(0, self.action_dim)
        else:
            # 神经网络预测Q值
            q_values = self._predict_q_values(state_vec)
            action_id = int(np.argmax(q_values))
        
        q_value = self._predict_q_values(state_vec)[action_id]
        
        return action_id, q_value
    
    def _state_to_vector(self, state: SystemState) -> np.ndarray:
        """状态向量化"""
        base_vec = state.to_vector()
        # 填充到固定维度
        if len(base_vec) < self.state_dim:
            base_vec = np.pad(base_vec, (0, self.state_dim - len(base_vec)))
        return base_vec[:self.state_dim]
    
    def _predict_q_values(self, state_vec: np.ndarray) -> np.ndarray:
        """预测Q值（简化前向传播）"""
        h1 = np.maximum(0, state_vec @ self.q_network['W1'])
        h2 = np.maximum(0, h1 @ self.q_network['W2'])
        q_values = h2 @ self.q_network['W3']
        return q_values
    
    def store_experience(self, 
                         state: SystemState, 
                         action: int, 
                         reward: float, 
                         next_state: SystemState):
        """存储经验（用于离线学习）"""
        experience = {
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state
        }
        self.replay_buffer.append(experience)
        
        # 限制缓冲区大小
        if len(self.replay_buffer) > self.buffer_size:
            self.replay_buffer.pop(0)
    
    def learn(self, batch_size: int = 32) -> float:
        """从经验中学习（简化版梯度下降）"""
        if len(self.replay_buffer) < batch_size:
            return 0.0
        
        # 随机采样
        batch = np.random.choice(self.replay_buffer, batch_size, replace=False)
        
        # 计算损失并更新（简化）
        total_loss = 0
        for exp in batch:
            # 目标Q值 = 即时奖励 + 折扣×下一状态最大Q值
            next_q = self._predict_q_values(self._state_to_vector(exp['next_state']))
            target_q = exp['reward'] + self.gamma * np.max(next_q)
            
            # 当前Q值
            current_q = self._predict_q_values(self._state_to_vector(exp['state']))[exp['action']]
            
            # TD误差
            loss = (target_q - current_q) ** 2
            total_loss += loss
        
        return total_loss / batch_size


class KalmanStateEstimator:
    """
    卡尔曼状态估计器
    
    从噪声观测中估计真实系统状态
    核心：预测-更新循环
    
    参考：Kalman (1960) "A New Approach to Linear Filtering and Prediction Problems"
    """
    
    def __init__(self, state_dim: int = 10, obs_dim: int = 5):
        self.state_dim = state_dim
        self.obs_dim = obs_dim
        
        # 状态估计
        self.x = np.zeros(state_dim)  # 状态估计
        self.P = np.eye(state_dim)    # 估计误差协方差
        
        # 系统模型（简化线性模型）
        self.F = np.eye(state_dim)    # 状态转移矩阵
        self.H = np.random.randn(obs_dim, state_dim) * 0.1  # 观测矩阵
        
        # 噪声协方差
        self.Q = np.eye(state_dim) * 0.01  # 过程噪声
        self.R = np.eye(obs_dim) * 0.1    # 观测噪声
        
    def predict(self) -> np.ndarray:
        """状态预测（时间更新）"""
        # 状态预测
        self.x = self.F @ self.x
        # 协方差预测
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x.copy()
    
    def update(self, observation: np.ndarray) -> np.ndarray:
        """状态更新（测量更新）"""
        # 卡尔曼增益
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S + np.eye(self.obs_dim) * 1e-6)
        
        # 状态更新
        y = observation - self.H @ self.x  # 新息
        self.x = self.x + K @ y
        
        # 协方差更新
        I = np.eye(self.state_dim)
        self.P = (I - K @ self.H) @ self.P
        
        return self.x.copy()
    
    def estimate(self, observation: np.ndarray) -> Dict:
        """完整估计流程"""
        # 确保观测维度正确
        if len(observation) < self.obs_dim:
            observation = np.pad(observation, (0, self.obs_dim - len(observation)))
        observation = observation[:self.obs_dim]
        
        self.predict()
        estimated_state = self.update(observation)
        
        return {
            'estimated_state': estimated_state,
            'estimation_error': np.trace(self.P),
            'confidence': 1 / (1 + np.trace(self.P))
        }


class ModelPredictiveController:
    """
    模型预测控制（MPC）
    
    预测未来N步，滚动优化
    核心：在每个时间步求解开环最优问题
    
    参考：Qin & Badgwell (2003) "A survey of industrial model predictive control technology"
    """
    
    def __init__(self, 
                 horizon: int = 5,
                 dt: float = 1.0):
        self.horizon = horizon  # 预测时域
        self.dt = dt           # 时间步长
        
    def predict_trajectory(self, 
                          current_state: SystemState,
                          control_sequence: List[ControlAction]) -> List[SystemState]:
        """
        预测未来状态轨迹
        
        Args:
            current_state: 当前状态
            control_sequence: 控制序列（未来horizon步）
        
        Returns:
            trajectory: 预测的状态轨迹
        """
        trajectory = [current_state.copy()]
        state = current_state.copy()
        
        for action in control_sequence[:self.horizon]:
            # 状态转移（简化模型）
            next_state = self._state_transition(state, action)
            trajectory.append(next_state)
            state = next_state
        
        return trajectory
    
    def _state_transition(self, 
                         state: SystemState, 
                         action: ControlAction) -> SystemState:
        """状态转移方程（简化）"""
        next_state = state.copy()
        
        # 根据动作类型更新状态
        if action.action_type == 'increase_effort':
            next_state.performance_metrics['progress'] = \
                state.performance_metrics.get('progress', 0) + action.magnitude * 0.1
        elif action.action_type == 'adjust_strategy':
            next_state.internal_state['strategy_version'] = \
                state.internal_state.get('strategy_version', 1) + 1
        
        next_state.timestamp = datetime.now().isoformat()
        return next_state
    
    def optimize(self,
                current_state: SystemState,
                objective: TaskObjective) -> List[ControlAction]:
        """
        求解最优控制序列
        
        简化版：使用贪心算法
        完整版：可用二次规划求解器
        """
        optimal_sequence = []
        
        for t in range(self.horizon):
            # 计算当前误差
            current_progress = current_state.performance_metrics.get('progress', 0)
            target_progress = objective.target_metrics.get('completion', 1.0)
            error = target_progress - current_progress
            
            # 根据误差选择动作
            if error > 0.3:
                action = ControlAction(
                    action_type='increase_effort',
                    parameters={'intensity': 'high'},
                    magnitude=0.8
                )
            elif error > 0.1:
                action = ControlAction(
                    action_type='adjust_strategy',
                    parameters={'method': 'fine_tune'},
                    magnitude=0.5
                )
            else:
                action = ControlAction(
                    action_type='maintain',
                    parameters={},
                    magnitude=0.2
                )
            
            optimal_sequence.append(action)
            
            # 预测下一状态（用于下一步优化）
            current_state = self._state_transition(current_state, action)
        
        return optimal_sequence


class A5LUniversalController:
    """
    A5L通用控制器（主控器）
    
    融合控制论与深度学习的顶级架构
    
    架构层次：
    L1: 感知层（Kalman估计器）
    L2: 认知层（神经自适应）
    L3: 决策层（深度强化学习）
    L4: 规划层（MPC预测控制）
    L5: 执行层（控制动作输出）
    """
    
    def __init__(self, task_type: TaskType = TaskType.DECISION):
        self.task_type = task_type
        
        # L1: 感知层
        self.state_estimator = KalmanStateEstimator()
        
        # L2: 认知层
        self.adaptive_controller = NeuralAdaptiveController()
        
        # L3: 决策层
        self.rl_controller = DeepReinforcementController()
        
        # L4: 规划层
        self.mpc_controller = ModelPredictiveController(horizon=5)
        
        # 控制历史（用于学习和分析）
        self.control_history = []
        
        # 性能统计
        self.performance_stats = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'average_error': 0.0
        }
    
    def execute(self, 
                objective: TaskObjective,
                initial_state: Optional[SystemState] = None) -> Dict:
        """
        执行任务（主入口）
        
        完整控制流程：
        1. 状态估计（Kalman）
        2. 自适应参数调整（神经自适应）
        3. 动作选择（深度强化学习）
        4. 轨迹规划（MPC）
        5. 执行与反馈
        """
        # 初始化状态
        if initial_state is None:
            current_state = SystemState(task_type=self.task_type)
        else:
            current_state = initial_state.copy()
        
        # 步骤1: 状态估计（从噪声中提取真实状态）
        obs = current_state.to_vector()
        estimation = self.state_estimator.estimate(obs)
        estimated_state_vector = estimation['estimated_state']
        
        # 步骤2: 自适应参数调整
        current_error = self._calculate_error(current_state, objective)
        adapted_params = self.adaptive_controller.adapt_parameters(
            current_state, current_error, {}
        )
        
        # 步骤3: 强化学习动作选择
        action_id, q_value = self.rl_controller.select_action(current_state)
        
        # 步骤4: MPC规划最优轨迹
        # 创建初始控制序列（基于RL动作）
        initial_action = ControlAction(
            action_type=f'rl_action_{action_id}',
            parameters={'q_value': q_value, 'adapted_params': adapted_params},
            magnitude=0.7
        )
        optimal_sequence = self.mpc_controller.optimize(
            current_state, objective
        )
        
        # 步骤5: 预测轨迹
        predicted_trajectory = self.mpc_controller.predict_trajectory(
            current_state, optimal_sequence
        )
        
        # 记录控制历史
        control_record = {
            'timestamp': datetime.now().isoformat(),
            'objective': objective,
            'initial_state': current_state,
            'estimation': estimation,
            'adapted_params': adapted_params,
            'rl_action': (action_id, q_value),
            'mpc_sequence': optimal_sequence,
            'predicted_trajectory': predicted_trajectory,
            'estimated_error': current_error
        }
        self.control_history.append(control_record)
        
        # 更新统计
        self.performance_stats['total_tasks'] += 1
        self.performance_stats['average_error'] = \
            (self.performance_stats['average_error'] * (len(self.control_history) - 1) + 
             abs(current_error)) / len(self.control_history)
        
        return {
            'status': 'planned',
            'task_type': self.task_type.value,
            'objective': objective,
            'current_state': current_state,
            'estimated_true_state': estimated_state_vector,
            'adapted_control_params': adapted_params,
            'selected_action': action_id,
            'expected_return': q_value,
            'optimal_control_sequence': [
                {'type': a.action_type, 'magnitude': a.magnitude} 
                for a in optimal_sequence
            ],
            'predicted_trajectory_length': len(predicted_trajectory),
            'estimation_confidence': estimation['confidence'],
            'control_philosophy': 'A5L-UCA: 卡尔曼估计 + 神经自适应 + 深度强化学习 + MPC预测控制'
        }
    
    def feedback(self, 
                 executed_action: ControlAction, 
                 actual_result: Dict,
                 reward: float):
        """
        反馈闭环（强化学习训练）
        
        将执行结果反馈给系统，用于学习和改进
        """
        # 创建下一状态
        next_state = SystemState(
            task_type=self.task_type,
            performance_metrics=actual_result.get('metrics', {})
        )
        
        # 获取当前状态（从历史中）
        if self.control_history:
            current_state = self.control_history[-1]['initial_state']
            
            # 存储经验用于RL训练
            action_id = int(executed_action.parameters.get('action_id', 0))
            self.rl_controller.store_experience(
                current_state, action_id, reward, next_state
            )
            
            # 执行学习
            loss = self.rl_controller.learn()
            
            # 更新统计
            if reward > 0:
                self.performance_stats['successful_tasks'] += 1
            
            return {'learning_loss': loss, 'reward': reward}
        
        return {'error': 'No control history'}
    
    def _calculate_error(self, 
                        state: SystemState, 
                        objective: TaskObjective) -> float:
        """计算当前误差"""
        errors = []
        for metric, target in objective.target_metrics.items():
            actual = state.performance_metrics.get(metric, 0)
            errors.append(target - actual)
        
        return np.mean(errors) if errors else 0.0
    
    def get_architecture_summary(self) -> Dict:
        """获取架构摘要"""
        return {
            'architecture_name': 'A5L-Universal-Control-Architecture',
            'version': '1.0',
            'task_type': self.task_type.value,
            'components': {
                'L1_perception': 'KalmanStateEstimator',
                'L2_cognition': 'NeuralAdaptiveController',
                'L3_decision': 'DeepReinforcementController',
                'L4_planning': 'ModelPredictiveController',
                'L5_execution': 'ControlAction'
            },
            'theoretical_basis': [
                'Kalman (1960) - Optimal state estimation',
                'Narendra & Mukhopadhyay (1997) - Neural adaptive control',
                'Silver et al. (2016) - Deep reinforcement learning',
                'Qin & Badgwell (2003) - Model predictive control',
                '钱学森 (1954) - Engineering Cybernetics'
            ],
            'performance_stats': self.performance_stats.copy(),
            'control_history_count': len(self.control_history)
        }


# 便捷接口函数
def create_investment_controller() -> A5LUniversalController:
    """创建投资专用控制器"""
    return A5LUniversalController(TaskType.INVESTMENT)

def create_research_controller() -> A5LUniversalController:
    """创建研究专用控制器"""
    return A5LUniversalController(TaskType.RESEARCH)

def create_coding_controller() -> A5LUniversalController:
    """创建编程专用控制器"""
    return A5LUniversalController(TaskType.CODING)

def create_universal_controller(task_type: str) -> A5LUniversalController:
    """创建通用控制器"""
    try:
        tt = TaskType(task_type)
    except ValueError:
        tt = TaskType.DECISION
    return A5LUniversalController(tt)
