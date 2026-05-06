#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Trading Scheduler
自动交易调度器

功能：
1. 根据市场开盘时间自动执行交易
2. 收盘后自动生成报告
3. 支持三大市场24小时轮询
4. 与飞书联动发送报告
"""

import sys
sys.path.insert(0, '/workspace/projects/workspace/TOOLS')

from trading_time_manager import TradingTimeManager
from unified_trading_manager import UnifiedTradingManager
from trading_rules_engine import TradingRulesEngine
from trading_visualization_report import TradingVisualizationReport
from blackswan_risk_control import BlackSwanRiskControl
from datetime import datetime, time
from typing import Dict, List, Optional
import json
import os

class AutoTradingScheduler:
    """自动交易调度器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.time_manager = TradingTimeManager()
        self.trading_manager = UnifiedTradingManager(workspace)
        self.rules_engine = TradingRulesEngine(workspace)
        self.viz_report = TradingVisualizationReport(workspace)
        self.risk_control = BlackSwanRiskControl(workspace)
        
        # 状态文件
        self.state_file = f"{workspace}/data/auto_trading_state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_check": None,
            "markets_traded_today": {},
            "reports_sent": {},
            "active": True
        }
    
    def _save_state(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def run_auto_trading_cycle(self) -> Dict:
        """
        执行自动交易周期
        检查各市场状态，在交易时间执行交易
        """
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        
        results = {
            "timestamp": now.isoformat(),
            "markets_checked": [],
            "trades_executed": [],
            "reports_generated": []
        }
        
        print(f"\n{'='*70}")
        print(f"🤖 自动交易周期 - {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # 检查每个市场
        for market in ["US", "CN", "HK"]:
            is_trading, message = self.time_manager.is_trading_time(market)
            results["markets_checked"].append({
                "market": market,
                "trading": is_trading,
                "message": message
            })
            
            status_icon = "🟢" if is_trading else "🔴"
            print(f"\n{status_icon} {market}: {message}")
            
            if is_trading:
                # 执行自动交易
                trades = self._execute_market_trading(market)
                results["trades_executed"].extend(trades)
                
                # 标记今日已交易
                if today not in self.state["markets_traded_today"]:
                    self.state["markets_traded_today"][today] = []
                if market not in self.state["markets_traded_today"][today]:
                    self.state["markets_traded_today"][today].append(market)
            
            else:
                # 检查是否需要发送收盘报告
                if self._should_send_report(market, today):
                    report_path = self._generate_and_send_report(market, today)
                    if report_path:
                        results["reports_generated"].append(report_path)
        
        self.state["last_check"] = now.isoformat()
        self._save_state()
        
        return results
    
    def _execute_market_trading(self, market: str) -> List[Dict]:
        """执行市场交易"""
        trades = []
        
        print(f"\n  🔍 {market} 扫描交易机会...")
        
        # 1. 风控检查
        risk_status = self.risk_control.get_risk_status()
        if risk_status['emergency_mode']:
            print(f"  🚨 紧急模式已激活，暂停{market}交易")
            return trades
        
        if risk_status['exposure_reduction'] >= 100:
            print(f"  🔒 全仓限制，暂停{market}交易")
            return trades
        
        # 2. 获取活跃规则
        rules = self.rules_engine.get_active_rules(market)
        if not rules:
            print(f"  ⚠️  {market} 无活跃交易规则")
            return trades
        
        # 3. 显示市场策略配置
        rule = rules[0]
        holding_style = rule.get('holding_style', 'unknown')
        avg_days = rule.get('avg_holding_days', 0)
        print(f"  📋 策略: {rule['name']} | 持仓风格: {holding_style} | 平均持仓: {avg_days}天")
        
        # 获取关注列表
        account_file = f"{self.workspace}/data/{market.lower()}_sim_trading/accounts/account_main.json"
        try:
            with open(account_file, 'r') as f:
                account = json.load(f)
                watchlist = account.get('watchlist', [])
        except:
            watchlist = []
        
        # 扫描每只标的
        for symbol in watchlist[:5]:  # 只扫描前5只，避免过度交易
            # 生成交易信号
            signal = self.rules_engine.generate_signal(symbol, market, {})
            
            if signal and signal['action'] in ['BUY', 'SELL']:
                print(f"  📊 {symbol}: {signal['action']} 信号 (置信度: {signal['confidence']:.0%})")
                
                # 执行交易
                result = self.trading_manager.execute_trade(
                    market=market,
                    symbol=symbol,
                    action=signal['action'],
                    shares=signal['suggested_shares'],
                    price=0,  # 实际应该用市价或限价
                    strategy=signal['strategy']
                )
                
                if result.get('success'):
                    trades.append(result)
                    print(f"  ✅ {symbol}: 交易执行成功")
                elif result.get('trade_blocked'):
                    print(f"  ⏸️  {symbol}: {result.get('error', '交易被阻止')}")
                else:
                    print(f"  ❌ {symbol}: {result.get('error', '交易失败')}")
        
        return trades
    
    def _should_send_report(self, market: str, today: str) -> bool:
        """检查是否应该发送报告"""
        # 如果今天已经交易过且还没发报告
        traded_today = today in self.state.get("markets_traded_today", {}) and \
                      market in self.state["markets_traded_today"].get(today, [])
        
        reported_today = today in self.state.get("reports_sent", {}) and \
                        market in self.state["reports_sent"].get(today, [])
        
        return traded_today and not reported_today
    
    def _generate_and_send_report(self, market: str, date: str) -> Optional[str]:
        """生成并发送报告"""
        print(f"\n  📄 {market} 生成收盘报告...")
        
        # 生成可视化报告
        report = self.viz_report.generate_full_report(date)
        
        # 保存报告
        report_file = f"{self.workspace}/data/trading_reports/{market}_report_{date}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 标记已发送
        if date not in self.state["reports_sent"]:
            self.state["reports_sent"][date] = []
        self.state["reports_sent"][date].append(market)
        self._save_state()
        
        print(f"  ✅ 报告已保存: {report_file}")
        
        return report_file
    
    def generate_daily_summary(self) -> str:
        """生成每日交易总结"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        summary = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              📊 每日交易总结 - {today}                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

生成时间: {datetime.now().strftime('%H:%M:%S')}

"""
        
        # 加载分析数据
        analytics_file = f"{self.workspace}/data/trading_analytics/skill_feedback.json"
        if os.path.exists(analytics_file):
            with open(analytics_file, 'r') as f:
                feedback = json.load(f)
            
            summary += "📈 今日统计\n"
            summary += "─" * 60 + "\n"
            stats = feedback.get('overall_stats', {})
            summary += f"总交易次数: {stats.get('total_trades', 0)}\n"
            summary += f"总体胜率: {stats.get('win_rate', 0):.1%}\n"
            summary += f"活跃策略: {', '.join(stats.get('strategies_used', []))}\n\n"
        
        # 各市场状态
        summary += "🌍 市场状态\n"
        summary += "─" * 60 + "\n"
        status = self.time_manager.get_all_markets_status()
        for market, info in status.items():
            icon = "🟢" if info['trading'] else "🔴"
            summary += f"{icon} {market}: {info['message']}\n"
        
        summary += "\n" + "="*60 + "\n"
        summary += "明日继续 📈\n"
        
        return summary

def main():
    """运行自动交易调度"""
    print("=" * 70)
    print("🤖 自动交易调度器启动")
    print("=" * 70)
    
    scheduler = AutoTradingScheduler()
    
    # 执行一个周期
    results = scheduler.run_auto_trading_cycle()
    
    # 生成总结
    print("\n" + "=" * 70)
    summary = scheduler.generate_daily_summary()
    print(summary)
    
    # 保存总结
    today = datetime.now().strftime('%Y-%m-%d')
    summary_file = f"{scheduler.workspace}/data/trading_reports/daily_summary_{today}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n✅ 调度完成，总结已保存")

if __name__ == "__main__":
    main()
