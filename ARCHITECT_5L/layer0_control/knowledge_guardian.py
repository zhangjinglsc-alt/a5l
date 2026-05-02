#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Knowledge Guardian - Layer0 Control
知识库守护者 - L0层图书馆管理员

职责:
1. 统一管理所有投研资料 (研报/文章/图片/PDF/公众号)
2. 归档A5L生成的分析 (行业/个股/策略)
3. 管理真实交易记录
4. 管理模拟交易记录
5. 提供快速检索和调阅接口
6. 飞书/KIWI深度集成

位置: Layer0 - Meta Control Layer
角色: Chief Librarian / Knowledge Guardian
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """内容类型枚举"""
    # 投研资料
    RESEARCH_REPORT = "research_report"      # 券商研报
    INDUSTRY_ANALYSIS = "industry_analysis"  # 行业分析
    STOCK_ANALYSIS = "stock_analysis"        # 个股分析
    MARKET_COMMENTARY = "market_commentary"  # 市场点评
    
    # 原始资料
    PDF_DOCUMENT = "pdf_document"            # PDF文档
    IMAGE = "image"                          # 图片
    ARTICLE = "article"                      # 文章
    WECHAT_ARTICLE = "wechat_article"        # 公众号文章
    NEWS = "news"                            # 新闻
    
    # 交易记录
    REAL_TRADE = "real_trade"                # 真实交易
    SIMULATED_TRADE = "simulated_trade"      # 模拟交易
    PORTFOLIO_SNAPSHOT = "portfolio_snapshot" # 持仓快照
    
    # 系统生成
    STRATEGY_REPORT = "strategy_report"      # 策略报告
    REVIEW_REPORT = "review_report"          # 复盘报告
    ALERT_LOG = "alert_log"                  # 告警记录


class KnowledgeSource(Enum):
    """知识来源"""
    USER_UPLOAD = "user_upload"              # 用户上传
    A5L_GENERATED = "a5l_generated"          # A5L生成
    EXTERNAL_IMPORT = "external_import"      # 外部导入
    AUTO_COLLECTED = "auto_collected"        # 自动采集


@dataclass
class KnowledgeItem:
    """知识条目数据模型"""
    # 基础信息
    item_id: str
    title: str
    content_type: str
    source: str
    
    # 内容信息
    content: Optional[str] = None            # 文本内容
    file_path: Optional[str] = None          # 文件路径
    file_size: int = 0
    file_hash: Optional[str] = None          # 文件哈希
    
    # 关联信息
    stock_code: Optional[str] = None         # 关联股票
    stock_name: Optional[str] = None
    industry: Optional[str] = None           # 关联行业
    tags: List[str] = field(default_factory=list)
    
    # 时间信息
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    content_date: Optional[str] = None       # 内容日期 (研报日期/交易日期)
    
    # 元数据
    author: Optional[str] = None
    source_url: Optional[str] = None         # 原始链接
    feishu_url: Optional[str] = None         # 飞书链接
    kiwi_url: Optional[str] = None           # KIWI链接
    
    # 访问统计
    access_count: int = 0
    last_accessed: Optional[str] = None
    
    # 状态
    is_archived: bool = False
    is_important: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TradeRecord:
    """交易记录数据模型"""
    record_id: str
    trade_type: str                          # real / simulated
    account_id: str                          # 账户ID
    
    # 交易信息
    symbol: str
    trade_date: str
    trade_time: str
    action: str                              # BUY / SELL
    quantity: int
    price: float
    amount: float
    
    # 额外信息
    strategy: Optional[str] = None           # 关联策略
    reason: Optional[str] = None             # 交易理由
    fees: float = 0.0                        # 手续费
    pnl: Optional[float] = None              # 盈亏 (卖出时)
    pnl_pct: Optional[float] = None          # 盈亏比例
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class KnowledgeGuardian:
    """
    知识库守护者 - Layer0核心组件
    
    职责:
    1. 知识采集 - 接收并存储各类知识
    2. 知识组织 - 分类、标签、归档
    3. 知识检索 - 快速查找和调阅
    4. 知识同步 - 飞书/KIWI同步
    5. 知识维护 - 定期清理和更新
    
    使用示例:
        guardian = KnowledgeGuardian()
        
        # 存储研报
        item = guardian.store_research_report(
            file_path="report.pdf",
            title="宁德时代深度报告",
            stock_code="300750.SZ"
        )
        
        # 存储交易记录
        trade = guardian.store_trade_record(
            trade_data={...},
            trade_type="real"
        )
        
        # 搜索知识
        results = guardian.search(
            stock_code="300750.SZ",
            content_type=ContentType.RESEARCH_REPORT
        )
    """
    
    def __init__(self, base_path: str = "/workspace/projects/workspace/knowledge_base"):
        self.base_path = Path(base_path)
        self.index_path = self.base_path / ".index"
        
        # 初始化目录结构
        self._init_knowledge_base()
        
        # 加载索引
        self.knowledge_index: Dict[str, KnowledgeItem] = {}
        self.trade_index: Dict[str, TradeRecord] = {}
        self._load_indexes()
        
        logger.info(f"📚 Knowledge Guardian initialized at {base_path}")
    
    def _init_knowledge_base(self):
        """初始化知识库目录结构"""
        directories = {
            # 投研资料
            "research/reports": "券商研报",
            "research/industry": "行业分析",
            "research/stock": "个股分析",
            "research/market": "市场点评",
            
            # 原始资料
            "raw/pdf": "PDF文档",
            "raw/images": "图片资料",
            "raw/articles": "网络文章",
            "raw/wechat": "公众号文章",
            "raw/news": "新闻资讯",
            
            # 交易记录
            "trades/real": "真实交易",
            "trades/simulated": "模拟交易",
            "trades/portfolio": "持仓快照",
            
            # 系统生成
            "system/strategy": "策略报告",
            "system/review": "复盘报告",
            "system/alerts": "告警记录",
            
            # 索引和元数据
            ".index": "索引数据",
            ".metadata": "元数据"
        }
        
        for dir_path, desc in directories.items():
            (self.base_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Initialized {len(directories)} knowledge directories")
    
    def _load_indexes(self):
        """加载索引"""
        # 知识条目索引
        knowledge_index_file = self.index_path / "knowledge.json"
        if knowledge_index_file.exists():
            try:
                with open(knowledge_index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item_id, item_data in data.items():
                        self.knowledge_index[item_id] = KnowledgeItem(**item_data)
                logger.info(f"📚 Loaded {len(self.knowledge_index)} knowledge items")
            except Exception as e:
                logger.error(f"❌ Failed to load knowledge index: {e}")
        
        # 交易记录索引
        trade_index_file = self.index_path / "trades.json"
        if trade_index_file.exists():
            try:
                with open(trade_index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for record_id, record_data in data.items():
                        self.trade_index[record_id] = TradeRecord(**record_data)
                logger.info(f"💼 Loaded {len(self.trade_index)} trade records")
            except Exception as e:
                logger.error(f"❌ Failed to load trade index: {e}")
    
    def _save_indexes(self):
        """保存索引"""
        # 保存知识索引
        knowledge_index_file = self.index_path / "knowledge.json"
        try:
            data = {item_id: item.to_dict() for item_id, item in self.knowledge_index.items()}
            with open(knowledge_index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save knowledge index: {e}")
        
        # 保存交易索引
        trade_index_file = self.index_path / "trades.json"
        try:
            data = {record_id: record.to_dict() for record_id, record in self.trade_index.items()}
            with open(trade_index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save trade index: {e}")
    
    def _generate_id(self, prefix: str = "") -> str:
        """生成唯一ID"""
        content = f"{prefix}_{datetime.now().isoformat()}"
        return f"{prefix}_{hashlib.md5(content.encode()).hexdigest()[:10]}"
    
    def _get_storage_path(self, content_type: ContentType, sub_path: str = "") -> Path:
        """获取存储路径"""
        type_path_map = {
            ContentType.RESEARCH_REPORT: "research/reports",
            ContentType.INDUSTRY_ANALYSIS: "research/industry",
            ContentType.STOCK_ANALYSIS: "research/stock",
            ContentType.MARKET_COMMENTARY: "research/market",
            ContentType.PDF_DOCUMENT: "raw/pdf",
            ContentType.IMAGE: "raw/images",
            ContentType.ARTICLE: "raw/articles",
            ContentType.WECHAT_ARTICLE: "raw/wechat",
            ContentType.NEWS: "raw/news",
            ContentType.STRATEGY_REPORT: "system/strategy",
            ContentType.REVIEW_REPORT: "system/review",
            ContentType.ALERT_LOG: "system/alerts",
        }
        
        base = type_path_map.get(content_type, "raw/other")
        return self.base_path / base / sub_path
    
    # ==================== 知识采集接口 ====================
    
    def store_knowledge(self,
                       content_type: ContentType,
                       title: str,
                       source: KnowledgeSource,
                       content: Optional[str] = None,
                       file_path: Optional[str] = None,
                       stock_code: Optional[str] = None,
                       stock_name: Optional[str] = None,
                       industry: Optional[str] = None,
                       tags: List[str] = None,
                       author: Optional[str] = None,
                       source_url: Optional[str] = None,
                       content_date: Optional[str] = None,
                       auto_sync_feishu: bool = False,
                       auto_sync_kiwi: bool = False) -> KnowledgeItem:
        """
        通用知识存储接口
        
        Args:
            content_type: 内容类型
            title: 标题
            source: 知识来源
            content: 文本内容
            file_path: 文件路径
            stock_code: 关联股票
            stock_name: 股票名称
            industry: 关联行业
            tags: 标签列表
            author: 作者
            source_url: 原始链接
            content_date: 内容日期
            auto_sync_feishu: 自动同步飞书
            auto_sync_kiwi: 自动同步KIWI
            
        Returns:
            KnowledgeItem: 知识条目
        """
        # 生成ID
        item_id = self._generate_id(content_type.value)
        
        # 创建知识条目
        item = KnowledgeItem(
            item_id=item_id,
            title=title,
            content_type=content_type.value,
            source=source.value,
            content=content,
            file_path=file_path,
            stock_code=stock_code,
            stock_name=stock_name,
            industry=industry,
            tags=tags or [],
            author=author,
            source_url=source_url,
            content_date=content_date
        )
        
        # 保存到索引
        self.knowledge_index[item_id] = item
        self._save_indexes()
        
        # 自动同步
        if auto_sync_feishu:
            self._sync_to_feishu(item)
        if auto_sync_kiwi:
            self._sync_to_kiwi(item)
        
        logger.info(f"✅ Stored knowledge: {title} ({item_id})")
        return item
    
    def store_research_report(self,
                             file_path: str,
                             title: str,
                             stock_code: Optional[str] = None,
                             stock_name: Optional[str] = None,
                             source: str = "Unknown",
                             rating: Optional[str] = None,
                             industry: Optional[str] = None,
                             **kwargs) -> KnowledgeItem:
        """存储研报"""
        tags = [rating] if rating else []
        
        return self.store_knowledge(
            content_type=ContentType.RESEARCH_REPORT,
            title=title,
            source=KnowledgeSource.USER_UPLOAD if kwargs.get('from_user') else KnowledgeSource.EXTERNAL_IMPORT,
            file_path=file_path,
            stock_code=stock_code,
            stock_name=stock_name,
            industry=industry,
            tags=tags,
            author=source,
            **kwargs
        )
    
    def store_analysis_report(self,
                             file_path: str,
                             title: str,
                             analysis_type: str,  # stock / industry
                             stock_code: Optional[str] = None,
                             industry: Optional[str] = None,
                             **kwargs) -> KnowledgeItem:
        """存储A5L生成的分析报告"""
        content_type = ContentType.STOCK_ANALYSIS if analysis_type == "stock" else ContentType.INDUSTRY_ANALYSIS
        
        return self.store_knowledge(
            content_type=content_type,
            title=title,
            source=KnowledgeSource.A5L_GENERATED,
            file_path=file_path,
            stock_code=stock_code,
            industry=industry,
            tags=["A5L生成", analysis_type],
            **kwargs
        )
    
    def store_raw_content(self,
                         content_type: ContentType,
                         file_path: str,
                         title: str,
                         source_url: Optional[str] = None,
                         **kwargs) -> KnowledgeItem:
        """存储原始内容 (图片/PDF/文章)"""
        return self.store_knowledge(
            content_type=content_type,
            title=title,
            source=KnowledgeSource.USER_UPLOAD,
            file_path=file_path,
            source_url=source_url,
            tags=["原始资料"],
            **kwargs
        )
    
    # ==================== 交易记录接口 ====================
    
    def store_trade_record(self,
                          trade_data: Dict,
                          trade_type: str = "real") -> TradeRecord:
        """
        存储交易记录
        
        Args:
            trade_data: 交易数据字典
            trade_type: real / simulated
            
        Returns:
            TradeRecord: 交易记录
        """
        record_id = self._generate_id(f"trade_{trade_type}")
        
        record = TradeRecord(
            record_id=record_id,
            trade_type=trade_type,
            account_id=trade_data.get('account_id', 'unknown'),
            symbol=trade_data['symbol'],
            trade_date=trade_data['trade_date'],
            trade_time=trade_data.get('trade_time', ''),
            action=trade_data['action'],
            quantity=trade_data['quantity'],
            price=trade_data['price'],
            amount=trade_data.get('amount', trade_data['quantity'] * trade_data['price']),
            strategy=trade_data.get('strategy'),
            reason=trade_data.get('reason'),
            fees=trade_data.get('fees', 0),
            pnl=trade_data.get('pnl'),
            pnl_pct=trade_data.get('pnl_pct'),
            tags=trade_data.get('tags', [])
        )
        
        # 保存到索引
        self.trade_index[record_id] = record
        self._save_indexes()
        
        # 保存详细记录到文件
        self._save_trade_to_file(record)
        
        logger.info(f"💼 Stored trade record: {record.symbol} {record.action} ({record_id})")
        return record
    
    def _save_trade_to_file(self, record: TradeRecord):
        """保存交易记录到文件"""
        # 按年月组织
        year_month = record.trade_date[:7]
        trade_dir = self.base_path / "trades" / record.trade_type / year_month
        trade_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存为JSON
        file_path = trade_dir / f"{record.record_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(record.to_dict(), f, ensure_ascii=False, indent=2)
    
    # ==================== 知识检索接口 ====================
    
    def search_knowledge(self,
                        keyword: Optional[str] = None,
                        content_type: Optional[ContentType] = None,
                        stock_code: Optional[str] = None,
                        industry: Optional[str] = None,
                        tags: List[str] = None,
                        source: Optional[KnowledgeSource] = None,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        limit: int = 50) -> List[KnowledgeItem]:
        """
        搜索知识条目
        
        支持多维度组合筛选，返回匹配的知识条目列表
        """
        results = []
        
        for item in self.knowledge_index.values():
            # 关键词匹配
            if keyword and keyword.lower() not in item.title.lower():
                if not item.content or keyword.lower() not in item.content.lower():
                    continue
            
            # 内容类型匹配
            if content_type and item.content_type != content_type.value:
                continue
            
            # 股票代码匹配
            if stock_code and item.stock_code != stock_code:
                continue
            
            # 行业匹配
            if industry and item.industry != industry:
                continue
            
            # 标签匹配
            if tags and not all(tag in item.tags for tag in tags):
                continue
            
            # 来源匹配
            if source and item.source != source.value:
                continue
            
            # 日期范围匹配
            if start_date and item.content_date and item.content_date < start_date:
                continue
            if end_date and item.content_date and item.content_date > end_date:
                continue
            
            results.append(item)
        
        # 按时间排序
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        logger.info(f"🔍 Found {len(results)} knowledge items")
        return results[:limit]
    
    def search_trades(self,
                     symbol: Optional[str] = None,
                     trade_type: Optional[str] = None,
                     action: Optional[str] = None,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     strategy: Optional[str] = None) -> List[TradeRecord]:
        """搜索交易记录"""
        results = []
        
        for record in self.trade_index.values():
            if symbol and record.symbol != symbol:
                continue
            if trade_type and record.trade_type != trade_type:
                continue
            if action and record.action != action:
                continue
            if start_date and record.trade_date < start_date:
                continue
            if end_date and record.trade_date > end_date:
                continue
            if strategy and record.strategy != strategy:
                continue
            
            results.append(record)
        
        # 按日期排序
        results.sort(key=lambda x: x.trade_date, reverse=True)
        
        logger.info(f"💼 Found {len(results)} trade records")
        return results
    
    def get_knowledge_by_id(self, item_id: str) -> Optional[KnowledgeItem]:
        """通过ID获取知识条目"""
        item = self.knowledge_index.get(item_id)
        if item:
            # 更新访问统计
            item.access_count += 1
            item.last_accessed = datetime.now().isoformat()
            self._save_indexes()
        return item
    
    def get_trade_by_id(self, record_id: str) -> Optional[TradeRecord]:
        """通过ID获取交易记录"""
        return self.trade_index.get(record_id)
    
    # ==================== 知识组织接口 ====================
    
    def tag_knowledge(self, item_id: str, tags: List[str]):
        """为知识条目添加标签"""
        if item_id in self.knowledge_index:
            item = self.knowledge_index[item_id]
            for tag in tags:
                if tag not in item.tags:
                    item.tags.append(tag)
            item.updated_at = datetime.now().isoformat()
            self._save_indexes()
            logger.info(f"🏷️ Tagged {item_id}: {tags}")
    
    def mark_important(self, item_id: str, important: bool = True):
        """标记知识重要性"""
        if item_id in self.knowledge_index:
            item = self.knowledge_index[item_id]
            item.is_important = important
            item.updated_at = datetime.now().isoformat()
            self._save_indexes()
            logger.info(f"⭐ Marked {item_id} as {'important' if important else 'normal'}")
    
    def archive_knowledge(self, item_id: str):
        """归档知识条目"""
        if item_id in self.knowledge_index:
            item = self.knowledge_index[item_id]
            item.is_archived = True
            item.updated_at = datetime.now().isoformat()
            self._save_indexes()
            logger.info(f"📦 Archived {item_id}")
    
    # ==================== 统计分析接口 ====================
    
    def get_knowledge_stats(self) -> Dict:
        """获取知识库统计"""
        stats = {
            "total_items": len(self.knowledge_index),
            "by_type": {},
            "by_source": {},
            "by_industry": {},
            "by_month": {},
            "important_items": 0,
            "archived_items": 0,
            "stocks_covered": set(),
            "recent_items": []
        }
        
        for item in self.knowledge_index.values():
            # 类型统计
            stats["by_type"][item.content_type] = stats["by_type"].get(item.content_type, 0) + 1
            
            # 来源统计
            stats["by_source"][item.source] = stats["by_source"].get(item.source, 0) + 1
            
            # 行业统计
            if item.industry:
                stats["by_industry"][item.industry] = stats["by_industry"].get(item.industry, 0) + 1
            
            # 月度统计
            month = item.created_at[:7]
            stats["by_month"][month] = stats["by_month"].get(month, 0) + 1
            
            # 重要/归档统计
            if item.is_important:
                stats["important_items"] += 1
            if item.is_archived:
                stats["archived_items"] += 1
            
            # 覆盖股票
            if item.stock_code:
                stats["stocks_covered"].add(item.stock_code)
        
        # 最近添加的条目
        recent = sorted(self.knowledge_index.values(), key=lambda x: x.created_at, reverse=True)[:10]
        stats["recent_items"] = [item.to_dict() for item in recent]
        
        stats["stocks_covered"] = len(stats["stocks_covered"])
        
        return stats
    
    def get_trade_stats(self, trade_type: Optional[str] = None) -> Dict:
        """获取交易统计"""
        stats = {
            "total_trades": 0,
            "total_buy": 0,
            "total_sell": 0,
            "total_pnl": 0.0,
            "by_symbol": {},
            "by_strategy": {},
            "by_month": {}
        }
        
        for record in self.trade_index.values():
            if trade_type and record.trade_type != trade_type:
                continue
            
            stats["total_trades"] += 1
            
            if record.action == "BUY":
                stats["total_buy"] += 1
            else:
                stats["total_sell"] += 1
            
            if record.pnl:
                stats["total_pnl"] += record.pnl
            
            # 按股票统计
            if record.symbol not in stats["by_symbol"]:
                stats["by_symbol"][record.symbol] = {"count": 0, "pnl": 0.0}
            stats["by_symbol"][record.symbol]["count"] += 1
            if record.pnl:
                stats["by_symbol"][record.symbol]["pnl"] += record.pnl
            
            # 按策略统计
            if record.strategy:
                stats["by_strategy"][record.strategy] = stats["by_strategy"].get(record.strategy, 0) + 1
            
            # 按月份统计
            month = record.trade_date[:7]
            stats["by_month"][month] = stats["by_month"].get(month, 0) + 1
        
        return stats
    
    # ==================== 同步接口 (占位) ====================
    
    def _sync_to_feishu(self, item: KnowledgeItem):
        """同步到飞书"""
        # TODO: 实现飞书同步
        logger.info(f"☁️ Sync to Feishu: {item.title}")
    
    def _sync_to_kiwi(self, item: KnowledgeItem):
        """同步到KIWI"""
        # TODO: 实现KIWI同步
        logger.info(f"🥝 Sync to KIWI: {item.title}")
    
    def export_to_feishu(self, item_ids: List[str] = None):
        """导出到飞书"""
        if item_ids is None:
            items = list(self.knowledge_index.values())
        else:
            items = [self.knowledge_index.get(id) for id in item_ids if id in self.knowledge_index]
        
        for item in items:
            self._sync_to_feishu(item)
        
        logger.info(f"☁️ Exported {len(items)} items to Feishu")


def main():
    """测试知识库守护者"""
    print("=" * 80)
    print("📚 Knowledge Guardian - Layer0 Control - Test")
    print("=" * 80)
    
    # 初始化守护者
    guardian = KnowledgeGuardian(base_path="/tmp/test_knowledge_base")
    
    # 测试存储研报
    print("\n[1/6] Testing research report storage...")
    report = guardian.store_research_report(
        file_path="/tmp/test_report.pdf",
        title="宁德时代深度研究报告",
        stock_code="300750.SZ",
        stock_name="宁德时代",
        source="中金公司",
        rating="买入",
        industry="新能源"
    )
    print(f"✅ Stored: {report.title}")
    
    # 测试存储分析
    print("\n[2/6] Testing analysis storage...")
    analysis = guardian.store_analysis_report(
        file_path="/tmp/test_analysis.md",
        title="宁德时代 - A5L智能分析",
        analysis_type="stock",
        stock_code="300750.SZ",
        industry="新能源"
    )
    print(f"✅ Stored: {analysis.title}")
    
    # 测试存储原始内容
    print("\n[3/6] Testing raw content storage...")
    raw = guardian.store_raw_content(
        content_type=ContentType.PDF_DOCUMENT,
        file_path="/tmp/test_pdf.pdf",
        title="行业研究资料",
        source_url="https://example.com/report.pdf"
    )
    print(f"✅ Stored: {raw.title}")
    
    # 测试存储交易记录
    print("\n[4/6] Testing trade record storage...")
    trade = guardian.store_trade_record({
        "account_id": "REAL_001",
        "symbol": "300750.SZ",
        "trade_date": "2024-05-02",
        "trade_time": "14:30:00",
        "action": "BUY",
        "quantity": 100,
        "price": 185.50,
        "strategy": "价值投资",
        "reason": "低于内在价值"
    }, trade_type="real")
    print(f"✅ Stored trade: {trade.symbol} {trade.action}")
    
    # 测试搜索
    print("\n[5/6] Testing knowledge search...")
    results = guardian.search_knowledge(stock_code="300750.SZ")
    print(f"✅ Found {len(results)} items for 300750.SZ")
    
    # 测试统计
    print("\n[6/6] Testing statistics...")
    kb_stats = guardian.get_knowledge_stats()
    trade_stats = guardian.get_trade_stats()
    print(f"✅ Knowledge: {kb_stats['total_items']} items")
    print(f"✅ Trades: {trade_stats['total_trades']} records")
    
    print("\n" + "=" * 80)
    print("✅ Knowledge Guardian test completed!")


if __name__ == "__main__":
    main()
