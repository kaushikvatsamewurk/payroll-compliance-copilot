import os
from langchain_community.document_loaders import PyPDFLoader

DOCS_PATH = "docs"

total_pages = 0
nonempty_pages = 0
sample = []

for f in os.listdir(DOCS_PATH):
    if f.lower().endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(DOCS_PATH, f))
        pages = loader.load()
        total_pages += len(pages)
        for p in pages:
            txt = (p.page_content or "").strip()
            if len(txt) > 50:
                nonempty_pages += 1
                if len(sample) < 5:
                    sample.append((f, len(txt), txt[:300].replace("\n", " ")))

print("Total pages:", total_pages)
print("Non-empty pages (>50 chars):", nonempty_pages)
print("\n--- Samples ---")
for s in sample:
    print("\nFILE:", s[0], "LEN:", s[1])
    print(s[2])