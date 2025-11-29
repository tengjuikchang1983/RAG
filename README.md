# Local Ollama RAG (Qwen3:4b) with Qdrant + Streamlit

## Prerequisites
- macOS with Ollama installed and serving on `localhost:11434`
- Models on host:
  - `qwen3:4b` for chat
  - `nomic-embed-text` (or your preferred embedding model)
- Docker Desktop

## Connectivity Tests
- Host → Ollama: `curl http://localhost:11434/api/tags`
- Container → Host Ollama (macOS): `docker run --rm curlimages/curl http://host.docker.internal:11434/api/tags`

## Start the Stack
```bash
docker compose up --build
```
- App: `http://localhost:8501`
- Qdrant: `http://localhost:6333`

## Configuration
- `docker-compose.yml` sets:
  - `OLLAMA_HOST=http://host.docker.internal:11434`
  - `OLLAMA_CHAT_MODEL=qwen3:4b`
  - `OLLAMA_EMBED_MODEL=nomic-embed-text`
  - `QDRANT_URL=http://qdrant:6333`
  - `QDRANT_COLLECTION=docs`

## Usage
1. Open the app at `http://localhost:8501`
2. Paste text into "Index Text" and click "Index"
3. Ask a question in "Ask" and click "Ask"

## Notes
- `host.docker.internal` allows containers to reach host services on macOS
- To change models, edit environment variables in `docker-compose.yml`
- If you prefer not to use Ollama for embeddings, install `sentence-transformers` and swap embedding generation in `app/rag.py`
