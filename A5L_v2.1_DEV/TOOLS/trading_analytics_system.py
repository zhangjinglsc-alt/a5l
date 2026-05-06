#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Record Analytics System
交易记录分析系统

功能：
1. 记录完整交易历史
2. 分析胜率、盈亏比、夏普比率
3. 生成交易复盘报告
4. 与Skill系统关联，持续改进策略
5. 支持三大市场（美股/A股/港股）
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import statistics

@dataclass
class TradeRecord:
    """交易记录"""
    trade_id: str
    market: str  # US/CN/HK
    symbol: str
    action: str  # BUY/SELL
    shares: int
    price: float
    amount: float
    fees: Dict
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    strategy: str = "manual"
    timestamp: str = ""
    notes: str = ""

@dataclass
class DailyPerformance:
    """每日表现"""
    date: str
    market: str
    starting_equity: float
    ending_equity: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float

class TradingAnalyticsSystem:
    """交易分析系统"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.analytics_dir = f"{workspace}/data/trading_analytics"
        os.makedirs(self.analytics_dir, exist_ok=True)
        
        # 分析文件路径
        self.records_file = f"{self.analytics_dir}/all_trades.json"
        self.daily_perf_file = f"{self.analytics_dir}/daily_performance.json"
        self.strategy_perf_file = f"{self.analytics_dir}/strategy_performance.json"
        self.skill_feedback_file = f"{self.analytics_dir}/skill_feedback.json"
        
        # 加载数据
        self.records = self._load_json(self.records_file, [])
        self.daily_perf = self._load_json(self.daily_perf_file, [])
        self.strategy_perf = self._load_json(self.strategy_perf_file, {})
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, filepath: str, data: Any):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def record_trade(self, trade: Dict, market: str) -> str:
        """记录交易"""
        record = TradeRecord(
            trade_id=trade.get('trade_id', f"{market}{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            market=market,
            symbol=trade.get('symbol', ''),
            action=trade.get('action', ''),
            shares=trade.get('shares', 0),
            price=trade.get('price', 0),
            amount=trade.get('amount', 0),
            fees=trade.get('fees', {}),
            pnl=trade.get('pnl'),
            pnl_pct=trade.get('pnl_pct'),
            strategy=trade.get('strategy', 'manual'),
            timestamp=trade.get('timestamp', datetime.now().isoformat()),
            notes=trade.get('notes', '')
        )
        
        self.records.append(asdict(record))
        self._save_json(self.records_file, self.records)
        
        # 更新策略表现
        self._update_strategy_performance(record)
        
        return record.trade_id
    
    def _update_strategy_performance(self, record: TradeRecord):
        """更新策略表现统计"""
        strategy = record.strategy
        if strategy not in self.strategy_perf:
            self.strategy_perf[strategy] = {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "total_pnl": 0.0,
                "avg_pnl": 0.0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "markets": {}
            }
        
        perf = self.strategy_perf[strategy]
        perf["total_trades"] += 1
        
        if record.pnl is not None:
            perf["total_pnl"] += record.pnl
            
            if record.pnl > 0:
                perf["winning_trades"] += 1
            elif record.pnl < 0:
                perf["losing_trades"] += 1
            
            # 计算胜率
            if perf["total_trades"] > 0:
                perf["win_rate"] = perf["winning_trades"] / perf["total_trades"]
            
            # 计算平均盈亏
            perf["avg_pnl"] = perf["total_pnl"] / perf["total_trades"]
            
            # 按市场统计
            market = record.market
            if market not in perf["markets"]:
                perf["markets"][market] = {
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_pnl": 0.0
                }
            perf["markets"][market]["trades"] += 1
            perf["markets"][market]["total_pnl"] += record.pnl
        
        self._save_json(self.strategy_perf_file, self.strategy_perf)
    
    def calculate_daily_performance(self, date: str, market: str) -> DailyPerformance:
        """计算每日表现"""
        # 获取当日交易
        day_trades = [r for r in self.records 
                     if r['timestamp'].startswith(date) and r['market'] == market]
        
        if not day_trades:
            return None
        
        # 统计盈亏交易
        winning_trades = [t for t in day_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in day_trades if t.get('pnl', 0) < 0]
        
        # 计算盈亏
        total_pnl = sum(t.get('pnl', 0) for t in day_trades if t.get('pnl'))
        
        # 计算胜率
        closed_trades = [t for t in day_trades if t.get('pnl') is not None]
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        
        # 计算平均盈亏
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # 计算盈亏比
        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        perf = DailyPerformance(
            date=date,
            market=market,
            starting_equity=0,  # 需要从账户数据获取
            ending_equity=0,
            total_trades=len(day_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            total_pnl=total_pnl,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=0  # 需要计算
        )
        
        return perf
    
    def generate_trading_report(self, days: int = 30) -> str:
        """生成交易报告"""
        report = f"""# 📊 交易分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**统计周期**: 最近{days}天

---

## 📈 总体统计

| 指标 | 数值 |
|------|------|
| 总交易次数 | {len(self.records)} |
| 盈利交易 | {len([r for r in self.records if r.get('pnl', 0) > 0])} |
| 亏损交易 | {len([r for r in self.records if r.get('pnl', 0) < 0])} |
| 胜率 | {self._calculate_overall_win_rate():.1%} |

---

## 🎯 策略表现

"""
        
        for strategy, perf in sorted(self.strategy_perf.items(), 
                                    key=lambda x: x[1].get('win_rate', 0), 
                                    reverse=True):
            report += f"""### {strategy}

- 交易次数: {perf['total_trades']}
- 胜率: {perf['win_rate']:.1%}
- 总盈亏: {perf['total_pnl']:+.2f}
- 平均盈亏: {perf['avg_pnl']:+.2f}

"""
        
        report += """---

## 💡 交易洞察

"""
        
        # 生成洞察
        insights = self._generate_insights()
        for i, insight in enumerate(insights, 1):
            report += f"{i}. {insight}\n"
        
        # 保存报告
        report_file = f"{self.analytics_dir}/trading_report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report
    
    def _calculate_overall_win_rate(self) -> float:
        """计算总体胜率"""
        closed = [r for r in self.records if r.get('pnl') is not None]
        if not closed:
            return 0.0
        wins = len([r for r in closed if r['pnl'] > 0])
        return wins / len(closed)
    
    def _generate_insights(self) -> List[str]:
        """生成交易洞察"""
        insights = []
        
        # 胜率分析
        win_rate = self._calculate_overall_win_rate()
        if win_rate > 0.6:
            insights.append(f"整体胜率{win_rate:.1%}表现优秀，策略有效")
        elif win_rate < 0.4:
            insights.append(f"整体胜率{win_rate:.1%}偏低，需要优化策略")
        
        # 策略对比
        if self.strategy_perf:
            best_strategy = max(self.strategy_perf.items(), 
                              key=lambda x: x[1].get('win_rate', 0))
            insights.append(f"'{best_strategy[0]}'策略胜率最高({best_strategy[1]['win_rate']:.1%})")
        
        # 市场分布
        markets = {}
        for r in self.records:
            m = r['market']
            markets[m] = markets.get(m, 0) + 1
        if markets:
            primary_market = max(markets.items(), key=lambda x: x[1])
            insights.append(f"主要交易市场在{primary_market[0]}({primary_market[1]}笔交易)")
        
        return insights
    
    def generate_skill_feedback(self) -> Dict:
        """
        生成Skill反馈数据
        用于改进交易Skill
        """
        feedback = {
            "generated_at": datetime.now().isoformat(),
            "overall_stats": {
                "total_trades": len(self.records),
                "win_rate": self._calculate_overall_win_rate(),
                "strategies_used": list(self.strategy_perf.keys())
            },
            "strategy_learnings": {},
            "market_patterns": {},
            "recommendations": []
        }
        
        # 策略学习
        for strategy, perf in self.strategy_perf.items():
            feedback["strategy_learnings"][strategy] = {
                "effectiveness": "high" if perf['win_rate'] > 0.55 else "medium" if perf['win_rate'] > 0.45 else "low",
                "avg_pnl": perf['avg_pnl'],
                "best_market": max(perf.get('markets', {}).items(), 
                                  key=lambda x: x[1].get('total_pnl', 0))[0] if perf.get('markets') else None
            }
        
        # 生成建议
        if self._calculate_overall_win_rate() < 0.5:
            feedback["recommendations"].append("胜率低于50%，建议减少交易频率，提高信号质量")
        
        best_strategy = max(self.strategy_perf.items(), 
                          key=lambda x: x[1].get('win_rate', 0)) if self.strategy_perf else None
        if best_strategy and best_strategy[1]['win_rate'] > 0.6:
            feedback["recommendations"].append(f"'{best_strategy[0]}'策略表现优异，可增加仓位配置")
        
        # 保存反馈
        self._save_json(self.skill_feedback_file, feedback)
        
        return feedback

def main():
    """演示"""
    print("=" * 70)
    print("📊 交易记录分析系统")
    print("=" * 70)
    
    analytics = TradingAnalyticsSystem()
    
    print(f"\n📈 已记录交易: {len(analytics.records)} 笔")
    print(f"🎯 使用策略: {len(analytics.strategy_perf)} 个")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 生成交易报告...")
    report = analytics.generate_trading_report()
    print(report[:500] + "...")
    
    # 生成Skill反馈
    print("\n" + "=" * 70)
    print("🧠 生成Skill反馈...")
    feedback = analytics.generate_skill_feedback()
    print(f"✅ 已生成 {len(feedback['recommendations'])} 条建议")

if __name__ == "__main__":
    main()
