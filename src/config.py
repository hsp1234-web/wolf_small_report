"""
wolf_report - 全局配置模組
定義所有環境相關的路徑、參數、常數
"""
import os
import sys

# ========== 環境檢測 ==========
PLATFORM = "kaggle" if "/kaggle/" in os.getcwd() else "colab" if "/content/" in os.getcwd() else "local"

# ========== 路徑定義 ==========
if PLATFORM == "kaggle":
    BASE_DIR = "/kaggle/working"
    INPUT_BASE_DIR = "/kaggle/input"
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DOCS_DIR = os.path.join(BASE_DIR, "docs")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    
    # Kaggle 的 Dataset 名稱 (由 Notebook 的 Data 頁面自動掛載)
    INPUT_DB_PATH = os.path.join(INPUT_BASE_DIR, "wolf-report-db", "wolf_report.db")
    WORKING_DB_PATH = os.path.join(DATA_DIR, "wolf_report.db")
    
elif PLATFORM == "colab":
    BASE_DIR = "/content"
    DRIVE_BASE = "/content/drive/MyDrive"
    PROJECT_NAME = "wolf_small_report"
    
    DATA_DIR = os.path.join(DRIVE_BASE, PROJECT_NAME, "output", "db")
    DOCS_DIR = os.path.join(DRIVE_BASE, PROJECT_NAME, "docs", "raw_text")
    LOGS_DIR = os.path.join(DRIVE_BASE, PROJECT_NAME, "logs")
    
    INPUT_DB_PATH = os.path.join(DATA_DIR, "wolf_report.db")
    WORKING_DB_PATH = INPUT_DB_PATH  # Colab 可直接讀寫 Drive
    
else:  # local
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DOCS_DIR = os.path.join(BASE_DIR, "docs")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    
    WORKING_DB_PATH = os.path.join(DATA_DIR, "wolf_report.db")
    INPUT_DB_PATH = WORKING_DB_PATH

# 建立必要資料夾
for dir_path in [DATA_DIR, DOCS_DIR, LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# ========== AI 模型設定 ==========
MODEL_NAME = "gemma3:4b"  # 可改為 "qwen3:8b" 或其他
OLLAMA_HOST = "http://localhost:11434"

# ========== 分析參數 ==========
BATCH_SIZE = 10              # 每次取多少筆進行分析
SYNC_INTERVAL = 50           # 多久同步一次 DB 到雲端
MAX_LOOPS = 1000             # 最多迴圈數

# ========== LLM 提示詞模板 ==========
PROMPT_TARGET = "文章：\n{text}\n分析哪支股票？只回【名稱 代碼】。"
PROMPT_SCORE = "文章：\n{text}\n給分析評分(1-15)。只回數字。"
PROMPT_SUMMARY = "文章：\n{text}\n繁中一句話摘要(30字內)。"

# ========== 日誌設定 ==========
LOG_FILE = os.path.join(LOGS_DIR, "wolf_report.log")
LOG_LEVEL = "INFO"

print(f"[Config] Platform: {PLATFORM} | DB: {WORKING_DB_PATH}")
