# 🐺 Wolf Report - Git 化遷移計劃書 (v99.0)
## 規格開發計劃書 (Specification & Development Plan)

**目標**：將現有 Colab 專案結構化為可復現的 Git Repository，支援跨平台（Colab → Kaggle → RunPod）無縫接力執行。

**版本**：v99.0  
**日期**：2025-12-06  
**狀態**：Ready for Development  

---

## 第一部分：項目背景與現狀

### 1.1 當前系統
- **環境**：Google Colab T4 GPU
- **進度**：1207/2554 篇文章已分析（~47% 完成）
- **核心工具**：Ollama + gemma3:4b LLM、SQLite (wolf_report.db)、PyMuPDF、gdown
- **問題**：Colab 免費額度即將用完，需遷移至 Kaggle 或其他平台繼續執行

### 1.2 遷移目標
1. **Colab → Kaggle**：無縫接力（讀取舊 DB，接續分析）
2. **程式碼標準化**：適應多平台環境差異（路徑、掛載方式）
3. **自動化佈署**：一行指令完成環境準備
4. **跨平台復現性**：同一套程式碼在任何平台都能跑

---

## 第二部分：Git 倉庫結構設計

### 2.1 資料夾樹狀結構（最終目標）
```
wolf_report/
├── .git/                      # Git 版本控制 (自動生成)
├── .gitignore                 # [需製作] Git 忽略規則
├── README.md                  # [需製作] 專案說明文件
├── LICENSE                    # [選用] MIT 或 Apache 2.0
│
├── src/                       # [需製作] 程式碼主目錄
│   ├── __init__.py           # Python 套件初始化
│   ├── main.py               # [需製作] 主程式 (改寫自 Colab v98.0)
│   ├── config.py             # [需製作] 配置檔 (路徑、參數定義)
│   ├── ollama_setup.py       # [需製作] Ollama 安裝與啟動模組
│   ├── db_manager.py         # [需製作] 資料庫初始化與同步模組
│   ├── downloader.py         # [需製作] 文章下載模組
│   ├── analyzer.py           # [需製作] AI 分析邏輯模組
│   └── utils.py              # [需製作] 工具函式 (Log、Display 等)
│
├── scripts/                   # [需製作] 環境佈署腳本
│   ├── setup_env.sh          # [需製作] 一鍵安裝腳本 (Bash)
│   ├── setup_kaggle.sh       # [需製作] Kaggle 專用啟動腳本
│   ├── download_db.py        # [需製作] 從 GDrive/Kaggle 下載 DB 的腳本
│   └── cleanup.sh            # [需製作] 清理臨時檔案
│
├── data/                      # [目錄結構] 資料存放區
│   ├── .gitkeep              # [需製作] 佔位符 (確保資料夾被追蹤)
│   └── wolf_report.db        # [方案 A] 或由 download_db.py 自動放入
│
├── docs/                      # [目錄結構] 下載的文章暫存區
│   └── .gitkeep              # [需製作] 佔位符
│
├── logs/                      # [目錄結構] 執行日誌
│   └── .gitkeep              # [需製作] 佔位符
│
└── requirements.txt           # [需製作] Python 依賴套件列表
```

### 2.2 檔案清單與責任

| 檔案 | 類型 | 說明 | 優先級 |
|------|------|------|--------|
| `.gitignore` | 設定 | 排除 `docs/*.txt`, `__pycache__`, `*.log` 等 | 🔴 必須 |
| `README.md` | 文件 | 說明如何 clone、setup、執行 | 🔴 必須 |
| `requirements.txt` | 設定 | pip 套件列表 | 🔴 必須 |
| `src/main.py` | 程式 | 主程式 (改寫自 v98.0) | 🔴 必須 |
| `src/config.py` | 程式 | 全局配置 (路徑、參數) | 🟡 強烈建議 |
| `src/ollama_setup.py` | 程式 | Ollama 安裝邏輯 | 🟡 強烈建議 |
| `src/db_manager.py` | 程式 | DB 初始化、複製、同步邏輯 | 🟡 強烈建議 |
| `src/downloader.py` | 程式 | 文章下載邏輯 (real_download) | 🟡 強烈建議 |
| `src/analyzer.py` | 程式 | 分析邏輯 (analyze_item、Ollama 調用) | 🟡 強烈建議 |
| `src/utils.py` | 程式 | 工具函式 (LogManager、DisplayManager) | 🟡 強烈建議 |
| `scripts/setup_env.sh` | 腳本 | 自動佈署環境 | 🟡 強烈建議 |
| `scripts/setup_kaggle.sh` | 腳本 | Kaggle 專用啟動 | 🟢 建議 |
| `scripts/download_db.py` | 腳本 | DB 下載工具 | 🟢 建議 |
| 空資料夾 + `.gitkeep` | 結構 | `data/`, `docs/`, `logs/` | 🔴 必須 |

---

## 第三部分：具體程式碼規格

### 3.1 `.gitignore` 
```text
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
.sagemath/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# 專案相關
docs/*.txt
data/*.db
logs/*.log
.kaggle/
```

### 3.2 `requirements.txt`
```text
# Core dependencies
sqlite3  # 通常內建，但列出以示明確性
requests>=2.31.0
gdown>=5.1.0
pymupdf>=1.23.0  # fitz 的替代品
psutil>=5.9.0

# For Google Drive integration (optional)
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.100.0

# For better CLI output
tqdm>=4.66.0
colorama>=0.4.6
```

### 3.3 `src/config.py` (全局配置)
```python
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
```

### 3.4 `src/db_manager.py` (資料庫模組)
```python
"""
wolf_report - 資料庫管理模組
負責 DB 初始化、複製、同步、查詢等操作
"""
import os
import shutil
import sqlite3
from typing import Tuple, List
from src.config import INPUT_DB_PATH, WORKING_DB_PATH, PLATFORM

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

# 全局 DB 管理器實例
db = DatabaseManager()
```

### 3.5 `src/main.py` (主程式骨架)
```python
"""
wolf_report - 主程式 v99.0
自動化財經文章分析系統
支援 Colab、Kaggle、Local 多平台執行
"""
import sys
import os

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import *
from src.db_manager import db
from src.ollama_setup import setup_ollama
from src.downloader import real_download, extract_text
from src.analyzer import analyze_item
from src.utils import LogManager, DisplayManager
import sqlite3

def main():
    print("=" * 80)
    print(f"🐺 Wolf Report v99.0 | Platform: {PLATFORM}")
    print("=" * 80)
    
    # 1. 設置 Ollama
    setup_ollama()
    
    # 2. 初始化 Log 與 Display
    log_mgr = LogManager()
    stats = {"status": "初始化", "processed": 0, "total": 0, "unsynced": 0}
    display = DisplayManager(stats, log_mgr)
    display.start()
    
    unsynced_count = 0
    loop = 0
    
    try:
        # 取得待分析總數
        stats["total"] = db.get_pending_count()
        print(f"待分析: {stats['total']} 筆")
        
        while loop < MAX_LOOPS:
            loop += 1
            
            # 取得一批待分析的記錄
            rows = db.get_pending_batch(BATCH_SIZE)
            if not rows:
                stats["status"] = "無可用任務"
                break
            
            for row in rows:
                eid, link, src_type, local_path, dl_status, title = row
                stats["status"] = "工作中"
                stats["task"] = f"ID {eid}"
                
                # 下載文章
                if dl_status != 'success' or not local_path or not os.path.exists(local_path):
                    temp_path = os.path.join(DOCS_DIR, f"essay_{eid:04d}.txt")
                    ok, msg = real_download(link, temp_path)
                    if ok:
                        local_path = temp_path
                        db.update_download_status(eid, 'success', temp_path)
                    else:
                        log_mgr.update_log(eid, f"[ID: {eid:04d}]", f"❌ 下載失敗: {msg}", "ERROR")
                        db.update_download_status(eid, 'failed')
                        continue
                
                # 分析文章
                text = extract_text(local_path)
                if text and len(text) > 10:
                    t_name, t_score, t_summ = analyze_item(eid, text, title[:30], log_mgr)
                    db.insert_score(eid, t_name, t_score, t_summ)
                    db.update_analysis_status(eid, 'done')
                    
                    stats["processed"] += 1
                    unsynced_count += 1
                    stats["unsynced"] = unsynced_count
                else:
                    db.update_analysis_status(eid, 'skipped')
                
                # 批次同步
                if unsynced_count >= SYNC_INTERVAL:
                    stats["status"] = "同步中..."
                    db.commit()
                    unsynced_count = 0
                    stats["unsynced"] = 0
                    print(f"\n✅ 已同步 {stats['processed']} 筆")
        
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.commit()  # 最後同步
        display.stop()
        display.join()
        print("\n✅ 執行結束")

if __name__ == "__main__":
    main()
```

### 3.6 `scripts/setup_env.sh` (一鍵佈署)
```bash
#!/bin/bash
set -e  # 發生錯誤立即中止

echo "🚀 開始佈署 Wolf Report 環境..."

# 1. 升級 pip
echo "📦 升級 pip..."
pip install --upgrade pip

# 2. 安裝 Python 依賴
echo "📥 安裝 Python 套件..."
pip install -r requirements.txt

# 3. 建立資料夾結構
echo "📁 建立資料夾..."
mkdir -p data docs logs

# 4. 安裝 Ollama (如果沒有)
if ! command -v ollama &> /dev/null; then
    echo "🔧 安裝 Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama 已安裝"
fi

# 5. 啟動 Ollama 服務 (背景執行)
echo "🔥 啟動 Ollama 服務..."
ollama serve &
OLLAMA_PID=$!
sleep 5

# 6. 拉取模型
echo "📥 拉取 AI 模型 (gemma3:4b)..."
ollama pull gemma3:4b

echo ""
echo "✅ 環境佈署完成！"
echo "📝 接下來執行: python src/main.py"
echo ""
```

### 3.7 `README.md` (快速開始指南)
```markdown
# 🐺 Wolf Report - 自動化財經文章分析系統

## 快速開始

### 📦 前置條件
- Git
- Python 3.8+
- Google Colab / Kaggle / 本地環境

### 🚀 執行步驟

#### 1️⃣ Clone Repository
\`\`\`bash
git clone https://github.com/您的帳號/wolf_report.git
cd wolf_report
\`\`\`

#### 2️⃣ 執行佈署腳本
\`\`\`bash
bash scripts/setup_env.sh
\`\`\`

#### 3️⃣ (Kaggle 專用) 下載資料庫
上傳您最新的 \`wolf_report.db\` 到 Kaggle Dataset \`wolf-report-db\`，
或執行：
\`\`\`bash
python scripts/download_db.py
\`\`\`

#### 4️⃣ 啟動分析
\`\`\`bash
python src/main.py
\`\`\`

## 📂 資料夾說明
- \`src/\` - 主程式代碼
- \`scripts/\` - 佈署與維護腳本
- \`data/\` - 資料庫儲存位置
- \`docs/\` - 下載的文章臨時儲存
- \`logs/\` - 執行日誌

## 🔄 跨平台接力

### Colab → Kaggle
1. 在 Colab 執行完一批，下載 \`data/wolf_report.db\`
2. 上傳至 Kaggle Dataset \`wolf-report-db\`
3. 在 Kaggle Notebook clone 本 repo，執行 \`setup_env.sh\`，跑 \`main.py\`

### 中斷後恢復
程式會自動檢查資料庫的分析狀態，只處理 \`analysis_status != 'done'\` 的記錄。

## 📊 配置參數

編輯 \`src/config.py\` 修改：
- \`BATCH_SIZE\` - 每次處理筆數
- \`SYNC_INTERVAL\` - 同步間隔
- \`MODEL_NAME\` - AI 模型選擇

## 📝 日誌
執行日誌存於 \`logs/wolf_report.log\`

---
**版本**：v99.0 | **最後更新**：2025-12-06
```

---

## 第四部分：AI 助理執行指令

### 4.1 完整 Prompt (複製給您的 AI 助理)

> **【任務名稱】Wolf Report Git 化專案 (v99.0)**
>
> **【目標】** 根據上述規格，生成一個完整的可執行 Git Repository，支援跨平台自動化執行。
>
> **【任務清單】**
>
> **第一組：建立檔案結構**
> 1. 建立以下空資料夾，並在各資料夾內放入 `.gitkeep` 檔案：
>    - `data/`
>    - `docs/`
>    - `logs/`
>    - `src/`
>    - `scripts/`
> 
> 2. 在根目錄建立 `.gitignore` 檔案 (內容見規格書第 3.1 節)
>
> 3. 在根目錄建立 `requirements.txt` (內容見規格書第 3.2 節)
>
> **第二組：核心程式碼生成**
> 
> 4. 在 `src/` 資料夾內建立 `__init__.py` (可以是空檔)
>
> 5. 在 `src/` 資料夾內建立 `config.py` (內容見規格書第 3.3 節)
>    - 注意：自動偵測 PLATFORM (kaggle / colab / local)
>    - 正確設定各平台的路徑
>
> 6. 在 `src/` 資料夾內建立 `db_manager.py` (內容見規格書第 3.4 節)
>    - 實現 DatabaseManager class
>    - 支援 Kaggle 模式的 DB 複製邏輯
>    - 包含所有 CRUD 操作
>
> 7. 在 `src/` 資料夾內建立 `ollama_setup.py`
>    - 函式 `setup_ollama()` - 安裝、啟動 Ollama、拉取 gemma3:4b 模型
>    - 根據當前環境檢查是否已安裝
>    - 參考原 Colab v98.0 中的 `install_ollama_if_needed` 和 `ensure_ollama_warmup` 邏輯
>
> 8. 在 `src/` 資料夾內建立 `downloader.py`
>    - 函式 `extract_gdoc_id(url)` - 從 Google Drive / Docs URL 提取 ID
>    - 函式 `real_download(url, output_path)` - 下載文章，返回 (success: bool, msg: str)
>    - 函式 `extract_text(path)` - 從 PDF / TXT / Docs 提取文字
>    - 參考原 Colab v98.0 中的同名函式邏輯
>
> 9. 在 `src/` 資料夾內建立 `analyzer.py`
>    - 函式 `call_ollama(prompt: str) -> str` - 呼叫 Ollama API
>    - 函式 `analyze_item(eid, text, author_info, log_mgr) -> (target, score, summary)` - 三階段分析
>    - 參考原 Colab v98.0 中的 `call_ollama_verbose` 和 `analyze_item` 邏輯
>
> 10. 在 `src/` 資料夾內建立 `utils.py`
>     - Class `LogManager` - 線程安全的日誌管理
>     - Class `DisplayManager` - 實時顯示執行進度
>     - 參考原 Colab v98.0 的相同類別邏輯，但改為模組化
>
> 11. 在 `src/` 資料夾內建立 `main.py` (內容見規格書第 3.5 節)
>     - 主入口點，協調所有模組
>     - 支援中斷後恢復 (自動檢查 DB 狀態)
>     - 批次同步邏輯
>
> **第三組：佈署腳本**
>
> 12. 在 `scripts/` 資料夾內建立 `setup_env.sh` (內容見規格書第 3.6 節)
>     - 一鍵安裝環境
>     - 自動安裝 Ollama、Python 依賴、建立資料夾
>
> 13. 在 `scripts/` 資料夾內建立 `setup_kaggle.sh`
>     - 專為 Kaggle Notebook 優化的啟動腳本
>     - 自動 clone repo、執行 setup_env.sh、執行 main.py
>
> 14. 在 `scripts/` 資料夾內建立 `download_db.py`
>     - 函式：從 Google Drive 公開連結下載 wolf_report.db
>     - 或從 Kaggle API 下載 (如果可能)
>
> 15. 在 `scripts/` 資料夾內建立 `cleanup.sh`
>     - 刪除臨時檔案 (`docs/*.txt`, `*.log`)
>     - 保留資料庫
>
> **第四組：文件**
>
> 16. 在根目錄建立 `README.md` (內容見規格書第 3.7 節)
>
> 17. 在根目錄建立 `LICENSE` (MIT 或 Apache 2.0)
>
> **【關鍵要求】**
> - 所有程式碼必須支援 Python 3.8+
> - 所有檔案必須正確設定 UTF-8 編碼
> - 所有 Bash 腳本必須有 `#!/bin/bash` 開頭與 `set -e`
> - 所有相對路徑應從專案根目錄開始
> - 程式碼應有基本的錯誤處理與 try-except
> - 日誌應輸出到 `logs/` 目錄
>
> **【輸出驗收標準】**
> 1. 專案可以用 `git init && git add . && git commit -m "Initial commit"` 初始化
> 2. 在 Kaggle 上可以執行 `bash scripts/setup_kaggle.sh` 一鍵啟動
> 3. 程式可以自動檢測環境 (Kaggle / Colab / Local) 並調整路徑
> 4. 中斷後重新執行可以自動恢復 (不重複分析已完成的記錄)
> 5. 日誌清晰，包含 emoji 與時戳

---

## 第五部分：後續步驟

### 5.1 給您的行動清單
1. ☐ 複製上述 Prompt 給您的 AI 助理
2. ☐ 等待 AI 生成檔案結構
3. ☐ 在本地驗證（`python src/main.py --test` 或在 Colab 跑一次）
4. ☐ 將專案 Push 到 GitHub (Create a new repository)
5. ☐ 準備您的 Kaggle Dataset (`wolf-report-db`)，上傳目前的 `wolf_report.db`
6. ☐ 在 Kaggle 建立 Notebook，執行 `bash scripts/setup_kaggle.sh`

### 5.2 Git 操作範例
```bash
# 在您的本地電腦 (或 Colab)
cd ~/wolf_report
git init
git add .
git commit -m "Initial commit: Wolf Report v99.0 Git structure"
git branch -M main
git remote add origin https://github.com/您的帳號/wolf_report.git
git push -u origin main
```

### 5.3 Kaggle 執行指令
```bash
# 在 Kaggle Notebook Cell 中
!git clone https://github.com/您的帳號/wolf_report.git
%cd wolf_report
!bash scripts/setup_kaggle.sh
```

---

## 第六部分：附錄

### A. 原 Colab v98.0 核心邏輯參考

您的 AI 助理在實現上述模組時，可以參考：
- **Ollama Setup**：原程式的 `install_ollama_if_needed()` 和 `ensure_ollama_warmup()`
- **Downloader**：原程式的 `extract_gdoc_id()`, `real_download()`, `extract_text()`
- **Analyzer**：原程式的 `call_ollama_verbose()`, `analyze_item()`
- **Utils**：原程式的 `LogManager` 和 `DisplayManager` class
- **Main Loop**：原程式的主迴圈邏輯 (批次取資料、分析、同步)

### B. 環境變數設置 (如需自定義)
```bash
export WOLF_MODEL_NAME="qwen3:8b"  # 改用其他模型
export WOLF_BATCH_SIZE="20"        # 改變批次大小
export WOLF_SYNC_INTERVAL="100"    # 改變同步間隔
```

### C. 常見問題排查
- **Ollama 連線失敗**：確保 `ollama serve` 已啟動
- **DB 不存在**：Kaggle 必須先上傳 Dataset，或程式會初始化新 DB
- **下載失敗**：檢查 URL 有效性、網路連線、Google Drive 分享設定
- **模型太大**：改用 `gemma3:1b` 或 `qwen3:1b`

---

**計劃書版本**：v99.0  
**建立日期**：2025-12-06  
**狀態**：Ready for Handoff to AI Assistant
