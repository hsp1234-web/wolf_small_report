"""
wolf_report - Ollama 安裝與管理模組
負責檢測環境、安裝 Ollama、拉取模型
"""
import shutil
import subprocess
import time
import requests
import sys
from .config import MODEL_NAME

def setup_ollama():
    """主要入口：確保 Ollama 已安裝、執行中且模型已就緒"""
    install_ollama_if_needed()
    ensure_ollama_warmup()

def install_ollama_if_needed():
    """檢查並安裝 Ollama"""
    if shutil.which("ollama"):
        print("✅ Ollama 已安裝")
        return

    print("🚀 檢測到未安裝 Ollama，開始自動安裝...")
    try:
        # 使用官方安裝腳本
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
        print("✅ Ollama 安裝完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ollama 安裝失敗: {e}")
        sys.exit(1)

def ensure_ollama_warmup():
    """確保 Ollama 服務執行中且模型已下載"""
    print(f"🔥 正在檢查 Ollama 服務...")
    
    # 嘗試啟動服務 (如果已經在跑，這行通常沒壞處，或者會被忽略)
    # 在背景啟動
    subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 等待服務回應
    connected = False
    for _ in range(10):
        try:
            requests.get("http://localhost:11434", timeout=2)
            connected = True
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            print(".", end="", flush=True)
    print("")
            
    if not connected:
        print("❌ 無法連接到 Ollama 服務，請檢查 Logs")
        return # 這裡不強制 exit，讓使用者可能有機會手動修

    print(f"📥 檢查模型 {MODEL_NAME}...")
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if MODEL_NAME not in res.stdout:
            print(f"⬇️ 模型尚未下載，正在拉取 {MODEL_NAME}...")
            subprocess.run(["ollama", "pull", MODEL_NAME], check=True)
            print(f"✅ 模型 {MODEL_NAME} 拉取完成")
        else:
            print(f"✅ 模型 {MODEL_NAME} 已存在")
    except Exception as e:
        print(f"❌ 模型檢查或下載失敗: {e}")
