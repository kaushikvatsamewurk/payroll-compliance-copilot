from dotenv import load_dotenv
load_dotenv()

print("Starting ingestion...")

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

DOCS_PATH = "docs"

print("Files:", os.listdir(DOCS_PATH))

documents = []

# Load PDFs and attach doc_name metadata
for f in os.listdir(DOCS_PATH):
    if f.lower().endswith(".pdf"):
        print("Loading:", f)
        loader = PyPDFLoader(os.path.join(DOCS_PATH, f))
        pages = loader.load()

        # Add filename as metadata to every page
        for p in pages:
            p.metadata["doc_name"] = f

        documents.extend(pages)

print("Total pages loaded:", len(documents))

# Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(documents)

print("Chunks created:", len(chunks))

# Create embeddings
embeddings = OpenAIEmbeddings()

# Build FAISS index
db = FAISS.from_documents(chunks, embeddings)
db.save_local("vectorstore")

print("DONE — Vectorstore created")