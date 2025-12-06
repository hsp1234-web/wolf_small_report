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
# 注意：在某些環境 (如 Colab) 可能需要 nohup
echo "🔥 啟動 Ollama 服務..."
# 嘗試檢查服務是否已經在跑
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
    sleep 5
else
    echo "✅ Ollama 服務已在執行"
fi

# 6. 拉取模型
echo "📥 拉取 AI 模型 (gemma3:4b)..."
ollama pull gemma3:4b

echo ""
echo "✅ 環境佈署完成！"
echo "📝 接下來執行: python src/main.py"
echo ""
