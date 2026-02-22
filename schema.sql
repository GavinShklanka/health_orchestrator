CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    module TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    model_name TEXT,
    temperature REAL,
    middleware_version TEXT,
    policy_pack_version TEXT,
    state_version INTEGER
);

CREATE TABLE IF NOT EXISTS tool_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    result_hash TEXT,
    executed_at TEXT NOT NULL,
    idempotency_key TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    approved_by TEXT NOT NULL,
    policy_level TEXT NOT NULL,
    approved_at TEXT NOT NULL,
    expiry TEXT,
    changes_summary TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    node_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    summary TEXT
);