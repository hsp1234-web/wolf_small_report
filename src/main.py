"""
wolf_report - 主程式 v99.0
自動化財經文章分析系統
支援 Colab、Kaggle、Local 多平台執行
"""
import sys
import os
import time

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import *
from src.db_manager import db
from src.ollama_setup import setup_ollama
from src.downloader import real_download, extract_text
from src.analyzer import analyze_item
from src.utils import LogManager, DisplayManager

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
        # 由於 display 線程在跑，這行 print 可能會被覆蓋，但還是留著
        # print(f"待分析: {stats['total']} 筆")
        
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
                
                # 準備顯示資訊
                c_info = f"[ID: {eid:04d}]"
                
                # 下載文章
                if dl_status != 'success' or not local_path or not os.path.exists(local_path):
                    # 檔名格式: essay_0001.txt
                    temp_path = os.path.join(DOCS_DIR, f"essay_{eid:04d}.txt")
                    
                    ok, msg = real_download(link, temp_path)
                    if ok:
                        local_path = temp_path
                        db.update_download_status(eid, 'success', temp_path)
                        log_mgr.update_log(eid, c_info, "📥 下載成功", "INFO")
                    else:
                        log_mgr.update_log(eid, c_info, f"❌ 下載失敗: {msg}", "ERROR")
                        db.update_download_status(eid, 'failed')
                        continue
                
                # 分析文章
                text = extract_text(local_path)
                if text and len(text) > 10:
                    # 原標題可能很長，截取前 20 字
                    title_short = title[:20] if title else "No Title"
                    display_info = f"{c_info} {title_short}"
                    
                    try:
                        t_name, t_score, t_summ = analyze_item(eid, text, display_info, log_mgr)
                        db.insert_score(eid, t_name, t_score, t_summ)
                        db.update_analysis_status(eid, 'done')
                    except Exception as ai_err:
                        log_mgr.update_log(eid, c_info, f"❌ 分析崩潰: {ai_err}", "ERROR")
                        # 標記失敗以免無限重試，或可選擇不標記以便下次重試
                        # db.update_analysis_status(eid, 'failed')
                    
                    stats["processed"] += 1
                    unsynced_count += 1
                    stats["unsynced"] = unsynced_count
                else:
                    log_mgr.update_log(eid, c_info, "⚠️ 內容過短或提取失敗", "ERROR")
                    db.update_analysis_status(eid, 'skipped')
                
                # 批次同步
                if unsynced_count >= SYNC_INTERVAL:
                    stats["status"] = "同步中..."
                    db.commit()
                    unsynced_count = 0
                    stats["unsynced"] = 0
                    time.sleep(1) # 讓使用者看到同步狀態
        
    except KeyboardInterrupt:
        print("\n使用者中斷執行...")
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        stats["status"] = "正在關閉..."
        db.commit()  # 最後同步
        display.stop()
        display.join()
        print("\n✅ 執行結束")

if __name__ == "__main__":
    main()
