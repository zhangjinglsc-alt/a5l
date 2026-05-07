#!/usr/bin/env python3
"""
CTF Analyzer - 催化事件CTF分级分析器
自动应用催化剂分级框架进行事件分析
"""

import json
import re
from datetime import datetime
from pathlib import Path

class CTFAnalyzer:
    """CTF分级分析器"""
    
    def __init__(self):
        self.base_path = Path('/workspace/projects/workspace/skills/catalyst-monitor-auto')
        self.keywords = self._load_keywords()
    
    def _load_keywords(self):
        """加载分级关键词库"""
        keywords_file = self.base_path / 'references' / 'tier_keywords.json'
        if keywords_file.exists():
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认关键词库
        return {
            "tier1": {
                "patterns": [
                    r"TAM.*(上调|翻倍|增长|扩大).*?(\d+)%",
                    r"市场规模.*(翻倍|扩大|上调)",
                    r"(成为|确立).*主流",
                    r"(行业|产业).*格局.*改变",
                    r"供需.*(不可逆|永久)",
                    r"(技术|路线).*主流化",
                    r"(范式|革命性).*变化"
                ],
                "keywords": ["TAM上调", "市场规模翻倍", "成为主流", "格局改变", "不可逆", "范式转移"]
            },
            "tier2": {
                "patterns": [
                    r"LTA",
                    r"长协",
                    r"锁定.*产能",
                    r"订单.*排至.*20\d{2}",
                    r"订单.*超预期",
                    r"指引.*上调",
                    r"产能.*(满载|饱和)"
                ],
                "keywords": ["长协", "锁定产能", "订单超预期", "指引上调", "产能满载"]
            },
            "tier3": {
                "patterns": [
                    r"(\d+)亿.*(订单|合同)",
                    r"战略.*(合作|签约)",
                    r"(收购|合并|重组)",
                    r"政策.*(出台|发布)",
                    r"补贴",
                    r"规划.*发布"
                ],
                "keywords": ["亿订单", "战略合作", "收购", "政策出台", "补贴"]
            },
            "tier4": {
                "patterns": [
                    r"涨价",
                    r"价格.*上调",
                    r"供不应求",
                    r"补涨",
                    r"扩散",
                    r"关联.*(板块|概念)"
                ],
                "keywords": ["涨价", "价格上调", "补涨", "扩散"]
            }
        }
    
    def analyze(self, title, content="", source=""):
        """
        分析单个事件的CTF级别
        
        Args:
            title: 事件标题
            content: 事件内容
            source: 事件来源
        
        Returns:
            dict: 包含tier, confidence, reason, action的分析结果
        """
        text = f"{title} {content}"
        
        # 各级别匹配
        tier_scores = {
            1: self._calculate_tier_score(text, "tier1"),
            2: self._calculate_tier_score(text, "tier2"),
            3: self._calculate_tier_score(text, "tier3"),
            4: self._calculate_tier_score(text, "tier4")
        }
        
        # 确定最高级别
        max_tier = max(tier_scores, key=tier_scores.get)
        max_score = tier_scores[max_tier]
        
        # 置信度判断
        if max_score >= 3:
            confidence = "high"
        elif max_score >= 1:
            confidence = "medium"
        else:
            confidence = "low"
            max_tier = 4  # 默认Tier 4
        
        # 生成分析结果
        result = {
            "tier": max_tier,
            "confidence": confidence,
            "score": max_score,
            "title": title,
            "content": content[:200] if content else "",
            "source": source,
            "time": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "reason": self._generate_reason(max_tier, text),
            "position_limit": self._get_position_limit(max_tier),
            "holding_period": self._get_holding_period(max_tier),
            "action": self._generate_action(max_tier, confidence)
        }
        
        return result
    
    def _calculate_tier_score(self, text, tier_key):
        """计算特定级别的匹配分数"""
        score = 0
        tier_data = self.keywords.get(tier_key, {})
        
        # 模式匹配
        for pattern in tier_data.get("patterns", []):
            if re.search(pattern, text, re.IGNORECASE):
                score += 2
        
        # 关键词匹配
        for keyword in tier_data.get("keywords", []):
            if keyword in text:
                score += 1
        
        return score
    
    def _generate_reason(self, tier, text):
        """生成分级理由"""
        reasons = {
            1: "TAM上修/技术主流化/供需结构变化 - 可能改变估值体系",
            2: "供需缺口确认/龙头订单上修 - 支撑中线持仓",
            3: "大额订单/政策/战略合作 - 短期情绪驱动",
            4: "补涨扩散/涨价叙事 - 快进快出"
        }
        return reasons.get(tier, "未知")
    
    def _get_position_limit(self, tier):
        """获取仓位上限"""
        limits = {1: "20-25%", 2: "15-20%", 3: "10-15%", 4: "5-10%"}
        return limits.get(tier, "5-10%")
    
    def _get_holding_period(self, tier):
        """获取持有周期"""
        periods = {
            1: "季度→年度",
            2: "月度→季度",
            3: "周度→月度",
            4: "日度→周度"
        }
        return periods.get(tier, "日度→周度")
    
    def _generate_action(self, tier, confidence):
        """生成操作建议"""
        if confidence == "low":
            return "信息不足，需进一步验证"
        
        actions = {
            1: "调整主仓位，寻找预期差入口；逻辑证伪才卖出",
            2: "支撑中线持仓；Tier1+2共振最强",
            3: "情绪消耗快(3-5天)，不宜追高",
            4: "快进快出；Tier4领涨=主线到顶信号"
        }
        return actions.get(tier, "观望")
    
    def batch_analyze(self, events):
        """批量分析事件"""
        results = []
        for event in events:
            result = self.analyze(
                title=event.get('title', ''),
                content=event.get('content', ''),
                source=event.get('source', '')
            )
            results.append(result)
        return results
    
    def generate_report(self, results):
        """生成分析报告"""
        if not results:
            return "无事件需要分析"
        
        # 按级别分组
        tier_groups = {1: [], 2: [], 3: [], 4: []}
        for r in results:
            tier_groups[r['tier']].append(r)
        
        report = f"""
🎯 CTF分级分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
分析事件: {len(results)} 个

分级统计:
├─ 🎯 Tier 1 (范式级): {len(tier_groups[1])} 个
├─ 🔶 Tier 2 (周期确认): {len(tier_groups[2])} 个
├─ 🔷 Tier 3 (资金驱动): {len(tier_groups[3])} 个
└─ ⚪ Tier 4 (补涨扩散): {len(tier_groups[4])} 个

重点事件:
"""
        
        # 重点显示Tier 1和Tier 2
        for tier in [1, 2]:
            if tier_groups[tier]:
                report += f"\n{'='*40}\n"
                icons = {1: "🎯", 2: "🔶"}
                report += f"{icons.get(tier, '')} Tier {tier} 事件:\n"
                for event in tier_groups[tier][:3]:  # 最多显示3个
                    report += f"\n• {event['title']}\n"
                    report += f"  理由: {event['reason']}\n"
                    report += f"  仓位: {event['position_limit']} | 周期: {event['holding_period']}\n"
                    report += f"  建议: {event['action']}\n"
        
        return report


def main():
    """测试分析器"""
    analyzer = CTFAnalyzer()
    
    # 测试事件
    test_events = [
        {
            "title": "AMD服务器CPU TAM从600亿上调至1200亿美元",
            "content": "AMD发布新一代服务器CPU，市场预测TAM翻倍增长",
            "source": "华尔街见闻"
        },
        {
            "title": "闪迪签署5份LTA锁定2027年1/3产能",
            "content": "存储涨价周期确认",
            "source": "财联社"
        },
        {
            "title": "字节跳动56亿美元昇腾大单",
            "content": "国产算力链情绪升温",
            "source": "科创板日报"
        }
    ]
    
    print("🧠 CTF分析器测试中...\n")
    
    results = analyzer.batch_analyze(test_events)
    
    for r in results:
        print(f"\n{'='*50}")
        print(f"事件: {r['title']}")
        print(f"分级: Tier {r['tier']} (置信度: {r['confidence']})")
        print(f"理由: {r['reason']}")
        print(f"仓位: {r['position_limit']} | 周期: {r['holding_period']}")
        print(f"建议: {r['action']}")
    
    print(f"\n{'='*50}")
    print(analyzer.generate_report(results))


if __name__ == '__main__':
    main()
