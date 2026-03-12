import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid

from src.core import config
from src.memory.schema import DB_PATH


class MemoryManager:
    """Handles all memory operations for the agent."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            import os
            self.db_path = os.path.join(os.getcwd(), getattr(config, 'MEMORY_DB_PATH', "agent_memory.db"))
        else:
            self.db_path = db_path
    
    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    # -------------------------
    # Task History Operations
    # -------------------------
    
    def save_task(
        self,
        task: str,
        complexity: str,
        tools_used: List[str],
        success: bool,
        execution_time: float,
        result_summary: str,
        error_count: int = 0
    ) -> int:
        """Save completed task to history."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO task_history 
            (task, complexity, tools_used, success, execution_time, result_summary, error_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task,
            complexity,
            json.dumps(tools_used),
            success,
            execution_time,
            result_summary[:500],  # Truncate long results
            error_count
        ))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
        
    def save_code_execution(self, code_snippet: str, success: bool, generated_files: List[str]):
        """Save a code execution record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Ensure table exists
        cursor.execute('''CREATE TABLE IF NOT EXISTS code_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            code_snippet TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            generated_files TEXT
        )''')
        
        cursor.execute("""
            INSERT INTO code_executions (code_snippet, success, generated_files)
            VALUES (?, ?, ?)
        """, (code_snippet, success, json.dumps(generated_files)))
        conn.commit()
        conn.close()

    def get_code_executions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent code executions."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT timestamp, code_snippet, success, generated_files
                FROM code_executions
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()
            
            executions = []
            for row in rows:
                executions.append({
                    'timestamp': row[0],
                    'code_snippet': row[1],
                    'success': bool(row[2]),
                    'generated_files': json.loads(row[3]) if row[3] else []
                })
            return executions
        except sqlite3.OperationalError:
            conn.close()
            return []
    
    def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task history."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, task, timestamp, complexity, tools_used, success, execution_time
            FROM task_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            tasks.append({
                'id': row[0],
                'task': row[1],
                'timestamp': row[2],
                'complexity': row[3],
                'tools_used': json.loads(row[4]) if row[4] else [],
                'success': bool(row[5]),
                'execution_time': row[6]
            })
        
        return tasks
    
    def search_similar_tasks(self, task: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Find similar past tasks (simple keyword matching for Phase 4)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Simple approach: search for tasks containing key words
        keywords = task.lower().split()[:3]  # First 3 words
        if not keywords:
            return []
            
        # Build LIKE query for each keyword
        where_clauses = " OR ".join(["task LIKE ?" for _ in keywords])
        query = f"""
            SELECT id, task, complexity, tools_used, success, execution_time
            FROM task_history
            WHERE {where_clauses}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        params = [f"%{kw}%" for kw in keywords] + [limit]
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            tasks.append({
                'id': row[0],
                'task': row[1],
                'complexity': row[2],
                'tools_used': json.loads(row[3]) if row[3] else [],
                'success': bool(row[4]),
                'execution_time': row[5]
            })
        
        return tasks
    
    # -------------------------
    # File Cache Operations
    # -------------------------
    
    def cache_file_metadata(
        self,
        path: str,
        size: int,
        line_count: int,
        word_count: int,
        content_hash: str
    ):
        """Cache file metadata to skip re-validation."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO file_cache
            (path, last_accessed, size, line_count, word_count, content_hash)
            VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?)
        """, (path, size, line_count, word_count, content_hash))
        
        conn.commit()
        conn.close()
    
    def get_file_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """Get cached file metadata."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT path, last_accessed, size, line_count, word_count, content_hash
            FROM file_cache
            WHERE path = ?
        """, (path,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'path': row[0],
                'last_accessed': row[1],
                'size': row[2],
                'line_count': row[3],
                'word_count': row[4],
                'content_hash': row[5]
            }
        return None
    
    def cleanup_file_cache(self, days: int = 30):
        """Remove file cache entries older than specified days."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(days=days)
        cursor.execute("""
            DELETE FROM file_cache
            WHERE last_accessed < ?
        """, (cutoff,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted
    
    # -------------------------
    # Tool Performance Operations
    # -------------------------
    
    def update_tool_performance(
        self,
        tool_name: str,
        success: bool,
        response_time: float
    ):
        """Update tool performance statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get current stats
        cursor.execute("""
            SELECT total_calls, successful_calls, failed_calls, avg_response_time
            FROM tool_performance
            WHERE tool_name = ?
        """, (tool_name,))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing
            total = row[0] + 1
            successful = row[1] + (1 if success else 0)
            failed = row[2] + (0 if success else 1)
            avg_time = (row[3] * row[0] + response_time) / total
            
            cursor.execute("""
                UPDATE tool_performance
                SET total_calls = ?,
                    successful_calls = ?,
                    failed_calls = ?,
                    avg_response_time = ?,
                    last_failure_time = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE tool_name = ?
            """, (
                total,
                successful,
                failed,
                avg_time,
                datetime.now() if not success else None,
                tool_name
            ))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO tool_performance
                (tool_name, total_calls, successful_calls, failed_calls, avg_response_time, last_failure_time)
                VALUES (?, 1, ?, ?, ?, ?)
            """, (
                tool_name,
                1 if success else 0,
                0 if success else 1,
                response_time,
                datetime.now() if not success else None
            ))
        
        conn.commit()
        conn.close()
    
    def get_tool_stats(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get performance stats for a tool."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tool_name, total_calls, successful_calls, failed_calls, 
                   avg_response_time, last_failure_time
            FROM tool_performance
            WHERE tool_name = ?
        """, (tool_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            total = row[1]
            success_rate = (row[2] / total) if total > 0 else 0.0
            
            return {
                'tool_name': row[0],
                'total_calls': row[1],
                'successful_calls': row[2],
                'failed_calls': row[3],
                'success_rate': success_rate,
                'avg_response_time': row[4],
                'last_failure_time': row[5]
            }
        return None
    
    def get_all_tool_stats(self) -> List[Dict[str, Any]]:
        """Get stats for all tools."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tool_name, total_calls, successful_calls, failed_calls, avg_response_time
            FROM tool_performance
            ORDER BY total_calls DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        stats = []
        for row in rows:
            total = row[1]
            success_rate = (row[2] / total) if total > 0 else 0.0
            stats.append({
                'tool_name': row[0],
                'total_calls': row[1],
                'success_rate': success_rate,
                'avg_response_time': row[4]
            })
        
        return stats
    
    # -------------------------
    # Session Memory Operations
    # -------------------------
    
    def save_session_task(
        self,
        session_id: str,
        task_index: int,
        task: str,
        result: str
    ):
        """Save task to current session memory."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO session_memory
            (session_id, task_index, task, result)
            VALUES (?, ?, ?, ?)
        """, (session_id, task_index, task, result[:500]))
        
        conn.commit()
        conn.close()
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent tasks from current session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_index, task, result, timestamp
            FROM session_memory
            WHERE session_id = ?
            ORDER BY task_index DESC
            LIMIT ?
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'task_index': row[0],
                'task': row[1],
                'result': row[2],
                'timestamp': row[3]
            })
        
        return history
    
    def clear_session(self, session_id: str):
        """Clear session memory."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM session_memory WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
    
    # -------------------------
    # Utility Operations
    # -------------------------
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get overall memory statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Task count
        cursor.execute("SELECT COUNT(*) FROM task_history")
        total_tasks = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute("SELECT COUNT(*) FROM task_history WHERE success = 1")
        successful_tasks = cursor.fetchone()[0]
        
        # Cached files
        cursor.execute("SELECT COUNT(*) FROM file_cache")
        cached_files = cursor.fetchone()[0]
        
        # Tools tracked
        cursor.execute("SELECT COUNT(*) FROM tool_performance")
        tracked_tools = cursor.fetchone()[0]
        
        conn.close()
        
        success_rate = (successful_tasks / total_tasks) if total_tasks > 0 else 0.0
        
        return {
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': success_rate,
            'cached_files': cached_files,
            'tracked_tools': tracked_tools
        }
    
    def clear_all_memory(self):
        """Clear all memory (destructive operation)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM task_history")
        cursor.execute("DELETE FROM file_cache")
        cursor.execute("DELETE FROM tool_performance")
        cursor.execute("DELETE FROM session_memory")
        
        conn.commit()
        conn.close()
