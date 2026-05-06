#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Trading Manager
统一交易管理器

整合三大市场（美股/A股/港股）的模拟交易
- 交易时间检查
- 自动记录交易
- 生成分析报告
- 与Skill系统联动
"""

import sys
sys.path.insert(0, '/workspace/projects/workspace/TOOLS')

from trading_time_manager import TradingTimeManager
from trading_analytics_system import TradingAnalyticsSystem
from datetime import datetime
from typing import Dict, Tuple, Optional

class UnifiedTradingManager:
    """统一交易管理器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.time_manager = TradingTimeManager()
        self.analytics = TradingAnalyticsSystem(workspace)
        
        # 加载各市场引擎
        self.engines = {}
        self._init_engines()
    
    def _init_engines(self):
        """初始化各市场引擎"""
        try:
            from us_sim_trading_engine import USSimTradingEngine
            self.engines['US'] = USSimTradingEngine(self.workspace)
        except Exception as e:
            print(f"⚠️ 美股引擎加载失败: {e}")
        
        try:
            from cn_sim_trading_engine import CNSimTradingEngine
            self.engines['CN'] = CNSimTradingEngine(self.workspace)
        except Exception as e:
            print(f"⚠️ A股引擎加载失败: {e}")
        
        try:
            from hk_sim_trading_engine import HKSimTradingEngine
            self.engines['HK'] = HKSimTradingEngine(self.workspace)
        except Exception as e:
            print(f"⚠️ 港股引擎加载失败: {e}")
    
    def execute_trade(self, market: str, symbol: str, action: str, 
                     shares: int, price: float, strategy: str = "manual") -> Dict:
        """
        执行交易（带时间检查）
        
        Args:
            market: US/CN/HK
            symbol: 股票代码
            action: BUY/SELL
            shares: 股数
            price: 价格
            strategy: 策略名称
        
        Returns:
            交易结果
        """
        # 1. 检查交易时间
        can_trade, message = self.time_manager.check_before_trade(market)
        if not can_trade:
            return {
                "success": False,
                "error": message,
                "trade_blocked": True,
                "market": market,
                "timestamp": datetime.now().isoformat()
            }
        
        # 2. 检查引擎
        if market not in self.engines:
            return {
                "success": False,
                "error": f"市场 {market} 引擎未加载",
                "timestamp": datetime.now().isoformat()
            }
        
        engine = self.engines[market]
        
        # 3. 执行交易
        try:
            if action == "BUY":
                result = engine.buy_stock(symbol, price, shares, strategy)
            elif action == "SELL":
                result = engine.sell_stock(symbol, price, shares, strategy)
            else:
                return {
                    "success": False,
                    "error": f"无效操作: {action}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"交易执行失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        
        # 4. 记录交易到分析系统
        if result.get('success') and 'trade' in result:
            trade_record = result['trade']
            trade_record['market'] = market
            self.analytics.record_trade(trade_record, market)
        
        # 5. 添加市场信息到结果
        result['market'] = market
        result['trading_time_check'] = message
        
        return result
    
    def get_portfolio_summary(self, market: Optional[str] = None) -> Dict:
        """获取投资组合摘要"""
        if market:
            if market in self.engines:
                return self.engines[market].get_portfolio_summary()
            return {"error": f"市场 {market} 不可用"}
        
        # 获取所有市场
        summary = {
            "timestamp": datetime.now().isoformat(),
            "markets": {}
        }
        
        for mkt, engine in self.engines.items():
            try:
                summary['markets'][mkt] = engine.get_portfolio_summary()
            except Exception as e:
                summary['markets'][mkt] = {"error": str(e)}
        
        # 计算总值
        total_initial = sum(m.get('initial_capital', 0) for m in summary['markets'].values() if 'initial_capital' in m)
        total_current = sum(m.get('current_equity', 0) for m in summary['markets'].values() if 'current_equity' in m)
        
        summary['total'] = {
            "initial_capital": total_initial,
            "current_equity": total_current,
            "total_pnl": total_current - total_initial,
            "total_pnl_pct": ((total_current - total_initial) / total_initial * 100) if total_initial > 0 else 0
        }
        
        return summary
    
    def get_all_markets_status(self) -> Dict:
        """获取所有市场状态"""
        return self.time_manager.get_all_markets_status()
    
    def generate_daily_report(self) -> str:
        """生成每日交易报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""# 📊 每日交易报告 - {today}

**生成时间**: {datetime.now().strftime('%H:%M:%S')}

---

## 🌍 市场状态

"""
        
        status = self.get_all_markets_status()
        for market, info in status.items():
            icon = "🟢" if info['trading'] else "🔴"
            report += f"{icon} **{market}**: {info['message']}\n\n"
        
        report += """---

## 💰 账户概览

"""
        
        portfolio = self.get_portfolio_summary()
        for market, data in portfolio.get('markets', {}).items():
            if 'error' not in data:
                report += f"""### {market}
- 初始资金: {data.get('initial_capital', 0):,.2f}
- 当前权益: {data.get('current_equity', 0):,.2f}
- 盈亏: {data.get('total_pnl', 0):+.2f} ({data.get('total_pnl_pct', 0):+.2f}%)
- 持仓: {data.get('position_count', 0)} 只
- 交易: {data.get('trade_count', 0)} 笔

"""
        
        if 'total' in portfolio:
            report += f"""### 📈 总计
- 初始资金: {portfolio['total']['initial_capital']:,.2f}
- 当前权益: {portfolio['total']['current_equity']:,.2f}
- 总盈亏: {portfolio['total']['total_pnl']:+.2f} ({portfolio['total']['total_pnl_pct']:+.2f}%)

"""
        
        report += """---

## 🎯 交易统计

"""
        
        # 添加分析系统数据
        analytics_data = self.analytics.generate_skill_feedback()
        report += f"""- 总交易次数: {analytics_data['overall_stats']['total_trades']}
- 总体胜率: {analytics_data['overall_stats']['win_rate']:.1%}
- 使用策略: {', '.join(analytics_data['overall_stats']['strategies_used'])}

"""
        
        if analytics_data['recommendations']:
            report += """### 💡 建议

"""
            for i, rec in enumerate(analytics_data['recommendations'], 1):
                report += f"{i}. {rec}\n"
        
        # 保存报告
        report_file = f"{self.workspace}/data/trading_analytics/daily_report_{today}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("🌍 统一交易管理器")
    print("=" * 70)
    
    manager = UnifiedTradingManager()
    
    # 显示市场状态
    print("\n📊 市场状态:")
    status = manager.get_all_markets_status()
    for market, info in status.items():
        icon = "🟢" if info['trading'] else "🔴"
        print(f"  {icon} {market}: {info['message']}")
    
    # 显示账户概览
    print("\n💰 账户概览:")
    portfolio = manager.get_portfolio_summary()
    for market, data in portfolio.get('markets', {}).items():
        if 'error' not in data:
            print(f"  {market}: {data.get('current_equity', 0):,.2f}")
    
    if 'total' in portfolio:
        print(f"\n  总计: {portfolio['total']['current_equity']:,.2f}")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 生成每日报告...")
    report = manager.generate_daily_report()
    print(report[:800] + "...")

if __name__ == "__main__":
    main()
