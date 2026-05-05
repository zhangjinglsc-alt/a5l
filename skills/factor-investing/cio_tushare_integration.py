#!/usr/bin/env python3
"""
CIO模拟交易系统 - Tushare数据集成
为CN_SIM_001和HK_SIM_001提供实时数据支持
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from data_unified import get_data_source
from datetime import datetime, timedelta
import pandas as pd


class CIOTushareIntegration:
    """CIO模拟交易Tushare数据集成"""
    
    def __init__(self):
        self.ds = get_data_source()
    
    def get_a_share_quote(self, symbol: str) -> dict:
        """
        获取A股实时行情 (用于CN_SIM_001)
        
        Args:
            symbol: 股票代码 (如 '000001' 或 '000001.SZ')
        
        Returns:
            包含实时行情的字典
        """
        realtime = self.ds.get_a_share_realtime(symbol)
        
        if not realtime:
            return {'status': 'error', 'message': '无法获取行情'}
        
        # 获取历史数据计算涨跌幅
        try:
            hist = self.ds.get_a_share_daily(symbol)
            if len(hist) > 1:
                prev_close = hist.iloc[1]['close'] if 'close' in hist.columns else 0
                current = realtime.get('close', 0)
                change_pct = ((current - prev_close) / prev_close * 100) if prev_close > 0 else 0
            else:
                change_pct = 0
        except:
            change_pct = 0
        
        return {
            'status': 'success',
            'code': symbol,
            'timestamp': datetime.now().isoformat(),
            'price': realtime.get('close', 0),
            'pe': realtime.get('pe', 0),
            'pb': realtime.get('pb', 0),
            'turnover_rate': realtime.get('turnover_rate', 0),
            'change_pct': change_pct,
            'source': realtime.get('source', 'unknown')
        }
    
    def get_a_share_daily_history(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        获取A股历史日线数据
        
        Args:
            symbol: 股票代码
            days: 获取天数
        
        Returns:
            DataFrame包含历史数据
        """
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        return self.ds.get_a_share_daily(symbol, start_date, end_date)
    
    def get_hk_quote(self, symbol: str) -> dict:
        """
        获取港股实时行情 (用于HK_SIM_001)
        
        Args:
            symbol: 港股代码 (如 '00700.HK')
        
        Returns:
            包含实时行情的字典
        """
        try:
            df = self.ds.get_hk_stock_daily(symbol)
            
            if len(df) == 0:
                return {'status': 'error', 'message': '无法获取港股行情'}
            
            latest = df.iloc[0]
            
            return {
                'status': 'success',
                'code': symbol,
                'timestamp': datetime.now().isoformat(),
                'price': latest.get('close', 0),
                'change': latest.get('change', 0),
                'pct_chg': latest.get('pct_chg', 0),
                'volume': latest.get('vol', 0),
                'source': 'tushare'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_stock_fundamentals(self, symbol: str) -> dict:
        """
        获取股票基本面数据 (用于交易决策)
        
        Args:
            symbol: 股票代码
        
        Returns:
            包含基本面分析的字典
        """
        if '.' not in symbol:
            if symbol.startswith('6'):
                symbol = f"{symbol}.SH"
            else:
                symbol = f"{symbol}.SZ"
        
        fundamentals = {
            'code': symbol,
            'timestamp': datetime.now().isoformat(),
            'financial_indicators': self.ds.get_financial_indicators(symbol),
            'valuation': self.ds.get_a_share_realtime(symbol)
        }
        
        # 计算基本面评分
        fundamentals['score'] = self._calculate_fundamental_score(fundamentals)
        
        return fundamentals
    
    def _calculate_fundamental_score(self, fundamentals: dict) -> dict:
        """计算基本面评分"""
        score = 50  # 基础分
        
        indicators = fundamentals.get('financial_indicators', {})
        
        # ROE评分
        roe = indicators.get('roe', 0)
        if roe > 15:
            score += 20
        elif roe > 10:
            score += 10
        
        # 毛利率评分
        gpm = indicators.get('grossprofit_margin', 0)
        if gpm > 30:
            score += 15
        elif gpm > 20:
            score += 10
        
        # 净利率评分
        npm = indicators.get('netprofit_margin', 0)
        if npm > 15:
            score += 15
        elif npm > 10:
            score += 10
        
        return {
            'total': min(100, score),
            'grade': '优秀' if score >= 80 else '良好' if score >= 60 else '一般'
        }
    
    def get_market_sentiment(self) -> dict:
        """
        获取市场情绪数据
        
        Returns:
            市场情绪分析
        """
        try:
            # 北向资金
            north_money = self.ds.get_north_money(days=1)
            north_flow = north_money.iloc[0].get('north_money', 0) if len(north_money) > 0 else 0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'north_money_flow': north_flow,
                'sentiment': '积极' if north_flow > 0 else '谨慎' if north_flow < -50 else '中性',
                'signal': 'bullish' if north_flow > 100 else 'bearish' if north_flow < -100 else 'neutral'
            }
        except:
            return {'status': 'error'}
    
    def screen_stocks(self, criteria: dict) -> pd.DataFrame:
        """
        股票筛选 (用于选股)
        
        Args:
            criteria: 筛选条件
                - min_roe: 最小ROE
                - max_pe: 最大PE
                - min_market_cap: 最小市值
        
        Returns:
            筛选结果DataFrame
        """
        # 获取股票列表
        stocks = self.ds.get_stock_basic()
        
        if len(stocks) == 0:
            return pd.DataFrame()
        
        results = []
        
        # 限制检查数量，避免API调用过多
        check_limit = min(100, len(stocks))
        
        for _, stock in stocks.head(check_limit).iterrows():
            code = stock['ts_code']
            
            try:
                # 获取实时数据
                realtime = self.ds.get_a_share_realtime(code)
                
                if not realtime:
                    continue
                
                pe = realtime.get('pe', 0)
                pb = realtime.get('pb', 0)
                
                # 条件筛选
                if criteria.get('max_pe') and pe > criteria['max_pe']:
                    continue
                if criteria.get('max_pb') and pb > criteria['max_pb']:
                    continue
                
                results.append({
                    'code': code,
                    'name': stock.get('name', ''),
                    'price': realtime.get('close', 0),
                    'pe': pe,
                    'pb': pb
                })
                
            except:
                continue
        
        return pd.DataFrame(results)


# 快捷函数
def get_a_share_quote(symbol: str) -> dict:
    """快捷获取A股行情"""
    cio = CIOTushareIntegration()
    return cio.get_a_share_quote(symbol)


def get_hk_quote(symbol: str) -> dict:
    """快捷获取港股行情"""
    cio = CIOTushareIntegration()
    return cio.get_hk_quote(symbol)


def get_stock_fundamentals(symbol: str) -> dict:
    """快捷获取基本面"""
    cio = CIOTushareIntegration()
    return cio.get_stock_fundamentals(symbol)


if __name__ == '__main__':
    print("="*60)
    print("💼 CIO模拟交易Tushare集成测试")
    print("="*60)
    
    cio = CIOTushareIntegration()
    
    # 测试1: A股行情
    print("\n📊 测试1: A股实时行情 (000001)")
    result = cio.get_a_share_quote('000001')
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print(f"价格: ¥{result['price']:.2f}")
        print(f"PE: {result['pe']:.2f}")
        print(f"PB: {result['pb']:.2f}")
        print(f"涨跌幅: {result['change_pct']:.2f}%")
    
    # 测试2: 基本面
    print("\n📊 测试2: 基本面分析")
    result = cio.get_stock_fundamentals('000001')
    print(f"代码: {result['code']}")
    print(f"基本面评分: {result['score']['total']}")
    print(f"评级: {result['score']['grade']}")
    
    # 测试3: 市场情绪
    print("\n📊 测试3: 市场情绪")
    result = cio.get_market_sentiment()
    if result.get('status') != 'error':
        print(f"北向资金: {result['north_money_flow']:.2f}万元")
        print(f"情绪: {result['sentiment']}")
    
    print("\n✅ 测试完成！")
