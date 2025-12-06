# 🐺 Wolf Report - Automated Financial Article Analysis System

## Overview
Wolf Report is an automated system designed to analyze financial articles using local LLMs (Ollama). It supports a seamless workflow across **Google Colab**, **Kaggle**, and **Local Environments**.

**Current Version**: v99.0

## 📦 Requirements

The project relies on the following Python packages. These are listed in `requirements.txt`:

```text
sqlite3          # Standard library (usually included)
requests>=2.31.0 # For HTTP requests
gdown>=5.1.0     # For downloading from Google Drive
pymupdf>=1.23.0  # For PDF/text extraction (module name: fitz)
psutil>=5.9.0    # For system monitoring
tqdm>=4.66.0     # For progress bars
colorama>=0.4.6  # For colored terminal output
google-auth-oauthlib>=1.0.0      # (Optional) GDrive Auth
google-auth-httplib2>=0.2.0      # (Optional) GDrive Auth
google-api-python-client>=2.100.0 # (Optional) GDrive Auth
```

**System Requirements**:
- **Python**: 3.8 or higher
- **Ollama**: Required for running the LLM (`gemma3:4b` by default)
- **Git**: For version control

## 🚀 Quick Start

### 1. Installation

Clone the repository and enter the directory:
```bash
git clone <your-repo-url>
cd wolf_report
```

Run the setup script to install dependencies and Ollama (if missing):
```bash
# Recommended for Linux/Colab/Kaggle
bash scripts/setup_env.sh
```

Or manually install Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration (Optional)
Check `src/config.py` if you need to adjust:
- `MODEL_NAME`: Default is `gemma3:4b`.
- `BATCH_SIZE`: Number of articles to process per batch.

### 3. Running the System

**On Local / Colab:**
```bash
python src/main.py
```

**On Kaggle:**
The project includes a specialized script for Kaggle notebooks:
```bash
bash scripts/setup_kaggle.sh
```

### 4. Database Handling
The system uses a SQLite database (`wolf_report.db`).
- **Initial Run**: A new empty database will be created in `data/`.
- **Importing Data**: If you have an existing DB, place it in `data/wolf_report.db` or use the download script:
```bash
# Edit the script with your DB URL first!
python scripts/download_db.py
```

## 📂 Project Structure

```
wolf_report/
├── src/               # Core Source Code
│   ├── config.py      # Configuration & Platform Detection
│   ├── main.py        # Main Entry Point
│   ├── db_manager.py  # Database Operations
│   ├── downloader.py  # Article Fetching Logic
│   ├── analyzer.py    # LLM Analysis Logic
│   ├── ollama_setup.py# Ollama Management
│   └── utils.py       # Logging & Display Utilities
├── scripts/           # Automation Scripts
│   ├── setup_env.sh   # Environment Setup
│   ├── setup_kaggle.sh# Kaggle Launcher
│   └── cleanup.sh     # Temp File Cleaner
├── data/              # Database Storage
├── docs/              # Temporary Text Files
├── logs/              # Execution Logs
└── requirements.txt   # Python Dependencies
```

## 🔄 Cross-Platform Workflow

1.  **Run on Colab/Local**: Process new articles.
2.  **Sync**: The `wolf_report.db` is updated automatically.
3.  **Transfer**: Upload the `data/wolf_report.db` to a Kaggle Dataset.
4.  **Run on Kaggle**: The system detects the Kaggle environment and loads the DB from input to continue processing.

## 📝 License
MIT License
