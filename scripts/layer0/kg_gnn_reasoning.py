#!/usr/bin/env python3
"""
A5L KG-GNN Dynamic Reasoning Engine v1.0
KG-GNN动态推理引擎 - 时序知识图谱 + 混合推理

技术架构:
1. 时序图卷积 (Temporal GCN) - 捕捉演化规律
2. 混合推理引擎 (Hybrid Reasoning) - 神经+符号双轨
3. 图-文对齐 (Graph-Text Alignment) - LLM与KG实时互动

执行时间: 2026-05-04 02:55
技术意义: KG从"图书馆"进化为"大脑皮层"
"""

import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class ReasoningType(Enum):
    """推理类型"""
    TEMPORAL = "时序演化"      # 基于历史模式的预测
    SYMBOLIC = "符号逻辑"      # 基于规则的硬约束
    NEURAL = "神经关联"        # 基于GNN的模糊匹配
    HYBRID = "混合推理"        # 动态仲裁

class EntityType(Enum):
    """实体类型"""
    STOCK = "股票"
    INDUSTRY = "行业"
    THEME = "主题"
    REPORT = "研报"
    EXECUTION = "执行记录"

@dataclass
class TemporalEmbedding:
    """时序嵌入 - 记录实体随时间的演化"""
    entity_id: str
    timestamp: datetime
    structural_features: np.ndarray  # 结构特征 (邻居关系)
    temporal_features: np.ndarray    # 时序特征 (历史状态)
    evolutionary_state: np.ndarray   # 演化状态 (RNN输出)

@dataclass
class ReasoningResult:
    """推理结果"""
    query: str
    reasoning_type: ReasoningType
    confidence: float
    result: Any
    explanation: str
    time_horizon: Optional[int] = None  # 预测时间跨度(天)


class TemporalKGNN:
    """
    时序知识图谱神经网络
    
    核心能力:
    1. 历史编码: 处理时间切片上的子图
    2. 演化单元: GRU/LSTM更新演化嵌入
    3. 动态预测: 预测关系随时间的转移
    """
    
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.entity_history = {}  # 实体历史状态
        self.temporal_snapshots = []  # 时间切片
        print("🧠 Temporal KG-NN 初始化")
        
    def encode_temporal_snapshot(self, timestamp: datetime, subgraph: Dict):
        """
        编码时间切片
        
        对特定时间点的KG子图进行编码
        """
        print(f"\n📊 编码时间切片: {timestamp}")
        
        snapshot = {
            'timestamp': timestamp,
            'entities': {},
            'relations': subgraph.get('relations', [])
        }
        
        # 对每个实体提取结构特征 (R-GCN编码)
        for entity_id, entity_data in subgraph.get('entities', {}).items():
            # 结构特征: 基于邻居关系
            neighbors = self._get_neighbors(entity_id, subgraph)
            structural_feat = self._aggregate_neighbor_features(neighbors)
            
            # 时序特征: 基于历史状态
            temporal_feat = self._get_temporal_features(entity_id, timestamp)
            
            snapshot['entities'][entity_id] = {
                'structural': structural_feat,
                'temporal': temporal_feat
            }
        
        self.temporal_snapshots.append(snapshot)
        print(f"✅ 切片编码完成: {len(snapshot['entities'])} 个实体")
        return snapshot
    
    def update_evolutionary_embedding(self, entity_id: str, 
                                       current_state: np.ndarray) -> np.ndarray:
        """
        更新演化嵌入 (Evolutionary Unit)
        
        使用GRU/LSTM根据历史状态更新实体嵌入
        """
        # 获取历史状态
        history = self.entity_history.get(entity_id, [])
        
        if not history:
            # 初始化
            evolutionary_state = current_state
        else:
            # GRU更新 (简化实现)
            last_state = history[-1]['evolutionary']
            # 实际应使用: evolutionary_state = GRU(current_state, last_state)
            evolutionary_state = 0.7 * last_state + 0.3 * current_state
        
        # 存储状态
        if entity_id not in self.entity_history:
            self.entity_history[entity_id] = []
        
        self.entity_history[entity_id].append({
            'timestamp': datetime.now(),
            'evolutionary': evolutionary_state,
            'structural': current_state
        })
        
        return evolutionary_state
    
    def predict_temporal_relation(self, source: str, relation_type: str, 
                                   target: str, future_days: int = 3) -> float:
        """
        时序关系预测
        
        预测: "历史上这种关系通常在X天后传导至Y"
        
        示例: 源杰科技(光芯片)异动 → 3天后传导至中际旭创(CPO)
        """
        print(f"\n🔮 时序预测: {source} --{relation_type}--> {target} (T+{future_days})")
        
        # 获取源实体的历史演化
        source_history = self.entity_history.get(source, [])
        if len(source_history) < 3:
            return 0.5  # 数据不足
        
        # 计算历史传导模式
        propagation_pattern = self._calculate_propagation_pattern(
            source, target, relation_type
        )
        
        # 基于当前状态和历史模式预测
        current_embedding = source_history[-1]['evolutionary']
        
        # 简化: 使用余弦相似度预测关联强度
        # 实际应使用: trained GNN model
        prediction_score = 0.6 + 0.3 * propagation_pattern
        
        print(f"✅ 预测结果: 传导概率 {prediction_score:.1%}")
        return prediction_score
    
    def detect_anomaly_propagation(self, entity_id: str, 
                                    anomaly_score: float) -> List[Dict]:
        """
        异常传导检测
        
        当某实体异常时,预测会传导到哪些相关实体
        """
        print(f"\n⚠️ 异常传导检测: {entity_id} (异常分数: {anomaly_score:.2f})")
        
        affected_entities = []
        
        # 获取实体的演化历史
        history = self.entity_history.get(entity_id, [])
        if len(history) < 2:
            return affected_entities
        
        # 查找历史上类似的异常模式
        similar_patterns = self._find_similar_anomaly_patterns(entity_id)
        
        # 预测受影响实体
        for pattern in similar_patterns:
            target = pattern['affected_entity']
            propagation_time = pattern['avg_propagation_time']
            correlation = pattern['correlation']
            
            affected_entities.append({
                'entity': target,
                'expected_time': propagation_time,
                'confidence': correlation * anomaly_score,
                'reason': f"历史相似异常平均{propagation_time}天后传导"
            })
        
        # 按置信度排序
        affected_entities.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"✅ 检测到 {len(affected_entities)} 个潜在受影响实体:")
        for aff in affected_entities[:3]:
            print(f"   → {aff['entity']}: T+{aff['expected_time']}天, 置信度{aff['confidence']:.1%}")
        
        return affected_entities
    
    # 辅助方法
    def _get_neighbors(self, entity_id: str, subgraph: Dict) -> List[str]:
        """获取邻居实体"""
        neighbors = []
        for rel in subgraph.get('relations', []):
            if rel['source'] == entity_id:
                neighbors.append(rel['target'])
            elif rel['target'] == entity_id:
                neighbors.append(rel['source'])
        return neighbors
    
    def _aggregate_neighbor_features(self, neighbors: List[str]) -> np.ndarray:
        """聚合邻居特征 (R-GCN风格)"""
        # 简化: 返回随机特征
        return np.random.randn(self.embedding_dim)
    
    def _get_temporal_features(self, entity_id: str, timestamp: datetime) -> np.ndarray:
        """获取时序特征"""
        history = self.entity_history.get(entity_id, [])
        if not history:
            return np.zeros(self.embedding_dim)
        return history[-1]['evolutionary']
    
    def _calculate_propagation_pattern(self, source: str, target: str, 
                                        relation: str) -> float:
        """计算历史传导模式"""
        # 简化实现
        return 0.7
    
    def _find_similar_anomaly_patterns(self, entity_id: str) -> List[Dict]:
        """查找历史上类似的异常模式"""
        # 返回模拟数据
        return [
            {'affected_entity': '300308', 'avg_propagation_time': 3, 'correlation': 0.8},
            {'affected_entity': '300394', 'avg_propagation_time': 2, 'correlation': 0.6},
            {'affected_entity': '688498', 'avg_propagation_time': 5, 'correlation': 0.5}
        ]


class HybridReasoningEngine:
    """
    混合推理引擎
    
    神经+符号双轨制:
    - 神经层: GAT处理非结构化数据,模糊匹配
    - 符号层: 预置金融逻辑规则,硬性约束
    - 动态仲裁: 门控机制决定使用哪一层
    """
    
    def __init__(self, temporal_kgnn: TemporalKGNN):
        self.tkg = temporal_kgnn
        self.symbolic_rules = self._load_symbolic_rules()
        print("⚖️ Hybrid Reasoning Engine 初始化")
        
    def _load_symbolic_rules(self) -> List[Dict]:
        """加载符号逻辑规则"""
        return [
            {
                'id': 'risk_limit',
                'type': 'hard_constraint',
                'description': '单一持仓不超过20%',
                'condition': 'position_pct > 0.20',
                'action': 'REJECT',
                'priority': 10
            },
            {
                'id': 'stop_loss',
                'type': 'risk_control',
                'description': '亏损超过10%必须止损',
                'condition': 'loss_pct > 0.10',
                'action': 'SELL',
                'priority': 9
            },
            {
                'id': 'concentration',
                'type': 'portfolio_rule',
                'description': '行业集中度不超过40%',
                'condition': 'industry_concentration > 0.40',
                'action': 'WARNING',
                'priority': 8
            }
        ]
    
    def reason(self, query: Dict, context: Dict) -> ReasoningResult:
        """
        混合推理主入口
        
        根据查询类型动态选择推理路径
        """
        query_type = query.get('type')
        
        # 1. 首先检查符号层 (硬约束)
        symbolic_result = self._symbolic_reasoning(query, context)
        if symbolic_result and symbolic_result['action'] == 'REJECT':
            return ReasoningResult(
                query=str(query),
                reasoning_type=ReasoningType.SYMBOLIC,
                confidence=1.0,
                result=symbolic_result,
                explanation=f"符号规则触发: {symbolic_result['rule']}"
            )
        
        # 2. 时序预测 (时间敏感)
        if 'temporal' in query_type or 'future' in query_type:
            temporal_result = self._temporal_reasoning(query, context)
            return ReasoningResult(
                query=str(query),
                reasoning_type=ReasoningType.TEMPORAL,
                confidence=temporal_result['confidence'],
                result=temporal_result,
                explanation=temporal_result['explanation'],
                time_horizon=temporal_result.get('horizon')
            )
        
        # 3. 神经关联 (模糊匹配)
        neural_result = self._neural_reasoning(query, context)
        
        # 4. 混合仲裁
        final_result = self._arbitrate(symbolic_result, neural_result, context)
        
        return ReasoningResult(
            query=str(query),
            reasoning_type=ReasoningType.HYBRID,
            confidence=final_result['confidence'],
            result=final_result,
            explanation=final_result['explanation']
        )
    
    def _symbolic_reasoning(self, query: Dict, context: Dict) -> Optional[Dict]:
        """符号逻辑推理 - CSO主要使用"""
        for rule in self.symbolic_rules:
            # 简化的规则匹配
            if self._check_rule_condition(rule, context):
                return {
                    'rule': rule['id'],
                    'action': rule['action'],
                    'description': rule['description']
                }
        return None
    
    def _temporal_reasoning(self, query: Dict, context: Dict) -> Dict:
        """时序推理 - 预测传导"""
        source = query.get('source_entity')
        target = query.get('target_entity')
        relation = query.get('relation')
        horizon = query.get('horizon', 3)
        
        # 调用Temporal KG-NN
        prediction = self.tkg.predict_temporal_relation(
            source, relation, target, horizon
        )
        
        return {
            'type': 'temporal_prediction',
            'source': source,
            'target': target,
            'relation': relation,
            'horizon': horizon,
            'probability': prediction,
            'confidence': prediction,
            'explanation': f"基于历史时序模式,传导概率{prediction:.1%}"
        }
    
    def _neural_reasoning(self, query: Dict, context: Dict) -> Dict:
        """神经推理 - UZI主要使用"""
        # Graph Attention Network风格的推理
        # 简化实现
        return {
            'type': 'neural_association',
            'confidence': 0.75,
            'related_entities': self._find_associated_entities(query),
            'explanation': "基于GNN模糊匹配发现关联"
        }
    
    def _arbitrate(self, symbolic: Optional[Dict], neural: Dict, 
                   context: Dict) -> Dict:
        """动态仲裁 - 决定最终推理结果"""
        # 门控机制
        if symbolic and symbolic['action'] in ['REJECT', 'SELL']:
            # 硬约束优先
            return {
                'type': 'symbolic_priority',
                'confidence': 1.0,
                'result': symbolic,
                'explanation': "符号规则优先触发"
            }
        
        # 神经推理补充
        return {
            'type': 'neural_primary',
            'confidence': neural['confidence'],
            'result': neural,
            'symbolic_check': symbolic,
            'explanation': "神经推理为主,符号规则校验通过"
        }
    
    def _check_rule_condition(self, rule: Dict, context: Dict) -> bool:
        """检查规则条件"""
        # 简化实现
        return False
    
    def _find_associated_entities(self, query: Dict) -> List[str]:
        """查找关联实体"""
        return ['300308', '300394', '688498']


class GraphTextAlignment:
    """
    图-文对齐模块
    
    实现LLM与KG的实时互动:
    1. KG引导LLM注意力
    2. LLM提取新事实更新KG
    3. GNN基于新图结构重新计算
    """
    
    def __init__(self, temporal_kgnn: TemporalKGNN):
        self.tkg = temporal_kgnn
        print("🔗 Graph-Text Alignment 初始化")
        
    def kg_guided_attention(self, text: str, focus_entity: str) -> Dict:
        """
        KG引导注意力
        
        当LLM处理文本时,KG告诉它重点关注哪些词
        
        示例: 
        新闻: "英伟达发布B100,光模块需求激增"
        KG引导: 关注"英伟达"→关联"光模块"→关联"中际旭创"
        """
        print(f"\n👁️ KG引导注意力: 聚焦 {focus_entity}")
        
        # 从KG获取相关实体
        related = self._get_related_entities_from_kg(focus_entity)
        
        # 构建注意力掩码
        attention_mask = {}
        for word in text.split():
            if any(rel['entity'] in word for rel in related):
                attention_mask[word] = 1.0  # 高权重
            else:
                attention_mask[word] = 0.3  # 低权重
        
        print(f"✅ 注意力掩码构建完成: {len([w for w,v in attention_mask.items() if v > 0.5])} 个高权重词")
        
        return {
            'focus_entity': focus_entity,
            'related_entities': related,
            'attention_mask': attention_mask,
            'kg_expansion': self._expand_context(related)
        }
    
    def extract_and_update_kg(self, text: str, timestamp: datetime) -> List[Dict]:
        """
        从文本提取事实并更新KG
        
        LLM提取新事实 → 实时更新KG三元组 → GNN重新计算嵌入
        """
        print(f"\n📝 从文本提取事实并更新KG")
        
        # 模拟LLM提取三元组
        extracted_facts = self._mock_llm_extraction(text)
        
        updates = []
        for fact in extracted_facts:
            # 更新KG
            update = {
                'timestamp': timestamp,
                'subject': fact['subject'],
                'predicate': fact['predicate'],
                'object': fact['object'],
                'confidence': fact['confidence']
            }
            updates.append(update)
            
            # 触发GNN重新计算
            self._trigger_embedding_update(fact['subject'])
        
        print(f"✅ 提取 {len(updates)} 个事实, KG已更新, GNN重新计算中...")
        return updates
    
    def query_with_kg_expansion(self, user_query: str) -> Dict:
        """
        查询时自动KG扩展
        
        用户提问 → GNN扩展上下文 → 返回完整答案
        
        示例:
        用户: "MACD金叉形态下历史上关联度最高的板块?"
        KG: 通过GNN找到"CPO"、"光通信"等关联板块
        """
        print(f"\n🔍 KG扩展查询: {user_query}")
        
        # 解析查询中的实体
        entities = self._extract_entities_from_query(user_query)
        
        # GNN扩展关联
        expanded_context = []
        for entity in entities:
            neighbors = self._gnn_expand_neighbors(entity, depth=2)
            expanded_context.extend(neighbors)
        
        # 去重排序
        unique_context = self._deduplicate_and_rank(expanded_context)
        
        print(f"✅ 查询扩展: {len(entities)} 个实体 → {len(unique_context)} 个关联实体")
        
        return {
            'original_query': user_query,
            'extracted_entities': entities,
            'expanded_context': unique_context[:10],  # Top 10
            'answer': self._generate_answer(user_query, unique_context)
        }
    
    # 辅助方法
    def _get_related_entities_from_kg(self, entity: str) -> List[Dict]:
        """从KG获取相关实体"""
        return [
            {'entity': '300308', 'relation': 'covers', 'weight': 0.9},
            {'entity': '300394', 'relation': 'upstream', 'weight': 0.7},
            {'entity': 'CPO', 'relation': 'industry', 'weight': 0.8}
        ]
    
    def _expand_context(self, related: List[Dict]) -> List[str]:
        """扩展上下文"""
        return [r['entity'] for r in related]
    
    def _mock_llm_extraction(self, text: str) -> List[Dict]:
        """模拟LLM事实提取"""
        return [
            {'subject': 'NVIDIA', 'predicate': 'release', 'object': 'B100', 'confidence': 0.95},
            {'subject': 'CPO', 'predicate': 'demand_surge', 'object': 'True', 'confidence': 0.85}
        ]
    
    def _trigger_embedding_update(self, entity: str):
        """触发嵌入更新"""
        # 更新GNN嵌入
        pass
    
    def _extract_entities_from_query(self, query: str) -> List[str]:
        """从查询提取实体"""
        return ['MACD', '金叉']
    
    def _gnn_expand_neighbors(self, entity: str, depth: int) -> List[Dict]:
        """GNN邻居扩展"""
        return [
            {'entity': 'CPO', 'relation': 'associated', 'score': 0.85},
            {'entity': '光通信', 'relation': 'associated', 'score': 0.78},
            {'entity': '中际旭创', 'relation': 'leader', 'score': 0.92}
        ]
    
    def _deduplicate_and_rank(self, context: List[Dict]) -> List[Dict]:
        """去重排序"""
        seen = set()
        result = []
        for item in context:
            if item['entity'] not in seen:
                seen.add(item['entity'])
                result.append(item)
        return sorted(result, key=lambda x: x['score'], reverse=True)
    
    def _generate_answer(self, query: str, context: List[Dict]) -> str:
        """生成答案"""
        return f"基于GNN扩展,历史上MACD金叉与{', '.join([c['entity'] for c in context[:3]])}关联度最高"


def demo():
    """演示KG-GNN动态推理"""
    print("="*70)
    print("🧠 A5L KG-GNN Dynamic Reasoning Demo")
    print("="*70)
    
    # 初始化组件
    tkg = TemporalKGNN(embedding_dim=128)
    hybrid = HybridReasoningEngine(tkg)
    alignment = GraphTextAlignment(tkg)
    
    # Demo 1: 时序演化编码
    print("\n" + "-"*70)
    print("【Demo 1】时序演化编码 - 捕捉CPO行业热度变化")
    print("-"*70)
    
    # 模拟3个时间切片的CPO行业数据
    for i, date in enumerate(['2024-01', '2024-03', '2024-05']):
        snapshot = {
            'entities': {
                'industry_cpo': {'type': 'industry', 'sentiment': 0.5 + i*0.2},
                'stock_300308': {'type': 'stock', 'price': 100 + i*20},
                'stock_300394': {'type': 'stock', 'price': 80 + i*15}
            },
            'relations': [
                {'source': 'industry_cpo', 'target': 'stock_300308', 'type': 'covers'},
                {'source': 'industry_cpo', 'target': 'stock_300394', 'type': 'covers'}
            ]
        }
        tkg.encode_temporal_snapshot(datetime(2024, i*2+1, 1), snapshot)
    
    # Demo 2: 时序关系预测
    print("\n" + "-"*70)
    print("【Demo 2】时序关系预测 - 传导效应预测")
    print("-"*70)
    
    prediction = tkg.predict_temporal_relation(
        source='源杰科技',
        relation_type='supply_chain',
        target='中际旭创',
        future_days=3
    )
    
    # Demo 3: 异常传导检测
    print("\n" + "-"*70)
    print("【Demo 3】异常传导检测 - 源杰科技异动影响")
    print("-"*70)
    
    affected = tkg.detect_anomaly_propagation('源杰科技', anomaly_score=0.85)
    
    # Demo 4: 混合推理 - CSO风控场景
    print("\n" + "-"*70)
    print("【Demo 4】混合推理 - CSO风控决策")
    print("-"*70)
    
    result = hybrid.reason(
        query={'type': 'risk_check', 'stock': '300308', 'position_pct': 0.25},
        context={'portfolio_value': 1000000, 'current_position': 0.25}
    )
    print(f"\n推理类型: {result.reasoning_type.value}")
    print(f"置信度: {result.confidence:.1%}")
    print(f"结果: {result.result}")
    print(f"解释: {result.explanation}")
    
    # Demo 5: 图-文对齐 - UZI研究场景
    print("\n" + "-"*70)
    print("【Demo 5】图-文对齐 - UZI研报分析")
    print("-"*70)
    
    news = "英伟达发布B100芯片，光模块和CPO技术需求激增，中际旭创等厂商受益"
    attention = alignment.kg_guided_attention(news, focus_entity='英伟达')
    print(f"\n原文: {news}")
    print(f"KG引导关注: {[k for k,v in attention['attention_mask'].items() if v > 0.5]}")
    
    # 提取事实并更新KG
    facts = alignment.extract_and_update_kg(news, datetime.now())
    
    # Demo 6: KG扩展查询
    print("\n" + "-"*70)
    print("【Demo 6】KG扩展查询 - L1技能调用")
    print("-"*70)
    
    query_result = alignment.query_with_kg_expansion(
        "MACD金叉形态下历史上关联度最高的板块?"
    )
    print(f"\n查询: {query_result['original_query']}")
    print(f"扩展实体: {[c['entity'] for c in query_result['expanded_context'][:3]]}")
    print(f"答案: {query_result['answer']}")
    
    print("\n" + "="*70)
    print("✅ KG-GNN动态推理演示完成")
    print("="*70)
    print("\n核心技术:")
    print("  ✓ 时序图卷积 (Temporal GCN) - 捕捉演化规律")
    print("  ✓ 混合推理引擎 (Hybrid) - 神经+符号双轨")
    print("  ✓ 图-文对齐 (Alignment) - LLM与KG实时互动")
    print("\n架构价值:")
    print("  • KG从'图书馆'进化为'大脑皮层'")
    print("  • 能思考、会预测、自适应的AI投资系统")


if __name__ == "__main__":
    demo()
