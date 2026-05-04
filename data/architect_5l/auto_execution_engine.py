#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Week 7: 自动化执行引擎
Auto-Execution Engine with signal-to-trade闭环
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class ExecutionMode(Enum):
    """执行模式"""
    MANUAL = "manual"          # 人工确认
    SEMI_AUTO = "semi_auto"    # 半自动 (大金额人工确认)
    FULL_AUTO = "full_auto"    # 全自动

class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class ExecutionOrder:
    """执行订单"""
    execution_id: str
    signal_id: str
    symbol: str
    action: str  # buy/sell
    quantity: int
    price: float
    mode: ExecutionMode
    status: ExecutionStatus
    created_at: str
    executed_at: Optional[str] = None
    error_message: Optional[str] = None

class AutoExecutionEngine:
    """自动化执行引擎"""
    
    def __init__(self, execution_mode: ExecutionMode = ExecutionMode.SEMI_AUTO):
        self.execution_mode = execution_mode
        self.pending_signals = []
        self.execution_history = []
        self.execution_counter = 0
        
        # 风控参数
        self.max_single_trade_value = 50000  # 单笔最大5万
        self.daily_trade_limit = 10          # 日交易次数限制
        self.today_trade_count = 0
        
        # 回调函数
        self.pre_execution_checks = []
        self.post_execution_hooks = []
        
    def register_pre_check(self, check_func: Callable):
        """注册前置检查"""
        self.pre_execution_checks.append(check_func)
    
    def register_post_hook(self, hook_func: Callable):
        """注册后置钩子"""
        self.post_execution_hooks.append(hook_func)
    
    def _generate_execution_id(self) -> str:
        """生成执行ID"""
        self.execution_counter += 1
        return f"EXEC{datetime.now().strftime('%Y%m%d%H%M%S')}{self.execution_counter:04d}"
    
    def receive_signal(self, signal: Dict) -> ExecutionOrder:
        """
        接收交易信号并创建执行订单
        
        流程:
        1. 验证信号有效性
        2. 确定执行模式
        3. 创建执行订单
        4. 根据模式决定是否立即执行
        """
        
        # 验证信号
        if not self._validate_signal(signal):
            print(f"❌ 信号无效，拒绝执行")
            return None
        
        # 确定执行模式
        trade_value = signal.get("quantity", 0) * signal.get("price", 0)
        
        if self.execution_mode == ExecutionMode.MANUAL:
            mode = ExecutionMode.MANUAL
        elif self.execution_mode == ExecutionMode.SEMI_AUTO:
            # 大额交易需要人工确认
            if trade_value > self.max_single_trade_value:
                mode = ExecutionMode.MANUAL
                print(f"⚠️  交易金额超过阈值 (¥{trade_value:,.0f} > ¥{self.max_single_trade_value:,.0f})，需要人工确认")
            else:
                mode = ExecutionMode.FULL_AUTO
        else:
            mode = ExecutionMode.FULL_AUTO
        
        # 创建执行订单
        order = ExecutionOrder(
            execution_id=self._generate_execution_id(),
            signal_id=signal.get("signal_id", "UNKNOWN"),
            symbol=signal.get("symbol", ""),
            action=signal.get("action", "buy"),
            quantity=signal.get("quantity", 0),
            price=signal.get("price", 0.0),
            mode=mode,
            status=ExecutionStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        self.pending_signals.append(order)
        
        print(f"📨 信号接收: {order.symbol} {order.action} {order.quantity}股 @ ¥{order.price:.2f}")
        print(f"   执行模式: {mode.value}")
        print(f"   执行ID: {order.execution_id}")
        
        # 自动执行 (全自动模式)
        if mode == ExecutionMode.FULL_AUTO:
            self.execute_order(order.execution_id)
        else:
            print(f"   ⏸️  等待人工确认...")
        
        return order
    
    def _validate_signal(self, signal: Dict) -> bool:
        """验证信号有效性"""
        required_fields = ["symbol", "action", "quantity", "price"]
        
        for field in required_fields:
            if field not in signal:
                print(f"   ⚠️  信号缺少字段: {field}")
                return False
        
        # 检查日交易次数限制
        if self.today_trade_count >= self.daily_trade_limit:
            print(f"   ⚠️  日交易次数已达上限 ({self.daily_trade_limit})")
            return False
        
        return True
    
    def execute_order(self, execution_id: str) -> bool:
        """执行订单"""
        # 查找订单
        order = None
        for o in self.pending_signals:
            if o.execution_id == execution_id:
                order = o
                break
        
        if not order:
            print(f"❌ 订单不存在: {execution_id}")
            return False
        
        # 前置检查
        print(f"\n🔍 执行前置检查...")
        for check in self.pre_execution_checks:
            passed, message = check(order)
            if not passed:
                order.status = ExecutionStatus.FAILED
                order.error_message = message
                print(f"   ❌ 前置检查失败: {message}")
                return False
        print(f"   ✅ 所有前置检查通过")
        
        # 执行交易
        order.status = ExecutionStatus.EXECUTING
        print(f"\n🚀 执行交易: {order.symbol} {order.action} {order.quantity}股")
        
        try:
            # 模拟交易执行
            time.sleep(0.5)
            
            # 模拟成交价格 (滑点)
            executed_price = order.price * (1 + random.uniform(-0.001, 0.001))
            
            order.status = ExecutionStatus.COMPLETED
            order.executed_at = datetime.now().isoformat()
            self.today_trade_count += 1
            
            print(f"   ✅ 交易成功")
            print(f"   成交价格: ¥{executed_price:.2f}")
            print(f"   成交金额: ¥{executed_price * order.quantity:,.2f}")
            
            # 后置钩子
            for hook in self.post_execution_hooks:
                hook(order)
            
            # 移出待处理列表
            self.pending_signals.remove(order)
            self.execution_history.append(order)
            
            return True
            
        except Exception as e:
            order.status = ExecutionStatus.FAILED
            order.error_message = str(e)
            print(f"   ❌ 交易失败: {e}")
            return False
    
    def manual_confirm(self, execution_id: str, confirmed: bool, user: str) -> bool:
        """人工确认"""
        for order in self.pending_signals:
            if order.execution_id == execution_id:
                if confirmed:
                    print(f"✅ 人工确认通过 (by {user})")
                    return self.execute_order(execution_id)
                else:
                    order.status = ExecutionStatus.FAILED
                    order.error_message = f"人工拒绝 (by {user})"
                    print(f"❌ 人工拒绝 (by {user})")
                    return False
        return False
    
    def rollback_order(self, execution_id: str) -> bool:
        """回滚订单"""
        for order in self.execution_history:
            if order.execution_id == execution_id:
                # 模拟回滚
                order.status = ExecutionStatus.ROLLED_BACK
                print(f"🔄 订单已回滚: {execution_id}")
                return True
        return False
    
    def get_execution_summary(self) -> Dict:
        """获取执行汇总"""
        completed = [o for o in self.execution_history if o.status == ExecutionStatus.COMPLETED]
        failed = [o for o in self.execution_history if o.status == ExecutionStatus.FAILED]
        pending = [o for o in self.pending_signals if o.status == ExecutionStatus.PENDING]
        
        return {
            "total_executions": len(self.execution_history),
            "completed": len(completed),
            "failed": len(failed),
            "pending": len(pending),
            "today_trade_count": self.today_trade_count,
            "success_rate": len(completed) / len(self.execution_history) * 100 if self.execution_history else 0
        }


# 前置检查函数
def check_market_open(order: ExecutionOrder) -> tuple:
    """检查市场是否开放"""
    from trading_calendar import TradingCalendar
    calendar = TradingCalendar()
    can_trade, reason = calendar.validate_trade()
    
    if not can_trade:
        return False, f"市场休市: {reason}"
    return True, "市场开放"

def check_position_limit(order: ExecutionOrder) -> tuple:
    """检查仓位限制"""
    # 模拟仓位检查
    max_position = 100000
    current_position = 50000  # 模拟当前持仓
    
    new_position = current_position + (order.quantity * order.price)
    
    if new_position > max_position:
        return False, f"超出仓位限制 (当前: {current_position}, 新增后: {new_position}, 限制: {max_position})"
    
    return True, "仓位检查通过"

def check_risk_level(order: ExecutionOrder) -> tuple:
    """检查风险等级"""
    # 模拟风险检查
    risk_score = random.randint(1, 100)
    
    if risk_score > 80:
        return False, f"风险评分过高 ({risk_score}/100)，禁止交易"
    
    return True, f"风险评分正常 ({risk_score}/100)"


def demo():
    """自动化执行引擎演示"""
    print("=" * 70)
    print("🤖 A5L Week 7: 自动化执行引擎演示")
    print("=" * 70)
    
    # 创建引擎 (半自动模式)
    engine = AutoExecutionEngine(execution_mode=ExecutionMode.SEMI_AUTO)
    
    # 注册前置检查
    print("\n【注册前置检查】")
    print("-" * 70)
    engine.register_pre_check(check_market_open)
    engine.register_pre_check(check_position_limit)
    engine.register_pre_check(check_risk_level)
    print("✅ 前置检查注册完成")
    
    # 场景1: 小额交易 (全自动)
    print("\n【场景1: 小额交易 - 全自动执行】")
    print("-" * 70)
    
    signal1 = {
        "signal_id": "SIG001",
        "symbol": "000066",
        "action": "buy",
        "quantity": 100,
        "price": 19.82
    }
    
    order1 = engine.receive_signal(signal1)
    
    # 场景2: 大额交易 (需人工确认)
    print("\n【场景2: 大额交易 - 需人工确认】")
    print("-" * 70)
    
    signal2 = {
        "signal_id": "SIG002",
        "symbol": "000858",
        "action": "buy",
        "quantity": 3000,  # 大额
        "price": 434.54
    }
    
    order2 = engine.receive_signal(signal2)
    
    # 人工确认
    if order2 and order2.mode == ExecutionMode.MANUAL:
        print(f"\n👤 人工审核中...")
        time.sleep(1)
        engine.manual_confirm(order2.execution_id, confirmed=True, user="CIO")
    
    # 场景3: 风控拒绝
    print("\n【场景3: 风控检查拒绝】")
    print("-" * 70)
    
    # 模拟高风险信号
    signal3 = {
        "signal_id": "SIG003",
        "symbol": "300001",
        "action": "buy",
        "quantity": 10000,
        "price": 50.0
    }
    
    # 强制设置高风险 (通过mock)
    original_random = random.randint
    random.randint = lambda a, b: 85  # 强制返回85分 (高风险)
    
    order3 = engine.receive_signal(signal3)
    
    random.randint = original_random  # 恢复
    
    # 执行汇总
    print("\n【执行汇总】")
    print("-" * 70)
    summary = engine.get_execution_summary()
    
    print(f"总执行数: {summary['total_executions']}")
    print(f"成功: {summary['completed']}")
    print(f"失败: {summary['failed']}")
    print(f"待处理: {summary['pending']}")
    print(f"今日交易: {summary['today_trade_count']}")
    print(f"成功率: {summary['success_rate']:.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ 自动化执行引擎演示完成!")
    print("=" * 70)
    print("\n💡 生产环境增强:")
    print("   • 与券商API对接 (实盘交易)")
    print("   • 分布式执行 (高并发)")
    print("   • 智能订单路由 (最优成交)")
    print("   • 异常自动回滚与恢复")


if __name__ == "__main__":
    import random
    demo()
