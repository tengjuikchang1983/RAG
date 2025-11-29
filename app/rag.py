from typing import List
from app.embeddings import embed_text
from app.ollama_client import chat
from app.qdrant_store import ensure_collection, upsert, search
from app.guardrails import validate_query, redact, require_context

def chunk(text: str, size: int = 800, overlap: int = 100) -> List[str]:
    parts = []
    step = max(1, size - overlap)
    for i in range(0, len(text), step):
        parts.append(text[i : i + size])
    return parts

def index_texts(texts: List[str]):
    vectors = [embed_text(t) for t in texts]
    ensure_collection(len(vectors[0]))
    upsert(vectors, [{"text": t} for t in texts])

def answer(query: str, top_k: int = 5):
    ok, msg = validate_query(query)
    if not ok:
        raise Exception(msg)
    qv = embed_text(query)
    ensure_collection(len(qv))
    hits = search(qv, limit=top_k)
    if not hits and require_context():
        return "Insufficient context. Please index documents first."
    context = "\n\n".join(h.payload["text"] for h in hits)
    context = redact(context)
    safe_query = redact(query)
    prompt = (
        "You are a helpful assistant. Use only the provided context, refuse unsafe or unrelated requests."
        "\n\nContext:\n" + context + "\n\nQuestion: " + safe_query
    )
    return chat(prompt)
