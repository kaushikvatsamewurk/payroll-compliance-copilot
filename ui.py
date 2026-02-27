import streamlit as st
import requests
import json

st.set_page_config(page_title="Payroll Compliance Copilot", layout="wide")

st.title("🇮🇳 Indian Payroll Compliance Copilot")
st.markdown("AI-powered payroll & labour law assistant for SMEs")

st.divider()

col1, col2 = st.columns(2)

with col1:
    question = st.text_input("Ask a compliance question", value="Calculate PF contribution")
    state = st.selectbox("State", ["KA", "MH"])
    basic = st.number_input("Basic Salary (₹)", value=25000)
    gross = st.number_input("Gross Salary (₹)", value=40000)
    years = st.number_input("Years of Service", value=6)

with col2:
    st.markdown("### Inputs Preview")
    st.write({
        "State": state,
        "Basic": basic,
        "Gross": gross,
        "Years of Service": years
    })

st.divider()

if st.button("🚀 Get Compliance Answer"):

    payload = {
        "question": question,
        "state": state,
        "emp_type": "Permanent",
        "basic": basic,
        "gross": gross,
        "years_of_service": years,
        "debug": False
    }

    with st.spinner("Analyzing compliance rules..."):
        #response = requests.post("http://127.0.0.1:9000/ask", json=payload)
        response = requests.post("http://localhost:8000/ask", json=payload)

    if response.status_code == 200:
        answer = response.json()["answer"]

        st.success("Compliance Analysis Complete")

        st.markdown("## 📘 Result")
        st.markdown(answer)

    else:
        st.error("Something went wrong.")