import os

files = {
    "specs/system_spec.md": """# System Specification: LLM-Based Essay Scoring Pipeline (Wolf Report)

## 1. Project Overview
目標是建立一條自動化、可中斷、可重跑的評分流水線。
- **Input**: LINE 匯出的 CSV 連結 (links_with_type.csv)。
- **Processing**: 下載原文 -> Ollama (Ministral-3b) 4輪評分 -> 寫入 SQLite。
- **Output**: Markdown 報告檔 (.md) 與 SQLite 資料庫。

## 2. Directory Structure
wolf_small_report/
├── config/
├── data/
├── src/
└── specs/
""",

    "config/paths.yaml": """raw_dir: "./data/raw/"
docs_dir: "./data/docs/"
output_db: "./data/output/db/wolf_small_report.db"
output_md_dir: "./data/output/md/"
""",

    "config/model.yaml": """ollama_host: "http://localhost:11434"
model: "ministral-3:3b"
options:
  temperature: 0.3
  num_ctx: 4096
  timeout: 120
""",

    "src/core/__init__.py": "",
    
    "src/core/db.py": """import sqlite3
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
""",

    "src/core/ollama_client.py": """import requests
import yaml
import time

class OllamaClient:
    def __init__(self, config_path: str = "config/model.yaml"):
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except:
            self.config = {}
            
        self.host = self.config.get("ollama_host", "http://localhost:11434")
        self.model = self.config.get("model", "ministral-3:3b")
        self.options = self.config.get("options", {})

    def call(self, prompt: str, system: str = None, max_retries: int = 3) -> str:
        url = f"{self.host}/api/chat"
        payload = {
            "model": self.model,
            "messages": [],
            "stream": False,
            "options": self.options
        }
        if system:
            payload["messages"].append({"role": "system", "content": system})
        payload["messages"].append({"role": "user", "content": prompt})

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, timeout=self.options.get("timeout", 120))
                response.raise_for_status()
                return response.json().get("message", {}).get("content", "").strip()
            except Exception as e:
                print(f"[Ollama] Retry {attempt+1}/{max_retries} failed: {e}")
                time.sleep(2)
        return ""
""",

    ".gitignore": """# Python
__pycache__/
*.py[cod]
*.so

# Data & Database
data/
!data/.gitkeep
*.db
*.sqlite3

# Environments
.env
venv/
.ipynb_checkpoints/
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {path}")

dirs = ["data/raw", "data/docs", "data/output/db", "data/output/md"]
for d in dirs:
    os.makedirs(d, exist_ok=True)
    with open(f"{d}/.gitkeep", "w") as f:
        f.write("")

print("\n專案初始化腳本寫入完成。")
