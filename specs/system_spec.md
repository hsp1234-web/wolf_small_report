# System Specification: LLM-Based Essay Scoring Pipeline (Wolf Report)

## 1. Project Overview
目標是建立一條自動化、可中斷、可重跑的評分流水線。
- **Input**: LINE 匯出的 CSV 連結 (links_with_type.csv)。
- **Processing**: 下載原文 -> Ollama (Ministral-3b) 4輪評分 -> 寫入 SQLite。
- **Output**: Markdown 報告檔 (.md) 與 SQLite 資料庫。

## 2. Directory Structure
wolf_small_report/
├── config/
├── data/
├── src/
└── specs/
