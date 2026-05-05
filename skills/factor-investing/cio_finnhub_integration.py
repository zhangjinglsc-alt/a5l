#!/usr/bin/env python3
"""
CIO交易系统 - Finnhub美股数据集成
为US_SIM_001提供实时美股数据支持
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from finnhub_client import FinnhubDataSource
from finnhub_websocket import FinnhubWebSocketClient
from datetime import datetime, timedelta
import json


class CIOFinnhubIntegration:
    """CIO交易系统Finnhub数据集成"""
    
    def __init__(self):
        self.finnhub = FinnhubDataSource()
        self.ws_client = None
        self.price_cache = {}
    
    def get_us_stock_quote(self, symbol: str) -> dict:
        """
        获取美股实时报价 (用于US_SIM_001交易决策)
        
        Args:
            symbol: 美股代码 (如 'NVDA', 'AAPL')
        
        Returns:
            实时报价数据
        """
        quote = self.finnhub.get_quote(symbol)
        
        if not quote:
            return {'status': 'error', 'message': '无法获取报价'}
        
        return {
            'status': 'success',
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'price': quote.get('current'),
            'change': quote.get('change'),
            'change_pct': quote.get('change_pct'),
            'open': quote.get('open'),
            'high': quote.get('high'),
            'low': quote.get('low'),
            'prev_close': quote.get('previous_close'),
            'source': 'finnhub'
        }
    
    def get_us_stock_profile(self, symbol: str) -> dict:
        """
        获取美股公司资料 (用于基本面分析)
        
        Args:
            symbol: 美股代码
        
        Returns:
            公司资料
        """
        profile = self.finnhub.get_company_profile(symbol)
        
        return {
            'status': 'success' if profile else 'error',
            'symbol': symbol,
            'name': profile.get('name'),
            'industry': profile.get('industry'),
            'sector': profile.get('sector'),
            'market_cap': profile.get('market_cap'),  # 百万美元
            'country': profile.get('country'),
            'website': profile.get('website')
        }
    
    def get_us_market_news(self, category: str = 'general') -> list:
        """
        获取美股市场新闻 (用于交易决策)
        
        Args:
            category: 新闻类别 (general/forex/crypto/merger)
        
        Returns:
            新闻列表
        """
        news = self.finnhub.get_market_news(category)
        
        formatted_news = []
        for item in news[:10]:  # 只取前10条
            formatted_news.append({
                'headline': item.get('headline'),
                'source': item.get('source'),
                'datetime': item.get('datetime'),
                'url': item.get('url'),
                'summary': item.get('summary', '')[:200] if item.get('summary') else ''
            })
        
        return formatted_news
    
    def get_stock_news(self, symbol: str) -> list:
        """
        获取个股新闻 (用于持仓监控)
        
        Args:
            symbol: 美股代码
        
        Returns:
            新闻列表
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        news = self.finnhub.get_news(
            symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        formatted_news = []
        for item in news[:5]:  # 只取前5条
            formatted_news.append({
                'headline': item.get('headline'),
                'source': item.get('source'),
                'datetime': item.get('datetime'),
                'summary': item.get('summary', '')[:150] if item.get('summary') else ''
            })
        
        return formatted_news
    
    def start_realtime_monitoring(self, symbols: list, callback=None):
        """
        启动实时监控 (用于盘中交易监控)
        
        Args:
            symbols: 监控的股票列表
            callback: 价格变化回调函数
        
        Returns:
            WebSocket客户端
        """
        self.ws_client = FinnhubWebSocketClient()
        
        # 添加价格回调
        def price_handler(symbol, price):
            self.price_cache[symbol] = {
                'price': price,
                'time': datetime.now().isoformat()
            }
            
            if callback:
                callback(symbol, price)
        
        self.ws_client.add_price_callback(price_handler)
        
        # 连接并订阅
        self.ws_client.connect()
        
        # 等待连接
        import time
        time.sleep(2)
        
        # 订阅股票
        for symbol in symbols:
            self.ws_client.subscribe(symbol)
            time.sleep(0.3)
        
        return self.ws_client
    
    def get_realtime_price(self, symbol: str) -> float:
        """获取最新实时价格 (从WebSocket缓存)"""
        if symbol in self.price_cache:
            return self.price_cache[symbol]['price']
        
        # 如果没有缓存，使用REST API
        quote = self.get_us_stock_quote(symbol)
        return quote.get('price')
    
    def analyze_us_stock(self, symbol: str) -> dict:
        """
        综合分析美股 (用于交易前分析)
        
        Args:
            symbol: 美股代码
        
        Returns:
            综合分析报告
        """
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'quote': self.get_us_stock_quote(symbol),
            'profile': self.get_us_stock_profile(symbol),
            'news': self.get_stock_news(symbol)
        }
        
        # 生成交易建议
        analysis['recommendation'] = self._generate_recommendation(analysis)
        
        return analysis
    
    def _generate_recommendation(self, analysis: dict) -> dict:
        """生成交易建议"""
        quote = analysis.get('quote', {})
        
        if quote.get('status') != 'success':
            return {'rating': 'unknown', 'reason': '无法获取数据'}
        
        change_pct = quote.get('change_pct', 0)
        
        # 简单策略：基于涨跌幅
        if change_pct > 5:
            return {
                'rating': 'caution',
                'reason': f'今日已涨{change_pct:.2f}%，追高需谨慎',
                'suggested_action': 'wait_for_pullback'
            }
        elif change_pct < -5:
            return {
                'rating': 'opportunity',
                'reason': f'今日已跌{change_pct:.2f}%，可能存在机会',
                'suggested_action': 'evaluate_entry'
            }
        else:
            return {
                'rating': 'neutral',
                'reason': f'涨跌幅正常({change_pct:.2f}%)',
                'suggested_action': 'monitor'
            }
    
    def get_us_market_summary(self) -> dict:
        """
        获取美股市场摘要 (用于日报)
        
        Returns:
            市场摘要
        """
        # 主要指数
        indices = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']
        
        index_data = []
        for symbol in indices:
            quote = self.get_us_stock_quote(symbol)
            if quote.get('status') == 'success':
                index_data.append({
                    'symbol': symbol,
                    'price': quote.get('price'),
                    'change_pct': quote.get('change_pct')
                })
        
        # 获取市场新闻
        news = self.get_us_market_news()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'indices': index_data,
            'top_news': news[:3],
            'market_sentiment': self._calculate_market_sentiment(index_data)
        }
    
    def _calculate_market_sentiment(self, index_data: list) -> str:
        """计算市场情绪"""
        if not index_data:
            return 'unknown'
        
        up_count = sum(1 for d in index_data if d.get('change_pct', 0) > 0)
        down_count = len(index_data) - up_count
        
        if up_count > down_count * 2:
            return 'very_bullish'
        elif up_count > down_count:
            return 'bullish'
        elif down_count > up_count * 2:
            return 'very_bearish'
        elif down_count > up_count:
            return 'bearish'
        else:
            return 'neutral'


# 快捷函数
def get_us_quote(symbol: str) -> dict:
    """快捷获取美股报价"""
    cio = CIOFinnhubIntegration()
    return cio.get_us_stock_quote(symbol)


def analyze_us_stock(symbol: str) -> dict:
    """快捷分析美股"""
    cio = CIOFinnhubIntegration()
    return cio.analyze_us_stock(symbol)


def get_us_market_summary() -> dict:
    """快捷获取市场摘要"""
    cio = CIOFinnhubIntegration()
    return cio.get_us_market_summary()


if __name__ == '__main__':
    print("="*70)
    print("🇺🇸 CIO Finnhub集成测试")
    print("="*70)
    
    cio = CIOFinnhubIntegration()
    
    # 测试1: 获取NVDA报价
    print("\n📊 测试1: NVDA实时报价")
    result = cio.get_us_stock_quote('NVDA')
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print(f"价格: ${result['price']:.2f}")
        print(f"涨跌幅: {result['change_pct']:.2f}%")
    
    # 测试2: 公司资料
    print("\n📊 测试2: NVDA公司资料")
    result = cio.get_us_stock_profile('NVDA')
    print(f"公司名称: {result.get('name')}")
    print(f"行业: {result.get('industry')}")
    
    # 测试3: 市场新闻
    print("\n📊 测试3: 美股市场新闻")
    news = cio.get_us_market_news()
    print(f"获取到 {len(news)} 条新闻")
    if news:
        print(f"最新: {news[0]['headline'][:50]}...")
    
    # 测试4: 综合分析
    print("\n📊 测试4: NVDA综合分析")
    result = cio.analyze_us_stock('NVDA')
    print(f"交易建议: {result['recommendation']['rating']}")
    print(f"建议操作: {result['recommendation']['reason']}")
    
    print("\n✅ 测试完成！")
