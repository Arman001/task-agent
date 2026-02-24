import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "agent_memory.db")

SCHEMA = """
-- Task history: All executed tasks
CREATE TABLE IF NOT EXISTS task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    complexity TEXT,
    tools_used TEXT,  -- JSON array of tool names
    success BOOLEAN NOT NULL,
    execution_time REAL,  -- seconds
    result_summary TEXT,
    error_count INTEGER DEFAULT 0
);

-- File metadata cache: Avoid re-validating known files
CREATE TABLE IF NOT EXISTS file_cache (
    path TEXT PRIMARY KEY,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
    size INTEGER,
    line_count INTEGER,
    word_count INTEGER,
    content_hash TEXT
);

-- Tool performance: Track success rates
CREATE TABLE IF NOT EXISTS tool_performance (
    tool_name TEXT PRIMARY KEY,
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    failed_calls INTEGER DEFAULT 0,
    avg_response_time REAL DEFAULT 0.0,
    last_failure_time DATETIME,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Session memory: Current session context (cleared on restart)
CREATE TABLE IF NOT EXISTS session_memory (
    session_id TEXT NOT NULL,
    task_index INTEGER NOT NULL,
    task TEXT NOT NULL,
    result TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, task_index)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_task_timestamp ON task_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_file_accessed ON file_cache(last_accessed DESC);
CREATE INDEX IF NOT EXISTS idx_session ON session_memory(session_id, task_index);
"""

def init_db():
    """Initialize database with schema."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
