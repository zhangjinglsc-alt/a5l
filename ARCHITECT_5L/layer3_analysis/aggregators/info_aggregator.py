#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 3: Info Aggregator
非结构化分析层 - 信息聚合器

功能：
1. 聚合多源非结构化信息
2. 公告、新闻、研报采集
3. 信息去重和过滤
4. 数据源可信度评估
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class InfoSource:
    """信息源"""
    name: str
    url: str
    category: str  # announcement, news, research, social
    credibility: int  # 1-10
    update_frequency: str
    requires_auth: bool = False

@dataclass
class AggregatedInfo:
    """聚合后的信息"""
    id: str
    title: str
    content: str
    source: str
    source_url: str
    publish_time: str
    category: str
    symbols: List[str]  # 相关股票代码
    credibility_score: float
    sentiment: Optional[str] = None
    verified: bool = False

class InfoAggregator:
    """信息聚合器"""
    
    def __init__(self, workspace: str = "/workspace/projects/workspace"):
        self.workspace = workspace
        self.raw_dir = f"{workspace}/data/architect_5l/raw_info"
        self.processed_dir = f"{workspace}/data/architect_5l/processed_info"
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # 信息源配置
        self.sources = self._init_sources()
        
        # 去重记录
        self._seen_hashes = set()
    
    def _init_sources(self) -> List[InfoSource]:
        """初始化信息源"""
        return [
            # 官方公告源（最高可信度）
            InfoSource(
                name="上交所公告",
                url="http://www.sse.com.cn/disclosure/listedinfo/announcement/",
                category="announcement",
                credibility=10,
                update_frequency="realtime"
            ),
            InfoSource(
                name="深交所公告",
                url="http://www.szse.cn/disclosure/listed/notice/",
                category="announcement",
                credibility=10,
                update_frequency="realtime"
            ),
            InfoSource(
                name="港交所披露易",
                url="https://www.hkexnews.hk",
                category="announcement",
                credibility=10,
                update_frequency="realtime"
            ),
            InfoSource(
                name="SEC EDGAR",
                url="https://www.sec.gov/edgar.shtml",
                category="announcement",
                credibility=10,
                update_frequency="realtime"
            ),
            
            # 财经新闻源
            InfoSource(
                name="财新网",
                url="https://www.caixin.com",
                category="news",
                credibility=9,
                update_frequency="continuous"
            ),
            InfoSource(
                name="华尔街日报",
                url="https://www.wsj.com",
                category="news",
                credibility=9,
                update_frequency="continuous"
            ),
            InfoSource(
                name="彭博社",
                url="https://www.bloomberg.com",
                category="news",
                credibility=9,
                update_frequency="continuous",
                requires_auth=True
            ),
            InfoSource(
                name="路透社",
                url="https://www.reuters.com",
                category="news",
                credibility=9,
                update_frequency="continuous"
            ),
            
            # 研报数据源
            InfoSource(
                name="东方财富研报",
                url="https://data.eastmoney.com/report/",
                category="research",
                credibility=7,
                update_frequency="daily"
            ),
            InfoSource(
                name="慧博投研",
                url="http://www.hibor.com.cn",
                category="research",
                credibility=7,
                update_frequency="daily",
                requires_auth=True
            ),
            
            # 社交媒体（仅监控，可信度低）
            InfoSource(
                name="雪球",
                url="https://xueqiu.com",
                category="social",
                credibility=4,
                update_frequency="continuous"
            ),
            InfoSource(
                name="StockTwits",
                url="https://stocktwits.com",
                category="social",
                credibility=3,
                update_frequency="continuous"
            )
        ]
    
    def fetch_info(self, symbol: str, category: Optional[str] = None,
                   days: int = 7) -> List[AggregatedInfo]:
        """
        获取聚合信息
        
        Args:
            symbol: 股票代码
            category: 信息类别筛选
            days: 最近几天
        
        Returns:
            聚合后的信息列表
        """
        # 这里应该是实际的数据获取逻辑
        # 现在返回模拟数据用于测试
        
        results = []
        
        # 模拟公告信息
        if not category or category == "announcement":
            results.extend(self._mock_announcements(symbol))
        
        # 模拟新闻信息
        if not category or category == "news":
            results.extend(self._mock_news(symbol))
        
        # 模拟研报信息
        if not category or category == "research":
            results.extend(self._mock_research(symbol))
        
        # 按可信度排序
        results.sort(key=lambda x: x.credibility_score, reverse=True)
        
        return results
    
    def _mock_announcements(self, symbol: str) -> List[AggregatedInfo]:
        """模拟公告数据"""
        return [
            AggregatedInfo(
                id=f"ann_{symbol}_001",
                title=f"{symbol} 2026年第一季度报告",
                content="公司2026年第一季度实现营业收入15亿元，同比增长30%；净利润3.5亿元，同比增长25%。",
                source="上交所公告",
                source_url="http://www.sse.com.cn/...",
                publish_time="2026-04-30 18:00:00",
                category="announcement",
                symbols=[symbol],
                credibility_score=10.0,
                verified=True
            ),
            AggregatedInfo(
                id=f"ann_{symbol}_002",
                title=f"{symbol} 关于投资新建生产基地的公告",
                content="公司拟投资10亿元建设新的智能制造基地，预计2027年投产。",
                source="上交所公告",
                source_url="http://www.sse.com.cn/...",
                publish_time="2026-05-01 10:30:00",
                category="announcement",
                symbols=[symbol],
                credibility_score=10.0,
                verified=True
            )
        ]
    
    def _mock_news(self, symbol: str) -> List[AggregatedInfo]:
        """模拟新闻数据"""
        return [
            AggregatedInfo(
                id=f"news_{symbol}_001",
                title=f"{symbol}获机构大额增持 北向资金连续5日净流入",
                content="据最新数据显示，{symbol}本周获北向资金累计净流入5亿元，机构持股比例提升至15%。",
                source="财新网",
                source_url="https://www.caixin.com/...",
                publish_time="2026-05-01 14:20:00",
                category="news",
                symbols=[symbol],
                credibility_score=8.5,
                sentiment="positive"
            ),
            AggregatedInfo(
                id=f"news_{symbol}_002",
                title=f"行业政策利好 {symbol}所在板块迎来发展机遇",
                content="近日工信部发布《智能制造发展规划》，{symbol}作为行业龙头有望受益。",
                source="财新网",
                source_url="https://www.caixin.com/...",
                publish_time="2026-04-29 09:15:00",
                category="news",
                symbols=[symbol],
                credibility_score=8.0,
                sentiment="positive"
            )
        ]
    
    def _mock_research(self, symbol: str) -> List[AggregatedInfo]:
        """模拟研报数据"""
        return [
            AggregatedInfo(
                id=f"res_{symbol}_001",
                title=f"{symbol}：业绩超预期，维持买入评级",
                content="Q1业绩超市场预期，新产能释放将驱动全年高增长。目标价上调至25元。",
                source="中信证券研报",
                source_url="https://data.eastmoney.com/...",
                publish_time="2026-05-01 16:00:00",
                category="research",
                symbols=[symbol],
                credibility_score=7.5,
                sentiment="positive"
            )
        ]
    
    def deduplicate(self, info_list: List[AggregatedInfo]) -> List[AggregatedInfo]:
        """去重"""
        unique_info = []
        seen = set()
        
        for info in info_list:
            # 基于标题和内容的哈希去重
            key = hash(f"{info.title}_{info.content[:100]}")
            if key not in seen:
                seen.add(key)
                unique_info.append(info)
        
        return unique_info
    
    def filter_by_credibility(self, info_list: List[AggregatedInfo],
                             min_score: float = 5.0) -> List[AggregatedInfo]:
        """按可信度过滤"""
        return [info for info in info_list if info.credibility_score >= min_score]
    
    def verify_info(self, info: AggregatedInfo) -> bool:
        """
        验证信息真实性
        
        Returns:
            是否通过验证
        """
        # 官方公告自动通过
        if info.category == "announcement" and info.source in ["上交所公告", "深交所公告", "港交所披露易", "SEC EDGAR"]:
            return True
        
        # 知名财经媒体可信度较高
        if info.source in ["财新网", "华尔街日报", "彭博社", "路透社"] and info.credibility_score >= 8:
            return True
        
        # 其他信息需要交叉验证（简化实现）
        return info.credibility_score >= 6
    
    def generate_aggregator_report(self, symbol: str) -> str:
        """生成聚合报告"""
        info_list = self.fetch_info(symbol)
        
        report = f"""# 📰 信息聚合报告 - {symbol}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**信息总数**: {len(info_list)} 条

---

## 📊 信息来源分布

"""
        
        # 统计来源
        source_count = {}
        for info in info_list:
            source_count[info.source] = source_count.get(info.source, 0) + 1
        
        for source, count in sorted(source_count.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{source}**: {count} 条\n"
        
        report += """
---

## 📋 重要信息

"""
        
        # 只显示高可信度信息
        high_cred_info = [info for info in info_list if info.credibility_score >= 8]
        
        for info in high_cred_info[:10]:  # 最多显示10条
            verified_icon = "✅" if info.verified else "⚠️"
            report += f"""### {verified_icon} {info.title}
- **来源**: {info.source} (可信度: {info.credibility_score}/10)
- **时间**: {info.publish_time}
- **类别**: {info.category}
- **内容**: {info.content[:200]}...

"""
        
        return report

def main():
    """演示"""
    print("=" * 70)
    print("📰 信息聚合器 (Layer 3)")
    print("=" * 70)
    
    aggregator = InfoAggregator()
    
    # 显示信息源
    print("\n📡 已配置信息源:")
    for source in aggregator.sources:
        cred_icon = "⭐" * (source.credibility // 2)
        print(f"  • {source.name} [{source.category}] {cred_icon} ({source.credibility}/10)")
    
    # 测试信息获取
    print("\n🔍 测试信息聚合...")
    info_list = aggregator.fetch_info("000001.SZ")
    print(f"  获取信息: {len(info_list)} 条")
    
    # 显示去重后
    unique_list = aggregator.deduplicate(info_list)
    print(f"  去重后: {len(unique_list)} 条")
    
    # 显示高可信度信息
    high_cred = aggregator.filter_by_credibility(unique_list, min_score=8.0)
    print(f"  高可信度(≥8分): {len(high_cred)} 条")
    
    for info in high_cred:
        verified = "✅" if info.verified else "⚠️"
        print(f"  {verified} [{info.source}] {info.title[:50]}...")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📄 聚合报告:")
    report = aggregator.generate_aggregator_report("000001.SZ")
    print(report[:800] + "...")

if __name__ == "__main__":
    main()
