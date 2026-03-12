import sqlite3
import os

DB_PATH = 'agent_memory.db'

class PreferenceManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        # Ensures table exists during init_db, but we can double check here
        
    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_preference(self, action_type: str) -> str:
        """Returns 'ALWAYS_ASK', 'NEVER_ASK', or 'AUTO'"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT policy FROM approval_preferences WHERE action_type = ?', (action_type,))
                row = cursor.fetchone()
                if row:
                    return row['policy']
        except Exception:
            pass
        return "AUTO"

    def set_preference(self, action_type: str, policy: str):
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT OR REPLACE INTO approval_preferences (action_type, policy) VALUES (?, ?)',
                    (action_type, policy)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving preference: {e}")
            return False

    def get_all_preferences(self) -> dict:
        prefs = {}
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT action_type, policy FROM approval_preferences')
                for row in cursor.fetchall():
                    prefs[row['action_type']] = row['policy']
        except Exception:
            pass
        return prefs

    def reset_preferences(self):
        default_prefs = {
            'file_read': 'NEVER_ASK',
            'file_write': 'AUTO',
            'file_delete': 'ALWAYS_ASK',
            'web_search': 'NEVER_ASK',
            'http_post': 'ALWAYS_ASK',
            'calculation': 'NEVER_ASK',
            'text_analyze': 'NEVER_ASK'
        }
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM approval_preferences')
                for act, pol in default_prefs.items():
                    cursor.execute('INSERT INTO approval_preferences (action_type, policy) VALUES (?, ?)', (act, pol))
                conn.commit()
        except Exception as e:
            print(f"Error resetting preferences: {e}")

preference_manager = PreferenceManager()
