#!/bin/bash
set -e

# Kaggle 專用啟動腳本
# 假設此 Repo 已經被 Clone 到 /kaggle/working/wolf_report (或者當前目錄)

echo "🚀 [Kaggle] 初始化 Wolf Report..."

# 給予執行權限
chmod +x scripts/setup_env.sh

# 執行環境佈署
./scripts/setup_env.sh

echo "🚀 [Kaggle] 開始執行主程式..."
python src/main.py
