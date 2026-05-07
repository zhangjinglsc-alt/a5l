# strategy_cgw_test.py
# 生成时间: 2026-05-08T03:21:30.599820
# 策略来源: CTF + Chief指令
# CTF分级: Tier 1

from a5l.trading import Strategy, Position
from a5l.risk import CTFPositionSizer

class ChinaGreatWall(Strategy):
    """
    中国长城 (000000.SZ) Tier 1策略执行器
    
    CTF分级:
    - Tier: 1 (范式级)
    - 仓位上限: 20-25%
    - 当前仓位: 0%
    - 触发条件: limit_up_broken
    """
    
    def __init__(self):
        super().__init__()
        self.symbol = "000000.SZ"
        self.name = "中国长城"
        self.ctf_tier = 1
        self.position_limit = 0.25
        self.current_position = 0.0
        
    def on_market_open(self):
        """开盘前检查"""
        # 检查是否连续涨停
if self.is_limit_up(days=4):
    self.plan_reduction(
        from_pct=self.current_position,
        to_pct=self.position_limit,
        method="gradual"
    )
    
    def on_market_close(self):
        """收盘后操作"""
        pass  # 无特定收盘逻辑
    
    def execute(self):
        """执行策略"""
        if self.check_limit_up_broken():
    self.reduce_position(
        target_pct=self.position_limit,
        urgency="immediate"
    )
