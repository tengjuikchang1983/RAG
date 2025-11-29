from typing import List

def read_pdf(file_bytes: bytes) -> str:
    from pypdf import PdfReader
    import io
    reader = PdfReader(io.BytesIO(file_bytes))
    texts: List[str] = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)

def read_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")
