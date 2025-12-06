"""
wolf_report - 文章下載模組
負責從 Google Drive / Docs 下載檔案並提取文字
"""
import os
import re
import requests
import fitz  # pymupdf
try:
    import gdown
except ImportError:
    gdown = None

def extract_gdoc_id(url):
    """從 URL 提取 Google Doc/Drive ID"""
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else None

def real_download(url, output_path):
    """
    下載文章
    Return: (success: bool, msg: str)
    """
    # 檢查 gdown 是否可用 (雖在 requirements 中，但做個防呆)
    if gdown is None:
        return False, "缺少 gdown 套件"

    if "drive.google.com" not in url and "docs.google.com" not in url:
        return False, "Skip: 非 Google 連結"
        
    file_id = extract_gdoc_id(url)
    if not file_id:
        return False, "無效 ID"
        
    try:
        # 確保目錄存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if "docs.google.com/document" in url:
            # Google Doc: 嘗試匯出為 txt
            export_url = f"https://docs.google.com/document/d/{file_id}/export?format=txt"
            resp = requests.get(export_url, timeout=15)
            if resp.status_code == 200:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(resp.text)
                return True, "GDocs Downloaded"
            return False, f"Err: {resp.status_code}"
            
        elif "drive.google.com/file" in url:
            # Google Drive File: 使用 gdown
            # quiet=True 減少輸出, fuzzy=True 允許寬鬆匹配
            gdown.download(id=file_id, output=output_path, quiet=True, fuzzy=True)
            
            if os.path.exists(output_path):
                return True, "GDrive Downloaded"
            return False, "GDrive Download Fail (File not found)"
            
    except Exception as e:
        return False, f"Exception: {str(e)[:50]}"
        
    return False, "不支援的連結格式"

def extract_text(path):
    """
    從檔案 (PDF / TXT) 提取純文字
    """
    if not os.path.exists(path):
        return ""
        
    text = ""
    try:
        # 讀取前幾個 byte 判斷是否為 PDF
        with open(path, 'rb') as f:
            header = f.read(4)
            
        if header == b'%PDF':
            # PDF 處理
            doc = fitz.open(path)
            for page in doc:
                text += page.get_text() + "\n"
        else:
            # 純文字處理，寬容編碼
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
                
    except Exception as e:
        print(f"Text extraction error for {path}: {e}")
        return ""
        
    return text.strip()
