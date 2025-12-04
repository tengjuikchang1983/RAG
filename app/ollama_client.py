import os
import time
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "ministral-3:8b")
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

def _get(url, retries=2, backoff=2):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=TIMEOUT)
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

def list_models():
    r = _get(f"{OLLAMA_HOST}/api/tags")
    j = r.json()
    ms = j.get("models", [])
    return [m.get("name") for m in ms if m.get("name")]

def set_chat_model(name: str):
    global CHAT_MODEL
    CHAT_MODEL = name

def set_embed_model(name: str):
    global EMBED_MODEL
    EMBED_MODEL = name

def set_host(url: str):
    global OLLAMA_HOST
    OLLAMA_HOST = url

def get_chat_model():
    return CHAT_MODEL

def get_embed_model():
    return EMBED_MODEL

def get_host():
    return OLLAMA_HOST
