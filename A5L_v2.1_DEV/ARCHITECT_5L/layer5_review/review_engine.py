#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5: Review Engine
复盘进化层 - 复盘引擎

功能：
1. 每日21:00自动复盘
2. 交易归因分析
3. 策略绩效跟踪
4. 错误模式识别
5. 改进建议生成

核心原则：绝对诚实，精准归因，持续改进
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TradeRecord:
    """交易记录"""
    symbol: str
    action: str  # BUY, SELL
    shares: int
    price: float
    timestamp: str
    strategy: str
    realized_pnl: Optional[float] = None

@dataclass
class DailyReview:
    """每日复盘"""
    date: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    strategy_performance: Dict[str, Dict]
    errors: List[Dict]
    lessons: List[str]
    improvements: List[str]

class ReviewEngine:
    """复盘引擎"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.review_dir = f"{workspace}/data/architect_5l/reviews"
        self.trade_log_file = f"{workspace}/data/architect_5l/trade_log.json"
        
        os.makedirs(self.review_dir, exist_ok=True)
    
    def generate_daily_review(self, date: Optional[str] = None) -> DailyReview:
        """
        生成每日复盘报告
        
        Args:
            date: 复盘日期 (默认昨天)
        
        Returns:
            每日复盘数据
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 加载交易记录
        trades = self._load_trades_for_date(date)
        
        # 分析交易绩效
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.realized_pnl and t.realized_pnl > 0]
        losing_trades = [t for t in trades if t.realized_pnl and t.realized_pnl < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        total_pnl = sum(t.realized_pnl or 0 for t in trades)
        
        # 策略绩效分析
        strategy_perf = self._analyze_strategy_performance(trades)
        
        # 错误模式识别
        errors = self._identify_error_patterns(trades)
        
        # 生成教训
        lessons = self._generate_lessons(trades, errors)
        
        # 生成改进建议
        improvements = self._generate_improvements(errors, strategy_perf)
        
        review = DailyReview(
            date=date,
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            total_pnl=total_pnl,
            strategy_performance=strategy_perf,
            errors=errors,
            lessons=lessons,
            improvements=improvements
        )
        
        # 保存复盘
        self._save_review(review)
        
        return review
    
    def _load_trades_for_date(self, date: str) -> List[TradeRecord]:
        """加载指定日期的交易记录"""
        if not os.path.exists(self.trade_log_file):
            return []
        
        with open(self.trade_log_file, 'r') as f:
            logs = json.load(f)
        
        trades = []
        for log in logs:
            if log['timestamp'].startswith(date):
                trades.append(TradeRecord(
                    symbol=log.get('symbol', ''),
                    action=log.get('action', ''),
                    shares=log.get('shares', 0),
                    price=log.get('price', 0),
                    timestamp=log['timestamp'],
                    strategy=log.get('strategy', 'unknown'),
                    realized_pnl=log.get('realized_pnl')
                ))
        
        return trades
    
    def _analyze_strategy_performance(self, trades: List[TradeRecord]) -> Dict[str, Dict]:
        """分析各策略绩效"""
        perf = {}
        
        for trade in trades:
            strategy = trade.strategy
            if strategy not in perf:
                perf[strategy] = {
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_pnl": 0,
                    "avg_pnl": 0
                }
            
            perf[strategy]["trades"] += 1
            if trade.realized_pnl:
                perf[strategy]["total_pnl"] += trade.realized_pnl
                if trade.realized_pnl > 0:
                    perf[strategy]["wins"] += 1
                else:
                    perf[strategy]["losses"] += 1
        
        # 计算平均值
        for strategy in perf:
            if perf[strategy]["trades"] > 0:
                perf[strategy]["avg_pnl"] = perf[strategy]["total_pnl"] / perf[strategy]["trades"]
                perf[strategy]["win_rate"] = perf[strategy]["wins"] / perf[strategy]["trades"]
        
        return perf
    
    def _identify_error_patterns(self, trades: List[TradeRecord]) -> List[Dict]:
        """识别错误模式"""
        errors = []
        
        # 检查亏损交易
        losing_trades = [t for t in trades if t.realized_pnl and t.realized_pnl < 0]
        
        if len(losing_trades) >= 3:
            errors.append({
                "type": "consecutive_losses",
                "severity": "high",
                "description": f"当日发生 {len(losing_trades)} 笔亏损交易",
                "count": len(losing_trades),
                "suggestion": "建议暂停交易24小时，检查策略参数"
            })
        
        # 检查大额亏损
        for trade in losing_trades:
            if trade.realized_pnl and trade.realized_pnl < -5000:
                errors.append({
                    "type": "large_loss",
                    "severity": "critical",
                    "description": f"{trade.symbol} 单笔亏损 ¥{abs(trade.realized_pnl):,.2f}",
                    "symbol": trade.symbol,
                    "loss": trade.realized_pnl,
                    "suggestion": "检查止损设置是否生效"
                })
        
        return errors
    
    def _generate_lessons(self, trades: List[TradeRecord], errors: List[Dict]) -> List[str]:
        """生成教训总结"""
        lessons = []
        
        if not trades:
            lessons.append("当日无交易，保持观望也是策略的一部分")
            return lessons
        
        # 分析盈亏比
        winning_trades = [t for t in trades if t.realized_pnl and t.realized_pnl > 0]
        losing_trades = [t for t in trades if t.realized_pnl and t.realized_pnl < 0]
        
        if winning_trades and losing_trades:
            avg_win = sum(t.realized_pnl for t in winning_trades) / len(winning_trades)
            avg_loss = abs(sum(t.realized_pnl for t in losing_trades) / len(losing_trades))
            
            if avg_win < avg_loss * 1.5:
                lessons.append(f"盈亏比 {avg_win/avg_loss:.2f}:1 偏低，建议优化止损策略")
            else:
                lessons.append(f"盈亏比 {avg_win/avg_loss:.2f}:1 健康，继续保持")
        
        # 基于错误的教训
        for error in errors:
            if error["type"] == "consecutive_losses":
                lessons.append(f"连续亏损警示: {error['description']}，需检查市场环境是否变化")
            elif error["type"] == "large_loss":
                lessons.append(f"风控漏洞: {error['symbol']} 产生大额亏损，需复盘入场逻辑")
        
        return lessons
    
    def _generate_improvements(self, errors: List[Dict], strategy_perf: Dict) -> List[str]:
        """生成改进建议"""
        improvements = []
        
        # 基于策略绩效
        if strategy_perf:
            best_strategy = max(strategy_perf.items(), key=lambda x: x[1].get("total_pnl", 0))
            worst_strategy = min(strategy_perf.items(), key=lambda x: x[1].get("total_pnl", 0))
            
            if best_strategy[1].get("total_pnl", 0) > 0:
                improvements.append(f"策略优化: 增加 {best_strategy[0]} 的仓位权重，当前表现最佳")
            
            if worst_strategy[1].get("total_pnl", 0) < 0:
                improvements.append(f"策略审查: 检查 {worst_strategy[0]} 的入场条件，连续亏损需优化")
        
        # 基于错误
        if any(e["type"] == "consecutive_losses" for e in errors):
            improvements.append("风控增强: 建议添加连续亏损3次后自动暂停机制")
        
        if any(e["type"] == "large_loss" for e in errors):
            improvements.append("止损优化: 检查止损单是否有效执行，考虑缩小止损幅度")
        
        return improvements
    
    def _save_review(self, review: DailyReview):
        """保存复盘报告"""
        filename = f"review_{review.date}.json"
        filepath = os.path.join(self.review_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                "date": review.date,
                "total_trades": review.total_trades,
                "winning_trades": review.winning_trades,
                "losing_trades": review.losing_trades,
                "win_rate": review.win_rate,
                "total_pnl": review.total_pnl,
                "strategy_performance": review.strategy_performance,
                "errors": review.errors,
                "lessons": review.lessons,
                "improvements": review.improvements
            }, f, indent=2, ensure_ascii=False)
    
    def generate_review_report(self, review: DailyReview) -> str:
        """生成复盘报告（Markdown格式）"""
        report = f"""# 📊 每日复盘报告 - {review.date}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**复盘周期**: {review.date}

---

## 📈 交易统计

| 指标 | 数值 |
|------|------|
| 总交易次数 | {review.total_trades} |
| 盈利次数 | {review.winning_trades} |
| 亏损次数 | {review.losing_trades} |
| 胜率 | {review.win_rate:.1%} |
| 总盈亏 | ¥{review.total_pnl:,.2f} |

---

## 🎯 策略绩效

| 策略 | 交易次数 | 盈利 | 亏损 | 胜率 | 总盈亏 | 平均盈亏 |
|------|----------|------|------|------|--------|----------|
"""
        
        for strategy, perf in review.strategy_performance.items():
            report += f"| {strategy} | {perf['trades']} | {perf['wins']} | {perf['losses']} | {perf.get('win_rate', 0):.0%} | ¥{perf['total_pnl']:,.2f} | ¥{perf['avg_pnl']:,.2f} |\n"
        
        # 错误分析
        if review.errors:
            report += """
---

## ⚠️ 错误分析

"""
            for error in review.errors:
                icon = "🔴" if error["severity"] == "critical" else "🟡"
                report += f"""{icon} **{error['type']}**
- 描述: {error['description']}
- 建议: {error['suggestion']}

"""
        
        # 教训总结
        report += """
---

## 📝 教训总结

"""
        for i, lesson in enumerate(review.lessons, 1):
            report += f"{i}. {lesson}\n"
        
        # 改进建议
        report += """
---

## 🚀 改进建议

"""
        for i, improvement in enumerate(review.improvements, 1):
            report += f"{i}. {improvement}\n"
        
        report += """
---

## 🎯 明日行动计划

- [ ] 检查策略参数是否需要调整
- [ ] 关注市场环境变化
- [ ] 严格执行风控规则
- [ ] 记录新的交易想法

---

**复盘原则**: 绝对诚实 | 精准归因 | 持续改进
"""
        
        return report
    
    def schedule_daily_review(self):
        """设置每日复盘任务（21:00执行）"""
        # 这里应该设置cron任务
        # 简化实现：返回配置说明
        return {
            "schedule": "0 21 * * *",
            "timezone": "Asia/Shanghai",
            "command": "python3 review_engine.py --daily",
            "description": "每日21:00自动执行复盘"
        }

def main():
    """演示"""
    print("=" * 70)
    print("📊 复盘引擎 (Layer 5)")
    print("=" * 70)
    
    engine = ReviewEngine()
    
    # 生成复盘（模拟数据）
    print("\n📝 生成每日复盘...")
    review = engine.generate_daily_review("2026-05-01")
    
    print(f"\n  日期: {review.date}")
    print(f"  总交易: {review.total_trades} 笔")
    print(f"  胜率: {review.win_rate:.1%}")
    print(f"  总盈亏: ¥{review.total_pnl:,.2f}")
    
    if review.errors:
        print(f"\n  ⚠️ 发现 {len(review.errors)} 个错误:")
        for error in review.errors:
            print(f"    - [{error['severity']}] {error['description']}")
    
    print(f"\n  📝 教训: {len(review.lessons)} 条")
    for lesson in review.lessons:
        print(f"    • {lesson}")
    
    print(f"\n  🚀 改进建议: {len(review.improvements)} 条")
    for imp in review.improvements:
        print(f"    • {imp}")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 复盘报告预览:")
    report = engine.generate_review_report(review)
    print(report[:1000] + "...")
    
    # 定时任务配置
    print("\n⏰ 定时任务配置:")
    schedule = engine.schedule_daily_review()
    print(f"  Cron: {schedule['schedule']}")
    print(f"  时区: {schedule['timezone']}")
    print(f"  说明: {schedule['description']}")

if __name__ == "__main__":
    main()
