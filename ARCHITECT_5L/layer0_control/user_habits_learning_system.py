#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Layer 0 - 用户习惯学习系统 (User Habits Learning System)
让A5L越来越懂用户，磨合程度越来越高！

核心功能:
1. 使用习惯记录 - 记录用户的操作偏好
2. 行为模式学习 - 学习用户的行为模式
3. 个性化推荐 - 基于习惯提供个性化服务
4. 默契度评分 - 量化A5L与用户的磨合程度
5. 自动适配 - 自动调整以符合用户习惯

位置: Layer 0 (元控制层) - 与七位一体并列
作者: A5L Chief Architect
创建时间: 2026-05-02 (五一假期)
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserPreference:
    """用户偏好设置"""
    # 沟通偏好
    communication_style: str = "concise"  # concise/detailed/humorous/professional
    response_length: str = "medium"  # short/medium/long
    use_emoji: bool = True
    use_markdown_tables: bool = True
    
    # 时间偏好
    preferred_analysis_time: str = "09:00"  # 每日分析时间
    preferred_review_time: str = "21:00"  # 每日复盘时间
    quiet_hours_start: str = "23:00"  # 免打扰开始
    quiet_hours_end: str = "08:00"  # 免打扰结束
    
    # 投资偏好
    preferred_markets: List[str] = field(default_factory=lambda: ["A股", "美股"])
    preferred_strategies: List[str] = field(default_factory=lambda: ["趋势跟踪", "价值投资"])
    risk_tolerance: str = "medium"  # low/medium/high
    holding_period: str = "swing"  # short/medium/long
    
    # 报告偏好
    report_format: str = "markdown"  # markdown/json/csv
    report_sections: List[str] = field(default_factory=lambda: ["summary", "signals", "risks"])
    include_charts: bool = True
    
    # 交互偏好
    auto_execute: bool = False  # 是否自动执行确认的操作
    confirm_destructive: bool = True  # 破坏性操作前确认
    proactive_suggestions: bool = True  # 主动提供建议
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserPreference':
        return cls(**data)


@dataclass
class UserAction:
    """用户行为记录"""
    action_type: str  # analyze/query/trade/review/config/etc.
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)
    context: str = ""  # 操作上下文
    
    def to_dict(self) -> Dict:
        return {
            'action_type': self.action_type,
            'timestamp': self.timestamp,
            'details': self.details,
            'context': self.context
        }


@dataclass
class InteractionPattern:
    """交互模式"""
    pattern_name: str
    frequency: int  # 发生次数
    last_occurrence: str
    typical_context: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'pattern_name': self.pattern_name,
            'frequency': self.frequency,
            'last_occurrence': self.last_occurrence,
            'typical_context': self.typical_context
        }


class UserHabitsLearningSystem:
    """
    用户习惯学习系统 - 让A5L越来越懂用户
    
    核心功能:
    1. 记录用户每次交互
    2. 学习用户行为模式
    3. 预测用户需求
    4. 提供个性化体验
    5. 量化默契度
    """
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.storage_path = f"KIWI/user_habits/{user_id}"
        self.preferences_file = f"{self.storage_path}/preferences.json"
        self.actions_file = f"{self.storage_path}/actions.json"
        self.patterns_file = f"{self.storage_path}/patterns.json"
        self.rapport_file = f"{self.storage_path}/rapport_score.json"
        
        # 确保存储目录存在
        os.makedirs(self.storage_path, exist_ok=True)
        
        # 加载现有数据
        self.preferences = self._load_preferences()
        self.actions_history: List[UserAction] = self._load_actions()
        self.patterns: Dict[str, InteractionPattern] = self._load_patterns()
        self.rapport_score: float = self._load_rapport_score()
        
        logger.info(f"✅ UserHabitsLearningSystem initialized for user: {user_id}")
    
    # ========== 数据加载/保存 ==========
    
    def _load_preferences(self) -> UserPreference:
        """加载用户偏好"""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserPreference.from_dict(data)
            except Exception as e:
                logger.warning(f"Failed to load preferences: {e}")
        return UserPreference()
    
    def _save_preferences(self):
        """保存用户偏好"""
        with open(self.preferences_file, 'w', encoding='utf-8') as f:
            json.dump(self.preferences.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_actions(self) -> List[UserAction]:
        """加载行为历史"""
        if os.path.exists(self.actions_file):
            try:
                with open(self.actions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return [UserAction(**item) for item in data]
            except Exception as e:
                logger.warning(f"Failed to load actions: {e}")
        return []
    
    def _save_actions(self):
        """保存行为历史"""
        with open(self.actions_file, 'w', encoding='utf-8') as f:
            json.dump([a.to_dict() for a in self.actions_history], f, ensure_ascii=False, indent=2)
    
    def _load_patterns(self) -> Dict[str, InteractionPattern]:
        """加载行为模式"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return {k: InteractionPattern(**v) for k, v in data.items()}
            except Exception as e:
                logger.warning(f"Failed to load patterns: {e}")
        return {}
    
    def _save_patterns(self):
        """保存行为模式"""
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump({k: v.to_dict() for k, v in self.patterns.items()}, f, ensure_ascii=False, indent=2)
    
    def _load_rapport_score(self) -> float:
        """加载默契度分数"""
        if os.path.exists(self.rapport_file):
            try:
                with open(self.rapport_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('score', 0.0)
            except Exception as e:
                logger.warning(f"Failed to load rapport score: {e}")
        return 0.0
    
    def _save_rapport_score(self):
        """保存默契度分数"""
        with open(self.rapport_file, 'w', encoding='utf-8') as f:
            json.dump({
                'score': self.rapport_score,
                'last_updated': datetime.now().isoformat(),
                'level': self._get_rapport_level()
            }, f, ensure_ascii=False, indent=2)
    
    # ========== 核心功能 ==========
    
    def record_action(self, action_type: str, details: Dict = None, context: str = ""):
        """记录用户行为"""
        action = UserAction(
            action_type=action_type,
            timestamp=datetime.now().isoformat(),
            details=details or {},
            context=context
        )
        self.actions_history.append(action)
        
        # 保留最近1000条记录
        if len(self.actions_history) > 1000:
            self.actions_history = self.actions_history[-1000:]
        
        self._save_actions()
        
        # 实时更新模式
        self._update_patterns(action)
        
        # 更新默契度
        self._update_rapport_score()
        
        logger.info(f"📝 Recorded action: {action_type}")
    
    def update_preference(self, key: str, value: Any):
        """更新用户偏好"""
        if hasattr(self.preferences, key):
            setattr(self.preferences, key, value)
            self._save_preferences()
            logger.info(f"💾 Updated preference: {key} = {value}")
            return True
        return False
    
    def get_preference(self, key: str) -> Any:
        """获取用户偏好"""
        return getattr(self.preferences, key, None)
    
    def _update_patterns(self, action: UserAction):
        """更新行为模式"""
        # 模式1: 时间段偏好
        hour = datetime.fromisoformat(action.timestamp).hour
        time_period = "morning" if 6 <= hour < 12 else "afternoon" if 12 <= hour < 18 else "evening" if 18 <= hour < 23 else "night"
        self._increment_pattern(f"active_{time_period}", action.context)
        
        # 模式2: 操作类型频率
        self._increment_pattern(f"action_{action.action_type}", action.context)
        
        # 模式3: 关注的市场
        if 'market' in action.details:
            self._increment_pattern(f"market_{action.details['market']}", action.context)
        
        # 模式4: 关注的股票
        if 'symbol' in action.details:
            self._increment_pattern(f"stock_{action.details['symbol']}", action.context)
        
        self._save_patterns()
    
    def _increment_pattern(self, pattern_name: str, context: str):
        """增加模式频率"""
        if pattern_name in self.patterns:
            self.patterns[pattern_name].frequency += 1
            self.patterns[pattern_name].last_occurrence = datetime.now().isoformat()
            if context and context not in self.patterns[pattern_name].typical_context:
                self.patterns[pattern_name].typical_context.append(context)
        else:
            self.patterns[pattern_name] = InteractionPattern(
                pattern_name=pattern_name,
                frequency=1,
                last_occurrence=datetime.now().isoformat(),
                typical_context=[context] if context else []
            )
    
    def _update_rapport_score(self):
        """更新默契度分数 (0-100)"""
        # 基于以下因素计算:
        # 1. 交互次数 (最多30分)
        interaction_score = min(30, len(self.actions_history) / 10)
        
        # 2. 偏好设置完整度 (最多20分)
        preference_fields = [
            self.preferences.communication_style != "concise",
            len(self.preferences.preferred_markets) > 0,
            len(self.preferences.preferred_strategies) > 0,
            self.preferences.preferred_analysis_time != "09:00"
        ]
        preference_score = sum(preference_fields) * 5
        
        # 3. 行为模式识别 (最多30分)
        pattern_score = min(30, len(self.patterns) * 2)
        
        # 4. 使用时长 (最多20分)
        if self.actions_history:
            first_action = datetime.fromisoformat(self.actions_history[0].timestamp)
            days_using = (datetime.now() - first_action).days
            usage_score = min(20, days_using)
        else:
            usage_score = 0
        
        self.rapport_score = interaction_score + preference_score + pattern_score + usage_score
        self._save_rapport_score()
    
    def _get_rapport_level(self) -> str:
        """获取默契度等级"""
        if self.rapport_score >= 80:
            return "灵魂伴侣"  # Soulmate
        elif self.rapport_score >= 60:
            return "亲密战友"  # Close Partner
        elif self.rapport_score >= 40:
            return "默契搭档"  # Good Partner
        elif self.rapport_score >= 20:
            return "熟悉朋友"  # Familiar Friend
        else:
            return "初识之交"  # New Acquaintance
    
    # ========== 分析与预测 ==========
    
    def get_usage_statistics(self) -> Dict:
        """获取使用统计"""
        if not self.actions_history:
            return {}
        
        # 时间段分布
        hour_distribution = Counter()
        for action in self.actions_history:
            hour = datetime.fromisoformat(action.timestamp).hour
            hour_distribution[hour] += 1
        
        # 操作类型分布
        action_types = Counter(a.action_type for a in self.actions_history)
        
        # 最近7天活跃度
        last_7_days = datetime.now() - timedelta(days=7)
        recent_actions = [a for a in self.actions_history if datetime.fromisoformat(a.timestamp) > last_7_days]
        
        return {
            'total_actions': len(self.actions_history),
            'unique_days': len(set(datetime.fromisoformat(a.timestamp).date() for a in self.actions_history)),
            'recent_7_days_actions': len(recent_actions),
            'hour_distribution': dict(hour_distribution),
            'action_type_distribution': dict(action_types),
            'most_active_hour': hour_distribution.most_common(1)[0][0] if hour_distribution else None
        }
    
    def predict_next_action(self) -> Dict:
        """预测用户下一步可能的行为"""
        if not self.patterns:
            return {'prediction': 'unknown', 'confidence': 0}
        
        # 找出最频繁的模式
        top_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.frequency,
            reverse=True
        )[:3]
        
        predictions = []
        for pattern in top_patterns:
            if pattern.pattern_name.startswith('action_'):
                action_type = pattern.pattern_name.replace('action_', '')
                confidence = min(100, pattern.frequency * 5)
                predictions.append({
                    'action_type': action_type,
                    'confidence': confidence,
                    'typical_context': pattern.typical_context[:3]
                })
        
        return {
            'top_predictions': predictions,
            'based_on_patterns': len(self.patterns)
        }
    
    def get_stock_interests(self) -> List[Dict]:
        """获取用户关注的股票 (基于历史行为)"""
        stock_patterns = {k: v for k, v in self.patterns.items() if k.startswith('stock_')}
        
        stocks = []
        for pattern_name, pattern in sorted(stock_patterns.items(), key=lambda x: x[1].frequency, reverse=True):
            symbol = pattern_name.replace('stock_', '')
            stocks.append({
                'symbol': symbol,
                'interest_score': pattern.frequency,
                'last_interest': pattern.last_occurrence,
                'typical_contexts': pattern.typical_context[:3]
            })
        
        return stocks[:10]  # 返回Top 10
    
    def get_optimal_communication_style(self) -> Dict:
        """获取最佳沟通方式建议"""
        return {
            'style': self.preferences.communication_style,
            'response_length': self.preferences.response_length,
            'use_emoji': self.preferences.use_emoji,
            'include_charts': self.preferences.include_charts,
            'proactive_suggestions': self.preferences.proactive_suggestions
        }
    
    # ========== 个性化推荐 ==========
    
    def get_personalized_greeting(self) -> str:
        """获取个性化问候"""
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            time_greeting = "早上好"
        elif 12 <= hour < 18:
            time_greeting = "下午好"
        elif 18 <= hour < 23:
            time_greeting = "晚上好"
        else:
            time_greeting = "夜深了"
        
        rapport_level = self._get_rapport_level()
        
        # 根据默契度调整问候语
        if self.rapport_score >= 60:
            return f"{time_greeting}！我们的默契度已经达到{rapport_level}级别({self.rapport_score:.0f}分)了！🎉"
        elif self.rapport_score >= 30:
            return f"{time_greeting}！我们的默契度正在提升中({self.rapport_score:.0f}分)，越来越了解你了！💪"
        else:
            return f"{time_greeting}！我是A5L，让我们一起建立默契吧！🚀"
    
    def suggest_next_actions(self) -> List[Dict]:
        """建议下一步操作"""
        suggestions = []
        
        # 基于时间的建议
        current_hour = datetime.now().hour
        if current_hour == 9:
            suggestions.append({
                'action': 'analyze_market_open',
                'description': '开盘分析 - 查看隔夜新闻和市场情绪',
                'reason': '这是你通常开始分析的时间'
            })
        elif current_hour == 21:
            suggestions.append({
                'action': 'daily_review',
                'description': '每日复盘 - 总结今天的交易和市场表现',
                'reason': '这是你习惯的复盘时间'
            })
        
        # 基于关注股票的建议
        stock_interests = self.get_stock_interests()
        if stock_interests:
            top_stock = stock_interests[0]
            suggestions.append({
                'action': 'analyze_stock',
                'target': top_stock['symbol'],
                'description': f"分析 {top_stock['symbol']} - 你近期最关注的股票",
                'reason': f"过去查询了 {top_stock['interest_score']} 次"
            })
        
        # 基于模式的建议
        if 'active_morning' in self.patterns and self.patterns['active_morning'].frequency > 5:
            suggestions.append({
                'action': 'morning_brief',
                'description': '生成晨会简报 - 你习惯在早上获取市场概览',
                'reason': '基于你的早间活跃模式'
            })
        
        return suggestions[:3]
    
    # ========== 报告生成 ==========
    
    def generate_habits_report(self) -> str:
        """生成用户习惯报告"""
        lines = []
        
        lines.append("# 🧠 A5L 用户习惯学习报告")
        lines.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**用户ID**: {self.user_id}")
        lines.append("\n---\n")
        
        # 默契度
        lines.append("## 💕 默契度评分")
        lines.append(f"\n**当前默契度**: {self.rapport_score:.1f}/100")
        lines.append(f"**关系等级**: {self._get_rapport_level()}")
        
        # 进度条
        bar_length = 20
        filled = int(self.rapport_score / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        lines.append(f"\n```")
        lines.append(f"[{bar}] {self.rapport_score:.0f}%")
        lines.append("```")
        
        # 使用统计
        lines.append("\n---\n")
        lines.append("## 📊 使用统计")
        
        stats = self.get_usage_statistics()
        if stats:
            lines.append(f"\n- **总交互次数**: {stats['total_actions']}")
            lines.append(f"- **使用天数**: {stats['unique_days']}天")
            lines.append(f"- **最近7天交互**: {stats['recent_7_days_actions']}次")
            if stats['most_active_hour'] is not None:
                lines.append(f"- **最活跃时段**: {stats['most_active_hour']}:00")
        
        # 行为模式
        lines.append("\n---\n")
        lines.append("## 🔍 识别的行为模式")
        
        if self.patterns:
            lines.append("\n| 模式 | 频率 | 最近发生 |")
            lines.append("|------|------|----------|")
            for pattern in sorted(self.patterns.values(), key=lambda p: p.frequency, reverse=True)[:10]:
                last_time = datetime.fromisoformat(pattern.last_occurrence).strftime('%m-%d %H:%M')
                lines.append(f"| {pattern.pattern_name} | {pattern.frequency} | {last_time} |")
        else:
            lines.append("\n还在学习中，暂时未识别到明确模式...")
        
        # 关注股票
        lines.append("\n---\n")
        lines.append("## 📈 关注的股票")
        
        stocks = self.get_stock_interests()
        if stocks:
            lines.append("\n| 股票代码 | 关注次数 | 最近关注 |")
            lines.append("|----------|----------|----------|")
            for stock in stocks[:5]:
                last_time = datetime.fromisoformat(stock['last_interest']).strftime('%m-%d')
                lines.append(f"| {stock['symbol']} | {stock['interest_score']} | {last_time} |")
        else:
            lines.append("\n暂无股票关注记录")
        
        # 个性化建议
        lines.append("\n---\n")
        lines.append("## 💡 个性化建议")
        
        suggestions = self.suggest_next_actions()
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"\n**{i}. {suggestion['description']}**")
                lines.append(f"   - 原因: {suggestion['reason']}")
        else:
            lines.append("\n继续互动，我会更好地了解你的习惯！")
        
        # 结语
        lines.append("\n---\n")
        lines.append("## 📝 备注")
        lines.append("\n> A5L正在持续学习你的习惯，每次交互都会让我更了解你。")
        lines.append("> 默契度会随着使用时间和交互质量不断提升！")
        lines.append(f"\n*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return '\n'.join(lines)
    
    def save_habits_report(self, output_path: str = None):
        """保存习惯报告"""
        if output_path is None:
            output_path = f"{self.storage_path}/habits_report.md"
        
        report = self.generate_habits_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✅ Habits report saved to: {output_path}")
        return output_path
    
    # ========== 快捷方法 ==========
    
    def quick_setup(self, **kwargs):
        """快速设置用户偏好"""
        for key, value in kwargs.items():
            self.update_preference(key, value)
        logger.info("✅ Quick setup completed")
    
    def export_all_data(self) -> Dict:
        """导出所有数据"""
        return {
            'user_id': self.user_id,
            'preferences': self.preferences.to_dict(),
            'actions_count': len(self.actions_history),
            'patterns_count': len(self.patterns),
            'rapport_score': self.rapport_score,
            'rapport_level': self._get_rapport_level(),
            'export_time': datetime.now().isoformat()
        }


def demo_user_habits_learning():
    """演示: 用户习惯学习系统"""
    
    print("=" * 80)
    print("🧠 A5L 用户习惯学习系统演示")
    print("=" * 80)
    print("\n💡 场景: 让A5L学习用户习惯，越来越默契！\n")
    
    # 创建学习系统
    print("[1/6] 初始化用户习惯学习系统...")
    habits = UserHabitsLearningSystem(user_id="zhangjing")
    
    # 设置偏好
    print("[2/6] 设置用户偏好...")
    habits.quick_setup(
        communication_style="concise",
        preferred_markets=["A股", "美股", "港股"],
        preferred_strategies=["趋势跟踪", "价值投资", "超短线"],
        preferred_analysis_time="09:00",
        preferred_review_time="21:00",
        risk_tolerance="medium"
    )
    
    # 模拟用户行为记录
    print("[3/6] 模拟记录用户行为...")
    
    # 模拟一些历史行为
    mock_actions = [
        ('analyze_stock', {'symbol': '300308.SZ', 'market': 'A股'}, '分析CPO龙头'),
        ('analyze_stock', {'symbol': '000977.SZ', 'market': 'A股'}, '分析AI服务器'),
        ('query_portfolio', {}, '查看持仓'),
        ('daily_review', {}, '每日复盘'),
        ('analyze_stock', {'symbol': '300308.SZ', 'market': 'A股'}, '再次分析CPO'),
        ('analyze_industry', {'industry': 'AI算力'}, '产业链分析'),
        ('set_config', {}, '更新配置'),
        ('analyze_stock', {'symbol': '688041.SH', 'market': 'A股'}, '分析AI芯片'),
    ]
    
    for action_type, details, context in mock_actions:
        habits.record_action(action_type, details, context)
    
    print(f"   ✅ 已记录 {len(mock_actions)} 个行为")
    
    # 显示默契度
    print("\n[4/6] 当前默契度:")
    print(f"   💕 默契度分数: {habits.rapport_score:.1f}/100")
    print(f"   🎖️ 关系等级: {habits._get_rapport_level()}")
    
    # 显示使用统计
    print("\n[5/6] 使用统计:")
    stats = habits.get_usage_statistics()
    print(f"   📊 总交互次数: {stats['total_actions']}")
    print(f"   📅 使用天数: {stats['unique_days']}天")
    if stats.get('most_active_hour'):
        print(f"   ⏰ 最活跃时段: {stats['most_active_hour']}:00")
    
    # 显示关注股票
    print("\n[6/6] 关注的股票:")
    stocks = habits.get_stock_interests()
    for i, stock in enumerate(stocks[:3], 1):
        print(f"   {i}. {stock['symbol']} - 关注{stock['interest_score']}次")
    
    # 个性化问候
    print("\n" + "=" * 80)
    print(habits.get_personalized_greeting())
    
    # 生成报告
    print("\n📄 生成习惯学习报告...")
    report_path = habits.save_habits_report()
    print(f"   ✅ 报告已保存: {report_path}")
    
    print("\n" + "=" * 80)
    print("🎉 演示完成！A5L已经开始学习你的习惯了！")
    print("=" * 80)
    print("\n💡 使用建议:")
    print("   1. 每次使用A5L时，系统会自动记录你的行为")
    print("   2. 默契度会随着使用时间和交互质量提升")
    print("   3. A5L会根据你的习惯提供个性化建议")
    print("   4. 查看习惯报告了解A5L有多懂你")
    print("\n🚀 A5L会越来越懂你！")


if __name__ == "__main__":
    demo_user_habits_learning()
