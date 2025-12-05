import requests
import yaml
import time

class OllamaClient:
    def __init__(self, config_path: str = "config/model.yaml"):
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except:
            self.config = {}
            
        self.host = self.config.get("ollama_host", "http://localhost:11434")
        self.model = self.config.get("model", "ministral-3:3b")
        self.options = self.config.get("options", {})

    def call(self, prompt: str, system: str = None, max_retries: int = 3) -> str:
        url = f"{self.host}/api/chat"
        payload = {
            "model": self.model,
            "messages": [],
            "stream": False,
            "options": self.options
        }
        if system:
            payload["messages"].append({"role": "system", "content": system})
        payload["messages"].append({"role": "user", "content": prompt})

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, timeout=self.options.get("timeout", 120))
                response.raise_for_status()
                return response.json().get("message", {}).get("content", "").strip()
            except Exception as e:
                print(f"[Ollama] Retry {attempt+1}/{max_retries} failed: {e}")
                time.sleep(2)
        return ""
