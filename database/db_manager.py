#!/usr/bin/env python3
"""
A5L SQLite Database Manager
SQLite持久化管理器 - 核心数据层

负责:
- 数据库初始化和连接管理
- Atoms CRUD操作
- Decisions记录
- Signals存储
- Squad任务追踪
- 同步日志
- 系统状态
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('A5L.DB')


@dataclass
class Atom:
    """Atom数据模型"""
    id: str
    kind: str
    content: str
    title: Optional[str] = None
    author: str = 'system'
    squad_id: Optional[str] = None
    metadata: Optional[Dict] = None
    links: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: str = 'active'
    version: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Decision:
    """Decision数据模型"""
    id: str
    type: str
    action: str
    atom_id: Optional[str] = None
    symbol: Optional[str] = None
    confidence: Optional[float] = None
    urgency: Optional[int] = None
    impact: Optional[int] = None
    status: str = 'pending'
    executed_at: Optional[str] = None
    execution_result: Optional[Dict] = None
    parent_id: Optional[str] = None
    chain_depth: int = 0
    chain_json: Optional[Dict] = None
    source_squad: Optional[str] = None
    source_skills: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Signal:
    """Signal数据模型"""
    symbol: str
    signal_type: str
    direction: str
    strength: float
    id: Optional[int] = None
    atom_id: Optional[str] = None
    timeframe: Optional[str] = None
    price_at_signal: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    source: Optional[str] = None
    source_skills: Optional[List[str]] = None
    context_json: Optional[Dict] = None
    created_at: Optional[str] = None


class DatabaseManager:
    """A5L数据库管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，默认 data/db/a5l_v2_2.db
        """
        if db_path is None:
            workspace = Path('/workspace/projects/workspace')
            db_path = workspace / 'data' / 'db' / 'a5l_v2_2.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        logger.info(f"✅ Database initialized: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化数据库结构"""
        schema_path = Path(__file__).parent / 'schema.sql'
        
        if not schema_path.exists():
            logger.error(f"❌ Schema file not found: {schema_path}")
            return
        
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        with self._get_connection() as conn:
            conn.executescript(schema)
    
    # ============================================
    # Atoms操作
    # ============================================
    
    def save_atom(self, atom: Atom) -> bool:
        """
        保存Atom到数据库
        
        Args:
            atom: Atom对象
            
        Returns:
            bool: 是否成功
        """
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO atoms 
                    (id, kind, title, content, author, squad_id, metadata, links, tags, 
                     status, version, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    atom.id,
                    atom.kind,
                    atom.title,
                    atom.content,
                    atom.author,
                    atom.squad_id,
                    json.dumps(atom.metadata) if atom.metadata else None,
                    json.dumps(atom.links) if atom.links else None,
                    json.dumps(atom.tags) if atom.tags else None,
                    atom.status,
                    atom.version,
                    atom.created_at or datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
            logger.info(f"✅ Atom saved: {atom.id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save atom {atom.id}: {e}")
            return False
    
    def get_atom(self, atom_id: str) -> Optional[Atom]:
        """
        根据ID获取Atom
        
        Args:
            atom_id: Atom ID
            
        Returns:
            Atom对象或None
        """
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    'SELECT * FROM atoms WHERE id = ?', (atom_id,)
                ).fetchone()
                
                if row:
                    return self._row_to_atom(row)
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get atom {atom_id}: {e}")
            return None
    
    def get_atoms_by_kind(self, kind: str, limit: int = 100) -> List[Atom]:
        """
        根据类型获取Atoms
        
        Args:
            kind: Atom类型
            limit: 返回数量限制
            
        Returns:
            Atom列表
        """
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    'SELECT * FROM atoms WHERE kind = ? AND status = "active" ORDER BY created_at DESC LIMIT ?',
                    (kind, limit)
                ).fetchall()
                
                return [self._row_to_atom(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get atoms by kind {kind}: {e}")
            return []
    
    def get_atoms_by_squad(self, squad_id: str, limit: int = 100) -> List[Atom]:
        """根据Squad获取Atoms"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    'SELECT * FROM atoms WHERE squad_id = ? AND status = "active" ORDER BY created_at DESC LIMIT ?',
                    (squad_id, limit)
                ).fetchall()
                
                return [self._row_to_atom(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get atoms by squad {squad_id}: {e}")
            return []
    
    def search_atoms(self, query: str, limit: int = 50) -> List[Atom]:
        """
        全文搜索Atoms (关键词匹配，后续可升级为语义搜索)
        
        Args:
            query: 搜索关键词
            limit: 返回数量
            
        Returns:
            Atom列表
        """
        try:
            with self._get_connection() as conn:
                # 使用LIKE进行简单全文搜索
                pattern = f'%{query}%'
                rows = conn.execute('''
                    SELECT * FROM atoms 
                    WHERE (title LIKE ? OR content LIKE ?) AND status = "active"
                    ORDER BY created_at DESC LIMIT ?
                ''', (pattern, pattern, limit)).fetchall()
                
                return [self._row_to_atom(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to search atoms: {e}")
            return []
    
    def update_atom_status(self, atom_id: str, status: str) -> bool:
        """更新Atom状态"""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    'UPDATE atoms SET status = ?, updated_at = ? WHERE id = ?',
                    (status, datetime.now().isoformat(), atom_id)
                )
            logger.info(f"✅ Atom {atom_id} status updated to {status}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update atom status: {e}")
            return False
    
    def delete_atom(self, atom_id: str, soft: bool = True) -> bool:
        """
        删除Atom
        
        Args:
            atom_id: Atom ID
            soft: 是否软删除（默认True）
        """
        try:
            if soft:
                return self.update_atom_status(atom_id, 'deleted')
            else:
                with self._get_connection() as conn:
                    conn.execute('DELETE FROM atoms WHERE id = ?', (atom_id,))
                logger.info(f"✅ Atom {atom_id} hard deleted")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to delete atom: {e}")
            return False
    
    def _row_to_atom(self, row: sqlite3.Row) -> Atom:
        """将数据库行转换为Atom对象"""
        return Atom(
            id=row['id'],
            kind=row['kind'],
            title=row['title'],
            content=row['content'],
            author=row['author'],
            squad_id=row['squad_id'],
            metadata=json.loads(row['metadata']) if row['metadata'] else None,
            links=json.loads(row['links']) if row['links'] else None,
            tags=json.loads(row['tags']) if row['tags'] else None,
            status=row['status'],
            version=row['version'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    # ============================================
    # Decisions操作
    # ============================================
    
    def save_decision(self, decision: Decision) -> bool:
        """保存决策记录"""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO decisions 
                    (id, atom_id, type, symbol, action, confidence, urgency, impact,
                     status, executed_at, execution_result, parent_id, chain_depth, chain_json,
                     source_squad, source_skills, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    decision.id,
                    decision.atom_id,
                    decision.type,
                    decision.symbol,
                    decision.action,
                    decision.confidence,
                    decision.urgency,
                    decision.impact,
                    decision.status,
                    decision.executed_at,
                    json.dumps(decision.execution_result) if decision.execution_result else None,
                    decision.parent_id,
                    decision.chain_depth,
                    json.dumps(decision.chain_json) if decision.chain_json else None,
                    decision.source_squad,
                    json.dumps(decision.source_skills) if decision.source_skills else None,
                    decision.created_at or datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
            logger.info(f"✅ Decision saved: {decision.id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save decision: {e}")
            return False
    
    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """获取决策记录"""
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    'SELECT * FROM decisions WHERE id = ?', (decision_id,)
                ).fetchone()
                
                if row:
                    return self._row_to_decision(row)
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get decision: {e}")
            return None
    
    def get_decisions_by_symbol(self, symbol: str, limit: int = 50) -> List[Decision]:
        """获取某股票的所有决策"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    'SELECT * FROM decisions WHERE symbol = ? ORDER BY created_at DESC LIMIT ?',
                    (symbol, limit)
                ).fetchall()
                
                return [self._row_to_decision(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get decisions by symbol: {e}")
            return []
    
    def get_pending_decisions(self, limit: int = 100) -> List[Decision]:
        """获取待处理决策"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    'SELECT * FROM decisions WHERE status = "pending" ORDER BY urgency DESC, confidence DESC LIMIT ?',
                    (limit,)
                ).fetchall()
                
                return [self._row_to_decision(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get pending decisions: {e}")
            return []
    
    def update_decision_status(self, decision_id: str, status: str, execution_result: Dict = None) -> bool:
        """更新决策状态"""
        try:
            with self._get_connection() as conn:
                if execution_result:
                    conn.execute('''
                        UPDATE decisions 
                        SET status = ?, execution_result = ?, executed_at = ?, updated_at = ?
                        WHERE id = ?
                    ''', (status, json.dumps(execution_result), datetime.now().isoformat(), 
                          datetime.now().isoformat(), decision_id))
                else:
                    conn.execute(
                        'UPDATE decisions SET status = ?, updated_at = ? WHERE id = ?',
                        (status, datetime.now().isoformat(), decision_id)
                    )
            logger.info(f"✅ Decision {decision_id} status updated to {status}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update decision status: {e}")
            return False
    
    def _row_to_decision(self, row: sqlite3.Row) -> Decision:
        """将数据库行转换为Decision对象"""
        return Decision(
            id=row['id'],
            atom_id=row['atom_id'],
            type=row['type'],
            symbol=row['symbol'],
            action=row['action'],
            confidence=row['confidence'],
            urgency=row['urgency'],
            impact=row['impact'],
            status=row['status'],
            executed_at=row['executed_at'],
            execution_result=json.loads(row['execution_result']) if row['execution_result'] else None,
            parent_id=row['parent_id'],
            chain_depth=row['chain_depth'],
            chain_json=json.loads(row['chain_json']) if row['chain_json'] else None,
            source_squad=row['source_squad'],
            source_skills=json.loads(row['source_skills']) if row['source_skills'] else None,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    # ============================================
    # Signals操作
    # ============================================
    
    def save_signal(self, signal: Signal) -> bool:
        """保存信号"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO signals 
                    (atom_id, symbol, signal_type, direction, strength, timeframe,
                     price_at_signal, target_price, stop_loss, source, source_skills, context_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal.atom_id,
                    signal.symbol,
                    signal.signal_type,
                    signal.direction,
                    signal.strength,
                    signal.timeframe,
                    signal.price_at_signal,
                    signal.target_price,
                    signal.stop_loss,
                    signal.source,
                    json.dumps(signal.source_skills) if signal.source_skills else None,
                    json.dumps(signal.context_json) if signal.context_json else None
                ))
                signal.id = cursor.lastrowid
            logger.info(f"✅ Signal saved: {signal.symbol} {signal.signal_type}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save signal: {e}")
            return False
    
    def get_signals_by_symbol(self, symbol: str, limit: int = 50) -> List[Signal]:
        """获取某股票的所有信号"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    'SELECT * FROM signals WHERE symbol = ? ORDER BY created_at DESC LIMIT ?',
                    (symbol, limit)
                ).fetchall()
                
                return [self._row_to_signal(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get signals: {e}")
            return []
    
    def get_recent_signals(self, hours: int = 24, min_strength: float = 0.7) -> List[Signal]:
        """获取最近的高强度信号"""
        try:
            with self._get_connection() as conn:
                rows = conn.execute('''
                    SELECT * FROM signals 
                    WHERE created_at > datetime('now', '-{} hours') 
                    AND strength >= ?
                    ORDER BY strength DESC, created_at DESC
                '''.format(hours), (min_strength,)).fetchall()
                
                return [self._row_to_signal(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get recent signals: {e}")
            return []
    
    def validate_signal(self, signal_id: int, pnl: float, result: Dict = None) -> bool:
        """验证信号并记录结果"""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    UPDATE signals 
                    SET validated = 1, validated_at = ?, validation_result = ?, pnl = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), json.dumps(result) if result else None, pnl, signal_id))
            logger.info(f"✅ Signal {signal_id} validated, PnL: {pnl}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to validate signal: {e}")
            return False
    
    def _row_to_signal(self, row: sqlite3.Row) -> Signal:
        """将数据库行转换为Signal对象"""
        return Signal(
            id=row['id'],
            atom_id=row['atom_id'],
            symbol=row['symbol'],
            signal_type=row['signal_type'],
            direction=row['direction'],
            strength=row['strength'],
            timeframe=row['timeframe'],
            price_at_signal=row['price_at_signal'],
            target_price=row['target_price'],
            stop_loss=row['stop_loss'],
            source=row['source'],
            source_skills=json.loads(row['source_skills']) if row['source_skills'] else None,
            context_json=json.loads(row['context_json']) if row['context_json'] else None,
            created_at=row['created_at']
        )
    
    # ============================================
    # 统计和查询
    # ============================================
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with self._get_connection() as conn:
                stats = {}
                
                # Atoms统计
                row = conn.execute('SELECT COUNT(*) as count FROM atoms').fetchone()
                stats['total_atoms'] = row['count']
                
                row = conn.execute('SELECT COUNT(*) as count FROM atoms WHERE status = "active"').fetchone()
                stats['active_atoms'] = row['count']
                
                # Decisions统计
                row = conn.execute('SELECT COUNT(*) as count FROM decisions').fetchone()
                stats['total_decisions'] = row['count']
                
                row = conn.execute('SELECT COUNT(*) as count FROM decisions WHERE status = "pending"').fetchone()
                stats['pending_decisions'] = row['count']
                
                # Signals统计
                row = conn.execute('SELECT COUNT(*) as count FROM signals').fetchone()
                stats['total_signals'] = row['count']
                
                row = conn.execute('SELECT COUNT(*) as count FROM signals WHERE validated = 1').fetchone()
                stats['validated_signals'] = row['count']
                
                # 24小时内的新增
                row = conn.execute('''
                    SELECT COUNT(*) as count FROM atoms 
                    WHERE created_at > datetime('now', '-24 hours')
                ''').fetchone()
                stats['atoms_24h'] = row['count']
                
                return stats
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {}
    
    def get_recent_activity(self, limit: int = 20) -> List[Dict]:
        """获取最近活动记录"""
        try:
            with self._get_connection() as conn:
                # 合并atoms和decisions的最近记录
                query = '''
                    SELECT 'atom' as type, id, kind as subtype, title as description, created_at
                    FROM atoms
                    WHERE status = 'active'
                    UNION ALL
                    SELECT 'decision' as type, id, type as subtype, 
                           symbol || ' ' || action as description, created_at
                    FROM decisions
                    ORDER BY created_at DESC
                    LIMIT ?
                '''
                rows = conn.execute(query, (limit,)).fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get recent activity: {e}")
            return []
    
    # ============================================
    # 系统状态
    # ============================================
    
    def set_state(self, key: str, value: Any, value_type: str = 'string'):
        """设置系统状态"""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO system_state (key, value, value_type, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (key, str(value), value_type, datetime.now().isoformat()))
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set state: {e}")
            return False
    
    def get_state(self, key: str, default=None) -> Any:
        """获取系统状态"""
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    'SELECT value, value_type FROM system_state WHERE key = ?', (key,)
                ).fetchone()
                
                if not row:
                    return default
                
                value, value_type = row['value'], row['value_type']
                
                if value_type == 'int':
                    return int(value)
                elif value_type == 'float':
                    return float(value)
                elif value_type == 'json':
                    return json.loads(value)
                elif value_type == 'bool':
                    return value.lower() == 'true'
                else:
                    return value
        except Exception as e:
            logger.error(f"❌ Failed to get state: {e}")
            return default


# ============================================
# 全局实例
# ============================================

_db_manager = None

def get_db_manager() -> DatabaseManager:
    """获取全局数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


# ============================================
# 测试
# ============================================

if __name__ == '__main__':
    print("🧪 Testing A5L Database Manager...")
    
    db = DatabaseManager()
    
    # 测试Atom保存
    test_atom = Atom(
        id='test-atom-001',
        kind='analysis',
        title='测试分析',
        content='这是一个测试Atom内容',
        author='test',
        squad_id='intelligence_core',
        tags=['test', 'analysis'],
        metadata={'source': 'test', 'priority': 3}
    )
    db.save_atom(test_atom)
    
    # 测试读取
    atom = db.get_atom('test-atom-001')
    print(f"✅ Read atom: {atom.title}")
    
    # 测试Decision
    test_decision = Decision(
        id='test-decision-001',
        type='trade',
        symbol='000001.SZ',
        action='buy',
        confidence=0.85,
        urgency=4,
        source_squad='execution_force'
    )
    db.save_decision(test_decision)
    
    # 测试Signal
    test_signal = Signal(
        symbol='000001.SZ',
        signal_type='breakout',
        direction='bullish',
        strength=0.82,
        source='tushare',
        timeframe='1d'
    )
    db.save_signal(test_signal)
    
    # 测试统计
    stats = db.get_stats()
    print(f"\n📊 Database Stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    # 测试最近活动
    activity = db.get_recent_activity(5)
    print(f"\n📝 Recent Activity:")
    for item in activity:
        print(f"  [{item['type']}] {item['description']}")
    
    print("\n✅ All tests passed!")
