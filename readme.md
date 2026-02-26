# 🇮🇳 Indian Payroll Compliance Copilot (MVP)

An AI-powered assistant that answers Indian payroll and labour law questions using Retrieval-Augmented Generation (RAG).

## 🚀 What It Does

- Answers PF / ESI / Gratuity / Bonus / Professional Tax queries
- Provides:
  - Clear Yes / No / Conditional
  - Formula
  - Salary-based calculation
  - Legal reference snippets
- Uses official documents as ground truth (no hallucination)

## 🧠 Architecture

PDFs → Chunking → Embeddings → FAISS Vector Store → GPT-4.1 → Structured Output

## 🛠 Tech Stack

- Python
- FastAPI
- LangChain
- FAISS
- OpenAI API

## 📦 How to Run

```bash
pip install -r requirements.txt
python ingest.py
uvicorn app:app --reload