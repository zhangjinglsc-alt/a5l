#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Layer 4/5 模拟交易与复盘系统
集成方案 - 2026-05-02

现状:
- ✅ 已有模拟交易引擎 (美股/A股/港股)
- ✅ 已有复盘引擎
- ⚠️ Layer 4/5 需要深度集成这些能力

目标:
1. Layer 4: 执行策略信号 → 自动模拟交易
2. Layer 5: 自动复盘 → 绩效归因 → 策略优化
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

sys.path.insert(0, "/workspace/projects/workspace")

# ============================================================================
# Layer 4: 执行控制层 - 模拟交易执行引擎
# ============================================================================

class TradeAction(Enum):
    """交易动作"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CLOSE = "CLOSE"

@dataclass
class TradeSignal:
    """交易信号"""
    symbol: str
    action: TradeAction
    quantity: int
    price: float
    confidence: float  # 0-1
    strategy: str
    reason: str
    timestamp: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class SimulatedTrade:
    """模拟交易记录"""
    trade_id: str
    symbol: str
    action: str
    quantity: int
    entry_price: float
    exit_price: Optional[float]
    entry_time: str
    exit_time: Optional[str]
    realized_pnl: Optional[float]
    unrealized_pnl: Optional[float]
    strategy: str
    status: str  # OPEN, CLOSED
    review_status: str  # PENDING, REVIEWED

class SimulatedTradingExecutor:
    """
    Layer 4: 模拟交易执行器
    
    核心能力:
    1. 接收策略信号 → 执行模拟交易
    2. 持仓管理 (多市场: 美股/A股/港股)
    3. 盈亏计算 (已实现/未实现)
    4. 风控检查 (止损/止盈/仓位限制)
    5. 交易日志记录
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.data_dir = f"{workspace}/data/sim_trading"
        
        # 确保目录存在
        os.makedirs(f"{self.data_dir}/trades", exist_ok=True)
        os.makedirs(f"{self.data_dir}/positions", exist_ok=True)
        os.makedirs(f"{self.data_dir}/accounts", exist_ok=True)
        os.makedirs(f"{self.data_dir}/reviews", exist_ok=True)
        
        # 加载或初始化账户
        self.accounts = self._load_accounts()
        self.positions = self._load_positions()
        self.trade_history = self._load_trade_history()
    
    def _load_accounts(self) -> Dict:
        """加载账户配置"""
        accounts_file = f"{self.data_dir}/accounts/accounts.json"
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认账户配置
        default_accounts = {
            "US_SIM_001": {
                "name": "美股模拟账户",
                "market": "US",
                "currency": "USD",
                "initial_capital": 100000,
                "available_cash": 100000,
                "total_equity": 100000,
                "margin_used": 0,
                "commission_rate": 0.001,  # 0.1%
                "min_commission": 1.0,
                "risk_per_trade": 0.02,  # 单笔风险2%
                "max_position_pct": 0.3,  # 最大仓位30%
                "trading_hours": "09:30-16:00 EST"
            },
            "CN_SIM_001": {
                "name": "A股模拟账户",
                "market": "CN",
                "currency": "CNY",
                "initial_capital": 1000000,
                "available_cash": 1000000,
                "total_equity": 1000000,
                "commission_rate": 0.0003,  # 0.03%
                "min_commission": 5.0,
                "stamp_duty": 0.001,  # 印花税 0.1%
                "risk_per_trade": 0.02,
                "max_position_pct": 0.3,
                "price_limit": True,  # 涨跌停限制
                "t_plus_1": True,  # T+1
                "trading_hours": "09:30-11:30, 13:00-15:00 CST"
            },
            "HK_SIM_001": {
                "name": "港股模拟账户",
                "market": "HK",
                "currency": "HKD",
                "initial_capital": 800000,
                "available_cash": 800000,
                "total_equity": 800000,
                "commission_rate": 0.0025,  # 0.25%
                "min_commission": 100.0,
                "stamp_duty": 0.001,
                "risk_per_trade": 0.02,
                "max_position_pct": 0.3,
                "t_plus_2": True,  # T+2
                "trading_hours": "09:30-12:00, 13:00-16:00 HKT"
            }
        }
        
        self._save_accounts(default_accounts)
        return default_accounts
    
    def _save_accounts(self, accounts: Dict):
        """保存账户配置"""
        with open(f"{self.data_dir}/accounts/accounts.json", 'w', encoding='utf-8') as f:
            json.dump(accounts, f, indent=2, ensure_ascii=False)
    
    def _load_positions(self) -> Dict:
        """加载持仓"""
        positions_file = f"{self.data_dir}/positions/positions.json"
        if os.path.exists(positions_file):
            with open(positions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {account: {} for account in self.accounts.keys()}
    
    def _save_positions(self):
        """保存持仓"""
        with open(f"{self.data_dir}/positions/positions.json", 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, indent=2, ensure_ascii=False)
    
    def _load_trade_history(self) -> List[Dict]:
        """加载交易历史"""
        history_file = f"{self.data_dir}/trades/trade_history.json"
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_trade_history(self):
        """保存交易历史"""
        with open(f"{self.data_dir}/trades/trade_history.json", 'w', encoding='utf-8') as f:
            json.dump(self.trade_history, f, indent=2, ensure_ascii=False)
    
    def execute_signal(self, signal: TradeSignal, account_id: str = "US_SIM_001") -> Dict:
        """
        执行交易信号
        
        Args:
            signal: 交易信号
            account_id: 账户ID
            
        Returns:
            执行结果
        """
        account = self.accounts.get(account_id)
        if not account:
            return {"success": False, "error": f"账户不存在: {account_id}"}
        
        # 风控检查
        risk_check = self._risk_check(signal, account_id)
        if not risk_check["passed"]:
            return {"success": False, "error": risk_check["reason"]}
        
        # 计算交易成本
        trade_value = signal.quantity * signal.price
        commission = max(trade_value * account["commission_rate"], account["min_commission"])
        
        # A股额外税费
        stamp_duty = 0
        if account["market"] == "CN" and signal.action == TradeAction.SELL:
            stamp_duty = trade_value * account.get("stamp_duty", 0)
        
        total_cost = commission + stamp_duty
        
        # 执行交易
        trade_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
        
        trade_record = {
            "trade_id": trade_id,
            "account_id": account_id,
            "symbol": signal.symbol,
            "action": signal.action.value,
            "quantity": signal.quantity,
            "price": signal.price,
            "trade_value": trade_value,
            "commission": commission,
            "stamp_duty": stamp_duty,
            "total_cost": total_cost,
            "strategy": signal.strategy,
            "reason": signal.reason,
            "confidence": signal.confidence,
            "timestamp": datetime.now().isoformat(),
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "status": "EXECUTED",
            "review_status": "PENDING"
        }
        
        # 更新账户
        if signal.action == TradeAction.BUY:
            account["available_cash"] -= (trade_value + total_cost)
        else:  # SELL
            account["available_cash"] += (trade_value - total_cost)
        
        # 更新持仓
        self._update_positions(signal, account_id)
        
        # 记录交易
        self.trade_history.append(trade_record)
        self._save_trade_history()
        self._save_accounts(self.accounts)
        self._save_positions()
        
        return {
            "success": True,
            "trade_id": trade_id,
            "signal": asdict(signal),
            "costs": {
                "commission": commission,
                "stamp_duty": stamp_duty,
                "total": total_cost
            },
            "account": {
                "available_cash": account["available_cash"],
                "total_equity": account["total_equity"]
            }
        }
    
    def _risk_check(self, signal: TradeSignal, account_id: str) -> Dict:
        """风控检查"""
        account = self.accounts[account_id]
        positions = self.positions.get(account_id, {})
        
        trade_value = signal.quantity * signal.price
        
        # 检查资金
        if signal.action == TradeAction.BUY:
            if trade_value > account["available_cash"]:
                return {"passed": False, "reason": "资金不足"}
        
        # 检查仓位限制
        if signal.action == TradeAction.BUY:
            current_position_value = sum(
                p["quantity"] * p["avg_price"] 
                for p in positions.values()
            )
            new_position_value = current_position_value + trade_value
            
            if new_position_value > account["total_equity"] * account["max_position_pct"]:
                return {"passed": False, "reason": f"超过最大仓位限制 ({account['max_position_pct']*100}%)"}
        
        # 检查信号置信度
        if signal.confidence < 0.6:
            return {"passed": False, "reason": f"信号置信度过低 ({signal.confidence:.2f})"}
        
        return {"passed": True, "reason": ""}
    
    def _update_positions(self, signal: TradeSignal, account_id: str):
        """更新持仓"""
        positions = self.positions.setdefault(account_id, {})
        symbol = signal.symbol
        
        if signal.action == TradeAction.BUY:
            if symbol in positions:
                # 加仓
                pos = positions[symbol]
                total_quantity = pos["quantity"] + signal.quantity
                total_cost = pos["quantity"] * pos["avg_price"] + signal.quantity * signal.price
                pos["avg_price"] = total_cost / total_quantity
                pos["quantity"] = total_quantity
                pos["last_updated"] = datetime.now().isoformat()
            else:
                # 新建仓
                positions[symbol] = {
                    "symbol": symbol,
                    "quantity": signal.quantity,
                    "avg_price": signal.price,
                    "entry_time": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "unrealized_pnl": 0,
                    "stop_loss": signal.stop_loss,
                    "take_profit": signal.take_profit
                }
        
        elif signal.action == TradeAction.SELL:
            if symbol in positions:
                pos = positions[symbol]
                if signal.quantity >= pos["quantity"]:
                    # 清仓
                    realized_pnl = (signal.price - pos["avg_price"]) * pos["quantity"]
                    del positions[symbol]
                else:
                    # 减仓
                    realized_pnl = (signal.price - pos["avg_price"]) * signal.quantity
                    pos["quantity"] -= signal.quantity
                    pos["last_updated"] = datetime.now().isoformat()
    
    def update_prices(self, prices: Dict[str, float], account_id: str = None):
        """
        更新持仓价格，计算浮动盈亏
        
        Args:
            prices: {symbol: current_price}
            account_id: 账户ID (None则更新所有)
        """
        accounts_to_update = [account_id] if account_id else self.accounts.keys()
        
        for acc_id in accounts_to_update:
            positions = self.positions.get(acc_id, {})
            account = self.accounts[acc_id]
            
            total_market_value = 0
            total_unrealized_pnl = 0
            
            for symbol, pos in positions.items():
                if symbol in prices:
                    current_price = prices[symbol]
                    market_value = pos["quantity"] * current_price
                    unrealized_pnl = (current_price - pos["avg_price"]) * pos["quantity"]
                    
                    pos["current_price"] = current_price
                    pos["market_value"] = market_value
                    pos["unrealized_pnl"] = unrealized_pnl
                    
                    total_market_value += market_value
                    total_unrealized_pnl += unrealized_pnl
            
            # 更新账户权益
            account["total_equity"] = account["available_cash"] + total_market_value
            account["unrealized_pnl"] = total_unrealized_pnl
        
        self._save_positions()
        self._save_accounts(self.accounts)
    
    def get_portfolio_summary(self, account_id: str = None) -> Dict:
        """获取投资组合摘要"""
        if account_id:
            return self._get_single_portfolio(account_id)
        
        # 返回所有账户
        return {
            acc_id: self._get_single_portfolio(acc_id)
            for acc_id in self.accounts.keys()
        }
    
    def _get_single_portfolio(self, account_id: str) -> Dict:
        """获取单个账户组合"""
        account = self.accounts[account_id]
        positions = self.positions.get(account_id, {})
        
        return {
            "account_id": account_id,
            "account_name": account["name"],
            "market": account["market"],
            "currency": account["currency"],
            "initial_capital": account["initial_capital"],
            "available_cash": account["available_cash"],
            "total_equity": account["total_equity"],
            "total_return": (account["total_equity"] - account["initial_capital"]) / account["initial_capital"] * 100,
            "unrealized_pnl": account.get("unrealized_pnl", 0),
            "positions_count": len(positions),
            "positions": positions
        }


# ============================================================================
# Layer 5: 复盘引擎 - 交易复盘与策略优化
# ============================================================================

@dataclass
class TradeReview:
    """单笔交易复盘"""
    trade_id: str
    symbol: str
    strategy: str
    entry_quality: int  # 1-10
    exit_quality: int   # 1-10
    timing_score: int   # 1-10
    risk_management: int # 1-10
    lessons: List[str]
    improvements: List[str]
    reviewed_at: str

@dataclass
class DailyReviewReport:
    """每日复盘报告"""
    date: str
    account_id: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_profit: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    strategy_performance: Dict[str, Dict]
    trade_reviews: List[TradeReview]
    summary: str
    action_items: List[str]

class TradingReviewEngine:
    """
    Layer 5: 交易复盘引擎
    
    核心能力:
    1. 每日自动复盘 (21:00触发)
    2. 单笔交易归因分析
    3. 策略绩效跟踪
    4. 错误模式识别
    5. 改进建议生成
    6. 学习反馈循环
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.data_dir = f"{workspace}/data/sim_trading"
        self.review_dir = f"{self.data_dir}/reviews"
        os.makedirs(self.review_dir, exist_ok=True)
    
    def generate_daily_review(self, date: str = None, account_id: str = None) -> DailyReviewReport:
        """
        生成每日复盘报告
        
        Args:
            date: 日期 (默认昨天)
            account_id: 账户ID (None则复盘所有)
            
        Returns:
            每日复盘报告
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 加载交易历史
        trades = self._load_trades_for_date(date, account_id)
        
        if not trades:
            return DailyReviewReport(
                date=date,
                account_id=account_id or "ALL",
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                total_pnl=0,
                avg_profit=0,
                avg_loss=0,
                profit_factor=0,
                max_drawdown=0,
                sharpe_ratio=0,
                strategy_performance={},
                trade_reviews=[],
                summary="今日无交易",
                action_items=[]
            )
        
        # 统计计算
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.get("realized_pnl", 0) > 0]
        losing_trades = [t for t in trades if t.get("realized_pnl", 0) < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        total_pnl = sum(t.get("realized_pnl", 0) for t in trades)
        
        avg_profit = sum(t["realized_pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t["realized_pnl"] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        profit_factor = abs(avg_profit / avg_loss) if avg_loss != 0 else float('inf')
        
        # 策略绩效
        strategy_performance = self._analyze_strategy_performance(trades)
        
        # 单笔交易复盘
        trade_reviews = [self._review_single_trade(t) for t in trades]
        
        # 生成总结和建议
        summary = self._generate_summary(date, total_trades, win_rate, total_pnl)
        action_items = self._generate_action_items(trade_reviews, strategy_performance)
        
        report = DailyReviewReport(
            date=date,
            account_id=account_id or "ALL",
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            total_pnl=total_pnl,
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=0,  # TODO: 计算最大回撤
            sharpe_ratio=0,  # TODO: 计算夏普比率
            strategy_performance=strategy_performance,
            trade_reviews=trade_reviews,
            summary=summary,
            action_items=action_items
        )
        
        # 保存复盘报告
        self._save_review_report(report)
        
        return report
    
    def _load_trades_for_date(self, date: str, account_id: str = None) -> List[Dict]:
        """加载指定日期的交易"""
        history_file = f"{self.data_dir}/trades/trade_history.json"
        if not os.path.exists(history_file):
            return []
        
        with open(history_file, 'r', encoding='utf-8') as f:
            all_trades = json.load(f)
        
        # 筛选日期和账户
        filtered_trades = []
        for trade in all_trades:
            trade_date = trade.get("timestamp", "")[:10]
            if trade_date == date:
                if account_id is None or trade.get("account_id") == account_id:
                    filtered_trades.append(trade)
        
        return filtered_trades
    
    def _analyze_strategy_performance(self, trades: List[Dict]) -> Dict[str, Dict]:
        """分析策略绩效"""
        strategy_stats = {}
        
        for trade in trades:
            strategy = trade.get("strategy", "unknown")
            pnl = trade.get("realized_pnl", 0)
            
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_pnl": 0,
                    "win_rate": 0
                }
            
            stats = strategy_stats[strategy]
            stats["trades"] += 1
            stats["total_pnl"] += pnl
            
            if pnl > 0:
                stats["wins"] += 1
            elif pnl < 0:
                stats["losses"] += 1
        
        # 计算胜率
        for strategy, stats in strategy_stats.items():
            if stats["trades"] > 0:
                stats["win_rate"] = stats["wins"] / stats["trades"]
        
        return strategy_stats
    
    def _review_single_trade(self, trade: Dict) -> TradeReview:
        """复盘单笔交易"""
        # 简单的复盘逻辑 (实际可以更复杂)
        pnl = trade.get("realized_pnl", 0)
        confidence = trade.get("confidence", 0.5)
        
        # 根据盈亏和信号质量评分
        if pnl > 0:
            entry_quality = 7 + int(confidence * 3)  # 7-10
            exit_quality = 8
            timing_score = 7 + int(confidence * 2)   # 7-9
        else:
            entry_quality = max(3, 6 - int(abs(pnl) / 100))
            exit_quality = max(3, 7 - int(abs(pnl) / 100))
            timing_score = 4
        
        risk_management = 7 if trade.get("stop_loss") else 5
        
        # 生成教训
        lessons = []
        improvements = []
        
        if pnl < 0:
            lessons.append("本次交易亏损，需要分析原因")
            if not trade.get("stop_loss"):
                lessons.append("未设置止损，导致亏损扩大")
                improvements.append("严格执行止损纪律")
        
        if confidence < 0.7:
            lessons.append("信号置信度较低，需要提高入场标准")
            improvements.append("提高信号置信度阈值至0.7以上")
        
        return TradeReview(
            trade_id=trade.get("trade_id", ""),
            symbol=trade.get("symbol", ""),
            strategy=trade.get("strategy", ""),
            entry_quality=entry_quality,
            exit_quality=exit_quality,
            timing_score=timing_score,
            risk_management=risk_management,
            lessons=lessons,
            improvements=improvements,
            reviewed_at=datetime.now().isoformat()
        )
    
    def _generate_summary(self, date: str, total_trades: int, win_rate: float, total_pnl: float) -> str:
        """生成复盘总结"""
        if total_trades == 0:
            return f"{date}: 今日无交易"
        
        performance = "盈利" if total_pnl > 0 else "亏损"
        return f"{date}: 今日共{total_trades}笔交易，胜率{win_rate*100:.1f}%，{performance}{abs(total_pnl):.2f}元"
    
    def _generate_action_items(self, trade_reviews: List[TradeReview], strategy_performance: Dict) -> List[str]:
        """生成行动项"""
        action_items = []
        
        # 分析常见问题
        low_rm_count = sum(1 for r in trade_reviews if r.risk_management < 6)
        if low_rm_count > 0:
            action_items.append(f"改进风险管理: {low_rm_count}笔交易风控不足")
        
        # 策略优化建议
        for strategy, stats in strategy_performance.items():
            if stats["win_rate"] < 0.5 and stats["trades"] >= 5:
                action_items.append(f"优化策略'{strategy}': 胜率{stats['win_rate']*100:.1f}%低于50%")
        
        if not action_items:
            action_items.append("继续保持当前交易策略")
        
        return action_items
    
    def _save_review_report(self, report: DailyReviewReport):
        """保存复盘报告"""
        filename = f"{self.review_dir}/review_{report.date}_{report.account_id}.json"
        
        # 将dataclass转换为dict
        report_dict = {
            "date": report.date,
            "account_id": report.account_id,
            "total_trades": report.total_trades,
            "winning_trades": report.winning_trades,
            "losing_trades": report.losing_trades,
            "win_rate": report.win_rate,
            "total_pnl": report.total_pnl,
            "avg_profit": report.avg_profit,
            "avg_loss": report.avg_loss,
            "profit_factor": report.profit_factor,
            "strategy_performance": report.strategy_performance,
            "trade_reviews": [
                {
                    "trade_id": r.trade_id,
                    "symbol": r.symbol,
                    "strategy": r.strategy,
                    "entry_quality": r.entry_quality,
                    "exit_quality": r.exit_quality,
                    "timing_score": r.timing_score,
                    "risk_management": r.risk_management,
                    "lessons": r.lessons,
                    "improvements": r.improvements
                }
                for r in report.trade_reviews
            ],
            "summary": report.summary,
            "action_items": report.action_items
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)


# ============================================================================
# 集成到A5L SKILL
# ============================================================================

class A5LTradingSystem:
    """
    A5L 交易系统集成
    
    整合 Layer 4 (执行) + Layer 5 (复盘)
    """
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.executor = SimulatedTradingExecutor(workspace)
        self.review_engine = TradingReviewEngine(workspace)
    
    def execute_strategy_signal(self, symbol: str, action: str, quantity: int,
                                price: float, strategy: str, confidence: float,
                                account_id: str = "US_SIM_001") -> Dict:
        """
        执行策略信号
        
        这是Layer 4的核心功能：接收Layer 2/3的信号，执行模拟交易
        """
        signal = TradeSignal(
            symbol=symbol,
            action=TradeAction(action),
            quantity=quantity,
            price=price,
            confidence=confidence,
            strategy=strategy,
            reason=f"策略{strategy}生成信号",
            timestamp=datetime.now().isoformat()
        )
        
        return self.executor.execute_signal(signal, account_id)
    
    def run_daily_review(self, date: str = None, account_id: str = None) -> DailyReviewReport:
        """
        运行每日复盘
        
        这是Layer 5的核心功能：自动复盘当日交易
        """
        return self.review_engine.generate_daily_review(date, account_id)
    
    def get_portfolio(self, account_id: str = None) -> Dict:
        """获取投资组合"""
        return self.executor.get_portfolio_summary(account_id)
    
    def update_market_prices(self, prices: Dict[str, float]):
        """更新市场价格"""
        self.executor.update_prices(prices)


def demo():
    """演示"""
    print("="*70)
    print("🚀 A5L Layer 4/5 模拟交易与复盘系统演示")
    print("="*70)
    print()
    
    # 初始化系统
    system = A5LTradingSystem()
    
    # 演示1: 执行交易信号 (Layer 4)
    print("📊 演示1: Layer 4 - 执行策略信号")
    print("-"*70)
    
    signals = [
        ("AAPL", "买入", 10, 180.5, "turtle_trading", 0.85),
        ("NVDA", "买入", 5, 890.0, "trend_rs", 0.78),
        ("TSLA", "买入", 8, 175.3, "volume_price", 0.72),
    ]
    
    for symbol, action, qty, price, strategy, conf in signals:
        result = system.execute_strategy_signal(
            symbol=symbol,
            action=action,
            quantity=qty,
            price=price,
            strategy=strategy,
            confidence=conf,
            account_id="US_SIM_001"
        )
        
        if result["success"]:
            print(f"  ✅ {symbol}: {action}{qty}股 @ ${price} ({strategy})")
            print(f"     交易成本: ${result['costs']['total']:.2f}")
        else:
            print(f"  ❌ {symbol}: {result['error']}")
    
    print()
    
    # 演示2: 查看投资组合
    print("📈 演示2: 投资组合概况")
    print("-"*70)
    
    portfolio = system.get_portfolio("US_SIM_001")
    print(f"  账户: {portfolio['account_name']}")
    print(f"  初始资金: ${portfolio['initial_capital']:,.2f}")
    print(f"  可用现金: ${portfolio['available_cash']:,.2f}")
    print(f"  总资产: ${portfolio['total_equity']:,.2f}")
    print(f"  持仓数: {portfolio['positions_count']}")
    print(f"  收益率: {portfolio['total_return']:.2f}%")
    
    print()
    
    # 演示3: 每日复盘 (Layer 5)
    print("🔄 演示3: Layer 5 - 每日复盘")
    print("-"*70)
    
    # 更新价格 (模拟卖出实现盈亏)
    # 这里简化处理，实际应该从市场获取价格
    
    review = system.run_daily_review(
        date=datetime.now().strftime('%Y-%m-%d'),
        account_id="US_SIM_001"
    )
    
    print(f"  复盘日期: {review.date}")
    print(f"  交易笔数: {review.total_trades}")
    print(f"  胜率: {review.win_rate*100:.1f}%")
    print(f"  总盈亏: ${review.total_pnl:.2f}")
    print(f"  盈亏比: {review.profit_factor:.2f}")
    print()
    print(f"  📋 复盘总结: {review.summary}")
    print()
    print("  📝 行动项:")
    for item in review.action_items:
        print(f"    - {item}")
    
    print()
    print("="*70)
    print("✅ A5L Layer 4/5 演示完成！")
    print("   Layer 4: 策略信号 → 模拟交易执行")
    print("   Layer 5: 自动复盘 → 绩效归因 → 策略优化")
    print("="*70)


if __name__ == "__main__":
    demo()
