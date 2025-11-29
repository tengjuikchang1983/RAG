from typing import List
from app.embeddings import embed_text
from app.ollama_client import chat
from app.qdrant_store import ensure_collection, upsert, search

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
    qv = embed_text(query)
    ensure_collection(len(qv))
    hits = search(qv, limit=top_k)
    context = "\n\n".join(h.payload["text"] for h in hits)
    prompt = (
        "You are a helpful assistant. Answer using the provided context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )
    return chat(prompt)
