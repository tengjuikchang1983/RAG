import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "docs")

client = QdrantClient(url=QDRANT_URL)

def ensure_collection(dim: int):
    names = [c.name for c in client.get_collections().collections]
    if COLLECTION not in names:
        client.create_collection(
            COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

def upsert(vectors, payloads):
    points = [PointStruct(id=i, vector=v, payload=p) for i, (v, p) in enumerate(zip(vectors, payloads))]
    client.upsert(collection_name=COLLECTION, points=points)

def search(query_vec, limit=5):
    return client.search(collection_name=COLLECTION, query_vector=query_vec, limit=limit)

def list_docs(limit=1000):
    points, _ = client.scroll(
        collection_name=COLLECTION,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )
    agg = {}
    for p in points:
        pl = p.payload or {}
        doc_id = pl.get("doc_id")
        if not doc_id:
            # Skip chunks without doc metadata
            continue
        info = agg.get(doc_id)
        if not info:
            agg[doc_id] = {
                "doc_id": doc_id,
                "source_filename": pl.get("source_filename", "unknown"),
                "uploaded_at": pl.get("uploaded_at"),
                "chunks": 1,
            }
        else:
            info["chunks"] += 1
    # Convert to list sorted by uploaded_at desc
    res = list(agg.values())
    res.sort(key=lambda x: (x.get("uploaded_at") or ""), reverse=True)
    return res

def delete_by_doc_id(doc_id: str):
    flt = Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))])
    client.delete(collection_name=COLLECTION, points_selector=flt)

def get_chunks_by_doc_id(doc_id: str, limit: int = 3):
    flt = Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))])
    points, _ = client.scroll(
        collection_name=COLLECTION,
        limit=limit,
        with_payload=True,
        with_vectors=False,
        filter=flt,
    )
    return [p.payload.get("text", "") for p in points]
