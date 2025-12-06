"""
wolf_report - 資料庫管理模組
負責 DB 初始化、複製、同步、查詢等操作
"""
import os
import shutil
import sqlite3
from typing import Tuple, List
from .config import INPUT_DB_PATH, WORKING_DB_PATH, PLATFORM

class DatabaseManager:
    def __init__(self):
        self.db_path = WORKING_DB_PATH
        self._init_local_db()
    
    def _init_local_db(self):
        """
        Kaggle 模式：複製 INPUT_DB 到 WORKING_DB
        Colab 模式：直接使用 WORKING_DB
        Local 模式：如果不存在則初始化新的
        """
        if PLATFORM == "kaggle":
            if os.path.exists(INPUT_DB_PATH):
                print(f"🚚 複製資料庫: {INPUT_DB_PATH} -> {WORKING_DB_PATH}")
                # 確保目標目錄存在
                os.makedirs(os.path.dirname(WORKING_DB_PATH), exist_ok=True)
                shutil.copy2(INPUT_DB_PATH, WORKING_DB_PATH)
                print("✅ 複製完成")
            else:
                print("⚠️  Kaggle Dataset 中找不到 wolf_report.db，初始化新檔...")
                self._create_new_db()
        else:
            if not os.path.exists(self.db_path):
                print(f"⚠️  資料庫不存在: {self.db_path}，初始化新檔...")
                self._create_new_db()
            else:
                print(f"✅ 使用現有資料庫: {self.db_path}")
    
    def _create_new_db(self):
        """建立全新的資料庫 schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # essays 表
        c.execute("""
            CREATE TABLE IF NOT EXISTS essays (
                id INTEGER PRIMARY KEY,
                link TEXT UNIQUE,
                source_type TEXT,
                local_text_path TEXT,
                download_status TEXT DEFAULT 'pending',
                analysis_status TEXT DEFAULT 'pending',
                original_title TEXT
            )
        """)
        
        # essay_scores 表
        c.execute("""
            CREATE TABLE IF NOT EXISTS essay_scores (
                essay_id INTEGER PRIMARY KEY,
                target_name TEXT,
                analysis_score TEXT,
                short_summary TEXT,
                FOREIGN KEY(essay_id) REFERENCES essays(id)
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"✅ 新資料庫已建立: {self.db_path}")
    
    def get_connection(self):
        """取得 DB 連線"""
        return sqlite3.connect(self.db_path)
    
    def get_pending_count(self) -> int:
        """查詢待分析的筆數"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM essays WHERE analysis_status != 'done' AND download_status != 'failed'")
        count = c.fetchone()[0]
        conn.close()
        return count
    
    def get_pending_batch(self, batch_size: int) -> List[Tuple]:
        """取得一批待分析的記錄"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, link, source_type, local_text_path, download_status, original_title 
            FROM essays 
            WHERE analysis_status != 'done' AND download_status != 'failed' 
            LIMIT ?
        """, (batch_size,))
        rows = c.fetchall()
        conn.close()
        return rows
    
    def update_download_status(self, essay_id: int, status: str, local_path: str = None):
        """更新下載狀態"""
        conn = self.get_connection()
        c = conn.cursor()
        if local_path:
            c.execute("UPDATE essays SET download_status=?, local_text_path=? WHERE id=?", 
                     (status, local_path, essay_id))
        else:
            c.execute("UPDATE essays SET download_status=? WHERE id=?", (status, essay_id))
        conn.commit()
        conn.close()
    
    def update_analysis_status(self, essay_id: int, status: str):
        """更新分析狀態"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE essays SET analysis_status=? WHERE id=?", (status, essay_id))
        conn.commit()
        conn.close()
    
    def insert_score(self, essay_id: int, target_name: str, score: str, summary: str):
        """插入分析結果"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO essay_scores (essay_id, target_name, analysis_score, short_summary)
            VALUES (?, ?, ?, ?)
        """, (essay_id, target_name, score, summary))
        conn.commit()
        conn.close()
    
    def commit(self):
        """手動 commit (如果需要)"""
        conn = self.get_connection()
        conn.commit()
        conn.close()

# 全局 DB 管理器實例，通常由 lazy loading 較好，但這裡為了簡單直接初始化
# 警告：這意味著 import db_manager 就會嘗試建立連線或初始化 DB
db = DatabaseManager()
