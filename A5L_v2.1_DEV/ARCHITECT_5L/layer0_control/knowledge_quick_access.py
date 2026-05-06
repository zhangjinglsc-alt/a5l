#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Knowledge Guardian Quick Access
知识库守护者快捷访问接口

提供便捷的全局访问点，所有A5L组件都可以快速存取知识
"""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ARCHITECT_5L.layer0_control.knowledge_guardian import (
    KnowledgeGuardian, 
    KnowledgeItem, 
    TradeRecord,
    ContentType,
    KnowledgeSource
)


# 全局知识库守护者实例
_guardian_instance: Optional[KnowledgeGuardian] = None


def get_guardian() -> KnowledgeGuardian:
    """获取知识库守护者实例 (单例模式)"""
    global _guardian_instance
    if _guardian_instance is None:
        _guardian_instance = KnowledgeGuardian()
    return _guardian_instance


# ==================== 快捷存储函数 ====================

def save_report(file_path: str, 
                title: str, 
                stock_code: str,
                **kwargs) -> KnowledgeItem:
    """
    快捷保存研报
    
    使用示例:
        save_report(
            file_path="report.pdf",
            title="宁德时代深度报告",
            stock_code="300750.SZ",
            source="中金公司",
            rating="买入"
        )
    """
    guardian = get_guardian()
    return guardian.store_research_report(
        file_path=file_path,
        title=title,
        stock_code=stock_code,
        **kwargs
    )


def save_system_file(file_path: str,
                    file_type: str,  # soul/goal/memory/cron/skill
                    version: Optional[str] = None,
                    change_summary: Optional[str] = None,
                    auto_commit_git: bool = True,
                    auto_sync_feishu: bool = True) -> Dict:
    """
    快捷保存系统文件 (SOUL/GOAL/MEMORY/CRON/SKILL)
    
    自动完成：存储 → Git提交 → 飞书同步
    
    使用示例:
        # 保存SOUL更新
        save_system_file(
            file_path="/workspace/SOUL.md",
            file_type="soul",
            version="2.0.0",
            change_summary="添加Knowledge Guardian角色"
        )
        
        # 保存GOAL更新
        save_system_file(
            file_path="/workspace/GOAL.md",
            file_type="goal",
            version="2024.05",
            change_summary="更新进化里程碑"
        )
    """
    guardian = get_guardian()
    
    # 获取标题
    title_map = {
        "soul": "SOUL人格宪章",
        "goal": "目标追踪",
        "memory": "记忆档案",
        "cron": "定时任务",
        "skill": "技能注册表",
        "doc": "系统文档"
    }
    title = title_map.get(file_type, "系统文档")
    
    # 使用自动归档工作流
    from ARCHITECT_5L.layer0_control.knowledge_guardian import ContentType
    
    type_map = {
        "soul": ContentType.SOUL_CONFIG,
        "goal": ContentType.GOAL_TRACKING,
        "memory": ContentType.MEMORY_LOG,
        "cron": ContentType.CRON_TASK,
        "skill": ContentType.SKILL_REGISTRY,
        "doc": ContentType.SYSTEM_DOC
    }
    content_type = type_map.get(file_type, ContentType.SYSTEM_DOC)
    
    # 执行自动归档
    result = guardian.auto_archive_workflow(
        file_path=file_path,
        content_type=content_type,
        title=f"{title} - v{version}" if version else title,
        file_type=file_type,
        version=version,
        change_summary=change_summary
    )
    
    return result


def backup_all_system_files() -> List[str]:
    """
    一键备份所有关键系统文件
    
    使用示例:
        backed_up = backup_all_system_files()
        print(f"已备份 {len(backed_up)} 个文件")
    """
    guardian = get_guardian()
    return guardian.backup_critical_files()


def save_analysis(file_path: str,
                 title: str,
                 stock_code: str,
                 analysis_type: str = "stock",
                 **kwargs) -> KnowledgeItem:
    """
    快捷保存A5L分析
    
    使用示例:
        save_analysis(
            file_path="analysis.md",
            title="宁德时代 - A5L分析",
            stock_code="300750.SZ",
            analysis_type="stock"
        )
    """
    guardian = get_guardian()
    return guardian.store_analysis_report(
        file_path=file_path,
        title=title,
        analysis_type=analysis_type,
        stock_code=stock_code,
        **kwargs
    )


def save_raw(file_path: str,
            title: str,
            content_type: str = "pdf",
            **kwargs) -> KnowledgeItem:
    """
    快捷保存原始资料
    
    使用示例:
        save_raw(
            file_path="image.jpg",
            title="行业图谱",
            content_type="image"
        )
    """
    guardian = get_guardian()
    
    type_map = {
        "pdf": ContentType.PDF_DOCUMENT,
        "image": ContentType.IMAGE,
        "article": ContentType.ARTICLE,
        "wechat": ContentType.WECHAT_ARTICLE,
        "news": ContentType.NEWS
    }
    
    ct = type_map.get(content_type, ContentType.PDF_DOCUMENT)
    
    return guardian.store_raw_content(
        content_type=ct,
        file_path=file_path,
        title=title,
        **kwargs
    )


def save_trade(trade_data: Dict, trade_type: str = "real") -> TradeRecord:
    """
    快捷保存交易记录
    
    使用示例:
        save_trade({
            "account_id": "REAL_001",
            "symbol": "300750.SZ",
            "trade_date": "2024-05-02",
            "action": "BUY",
            "quantity": 100,
            "price": 185.50
        }, trade_type="real")
    """
    guardian = get_guardian()
    return guardian.store_trade_record(trade_data, trade_type)


# ==================== 快捷检索函数 ====================

def find_reports(stock_code: Optional[str] = None, 
                keyword: Optional[str] = None,
                limit: int = 50) -> List[KnowledgeItem]:
    """
    快捷查找研报
    
    使用示例:
        find_reports(stock_code="300750.SZ")
        find_reports(keyword="新能源")
    """
    guardian = get_guardian()
    return guardian.search_knowledge(
        stock_code=stock_code,
        keyword=keyword,
        content_type=ContentType.RESEARCH_REPORT,
        limit=limit
    )


def find_analysis(stock_code: Optional[str] = None,
                 limit: int = 50) -> List[KnowledgeItem]:
    """快捷查找A5L分析"""
    guardian = get_guardian()
    return guardian.search_knowledge(
        stock_code=stock_code,
        content_type=ContentType.STOCK_ANALYSIS,
        limit=limit
    )


def find_trades(symbol: Optional[str] = None,
               trade_type: str = "real",
               limit: int = 100) -> List[TradeRecord]:
    """
    快捷查找交易记录
    
    使用示例:
        find_trades(symbol="300750.SZ", trade_type="real")
        find_trades(trade_type="simulated")
    """
    guardian = get_guardian()
    return guardian.search_trades(
        symbol=symbol,
        trade_type=trade_type
    )[:limit]


def get_item(item_id: str) -> Optional[KnowledgeItem]:
    """通过ID获取知识条目"""
    guardian = get_guardian()
    return guardian.get_knowledge_by_id(item_id)


def get_trade(record_id: str) -> Optional[TradeRecord]:
    """通过ID获取交易记录"""
    guardian = get_guardian()
    return guardian.get_trade_by_id(record_id)


# ==================== 快捷统计函数 ====================

def stats() -> Dict:
    """快捷获取知识库统计"""
    guardian = get_guardian()
    return {
        "knowledge": guardian.get_knowledge_stats(),
        "real_trades": guardian.get_trade_stats("real"),
        "simulated_trades": guardian.get_trade_stats("simulated")
    }


def recent_items(limit: int = 10) -> List[KnowledgeItem]:
    """获取最近添加的知识"""
    guardian = get_guardian()
    kb_stats = guardian.get_knowledge_stats()
    return [KnowledgeItem(**item) for item in kb_stats.get("recent_items", [])[:limit]]


# ==================== 装饰器 (自动归档) ====================

def auto_archive(content_type: str = "analysis"):
    """
    装饰器：自动归档函数结果
    
    使用示例:
        @auto_archive(content_type="analysis")
        def analyze_stock(stock_code):
            # 分析逻辑
            return {"file_path": "...", "title": "...", "stock_code": "..."}
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 自动归档
            try:
                guardian = get_guardian()
                
                if content_type == "analysis":
                    guardian.store_analysis_report(
                        file_path=result.get('file_path'),
                        title=result.get('title'),
                        analysis_type=result.get('analysis_type', 'stock'),
                        stock_code=result.get('stock_code'),
                        industry=result.get('industry')
                    )
                elif content_type == "trade":
                    guardian.store_trade_record(
                        result,
                        trade_type=result.get('trade_type', 'real')
                    )
                    
            except Exception as e:
                print(f"⚠️ Auto archive failed: {e}")
            
            return result
        return wrapper
    return decorator


# ==================== 便捷类 ====================

class KnowledgeQuery:
    """知识查询便捷类"""
    
    def __init__(self):
        self.guardian = get_guardian()
    
    def by_stock(self, stock_code: str):
        """查询某股票的所有知识"""
        return self.guardian.search_knowledge(stock_code=stock_code)
    
    def by_industry(self, industry: str):
        """查询某行业的所有知识"""
        return self.guardian.search_knowledge(industry=industry)
    
    def by_type(self, content_type: ContentType):
        """查询某类型的所有知识"""
        return self.guardian.search_knowledge(content_type=content_type)
    
    def trades_by_symbol(self, symbol: str, trade_type: str = "real"):
        """查询某股票的交易记录"""
        return self.guardian.search_trades(symbol=symbol, trade_type=trade_type)


# 全局查询实例
query = KnowledgeQuery()


if __name__ == "__main__":
    print("=" * 80)
    print("📚 Knowledge Guardian Quick Access - Test")
    print("=" * 80)
    
    # 测试快捷函数
    print("\n[1/4] Testing quick save functions...")
    
    # 创建测试文件
    import os
    os.makedirs("/tmp/test_kb", exist_ok=True)
    with open("/tmp/test_kb/report.md", 'w') as f:
        f.write("# 测试研报")
    
    # 测试保存
    item = save_report(
        file_path="/tmp/test_kb/report.md",
        title="测试研报",
        stock_code="300750.SZ",
        source="测试"
    )
    print(f"✅ Saved report: {item.title}")
    
    # 测试快捷查询
    print("\n[2/4] Testing quick query...")
    results = find_reports(stock_code="300750.SZ")
    print(f"✅ Found {len(results)} reports")
    
    # 测试全局查询
    print("\n[3/4] Testing KnowledgeQuery...")
    items = query.by_stock("300750.SZ")
    print(f"✅ Query by stock: {len(items)} items")
    
    # 测试统计
    print("\n[4/4] Testing stats...")
    s = stats()
    print(f"✅ Knowledge: {s['knowledge']['total_items']} items")
    
    print("\n" + "=" * 80)
    print("✅ Quick Access test completed!")
