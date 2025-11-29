import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

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
