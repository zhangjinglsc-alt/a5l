-- A5L v2.2 SQLite Database Schema
-- 创建时间: 2026-05-11
-- 用途: Prime/Level3/KIWI数据持久化

-- ============================================
-- 1. Atoms表 - Prime Registry核心存储
-- ============================================
CREATE TABLE IF NOT EXISTS atoms (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,              -- 'decision', 'signal', 'analysis', 'memo', 'tag'
    title TEXT,
    content TEXT NOT NULL,
    author TEXT DEFAULT 'system',    -- 创建者标识
    squad_id TEXT,                   -- 所属Squad
    
    -- JSON字段存储复杂数据结构
    metadata TEXT,                   -- 通用元数据JSON
    links TEXT,                      -- 关联Atom ID列表JSON
    tags TEXT,                       -- 标签列表JSON
    
    -- 状态管理
    status TEXT DEFAULT 'active',    -- 'active', 'archived', 'deleted'
    version INTEGER DEFAULT 1,       -- 版本号
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Atoms索引
CREATE INDEX IF NOT EXISTS idx_atoms_kind ON atoms(kind);
CREATE INDEX IF NOT EXISTS idx_atoms_author ON atoms(author);
CREATE INDEX IF NOT EXISTS idx_atoms_squad ON atoms(squad_id);
CREATE INDEX IF NOT EXISTS idx_atoms_status ON atoms(status);
CREATE INDEX IF NOT EXISTS idx_atoms_created ON atoms(created_at);

-- ============================================
-- 2. Decisions表 - 决策记录
-- ============================================
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    atom_id TEXT,                    -- 关联的Atom
    
    -- 决策内容
    type TEXT NOT NULL,              -- 'trade', 'strategy', 'risk', 'allocation'
    symbol TEXT,                     -- 股票代码(如果是交易决策)
    action TEXT NOT NULL,            -- 'buy', 'sell', 'hold', 'watch'
    
    -- 决策参数
    confidence REAL,                 -- 置信度 0-1
    urgency INTEGER,                 -- 紧急程度 1-5
    impact INTEGER,                  -- 影响程度 1-5
    
    -- 状态追踪
    status TEXT DEFAULT 'pending',   -- 'pending', 'approved', 'rejected', 'executed', 'cancelled'
    executed_at TIMESTAMP,           -- 执行时间
    execution_result TEXT,           -- 执行结果JSON
    
    -- 决策链(递归决策)
    parent_id TEXT,                  -- 父决策ID
    chain_depth INTEGER DEFAULT 0,   -- 决策链深度
    chain_json TEXT,                 -- 完整决策链JSON
    
    -- 来源追踪
    source_squad TEXT,               -- 来源Squad
    source_skills TEXT,              -- 使用的SKILL列表JSON
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (atom_id) REFERENCES atoms(id),
    FOREIGN KEY (parent_id) REFERENCES decisions(id)
);

-- Decisions索引
CREATE INDEX IF NOT EXISTS idx_decisions_type ON decisions(type);
CREATE INDEX IF NOT EXISTS idx_decisions_symbol ON decisions(symbol);
CREATE INDEX IF NOT EXISTS idx_decisions_action ON decisions(action);
CREATE INDEX IF NOT EXISTS idx_decisions_status ON decisions(status);
CREATE INDEX IF NOT EXISTS idx_decisions_confidence ON decisions(confidence);

-- ============================================
-- 3. Signals表 - 交易/分析信号
-- ============================================
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    atom_id TEXT,                    -- 关联的Atom
    
    -- 信号内容
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL,       -- 'breakout', 'reversal', 'momentum', 'value', 'risk'
    direction TEXT NOT NULL,         -- 'bullish', 'bearish', 'neutral'
    strength REAL NOT NULL,          -- 强度 0-1
    
    -- 信号参数
    timeframe TEXT,                  -- '1m', '5m', '15m', '1h', '1d', '1w'
    price_at_signal REAL,            -- 信号时价格
    target_price REAL,               -- 目标价
    stop_loss REAL,                  -- 止损价
    
    -- 信号来源
    source TEXT,                     -- 'tushare', 'technical', 'fundamental', 'news', 'composite'
    source_skills TEXT,              -- 使用的SKILL列表JSON
    
    -- 验证追踪
    validated BOOLEAN DEFAULT 0,     -- 是否已验证
    validated_at TIMESTAMP,          -- 验证时间
    validation_result TEXT,          -- 验证结果JSON
    pnl REAL,                        -- 实际盈亏(验证后)
    
    -- 上下文
    context_json TEXT,               -- 完整上下文JSON
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (atom_id) REFERENCES atoms(id)
);

-- Signals索引
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_signals_direction ON signals(direction);
CREATE INDEX IF NOT EXISTS idx_signals_strength ON signals(strength);
CREATE INDEX IF NOT EXISTS idx_signals_validated ON signals(validated);
CREATE INDEX IF NOT EXISTS idx_signals_created ON signals(created_at);

-- ============================================
-- 4. Squad执行任务表
-- ============================================
CREATE TABLE IF NOT EXISTS squad_tasks (
    id TEXT PRIMARY KEY,
    squad_id TEXT NOT NULL,
    task_type TEXT NOT NULL,         -- 'analysis', 'research', 'screening', 'validation'
    
    -- 任务内容
    description TEXT NOT NULL,
    parameters TEXT,                 -- 任务参数JSON
    
    -- 执行状态
    status TEXT DEFAULT 'pending',   -- 'pending', 'running', 'completed', 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- 执行结果
    result TEXT,                     -- 结果摘要
    result_data TEXT,                -- 完整结果JSON
    output_atoms TEXT,               -- 产出的Atom ID列表JSON
    
    -- 性能追踪
    execution_time_ms INTEGER,       -- 执行时间(毫秒)
    skills_used TEXT,                -- 使用的SKILL列表
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (squad_id) REFERENCES squads(id)
);

-- Squad Tasks索引
CREATE INDEX IF NOT EXISTS idx_squad_tasks_squad ON squad_tasks(squad_id);
CREATE INDEX IF NOT EXISTS idx_squad_tasks_type ON squad_tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_squad_tasks_status ON squad_tasks(status);

-- ============================================
-- 5. Squads表 - Squad定义
-- ============================================
CREATE TABLE IF NOT EXISTS squads (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    domain TEXT,                     -- 专业领域
    
    -- Squad配置
    skills TEXT NOT NULL,            -- SKILL列表JSON
    max_workers INTEGER DEFAULT 5,
    priority INTEGER DEFAULT 3,      -- 1-5, 越高越优先
    
    -- 状态
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 6. 同步日志表 - KIWI↔Prime同步记录
-- ============================================
CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 同步方向
    direction TEXT NOT NULL,         -- 'KIWI_TO_PRIME', 'PRIME_TO_KIWI'
    sync_type TEXT NOT NULL,         -- 'atom', 'decision', 'signal', 'memo'
    
    -- 同步内容
    item_id TEXT NOT NULL,           -- 同步项ID
    item_kind TEXT,                  -- 项目类型
    
    -- 同步操作
    action TEXT NOT NULL,            -- 'create', 'update', 'delete', 'sync'
    
    -- 状态
    status TEXT DEFAULT 'pending',   -- 'pending', 'success', 'failed', 'conflict'
    error_message TEXT,              -- 错误信息
    
    -- 元数据
    source_version INTEGER,          -- 源版本
    target_version INTEGER,          -- 目标版本
    
    -- 时间戳
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- 冲突解决
    resolution TEXT,                 -- 'source_wins', 'target_wins', 'merge', 'manual'
    resolved_by TEXT,                -- 解决者
    resolved_at TIMESTAMP
);

-- Sync Log索引
CREATE INDEX IF NOT EXISTS idx_sync_direction ON sync_log(direction);
CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_log(status);
CREATE INDEX IF NOT EXISTS idx_sync_item ON sync_log(item_id);
CREATE INDEX IF NOT EXISTS idx_sync_attempted ON sync_log(attempted_at);

-- ============================================
-- 7. 系统状态表 - 运行时状态持久化
-- ============================================
CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT DEFAULT 'string', -- 'string', 'int', 'float', 'json', 'bool'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 8. 改进循环记录表
-- ============================================
CREATE TABLE IF NOT EXISTS improvement_cycles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_number INTEGER NOT NULL,   -- 循环编号
    
    -- 改进内容
    component TEXT NOT NULL,         -- 'skill', 'squad', 'decision', 'sync', 'search'
    issue_description TEXT,
    improvement_action TEXT,
    
    -- 执行状态
    status TEXT DEFAULT 'planned',   -- 'planned', 'executed', 'verified', 'failed'
    executed_at TIMESTAMP,
    verified_at TIMESTAMP,
    
    -- 效果评估
    before_metrics TEXT,             -- 改进前指标JSON
    after_metrics TEXT,              -- 改进后指标JSON
    improvement_score REAL,          -- 改进效果评分
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Improvement索引
CREATE INDEX IF NOT EXISTS idx_improvement_cycle ON improvement_cycles(cycle_number);
CREATE INDEX IF NOT EXISTS idx_improvement_component ON improvement_cycles(component);
CREATE INDEX IF NOT EXISTS idx_improvement_status ON improvement_cycles(status);

-- ============================================
-- 9. 性能指标表
-- ============================================
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    
    -- 维度
    component TEXT,                  -- 组件名称
    squad_id TEXT,                   -- Squad ID(可选)
    
    -- 时间
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 标签
    tags TEXT                        -- JSON标签
);

-- Performance索引
CREATE INDEX IF NOT EXISTS idx_perf_name ON performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_perf_component ON performance_metrics(component);
CREATE INDEX IF NOT EXISTS idx_perf_recorded ON performance_metrics(recorded_at);

-- ============================================
-- 初始化默认Squad数据
-- ============================================
INSERT OR IGNORE INTO squads (id, name, description, domain, skills, priority) VALUES
('prime_council', 'Prime Council', 'Meta-level coordination and final decision authority', 'meta', '["meta_coordination", "final_decision"]', 5),
('intelligence_core', 'Intelligence Core', 'Knowledge synthesis and strategic analysis', 'intelligence', '["knowledge_graph", "semantic_search", "pattern_recognition"]', 4),
('execution_force', 'Execution Force', 'Real-time trading and execution operations', 'execution', '["market_data", "order_execution", "risk_control"]', 4),
('validation_guard', 'Validation Guard', 'Quality assurance and verification', 'validation', '["backtesting", "verification", "audit"]', 3),
('research_lab', 'Research Lab', 'Deep research and innovation', 'research', '["fundamental_analysis", "technical_analysis", "sector_research"]', 3),
('integration_hub', 'Integration Hub', 'External system integration', 'integration', '["feishu", "tushare", "prime_mcp"]', 4);

-- ============================================
-- 初始化系统状态
-- ============================================
INSERT OR IGNORE INTO system_state (key, value, value_type) VALUES
('db_version', '2.2.0', 'string'),
('db_initialized_at', datetime('now'), 'string'),
('prime_mode', 'active', 'string'),
('kiwi_mode', 'active', 'string'),
('level3_mode', 'active', 'string'),
('last_sync_timestamp', '0', 'int'),
('total_atoms', '0', 'int'),
('total_decisions', '0', 'int'),
('total_signals', '0', 'int');
