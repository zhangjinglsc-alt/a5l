#!/usr/bin/env python3
"""
A5L v2.1.0 Olympus - SKILL自动组队算法 (Auto Skill Squad)

基于91% Expert率的智能SKILL协作系统
自动识别最优SKILL组合，实现复杂任务的自动化编排

作者: A5L Chief Architect
版本: v2.1.0-alpha
日期: 2026-05-09
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class TaskType(Enum):
    """任务类型分类"""
    STOCK_ANALYSIS = "stock_analysis"          # 个股分析
    INDUSTRY_RESEARCH = "industry_research"    # 行业研究
    MARKET_MONITOR = "market_monitor"          # 市场监控
    PORTFOLIO_REVIEW = "portfolio_review"      # 持仓复盘
    NEWS_ANALYSIS = "news_analysis"            # 新闻分析
    RISK_ASSESSMENT = "risk_assessment"        # 风险评估
    GENERAL_QUERY = "general_query"            # 通用查询


class SkillLevel(Enum):
    """SKILL等级"""
    MASTER = "Master"           # >95%
    EXPERT = "Expert"           # 80-95%
    PROFICIENT = "Proficient"   # 60-80%
    BEGINNER = "Beginner"       # <60%


@dataclass
class Skill:
    """SKILL定义"""
    id: str
    name: str
    proficiency: float
    category: str
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    @property
    def level(self) -> SkillLevel:
        if self.proficiency >= 0.95:
            return SkillLevel.MASTER
        elif self.proficiency >= 0.80:
            return SkillLevel.EXPERT
        elif self.proficiency >= 0.60:
            return SkillLevel.PROFICIENT
        else:
            return SkillLevel.BEGINNER
    
    @property
    def is_expert_or_above(self) -> bool:
        return self.proficiency >= 0.80


@dataclass
class SkillSquad:
    """SKILL小队 - 针对特定任务的SKILL组合"""
    name: str
    task_type: TaskType
    skills: List[Skill]
    execution_mode: str  # parallel / chain / mixed
    coordinator: Optional[Skill] = None  # Master级协调者
    
    @property
    def avg_proficiency(self) -> float:
        if not self.skills:
            return 0.0
        return sum(s.proficiency for s in self.skills) / len(self.skills)
    
    @property
    def master_count(self) -> int:
        return sum(1 for s in self.skills if s.level == SkillLevel.MASTER)
    
    @property
    def expert_count(self) -> int:
        return sum(1 for s in self.skills if s.level == SkillLevel.EXPERT)


class AutoSkillSquad:
    """
    SKILL自动组队引擎 - v2.1.0 Olympus核心组件
    
    基于91% Expert率的假设，实现：
    1. 自动识别任务类型
    2. 智能匹配最优SKILL组合
    3. 自动选择执行模式
    4. Master级协调者兜底
    """
    
    def __init__(self, skill_registry_path: str = "SKILL_REGISTRY.json"):
        self.skills: Dict[str, Skill] = {}
        self.squad_templates: Dict[TaskType, SkillSquad] = {}
        self.load_skills(skill_registry_path)
        self.init_squad_templates()
    
    def load_skills(self, registry_path: str):
        """加载SKILL注册表"""
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # 解析SKILL注册表
            for category, data in registry.get("categories", {}).items():
                for skill_data in data.get("skills", []):
                    skill = Skill(
                        id=skill_data.get("id", ""),
                        name=skill_data.get("name", ""),
                        proficiency=skill_data.get("proficiency", 0.0),
                        category=category,
                        capabilities=skill_data.get("description", "").split()
                    )
                    self.skills[skill.id] = skill
            
            print(f"✅ 加载 {len(self.skills)} 个SKILL")
            print(f"   Master: {sum(1 for s in self.skills.values() if s.level == SkillLevel.MASTER)}")
            print(f"   Expert: {sum(1 for s in self.skills.values() if s.level == SkillLevel.EXPERT)}")
            
        except Exception as e:
            print(f"⚠️ 加载SKILL注册表失败: {e}")
            self._load_default_skills()
    
    def _load_default_skills(self):
        """加载默认SKILL (v2.1.1 Olympus+状态)"""
        default_skills = [
            Skill("architect_5l", "五层架构", 0.9716, "trading_systems"),
            Skill("unified_stock_price", "统一股价", 0.95, "data_research"),
            Skill("coze_web_search", "Coze搜索", 0.95, "data_research"),
            Skill("blackswan_risk_control", "黑天鹅风控", 0.95, "trading_systems"),
            Skill("factor_investing", "因子投资", 0.941, "investment_analysis"),
            Skill("stock_five_steps", "股票五步法", 0.88, "investment_analysis"),
            Skill("yangguan_daodao", "阳关大道", 0.898, "investment_analysis"),
            Skill("private_banker", "私人投行", 0.83, "investment_analysis"),
            Skill("technical_analysis", "技术分析", 0.804, "investment_analysis"),
            Skill("catalyst_tier_framework", "CTF框架", 0.854, "investment_analysis"),
            Skill("industry_research", "白金分析师", 0.85, "investment_analysis"),
            Skill("sector_etf_monitor", "板块监控", 0.822, "data_research"),
        ]
        for skill in default_skills:
            self.skills[skill.id] = skill
    
    def init_squad_templates(self):
        """初始化SKILL小队模板 (v2.1.0优化版)"""
        
        # 个股分析小队 - v2.1.1升级：自下而上行业关联
        self.squad_templates[TaskType.STOCK_ANALYSIS] = SkillSquad(
            name="个股分析小队 (Stock Analysis Squad) - 自下而上",
            task_type=TaskType.STOCK_ANALYSIS,
            skills=[
                self.skills.get("unified_stock_price"),       # 数据基础
                self.skills.get("stock_five_steps"),          # 个股五维
                self.skills.get("private_banker"),            # 投行视角
                self.skills.get("catalyst_tier_framework"),   # 催化评估
                self.skills.get("industry_research"),         # ⭐ 白金分析师 - 自下而上行业分析
            ],
            execution_mode="mixed",  # 个股并行 + 行业链式
            coordinator=self.skills.get("architect_5l")
        )
        
        # 行业研究小队 - 白金方法论核心
        self.squad_templates[TaskType.INDUSTRY_RESEARCH] = SkillSquad(
            name="行业研究小队 (Industry Research Squad) - 白金方法论",
            task_type=TaskType.INDUSTRY_RESEARCH,
            skills=[
                self.skills.get("coze_web_search"),      # 信息收集
                self.skills.get("industry_research"),    # 白金分析师 - 核心
                self.skills.get("catalyst_tier_framework"),  # 催化评估
                self.skills.get("factor_investing"),     # 因子验证
            ],
            execution_mode="chain",
            coordinator=self.skills.get("architect_5l")
        )
        
        # 风险评估小队
        self.squad_templates[TaskType.RISK_ASSESSMENT] = SkillSquad(
            name="风险评估小队 (Risk Assessment Squad)",
            task_type=TaskType.RISK_ASSESSMENT,
            skills=[
                self.skills.get("blackswan_risk_control"),
                self.skills.get("factor_investing"),
                self.skills.get("technical_analysis"),
            ],
            execution_mode="parallel",
            coordinator=self.skills.get("blackswan_risk_control")
        )
        
        # 白金深度研究小队 (Premium Deep Research Squad) - v2.1.1升级
        # 双向分析模式：个股→行业（自下而上）| 行业→标的（自上而下）
        self.squad_templates["premium_research"] = SkillSquad(
            name="白金深度研究小队 (Premium Deep Research Squad) - 双向分析",
            task_type=TaskType.INDUSTRY_RESEARCH,
            skills=[
                # 数据层 (并行)
                self.skills.get("industry_research"),         # ⭐ 白金分析师 - 核心
                self.skills.get("coze_web_search"),           # 多源信息
                self.skills.get("factor_investing"),          # 量化筛选
                # 分析层 (并行)
                self.skills.get("catalyst_tier_framework"),   # 催化识别
                self.skills.get("private_banker"),            # 投行视角
                self.skills.get("stock_five_steps"),          # 个股五维 - 用于自上而下找标的
            ],
            execution_mode="mixed",  # 混合模式: 并行分析 + 链式整合
            coordinator=self.skills.get("architect_5l")
        )
        
        # 自上而下选股小队 (Top-Down Stock Picking Squad) - v2.1.1新增
        # 专门用于：聊行业 → 找好标的
        self.squad_templates["top_down_picking"] = SkillSquad(
            name="自上而下选股小队 (Top-Down Stock Picking Squad)",
            task_type=TaskType.INDUSTRY_RESEARCH,
            skills=[
                self.skills.get("industry_research"),         # ⭐ 白金分析师 - 行业框架
                self.skills.get("sector_etf_monitor"),        # 板块轮动
                self.skills.get("factor_investing"),          # 因子筛选
                self.skills.get("catalyst_tier_framework"),   # 催化事件
                self.skills.get("private_banker"),            # 投行标的池
            ],
            execution_mode="chain",  # 链式：行业→板块→个股
            coordinator=self.skills.get("architect_5l")
        )
    
    def detect_task_type(self, user_input: str) -> TaskType:
        """
        智能识别任务类型
        
        v2.1.0改进: 基于训练数据优化识别准确率
        """
        user_input = user_input.lower()
        
        # 股票代码模式 (6位数字 或 股票名称)
        import re
        stock_patterns = [
            r'\d{6}',  # 6位数字
            r'分析.*股票', r'分析.*股', r'看看.*股票',
            r'查询.*股价', r'查.*股价',
        ]
        for pattern in stock_patterns:
            if re.search(pattern, user_input):
                return TaskType.STOCK_ANALYSIS
        
        # 行业研究模式
        industry_keywords = ['行业', '板块', '产业链', '研报', '研究']
        if any(kw in user_input for kw in industry_keywords):
            return TaskType.INDUSTRY_RESEARCH
        
        # 自上而下选股模式 (v2.1.1新增)
        top_down_keywords = ['选股', '找标的', '推荐股票', '有什么好股票', '行业龙头', '板块机会']
        if any(kw in user_input for kw in top_down_keywords):
            return "top_down_picking"
        
        # 白金深度研究模式 (v2.1.0)
        premium_keywords = ['白金', '深度研究', '深度分析', '超级分析', '专业研报']
        if any(kw in user_input for kw in premium_keywords):
            return "premium_research"
        
        # 风险评估模式
        risk_keywords = ['风险', '风控', '回撤', '止损', '风险评估']
        if any(kw in user_input for kw in risk_keywords):
            return TaskType.RISK_ASSESSMENT
        
        # 市场监控模式
        market_keywords = ['市场', '大盘', '行情', '监控', '新闻']
        if any(kw in user_input for kw in market_keywords):
            return TaskType.MARKET_MONITOR
        
        return TaskType.GENERAL_QUERY
    
    def form_squad(self, task_type, complexity: str = "auto") -> SkillSquad:
        """
        组建SKILL小队
        
        Args:
            task_type: 任务类型 (TaskType 或 str)
            complexity: 复杂度 (simple/medium/complex/auto)
        
        Returns:
            最优SKILL小队配置
        """
        # 处理特殊类型 (v2.1.1双向分析)
        if task_type == "premium_research":
            return self.squad_templates.get("premium_research")
        if task_type == "top_down_picking":
            return self.squad_templates.get("top_down_picking")
        
        # 获取基础模板
        base_squad = self.squad_templates.get(task_type)
        if not base_squad:
            # 通用小队
            return SkillSquad(
                name="通用分析小队",
                task_type=task_type,
                skills=[self.skills.get("architect_5l")],
                execution_mode="chain",
                coordinator=self.skills.get("architect_5l")
            )
        
        # 根据复杂度调整
        if complexity == "simple":
            # 简化小队: 保留最高熟练度的1-2个SKILL
            sorted_skills = sorted(
                [s for s in base_squad.skills if s],
                key=lambda x: x.proficiency,
                reverse=True
            )
            return SkillSquad(
                name=f"{base_squad.name} (轻量版)",
                task_type=task_type,
                skills=sorted_skills[:2],
                execution_mode="chain",
                coordinator=base_squad.coordinator
            )
        
        elif complexity == "complex":
            # 增强小队: 添加额外Expert级SKILL
            enhanced_skills = list(base_squad.skills)
            # 添加相关Expert级SKILL
            for skill in self.skills.values():
                if skill.level == SkillLevel.EXPERT and skill not in enhanced_skills:
                    enhanced_skills.append(skill)
                    if len(enhanced_skills) >= 6:  # 限制小队规模
                        break
            return SkillSquad(
                name=f"{base_squad.name} (深度版)",
                task_type=task_type,
                skills=enhanced_skills,
                execution_mode="mixed",
                coordinator=base_squad.coordinator
            )
        
        return base_squad
    
    def execute(self, user_input: str, complexity: str = "auto") -> Dict:
        """
        执行自动组队流程
        
        v2.1.0核心接口 - 用户只需提供输入，自动完成：
        1. 任务类型识别
        2. SKILL小队组建
        3. 执行模式选择
        4. Master级协调
        """
        # Step 1: 识别任务类型
        task_type = self.detect_task_type(user_input)
        
        # Step 2: 组建SKILL小队 (支持白金深度研究)
        squad = self.form_squad(task_type, complexity)
        
        # 检查特殊分析模式
        is_premium = (task_type == "premium_research")
        is_top_down = (task_type == "top_down_picking")
        
        # Step 3: 生成执行计划
        execution_plan = {
            "input": user_input,
            "task_type": task_type.value,
            "squad_name": squad.name,
            "execution_mode": squad.execution_mode,
            "coordinator": squad.coordinator.name if squad.coordinator else None,
            "skills": [
                {
                    "id": s.id,
                    "name": s.name,
                    "proficiency": f"{s.proficiency:.1%}",
                    "level": s.level.value
                }
                for s in squad.skills if s
            ],
            "squad_stats": {
                "total_skills": len(squad.skills),
                "master_count": squad.master_count,
                "expert_count": squad.expert_count,
                "avg_proficiency": f"{squad.avg_proficiency:.1%}"
            },
            "v2.1_features": {
                "auto_detection": True,
                "expert_squad": squad.avg_proficiency >= 0.85,
                "master_coordination": squad.coordinator is not None,
                "parallel_ready": squad.execution_mode in ["parallel", "mixed"],
                "premium_research": is_premium,  # 白金深度研究
                "top_down_picking": is_top_down,  # 自上而下选股 (v2.1.1)
                "platinum_methodology": "industry_research" in [s.id for s in squad.skills if s],
                "bidirectional_analysis": True  # 双向分析模式 (v2.1.1)
            }
        }
        
        return execution_plan
    
    def print_squad_info(self, plan: Dict):
        """打印小队信息"""
        print(f"\n{'='*60}")
        print(f"🎯 {plan['squad_name']}")
        print(f"{'='*60}")
        
        # 打印分析模式标识
        features = plan.get('v2.1_features', {})
        if features.get('top_down_picking'):
            print("🔍 分析模式: 自上而下选股 (行业→标的)")
        elif features.get('premium_research'):
            print("💎 分析模式: 白金深度研究 (双向分析)")
        elif 'stock' in plan['task_type'] or plan['task_type'] == 'stock_analysis':
            print("📈 分析模式: 自下而上分析 (个股→行业)")
        elif 'industry' in plan['task_type']:
            print("🏭 分析模式: 行业研究")
        
        print(f"任务类型: {plan['task_type']}")
        print(f"执行模式: {plan['execution_mode']}")
        print(f"协调者: {plan['coordinator'] or 'None'}")
        print(f"\n📊 小队配置 ({plan['squad_stats']['total_skills']}个SKILL):")
        print(f"{'-'*60}")
        
        for skill in plan['skills']:
            level_emoji = {
                "Master": "💎",
                "Expert": "🥇",
                "Proficient": "🥈",
                "Beginner": "🥉"
            }.get(skill['level'], "❓")
            print(f"  {level_emoji} {skill['name']} ({skill['id']}) - {skill['proficiency']}")
        
        print(f"{'-'*60}")
        print(f"平均熟练度: {plan['squad_stats']['avg_proficiency']}")
        print(f"Master级: {plan['squad_stats']['master_count']} | Expert级: {plan['squad_stats']['expert_count']}")
        print(f"{'='*60}\n")


def main():
    """演示SKILL自动组队"""
    print("🚀 A5L v2.1.0 Olympus - SKILL自动组队系统")
    print("="*60)
    
    # 初始化自动组队引擎
    engine = AutoSkillSquad()
    
    # 测试用例 (v2.1.1更新 - 双向分析模式测试)
    test_inputs = [
        "分析000066中国长城",           # 个股分析 → 自下而上行业关联
        "研究AI算力行业",               # 行业研究
        "评估当前持仓风险",             # 风险评估
        "看看美股特斯拉",               # 个股分析
        "查询招商银行股价",             # 快速查询
        "白金深度分析半导体行业",       # 白金深度研究
        "深度研究SpaceX商业航天",       # 深度研究
        "AI算力行业有什么好股票",       # ⭐ 自上而下选股
        "半导体板块推荐几个标的",       # ⭐ 自上而下选股
        "自下而上分析一下中芯国际",     # 个股→行业
    ]
    
    print("\n📋 测试自动组队:\n")
    for user_input in test_inputs:
        print(f"📝 输入: \"{user_input}\"")
        plan = engine.execute(user_input)
        engine.print_squad_info(plan)


if __name__ == "__main__":
    main()
