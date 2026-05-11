#!/usr/bin/env python3
"""
A5L Database Utils
数据库便捷工具 - 简化常用操作

使用方法:
    from database.db_utils import save_analysis, get_decisions, get_signals_for_symbol
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    from database.db_manager import get_db_manager, Atom, Decision, Signal
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from database.db_manager import get_db_manager, Atom, Decision, Signal


def generate_id(prefix: str = "a5l") -> str:
    """生成唯一ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{random_suffix}"


# ============================================
# 便捷保存函数
# ============================================

def save_analysis(
    content: str,
    title: str = None,
    symbol: str = None,
    analysis_type: str = "general",
    squad_id: str = "intelligence_core",
    tags: List[str] = None,
    metadata: Dict = None
) -> str:
    """
    保存分析结果
    
    Args:
        content: 分析内容
        title: 标题
        symbol: 相关股票代码(可选)
        analysis_type: 分析类型
        squad_id: 执行Squad
        tags: 标签列表
        metadata: 元数据
        
    Returns:
        Atom ID
    """
    db = get_db_manager()
    
    atom_id = generate_id("analysis")
    
    if tags is None:
        tags = []
    tags.append(analysis_type)
    if symbol:
        tags.append(symbol)
    
    if metadata is None:
        metadata = {}
    metadata['analysis_type'] = analysis_type
    if symbol:
        metadata['symbol'] = symbol
    
    atom = Atom(
        id=atom_id,
        kind='analysis',
        title=title or f"Analysis {datetime.now().strftime('%H:%M')}",
        content=content,
        squad_id=squad_id,
        tags=list(set(tags)),  # 去重
        metadata=metadata
    )
    
    db.save_atom(atom)
    return atom_id


def save_memo(
    content: str,
    title: str = None,
    category: str = "general",
    tags: List[str] = None
) -> str:
    """
    保存备忘录
    
    Args:
        content: 内容
        title: 标题
        category: 分类
        tags: 标签
        
    Returns:
        Atom ID
    """
    db = get_db_manager()
    
    atom_id = generate_id("memo")
    
    if tags is None:
        tags = []
    tags.append(category)
    
    atom = Atom(
        id=atom_id,
        kind='memo',
        title=title or f"Memo {datetime.now().strftime('%H:%M')}",
        content=content,
        squad_id='prime_council',
        tags=tags,
        metadata={'category': category}
    )
    
    db.save_atom(atom)
    return atom_id


def save_decision_record(
    decision_type: str,
    action: str,
    symbol: str = None,
    confidence: float = None,
    urgency: int = None,
    reason: str = None,
    source_squad: str = None,
    source_skills: List[str] = None
) -> str:
    """
    保存决策记录
    
    Args:
        decision_type: 决策类型 (trade/strategy/risk/allocation)
        action: 决策动作 (buy/sell/hold/watch)
        symbol: 股票代码
        confidence: 置信度 0-1
        urgency: 紧急度 1-5
        reason: 决策理由
        source_squad: 来源Squad
        source_skills: 使用的SKILL
        
    Returns:
        Decision ID
    """
    db = get_db_manager()
    
    decision_id = generate_id("decision")
    
    # 创建关联的Atom
    if reason:
        atom_id = save_memo(
            content=reason,
            title=f"Decision: {action} {symbol}" if symbol else f"Decision: {action}",
            category='decision_reason'
        )
    else:
        atom_id = None
    
    decision = Decision(
        id=decision_id,
        atom_id=atom_id,
        type=decision_type,
        symbol=symbol,
        action=action,
        confidence=confidence,
        urgency=urgency,
        source_squad=source_squad,
        source_skills=source_skills
    )
    
    db.save_decision(decision)
    return decision_id


def save_trade_signal(
    symbol: str,
    direction: str,  # bullish/bearish/neutral
    strength: float,
    signal_type: str = "composite",
    price: float = None,
    target: float = None,
    stop_loss: float = None,
    timeframe: str = "1d",
    reason: str = None,
    source_skills: List[str] = None
) -> int:
    """
    保存交易信号
    
    Args:
        symbol: 股票代码
        direction: 方向
        strength: 强度 0-1
        signal_type: 信号类型
        price: 当前价格
        target: 目标价
        stop_loss: 止损价
        timeframe: 时间框架
        reason: 信号理由
        source_skills: 使用的SKILL
        
    Returns:
        Signal ID
    """
    db = get_db_manager()
    
    # 创建关联的Atom
    atom_id = None
    if reason:
        atom_id = save_analysis(
            content=reason,
            title=f"Signal: {symbol} {direction}",
            symbol=symbol,
            analysis_type='signal',
            tags=['signal', direction, signal_type]
        )
    
    signal = Signal(
        atom_id=atom_id,
        symbol=symbol,
        signal_type=signal_type,
        direction=direction,
        strength=strength,
        price_at_signal=price,
        target_price=target,
        stop_loss=stop_loss,
        timeframe=timeframe,
        source='a5l_system',
        source_skills=source_skills,
        context_json={
            'generated_at': datetime.now().isoformat(),
            'system_version': '2.2.0'
        }
    )
    
    db.save_signal(signal)
    return signal.id


# ============================================
# 便捷查询函数
# ============================================

def get_decisions(
    symbol: str = None,
    status: str = None,
    decision_type: str = None,
    limit: int = 50
) -> List[Dict]:
    """
    查询决策记录
    
    Args:
        symbol: 股票代码筛选
        status: 状态筛选
        decision_type: 类型筛选
        limit: 数量限制
        
    Returns:
        决策列表
    """
    db = get_db_manager()
    
    if symbol:
        decisions = db.get_decisions_by_symbol(symbol, limit)
    elif status == 'pending':
        decisions = db.get_pending_decisions(limit)
    else:
        # 通用查询
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        
        query = 'SELECT * FROM decisions WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        if decision_type:
            query += ' AND type = ?'
            params.append(decision_type)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        rows = conn.execute(query, params).fetchall()
        decisions = [db._row_to_decision(row) for row in rows]
        conn.close()
    
    return [{
        'id': d.id,
        'type': d.type,
        'symbol': d.symbol,
        'action': d.action,
        'confidence': d.confidence,
        'status': d.status,
        'created_at': d.created_at
    } for d in decisions]


def get_signals_for_symbol(symbol: str, limit: int = 20) -> List[Dict]:
    """
    获取某股票的信号
    
    Args:
        symbol: 股票代码
        limit: 数量限制
        
    Returns:
        信号列表
    """
    db = get_db_manager()
    signals = db.get_signals_by_symbol(symbol, limit)
    
    return [{
        'id': s.id,
        'symbol': s.symbol,
        'type': s.signal_type,
        'direction': s.direction,
        'strength': s.strength,
        'timeframe': s.timeframe,
        'created_at': s.created_at
    } for s in signals]


def get_recent_signals(hours: int = 24, min_strength: float = 0.7) -> List[Dict]:
    """
    获取最近的高强度信号
    
    Args:
        hours: 时间范围(小时)
        min_strength: 最小强度
        
    Returns:
        信号列表
    """
    db = get_db_manager()
    signals = db.get_recent_signals(hours, min_strength)
    
    return [{
        'id': s.id,
        'symbol': s.symbol,
        'type': s.signal_type,
        'direction': s.direction,
        'strength': s.strength,
        'timeframe': s.timeframe,
        'created_at': s.created_at
    } for s in signals]


def get_analysis_by_symbol(symbol: str, limit: int = 10) -> List[Dict]:
    """
    获取某股票的分析记录
    
    Args:
        symbol: 股票代码
        limit: 数量限制
        
    Returns:
        分析列表
    """
    db = get_db_manager()
    
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute('''
        SELECT * FROM atoms 
        WHERE kind = 'analysis' 
        AND (metadata LIKE ? OR tags LIKE ?)
        AND status = 'active'
        ORDER BY created_at DESC LIMIT ?
    ''', (f'%"symbol": "{symbol}"%', f'%"{symbol}"%', limit)).fetchall()
    
    atoms = [db._row_to_atom(row) for row in rows]
    conn.close()
    
    return [{
        'id': a.id,
        'title': a.title,
        'content': a.content[:200] + '...' if len(a.content) > 200 else a.content,
        'tags': a.tags,
        'created_at': a.created_at
    } for a in atoms]


# ============================================
# 快捷统计
# ============================================

def get_dashboard_stats() -> Dict:
    """
    获取仪表板统计数据
    
    Returns:
        统计数据字典
    """
    db = get_db_manager()
    
    stats = db.get_stats()
    recent_activity = db.get_recent_activity(10)
    
    return {
        'stats': stats,
        'recent_activity': recent_activity,
        'timestamp': datetime.now().isoformat()
    }


def print_dashboard():
    """打印仪表板到控制台"""
    dashboard = get_dashboard_stats()
    stats = dashboard['stats']
    activity = dashboard['recent_activity']
    
    print("\n" + "=" * 50)
    print("📊 A5L Database Dashboard")
    print("=" * 50)
    
    print(f"\n📈 总体统计:")
    print(f"  • Total Atoms: {stats.get('total_atoms', 0)} (Active: {stats.get('active_atoms', 0)})")
    print(f"  • Total Decisions: {stats.get('total_decisions', 0)} (Pending: {stats.get('pending_decisions', 0)})")
    print(f"  • Total Signals: {stats.get('total_signals', 0)} (Validated: {stats.get('validated_signals', 0)})")
    print(f"  • Atoms (24h): {stats.get('atoms_24h', 0)}")
    
    print(f"\n📝 最近活动:")
    for item in activity[:5]:
        time_str = item['created_at'][11:16] if item['created_at'] else '--:--'
        print(f"  [{time_str}] [{item['type']}] {item['description'][:40]}")
    
    print("\n" + "=" * 50)


# ============================================
# 测试
# ============================================

if __name__ == '__main__':
    print("🧪 Testing A5L Database Utils...")
    
    # 测试保存分析
    analysis_id = save_analysis(
        content="平安银行技术面突破，MACD金叉形成，成交量放大",
        title="平安银行技术分析",
        symbol="000001.SZ",
        analysis_type="technical",
        tags=['breakout', 'macd']
    )
    print(f"✅ Analysis saved: {analysis_id}")
    
    # 测试保存决策
    decision_id = save_decision_record(
        decision_type='trade',
        action='buy',
        symbol='000001.SZ',
        confidence=0.78,
        urgency=3,
        reason="技术面突破，基本面稳健，建议建仓",
        source_squad='execution_force',
        source_skills=['technical_analysis', 'yangguan_daodao']
    )
    print(f"✅ Decision saved: {decision_id}")
    
    # 测试保存信号
    signal_id = save_trade_signal(
        symbol='000001.SZ',
        direction='bullish',
        strength=0.82,
        signal_type='breakout',
        price=11.20,
        target=12.50,
        stop_loss=10.80,
        reason="突破近期高点，量能配合",
        source_skills=['technical_analysis']
    )
    print(f"✅ Signal saved: {signal_id}")
    
    # 测试查询
    decisions = get_decisions(symbol='000001.SZ')
    print(f"\n📋 Decisions for 000001.SZ: {len(decisions)}")
    
    signals = get_signals_for_symbol('000001.SZ')
    print(f"📡 Signals for 000001.SZ: {len(signals)}")
    
    # 打印仪表板
    print_dashboard()
    
    print("\n✅ All utils tests passed!")
