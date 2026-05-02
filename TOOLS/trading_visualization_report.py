#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Visualization Report Generator
交易可视化报告生成器

功能：
1. 生成ASCII图表（持仓、盈亏、净值曲线）
2. 创建持仓热力图
3. 生成交易分布图
4. 制作每日交割单
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class TradingVisualizationReport:
    """交易可视化报告生成器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.reports_dir = f"{workspace}/data/trading_reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_ascii_chart(self, data: List[float], width: int = 50, height: int = 10) -> str:
        """生成ASCII折线图"""
        if not data:
            return "暂无数据"
        
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        lines = []
        for i in range(height, -1, -1):
            threshold = min_val + (range_val * i / height)
            line = ""
            for j, val in enumerate(data):
                if val >= threshold:
                    line += "█"
                else:
                    line += " "
            lines.append(line)
        
        return "\n".join(lines)
    
    def generate_portfolio_visualization(self, portfolio: Dict, market: str) -> str:
        """生成持仓可视化"""
        positions = portfolio.get('positions', [])
        if not positions:
            return f"\n📊 {market}持仓: 空仓\n"
        
        result = f"\n{'='*60}\n"
        result += f"📊 {market}持仓分布\n"
        result += f"{'='*60}\n\n"
        
        total_value = sum(p.get('market_value', 0) for p in positions)
        
        for pos in positions:
            symbol = pos.get('symbol', 'N/A')
            shares = pos.get('shares', 0)
            price = pos.get('current_price', pos.get('cost_basis', 0))
            cost = pos.get('cost_basis', 0)
            pnl = pos.get('pnl', 0)
            pnl_pct = pos.get('pnl_pct', 0)
            value = pos.get('market_value', shares * price)
            
            pct = (value / total_value * 100) if total_value > 0 else 0
            
            # 盈亏颜色符号
            color_symbol = "🟢" if pnl >= 0 else "🔴"
            
            # 仓位条
            bar_len = int(pct / 2)
            bar = "█" * bar_len + "░" * (25 - bar_len)
            
            result += f"{color_symbol} {symbol:8} {shares:>6}股 @ {price:>8.2f}\n"
            result += f"   盈亏: {pnl:+10.2f} ({pnl_pct:+6.2f}%)\n"
            result += f"   市值: {value:>10.2f} ({pct:5.1f}%) [{bar}]\n\n"
        
        result += f"{'='*60}\n"
        result += f"💰 总持仓市值: {total_value:,.2f}\n"
        
        return result
    
    def generate_pnl_chart(self, daily_pnl: List[float], days: int = 20) -> str:
        """生成盈亏走势图"""
        if not daily_pnl:
            return "暂无盈亏数据\n"
        
        result = "\n📈 每日盈亏走势 (最近20日)\n"
        result += "="*60 + "\n"
        
        # 简化的ASCII图表
        chart = self.generate_ascii_chart(daily_pnl[-days:], width=50, height=8)
        result += chart + "\n"
        
        # 统计
        total = sum(daily_pnl)
        wins = len([p for p in daily_pnl if p > 0])
        losses = len([p for p in daily_pnl if p < 0])
        
        result += f"\n总盈亏: {total:+,.2f}\n"
        result += f"盈利天数: {wins}  亏损天数: {losses}  胜率: {wins/len(daily_pnl)*100:.1f}%\n"
        
        return result
    
    def generate_daily_settlement(self, trades: List[Dict], date: str, market: str) -> str:
        """生成每日交割单"""
        day_trades = [t for t in trades if t.get('timestamp', '').startswith(date) and t.get('market') == market]
        
        result = f"\n{'='*70}\n"
        result += f"📜 {market} 每日交割单 - {date}\n"
        result += f"{'='*70}\n\n"
        
        if not day_trades:
            result += "今日无交易\n"
            return result
        
        result += f"{'时间':<12} {'操作':<6} {'标的':<10} {'数量':<8} {'价格':<10} {'金额':<12} {'盈亏':<12}\n"
        result += "-" * 70 + "\n"
        
        total_pnl = 0
        for trade in day_trades:
            time_str = trade.get('timestamp', '')[11:19]
            action = trade.get('action', '')
            symbol = trade.get('symbol', '')
            shares = trade.get('shares', 0)
            price = trade.get('price', 0)
            amount = trade.get('amount', 0)
            pnl = trade.get('pnl', 0)
            
            total_pnl += pnl if pnl else 0
            
            pnl_str = f"{pnl:+,.2f}" if pnl else "-"
            result += f"{time_str:<12} {action:<6} {symbol:<10} {shares:<8} {price:<10.2f} {amount:<12,.2f} {pnl_str:<12}\n"
        
        result += "-" * 70 + "\n"
        result += f"{'合计':<48} {total_pnl:+,.2f}\n"
        
        return result
    
    def generate_full_report(self, date: Optional[str] = None) -> str:
        """生成完整可视化报告"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           📊 每日交易可视化报告 - {date}                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

生成时间: {datetime.now().strftime('%H:%M:%S')}

"""
        
        # 加载各市场数据
        for market in ["US", "CN", "HK"]:
            account_file = f"{self.workspace}/data/{market.lower()}_sim_trading/accounts/account_main.json"
            positions_file = f"{self.workspace}/data/{market.lower()}_sim_trading/positions/current_positions.json"
            trades_file = f"{self.workspace}/data/{market.lower()}_sim_trading/trades/trade_history.json"
            
            try:
                with open(account_file, 'r') as f:
                    account = json.load(f)
                with open(positions_file, 'r') as f:
                    positions = json.load(f)
                with open(trades_file, 'r') as f:
                    trades = json.load(f)
                
                # 账户概览
                report += f"\n{'─'*70}\n"
                report += f"🏦 {market} 账户概览\n"
                report += f"{'─'*70}\n"
                report += f"初始资金: {account['initial_capital']:>15,.2f}\n"
                report += f"当前权益: {account['current_status']['total_equity']:>15,.2f}\n"
                pnl = account['current_status']['total_equity'] - account['initial_capital']
                pnl_pct = (pnl / account['initial_capital']) * 100
                report += f"累计盈亏: {pnl:>+15,.2f} ({pnl_pct:+.2f}%)\n"
                report += f"可用资金: {account['current_status']['available_funds']:>15,.2f}\n"
                
                # 持仓可视化
                report += self.generate_portfolio_visualization(positions, market)
                
                # 交割单
                report += self.generate_daily_settlement(trades.get('trades', []), date, market)
                
            except Exception as e:
                report += f"\n⚠️ {market}数据加载失败: {e}\n"
        
        # 添加总结
        report += f"\n{'='*70}\n"
        report += "📋 交易总结\n"
        report += f"{'='*70}\n\n"
        
        # 加载分析数据
        try:
            analytics_file = f"{self.workspace}/data/trading_analytics/skill_feedback.json"
            if os.path.exists(analytics_file):
                with open(analytics_file, 'r') as f:
                    feedback = json.load(f)
                
                report += "💡 策略建议:\n"
                for i, rec in enumerate(feedback.get('recommendations', [])[:3], 1):
                    report += f"  {i}. {rec}\n"
        except:
            pass
        
        report += "\n" + "="*70 + "\n"
        report += "报告结束 | 明日继续 📈\n"
        report += "="*70 + "\n"
        
        # 保存报告
        report_file = f"{self.reports_dir}/visual_report_{date}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report

def main():
    """生成今日报告"""
    viz = TradingVisualizationReport()
    report = viz.generate_full_report()
    print(report)

if __name__ == "__main__":
    main()
