import os
import time
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen3:4b")
TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))
KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "1h")

def _post(url, payload, retries=3, backoff=2):
    for i in range(retries):
        try:
            r = requests.post(url, json=payload, timeout=TIMEOUT)
            r.raise_for_status()
            return r
        except requests.exceptions.ReadTimeout:
            if i == retries - 1:
                raise
            time.sleep(backoff * (i + 1))

def embed(text: str):
    r = _post(f"{OLLAMA_HOST}/api/embeddings", {"model": EMBED_MODEL, "prompt": text})
    return r.json()["embedding"]

def chat(prompt: str):
    payload = {
        "model": CHAT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "keep_alive": KEEP_ALIVE,
        "options": {"temperature": 0},
    }
    r = _post(f"{OLLAMA_HOST}/api/chat", payload)
    return r.json()["message"]["content"]
