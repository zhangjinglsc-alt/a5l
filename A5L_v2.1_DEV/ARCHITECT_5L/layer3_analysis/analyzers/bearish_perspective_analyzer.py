#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Layer 3 - 空方视角风险审查系统 (Bearish Perspective Risk Review System)
以空方视角审视每一笔交易，发现潜在风险，验证策略逻辑

核心功能:
1. 风险自查清单 - 列出当前交易的潜在风险点
2. 策略逻辑审查 - 反驳式验证交易想法
3. 空方分析报告 - 生成专业的风险分析
4. 多空对比 - 平衡视角辅助决策

位置: Layer 3 (认知分析层) - 与情绪分析、研报阅读并列
作者: A5L Chief Architect
创建时间: 2026-05-02 (五一假期)
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """风险等级"""
    CRITICAL = "critical"  # 致命风险
    HIGH = "high"          # 高风险
    MEDIUM = "medium"      # 中风险
    LOW = "low"            # 低风险
    INFO = "info"          # 提示信息


@dataclass
class RiskItem:
    """风险项"""
    risk_type: str                    # 风险类型
    description: str                  # 风险描述
    level: RiskLevel                  # 风险等级
    probability: float                # 发生概率 (0-1)
    impact: float                     # 影响程度 (0-1)
    risk_score: float                 # 风险评分 (概率*影响)
    mitigation: str                   # 缓解措施
    evidence: List[str] = field(default_factory=list)  # 证据支持
    
    def to_dict(self) -> Dict:
        return {
            'risk_type': self.risk_type,
            'description': self.description,
            'level': self.level.value,
            'probability': self.probability,
            'impact': self.impact,
            'risk_score': self.risk_score,
            'mitigation': self.mitigation,
            'evidence': self.evidence
        }


@dataclass
class StrategyFlaw:
    """策略逻辑缺陷"""
    flaw_id: str
    aspect: str                       # 缺陷维度 (逻辑/数据/市场/执行)
    bearish_argument: str             # 空方论点
    counter_evidence: List[str]       # 反驳证据
    severity: str                     # 严重程度
    suggestion: str                   # 改进建议
    
    def to_dict(self) -> Dict:
        return {
            'flaw_id': self.flaw_id,
            'aspect': self.aspect,
            'bearish_argument': self.bearish_argument,
            'counter_evidence': self.counter_evidence,
            'severity': self.severity,
            'suggestion': self.suggestion
        }


@dataclass
class BearishAnalysisReport:
    """空方分析报告"""
    symbol: str
    analysis_date: str
    overall_risk_score: float         # 总体风险评分 (0-100)
    risk_level: str                   # 风险等级
    risk_items: List[RiskItem]        # 风险清单
    strategy_flaws: List[StrategyFlaw]  # 策略缺陷
    bearish_summary: str              # 空方观点总结
    recommendation: str               # 建议
    confidence: float                 # 分析置信度
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'analysis_date': self.analysis_date,
            'overall_risk_score': self.overall_risk_score,
            'risk_level': self.risk_level,
            'risk_items': [r.to_dict() for r in self.risk_items],
            'strategy_flaws': [f.to_dict() for f in self.strategy_flaws],
            'bearish_summary': self.bearish_summary,
            'recommendation': self.recommendation,
            'confidence': self.confidence
        }


class RiskSelfChecklist:
    """风险自查清单生成器"""
    
    def __init__(self):
        # 风险检查模板
        self.checklist_templates = {
            'valuation': {
                'name': '估值风险',
                'checks': [
                    {'question': '当前PE是否高于行业平均50%以上?', 'weight': 0.8},
                    {'question': '当前PB是否处于历史80%分位以上?', 'weight': 0.7},
                    {'question': 'PEG比率是否大于2?', 'weight': 0.6},
                    {'question': '自由现金流/市值比率是否低于3%?', 'weight': 0.5},
                ]
            },
            'technical': {
                'name': '技术风险',
                'checks': [
                    {'question': '是否处于历史高点附近?', 'weight': 0.9},
                    {'question': '成交量是否持续萎缩?', 'weight': 0.7},
                    {'question': 'RSI是否超过70(超买)?', 'weight': 0.6},
                    {'question': 'MACD是否出现顶背离?', 'weight': 0.7},
                    {'question': '是否跌破关键支撑位?', 'weight': 0.8},
                ]
            },
            'fundamental': {
                'name': '基本面风险',
                'checks': [
                    {'question': '最近季报营收是否下滑?', 'weight': 0.8},
                    {'question': '净利润增长率是否连续两季下降?', 'weight': 0.9},
                    {'question': '负债率是否超过70%?', 'weight': 0.6},
                    {'question': '经营性现金流是否为负?', 'weight': 0.7},
                    {'question': '是否有大股东减持?', 'weight': 0.8},
                ]
            },
            'market': {
                'name': '市场风险',
                'checks': [
                    {'question': '大盘是否处于下跌趋势?', 'weight': 0.8},
                    {'question': '行业板块是否轮动 away?', 'weight': 0.6},
                    {'question': 'VIX恐慌指数是否大于30?', 'weight': 0.7},
                    {'question': '是否有重大政策利空?', 'weight': 0.9},
                ]
            },
            'liquidity': {
                'name': '流动性风险',
                'checks': [
                    {'question': '日均成交额是否低于1亿?', 'weight': 0.6},
                    {'question': '换手率是否异常偏低?', 'weight': 0.5},
                    {'question': '是否有解禁/减持压力?', 'weight': 0.8},
                ]
            },
            'concentration': {
                'name': '集中度风险',
                'checks': [
                    {'question': '前五大客户收入占比是否超过50%?', 'weight': 0.7},
                    {'question': '单一供应商依赖度是否过高?', 'weight': 0.6},
                    {'question': '业务是否过度依赖单一产品?', 'weight': 0.7},
                ]
            }
        }
    
    def generate_checklist(self, symbol: str, market_data: Dict = None) -> Dict:
        """
        生成风险自查清单
        
        Args:
            symbol: 股票代码
            market_data: 市场数据
            
        Returns:
            结构化清单
        """
        logger.info(f"🛡️ 生成风险自查清单: {symbol}")
        
        checklist = {
            'symbol': symbol,
            'generated_at': datetime.now().isoformat(),
            'categories': {}
        }
        
        for category_id, category in self.checklist_templates.items():
            checklist['categories'][category_id] = {
                'name': category['name'],
                'items': category['checks'],
                'risk_score': 0.0,  # 待填写
                'max_score': sum(c['weight'] for c in category['checks'])
            }
        
        return checklist
    
    def evaluate_checklist(self, checklist: Dict, answers: Dict[str, List[bool]]) -> Dict:
        """
        评估清单结果
        
        Args:
            checklist: 清单
            answers: 各分类的答案 (True=有风险, False=无风险)
            
        Returns:
            评估结果
        """
        total_risk_score = 0
        total_max_score = 0
        category_scores = {}
        
        for category_id, category in checklist['categories'].items():
            category_answers = answers.get(category_id, [False] * len(category['items']))
            
            category_risk = 0
            for i, item in enumerate(category['items']):
                if category_answers[i]:  # 如果有风险
                    category_risk += item['weight']
            
            category_max = category['max_score']
            category_risk_ratio = category_risk / category_max if category_max > 0 else 0
            
            category_scores[category_id] = {
                'name': category['name'],
                'risk_score': category_risk,
                'max_score': category_max,
                'risk_ratio': category_risk_ratio,
                'level': self._get_risk_level(category_risk_ratio)
            }
            
            total_risk_score += category_risk
            total_max_score += category_max
        
        overall_ratio = total_risk_score / total_max_score if total_max_score > 0 else 0
        
        return {
            'symbol': checklist['symbol'],
            'evaluated_at': datetime.now().isoformat(),
            'overall_risk_ratio': overall_ratio,
            'overall_level': self._get_risk_level(overall_ratio),
            'categories': category_scores,
            'total_checks': sum(len(c['items']) for c in checklist['categories'].values()),
            'risky_checks': sum(1 for cat_ans in answers.values() for ans in cat_ans if ans)
        }
    
    def _get_risk_level(self, ratio: float) -> str:
        """根据比例获取风险等级"""
        if ratio >= 0.7:
            return 'CRITICAL'
        elif ratio >= 0.5:
            return 'HIGH'
        elif ratio >= 0.3:
            return 'MEDIUM'
        elif ratio >= 0.1:
            return 'LOW'
        else:
            return 'SAFE'


class StrategyLogicReviewer:
    """策略逻辑审查器 - 反驳式验证"""
    
    def __init__(self):
        self.review_dimensions = [
            'logic',      # 逻辑一致性
            'data',       # 数据支撑
            'market',     # 市场环境
            'timing',     # 时机选择
            'position',   # 仓位管理
            'exit'        # 退出策略
        ]
    
    def review_strategy(self, symbol: str, strategy_logic: str, 
                       supporting_data: Dict = None) -> List[StrategyFlaw]:
        """
        审查策略逻辑
        
        Args:
            symbol: 股票代码
            strategy_logic: 策略逻辑描述
            supporting_data: 支撑数据
            
        Returns:
            发现的缺陷列表
        """
        logger.info(f"🔍 审查策略逻辑: {symbol}")
        
        flaws = []
        
        # 模拟审查各个维度 (实际应接入LLM进行深度分析)
        # 这里使用预设的审查点作为示例
        
        # 维度1: 逻辑审查
        flaws.append(StrategyFlaw(
            flaw_id="LOGIC_001",
            aspect="逻辑",
            bearish_argument="当前买入逻辑基于'突破新高'，但未考虑是否为假突破",
            counter_evidence=["成交量未同步放大", "突破幅度小于3%"],
            severity="high",
            suggestion="等待回踩确认或放量突破后再入场"
        ))
        
        # 维度2: 数据审查
        flaws.append(StrategyFlaw(
            flaw_id="DATA_001",
            aspect="数据",
            bearish_argument="业绩增长数据与估值提升不匹配",
            counter_evidence=["Q1净利润增长仅15%，但股价已上涨80%", "行业平均PE为20，当前PE为45"],
            severity="critical",
            suggestion="重新评估估值合理性，考虑获利了结"
        ))
        
        # 维度3: 市场环境
        flaws.append(StrategyFlaw(
            flaw_id="MARKET_001",
            aspect="市场",
            bearish_argument="大盘处于调整期，个股难以独善其身",
            counter_evidence=["上证指数跌破20日均线", "北向资金连续3日净流出"],
            severity="medium",
            suggestion="降低仓位或等待大盘企稳"
        ))
        
        # 维度4: 时机选择
        flaws.append(StrategyFlaw(
            flaw_id="TIMING_001",
            aspect="时机",
            bearish_argument="即将面临业绩披露期，不确定性增加",
            counter_evidence=["距离Q2财报披露仅剩2周", "前期涨幅过大，财报超预期难度高"],
            severity="high",
            suggestion="财报披露后再做决策，或提前减仓避险"
        ))
        
        # 维度5: 仓位管理
        flaws.append(StrategyFlaw(
            flaw_id="POSITION_001",
            aspect="仓位",
            bearish_argument="计划仓位过重，单票风险集中度过高",
            counter_evidence=["计划买入30%仓位", "该板块已有其他持仓，合计超50%"],
            severity="medium",
            suggestion="将仓位控制在15%以内，分散风险"
        ))
        
        # 维度6: 退出策略
        flaws.append(StrategyFlaw(
            flaw_id="EXIT_001",
            aspect="退出",
            bearish_argument="未设定明确的止损和止盈点",
            counter_evidence=["策略中未提及止损位", "缺乏应对黑天鹅事件的预案"],
            severity="high",
            suggestion="设定明确止损点(-8%)和止盈点(+20%)，严格执行"
        ))
        
        return flaws
    
    def generate_counter_strategy(self, symbol: str, original_strategy: str) -> Dict:
        """
        生成反方策略 (做空视角)
        
        Args:
            symbol: 股票代码
            original_strategy: 原策略
            
        Returns:
            反方策略
        """
        return {
            'symbol': symbol,
            'perspective': 'bearish',
            'counter_strategy': f"针对{symbol}的看多策略，反方建议:",
            'key_points': [
                "等待回调至支撑位再考虑",
                "观察成交量是否持续萎缩",
                "关注大股东减持动向",
                "评估业绩能否支撑当前估值"
            ],
            'alternative_actions': [
                "观望等待更好入场点",
                "小仓位试探性买入",
                "买入同行业估值更低的标的",
                "配置部分对冲仓位"
            ],
            'generated_at': datetime.now().isoformat()
        }


class BearishPerspectiveAnalyzer:
    """
    空方视角分析器 - Layer 3核心组件
    
    以空方视角审视交易，发现潜在风险
    """
    
    def __init__(self):
        self.checklist_generator = RiskSelfChecklist()
        self.strategy_reviewer = StrategyLogicReviewer()
        
        logger.info("🐻 空方视角分析器初始化完成")
    
    def comprehensive_risk_analysis(self, symbol: str, 
                                   position_info: Dict = None,
                                   strategy_logic: str = None) -> BearishAnalysisReport:
        """
        全面的风险分析
        
        Args:
            symbol: 股票代码
            position_info: 持仓信息
            strategy_logic: 策略逻辑
            
        Returns:
            空方分析报告
        """
        logger.info(f"🐻 开始空方视角分析: {symbol}")
        
        # 1. 生成风险清单
        risk_items = self._generate_risk_items(symbol, position_info)
        
        # 2. 审查策略逻辑
        strategy_flaws = []
        if strategy_logic:
            strategy_flaws = self.strategy_reviewer.review_strategy(
                symbol, strategy_logic
            )
        
        # 3. 计算总体风险评分
        overall_score = self._calculate_overall_risk(risk_items, strategy_flaws)
        
        # 4. 生成空方观点总结
        bearish_summary = self._generate_bearish_summary(symbol, risk_items, strategy_flaws)
        
        # 5. 生成建议
        recommendation = self._generate_recommendation(overall_score, risk_items)
        
        report = BearishAnalysisReport(
            symbol=symbol,
            analysis_date=datetime.now().isoformat(),
            overall_risk_score=overall_score,
            risk_level=self._get_overall_risk_level(overall_score),
            risk_items=risk_items,
            strategy_flaws=strategy_flaws,
            bearish_summary=bearish_summary,
            recommendation=recommendation,
            confidence=0.85
        )
        
        logger.info(f"✅ 空方分析完成: {symbol} - 风险评分 {overall_score:.1f}/100")
        
        return report
    
    def _generate_risk_items(self, symbol: str, position_info: Dict = None) -> List[RiskItem]:
        """生成风险项列表"""
        risks = []
        
        # 模拟风险项 (实际应基于真实数据)
        risk_templates = [
            {
                'type': '估值风险',
                'desc': f'{symbol}当前PE为45倍，显著高于行业平均的20倍',
                'level': RiskLevel.HIGH,
                'prob': 0.7,
                'impact': 0.8,
                'mitigation': '设定PE回归止损线，或分批减仓',
                'evidence': ['行业PE数据', '历史估值分位']
            },
            {
                'type': '技术风险',
                'desc': '股价处于历史高点附近，RSI指标显示超买',
                'level': RiskLevel.MEDIUM,
                'prob': 0.6,
                'impact': 0.5,
                'mitigation': '等待回调至支撑位，或设置移动止损',
                'evidence': ['RSI=78', '股价接近前高']
            },
            {
                'type': '基本面风险',
                'desc': 'Q2业绩预告低于市场预期，增长率放缓',
                'level': RiskLevel.CRITICAL,
                'prob': 0.8,
                'impact': 0.9,
                'mitigation': '财报披露前减仓避险',
                'evidence': ['业绩预告', '分析师下调预期']
            },
            {
                'type': '市场风险',
                'desc': '大盘处于调整期，系统性风险增加',
                'level': RiskLevel.MEDIUM,
                'prob': 0.5,
                'impact': 0.6,
                'mitigation': '降低仓位，增加防御性配置',
                'evidence': ['大盘跌破20日线', 'VIX上升']
            },
            {
                'type': '流动性风险',
                'desc': '日均成交额下降，可能出现流动性不足',
                'level': RiskLevel.LOW,
                'prob': 0.3,
                'impact': 0.4,
                'mitigation': '控制单笔交易规模',
                'evidence': ['成交量环比下降30%']
            }
        ]
        
        for template in risk_templates:
            risks.append(RiskItem(
                risk_type=template['type'],
                description=template['desc'],
                level=template['level'],
                probability=template['prob'],
                impact=template['impact'],
                risk_score=template['prob'] * template['impact'],
                mitigation=template['mitigation'],
                evidence=template['evidence']
            ))
        
        return risks
    
    def _calculate_overall_risk(self, risk_items: List[RiskItem], 
                               strategy_flaws: List[StrategyFlaw]) -> float:
        """计算总体风险评分 (0-100)"""
        if not risk_items:
            return 0
        
        # 基于风险项计算
        item_scores = [item.risk_score * 100 for item in risk_items]
        avg_item_score = sum(item_scores) / len(item_scores)
        
        # 基于策略缺陷调整
        flaw_penalty = len(strategy_flaws) * 5  # 每个缺陷+5分风险
        
        # 基于缺陷严重程度额外调整
        severity_multiplier = 1.0
        for flaw in strategy_flaws:
            if flaw.severity == 'critical':
                severity_multiplier += 0.2
            elif flaw.severity == 'high':
                severity_multiplier += 0.1
        
        final_score = min(100, (avg_item_score + flaw_penalty) * severity_multiplier)
        
        return round(final_score, 1)
    
    def _get_overall_risk_level(self, score: float) -> str:
        """获取总体风险等级"""
        if score >= 70:
            return '极高风险'
        elif score >= 50:
            return '高风险'
        elif score >= 30:
            return '中等风险'
        elif score >= 15:
            return '低风险'
        else:
            return '安全'
    
    def _generate_bearish_summary(self, symbol: str, 
                                 risk_items: List[RiskItem],
                                 strategy_flaws: List[StrategyFlaw]) -> str:
        """生成空方观点总结"""
        critical_count = sum(1 for r in risk_items if r.level == RiskLevel.CRITICAL)
        high_count = sum(1 for r in risk_items if r.level == RiskLevel.HIGH)
        
        summary_parts = [
            f"【空方视角】对{symbol}的审慎评估：",
            "",
            f"1. 风险概况：识别到{len(risk_items)}个主要风险点，",
            f"   其中致命风险{critical_count}个，高风险{high_count}个。",
            "",
            "2. 核心担忧：",
        ]
        
        # 添加Top 3风险
        top_risks = sorted(risk_items, key=lambda x: x.risk_score, reverse=True)[:3]
        for i, risk in enumerate(top_risks, 1):
            summary_parts.append(f"   {i}. {risk.risk_type}：{risk.description[:50]}...")
        
        if strategy_flaws:
            summary_parts.extend([
                "",
                f"3. 策略缺陷：发现{len(strategy_flaws)}个逻辑漏洞，",
                "   主要涉及逻辑严谨性、数据支撑、时机选择等方面。",
            ])
        
        summary_parts.extend([
            "",
            "4. 空方结论：当前价格已充分甚至过度反映乐观预期，",
            "   下行风险大于上行空间，建议保持谨慎。"
        ])
        
        return '\n'.join(summary_parts)
    
    def _generate_recommendation(self, risk_score: float, 
                                risk_items: List[RiskItem]) -> str:
        """生成建议"""
        if risk_score >= 70:
            return "强烈建议观望，当前风险过高，不宜入场。如已持仓，考虑减仓避险。"
        elif risk_score >= 50:
            return "建议谨慎，可小仓位试探，严格设置止损(-8%)。"
        elif risk_score >= 30:
            return "可以参与，但需控制仓位(不超过15%)，密切关注风险点变化。"
        else:
            return "风险可控，可按计划执行，但仍需设定止损。"
    
    def generate_risk_checklist_for_user(self, symbol: str) -> str:
        """
        生成给用户的风险自查清单 (Markdown格式)
        
        Args:
            symbol: 股票代码
            
        Returns:
            Markdown格式的清单
        """
        checklist = self.checklist_generator.generate_checklist(symbol)
        
        lines = [
            f"# 🛡️ {symbol} 风险自查清单",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "**说明**: 请以空方视角诚实回答以下问题",
            "",
            "---",
            "",
        ]
        
        for category_id, category in checklist['categories'].items():
            lines.append(f"## {category['name']}")
            lines.append("")
            
            for i, item in enumerate(category['items'], 1):
                lines.append(f"{i}. [ ] {item['question']} (权重: {item['weight']})")
            
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "## 使用说明",
            "",
            "1. 请诚实勾选所有符合当前情况的问题",
            "2. 每个勾选项代表一个潜在风险点",
            "3. 将勾选结果输入系统进行风险评估",
            "4. 风险评分 = Σ(勾选权重) / Σ(总权重)",
            "",
            "## 风险等级对照",
            "",
            "| 风险比例 | 等级 | 建议 |",
            "|----------|------|------|",
            "| 70%+ | 🔴 致命 | 强烈建议观望 |",
            "| 50-69% | 🟠 高风险 | 谨慎参与 |",
            "| 30-49% | 🟡 中等 | 控制仓位 |",
            "| 10-29% | 🟢 低 | 可以参与 |",
            "| <10% | ⚪ 安全 | 按计划执行 |",
            "",
            f"*清单生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return '\n'.join(lines)
    
    def save_risk_report(self, report: BearishAnalysisReport, 
                        output_path: str = None) -> str:
        """保存风险报告"""
        if output_path is None:
            output_path = f"KIWI/risk_analysis/{report.symbol}_bearish_report.json"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 风险报告已保存: {output_path}")
        return output_path


def demo_bearish_analysis():
    """演示: 空方视角分析"""
    
    print("=" * 80)
    print("🐻 A5L 空方视角风险审查系统演示")
    print("=" * 80)
    print("\n💡 场景: 以空方视角审视 300308.SZ (中际旭创) 的交易计划\n")
    
    # 创建分析器
    print("[1/5] 初始化空方视角分析器...")
    analyzer = BearishPerspectiveAnalyzer()
    
    # 模拟持仓信息
    position_info = {
        'symbol': '300308.SZ',
        'planned_position': 0.20,  # 计划20%仓位
        'entry_price': 145.0,
        'stop_loss': 130.0,
        'take_profit': 180.0
    }
    
    # 模拟策略逻辑
    strategy_logic = """
    买入逻辑:
    1. CPO赛道龙头，业绩高增长
    2. 股价突破历史新高，趋势强劲
    3. 机构持续买入，北向资金流入
    4. AI算力需求爆发，行业景气度高
    
    计划: 买入20%仓位，止损-10%，止盈+25%
    """
    
    # 执行全面分析
    print("[2/5] 执行空方视角风险分析...")
    report = analyzer.comprehensive_risk_analysis(
        symbol='300308.SZ',
        position_info=position_info,
        strategy_logic=strategy_logic
    )
    
    print(f"\n   ✅ 分析完成!")
    print(f"   📊 总体风险评分: {report.overall_risk_score}/100")
    print(f"   🚨 风险等级: {report.risk_level}")
    
    # 显示风险清单
    print("\n[3/5] 风险清单详情:")
    print("-" * 80)
    print(f"{'风险类型':<12} {'等级':<8} {'概率':<8} {'影响':<8} {'评分':<8} {'描述':<30}")
    print("-" * 80)
    
    for risk in report.risk_items:
        level_emoji = "🔴" if risk.level == RiskLevel.CRITICAL else "🟠" if risk.level == RiskLevel.HIGH else "🟡"
        print(f"{risk.risk_type:<12} {level_emoji:<8} {risk.probability:<8.0%} {risk.impact:<8.0%} "
              f"{risk.risk_score:<8.2f} {risk.description[:30]}...")
    
    # 显示策略缺陷
    print("\n[4/5] 策略逻辑缺陷:")
    print("-" * 80)
    
    for flaw in report.strategy_flaws:
        severity_emoji = "🔴" if flaw.severity == 'critical' else "🟠" if flaw.severity == 'high' else "🟡"
        print(f"\n{severity_emoji} [{flaw.aspect}] {flaw.flaw_id}")
        print(f"   空方论点: {flaw.bearish_argument}")
        print(f"   建议: {flaw.suggestion}")
    
    # 显示总结和建议
    print("\n[5/5] 空方观点总结:")
    print("-" * 80)
    print(report.bearish_summary)
    
    print("\n💡 最终建议:")
    print(f"   {report.recommendation}")
    
    # 生成自查清单
    print("\n📋 生成风险自查清单...")
    checklist = analyzer.generate_risk_checklist_for_user('300308.SZ')
    checklist_path = f"risk_checklist_300308.md"
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(checklist)
    print(f"   ✅ 清单已保存: {checklist_path}")
    
    # 保存报告
    print("\n💾 保存分析报告...")
    report_path = analyzer.save_risk_report(report)
    print(f"   ✅ 报告已保存: {report_path}")
    
    print("\n" + "=" * 80)
    print("🎉 演示完成！空方视角分析让交易更加审慎！")
    print("=" * 80)
    print("\n💡 使用建议:")
    print("   1. 每次交易前运行空方视角分析")
    print("   2. 诚实填写风险自查清单")
    print("   3. 关注策略逻辑缺陷，改进交易计划")
    print("   4. 将风险报告归档到KIWI，建立风险档案")
    print("\n🛡️ 记住：空方视角不是为了阻止交易，而是为了更全面地认识风险！")


if __name__ == "__main__":
    demo_bearish_analysis()
