#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALUE CELL - 价值投资分析框架
Chief Architect设计 | Layer 3核心组件 | P0最高优先级

V - Valuation: 估值分析
A - Assets: 资产质量
L - Leverage: 杠杆优化
U - Utility: 盈利能力
E - Endurance: 可持续性

位置: ARCHITECT_5L/layer3_analysis/analyzers/value_cell_analyzer.py
作者: A5L Chief Architect
创建: 2026-05-02 (五一假期冲刺)
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValueRating(Enum):
    """价值投资评级"""
    STRONG_BUY = "强烈买入"    # 安全边际>50%, 质量优秀
    BUY = "买入"               # 安全边际30-50%, 质量良好
    HOLD = "持有"              # 安全边际10-30%, 质量一般
    REDUCE = "减仓"            # 安全边际<10%, 或质量下降
    SELL = "卖出"              # 高估或质量恶化


@dataclass
class ValuationMetrics:
    """估值指标"""
    # DCF估值
    dcf_value: float = 0.0              # DCF内在价值
    dcf_assumptions: Dict = field(default_factory=dict)
    
    # 相对估值
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    ps_ratio: float = 0.0
    ev_ebitda: float = 0.0
    
    # 历史分位
    pe_percentile: float = 0.0          # PE历史分位
    pb_percentile: float = 0.0          # PB历史分位
    
    # 安全边际
    current_price: float = 0.0
    margin_of_safety: float = 0.0       # 安全边际 (%)
    
    # 评级
    valuation_score: float = 0.0        # 0-100
    assessment: str = ""


@dataclass
class AssetQuality:
    """资产质量"""
    # 有形资产
    tangible_assets: float = 0.0        # 有形资产价值
    property_plant_equipment: float = 0.0
    inventory: float = 0.0
    
    # 无形资产
    intangible_assets: float = 0.0      # 无形资产价值
    brand_value: float = 0.0            # 品牌价值
    patents: int = 0                    # 专利数量
    licenses: List[str] = field(default_factory=list)
    
    # 表外资产
    off_balance_sheet: float = 0.0      # 表外资产价值
    hidden_assets: List[str] = field(default_factory=list)
    
    # 资产变现
    asset_liquidity: float = 0.0        # 资产流动性评分
    
    # 评级
    asset_score: float = 0.0            # 0-100
    assessment: str = ""


@dataclass
class LeverageMetrics:
    """杠杆与资本结构"""
    # 财务杠杆
    debt_to_equity: float = 0.0         # 负债权益比
    debt_ratio: float = 0.0             # 资产负债率
    interest_coverage: float = 0.0      # 利息保障倍数
    
    # 经营杠杆
    fixed_cost_ratio: float = 0.0       # 固定成本占比
    operating_leverage: float = 0.0     # 经营杠杆系数
    
    # 资本配置
    roic: float = 0.0                   # 投入资本回报率
    wacc: float = 0.0                   # 加权平均资本成本
    roic_spread: float = 0.0            # ROIC - WACC
    
    # 安全边际
    margin_of_safety_pct: float = 0.0   # 安全边际百分比
    
    # 评级
    leverage_score: float = 0.0         # 0-100
    assessment: str = ""


@dataclass
class UtilityMetrics:
    """盈利能力"""
    # ROE分析
    roe: float = 0.0                    # 净资产收益率
    roe_dupont: Dict = field(default_factory=dict)  # 杜邦分析
    
    # ROIC
    roic: float = 0.0                   # 投入资本回报率
    roic_3yr_avg: float = 0.0           # 3年平均ROIC
    
    # 利润率
    gross_margin: float = 0.0           # 毛利率
    operating_margin: float = 0.0       # 营业利润率
    net_margin: float = 0.0             # 净利率
    
    # 盈利质量
    cash_flow_to_net_income: float = 0.0  # 现金流/净利润
    accrual_ratio: float = 0.0          # 应计比率
    
    # 评级
    utility_score: float = 0.0          # 0-100
    assessment: str = ""


@dataclass
class EnduranceMetrics:
    """可持续性/护城河"""
    # 波特五力
    supplier_power: float = 0.0         # 供应商议价能力 (1-10, 越低越好)
    buyer_power: float = 0.0            # 买方议价能力 (1-10, 越低越好)
    competitive_rivalry: float = 0.0    # 竞争程度 (1-10, 越低越好)
    threat_of_substitutes: float = 0.0  # 替代品威胁 (1-10, 越低越好)
    threat_of_new_entrants: float = 0.0 # 新进入者威胁 (1-10, 越低越好)
    
    # 护城河类型
    moat_type: str = ""                 # 护城河类型
    moat_strength: float = 0.0          # 护城河强度 (0-100)
    
    # 行业生命周期
    industry_lifecycle: str = ""        # 成长期/成熟期/衰退期
    
    # 管理层
    management_quality: float = 0.0     # 管理层质量 (0-100)
    capital_allocation: float = 0.0     # 资本配置能力
    
    # 评级
    endurance_score: float = 0.0        # 0-100
    assessment: str = ""


@dataclass
class VALUECellReport:
    """VALUE CELL分析报告"""
    symbol: str
    analysis_date: str
    
    # 五维度评分
    v_score: float = 0.0                # Valuation评分
    a_score: float = 0.0                # Assets评分
    l_score: float = 0.0                # Leverage评分
    u_score: float = 0.0                # Utility评分
    e_score: float = 0.0                # Endurance评分
    
    # 综合评分
    total_score: float = 0.0            # 总分 (0-100)
    value_rating: str = ""              # 价值投资评级
    
    # 内在价值
    intrinsic_value: float = 0.0        # 估算内在价值
    current_price: float = 0.0          # 当前价格
    upside_potential: float = 0.0       # 上涨空间 (%)
    
    # 详细指标
    valuation: ValuationMetrics = field(default_factory=ValuationMetrics)
    assets: AssetQuality = field(default_factory=AssetQuality)
    leverage: LeverageMetrics = field(default_factory=LeverageMetrics)
    utility: UtilityMetrics = field(default_factory=UtilityMetrics)
    endurance: EnduranceMetrics = field(default_factory=EnduranceMetrics)
    
    # 投资建议
    recommendation: str = ""
    target_position: str = ""           # 建议仓位
    key_risks: List[str] = field(default_factory=list)
    key_opportunities: List[str] = field(default_factory=list)


class ValuationAnalyzer:
    """V - 估值分析器"""
    
    def calculate_dcf(self, symbol: str, 
                      free_cash_flow: float,
                      growth_rate_5yr: float,
                      growth_rate_terminal: float,
                      discount_rate: float,
                      shares_outstanding: float) -> Dict:
        """
        计算DCF内在价值
        
        Args:
            symbol: 股票代码
            free_cash_flow: 当前自由现金流
            growth_rate_5yr: 前5年增长率
            growth_rate_terminal: 永续增长率
            discount_rate: 折现率 (WACC)
            shares_outstanding: 总股本
            
        Returns:
            DCF估值结果
        """
        # 5年预测期现金流
        cash_flows = []
        fcf = free_cash_flow
        for year in range(1, 6):
            fcf = fcf * (1 + growth_rate_5yr)
            pv = fcf / ((1 + discount_rate) ** year)
            cash_flows.append(pv)
        
        # 终值
        terminal_value = fcf * (1 + growth_rate_terminal) / (discount_rate - growth_rate_terminal)
        pv_terminal = terminal_value / ((1 + discount_rate) ** 5)
        
        # 企业价值
        enterprise_value = sum(cash_flows) + pv_terminal
        
        # 每股价值
        value_per_share = enterprise_value / shares_outstanding
        
        return {
            'dcf_value_per_share': value_per_share,
            'enterprise_value': enterprise_value,
            'pv_cash_flows': sum(cash_flows),
            'pv_terminal': pv_terminal,
            'assumptions': {
                'fcf': free_cash_flow,
                'growth_5yr': growth_rate_5yr,
                'growth_terminal': growth_rate_terminal,
                'discount_rate': discount_rate
            }
        }
    
    def calculate_relative_valuation(self, symbol: str, 
                                    pe: float, pb: float, ps: float,
                                    industry_avg_pe: float,
                                    industry_avg_pb: float,
                                    hist_pe_low: float, hist_pe_high: float) -> Dict:
        """计算相对估值"""
        pe_vs_industry = pe / industry_avg_pe if industry_avg_pe > 0 else 1.0
        pb_vs_industry = pb / industry_avg_pb if industry_avg_pb > 0 else 1.0
        
        # PE历史分位
        pe_range = hist_pe_high - hist_pe_low
        pe_percentile = (pe - hist_pe_low) / pe_range if pe_range > 0 else 0.5
        
        return {
            'pe_ratio': pe,
            'pb_ratio': pb,
            'ps_ratio': ps,
            'pe_vs_industry': pe_vs_industry,
            'pb_vs_industry': pb_vs_industry,
            'pe_percentile': pe_percentile,
            'undervalued': pe_vs_industry < 0.8 and pe_percentile < 0.3
        }
    
    def calculate_margin_of_safety(self, intrinsic_value: float, 
                                   current_price: float) -> float:
        """计算安全边际"""
        if intrinsic_value <= 0:
            return 0.0
        margin = (intrinsic_value - current_price) / intrinsic_value
        return margin * 100  # 转为百分比
    
    def analyze(self, symbol: str, market_data: Dict) -> ValuationMetrics:
        """执行完整估值分析"""
        metrics = ValuationMetrics()
        
        # 模拟数据 (实际应接入真实财务数据)
        # DCF计算
        dcf_result = self.calculate_dcf(
            symbol=symbol,
            free_cash_flow=market_data.get('fcf', 1e9),
            growth_rate_5yr=0.15,
            growth_rate_terminal=0.03,
            discount_rate=0.10,
            shares_outstanding=market_data.get('shares', 1e9)
        )
        
        metrics.dcf_value = dcf_result['dcf_value_per_share']
        metrics.dcf_assumptions = dcf_result['assumptions']
        
        # 相对估值
        rel_val = self.calculate_relative_valuation(
            symbol=symbol,
            pe=market_data.get('pe', 20),
            pb=market_data.get('pb', 3),
            ps=market_data.get('ps', 5),
            industry_avg_pe=market_data.get('industry_pe', 25),
            industry_avg_pb=market_data.get('industry_pb', 4),
            hist_pe_low=10,
            hist_pe_high=50
        )
        
        metrics.pe_ratio = rel_val['pe_ratio']
        metrics.pb_ratio = rel_val['pb_ratio']
        metrics.ps_ratio = rel_val['ps_ratio']
        metrics.pe_percentile = rel_val['pe_percentile']
        
        # 当前价格和安全边际
        metrics.current_price = market_data.get('price', 100)
        metrics.margin_of_safety = self.calculate_margin_of_safety(
            metrics.dcf_value, metrics.current_price
        )
        
        # 评分 (安全边际越高越好，PE越低越好)
        margin_score = min(100, max(0, metrics.margin_of_safety * 2))
        pe_score = max(0, 100 - metrics.pe_percentile * 100)
        metrics.valuation_score = (margin_score + pe_score) / 2
        
        # 评估结论
        if metrics.margin_of_safety > 50:
            metrics.assessment = "极度低估，强烈安全边际"
        elif metrics.margin_of_safety > 30:
            metrics.assessment = "明显低估，良好安全边际"
        elif metrics.margin_of_safety > 10:
            metrics.assessment = "轻微低估，有限安全边际"
        else:
            metrics.assessment = "高估或合理估值，无安全边际"
        
        return metrics


class AssetAnalyzer:
    """A - 资产质量分析器"""
    
    def analyze(self, symbol: str, market_data: Dict) -> AssetQuality:
        """分析资产质量"""
        assets = AssetQuality()
        
        # 模拟分析 (实际应接入资产负债表)
        assets.tangible_assets = market_data.get('tangible_assets', 10e9)
        assets.intangible_assets = market_data.get('intangible_assets', 5e9)
        assets.brand_value = market_data.get('brand_value', 2e9)
        assets.patents = market_data.get('patents', 100)
        
        # 计算资产评分
        # 无形资产占比 (科技类公司越高越好)
        total_assets = assets.tangible_assets + assets.intangible_assets
        intangible_ratio = assets.intangible_assets / total_assets if total_assets > 0 else 0
        
        # 评分逻辑
        brand_score = min(100, assets.brand_value / 1e9 * 10)  # 品牌价值
        patent_score = min(100, assets.patents / 10)           # 专利数量
        liquidity_score = 70  # 假设流动性良好
        
        assets.asset_score = (brand_score + patent_score + liquidity_score) / 3
        
        # 评估结论
        if assets.asset_score >= 80:
            assets.assessment = "资产质量优秀，无形资产价值高"
        elif assets.asset_score >= 60:
            assets.assessment = "资产质量良好"
        else:
            assets.assessment = "资产质量一般，需关注"
        
        return assets


class LeverageAnalyzer:
    """L - 杠杆与资本结构分析器"""
    
    def analyze(self, symbol: str, market_data: Dict) -> LeverageMetrics:
        """分析杠杆"""
        lev = LeverageMetrics()
        
        # 财务杠杆
        lev.debt_to_equity = market_data.get('debt_to_equity', 0.5)
        lev.debt_ratio = market_data.get('debt_ratio', 0.4)
        lev.interest_coverage = market_data.get('interest_coverage', 10)
        
        # 资本配置
        lev.roic = market_data.get('roic', 0.12)
        lev.wacc = market_data.get('wacc', 0.08)
        lev.roic_spread = lev.roic - lev.wacc
        
        # 安全边际
        lev.margin_of_safety_pct = market_data.get('margin_of_safety', 20)
        
        # 评分
        # 负债率越低越好，ROIC-WACC越大越好
        debt_score = max(0, 100 - lev.debt_ratio * 100)
        roic_score = min(100, lev.roic_spread * 500 + 50)  # 假设spread=10%得满分
        coverage_score = min(100, lev.interest_coverage * 5)  # 利息保障
        
        lev.leverage_score = (debt_score + roic_score + coverage_score) / 3
        
        # 评估结论
        if lev.roic_spread > 0.05 and lev.debt_ratio < 0.5:
            lev.assessment = "资本结构健康，ROIC>WACC，创造价值"
        elif lev.roic_spread > 0:
            lev.assessment = "资本结构合理，勉强创造价值"
        else:
            lev.assessment = "资本结构需优化，ROIC<WACC，毁灭价值"
        
        return lev


class UtilityAnalyzer:
    """U - 盈利能力分析器"""
    
    def analyze(self, symbol: str, market_data: Dict) -> UtilityMetrics:
        """分析盈利能力"""
        util = UtilityMetrics()
        
        # ROE和杜邦分析
        util.roe = market_data.get('roe', 0.15)
        net_margin = market_data.get('net_margin', 0.10)
        asset_turnover = market_data.get('asset_turnover', 1.0)
        equity_multiplier = market_data.get('equity_multiplier', 1.5)
        
        util.roe_dupont = {
            'net_margin': net_margin,
            'asset_turnover': asset_turnover,
            'equity_multiplier': equity_multiplier,
            'calculated_roe': net_margin * asset_turnover * equity_multiplier
        }
        
        # ROIC
        util.roic = market_data.get('roic', 0.12)
        util.roic_3yr_avg = market_data.get('roic_3yr_avg', 0.10)
        
        # 利润率
        util.gross_margin = market_data.get('gross_margin', 0.40)
        util.operating_margin = market_data.get('operating_margin', 0.15)
        util.net_margin = net_margin
        
        # 盈利质量
        util.cash_flow_to_net_income = market_data.get('cf_ni_ratio', 1.2)
        util.accrual_ratio = market_data.get('accrual_ratio', 0.05)
        
        # 评分
        roe_score = min(100, util.roe * 400)  # ROE 25%得满分
        margin_score = util.gross_margin * 150  # 毛利率
        quality_score = util.cash_flow_to_net_income * 40  # 现金流质量
        
        util.utility_score = (roe_score + margin_score + quality_score) / 3
        
        # 评估结论
        if util.roe > 0.20 and util.roic > 0.15:
            util.assessment = "盈利能力卓越，ROE和ROIC均优秀"
        elif util.roe > 0.15:
            util.assessment = "盈利能力良好"
        else:
            util.assessment = "盈利能力一般，需提升"
        
        return util


class EnduranceAnalyzer:
    """E - 可持续性/护城河分析器"""
    
    def analyze_porter_five_forces(self, symbol: str) -> Dict:
        """分析波特五力"""
        # 模拟五力分析 (实际应基于行业数据)
        return {
            'supplier_power': 4,        # 供应商议价能力 (1-10)
            'buyer_power': 5,           # 买方议价能力
            'competitive_rivalry': 6,   # 竞争程度
            'threat_of_substitutes': 3, # 替代品威胁
            'threat_of_new_entrants': 4 # 新进入者威胁
        }
    
    def identify_moat(self, symbol: str, market_data: Dict) -> Tuple[str, float]:
        """识别护城河类型和强度"""
        # 模拟护城河分析
        moat_types = ['品牌', '成本优势', '网络效应', '技术专利', '转换成本', '规模经济']
        
        # 根据公司特征判断
        if market_data.get('brand_value', 0) > 5e9:
            return '品牌护城河', 85
        elif market_data.get('patents', 0) > 500:
            return '技术专利护城河', 80
        elif market_data.get('gross_margin', 0) > 0.50:
            return '成本优势护城河', 75
        else:
            return '弱护城河', 40
    
    def analyze(self, symbol: str, market_data: Dict) -> EnduranceMetrics:
        """分析可持续性"""
        end = EnduranceMetrics()
        
        # 波特五力
        five_forces = self.analyze_porter_five_forces(symbol)
        end.supplier_power = five_forces['supplier_power']
        end.buyer_power = five_forces['buyer_power']
        end.competitive_rivalry = five_forces['competitive_rivalry']
        end.threat_of_substitutes = five_forces['threat_of_substitutes']
        end.threat_of_new_entrants = five_forces['threat_of_new_entrants']
        
        # 护城河
        end.moat_type, end.moat_strength = self.identify_moat(symbol, market_data)
        
        # 行业生命周期
        revenue_growth = market_data.get('revenue_growth', 0.15)
        if revenue_growth > 0.20:
            end.industry_lifecycle = '高速成长期'
        elif revenue_growth > 0.05:
            end.industry_lifecycle = '成熟期'
        else:
            end.industry_lifecycle = '衰退期'
        
        # 管理层
        end.management_quality = market_data.get('mgmt_quality', 75)
        end.capital_allocation = market_data.get('capital_allocation', 70)
        
        # 评分
        # 五力平均分 (越低越好，所以用10减)
        five_forces_avg = (end.supplier_power + end.buyer_power + 
                          end.competitive_rivalry + end.threat_of_substitutes + 
                          end.threat_of_new_entrants) / 5
        competitive_score = (10 - five_forces_avg) * 10  # 转为0-100
        
        moat_score = end.moat_strength
        mgmt_score = end.management_quality
        
        end.endurance_score = (competitive_score + moat_score + mgmt_score) / 3
        
        # 评估结论
        if end.moat_strength >= 80 and end.endurance_score >= 75:
            end.assessment = f"强大{end.moat_type}，可持续竞争优势明确"
        elif end.moat_strength >= 60:
            end.assessment = f"具备{end.moat_type}，竞争优势一般"
        else:
            end.assessment = "护城河较弱，竞争优势不明显"
        
        return end


class VALUECellAnalyzer:
    """
    VALUE CELL 价值投资分析器 - P0最高优先级
    
    五维度价值投资分析:
    V - Valuation: 估值分析
    A - Assets: 资产质量
    L - Leverage: 杠杆优化
    U - Utility: 盈利能力
    E - Endurance: 可持续性
    """
    
    def __init__(self):
        self.v_analyzer = ValuationAnalyzer()
        self.a_analyzer = AssetAnalyzer()
        self.l_analyzer = LeverageAnalyzer()
        self.u_analyzer = UtilityAnalyzer()
        self.e_analyzer = EnduranceAnalyzer()
        
        logger.info("💎 VALUE CELL Analyzer initialized")
    
    def analyze(self, symbol: str, market_data: Optional[Dict] = None) -> VALUECellReport:
        """
        执行完整VALUE CELL分析
        
        Args:
            symbol: 股票代码
            market_data: 市场数据 (可选)
            
        Returns:
            VALUECellReport: 完整分析报告
        """
        if market_data is None:
            market_data = self._get_mock_data(symbol)
        
        logger.info(f"💎 Starting VALUE CELL analysis for {symbol}")
        
        # 五维度分析
        v_metrics = self.v_analyzer.analyze(symbol, market_data)
        a_metrics = self.a_analyzer.analyze(symbol, market_data)
        l_metrics = self.l_analyzer.analyze(symbol, market_data)
        u_metrics = self.u_analyzer.analyze(symbol, market_data)
        e_metrics = self.e_analyzer.analyze(symbol, market_data)
        
        # 创建报告
        report = VALUECellReport(
            symbol=symbol,
            analysis_date=datetime.now().isoformat(),
            v_score=v_metrics.valuation_score,
            a_score=a_metrics.asset_score,
            l_score=l_metrics.leverage_score,
            u_score=u_metrics.utility_score,
            e_score=e_metrics.endurance_score,
            valuation=v_metrics,
            assets=a_metrics,
            leverage=l_metrics,
            utility=u_metrics,
            endurance=e_metrics
        )
        
        # 计算综合评分
        report.total_score = (report.v_score + report.a_score + report.l_score + 
                             report.u_score + report.e_score) / 5
        
        # 内在价值 (使用DCF)
        report.intrinsic_value = v_metrics.dcf_value
        report.current_price = v_metrics.current_price
        
        # 上涨空间
        if report.intrinsic_value > 0:
            report.upside_potential = ((report.intrinsic_value - report.current_price) 
                                      / report.current_price * 100)
        
        # 价值投资评级
        report.value_rating = self._determine_rating(report)
        
        # 投资建议
        report.recommendation = self._generate_recommendation(report)
        report.target_position = self._suggest_position(report)
        report.key_risks = self._identify_risks(report)
        report.key_opportunities = self._identify_opportunities(report)
        
        logger.info(f"✅ VALUE CELL analysis complete: {symbol} - Score {report.total_score:.1f}/100")
        
        return report
    
    def _get_mock_data(self, symbol: str) -> Dict:
        """获取模拟数据 (实际应接入真实API)"""
        # 模拟一只优质价值股的数据
        return {
            'price': 100,
            'pe': 15,
            'pb': 2.5,
            'ps': 3,
            'industry_pe': 25,
            'industry_pb': 4,
            'fcf': 2e9,
            'shares': 1e9,
            'roe': 0.18,
            'roic': 0.15,
            'gross_margin': 0.45,
            'net_margin': 0.12,
            'debt_ratio': 0.35,
            'debt_to_equity': 0.5,
            'interest_coverage': 12,
            'wacc': 0.08,
            'brand_value': 8e9,
            'patents': 200,
            'tangible_assets': 15e9,
            'intangible_assets': 8e9,
            'mgmt_quality': 85,
            'capital_allocation': 80,
            'revenue_growth': 0.12
        }
    
    def _determine_rating(self, report: VALUECellReport) -> str:
        """确定价值投资评级"""
        # 基于安全边际和质量评分
        margin = report.valuation.margin_of_safety
        quality = (report.a_score + report.e_score) / 2  # 资产质量和可持续性
        
        if margin > 50 and quality >= 70:
            return ValueRating.STRONG_BUY.value
        elif margin > 30 and quality >= 60:
            return ValueRating.BUY.value
        elif margin > 10:
            return ValueRating.HOLD.value
        elif margin > -10:
            return ValueRating.REDUCE.value
        else:
            return ValueRating.SELL.value
    
    def _generate_recommendation(self, report: VALUECellReport) -> str:
        """生成投资建议"""
        parts = []
        
        # 估值部分
        if report.v_score >= 70:
            parts.append(f"估值吸引力强，安全边际{report.valuation.margin_of_safety:.1f}%")
        elif report.v_score >= 50:
            parts.append(f"估值合理，安全边际{report.valuation.margin_of_safety:.1f}%")
        else:
            parts.append(f"估值偏高，缺乏安全边际")
        
        # 质量部分
        if report.e_score >= 70:
            parts.append(f"具备{report.endurance.moat_type}，竞争优势明确")
        
        # 盈利部分
        if report.u_score >= 70:
            parts.append(f"盈利能力优秀，ROE {report.utility.roe:.1%}")
        
        return "；".join(parts)
    
    def _suggest_position(self, report: VALUECellReport) -> str:
        """建议仓位"""
        if report.total_score >= 80:
            return "15-20% (重仓)"
        elif report.total_score >= 65:
            return "8-12% (中仓)"
        elif report.total_score >= 50:
            return "3-5% (轻仓)"
        else:
            return "0-2% (观望)"
    
    def _identify_risks(self, report: VALUECellReport) -> List[str]:
        """识别关键风险"""
        risks = []
        
        if report.v_score < 50:
            risks.append("估值偏高，下行风险大")
        if report.l_score < 50:
            risks.append("财务杠杆较高")
        if report.e_score < 50:
            risks.append("护城河较弱，竞争优势不明显")
        if report.u_score < 50:
            risks.append("盈利能力一般")
        
        return risks if risks else ["主要风险: 市场整体下行"]
    
    def _identify_opportunities(self, report: VALUECellReport) -> List[str]:
        """识别关键机会"""
        opportunities = []
        
        if report.v_score >= 70:
            opportunities.append(f"估值低估，潜在上涨空间{report.upside_potential:.1f}%")
        if report.e_score >= 70:
            opportunities.append(f"{report.endurance.moat_type}支撑长期价值")
        if report.u_score >= 70:
            opportunities.append("盈利能力持续优秀")
        if report.l_score >= 70:
            opportunities.append("资本配置效率高，ROIC>WACC")
        
        return opportunities if opportunities else ["关注基本面改善机会"]
    
    def generate_report_markdown(self, report: VALUECellReport) -> str:
        """生成Markdown格式报告"""
        lines = [
            f"# 💎 VALUE CELL 价值投资分析报告: {report.symbol}",
            "",
            f"**分析日期**: {report.analysis_date}",
            f"**综合评分**: {report.total_score:.1f}/100",
            f"**价值投资评级**: {report.value_rating}",
            "",
            "---",
            "",
            "## 📊 五维度评分雷达",
            "",
            f"| 维度 | 评分 | 评估 |",
            f"|------|------|------|",
            f"| **V - 估值** | {report.v_score:.1f} | {report.valuation.assessment} |",
            f"| **A - 资产** | {report.a_score:.1f} | {report.assets.assessment} |",
            f"| **L - 杠杆** | {report.l_score:.1f} | {report.leverage.assessment} |",
            f"| **U - 盈利** | {report.u_score:.1f} | {report.utility.assessment} |",
            f"| **E - 持续** | {report.e_score:.1f} | {report.endurance.assessment} |",
            "",
            "---",
            "",
            "## 💰 估值分析 (V)",
            "",
            f"- **DCF内在价值**: ¥{report.intrinsic_value:.2f}",
            f"- **当前价格**: ¥{report.current_price:.2f}",
            f"- **安全边际**: {report.valuation.margin_of_safety:.1f}%",
            f"- **上涨空间**: {report.upside_potential:.1f}%",
            f"- **PE比率**: {report.valuation.pe_ratio:.1f}x",
            f"- **PB比率**: {report.valuation.pb_ratio:.1f}x",
            "",
            "## 🏭 资产质量 (A)",
            "",
            f"- **有形资产**: ¥{report.assets.tangible_assets/1e9:.1f}亿",
            f"- **无形资产**: ¥{report.assets.intangible_assets/1e9:.1f}亿",
            f"- **品牌价值**: ¥{report.assets.brand_value/1e9:.1f}亿",
            f"- **专利数量**: {report.assets.patents}项",
            "",
            "## ⚖️ 杠杆与资本 (L)",
            "",
            f"- **资产负债率**: {report.leverage.debt_ratio:.1%}",
            f"- **ROIC**: {report.leverage.roic:.1%}",
            f"- **WACC**: {report.leverage.wacc:.1%}",
            f"- **ROIC-WACC利差**: {report.leverage.roic_spread:.1%}",
            "",
            "## 📈 盈利能力 (U)",
            "",
            f"- **ROE**: {report.utility.roe:.1%}",
            f"- **毛利率**: {report.utility.gross_margin:.1%}",
            f"- **净利率**: {report.utility.net_margin:.1%}",
            f"- **ROIC(3年均)**: {report.utility.roic_3yr_avg:.1%}",
            "",
            "## 🛡️ 护城河与可持续性 (E)",
            "",
            f"- **护城河类型**: {report.endurance.moat_type}",
            f"- **护城河强度**: {report.endurance.moat_strength:.0f}/100",
            f"- **行业生命周期**: {report.endurance.industry_lifecycle}",
            f"- **管理层质量**: {report.endurance.management_quality:.0f}/100",
            "",
            "---",
            "",
            "## 🎯 投资建议",
            "",
            f"**总体建议**: {report.recommendation}",
            "",
            f"**建议仓位**: {report.target_position}",
            "",
            "### ⚠️ 关键风险",
        ]
        
        for risk in report.key_risks:
            lines.append(f"- {risk}")
        
        lines.extend([
            "",
            "### 💡 关键机会",
        ])
        
        for opp in report.key_opportunities:
            lines.append(f"- {opp}")
        
        lines.extend([
            "",
            "---",
            "",
            "*报告生成时间: {}*".format(datetime.now().strftime('%Y-%m-%d %H:%M')),
            "*方法论: VALUE CELL 价值投资框架*",
        ])
        
        return '\n'.join(lines)


def demo_value_cell():
    """演示VALUE CELL分析"""
    print("=" * 80)
    print("💎 VALUE CELL 价值投资分析框架演示")
    print("=" * 80)
    print("\n💡 场景: 分析一只价值股的五个维度\n")
    
    # 创建分析器
    print("[1/5] 初始化VALUE CELL分析器...")
    analyzer = VALUECellAnalyzer()
    
    # 分析示例股票
    print("[2/5] 执行五维度价值投资分析...")
    report = analyzer.analyze("600519.SH")  # 茅台
    
    print(f"\n   ✅ 分析完成!")
    print(f"   💎 综合评分: {report.total_score:.1f}/100")
    print(f"   🎯 投资评级: {report.value_rating}")
    
    # 显示五维度评分
    print("\n[3/5] 五维度评分:")
    print("-" * 80)
    print(f"{'维度':<15} {'评分':<10} {'评估':<50}")
    print("-" * 80)
    print(f"{'V - 估值':<15} {report.v_score:<10.1f} {report.valuation.assessment:<50}")
    print(f"{'A - 资产':<15} {report.a_score:<10.1f} {report.assets.assessment:<50}")
    print(f"{'L - 杠杆':<15} {report.l_score:<10.1f} {report.leverage.assessment:<50}")
    print(f"{'U - 盈利':<15} {report.u_score:<10.1f} {report.utility.assessment:<50}")
    print(f"{'E - 持续':<15} {report.e_score:<10.1f} {report.endurance.assessment:<50}")
    
    # 显示估值详情
    print("\n[4/5] 估值分析详情:")
    print("-" * 80)
    print(f"   DCF内在价值: ¥{report.intrinsic_value:.2f}")
    print(f"   当前价格: ¥{report.current_price:.2f}")
    print(f"   安全边际: {report.valuation.margin_of_safety:.1f}%")
    print(f"   上涨空间: {report.upside_potential:.1f}%")
    print(f"   PE: {report.valuation.pe_ratio:.1f}x | PB: {report.valuation.pb_ratio:.1f}x")
    
    # 显示护城河
    print("\n[5/5] 护城河分析:")
    print("-" * 80)
    print(f"   护城河类型: {report.endurance.moat_type}")
    print(f"   护城河强度: {report.endurance.moat_strength:.0f}/100")
    print(f"   行业周期: {report.endurance.industry_lifecycle}")
    
    # 显示投资建议
    print("\n💡 投资建议:")
    print("-" * 80)
    print(f"   总体建议: {report.recommendation}")
    print(f"   建议仓位: {report.target_position}")
    print(f"   关键风险: {', '.join(report.key_risks)}")
    print(f"   关键机会: {', '.join(report.key_opportunities)}")
    
    # 生成完整报告
    print("\n📝 生成完整报告...")
    report_md = analyzer.generate_report_markdown(report)
    report_path = f"value_cell_report_{report.symbol.replace('.', '_')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
    print(f"   ✅ 报告已保存: {report_path}")
    
    print("\n" + "=" * 80)
    print("🎉 演示完成！VALUE CELL让价值投资更系统化！")
    print("=" * 80)
    print("\n💡 价值投资核心理念:")
    print("   V - 估值: 寻找安全边际")
    print("   A - 资产: 关注资产质量")
    print("   L - 杠杆: 优化资本结构")
    print("   U - 盈利: 衡量盈利能力")
    print("   E - 持续: 评估竞争优势")
    print("\n💎 记住: 价值投资是购买公司的一部分，而非猜测股价走势！")


if __name__ == "__main__":
    demo_value_cell()
