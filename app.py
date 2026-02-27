from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from calculations import (
    calculate_pf,
    calculate_esi,
    calculate_pt,
    calculate_bonus,
    calculate_gratuity
)

app = FastAPI()

# Load Vectorstore
embeddings = OpenAIEmbeddings()
db = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

SYSTEM_PROMPT = """
You are an Indian Payroll Compliance Assistant.

Use ONLY the provided Context to explain and cite laws.

Rules:
- Use Deterministic Calculations exactly as given.
- Do NOT recalculate values.
- Do NOT mix different laws.
- If context does not contain something, clearly state it.
- Always provide short legal reference snippet.

Output format:

Answer:
Conditions:
Formula:
Calculation:
Reference:
"""


class Query(BaseModel):
    question: str
    state: str
    emp_type: str
    basic: float
    gross: float
    years_of_service: int = 6
    debug: bool = False


# ------------------------------
# Retrieval Boosting
# ------------------------------
def boost_query(q: Query):
    q_lower = q.question.lower()

    retrieval_query = f"""
    {q.question}
    State: {q.state}
    Employee type: {q.emp_type}
    Basic: {q.basic}
    Gross: {q.gross}
    """

    if "pf" in q_lower or "epf" in q_lower:
        retrieval_query += "Include wage ceiling 15000, contribution rate 12%, EPS 8.33%, basic wages definition."

    if "esi" in q_lower:
        retrieval_query += "Include eligibility threshold 21000, contribution rates."

    if "bonus" in q_lower:
        retrieval_query += "Include eligibility salary limit 21000, minimum 8.33%, maximum 20%."

    if "gratuity" in q_lower:
        retrieval_query += "Include 5 years continuous service rule, 15/26 formula."

    return retrieval_query


# ------------------------------
# Document Routing (A1)
# ------------------------------
def route_filter(q: Query):
    q_lower = q.question.lower()

    if "pf" in q_lower or "epf" in q_lower:
        return {"doc_name": "pf.pdf"}

    if "esi" in q_lower:
        return {"doc_name": "esi.pdf"}

    if "bonus" in q_lower:
        return {"doc_name": "bonus.pdf"}

    if "gratuity" in q_lower:
        return {"doc_name": "gratuity.pdf"}

    if "professional tax" in q_lower or "pt" in q_lower:
        if q.state.upper() == "KA":
            return {"doc_name": "pt_ka.pdf"}
        if q.state.upper() == "MH":
            return {"doc_name": "pt_mh.pdf"}

    return None


@app.post("/ask")
def ask(q: Query):

    q_lower = q.question.lower()
    calculated_data = {}

    # ------------------------------
    # Deterministic Engine
    # ------------------------------
    if "pf" in q_lower or "epf" in q_lower:
        calculated_data = calculate_pf(q.basic)

    elif "esi" in q_lower:
        calculated_data = calculate_esi(q.gross)

    elif "professional tax" in q_lower or "pt" in q_lower:
        calculated_data = calculate_pt(q.state, q.gross)

    elif "bonus" in q_lower:
        calculated_data = calculate_bonus(q.gross)

    elif "gratuity" in q_lower:
        calculated_data = calculate_gratuity(q.basic, q.years_of_service)

    # ------------------------------
    # Retrieval (A2 + A3)
    # ------------------------------
    retrieval_query = boost_query(q)
    filter_doc = route_filter(q)

    # Use MMR retrieval (A3)
    if filter_doc:
        docs = db.max_marginal_relevance_search(
            retrieval_query,
            k=5,
            filter=filter_doc
        )
    else:
        docs = db.max_marginal_relevance_search(
            retrieval_query,
            k=5
        )

    context_parts = []
    debug_chunks = []

    for d in docs:
        txt = (d.page_content or "").strip()
        if not txt:
            continue
        context_parts.append(txt)
        debug_chunks.append({
            "doc_name": d.metadata.get("doc_name"),
            "page": d.metadata.get("page"),
            "preview": txt[:250].replace("\n", " ")
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
Years of Service: {q.years_of_service}

Deterministic Calculations:
{calculated_data}

Question:
{q.question}
"""

    response = llm.invoke(prompt)

    if q.debug:
        return {
            "answer": response.content,
            "calculated_data": calculated_data,
            "retrieval_debug": debug_chunks
        }

    return {
        "answer": response.content
    }