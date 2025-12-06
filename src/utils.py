"""
wolf_report - 工具函式模組
包含 LogManager 和 DisplayManager
"""
import time
import threading
import collections
import psutil
import os
from .config import LOG_FILE

class LogManager:
    def __init__(self, max_lines=5):
        self.buffer_logs = collections.deque(maxlen=max_lines)
        self.lock = threading.Lock()
        
    def update_log(self, eid, c_info, r_info, level="INFO"):
        """
        更新日誌
        eid: 文章 ID
        c_info: 顯示資訊 (如 ID, 作者)
        r_info: 結果資訊 (如 下載完成, 分析結果)
        level: INFO, SUCCESS, ERROR, BUSY
        """
        with self.lock:
            found = False
            new_buffer = collections.deque(maxlen=self.buffer_logs.maxlen)
            # 嘗試更新現有的 log entry
            for item in self.buffer_logs:
                if item[0] == eid:
                    item = (eid, level, c_info, r_info)
                    found = True
                new_buffer.append(item)
            if not found:
                new_buffer.append((eid, level, c_info, r_info))
            self.buffer_logs = new_buffer
            
        # 同時寫入檔案
        self._write_to_file(eid, c_info, r_info, level)

    def _write_to_file(self, eid, c_info, r_info, level):
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f"[{timestamp}] [{level}] [{eid}] {c_info} - {r_info}\n"
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_msg)
        except Exception as e:
            pass # 避免日誌寫入失敗導致程式崩潰

    def get_logs(self):
        with self.lock:
            return list(self.buffer_logs)

class DisplayManager(threading.Thread):
    def __init__(self, stats, log_mgr, max_log_lines=5):
        super().__init__()
        self.stats = stats
        self.log_mgr = log_mgr
        self.max_log_lines = max_log_lines
        self.running = True
        self.daemon = True
        
    def run(self):
        # 初始清除一次
        # 在某些環境下 clear_output 需要特定 import，這邊簡化處理
        try:
            from IPython.display import clear_output
            has_ipython = True
        except ImportError:
            has_ipython = False

        while self.running:
            self._refresh(has_ipython)
            time.sleep(0.5) # 0.5s 刷新

    def _refresh(self, has_ipython):
        logs = self.log_mgr.get_logs()
        status = self.stats.get("status", "待機")
        task = self.stats.get("task", "")
        processed = self.stats.get("processed", 0)
        total = self.stats.get("total", 0)
        unsynced = self.stats.get("unsynced", 0)

        # 構建輸出字串
        output_str = []
        output_str.append(f"📊 Wolf Report (Status: {status})")
        output_str.append("=" * 80)

        # 顯示 logs
        for eid, level, l1, l2 in logs:
            # 簡化顏色代碼，避免不同終端機支援問題，這裡主要針對支援 ANSI 的終端
            color = "\033[92m" if level=="SUCCESS" else "\033[91m" if level=="ERROR" else "\033[93m" if level=="BUSY" else "\033[97m"
            reset = "\033[0m"
            
            l1_short = l1[:75] + "..." if len(l1) > 75 else l1
            l2_short = l2[:75] + "..." if len(l2) > 75 else l2
            output_str.append(f"\033[90m  {l1_short}{reset}")
            output_str.append(f"{color}  └── {l2_short}{reset}")
            output_str.append("-" * 40)

        # 補齊空白行
        current_lines = len(logs) * 3
        target_lines = self.max_log_lines * 3
        if current_lines < target_lines:
            output_str.append("\n" * (target_lines - current_lines))

        # 系統狀態
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        progress = processed / total if total > 0 else 0
        bar_len = 20
        filled_len = int(bar_len * progress)
        bar = "█" * filled_len + "░" * (bar_len - filled_len)

        status_line = f"CPU:{cpu}% | RAM:{ram}% | {bar} ({processed}/{total}) | ⚠️ 未同步: {unsynced}"
        output_str.append(status_line)

        final_output = "\n".join(output_str)

        if has_ipython:
            from IPython.display import clear_output
            clear_output(wait=True)
            print(final_output, end="")
        else:
            # 一般終端機簡單刷新模式 (ANSI escape code to clear screen or move cursor)
            # 這裡簡單使用 clear 目前畫面，或者只在最後輸出
            # 為了兼容性，我們嘗試使用 ANSI code 清除畫面並移動游標到左上角
            print("\033[2J\033[H" + final_output, end="")

    def stop(self):
        self.running = False
