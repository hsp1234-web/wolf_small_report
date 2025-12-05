import sqlite3
import os
import yaml
from typing import List, Dict, Any

class DBHandler:
    def __init__(self, db_path: str = None):
        if db_path is None:
            try:
                with open("config/paths.yaml", "r") as f:
                    config = yaml.safe_load(f)
                db_path = config["output_db"]
            except:
                db_path = "data/output/db/wolf_small_report.db"
            
        self.db_path = db_path
        self._ensure_dir()
        self.conn = None

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()

    def init_db(self):
        self.connect()
        cursor = self.conn.cursor()
        
        # Essays Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS essays (
                id INTEGER PRIMARY KEY,
                title_text TEXT,
                link TEXT,
                source_type TEXT,
                download_status TEXT DEFAULT 'pending',
                local_path TEXT,
                meta_status TEXT DEFAULT 'pending',
                analysis_status TEXT DEFAULT 'pending',
                risk_status TEXT DEFAULT 'pending',
                summary_status TEXT DEFAULT 'pending',
                markdown_status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Meta Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS essay_meta (
                essay_id INTEGER PRIMARY KEY,
                target_name TEXT,
                target_code TEXT,
                topic_type TEXT,
                FOREIGN KEY(essay_id) REFERENCES essays(id)
            )
        ''')

        # Scores Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS essay_scores (
                essay_id INTEGER PRIMARY KEY,
                analysis_score INTEGER,
                analysis_comment TEXT,
                risk_score INTEGER,
                risk_comment TEXT,
                FOREIGN KEY(essay_id) REFERENCES essays(id)
            )
        ''')

        # Outputs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS essay_outputs (
                essay_id INTEGER PRIMARY KEY,
                short_summary TEXT,
                markdown_path TEXT,
                FOREIGN KEY(essay_id) REFERENCES essays(id)
            )
        ''')

        # Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                essay_id INTEGER,
                step TEXT,
                error_type TEXT,
                message TEXT,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print(f"Database initialized at {self.db_path}")

    def mark_status(self, essay_id, step, status, local_path=None):
        col = f"{step}_status"
        query = f"UPDATE essays SET {col} = ?"
        params = [status]
        if local_path:
            query += ", local_path = ?"
            params.append(local_path)
        query += " WHERE id = ?"
        params.append(essay_id)
        self.conn.execute(query, tuple(params))
        self.conn.commit()

if __name__ == "__main__":
    db = DBHandler()
    db.init_db()
    db.close()
