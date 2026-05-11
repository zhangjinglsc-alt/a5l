"""
《中国革命战争的战略问题》第一章 - 投资规律识别器
对应毛选：不懂得那件事的情形、性质、关联，就不知道规律
"""

import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime


class InvestmentLawRecognizer:
    """
    投资规律识别器
    
    核心思想：
    - 分析市场情形（估值、情绪、资金、技术形态）
    - 判断市场性质（趋势强度、波动率、周期性）
    - 评估外部关联（宏观、产业、政策、国际）
    - 综合判断投资规律
    """
    
    def __init__(self):
        self.market_state_dims = ['valuation', 'sentiment', 'capital_flow', 'technical']
        self.market_nature_dims = ['trend_strength', 'volatility', 'cyclicality']
        self.external_dims = ['macro', 'industry', 'policy', 'geopolitics']
    
    def recognize_investment_law(self, market_data: dict) -> dict:
        """
        识别当前市场规律
        
        Args:
            market_data: 市场数据字典
            
        Returns:
            law_recognition: 规律识别结果
        """
        # 1. 分析市场情形
        market_state = self._analyze_market_state(market_data)
        
        # 2. 判断市场性质
        market_nature = self._judge_market_nature(market_data)
        
        # 3. 评估外部关联
        external_corr = self._evaluate_external_correlation(market_data)
        
        # 4. 综合判断投资规律
        law = self._synthesize_law(market_state, market_nature, external_corr)
        
        return {
            'market_state': market_state,
            'market_nature': market_nature,
            'external_correlation': external_corr,
            'investment_law': law,
            'confidence': law['confidence'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_market_state(self, data: dict) -> dict:
        """分析市场情形"""
        return {
            'valuation': self._calculate_valuation_score(data),
            'sentiment': self._calculate_sentiment_score(data),
            'capital_flow': self._analyze_capital_flow(data),
            'technical': self._analyze_technical_pattern(data)
        }
    
    def _judge_market_nature(self, data: dict) -> dict:
        """判断市场性质"""
        prices = data.get('price_history', [])
        if len(prices) < 2:
            return {'trend_strength': 0.5, 'volatility': 0.2, 'cyclicality': 0.5}
        
        returns = np.diff(prices) / prices[:-1]
        
        return {
            'trend_strength': self._calculate_trend_strength(returns),
            'volatility': float(np.std(returns) * np.sqrt(252)),
            'cyclicality': self._detect_cycle_phase(data)
        }
    
    def _evaluate_external_correlation(self, data: dict) -> dict:
        """评估外部关联"""
        return {
            'macro_impact': self._assess_macro_factor(data),
            'industry_cycle': self._assess_industry_cycle(data),
            'policy_risk': self._assess_policy_risk(data),
            'geopolitical': self._assess_geopolitical_risk(data)
        }
    
    def _synthesize_law(self, state, nature, external) -> dict:
        """综合判断投资规律"""
        trend = nature.get('trend_strength', 0.5)
        macro = external.get('macro_impact', 0)
        
        if trend > 0.7 and macro > 0:
            return {
                'law_name': '趋势跟随',
                'law_description': '强趋势+宏观支持，适用趋势跟踪策略',
                'recommended_strategy': 'trend_following',
                'position_approach': '逐步加仓',
                'confidence': 0.85
            }
        elif nature.get('volatility', 0) > 0.3 and state.get('sentiment', 0.5) < 0.3:
            return {
                'law_name': '均值回归',
                'law_description': '高波动+情绪冰点，适用均值回归策略',
                'recommended_strategy': 'mean_reversion',
                'position_approach': '左侧布局',
                'confidence': 0.75
            }
        else:
            return {
                'law_name': '观望等待',
                'law_description': '市场规律不清晰，等待信号',
                'recommended_strategy': 'wait',
                'position_approach': '空仓或轻仓',
                'confidence': 0.6
            }
    
    def _calculate_valuation_score(self, data: dict) -> float:
        """计算估值评分"""
        pe_percentile = data.get('pe_percentile', 0.5)
        pb_percentile = data.get('pb_percentile', 0.5)
        return 1 - (pe_percentile + pb_percentile) / 2  # 越低越好
    
    def _calculate_sentiment_score(self, data: dict) -> float:
        """计算情绪评分"""
        return data.get('sentiment_index', 0.5)
    
    def _analyze_capital_flow(self, data: dict) -> dict:
        """分析资金流向"""
        return {
            'northbound': data.get('northbound_flow', 0),
            'institutional': data.get('institutional_flow', 0),
            'retail': data.get('retail_flow', 0)
        }
    
    def _analyze_technical_pattern(self, data: dict) -> dict:
        """分析技术形态"""
        return {
            'trend': data.get('trend_direction', 'neutral'),
            'support': data.get('support_level', 0),
            'resistance': data.get('resistance_level', 0)
        }
    
    def _calculate_trend_strength(self, returns: np.ndarray) -> float:
        """计算趋势强度"""
        if len(returns) < 10:
            return 0.5
        
        # 使用线性回归斜率
        x = np.arange(len(returns))
        slope = np.polyfit(x, returns, 1)[0]
        
        # 归一化到0-1
        return min(1.0, max(0.0, abs(slope) * 100))
    
    def _detect_cycle_phase(self, data: dict) -> float:
        """检测周期阶段"""
        # 简化实现：根据估值和情绪判断
        valuation = data.get('valuation_percentile', 0.5)
        sentiment = data.get('sentiment_index', 0.5)
        
        # 早期：低估值+低情绪
        # 晚期：高估值+高情绪
        return (valuation + sentiment) / 2
    
    def _assess_macro_factor(self, data: dict) -> float:
        """评估宏观因素"""
        interest_trend = data.get('interest_rate_trend', 0)
        gdp_growth = data.get('gdp_growth', 0.05)
        inflation = data.get('inflation', 0.02)
        
        # 简单评分
        score = 0.5
        if interest_trend < 0:  # 降息利好
            score += 0.2
        if gdp_growth > 0.05:
            score += 0.1
        if 0.01 < inflation < 0.03:  # 温和通胀
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_industry_cycle(self, data: dict) -> float:
        """评估产业周期"""
        return data.get('industry_cycle_score', 0.5)
    
    def _assess_policy_risk(self, data: dict) -> float:
        """评估政策风险"""
        return data.get('policy_risk_score', 0.3)
    
    def _assess_geopolitical_risk(self, data: dict) -> float:
        """评估地缘政治风险"""
        return data.get('geopolitical_risk', 0.3)
