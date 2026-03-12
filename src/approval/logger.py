import sqlite3
import os

DB_PATH = 'agent_memory.db'

class ApprovalLogger:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def log_approval(self, step_description: str, action_type: str, risk_level: str, user_decision: str, reason: str = ""):
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO approval_history 
                       (step_description, action_type, risk_level, user_decision, reason) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (step_description, action_type, risk_level, user_decision, reason)
                )
                conn.commit()
        except Exception as e:
            print(f"Error logging approval: {e}")

    def get_recent_approvals(self, limit=10):
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM approval_history ORDER BY timestamp DESC LIMIT ?', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []

    def get_approval_stats(self):
        stats = {'APPROVED': 0, 'REJECTED': 0}
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_decision, COUNT(*) as count FROM approval_history GROUP BY user_decision')
                for row in cursor.fetchall():
                    if row['user_decision'] in stats:
                        stats[row['user_decision']] = row['count']
        except Exception:
            pass
        return stats

approval_logger = ApprovalLogger()
