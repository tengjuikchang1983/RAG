import os
from typing import List
from app.ollama_client import embed as ollama_embed

USE_OLLAMA_EMBED = os.getenv("OLLAMA_EMBED_MODEL", "").strip().lower() not in ("", "none")

_st = None
_st_name = os.getenv("ST_EMBED_MODEL", "all-MiniLM-L6-v2")

def _ensure_st():
    global _st
    if _st is None:
        from sentence_transformers import SentenceTransformer
        _st = SentenceTransformer(_st_name)

def embed_text(text: str) -> List[float]:
    if USE_OLLAMA_EMBED:
        try:
            return ollama_embed(text)
        except Exception:
            pass
    _ensure_st()
    return _st.encode(text, normalize_embeddings=True).tolist()
