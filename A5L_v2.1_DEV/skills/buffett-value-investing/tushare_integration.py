#!/usr/bin/env python3
"""
价值投资 - Tushare财务数据集成
使用Tushare完整财务三表进行深入分析
"""

import sys
import os
sys.path.insert(0, '/workspace/projects/workspace')
sys.path.insert(0, '/workspace/projects/workspace/tools')

from data_unified import get_data_source
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class ValueInvestingTushare:
    """价值投资Tushare数据集成"""
    
    def __init__(self):
        self.ds = get_data_source()
    
    def get_full_financial_analysis(self, symbol: str) -> dict:
        """
        获取完整财务分析
        
        Args:
            symbol: 股票代码
        
        Returns:
            包含三表分析的字典
        """
        if '.' not in symbol:
            if symbol.startswith('6'):
                symbol = f"{symbol}.SH"
            else:
                symbol = f"{symbol}.SZ"
        
        analysis = {
            'code': symbol,
            'timestamp': datetime.now().isoformat(),
            'income_statement': self._analyze_income(symbol),
            'balance_sheet': self._analyze_balance(symbol),
            'cash_flow': self._analyze_cashflow(symbol),
            'financial_indicators': self._analyze_indicators(symbol),
            'valuation_metrics': self._calculate_valuation(symbol)
        }
        
        # 综合评分
        analysis['overall_score'] = self._calculate_overall_score(analysis)
        analysis['investment_recommendation'] = self._generate_recommendation(analysis)
        
        return analysis
    
    def _analyze_income(self, symbol: str) -> dict:
        """分析利润表"""
        df = self.ds.get_financial_report(symbol, 'income')
        
        if len(df) == 0:
            return {'status': 'no_data'}
        
        latest = df.iloc[0]
        
        return {
            'status': 'success',
            'latest_period': latest.get('end_date', ''),
            'total_revenue': latest.get('total_revenue', 0),  # 营业总收入
            'revenue': latest.get('revenue', 0),  # 营业收入
            'operate_profit': latest.get('operate_profit', 0),  # 营业利润
            'total_profit': latest.get('total_profit', 0),  # 利润总额
            'n_income': latest.get('n_income', 0),  # 净利润
            'income_trend': self._calculate_trend(df, 'n_income') if len(df) > 1 else None
        }
    
    def _analyze_balance(self, symbol: str) -> dict:
        """分析资产负债表"""
        df = self.ds.get_financial_report(symbol, 'balance')
        
        if len(df) == 0:
            return {'status': 'no_data'}
        
        latest = df.iloc[0]
        
        return {
            'status': 'success',
            'latest_period': latest.get('end_date', ''),
            'total_assets': latest.get('total_assets', 0),  # 总资产
            'total_liab': latest.get('total_liab', 0),  # 总负债
            'total_hldr_eqy': latest.get('total_hldr_eqy', 0),  # 股东权益
            'debt_to_asset': latest.get('total_liab', 0) / latest.get('total_assets', 1) if latest.get('total_assets', 0) > 0 else None,
            'equity_ratio': latest.get('total_hldr_eqy', 0) / latest.get('total_assets', 1) if latest.get('total_assets', 0) > 0 else None
        }
    
    def _analyze_cashflow(self, symbol: str) -> dict:
        """分析现金流量表"""
        df = self.ds.get_financial_report(symbol, 'cashflow')
        
        if len(df) == 0:
            return {'status': 'no_data'}
        
        latest = df.iloc[0]
        
        return {
            'status': 'success',
            'latest_period': latest.get('end_date', ''),
            'c_cash_equ': latest.get('c_cash_equ_end_period', 0),  # 期末现金余额
            'n_cashflow_act': latest.get('n_cashflow_act', 0),  # 经营活动现金流
            'n_cashflow_inv': latest.get('n_cashflow_inv_act', 0),  # 投资活动现金流
            'n_cashflow_fin': latest.get('n_cashflow_fin_act', 0),  # 筹资活动现金流
            'free_cash_flow': self._calculate_fcf(latest)
        }
    
    def _calculate_fcf(self, row) -> float:
        """计算自由现金流"""
        ocf = row.get('n_cashflow_act', 0)  # 经营现金流
        capex = abs(row.get('c_pay_acq_const_foli', 0))  # 资本支出
        return ocf - capex
    
    def _analyze_indicators(self, symbol: str) -> dict:
        """分析财务指标"""
        df = self.ds.get_financial_indicators(symbol)
        
        if len(df) == 0:
            return {'status': 'no_data'}
        
        latest = df.iloc[0]
        
        return {
            'status': 'success',
            'roe': latest.get('roe', 0),  # 净资产收益率
            'roa': latest.get('roa', 0),  # 总资产收益率
            'grossprofit_margin': latest.get('grossprofit_margin', 0),  # 毛利率
            'netprofit_margin': latest.get('netprofit_margin', 0),  # 净利率
            'debt_to_assets': latest.get('debt_to_assets', 0),  # 资产负债率
            'current_ratio': latest.get('current_ratio', 0),  # 流动比率
            'quick_ratio': latest.get('quick_ratio', 0),  # 速动比率
            'assets_turn': latest.get('assets_turn', 0),  # 总资产周转率
            'inv_turn': latest.get('inv_turn', 0),  # 存货周转率
            'ar_turn': latest.get('ar_turn', 0)  # 应收账款周转率
        }
    
    def _calculate_valuation(self, symbol: str) -> dict:
        """计算估值指标"""
        try:
            # 获取实时行情
            realtime = self.ds.get_a_share_realtime(symbol)
            
            return {
                'status': 'success',
                'price': realtime.get('close', 0),
                'pe': realtime.get('pe', 0),
                'pb': realtime.get('pb', 0),
                'turnover_rate': realtime.get('turnover_rate', 0)
            }
        except:
            return {'status': 'error'}
    
    def _calculate_trend(self, df: pd.DataFrame, column: str) -> dict:
        """计算趋势"""
        if len(df) < 2:
            return None
        
        values = df[column].dropna().values
        if len(values) < 2:
            return None
        
        latest = values[0]
        previous = values[1]
        
        if previous == 0:
            return None
        
        change = (latest - previous) / abs(previous) * 100
        
        return {
            'latest': latest,
            'previous': previous,
            'change_pct': change,
            'trend': 'up' if change > 0 else 'down' if change < 0 else 'flat'
        }
    
    def _calculate_overall_score(self, analysis: dict) -> dict:
        """计算综合评分"""
        scores = {
            'profitability': 0,  # 盈利能力
            'stability': 0,  # 偿债能力
            'growth': 0,  # 成长性
            'valuation': 0  # 估值
        }
        
        # 盈利能力评分 (ROE > 15%为优秀)
        indicators = analysis.get('financial_indicators', {})
        if indicators.get('status') == 'success':
            roe = indicators.get('roe', 0)
            if roe > 20:
                scores['profitability'] = 100
            elif roe > 15:
                scores['profitability'] = 80
            elif roe > 10:
                scores['profitability'] = 60
            elif roe > 5:
                scores['profitability'] = 40
            else:
                scores['profitability'] = 20
            
            # 净利率评分
            npm = indicators.get('netprofit_margin', 0)
            scores['profitability'] = min(100, scores['profitability'] + npm * 0.5)
        
        # 估值评分 (PE < 15为优秀)
        valuation = analysis.get('valuation_metrics', {})
        if valuation.get('status') == 'success':
            pe = valuation.get('pe', 0)
            if pe > 0 and pe < 15:
                scores['valuation'] = 100
            elif pe > 0 and pe < 25:
                scores['valuation'] = 70
            elif pe > 0 and pe < 40:
                scores['valuation'] = 50
            else:
                scores['valuation'] = 30
        
        # 综合评分
        overall = sum(scores.values()) / len(scores)
        
        return {
            'overall': overall,
            'details': scores
        }
    
    def _generate_recommendation(self, analysis: dict) -> dict:
        """生成投资建议"""
        score = analysis.get('overall_score', {}).get('overall', 50)
        
        if score >= 80:
            return {
                'rating': '强烈买入',
                'score': score,
                'reason': '财务指标优秀，估值合理'
            }
        elif score >= 60:
            return {
                'rating': '买入',
                'score': score,
                'reason': '基本面良好'
            }
        elif score >= 40:
            return {
                'rating': '持有',
                'score': score,
                'reason': '基本面一般'
            }
        else:
            return {
                'rating': '回避',
                'score': score,
                'reason': '财务指标不佳'
            }
    
    def compare_stocks(self, symbols: list) -> pd.DataFrame:
        """
        多股票对比分析
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            对比分析DataFrame
        """
        results = []
        
        for symbol in symbols:
            analysis = self.get_full_financial_analysis(symbol)
            
            row = {
                'code': symbol,
                'roe': analysis.get('financial_indicators', {}).get('roe', 0),
                'pe': analysis.get('valuation_metrics', {}).get('pe', 0),
                'pb': analysis.get('valuation_metrics', {}).get('pb', 0),
                'score': analysis.get('overall_score', {}).get('overall', 0),
                'rating': analysis.get('investment_recommendation', {}).get('rating', '未知')
            }
            results.append(row)
        
        return pd.DataFrame(results)


# 快捷函数
def analyze_stock(symbol: str) -> dict:
    """快捷分析个股"""
    vi = ValueInvestingTushare()
    return vi.get_full_financial_analysis(symbol)


def compare_stocks(symbols: list) -> pd.DataFrame:
    """快捷对比多股"""
    vi = ValueInvestingTushare()
    return vi.compare_stocks(symbols)


if __name__ == '__main__':
    print("="*60)
    print("💰 价值投资Tushare集成测试")
    print("="*60)
    
    vi = ValueInvestingTushare()
    
    # 测试1: 单股分析
    print("\n📊 测试1: 平安银行(000001)财务分析")
    result = vi.get_full_financial_analysis('000001')
    print(f"代码: {result['code']}")
    print(f"综合评分: {result['overall_score']['overall']:.1f}")
    print(f"投资建议: {result['investment_recommendation']['rating']}")
    
    if result['financial_indicators'].get('status') == 'success':
        print(f"ROE: {result['financial_indicators']['roe']:.2f}%")
        print(f"毛利率: {result['financial_indicators']['grossprofit_margin']:.2f}%")
    
    if result['valuation_metrics'].get('status') == 'success':
        print(f"PE: {result['valuation_metrics']['pe']:.2f}")
        print(f"PB: {result['valuation_metrics']['pb']:.2f}")
    
    # 测试2: 多股对比
    print("\n📊 测试2: 多股对比")
    df = vi.compare_stocks(['000001', '600519'])
    print(df.to_string(index=False))
    
    print("\n✅ 测试完成！")
