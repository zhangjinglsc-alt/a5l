#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A5L Research Report Manager SKILL
研报管理与文件组织系统

功能:
1. 研报自动分类归档
2. 研报全文检索
3. 研报标签管理
4. 研报摘要提取
5. 飞书云文档同步
6. 研报版本控制
"""

import os
import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ResearchReport:
    """研报数据模型"""
    report_id: str
    title: str
    stock_code: Optional[str]
    stock_name: Optional[str]
    author: str
    source: str  # 研报来源: 券商/机构
    report_date: str
    rating: Optional[str]  # 评级: 买入/增持/中性/减持
    target_price: Optional[float]
    industry: Optional[str]  # 行业分类
    tags: List[str]
    file_path: str
    file_type: str  # pdf/docx/md
    file_size: int
    created_at: str
    summary: Optional[str] = None
    key_points: List[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ReportFolder:
    """研报文件夹"""
    folder_id: str
    name: str
    path: str
    parent_id: Optional[str]
    report_count: int
    created_at: str


class ReportCategory:
    """研报分类体系"""
    
    # 按股票分类
    BY_STOCK = "by_stock"  # 按股票代码分类
    
    # 按行业分类
    BY_INDUSTRY = "by_industry"  # 按行业分类
    
    # 按时间分类
    BY_DATE = "by_date"  # 按日期分类
    
    # 按评级分类
    BY_RATING = "by_rating"  # 按评级分类
    
    # 按来源分类
    BY_SOURCE = "by_source"  # 按研报来源分类
    
    # 预定义行业分类
    INDUSTRIES = [
        "半导体", "新能源", "医药生物", "消费电子",
        "人工智能", "金融科技", "新能源汽车", "光伏",
        "军工", "化工", "食品饮料", "银行",
        "房地产", "传媒", "通信", "其他"
    ]
    
    # 预定义评级分类
    RATINGS = ["买入", "增持", "中性", "减持", "卖出"]
    
    # 预定义来源分类
    SOURCES = [
        "中金公司", "中信证券", "华泰证券", "国泰君安",
        "招商证券", "广发证券", "海通证券", "兴业证券",
        "天风证券", "东方证券", "其他券商", "机构研报"
    ]


class ResearchReportManager:
    """
    研报管理核心类
    
    使用示例:
        manager = ResearchReportManager()
        
        # 添加研报
        report = manager.add_report(
            file_path="report.pdf",
            title="宁德时代深度报告",
            stock_code="300750.SZ",
            source="中金公司",
            rating="买入"
        )
        
        # 搜索研报
        results = manager.search_reports(stock_code="300750.SZ")
        
        # 分类归档
        manager.organize_reports(category=ReportCategory.BY_STOCK)
    """
    
    def __init__(self, base_path: str = "/workspace/projects/workspace/output/reports"):
        self.base_path = Path(base_path)
        self.metadata_path = self.base_path / ".metadata"
        self.index_path = self.base_path / ".index"
        
        # 初始化目录结构
        self._init_directories()
        
        # 加载索引
        self.report_index: Dict[str, ResearchReport] = {}
        self._load_index()
        
        logger.info(f"📁 Research Report Manager initialized at {base_path}")
    
    def _init_directories(self):
        """初始化目录结构"""
        dirs = [
            self.base_path / "by_stock",      # 按股票分类
            self.base_path / "by_industry",   # 按行业分类
            self.base_path / "by_date",       # 按日期分类
            self.base_path / "by_rating",     # 按评级分类
            self.base_path / "by_source",     # 按来源分类
            self.base_path / "archive",       # 归档文件夹
            self.metadata_path,                # 元数据
            self.index_path                    # 索引
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _load_index(self):
        """加载研报索引"""
        index_file = self.index_path / "reports.json"
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for report_id, report_data in data.items():
                        self.report_index[report_id] = ResearchReport(**report_data)
                logger.info(f"📚 Loaded {len(self.report_index)} reports from index")
            except Exception as e:
                logger.error(f"❌ Failed to load index: {e}")
    
    def _save_index(self):
        """保存研报索引"""
        index_file = self.index_path / "reports.json"
        try:
            data = {rid: r.to_dict() for rid, r in self.report_index.items()}
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save index: {e}")
    
    def _generate_report_id(self, file_path: str) -> str:
        """生成研报唯一ID"""
        content = f"{file_path}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def add_report(self, 
                   file_path: str,
                   title: str,
                   stock_code: Optional[str] = None,
                   stock_name: Optional[str] = None,
                   author: str = "Unknown",
                   source: str = "Unknown",
                   report_date: Optional[str] = None,
                   rating: Optional[str] = None,
                   target_price: Optional[float] = None,
                   industry: Optional[str] = None,
                   tags: List[str] = None,
                   auto_organize: bool = True) -> ResearchReport:
        """
        添加研报到管理系统
        
        Args:
            file_path: 研报文件路径
            title: 研报标题
            stock_code: 股票代码 (如: 300750.SZ)
            stock_name: 股票名称
            author: 分析师
            source: 研报来源 (券商/机构)
            report_date: 研报日期 (YYYY-MM-DD)
            rating: 评级 (买入/增持/中性/减持)
            target_price: 目标价
            industry: 行业分类
            tags: 自定义标签
            auto_organize: 是否自动分类归档
            
        Returns:
            ResearchReport: 研报对象
        """
        # 检查文件
        src_path = Path(file_path)
        if not src_path.exists():
            raise FileNotFoundError(f"Report file not found: {file_path}")
        
        # 生成研报ID
        report_id = self._generate_report_id(str(file_path))
        
        # 解析日期
        if report_date is None:
            report_date = datetime.now().strftime("%Y-%m-%d")
        
        # 创建研报对象
        report = ResearchReport(
            report_id=report_id,
            title=title,
            stock_code=stock_code,
            stock_name=stock_name,
            author=author,
            source=source,
            report_date=report_date,
            rating=rating,
            target_price=target_price,
            industry=industry,
            tags=tags or [],
            file_path=str(src_path),
            file_type=src_path.suffix.lower(),
            file_size=src_path.stat().st_size,
            created_at=datetime.now().isoformat()
        )
        
        # 保存到索引
        self.report_index[report_id] = report
        self._save_index()
        
        # 自动分类归档
        if auto_organize:
            self._organize_single_report(report)
        
        logger.info(f"✅ Added report: {title} ({report_id})")
        return report
    
    def _organize_single_report(self, report: ResearchReport):
        """归档单个研报"""
        # 按股票归档
        if report.stock_code:
            self._create_symlink(
                report.file_path,
                self.base_path / "by_stock" / report.stock_code / f"{report.report_id}{report.file_type}"
            )
        
        # 按行业归档
        if report.industry:
            self._create_symlink(
                report.file_path,
                self.base_path / "by_industry" / report.industry / f"{report.report_id}{report.file_type}"
            )
        
        # 按日期归档
        year_month = report.report_date[:7]  # YYYY-MM
        self._create_symlink(
            report.file_path,
            self.base_path / "by_date" / year_month / f"{report.report_id}{report.file_type}"
        )
        
        # 按评级归档
        if report.rating:
            self._create_symlink(
                report.file_path,
                self.base_path / "by_rating" / report.rating / f"{report.report_id}{report.file_type}"
            )
        
        # 按来源归档
        if report.source:
            self._create_symlink(
                report.file_path,
                self.base_path / "by_source" / report.source / f"{report.report_id}{report.file_type}"
            )
    
    def _create_symlink(self, src: str, dst: Path):
        """创建符号链接"""
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() or dst.is_symlink():
            dst.unlink()
        try:
            os.symlink(src, dst)
        except Exception as e:
            # 如果符号链接失败，复制文件
            import shutil
            shutil.copy2(src, dst)
    
    def search_reports(self,
                      keyword: Optional[str] = None,
                      stock_code: Optional[str] = None,
                      industry: Optional[str] = None,
                      rating: Optional[str] = None,
                      source: Optional[str] = None,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      tags: List[str] = None) -> List[ResearchReport]:
        """
        搜索研报
        
        Args:
            keyword: 关键词 (标题/内容)
            stock_code: 股票代码
            industry: 行业
            rating: 评级
            source: 研报来源
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            tags: 标签列表
            
        Returns:
            List[ResearchReport]: 匹配的研报列表
        """
        results = []
        
        for report in self.report_index.values():
            # 关键词匹配
            if keyword and keyword.lower() not in report.title.lower():
                continue
            
            # 股票代码匹配
            if stock_code and report.stock_code != stock_code:
                continue
            
            # 行业匹配
            if industry and report.industry != industry:
                continue
            
            # 评级匹配
            if rating and report.rating != rating:
                continue
            
            # 来源匹配
            if source and report.source != source:
                continue
            
            # 日期范围匹配
            if start_date and report.report_date < start_date:
                continue
            if end_date and report.report_date > end_date:
                continue
            
            # 标签匹配
            if tags and not all(tag in report.tags for tag in tags):
                continue
            
            results.append(report)
        
        # 按日期排序
        results.sort(key=lambda x: x.report_date, reverse=True)
        
        logger.info(f"🔍 Found {len(results)} reports matching criteria")
        return results
    
    def get_report_by_id(self, report_id: str) -> Optional[ResearchReport]:
        """通过ID获取研报"""
        return self.report_index.get(report_id)
    
    def get_reports_by_stock(self, stock_code: str) -> List[ResearchReport]:
        """获取某只股票的所有研报"""
        return self.search_reports(stock_code=stock_code)
    
    def get_latest_reports(self, limit: int = 10) -> List[ResearchReport]:
        """获取最新研报"""
        reports = sorted(self.report_index.values(), 
                        key=lambda x: x.report_date, 
                        reverse=True)
        return reports[:limit]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            "total_reports": len(self.report_index),
            "by_industry": {},
            "by_rating": {},
            "by_source": {},
            "by_month": {},
            "stocks_covered": set()
        }
        
        for report in self.report_index.values():
            # 行业统计
            if report.industry:
                stats["by_industry"][report.industry] = stats["by_industry"].get(report.industry, 0) + 1
            
            # 评级统计
            if report.rating:
                stats["by_rating"][report.rating] = stats["by_rating"].get(report.rating, 0) + 1
            
            # 来源统计
            if report.source:
                stats["by_source"][report.source] = stats["by_source"].get(report.source, 0) + 1
            
            # 月度统计
            month = report.report_date[:7]
            stats["by_month"][month] = stats["by_month"].get(month, 0) + 1
            
            # 覆盖股票
            if report.stock_code:
                stats["stocks_covered"].add(report.stock_code)
        
        stats["stocks_covered"] = len(stats["stocks_covered"])
        
        return stats
    
    def delete_report(self, report_id: str) -> bool:
        """删除研报"""
        if report_id not in self.report_index:
            return False
        
        report = self.report_index[report_id]
        
        # 删除符号链接
        self._remove_symlinks(report)
        
        # 从索引中删除
        del self.report_index[report_id]
        self._save_index()
        
        logger.info(f"🗑️ Deleted report: {report.title}")
        return True
    
    def _remove_symlinks(self, report: ResearchReport):
        """删除所有符号链接"""
        paths_to_check = [
            self.base_path / "by_stock" / (report.stock_code or "") / f"{report.report_id}{report.file_type}",
            self.base_path / "by_industry" / (report.industry or "") / f"{report.report_id}{report.file_type}",
            self.base_path / "by_date" / report.report_date[:7] / f"{report.report_id}{report.file_type}",
            self.base_path / "by_rating" / (report.rating or "") / f"{report.report_id}{report.file_type}",
            self.base_path / "by_source" / (report.source or "") / f"{report.report_id}{report.file_type}",
        ]
        
        for path in paths_to_check:
            if path.exists() or path.is_symlink():
                try:
                    path.unlink()
                except Exception as e:
                    logger.warning(f"⚠️ Failed to remove {path}: {e}")
    
    def export_catalog(self, output_path: str):
        """导出研报目录"""
        catalog = {
            "generated_at": datetime.now().isoformat(),
            "total_reports": len(self.report_index),
            "reports": [r.to_dict() for r in self.report_index.values()]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📋 Exported catalog to {output_path}")


def main():
    """测试研报管理器"""
    print("=" * 80)
    print("📁 Research Report Manager - Test")
    print("=" * 80)
    
    # 初始化管理器
    manager = ResearchReportManager()
    
    # 添加测试研报
    test_reports = [
        {
            "file_path": "/tmp/test_report1.pdf",
            "title": "宁德时代深度研究报告",
            "stock_code": "300750.SZ",
            "stock_name": "宁德时代",
            "source": "中金公司",
            "rating": "买入",
            "industry": "新能源",
            "target_price": 280.0
        },
        {
            "file_path": "/tmp/test_report2.pdf",
            "title": "贵州茅台季报点评",
            "stock_code": "600519.SH",
            "stock_name": "贵州茅台",
            "source": "中信证券",
            "rating": "增持",
            "industry": "食品饮料",
            "target_price": 1850.0
        }
    ]
    
    # 创建测试文件
    for report_data in test_reports:
        with open(report_data["file_path"], 'w') as f:
            f.write("Test report content")
    
    # 添加研报
    for report_data in test_reports:
        try:
            report = manager.add_report(**report_data)
            print(f"✅ Added: {report.title}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 搜索测试
    print("\n🔍 Search results for '宁德时代':")
    results = manager.search_reports(keyword="宁德")
    for r in results:
        print(f"   - {r.title} ({r.rating})")
    
    # 统计信息
    print("\n📊 Statistics:")
    stats = manager.get_statistics()
    print(f"   Total reports: {stats['total_reports']}")
    print(f"   Stocks covered: {stats['stocks_covered']}")
    print(f"   By industry: {stats['by_industry']}")
    
    print("\n" + "=" * 80)
    print("✅ Research Report Manager test completed!")


if __name__ == "__main__":
    main()
