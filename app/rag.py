from typing import List
from app.embeddings import embed_text
from app.ollama_client import chat
from app.qdrant_store import ensure_collection, upsert, search
from app.qdrant_store import list_docs as _store_list_docs
from app.qdrant_store import delete_by_doc_id as _store_delete_by_doc_id
from app.qdrant_store import get_chunks_by_doc_id as _store_get_chunks

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

def index_document(text: str, filename: str | None = None, mime_type: str | None = None):
    import uuid
    from datetime import datetime
    doc_id = uuid.uuid4().hex
    parts = chunk(text)
    vectors = [embed_text(t) for t in parts]
    ensure_collection(len(vectors[0]))
    uploaded_at = datetime.utcnow().isoformat()
    payloads = [
        {
            "text": t,
            "doc_id": doc_id,
            "source_filename": filename or "manual",
            "mime_type": mime_type or "text/plain",
            "uploaded_at": uploaded_at,
            "chunk_index": i,
        }
        for i, t in enumerate(parts)
    ]
    upsert(vectors, payloads)
    return {"doc_id": doc_id, "chunks": len(parts), "filename": filename or "manual"}

def list_docs():
    return _store_list_docs()

def delete_doc(doc_id: str):
    _store_delete_by_doc_id(doc_id)

def get_doc_preview(doc_id: str, limit: int = 2):
    return _store_get_chunks(doc_id, limit=limit)

def answer(query: str, top_k: int = 5):
    qv = embed_text(query)
    ensure_collection(len(qv))
    hits = search(qv, limit=top_k)
    if not hits:
        return "No relevant context found. Please index documents first."
    context = "\n\n".join(h.payload["text"] for h in hits)
    prompt = (
        "You are a helpful assistant. Use the provided context when relevant."
        "\n\nContext:\n" + context + "\n\nQuestion: " + query
    )
    return chat(prompt)
