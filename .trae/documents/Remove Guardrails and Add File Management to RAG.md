## Summary
- Remove the current guardrail feature from both backend and UI.
- Enhance RAG to track per-file metadata, list indexed files, preview contents, and delete files via GUI.
- Use Qdrant payloads (with `doc_id`, `source_filename`, etc.) and filter-based deletes to keep operations simple and persistent across restarts.

## Code Changes
### Remove Guardrails
- Delete guardrail usage in backend:
  - Remove import from `app/rag.py:5` and all references in `answer()` (`app/rag.py:19-35`).
  - Simplify prompt; drop `validate_query`, `redact`, and `require_context` gating.
- Remove guardrail UI:
  - Remove imports and sidebar toggles in `app/streamlit_app.py:4` and `app/streamlit_app.py:9-15`.
- Optionally remove `app/guardrails.py` and any envs (`docker-compose.yml`) tied to guardrails.

### Persist Per-File Metadata in Index
- Do not merge uploaded files into a single blob.
- For each uploaded file:
  - Read text with existing `read_pdf` / `read_txt`.
  - Chunk separately using `chunk()`.
  - Generate a new `doc_id` (UUID) per file.
  - Build payload per chunk: `{"text", "doc_id", "source_filename", "mime_type", "uploaded_at", "chunk_index"}`.
  - Upsert vectors+payloads to Qdrant.

### Qdrant Store Enhancements
- Extend `app/qdrant_store.py` (current upsert is `app/qdrant_store.py:18-21`):
  - Keep `upsert(vectors, payloads)` for simple cases; add helpers:
    - `list_docs(limit=1000)`: `scroll` with `with_payload=True`, group by `doc_id` and aggregate `chunk_count`, `source_filename`, `uploaded_at`.
    - `delete_by_doc_id(doc_id)`: use `Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))])` to delete points.
    - `get_chunks_by_doc_id(doc_id, limit=3)`: fetch first chunks for preview.
  - Import needed models: `Filter`, `FieldCondition`, `MatchValue` from `qdrant_client.http.models`.

### RAG Orchestration Updates
- Add in `app/rag.py`:
  - `index_document(text: str, filename: Optional[str], mime_type: Optional[str])` that performs chunk → embed → ensure_collection → upsert with rich payloads.
  - `list_docs()` and `delete_doc(doc_id)` thin wrappers around qdrant store.
  - `get_doc_preview(doc_id)` returning first chunk(s).
- Update `answer(query, top_k=5)`:
  - Remove guardrail checks; if no hits, return a simple guidance string.
  - Prompt: "Use the provided context when relevant."

### Streamlit UI Enhancements
- Upload Files section:
  - Index each file individually: loop files → read → `index_document(...)` → show per-file success.
- Index Text section:
  - Add optional "Title" input; index text as its own document with a generated `doc_id` and `source_filename` = title or `"manual"`.
- New "Indexed Files" section:
  - Display a table of `filename/title`, `chunks`, `uploaded_at`.
  - Allow selecting one or multiple rows (e.g., via `st.data_editor` or `st.multiselect` on `doc_id`).
  - Actions:
    - `Preview`: show first 1-2 chunks from `get_doc_preview(doc_id)`.
    - `Delete Selected`: call `delete_doc(doc_id)` for each and refresh the list.

## Verification
- Functional:
  - Upload two files; confirm they appear individually in "Indexed Files" with correct chunk counts.
  - Ask a question; confirm answers draw from the uploaded context.
  - Delete one file; re-ask and observe its content no longer retrieved.
- Persistence:
  - Restart app; verify list still shows indexed files (Qdrant payloads persist).
- Edge cases:
  - Large files chunking and indexing still succeed.
  - Empty or unreadable files are skipped with a UI warning.

## Notes & Rationale
- Using filter-based deletes avoids needing stable point IDs.
- Grouping by `doc_id` enables user-facing file management while keeping chunk-level retrieval intact.
- Guardrails removal aligns with your request; if later needed, can reintroduce as optional toggles.

## Deliverables
- Updated `app/rag.py`, `app/qdrant_store.py`, and `app/streamlit_app.py` with the features above.
- Clean removal of `app/guardrails.py` references (and file if desired).
- Working UI for listing, previewing, and deleting indexed files.