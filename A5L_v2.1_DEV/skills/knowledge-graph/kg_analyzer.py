"""
A5L Knowledge Graph - Deep Analysis Module
知识图谱深度分析模块 - 让A5L"进去思考"

Features:
- Entity-driven analysis (基于提取的实体触发A5L分析)
- Knowledge reasoning (结合已有图谱进行推理)
- Investment signal generation (生成投资信号)
- Thinking process archival (思考过程归档)
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_graph_core import KnowledgeGraph, Entity
from kg_integration import KGIntegration


class SignalType(Enum):
    """投资信号类型"""
    BULLISH = "看多"
    BEARISH = "看空"
    NEUTRAL = "中性"
    WATCH = "观望"
    HIGH_RISK = "高风险"


@dataclass
class InvestmentSignal:
    """投资信号"""
    entity_id: str
    entity_name: str
    signal_type: SignalType
    confidence: float  # 0-1
    reasoning: str
    related_entities: List[str]
    timestamp: str
    source_doc: str


@dataclass
class AnalysisResult:
    """分析结果"""
    entity_id: str
    entity_name: str
    analysis_type: str
    score: float
    findings: List[str]
    risks: List[str]
    opportunities: List[str]
    recommendation: str


class KGAnalyzer:
    """知识图谱分析器 - A5L深度思考入口"""
    
    def __init__(self, kg: KnowledgeGraph = None):
        self.kg = kg or KnowledgeGraph()
        self.integration = KGIntegration(self.kg)
    
    def analyze_document(self, doc_content: str, doc_id: str, doc_title: str) -> Dict:
        """
        完整分析流程：提取实体 → 构建关系 → A5L深度思考 → 生成洞察
        
        Returns:
            {
                'extraction': {...},      # 实体提取结果
                'thinking': {...},        # A5L思考过程
                'signals': [...],         # 投资信号
                'analysis': [...],        # 深度分析结果
                'recommendations': [...], # 操作建议
                'knowledge_added': {...}  # 新增知识
            }
        """
        print(f"\n{'='*60}")
        print(f"A5L 知识图谱深度分析")
        print(f"{'='*60}")
        print(f"文档: {doc_title}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Step 1: 提取实体和关系
        print("[Step 1] 提取实体和构建关系...")
        extraction_result = self.integration.process_feishu_document(
            doc_content, doc_id, doc_title
        )
        
        # Step 2: 获取提取的实体
        print("[Step 2] 加载提取的实体...")
        recent_entities = self._get_recent_entities(doc_id)
        
        # Step 3: A5L深度思考
        print("[Step 3] A5L开始深度思考...")
        thinking_result = self._a5l_thinking_process(recent_entities, doc_content)
        
        # Step 4: 生成投资信号
        print("[Step 4] 生成投资信号...")
        signals = self._generate_investment_signals(recent_entities, thinking_result)
        
        # Step 5: 深度分析
        print("[Step 5] 进行多维度分析...")
        analysis_results = self._multi_dimension_analysis(recent_entities)
        
        # Step 6: 整合已有知识进行推理
        print("[Step 6] 结合已有知识图谱推理...")
        reasoning_result = self._knowledge_reasoning(recent_entities)
        
        # Step 7: 生成操作建议
        print("[Step 7] 生成操作建议...")
        recommendations = self._generate_recommendations(
            signals, analysis_results, reasoning_result
        )
        
        # Step 8: 将思考结果存入知识图谱
        print("[Step 8] 归档思考结果...")
        knowledge_added = self._archive_thinking(
            doc_id, doc_title, thinking_result, signals, analysis_results
        )
        
        # 整合输出
        result = {
            'extraction': extraction_result,
            'thinking': thinking_result,
            'signals': [self._signal_to_dict(s) for s in signals],
            'analysis': [self._analysis_to_dict(a) for a in analysis_results],
            'reasoning': reasoning_result,
            'recommendations': recommendations,
            'knowledge_added': knowledge_added,
            'timestamp': datetime.now().isoformat()
        }
        
        # 打印总结
        self._print_summary(result)
        
        return result
    
    def _get_recent_entities(self, doc_id: str) -> List[Entity]:
        """获取最近添加的实体"""
        # 从知识图谱中获取与当前文档相关的实体
        all_entities = []
        for entity in self.kg.get_entities_by_type('Stock'):
            if doc_id in str(entity.properties.get('source', '')):
                all_entities.append(entity)
        for entity in self.kg.get_entities_by_type('Company'):
            if doc_id in str(entity.properties.get('source', '')):
                all_entities.append(entity)
        return all_entities
    
    def _a5l_thinking_process(self, entities: List[Entity], doc_content: str) -> Dict:
        """
        A5L深度思考过程
        模拟A5L的思考流程：观察 → 分析 → 推理 → 判断
        """
        thinking = {
            'observation': [],      # 观察到的信息
            'analysis': [],         # 分析过程
            'reasoning': [],        # 推理过程
            'judgment': [],         # 判断结论
            'confidence': 0.0       # 整体置信度
        }
        
        # 观察阶段：识别关键实体和事件
        for entity in entities:
            if entity.type == 'Stock':
                thinking['observation'].append(f"发现股票: {entity.name} ({entity.code})")
                # 检查是否有特殊标记（如"受益者"、"风险"等）
                if '受益' in str(entity.properties) or 'benefit' in str(entity.properties):
                    thinking['observation'].append(f"  → {entity.name} 被标记为潜在受益者")
                if '风险' in str(entity.properties) or 'risk' in str(entity.properties):
                    thinking['observation'].append(f"  → {entity.name} 存在风险信号")
            
            elif entity.type == 'Company':
                thinking['observation'].append(f"发现公司: {entity.name}")
                if '估值' in str(entity.properties):
                    thinking['observation'].append(f"  → 估值信息: {entity.properties.get('估值', 'N/A')}")
            
            elif entity.type == 'Concept':
                thinking['observation'].append(f"发现概念: {entity.name}")
        
        # 分析阶段：产业链、竞争、政策等维度
        thinking['analysis'].append("【产业链分析】")
        for entity in entities:
            if entity.type in ['Stock', 'Company']:
                # 查询产业链位置
                chain = self.kg.get_industry_chain(entity.id)
                if chain['upstream'] or chain['downstream']:
                    thinking['analysis'].append(f"  {entity.name}: 产业链位置已识别")
                
                # 查询竞争关系
                related = self.kg.get_related_entities(entity.id, depth=1)
                competitors = [r for r in related if r.get('relation_type') == 'competes_with']
                if competitors:
                    thinking['analysis'].append(f"  {entity.name}: 竞争对手 {len(competitors)} 个")
        
        thinking['analysis'].append("【政策影响分析】")
        if '监管' in doc_content or '政策' in doc_content or 'regulator' in doc_content.lower():
            thinking['analysis'].append("  检测到政策/监管相关内容")
            thinking['analysis'].append("  → 评估政策风险对公司架构、融资、IPO的影响")
        
        if 'IPO' in doc_content or '上市' in doc_content:
            thinking['analysis'].append("  检测到IPO相关内容")
            thinking['analysis'].append("  → 评估上市进程、估值、时间窗口")
        
        thinking['analysis'].append("【竞争格局分析】")
        # 识别竞争关系
        for entity in entities:
            related = self.kg.get_related_entities(entity.id, depth=2)
            competitors = [r for r in related if r.get('relation_type') == 'competes_with']
            if competitors:
                comp_names = [r['entity_name'] for r in competitors]
                thinking['analysis'].append(f"  {entity.name} vs {', '.join(comp_names)}")
        
        # 推理阶段：基于已有知识推理
        thinking['reasoning'].append("【关联推理】")
        for entity in entities:
            # 查找已有知识中的相似案例
            similar = self._find_similar_cases(entity)
            if similar:
                thinking['reasoning'].append(f"  {entity.name}: 发现 {len(similar)} 个相似历史案例")
        
        thinking['reasoning'].append("【趋势推理】")
        # 基于概念热度推理
        concepts = [e for e in entities if e.type == 'Concept']
        if concepts:
            thinking['reasoning'].append(f"  涉及概念: {', '.join([c.name for c in concepts])}")
            thinking['reasoning'].append("  → 评估概念持续性和市场关注度")
        
        # 判断阶段：形成投资判断
        thinking['judgment'].append("【投资判断】")
        for entity in entities:
            if entity.type == 'Stock':
                judgment = self._form_judgment(entity, doc_content)
                thinking['judgment'].append(f"  {entity.name}: {judgment}")
        
        # 计算整体置信度
        thinking['confidence'] = self._calculate_confidence(thinking)
        
        return thinking
    
    def _find_similar_cases(self, entity: Entity) -> List[Dict]:
        """查找相似历史案例"""
        similar = []
        # 基于实体类型和行业查找相似案例
        if entity.type == 'Company':
            # 查找同行业的其他公司
            all_entities = self.kg.get_entities_by_type('Company')
            for e in all_entities:
                if e.id != entity.id:
                    # 简单的相似度判断
                    if entity.properties.get('industry') == e.properties.get('industry'):
                        similar.append({
                            'entity_id': e.id,
                            'entity_name': e.name,
                            'reason': '同行业'
                        })
        return similar[:3]  # 返回最相似的3个
    
    def _form_judgment(self, entity: Entity, doc_content: str) -> str:
        """形成对单个实体的投资判断"""
        # 基于文档内容和实体属性形成判断
        judgment = ""
        
        # 检查风险信号
        if any(word in doc_content for word in ['风险', 'risk', '担忧', 'concern', '困难', 'difficult']):
            if entity.name in doc_content:
                judgment += "存在风险信号; "
        
        # 检查利好信号
        if any(word in doc_content for word in ['受益', 'benefit', '利好', 'positive', '增长', 'growth']):
            if entity.name in doc_content:
                judgment += "存在利好信号; "
        
        # 检查估值
        if '估值' in str(entity.properties) or 'valuation' in str(entity.properties):
            judgment += "需关注估值合理性; "
        
        if not judgment:
            judgment = "需进一步观察"
        
        return judgment
    
    def _calculate_confidence(self, thinking: Dict) -> float:
        """计算整体置信度"""
        # 基于观察、分析、推理的完整性计算置信度
        score = 0.0
        if thinking['observation']:
            score += 0.3
        if thinking['analysis']:
            score += 0.3
        if thinking['reasoning']:
            score += 0.2
        if thinking['judgment']:
            score += 0.2
        return min(score, 1.0)
    
    def _generate_investment_signals(self, entities: List[Entity], thinking: Dict) -> List[InvestmentSignal]:
        """生成投资信号"""
        signals = []
        
        for entity in entities:
            if entity.type != 'Stock':
                continue
            
            # 基于思考过程生成信号
            signal_type = SignalType.NEUTRAL
            confidence = 0.5
            reasoning = ""
            
            # 分析思考过程中的判断
            for judgment in thinking['judgment']:
                if entity.name in judgment:
                    if '利好' in judgment or '受益' in judgment:
                        signal_type = SignalType.BULLISH
                        confidence = 0.7
                        reasoning = "文档中存在利好/受益描述"
                    elif '风险' in judgment or '困难' in judgment:
                        signal_type = SignalType.BEARISH
                        confidence = 0.6
                        reasoning = "文档中存在风险/困难描述"
                    elif '观察' in judgment:
                        signal_type = SignalType.WATCH
                        confidence = 0.5
                        reasoning = "需持续观察"
            
            # 获取相关实体
            related = self.kg.get_related_entities(entity.id, depth=1)
            related_ids = [r['entity_id'] for r in related]
            
            signal = InvestmentSignal(
                entity_id=entity.id,
                entity_name=entity.name,
                signal_type=signal_type,
                confidence=confidence,
                reasoning=reasoning,
                related_entities=related_ids,
                timestamp=datetime.now().isoformat(),
                source_doc=thinking.get('source_doc', 'unknown')
            )
            signals.append(signal)
        
        return signals
    
    def _multi_dimension_analysis(self, entities: List[Entity]) -> List[AnalysisResult]:
        """多维度分析 - UZI风格"""
        results = []
        
        for entity in entities:
            if entity.type not in ['Stock', 'Company']:
                continue
            
            findings = []
            risks = []
            opportunities = []
            
            # UZI维度1: 产业链位置
            chain = self.kg.get_industry_chain(entity.id)
            if chain['upstream'] or chain['downstream']:
                findings.append(f"产业链位置: 上游{len(chain['upstream'])}个, 下游{len(chain['downstream'])}个")
                if len(chain['upstream']) > 3:
                    opportunities.append("上游供应商多元化，供应链稳定")
            
            # UZI维度2: 竞争格局
            related = self.kg.get_related_entities(entity.id, depth=1)
            competitors = [r for r in related if r.get('relation_type') == 'competes_with']
            if competitors:
                findings.append(f"竞争对手: {len(competitors)}个")
                if len(competitors) > 5:
                    risks.append("竞争激烈")
                elif len(competitors) < 2:
                    opportunities.append("竞争格局良好")
            
            # UZI维度3: 概念关联
            concepts = [r for r in related if r.get('entity_type') == 'Concept']
            if concepts:
                concept_names = [c['entity_name'] for c in concepts]
                findings.append(f"关联概念: {', '.join(concept_names)}")
                if len(concepts) >= 2:
                    opportunities.append("多概念叠加，想象空间大")
            
            # UZI维度4: 政策环境
            if '政策' in str(entity.properties) or '监管' in str(entity.properties):
                risks.append("政策/监管风险需关注")
            
            # 综合评分
            score = self._calculate_uzi_score(findings, risks, opportunities)
            
            # 生成建议
            if score >= 70:
                recommendation = "值得关注"
            elif score >= 50:
                recommendation = "可纳入观察名单"
            else:
                recommendation = "暂不建议关注"
            
            result = AnalysisResult(
                entity_id=entity.id,
                entity_name=entity.name,
                analysis_type='UZI_Multi_Dimension',
                score=score,
                findings=findings,
                risks=risks,
                opportunities=opportunities,
                recommendation=recommendation
            )
            results.append(result)
        
        return results
    
    def _calculate_uzi_score(self, findings: List[str], risks: List[str], opportunities: List[str]) -> float:
        """计算UZI风格综合评分"""
        base_score = 50.0
        base_score += len(findings) * 5
        base_score += len(opportunities) * 10
        base_score -= len(risks) * 8
        return max(0, min(100, base_score))
    
    def _knowledge_reasoning(self, entities: List[Entity]) -> Dict:
        """基于已有知识的推理"""
        reasoning = {
            'hidden_relations': [],    # 隐藏关系
            'trend_prediction': [],    # 趋势预测
            'risk_warnings': [],       # 风险预警
            'opportunity_alerts': []   # 机会提示
        }
        
        for entity in entities:
            # 查找隐藏关系（通过中间节点）
            paths = self.kg.find_path(entity.id, "industry_半导体", max_depth=3)
            if paths and len(paths) > 0:
                reasoning['hidden_relations'].append({
                    'from': entity.name,
                    'to': '半导体',
                    'path_length': len(paths[0]),
                    'insight': f"{entity.name}与半导体行业存在{len(paths[0])}跳关联"
                })
            
            # 检查是否涉及热门概念
            related = self.kg.get_related_entities(entity.id, depth=2)
            ai_related = [r for r in related if 'AI' in r.get('entity_name', '') or '人工智能' in r.get('entity_name', '')]
            if ai_related:
                reasoning['opportunity_alerts'].append(f"{entity.name}与AI概念关联，可能受益于AI浪潮")
        
        return reasoning
    
    def _generate_recommendations(self, signals: List[InvestmentSignal], 
                                   analysis: List[AnalysisResult],
                                   reasoning: Dict) -> List[Dict]:
        """生成综合操作建议"""
        recommendations = []
        
        # 基于信号生成建议
        for signal in signals:
            if signal.signal_type == SignalType.BULLISH:
                recommendations.append({
                    'type': '关注',
                    'entity': signal.entity_name,
                    'action': '纳入观察名单',
                    'reason': signal.reasoning,
                    'confidence': signal.confidence
                })
            elif signal.signal_type == SignalType.BEARISH:
                recommendations.append({
                    'type': '警惕',
                    'entity': signal.entity_name,
                    'action': '关注风险，谨慎对待',
                    'reason': signal.reasoning,
                    'confidence': signal.confidence
                })
        
        # 基于推理生成建议
        for alert in reasoning.get('opportunity_alerts', []):
            recommendations.append({
                'type': '机会',
                'alert': alert,
                'action': '深入研究关联逻辑'
            })
        
        for warning in reasoning.get('risk_warnings', []):
            recommendations.append({
                'type': '风险',
                'warning': warning,
                'action': '设置风险监控'
            })
        
        return recommendations
    
    def _archive_thinking(self, doc_id: str, doc_title: str, 
                          thinking: Dict, signals: List[InvestmentSignal],
                          analysis: List[AnalysisResult]) -> Dict:
        """将思考结果归档到知识图谱"""
        archived = {
            'thinking_node': None,
            'signal_nodes': [],
            'analysis_nodes': []
        }
        
        # 创建思考节点
        from knowledge_graph_core import Entity
        thinking_entity = Entity(
            id=f"thinking_{doc_id}",
            type="Analysis",
            name=f"A5L分析_{doc_title}",
            properties={
                'doc_id': doc_id,
                'thinking_process': json.dumps(thinking, ensure_ascii=False),
                'confidence': thinking.get('confidence', 0),
                'timestamp': datetime.now().isoformat(),
                'analyst': 'A5L_KGAnalyzer'
            }
        )
        self.kg.add_entity(thinking_entity)
        archived['thinking_node'] = thinking_entity.id
        
        # 创建信号节点
        for signal in signals:
            signal_entity = Entity(
                id=f"signal_{signal.entity_id}_{datetime.now().strftime('%Y%m%d')}",
                type="Signal",
                name=f"{signal.entity_name}_{signal.signal_type.value}",
                properties={
                    'target_entity': signal.entity_id,
                    'signal_type': signal.signal_type.value,
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning,
                    'timestamp': signal.timestamp
                }
            )
            self.kg.add_entity(signal_entity)
            archived['signal_nodes'].append(signal_entity.id)
            
            # 添加从思考到信号的关联
            from knowledge_graph_core import Relation
            relation = Relation(
                id=f"{thinking_entity.id}_generates_{signal_entity.id}",
                source_id=thinking_entity.id,
                target_id=signal_entity.id,
                type="generates"
            )
            self.kg.add_relation(relation)
        
        return archived
    
    def _signal_to_dict(self, signal: InvestmentSignal) -> Dict:
        """转换信号为字典"""
        return {
            'entity_id': signal.entity_id,
            'entity_name': signal.entity_name,
            'signal_type': signal.signal_type.value,
            'confidence': signal.confidence,
            'reasoning': signal.reasoning,
            'related_entities': signal.related_entities,
            'timestamp': signal.timestamp
        }
    
    def _analysis_to_dict(self, analysis: AnalysisResult) -> Dict:
        """转换分析结果为字典"""
        return {
            'entity_id': analysis.entity_id,
            'entity_name': analysis.entity_name,
            'analysis_type': analysis.analysis_type,
            'score': analysis.score,
            'findings': analysis.findings,
            'risks': analysis.risks,
            'opportunities': analysis.opportunities,
            'recommendation': analysis.recommendation
        }
    
    def _print_summary(self, result: Dict):
        """打印分析总结"""
        print(f"\n{'='*60}")
        print("分析完成总结")
        print(f"{'='*60}")
        print(f"提取实体: {result['extraction'].get('entities_added', 0)} 个")
        print(f"构建关系: {result['extraction'].get('relations_added', 0)} 个")
        print(f"投资信号: {len(result['signals'])} 个")
        print(f"深度分析: {len(result['analysis'])} 个")
        print(f"操作建议: {len(result['recommendations'])} 条")
        print(f"思考置信度: {result['thinking'].get('confidence', 0):.2f}")
        print(f"{'='*60}\n")
        
        # 打印投资信号
        if result['signals']:
            print("📊 投资信号:")
            for signal in result['signals']:
                emoji = "🟢" if signal['signal_type'] == "看多" else "🔴" if signal['signal_type'] == "看空" else "🟡"
                print(f"  {emoji} {signal['entity_name']}: {signal['signal_type']} (置信度: {signal['confidence']:.0%})")
        
        # 打印操作建议
        if result['recommendations']:
            print("\n💡 操作建议:")
            for rec in result['recommendations'][:5]:
                print(f"  • {rec.get('entity', rec.get('alert', 'N/A'))}: {rec['action']}")


def main():
    """测试A5L深度分析"""
    # 测试用的研报内容
    test_doc = """
    NVIDIA (NVDA)是AI算力龙头，受益于数据中心需求增长。
    与AMD竞争激烈，在GPU市场占据主导地位。
    半导体行业包括芯片设计、晶圆代工等环节。
    台积电(TSM)是NVDA的主要供应商。
    """
    
    analyzer = KGAnalyzer()
    result = analyzer.analyze_document(
        doc_content=test_doc,
        doc_id="test_analysis_001",
        doc_title="半导体行业测试分析"
    )
    
    # 保存结果
    output_path = f"analysis_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析结果已保存: {output_path}")


if __name__ == "__main__":
    main()
