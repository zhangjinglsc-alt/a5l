#!/usr/bin/env python3
"""
A5L Semantic Search
语义搜索模块 - 基于向量嵌入

功能:
- 文本向量化 (Embedding)
- 向量存储 (ChromaDB)
- 语义相似度搜索
- 混合搜索 (语义+关键词)

Usage:
    from search.semantic_search import SemanticSearch
    
    search = SemanticSearch()
    search.index_atom(atom_id, content, metadata)
    results = search.semantic_search("AI算力投资", top_k=5)
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('A5L.Search')


@dataclass
class SearchResult:
    """搜索结果"""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    search_type: str  # 'semantic' or 'keyword'


class SemanticSearch:
    """
    语义搜索引擎
    
    架构:
        输入文本 → Embedding模型 → 向量 → ChromaDB存储 → 相似度搜索
    """
    
    def __init__(self, collection_name: str = "a5l_knowledge"):
        """
        初始化语义搜索引擎
        
        Args:
            collection_name: ChromaDB集合名称
        """
        self.collection_name = collection_name
        self._chroma_client = None
        self._collection = None
        self._embedding_model = None
        
        # 延迟初始化 (第一次使用时)
        self._initialized = False
        
        logger.info(f"✅ SemanticSearch initialized (collection: {collection_name})")
    
    def _ensure_initialized(self):
        """确保组件已初始化"""
        if self._initialized:
            return
        
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            
            # 初始化ChromaDB
            workspace = Path('/workspace/projects/workspace')
            db_path = workspace / 'data' / 'chroma_db'
            db_path.mkdir(parents=True, exist_ok=True)
            
            self._chroma_client = chromadb.PersistentClient(path=str(db_path))
            
            # 获取或创建集合
            try:
                self._collection = self._chroma_client.get_collection(self.collection_name)
                logger.info(f"✅ Loaded existing collection: {self.collection_name}")
            except Exception:
                self._collection = self._chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "A5L knowledge base"}
                )
                logger.info(f"✅ Created new collection: {self.collection_name}")
            
            # 初始化Embedding模型 (仅首次加载时需要下载，约80MB)
            logger.info("🔄 Loading embedding model...")
            self._embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("✅ Embedding model loaded")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize semantic search: {e}")
            raise
    
    def encode(self, text: str) -> List[float]:
        """
        将文本编码为向量
        
        Args:
            text: 输入文本
            
        Returns:
            向量 (384维)
        """
        self._ensure_initialized()
        return self._embedding_model.encode(text).tolist()
    
    def index_atom(self, atom_id: str, content: str, metadata: Dict = None):
        """
        索引Atom到语义搜索引擎
        
        Args:
            atom_id: Atom ID
            content: 文本内容
            metadata: 元数据
        """
        self._ensure_initialized()
        
        try:
            # 生成向量
            embedding = self.encode(content)
            
            # 添加到ChromaDB
            self._collection.add(
                ids=[atom_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata or {}]
            )
            
            logger.info(f"✅ Indexed atom: {atom_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to index atom {atom_id}: {e}")
    
    def semantic_search(self, query: str, top_k: int = 5, 
                        filter_dict: Dict = None) -> List[SearchResult]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_dict: 过滤条件
            
        Returns:
            搜索结果列表
        """
        self._ensure_initialized()
        
        try:
            # 查询向量化
            query_embedding = self.encode(query)
            
            # 相似度搜索
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_dict
            )
            
            # 组装结果
            search_results = []
            for i in range(len(results['ids'][0])):
                result = SearchResult(
                    id=results['ids'][0][i],
                    content=results['documents'][0][i],
                    score=float(results['distances'][0][i]),
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                    search_type='semantic'
                )
                search_results.append(result)
            
            logger.info(f"✅ Semantic search: '{query[:30]}...' → {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []
    
    def keyword_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        关键词搜索 (备用)
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        self._ensure_initialized()
        
        try:
            # 使用ChromaDB的全文搜索
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            search_results = []
            for i in range(len(results['ids'][0])):
                result = SearchResult(
                    id=results['ids'][0][i],
                    content=results['documents'][0][i],
                    score=float(results['distances'][0][i]) if results['distances'] else 0.0,
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                    search_type='keyword'
                )
                search_results.append(result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Keyword search failed: {e}")
            return []
    
    def hybrid_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        混合搜索 (语义 + 关键词)
        
        先进行语义搜索，如果结果不足，补充关键词搜索结果
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            合并后的搜索结果
        """
        semantic_results = self.semantic_search(query, top_k=top_k)
        
        # 如果语义搜索结果不足，补充关键词搜索
        if len(semantic_results) < top_k:
            keyword_results = self.keyword_search(query, top_k=top_k)
            
            # 合并去重
            seen_ids = {r.id for r in semantic_results}
            for kr in keyword_results:
                if kr.id not in seen_ids:
                    semantic_results.append(kr)
                    if len(semantic_results) >= top_k:
                        break
        
        return semantic_results[:top_k]
    
    def delete_atom(self, atom_id: str):
        """
        删除索引
        
        Args:
            atom_id: Atom ID
        """
        self._ensure_initialized()
        
        try:
            self._collection.delete(ids=[atom_id])
            logger.info(f"✅ Deleted atom from index: {atom_id}")
        except Exception as e:
            logger.error(f"❌ Failed to delete atom {atom_id}: {e}")
    
    def get_stats(self) -> Dict:
        """获取索引统计"""
        self._ensure_initialized()
        
        try:
            count = self._collection.count()
            return {
                "total_indexed": count,
                "collection_name": self.collection_name,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dim": 384
            }
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {}
    
    def sync_from_database(self):
        """
        从SQLite数据库同步所有Atoms到语义搜索引擎
        
        一次性索引所有历史数据
        """
        from database import get_db_manager
        
        self._ensure_initialized()
        db = get_db_manager()
        
        logger.info("🔄 Syncing atoms from database to semantic index...")
        
        # 获取所有Atoms
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            'SELECT id, kind, title, content, metadata, tags FROM atoms WHERE status = "active"'
        ).fetchall()
        conn.close()
        
        indexed_count = 0
        for row in rows:
            try:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                metadata['kind'] = row['kind']
                metadata['title'] = row['title']
                
                # 组合标题和内容作为索引文本
                text_to_index = f"{row['title'] or ''}\n{row['content']}"
                
                self.index_atom(row['id'], text_to_index, metadata)
                indexed_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to index atom {row['id']}: {e}")
        
        logger.info(f"✅ Sync complete: {indexed_count}/{len(rows)} atoms indexed")
        return indexed_count


# ============================================
# 便捷函数
# ============================================

_search_engine = None

def get_search_engine() -> SemanticSearch:
    """获取全局搜索引擎实例"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SemanticSearch()
    return _search_engine


def semantic_search(query: str, top_k: int = 5) -> List[SearchResult]:
    """便捷语义搜索"""
    return get_search_engine().semantic_search(query, top_k)


def hybrid_search(query: str, top_k: int = 5) -> List[SearchResult]:
    """便捷混合搜索"""
    return get_search_engine().hybrid_search(query, top_k)


def index_atom(atom_id: str, content: str, metadata: Dict = None):
    """便捷索引"""
    return get_search_engine().index_atom(atom_id, content, metadata)


def sync_search_index():
    """同步数据库到搜索索引"""
    return get_search_engine().sync_from_database()


# ============================================
# 测试
# ============================================

def test_semantic_search():
    """测试语义搜索"""
    print("🧪 Testing A5L Semantic Search...")
    print("=" * 60)
    
    # 创建搜索引擎
    search = SemanticSearch()
    
    # 测试数据
    test_docs = [
        ("doc1", "人工智能算力需求激增，GPU芯片供不应求", {"category": "AI"}),
        ("doc2", "新能源电池技术突破，锂电池能量密度提升", {"category": "新能源"}),
        ("doc3", "数据中心建设加速，液冷技术成为主流", {"category": "基础设施"}),
        ("doc4", "英伟达显卡价格飙升，AI训练成本增加", {"category": "AI"}),
        ("doc5", "光伏产业链景气度高，硅料价格上涨", {"category": "新能源"}),
    ]
    
    # 索引文档
    print("\n1️⃣ 索引测试文档...")
    for doc_id, content, meta in test_docs:
        search.index_atom(doc_id, content, meta)
    
    stats = search.get_stats()
    print(f"   ✅ Indexed {stats['total_indexed']} documents")
    
    # 语义搜索测试
    print("\n2️⃣ 语义搜索测试...")
    queries = [
        "AI算力投资",  # 应该匹配doc1, doc4
        "新能源产业链",  # 应该匹配doc2, doc5
        "数据中心冷却",  # 应该匹配doc3
    ]
    
    for query in queries:
        print(f"\n   查询: '{query}'")
        results = search.semantic_search(query, top_k=2)
        for r in results:
            print(f"     → {r.id}: {r.content[:30]}... (score: {r.score:.3f})")
    
    # 混合搜索测试
    print("\n3️⃣ 混合搜索测试...")
    results = search.hybrid_search("GPU和人工智能", top_k=3)
    for r in results:
        print(f"   → {r.id} ({r.search_type}): {r.content[:30]}...")
    
    print("\n" + "=" * 60)
    print("✅ Semantic search test complete!")


if __name__ == '__main__':
    test_semantic_search()
