"""
wolf_report - 分析邏輯模組
負責呼叫 Ollama 進行文章分析 (標的、評分、摘要)
"""
import requests
import re
from .config import MODEL_NAME, OLLAMA_HOST, PROMPT_TARGET, PROMPT_SCORE, PROMPT_SUMMARY

def call_ollama(prompt: str) -> str:
    """
    呼叫 Ollama API
    """
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1, 
                "num_ctx": 8192
            }
        }
        res = requests.post(url, json=payload, timeout=90) # 分析長文可能較久，給 90s
        if res.status_code == 200:
            return res.json().get("response", "").strip()
        else:
            return f"ERR: HTTP {res.status_code}"
    except Exception as e:
        return f"ERR: {str(e)[:20]}"

def analyze_item(eid, text, c_info, log_mgr):
    """
    對單篇文章進行三階段分析
    Returns: (target_name, analysis_score, short_summary)
    """
    
    # 1. 識別標的
    log_mgr.update_log(eid, c_info, "⏳ 1/3 識別標的...", "BUSY")
    
    prompt_1 = PROMPT_TARGET.format(text=text[:1500])
    resp_1 = call_ollama(prompt_1)
    
    # 清理回應
    target = resp_1.split("\n")[0].replace("。", "").replace("標的：", "").strip()
    
    # 2. 評分
    log_mgr.update_log(eid, c_info, f"🎯 {target} | ⏳ 2/3 評分...", "BUSY")
    
    prompt_2 = PROMPT_SCORE.format(text=text[:2000])
    resp_2 = call_ollama(prompt_2)
    
    # 提取數字
    match = re.search(r'\d+', resp_2)
    score = match.group() if match else "N/A"
    
    # 3. 摘要
    log_mgr.update_log(eid, c_info, f"🎯 {target} | ⭐ {score} | ⏳ 3/3 摘要...", "BUSY")
    
    prompt_3 = PROMPT_SUMMARY.format(text=text[:2000])
    resp_3 = call_ollama(prompt_3)
    
    summary = resp_3.replace("\n", " ").strip()
    
    # 完成
    final_res = f"🎯 {target} | ⭐ {score}/15 | 📝 {summary[:15]}..."
    log_mgr.update_log(eid, c_info, final_res, "SUCCESS")
    
    return target, score, summary
