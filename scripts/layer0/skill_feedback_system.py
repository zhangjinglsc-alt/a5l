#!/usr/bin/env python3
"""
A5L Skill Feedback Loop & Dynamic Loading System v1.0
技能反馈闭环与动态加载系统

架构改进:
1. L1-L5 → KG 结果回写 (反馈闭环)
2. 技能热插拔 (根据市场环境动态加载)
3. 技能置信度进化 (基于执行结果自我优化)

执行时间: 2026-05-04 02:49
架构意义: 实现完整的学习-执行-反馈-进化闭环
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class MarketRegime(Enum):
    """市场环境状态"""
    BULL = "牛市"
    BEAR = "熊市"
    RANGING = "震荡市"
    RECOVERY = "复苏期"
    DECLINE = "衰退期"

class SkillType(Enum):
    """技能类型"""
    VALUE = "价值投资"      # Buffett
    GROWTH = "成长投资"     # CANSLIM
    TECHNICAL = "技术分析"  # 技术指标
    MOMENTUM = "动量策略"   # 因子投资
    MEAN_REVERSION = "均值回归"  # 超短
    MACRO = "宏观对冲"      # 资产配置

@dataclass
class SkillExecutionResult:
    """技能执行结果"""
    skill_id: str
    skill_type: SkillType
    stock_code: str
    action: str  # BUY, SELL, HOLD
    position_pct: float
    entry_price: float
    exit_price: Optional[float] = None
    pnl_pct: Optional[float] = None
    holding_days: int = 0
    market_regime: MarketRegime = MarketRegime.RANGING
    execution_time: str = ""
    
@dataclass
class SkillConfidence:
    """技能置信度"""
    skill_id: str
    skill_type: SkillType
    overall_score: float  # 0-100
    win_rate: float  # 胜率
    avg_return: float  # 平均收益
    sharpe_ratio: float
    max_drawdown: float
    best_regime: MarketRegime  # 最适合的市场环境
    worst_regime: MarketRegime  # 最不适合的市场环境
    total_trades: int
    last_updated: str

class SkillFeedbackSystem:
    """
    技能反馈系统 - 实现L1-L5到KG的结果回写
    
    核心功能:
    1. 记录技能执行结果
    2. 计算技能置信度
    3. 更新KG中的技能表现数据
    4. 技能进化建议
    """
    
    def __init__(self, kg_hub):
        self.kg_hub = kg_hub
        self.execution_history = []
        self.skill_confidence = {}
        print("🔄 技能反馈系统初始化")
        
    def record_execution(self, result: SkillExecutionResult):
        """
        记录技能执行结果 - L1-L5调用KG回写
        
        这是反馈闭环的关键节点!
        """
        print(f"\n📝 记录技能执行: {result.skill_id} @ {result.stock_code}")
        
        # 1. 存储执行记录
        self.execution_history.append(asdict(result))
        
        # 2. 更新技能置信度
        self._update_skill_confidence(result)
        
        # 3. 回写到KG (关键!)
        self._write_back_to_kg(result)
        
        print(f"✅ 执行结果已回写至KG")
        
    def _update_skill_confidence(self, result: SkillExecutionResult):
        """更新技能置信度"""
        skill_id = result.skill_id
        
        if skill_id not in self.skill_confidence:
            self.skill_confidence[skill_id] = {
                'total_trades': 0,
                'wins': 0,
                'total_return': 0,
                'regime_performance': {regime: [] for regime in MarketRegime}
            }
        
        conf = self.skill_confidence[skill_id]
        conf['total_trades'] += 1
        
        if result.pnl_pct and result.pnl_pct > 0:
            conf['wins'] += 1
        
        if result.pnl_pct:
            conf['total_return'] += result.pnl_pct
            conf['regime_performance'][result.market_regime].append(result.pnl_pct)
            
    def _write_back_to_kg(self, result: SkillExecutionResult):
        """回写执行结果到KG - 这是架构改进的核心!"""
        
        # 创建执行实体
        execution_entity = {
            'entity_type': 'skill_execution',
            'entity_id': f"exec_{result.skill_id}_{result.stock_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'skill_id': result.skill_id,
            'skill_type': result.skill_type.value,
            'stock_code': result.stock_code,
            'action': result.action,
            'pnl_pct': result.pnl_pct,
            'market_regime': result.market_regime.value,
            'execution_time': result.execution_time or datetime.now().isoformat(),
            'relations': [
                {'target': f"skill_{result.skill_id}", 'relation': 'executed_by'},
                {'target': f"stock_{result.stock_code}", 'relation': 'applied_to'},
                {'target': f"regime_{result.market_regime.value}", 'relation': 'executed_in'}
            ]
        }
        
        # 存储到KG (实际实现中调用KG API)
        print(f"   ↳ KG实体创建: {execution_entity['entity_id']}")
        print(f"   ↳ 关联: skill_{result.skill_id} → stock_{result.stock_code}")
        
    def calculate_skill_confidence(self, skill_id: str) -> SkillConfidence:
        """计算技能置信度 - 基于历史执行结果"""
        
        if skill_id not in self.skill_confidence:
            return SkillConfidence(
                skill_id=skill_id,
                skill_type=SkillType.VALUE,
                overall_score=50,
                win_rate=0.5,
                avg_return=0,
                sharpe_ratio=1.0,
                max_drawdown=0,
                best_regime=MarketRegime.RANGING,
                worst_regime=MarketRegime.RANGING,
                total_trades=0,
                last_updated=datetime.now().isoformat()
            )
        
        conf = self.skill_confidence[skill_id]
        total = conf['total_trades']
        
        if total == 0:
            return None
            
        win_rate = conf['wins'] / total
        avg_return = conf['total_return'] / total
        
        # 计算不同市场环境下的表现
        regime_performance = {}
        for regime, returns in conf['regime_performance'].items():
            if returns:
                regime_performance[regime] = sum(returns) / len(returns)
            else:
                regime_performance[regime] = 0
        
        best_regime = max(regime_performance, key=regime_performance.get)
        worst_regime = min(regime_performance, key=regime_performance.get)
        
        # 综合置信度评分 (0-100)
        overall_score = (
            win_rate * 40 +  # 胜率权重40%
            min(avg_return * 10, 30) +  # 收益权重30%
            (1 if best_regime != worst_regime else 0) * 20 +  # 环境适应性20%
            min(total / 10, 10)  # 样本量权重10%
        )
        
        return SkillConfidence(
            skill_id=skill_id,
            skill_type=SkillType.VALUE,  # 简化处理
            overall_score=overall_score,
            win_rate=win_rate,
            avg_return=avg_return,
            sharpe_ratio=1.5,  # 简化
            max_drawdown=0.15,  # 简化
            best_regime=best_regime,
            worst_regime=worst_regime,
            total_trades=total,
            last_updated=datetime.now().isoformat()
        )
        
    def get_skill_evolution_suggestion(self, skill_id: str) -> List[str]:
        """获取技能进化建议 - 基于反馈数据"""
        
        confidence = self.calculate_skill_confidence(skill_id)
        suggestions = []
        
        if confidence.overall_score < 50:
            suggestions.append(f"技能 {skill_id} 置信度较低({confidence.overall_score:.1f})，建议降低权重或停用")
        
        if confidence.best_regime != confidence.worst_regime:
            suggestions.append(f"该技能在 {confidence.best_regime.value} 表现最佳，在 {confidence.worst_regime.value} 表现最差")
            suggestions.append(f"建议: 在 {confidence.best_regime.value} 时增加该技能权重")
        
        if confidence.total_trades < 10:
            suggestions.append(f"样本量不足({confidence.total_trades})，需要更多数据验证")
            
        return suggestions


class DynamicSkillLoader:
    """
    动态技能加载器 - CIO根据市场环境动态加载技能组合
    
    核心功能:
    1. 市场环境识别
    2. 技能库管理 (热插拔)
    3. 技能组合优化
    4. 实时加载/卸载
    """
    
    def __init__(self, feedback_system: SkillFeedbackSystem):
        self.feedback = feedback_system
        self.skill_library = {}  # 技能库
        self.active_skills = {}  # 当前激活的技能
        self.current_regime = MarketRegime.RANGING
        self._init_skill_library()
        print("🔌 动态技能加载器初始化")
        
    def _init_skill_library(self):
        """初始化技能库"""
        self.skill_library = {
            # 价值投资技能
            'buffett_v12': {
                'name': 'VALUE_CELL Buffett集成版',
                'type': SkillType.VALUE,
                'description': '巴菲特价值投资框架',
                'best_regimes': [MarketRegime.BEAR, MarketRegime.RECOVERY],
                'params': {'moat_weight': 0.3, 'margin_safety': 0.3}
            },
            
            # 成长投资技能
            'canslim_v10': {
                'name': 'CANSLIM成长策略',
                'type': SkillType.GROWTH,
                'description': '欧奈尔CANSLIM成长股策略',
                'best_regimes': [MarketRegime.BULL, MarketRegime.RECOVERY],
                'params': {'eps_growth_threshold': 0.25}
            },
            
            # 技术分析技能
            'technical_v15': {
                'name': '技术分析综合版',
                'type': SkillType.TECHNICAL,
                'description': '技术指标综合分析',
                'best_regimes': [MarketRegime.RANGING],
                'params': {'ma_periods': [5, 10, 20, 60]}
            },
            
            # 动量策略技能
            'momentum_v8': {
                'name': '因子投资动量策略',
                'type': SkillType.MOMENTUM,
                'description': '量化动量因子策略',
                'best_regimes': [MarketRegime.BULL],
                'params': {'lookback': 60, 'holding': 20}
            },
            
            # 均值回归技能
            'yangguan_v12': {
                'name': '阳关大道超短策略',
                'type': SkillType.MEAN_REVERSION,
                'description': '浪主超短线交易系统',
                'best_regimes': [MarketRegime.RANGING, MarketRegime.BULL],
                'params': {'stop_loss': 0.05, 'take_profit': 0.10}
            },
            
            # 宏观对冲技能
            'macro_v5': {
                'name': '宏观资产配置',
                'type': SkillType.MACRO,
                'description': '基于宏观周期的资产配置',
                'best_regimes': [MarketRegime.DECLINE, MarketRegime.RECOVERY],
                'params': {'cycle_weight': 0.4}
            }
        }
        
        print(f"✅ 技能库初始化: {len(self.skill_library)} 个技能")
        
    def detect_market_regime(self, market_data: Dict) -> MarketRegime:
        """
        识别当前市场环境
        
        基于多维度指标判断:
        - 趋势指标 (MA排列)
        - 波动率
        - 成交量
        - 市场情绪
        """
        # 简化实现 - 实际应基于复杂算法
        trend_score = market_data.get('trend_score', 0)  # -100 to 100
        volatility = market_data.get('volatility', 0.2)
        
        if trend_score > 50 and volatility < 0.25:
            return MarketRegime.BULL
        elif trend_score < -50 and volatility > 0.25:
            return MarketRegime.BEAR
        elif abs(trend_score) < 20:
            return MarketRegime.RANGING
        elif trend_score > 0:
            return MarketRegime.RECOVERY
        else:
            return MarketRegime.DECLINE
            
    def load_skill_combination(self, regime: MarketRegime) -> Dict[str, Any]:
        """
        根据市场环境加载最优技能组合
        
        这是CIO的核心能力!
        """
        print(f"\n🔌 加载技能组合: {regime.value}")
        
        # 1. 筛选适合当前环境的技能
        suitable_skills = []
        for skill_id, skill in self.skill_library.items():
            if regime in skill['best_regimes']:
                # 获取技能置信度
                confidence = self.feedback.calculate_skill_confidence(skill_id)
                if confidence and confidence.overall_score > 40:  # 置信度门槛
                    suitable_skills.append({
                        'id': skill_id,
                        'skill': skill,
                        'confidence': confidence.overall_score,
                        'win_rate': confidence.win_rate
                    })
        
        # 2. 按置信度排序
        suitable_skills.sort(key=lambda x: x['confidence'], reverse=True)
        
        # 3. 选择 top 3-5 个技能
        selected = suitable_skills[:4]
        
        # 4. 计算权重 (基于置信度)
        total_conf = sum(s['confidence'] for s in selected)
        for s in selected:
            s['weight'] = s['confidence'] / total_conf if total_conf > 0 else 1/len(selected)
        
        self.active_skills = {s['id']: s for s in selected}
        self.current_regime = regime
        
        print(f"✅ 已加载 {len(selected)} 个技能:")
        for s in selected:
            print(f"   • {s['skill']['name']}: 权重{s['weight']:.1%}, 置信度{s['confidence']:.1f}")
        
        return self.active_skills
        
    def hot_swap_skill(self, skill_id: str, action: str = 'load'):
        """
        技能热插拔 - 运行时动态加载/卸载
        
        action: 'load' | 'unload' | 'reload'
        """
        if action == 'load':
            if skill_id in self.skill_library:
                skill = self.skill_library[skill_id]
                confidence = self.feedback.calculate_skill_confidence(skill_id)
                self.active_skills[skill_id] = {
                    'id': skill_id,
                    'skill': skill,
                    'confidence': confidence.overall_score if confidence else 50,
                    'weight': 0.2  # 默认权重
                }
                print(f"🔌 热加载技能: {skill['name']}")
            else:
                print(f"❌ 技能 {skill_id} 不存在")
                
        elif action == 'unload':
            if skill_id in self.active_skills:
                removed = self.active_skills.pop(skill_id)
                print(f"🔌 热卸载技能: {removed['skill']['name']}")
            else:
                print(f"❌ 技能 {skill_id} 未加载")
                
        elif action == 'reload':
            # 重新加载并更新参数
            if skill_id in self.active_skills:
                self.hot_swap_skill(skill_id, 'unload')
            self.hot_swap_skill(skill_id, 'load')
            print(f"🔄 重新加载技能: {skill_id}")
            
    def execute_with_active_skills(self, stock_code: str) -> Dict:
        """
        使用当前激活的技能组合执行分析
        
        这是CIO的实际工作流程!
        """
        print(f"\n🎯 执行多技能分析: {stock_code}")
        
        results = []
        for skill_id, skill_info in self.active_skills.items():
            skill = skill_info['skill']
            weight = skill_info['weight']
            
            # 模拟执行技能
            print(f"   执行: {skill['name']} (权重{weight:.1%})")
            
            # 模拟结果
            result = {
                'skill_id': skill_id,
                'skill_name': skill['name'],
                'weight': weight,
                'signal': 'BUY',  # BUY, SELL, HOLD
                'confidence': skill_info['confidence'],
                'rationale': f"基于{skill['type'].value}分析"
            }
            results.append(result)
        
        # 加权综合
        buy_score = sum(r['weight'] for r in results if r['signal'] == 'BUY')
        sell_score = sum(r['weight'] for r in results if r['signal'] == 'SELL')
        
        final_signal = 'BUY' if buy_score > sell_score else 'SELL' if sell_score > buy_score else 'HOLD'
        final_confidence = sum(r['weight'] * r['confidence'] for r in results)
        
        final_result = {
            'stock_code': stock_code,
            'market_regime': self.current_regime.value,
            'active_skills': list(self.active_skills.keys()),
            'skill_results': results,
            'final_signal': final_signal,
            'final_confidence': final_confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ 综合结果: {final_signal} (置信度{final_confidence:.1f})")
        
        # 记录执行结果 (反馈闭环!)
        execution = SkillExecutionResult(
            skill_id='combined',
            skill_type=SkillType.VALUE,
            stock_code=stock_code,
            action=final_signal,
            position_pct=0.2,
            entry_price=100.0,
            market_regime=self.current_regime
        )
        self.feedback.record_execution(execution)
        
        return final_result


def demo():
    """演示技能反馈闭环与动态加载"""
    print("="*70)
    print("🔄 A5L Skill Feedback Loop & Dynamic Loading Demo")
    print("="*70)
    
    # 初始化系统
    from kg_knowledge_hub import KnowledgeGuardianHub
    kg_hub = KnowledgeGuardianHub()
    feedback = SkillFeedbackSystem(kg_hub)
    loader = DynamicSkillLoader(feedback)
    
    # Demo 1: 模拟历史执行记录 (构建反馈数据)
    print("\n" + "-"*70)
    print("【Demo 1】模拟历史执行 - 构建反馈数据")
    print("-"*70)
    
    # 模拟价值投资在熊市中的表现
    for i in range(5):
        result = SkillExecutionResult(
            skill_id='buffett_v12',
            skill_type=SkillType.VALUE,
            stock_code=f'00000{i}',
            action='BUY',
            position_pct=0.2,
            entry_price=100,
            exit_price=115,
            pnl_pct=0.15,
            market_regime=MarketRegime.BEAR
        )
        feedback.record_execution(result)
    
    # 模拟动量策略在牛市中的表现
    for i in range(5):
        result = SkillExecutionResult(
            skill_id='momentum_v8',
            skill_type=SkillType.MOMENTUM,
            stock_code=f'30000{i}',
            action='BUY',
            position_pct=0.2,
            entry_price=100,
            exit_price=130,
            pnl_pct=0.30,
            market_regime=MarketRegime.BULL
        )
        feedback.record_execution(result)
    
    # Demo 2: 查看技能置信度
    print("\n" + "-"*70)
    print("【Demo 2】技能置信度评估")
    print("-"*70)
    
    for skill_id in ['buffett_v12', 'momentum_v8']:
        conf = feedback.calculate_skill_confidence(skill_id)
        print(f"\n技能: {skill_id}")
        print(f"  综合置信度: {conf.overall_score:.1f}/100")
        print(f"  胜率: {conf.win_rate:.1%}")
        print(f"  平均收益: {conf.avg_return:.1%}")
        print(f"  最佳环境: {conf.best_regime.value}")
        print(f"  交易次数: {conf.total_trades}")
        
        # 进化建议
        suggestions = feedback.get_skill_evolution_suggestion(skill_id)
        if suggestions:
            print(f"  进化建议:")
            for s in suggestions:
                print(f"    → {s}")
    
    # Demo 3: 动态加载技能组合
    print("\n" + "-"*70)
    print("【Demo 3】根据市场环境动态加载技能")
    print("-"*70)
    
    # 场景A: 牛市
    print("\n场景A: 牛市环境")
    bull_skills = loader.load_skill_combination(MarketRegime.BULL)
    
    # 场景B: 熊市
    print("\n场景B: 熊市环境")
    bear_skills = loader.load_skill_combination(MarketRegime.BEAR)
    
    # 场景C: 震荡市
    print("\n场景C: 震荡市环境")
    range_skills = loader.load_skill_combination(MarketRegime.RANGING)
    
    # Demo 4: 技能热插拔
    print("\n" + "-"*70)
    print("【Demo 4】技能热插拔")
    print("-"*70)
    
    # 运行时加载新技能
    loader.hot_swap_skill('yangguan_v12', 'load')
    
    # 运行时卸载技能
    loader.hot_swap_skill('momentum_v8', 'unload')
    
    print(f"\n当前激活技能: {list(loader.active_skills.keys())}")
    
    # Demo 5: 多技能协同执行
    print("\n" + "-"*70)
    print("【Demo 5】多技能协同执行")
    print("-"*70)
    
    result = loader.execute_with_active_skills('300308')
    
    print("\n" + "="*70)
    print("✅ 技能反馈闭环与动态加载演示完成")
    print("="*70)
    print("\n核心成果:")
    print("  ✓ L1-L5 → KG 结果回写 (反馈闭环)")
    print("  ✓ 技能置信度动态计算 (自我进化)")
    print("  ✓ 市场环境识别 (智能加载)")
    print("  ✓ 技能热插拔 (运行时动态调整)")
    print("  ✓ 多技能加权综合 (协同决策)")


if __name__ == "__main__":
    demo()
