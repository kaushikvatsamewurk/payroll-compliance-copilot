from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

app = FastAPI()

embeddings = OpenAIEmbeddings()
db = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

SYSTEM_PROMPT = """
You are an Indian Payroll Compliance Assistant.

Use ONLY the provided Context to answer.

Output format (always):
Answer: (Yes/No/Conditional + 1-2 lines)
Conditions: (bullet list if Conditional, else 'N/A')
Formula: (bullet list)
Calculation: (show calculation using given Basic/Gross when applicable, else 'N/A')
Reference: (quote 1-3 short snippets from Context with doc/page if available)

Rules:
- If Context contains thresholds/conditions but not explicit Yes/No, respond "Conditional" and list conditions.
- Only say "Not found in provided documents." if Context is empty or clearly unrelated.
- Do NOT invent sections or clauses.
"""

class Query(BaseModel):
    question: str
    state: str
    emp_type: str
    basic: float
    gross: float
    debug: bool = True  # you can turn off later

def route_docs(question: str, state: str):
    q = question.lower()

    # Professional tax: route by state
    if "professional tax" in q or "pt " in q or q.strip().startswith("pt") or " p.t" in q:
        st = state.upper()
        if st == "KA":
            return {"doc_name": "pt_ka.pdf"}
        if st == "MH":
            return {"doc_name": "pt_mh.pdf"}
        if st == "TN":
            return {"doc_name": "pt_tn.pdf"}
        return None

    if "pf" in q or "epf" in q or "provident" in q:
        return {"doc_name": "pf.pdf"}

    if "esi" in q:
        return {"doc_name": "esi.pdf"}

    if "gratuity" in q:
        return {"doc_name": "gratuity.pdf"}

    if "bonus" in q:
        return {"doc_name": "bonus.pdf"}

    return None

@app.post("/ask")
def ask(q: Query):
    # Build a better retrieval query (helps vague questions like "Is PF applicable?")
    retrieval_query = (
        f"{q.question}\n"
        f"State: {q.state}\n"
        f"Employee type: {q.emp_type}\n"
        f"Basic: {q.basic}\n"
        f"Gross: {q.gross}\n"
        f"Answer with eligibility/coverage conditions and thresholds."
    )

    # ✅ Add domain keywords to improve retrieval for PF / EPF questions
    q_lower = q.question.lower()
    if "pf" in q_lower or "epf" in q_lower or "provident" in q_lower:
        retrieval_query += (
            "\nInclude: wage ceiling 15000, contribution rate 12%, EPS 8.33%, EPF, basic wages definition."
        )

    flt = route_docs(q.question, q.state)

    # Try doc-filtered retrieval first; if filter isn't supported, fallback to unfiltered.
    try:
        docs_scores = (
            db.similarity_search_with_score(retrieval_query, k=8, filter=flt)
            if flt
            else db.similarity_search_with_score(retrieval_query, k=8)
        )
    except TypeError:
        docs_scores = db.similarity_search_with_score(retrieval_query, k=8)

    # Build context + debug info
    context_parts = []
    debug_chunks = []
    for d, score in docs_scores:
        txt = (d.page_content or "").strip()
        if not txt:
            continue
        context_parts.append(txt)
        debug_chunks.append({
            "score": float(score),
            "doc_name": d.metadata.get("doc_name"),
            "source": d.metadata.get("source"),
            "page": d.metadata.get("page"),
            "preview": txt[:300].replace("\n", " ")
        })

    context = "\n\n".join(context_parts)

    prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

User Inputs:
State: {q.state}
Employee Type: {q.emp_type}
Monthly Basic: {q.basic}
Monthly Gross: {q.gross}

Question:
{q.question}
"""

    response = llm.invoke(prompt)

    if q.debug:
        return {"answer": response.content, "retrieval_debug": debug_chunks}
    return {"answer": response.content}