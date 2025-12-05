import pandas as pd
from src.core.db import DBHandler
import logging
import os

# 設定日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Orchestrator:
    def __init__(self):
        """
        初始化 Orchestrator，並建立一個 DBHandler 實例。
        """
        self.db_handler = DBHandler()

    def ingest_csv(self, csv_path: str):
        """
        讀取 CSV 檔案，並將其資料寫入資料庫的 'essays' 表格。
        此函式會檢查連結是否存在，以避免重複寫入。

        Args:
            csv_path (str): CSV 檔案的路徑。
        """
        if not os.path.exists(csv_path):
            logging.error(f"檔案不存在於指定路徑：{csv_path}")
            return

        logging.info(f"開始從 {csv_path} 進行 CSV 資料注入")
        try:
            # 讀取 CSV 檔案
            df = pd.read_csv(csv_path)
            logging.info(f"成功從 CSV 檔案讀取 {len(df)} 行資料。 সন")

            # 連接資料庫
            self.db_handler.connect()
            cursor = self.db_handler.conn.cursor()

            new_records_count = 0
            for index, row in df.iterrows():
                link = row.get('link')

                # 如果 link 欄位為空，則跳過此行
                if pd.isna(link):
                    logging.warning(f"第 {index + 2} 行因為缺少 'link' 而被跳過。 সন")
                    continue

                # 步驟 1: 檢查 link 是否已存在
                cursor.execute("SELECT id FROM essays WHERE link = ?", (link,))
                existing_essay = cursor.fetchone()

                if existing_essay:
                    logging.info(f"連結 '{link}' 已存在於資料庫中，跳過。 সন")
                    continue

                # 步驟 2: 若不存在，則插入新紀錄
                try:
                    insert_data = {
                        "id": int(row['id']),
                        "title_text": row.get('text', ''),
                        "link": link,
                        "source_type": row.get('source_type', '')
                    }
                    
                    cursor.execute(
                        "INSERT INTO essays (id, title_text, link, source_type) VALUES (:id, :title_text, :link, :source_type)",
                        insert_data
                    )
                    new_records_count += 1
                    logging.info(f"已插入新的文章，ID: {insert_data['id']}")

                except KeyError as e:
                    logging.error(f"CSV 第 {index + 2} 行缺少預期欄位: {e}")
                except Exception as e:
                    logging.error(f"處理第 {index + 2} 行時發生錯誤: {row.to_dict()}。錯誤訊息: {e}")

            # 提交資料庫交易
            self.db_handler.conn.commit()
            logging.info(f"CSV 資料注入完成。總共插入 {new_records_count} 筆新紀錄。 সন")

        except FileNotFoundError:
            logging.error(f"在指定路徑找不到檔案：{csv_path}")
        except Exception as e:
            logging.error(f"CSV 資料注入過程中發生錯誤：{e}")
        finally:
            # 確保資料庫連線已關閉
            if self.db_handler.conn:
                self.db_handler.close()
                logging.info("資料庫連線已關閉。 সন")

if __name__ == '__main__':
    # 根據 SDD 文件，路徑應為 'data/output/links_with_type.csv'
    # 但您提供的路徑是 'wolf_small_report-20251205T183946Z-1-001 (2)/...' 
    # 此處我們使用您提供的路徑，請根據您的實際檔案位置進行調整。
    csv_file_path = 'wolf_small_report-20251205T183946Z-1-001 (2)/wolf_small_report/output/links_with_type.csv'

    # 1. 初始化資料庫 (如果表格不存在，會自動建立)
    print("正在初始化資料庫...")
    db_initializer = DBHandler()
    db_initializer.init_db()
    db_initializer.close()
    print("資料庫初始化完成。 সন")

    # 2. 執行注入腳本
    print("\n開始執行資料注入腳本...")
    orchestrator = Orchestrator()
    orchestrator.ingest_csv(csv_file_path)
    print("腳本執行完畢。 সন")
