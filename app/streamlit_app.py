import streamlit as st
from app.rag import chunk, index_texts, answer, index_document, list_docs, delete_doc, get_doc_preview
from app.qdrant_store import delete_all
from app.ingest import read_pdf, read_txt
from app.ollama_client import list_models, set_chat_model, set_embed_model, get_chat_model, get_embed_model, set_host, get_host
from app.embeddings import set_use_ollama_embed, set_st_model_name

st.set_page_config(page_title="Local Ollama RAG", layout="centered")
st.title("Local Ollama RAG (Ministral-3:8b + Qdrant)")

# Guardrails removed

st.header("Index Text")
title = st.text_input("Title (optional)")
text = st.text_area("Paste text to index", height=200)
if st.button("Index"):
    if text.strip():
        info = index_document(text, filename=(title.strip() or "manual"), mime_type="text/plain")
        st.success(f"Indexed {info['chunks']} chunks as '{info['filename']}'")
    else:
        st.warning("Please paste some text")

st.header("Upload Files")
files = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"], accept_multiple_files=True)
if st.button("Index Uploaded"):
    if files:
        total_chunks = 0
        for f in files:
            bytes_data = f.read()
            if f.type == "application/pdf" or f.name.lower().endswith(".pdf"):
                text_src = read_pdf(bytes_data)
                mime = "application/pdf"
            else:
                text_src = read_txt(bytes_data)
                mime = "text/plain"
            info = index_document(text_src, filename=f.name, mime_type=mime)
            total_chunks += info["chunks"]
        st.success(f"Indexed {total_chunks} chunks from {len(files)} file(s)")
    else:
        st.warning("Please upload files")

st.header("Ask")
q = st.text_input("Enter a question")
if st.button("Ask"):
    if q.strip():
        try:
            ans = answer(q)
            st.markdown(ans)
        except Exception as e:
            st.error(str(e))
    else:
        st.warning("Please enter a question")

st.header("Indexed Files")
docs = list_docs()
if docs:
    st.dataframe(
        {"filename": [d["source_filename"] for d in docs],
         "chunks": [d["chunks"] for d in docs],
         "uploaded_at": [d.get("uploaded_at", "") for d in docs]},
        hide_index=True,
    )
    options = {d["source_filename"]: d["doc_id"] for d in docs}
    selected = st.multiselect("Select files", list(options.keys()))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Preview First Chunks") and selected:
            # Preview only the first selected
            doc_id = options[selected[0]]
            chunks = get_doc_preview(doc_id)
            for i, ch in enumerate(chunks):
                st.markdown(f"**Chunk {i+1}:**\n\n{ch}")
    with col2:
        if st.button("Delete Selected") and selected:
            for name in selected:
                delete_doc(options[name])
            st.success(f"Deleted {len(selected)} document(s)")
            # Refresh list after deletion
            docs = list_docs()
        if st.button("Delete All"):
            delete_all()
            st.success("Deleted all documents in the vector store")
            docs = list_docs()
else:
    st.info("No indexed files yet.")
# Models
st.header("Models")
host = st.text_input("Ollama host", value=get_host())
if host.strip():
    set_host(host.strip())
model_names = []
try:
    model_names = list_models()
except Exception:
    model_names = []
chat_default = get_chat_model()
embed_default = get_embed_model()
if model_names:
    chat_model = st.selectbox("Chat model", options=model_names, index=(model_names.index(chat_default) if chat_default in model_names else 0))
    embed_model = st.selectbox("Embed model", options=model_names, index=(model_names.index(embed_default) if embed_default in model_names else 0))
else:
    chat_model = st.text_input("Chat model", value=chat_default)
    embed_model = st.text_input("Embed model", value=embed_default)
colm1, colm2 = st.columns(2)
with colm1:
    if st.button("Apply Models"):
        set_chat_model(chat_model)
        set_embed_model(embed_model)
        st.success("Models updated")
with colm2:
    use_ollama = st.checkbox("Use Ollama for embeddings", value=True)
    set_use_ollama_embed(use_ollama)
    if not use_ollama:
        st_model = st.text_input("SentenceTransformer model", value="all-MiniLM-L6-v2")
        if st.button("Apply ST Model"):
            set_st_model_name(st_model)
            st.success("SentenceTransformer model updated")
