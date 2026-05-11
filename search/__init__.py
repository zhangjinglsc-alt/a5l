"""
A5L Search Package
搜索模块

组件:
- semantic_search: 语义搜索 (向量嵌入)

Quick Start:
    from search import semantic_search, index_atom
    
    # 索引内容
    index_atom("id1", "股票分析内容", {"symbol": "000001.SZ"})
    
    # 语义搜索
    results = semantic_search("AI算力投资", top_k=5)
"""

from search.semantic_search import (
    SemanticSearch,
    SearchResult,
    get_search_engine,
    semantic_search,
    hybrid_search,
    index_atom,
    sync_search_index
)

__all__ = [
    'SemanticSearch',
    'SearchResult',
    'get_search_engine',
    'semantic_search',
    'hybrid_search',
    'index_atom',
    'sync_search_index'
]
