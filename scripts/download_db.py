"""
Script to download wolf_report.db from external source (e.g. Google Drive)
如果使用者有備份 DB 的連結，可以在此設定
"""
import os
import sys

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.downloader import real_download
from src.config import DATA_DIR

DB_URL = "" # TODO: 在此填入您的 Google Drive 公開分享連結 (若有的話)
TARGET_PATH = os.path.join(DATA_DIR, "wolf_report.db")

def main():
    if os.path.exists(TARGET_PATH):
        print(f"✅ 資料庫已存在: {TARGET_PATH}")
        choice = input("是否覆蓋? (y/N): ")
        if choice.lower() != 'y':
            return

    if not DB_URL:
        print("❌ 請先在 script 中設定 DB_URL")
        return

    print(f"📥 正在下載資料庫 from {DB_URL}...")
    success, msg = real_download(DB_URL, TARGET_PATH)
    
    if success:
        print("✅ 下載成功")
    else:
        print(f"❌ 下載失敗: {msg}")

if __name__ == "__main__":
    main()
