import streamlit as st
from app.rag import chunk, index_texts, answer
from app.ingest import read_pdf, read_txt
from app.guardrails import is_enabled, require_context, set_enabled, set_require_context, set_max_query_chars

st.set_page_config(page_title="Local Ollama RAG", layout="centered")
st.title("Local Ollama RAG (Qwen3:4b + Qdrant)")

st.sidebar.header("Guardrails")
en = st.sidebar.checkbox("Enable guardrails", value=is_enabled())
rc = st.sidebar.checkbox("Require indexed context", value=require_context())
mql = st.sidebar.slider("Max query length", min_value=100, max_value=8000, value=2000, step=100)
set_enabled(en)
set_require_context(rc)
set_max_query_chars(mql)

st.header("Index Text")
text = st.text_area("Paste text to index", height=200)
if st.button("Index"):
    if text.strip():
        docs = chunk(text)
        index_texts(docs)
        st.success(f"Indexed {len(docs)} chunks")
    else:
        st.warning("Please paste some text")

st.header("Upload Files")
files = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"], accept_multiple_files=True)
if st.button("Index Uploaded"):
    if files:
        combined = []
        for f in files:
            if f.type == "application/pdf" or f.name.lower().endswith(".pdf"):
                combined.append(read_pdf(f.read()))
            else:
                combined.append(read_txt(f.read()))
        merged = "\n\n".join(combined)
        docs = chunk(merged)
        index_texts(docs)
        st.success(f"Indexed {len(docs)} chunks from {len(files)} file(s)")
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
