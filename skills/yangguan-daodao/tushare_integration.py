#!/usr/bin/env python3
"""
阳关大道 - Tushare数据集成模块
整合Tushare龙虎榜、资金流向、北向资金等数据
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from data_unified import get_data_source
from datetime import datetime, timedelta
import pandas as pd


class YangguanTushareIntegration:
    """阳关大道Tushare数据集成"""
    
    def __init__(self):
        self.ds = get_data_source()
    
    def get_top_list_analysis(self, date: str = None) -> dict:
        """
        获取龙虎榜分析数据
        
        Args:
            date: 日期 (YYYYMMDD)，默认最近交易日
        
        Returns:
            包含龙虎榜统计和热点分析的字典
        """
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        
        # 获取龙虎榜数据
        top_list = self.ds.get_top_list(date)
        top_inst = self.ds.get_top_inst(date)
        
        if len(top_list) == 0:
            return {
                'date': date,
                'status': 'no_data',
                'message': '当日无龙虎榜数据'
            }
        
        # 统计分析
        analysis = {
            'date': date,
            'status': 'success',
            'total_stocks': top_list['ts_code'].nunique(),
            'total_items': len(top_list),
            'buy_amount': top_list['buy_amount'].sum() if 'buy_amount' in top_list.columns else 0,
            'sell_amount': top_list['sell_amount'].sum() if 'sell_amount' in top_list.columns else 0,
            'hot_stocks': self._analyze_hot_stocks(top_list),
            'institution_activity': self._analyze_institutions(top_inst) if len(top_inst) > 0 else {}
        }
        
        return analysis
    
    def _analyze_hot_stocks(self, top_list: pd.DataFrame) -> list:
        """分析热门股票"""
        hot_stocks = []
        
        # 按买入金额排序
        if 'buy_amount' in top_list.columns:
            top_buyers = top_list.nlargest(5, 'buy_amount')
            for _, row in top_buyers.iterrows():
                hot_stocks.append({
                    'code': row['ts_code'],
                    'name': row.get('name', ''),
                    'buy_amount': row.get('buy_amount', 0),
                    'sell_amount': row.get('sell_amount', 0),
                    'reason': row.get('reason', '')
                })
        
        return hot_stocks
    
    def _analyze_institutions(self, top_inst: pd.DataFrame) -> dict:
        """分析机构行为"""
        if len(top_inst) == 0:
            return {}
        
        # 统计机构买卖
        buy_items = top_inst[top_inst['net_amount'] > 0] if 'net_amount' in top_inst.columns else pd.DataFrame()
        sell_items = top_inst[top_inst['net_amount'] < 0] if 'net_amount' in top_inst.columns else pd.DataFrame()
        
        return {
            'inst_buy_count': len(buy_items),
            'inst_sell_count': len(sell_items),
            'inst_buy_amount': buy_items['net_amount'].sum() if len(buy_items) > 0 else 0,
            'inst_sell_amount': sell_items['net_amount'].sum() if len(sell_items) > 0 else 0,
        }
    
    def get_north_money_analysis(self, days: int = 5) -> dict:
        """
        获取北向资金分析
        
        Args:
            days: 分析天数
        
        Returns:
            北向资金分析报告
        """
        df = self.ds.get_north_money(days=days)
        
        if len(df) == 0:
            return {
                'status': 'no_data',
                'message': '无法获取北向资金数据'
            }
        
        # 计算净流入/流出
        latest = df.iloc[0]
        
        analysis = {
            'status': 'success',
            'latest_date': latest.get('trade_date', ''),
            'north_money': latest.get('north_money', 0),
            'south_money': latest.get('south_money', 0),
            'trend': self._analyze_north_trend(df),
            'signal': self._generate_north_signal(df)
        }
        
        return analysis
    
    def _analyze_north_trend(self, df: pd.DataFrame) -> str:
        """分析北向资金趋势"""
        if len(df) < 3:
            return 'insufficient_data'
        
        recent_3d = df.head(3)['north_money'].sum()
        
        if recent_3d > 100:
            return 'strong_inflow'
        elif recent_3d > 0:
            return 'moderate_inflow'
        elif recent_3d > -100:
            return 'moderate_outflow'
        else:
            return 'strong_outflow'
    
    def _generate_north_signal(self, df: pd.DataFrame) -> str:
        """生成北向资金信号"""
        if len(df) < 2:
            return 'neutral'
        
        latest = df.iloc[0]['north_money']
        prev = df.iloc[1]['north_money']
        
        if latest > 50 and prev > 50:
            return 'bullish'
        elif latest < -50 and prev < -50:
            return 'bearish'
        else:
            return 'neutral'
    
    def get_stock_sentiment(self, symbol: str) -> dict:
        """
        获取个股情绪数据
        
        Args:
            symbol: 股票代码
        
        Returns:
            包含龙虎榜、新闻、资金流向的情绪分析
        """
        if '.' not in symbol:
            # 标准化代码
            if symbol.startswith('6'):
                symbol = f"{symbol}.SH"
            else:
                symbol = f"{symbol}.SZ"
        
        sentiment = {
            'code': symbol,
            'top_list': self._check_top_list(symbol),
            'news': self._check_news(symbol),
            'analysis_time': datetime.now().isoformat()
        }
        
        # 综合情绪评分
        sentiment['score'] = self._calculate_sentiment_score(sentiment)
        sentiment['signal'] = self._generate_sentiment_signal(sentiment['score'])
        
        return sentiment
    
    def _check_top_list(self, symbol: str) -> dict:
        """检查股票是否在龙虎榜"""
        date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        top_list = self.ds.get_top_list(date)
        
        if len(top_list) > 0 and symbol in top_list['ts_code'].values:
            item = top_list[top_list['ts_code'] == symbol].iloc[0]
            return {
                'in_top_list': True,
                'date': date,
                'buy_amount': item.get('buy_amount', 0),
                'sell_amount': item.get('sell_amount', 0),
                'reason': item.get('reason', '')
            }
        
        return {'in_top_list': False}
    
    def _check_news(self, symbol: str) -> dict:
        """检查个股新闻"""
        try:
            news = self.ds.get_stock_news(symbol, limit=10)
            if len(news) > 0:
                latest_news = news.iloc[0]
                return {
                    'has_news': True,
                    'count': len(news),
                    'latest_title': str(latest_news.get('title', ''))[:50],
                    'latest_time': latest_news.get('datetime', '')
                }
        except:
            pass
        
        return {'has_news': False}
    
    def _calculate_sentiment_score(self, sentiment: dict) -> int:
        """计算情绪评分 (-100 to 100)"""
        score = 0
        
        # 龙虎榜加分
        if sentiment['top_list'].get('in_top_list'):
            score += 30
        
        # 新闻加分
        if sentiment['news'].get('has_news'):
            score += 10
        
        return min(100, max(-100, score))
    
    def _generate_sentiment_signal(self, score: int) -> str:
        """生成情绪信号"""
        if score > 50:
            return 'very_bullish'
        elif score > 20:
            return 'bullish'
        elif score > -20:
            return 'neutral'
        elif score > -50:
            return 'bearish'
        else:
            return 'very_bearish'
    
    def generate_daily_report(self) -> dict:
        """
        生成每日阳关大道交易报告
        
        Returns:
            包含龙虎榜、北向资金、热点分析的完整报告
        """
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'top_list': self.get_top_list_analysis(),
            'north_money': self.get_north_money_analysis(days=5),
            'recommendations': self._generate_recommendations(),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def _generate_recommendations(self) -> list:
        """生成交易建议"""
        recommendations = []
        
        # 基于北向资金
        north_analysis = self.get_north_money_analysis(days=3)
        if north_analysis.get('signal') == 'bullish':
            recommendations.append({
                'type': 'market_sentiment',
                'signal': 'bullish',
                'message': '北向资金连续净流入，市场情绪积极'
            })
        elif north_analysis.get('signal') == 'bearish':
            recommendations.append({
                'type': 'market_sentiment',
                'signal': 'bearish',
                'message': '北向资金连续净流出，谨慎操作'
            })
        
        # 基于龙虎榜
        top_analysis = self.get_top_list_analysis()
        if top_analysis.get('total_stocks', 0) > 50:
            recommendations.append({
                'type': 'top_list',
                'signal': 'active',
                'message': f'龙虎榜活跃，{top_analysis["total_stocks"]}只股票上榜，关注热点'
            })
        
        return recommendations


# 快捷函数
def get_top_list_analysis(date: str = None) -> dict:
    """快捷获取龙虎榜分析"""
    yg = YangguanTushareIntegration()
    return yg.get_top_list_analysis(date)


def get_north_money_analysis(days: int = 5) -> dict:
    """快捷获取北向资金分析"""
    yg = YangguanTushareIntegration()
    return yg.get_north_money_analysis(days)


def get_stock_sentiment(symbol: str) -> dict:
    """快捷获取个股情绪"""
    yg = YangguanTushareIntegration()
    return yg.get_stock_sentiment(symbol)


def generate_daily_report() -> dict:
    """快捷生成日报"""
    yg = YangguanTushareIntegration()
    return yg.generate_daily_report()


if __name__ == '__main__':
    print("="*60)
    print("🚀 阳关大道Tushare集成测试")
    print("="*60)
    
    yg = YangguanTushareIntegration()
    
    # 测试1: 龙虎榜分析
    print("\n📊 测试1: 龙虎榜分析")
    result = yg.get_top_list_analysis()
    print(f"状态: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"上榜股票: {result['total_stocks']}只")
        print(f"热门股票: {[s['code'] for s in result['hot_stocks'][:3]]}")
    
    # 测试2: 北向资金
    print("\n📊 测试2: 北向资金分析")
    result = yg.get_north_money_analysis(days=5)
    print(f"状态: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"最新北向资金: {result['north_money']}万元")
        print(f"趋势: {result['trend']}")
        print(f"信号: {result['signal']}")
    
    # 测试3: 个股情绪
    print("\n📊 测试3: 个股情绪分析 (000001.SZ)")
    result = yg.get_stock_sentiment('000001')
    print(f"情绪评分: {result['score']}")
    print(f"情绪信号: {result['signal']}")
    print(f"龙虎榜: {'是' if result['top_list']['in_top_list'] else '否'}")
    
    print("\n✅ 测试完成！")
