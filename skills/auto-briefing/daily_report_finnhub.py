#!/usr/bin/env python3
"""
A5L日报生成系统 - Finnhub美股数据集成
为日报提供美股市场数据和新闻
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from finnhub_client import FinnhubDataSource
from datetime import datetime, timedelta


class DailyReportFinnhub:
    """日报Finnhub数据集成"""
    
    def __init__(self):
        self.finnhub = FinnhubDataSource()
    
    def generate_us_market_summary(self) -> dict:
        """
        生成美股市场摘要 (用于日报)
        
        Returns:
            美股市场摘要
        """
        # 主要科技股
        tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META']
        
        stock_data = []
        for symbol in tech_stocks:
            quote = self.finnhub.get_quote(symbol)
            if quote:
                stock_data.append({
                    'symbol': symbol,
                    'price': quote.get('c'),
                    'change': quote.get('d'),
                    'change_pct': quote.get('dp'),
                    'trend': 'up' if quote.get('d', 0) > 0 else 'down' if quote.get('d', 0) < 0 else 'flat'
                })
        
        # 获取市场新闻
        news = self.finnhub.get_market_news('general')
        
        # 计算市场情绪
        if stock_data:
            up_count = sum(1 for s in stock_data if s['change'] > 0)
            down_count = sum(1 for s in stock_data if s['change'] < 0)
            sentiment = 'bullish' if up_count > down_count else 'bearish' if down_count > up_count else 'neutral'
        else:
            sentiment = 'unknown'
        
        return {
            'timestamp': datetime.now().isoformat(),
            'market': 'US',
            'stocks': stock_data,
            'sentiment': sentiment,
            'top_news': self._format_news(news[:5]),
            'summary': self._generate_summary(stock_data, sentiment)
        }
    
    def _format_news(self, news: list) -> list:
        """格式化新闻"""
        formatted = []
        for item in news:
            formatted.append({
                'headline': item.get('headline', ''),
                'source': item.get('source', ''),
                'datetime': datetime.fromtimestamp(item.get('datetime', 0)).isoformat() if item.get('datetime') else '',
                'summary': item.get('summary', '')[:100] + '...' if item.get('summary') else ''
            })
        return formatted
    
    def _generate_summary(self, stock_data: list, sentiment: str) -> str:
        """生成文字摘要"""
        if not stock_data:
            return '无法获取美股数据'
        
        # 找出涨跌最大
        stock_data_sorted = sorted(stock_data, key=lambda x: abs(x.get('change_pct', 0)), reverse=True)
        top_mover = stock_data_sorted[0] if stock_data_sorted else None
        
        if sentiment == 'bullish':
            sentiment_text = '美股市场整体上涨'
        elif sentiment == 'bearish':
            sentiment_text = '美股市场整体下跌'
        else:
            sentiment_text = '美股市场涨跌互现'
        
        if top_mover:
            direction = '领涨' if top_mover['change'] > 0 else '领跌'
            return f"{sentiment_text}，{top_mover['symbol']} {direction} {abs(top_mover['change_pct']):.2f}%"
        
        return sentiment_text
    
    def get_us_portfolio_summary(self, portfolio: dict) -> dict:
        """
        获取美股持仓摘要 (用于日报)
        
        Args:
            portfolio: 持仓字典 {symbol: shares}
        
        Returns:
            持仓摘要
        """
        positions = []
        total_value = 0
        total_cost = 0  # 需要有成本数据
        
        for symbol, shares in portfolio.items():
            quote = self.finnhub.get_quote(symbol)
            if quote:
                price = quote.get('c', 0)
                value = price * shares
                total_value += value
                
                positions.append({
                    'symbol': symbol,
                    'shares': shares,
                    'price': price,
                    'value': value,
                    'change_pct': quote.get('dp', 0)
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'positions': positions,
            'total_value': total_value,
            'market': 'US'
        }
    
    def generate_full_daily_report(self, us_portfolio: dict = None) -> dict:
        """
        生成完整日报 (包含美股数据)
        
        Args:
            us_portfolio: 美股持仓 (可选)
        
        Returns:
            完整日报
        """
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'type': 'A5L_Daily_Report_v3.0',
            'us_market': self.generate_us_market_summary(),
            'generated_at': datetime.now().isoformat()
        }
        
        if us_portfolio:
            report['us_portfolio'] = self.get_us_portfolio_summary(us_portfolio)
        
        return report


# 快捷函数
def get_us_market_summary() -> dict:
    """快捷获取美股市场摘要"""
    report = DailyReportFinnhub()
    return report.generate_us_market_summary()


def generate_daily_report_with_us(us_portfolio: dict = None) -> dict:
    """快捷生成包含美股的日报"""
    report = DailyReportFinnhub()
    return report.generate_full_daily_report(us_portfolio)


if __name__ == '__main__':
    print("="*70)
    print("📰 日报系统Finnhub集成测试")
    print("="*70)
    
    report_gen = DailyReportFinnhub()
    
    # 测试1: 美股市场摘要
    print("\n📊 测试1: 美股市场摘要")
    summary = report_gen.generate_us_market_summary()
    print(f"市场情绪: {summary['sentiment']}")
    print(f"摘要: {summary['summary']}")
    print(f"主要股票: {len(summary['stocks'])}只")
    
    # 显示涨跌
    for stock in summary['stocks'][:3]:
        emoji = "🟢" if stock['change'] > 0 else "🔴"
        print(f"   {emoji} {stock['symbol']}: ${stock['price']:.2f} ({stock['change_pct']:+.2f}%)")
    
    # 测试2: 持仓摘要
    print("\n📊 测试2: US_SIM_001持仓摘要")
    portfolio = {'NVDA': 100, 'AAPL': 50}
    portfolio_summary = report_gen.get_us_portfolio_summary(portfolio)
    print(f"持仓股票: {len(portfolio_summary['positions'])}只")
    print(f"总市值: ${portfolio_summary['total_value']:,.2f}")
    
    print("\n✅ 测试完成！")
