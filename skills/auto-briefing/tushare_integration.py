#!/usr/bin/env python3
"""
A5L日报生成系统 - Tushare数据集成
自动生成包含Tushare数据的日报
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from data_unified import get_data_source
from datetime import datetime, timedelta
import json


class DailyReportTushare:
    """日报Tushare数据集成"""
    
    def __init__(self):
        self.ds = get_data_source()
    
    def generate_market_overview(self) -> dict:
        """生成市场概览"""
        overview = {
            'timestamp': datetime.now().isoformat(),
            'north_money': self._get_north_money_summary(),
            'top_list_summary': self._get_top_list_summary(),
            'news_summary': self._get_news_summary()
        }
        return overview
    
    def _get_north_money_summary(self) -> dict:
        """获取北向资金摘要"""
        try:
            df = self.ds.get_north_money(days=5)
            if len(df) > 0:
                latest = df.iloc[0]
                return {
                    'status': 'success',
                    'latest_date': latest.get('trade_date', ''),
                    'flow_1d': latest.get('north_money', 0),
                    'trend': '流入' if latest.get('north_money', 0) > 0 else '流出'
                }
        except:
            pass
        return {'status': 'error'}
    
    def _get_top_list_summary(self) -> dict:
        """获取龙虎榜摘要"""
        try:
            df = self.ds.get_top_list()
            if len(df) > 0:
                return {
                    'status': 'success',
                    'count': len(df),
                    'hot_sectors': self._extract_hot_sectors(df)
                }
        except:
            pass
        return {'status': 'error'}
    
    def _extract_hot_sectors(self, df) -> list:
        """提取热门板块"""
        # 简化处理，实际应该根据股票所属板块统计
        return ['需进一步分析']
    
    def _get_news_summary(self) -> dict:
        """获取新闻摘要"""
        try:
            df = self.ds.get_major_news()
            if len(df) > 0:
                return {
                    'status': 'success',
                    'count': len(df),
                    'latest_title': str(df.iloc[0].get('title', ''))[:50] if 'title' in df.columns else ''
                }
        except:
            pass
        return {'status': 'error'}
    
    def generate_full_report(self) -> dict:
        """生成完整日报"""
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'type': 'A5L_Daily_Report',
            'market_overview': self.generate_market_overview(),
            'data_sources': {
                'primary': 'Tushare (15000积分会员)',
                'backup': 'AKShare',
                'news': 'Tushare新闻包年会员'
            },
            'generated_at': datetime.now().isoformat()
        }
        return report


if __name__ == '__main__':
    print("="*60)
    print("📰 日报系统Tushare集成测试")
    print("="*60)
    
    report_gen = DailyReportTushare()
    report = report_gen.generate_full_report()
    
    print(f"\n报告日期: {report['date']}")
    print(f"数据源: {report['data_sources']['primary']}")
    
    print("\n市场概览:")
    overview = report['market_overview']
    
    if overview['north_money'].get('status') == 'success':
        print(f"  北向资金: {overview['north_money']['flow_1d']:.2f}万元 ({overview['north_money']['trend']})")
    
    if overview['top_list_summary'].get('status') == 'success':
        print(f"  龙虎榜: {overview['top_list_summary']['count']}只股票上榜")
    
    if overview['news_summary'].get('status') == 'success':
        print(f"  重大新闻: {overview['news_summary']['count']}条")
        print(f"    最新: {overview['news_summary']['latest_title']}")
    
    print("\n✅ 测试完成！")
