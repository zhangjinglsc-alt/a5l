"""
A5L Database Package
SQLite持久化数据层

核心组件:
- db_manager: 数据库管理器
- db_utils: 便捷工具函数

Quick Start:
    from database import get_db_manager, save_analysis, get_dashboard_stats
    
    # 保存分析
    save_analysis(content="分析内容", symbol="000001.SZ")
    
    # 获取统计
    stats = get_dashboard_stats()
"""

from database.db_manager import DatabaseManager, get_db_manager, Atom, Decision, Signal
from database.db_utils import (
    save_analysis,
    save_memo,
    save_decision_record,
    save_trade_signal,
    get_decisions,
    get_signals_for_symbol,
    get_recent_signals,
    get_analysis_by_symbol,
    get_dashboard_stats,
    print_dashboard
)

__all__ = [
    'DatabaseManager',
    'get_db_manager',
    'Atom',
    'Decision',
    'Signal',
    'save_analysis',
    'save_memo',
    'save_decision_record',
    'save_trade_signal',
    'get_decisions',
    'get_signals_for_symbol',
    'get_recent_signals',
    'get_analysis_by_symbol',
    'get_dashboard_stats',
    'print_dashboard'
]

__version__ = '2.2.0'
