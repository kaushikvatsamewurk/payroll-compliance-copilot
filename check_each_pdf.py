import os
from langchain_community.document_loaders import PyPDFLoader

DOCS_PATH = "docs"

for f in sorted(os.listdir(DOCS_PATH)):
    if not f.lower().endswith(".pdf"):
        continue

    path = os.path.join(DOCS_PATH, f)
    pages = PyPDFLoader(path).load()

    chars = sum(len((p.page_content or "").strip()) for p in pages)
    nonempty = sum(1 for p in pages if len((p.page_content or "").strip()) > 50)

    print(f"{f:18} | pages={len(pages):3} | nonempty_pages={nonempty:3} | total_chars={chars}")