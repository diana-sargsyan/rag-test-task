"""Streamlit chat UI for RAG over tabular data."""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from src.chat_engine import ChatEngine

load_dotenv()

st.set_page_config(page_title="Aderant Data Chat", page_icon="📊", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Settings")
    model = st.selectbox(
        "Model",
        ["gpt-5.1", "gpt-5.2", "gpt-5-mini", "gpt-4o-mini"],
        index=0,
    )
    if st.button("🗑️ Clear conversation"):
        st.session_state.pop("engine", None)
        st.session_state.pop("messages", None)
        st.rerun()

    st.divider()
    st.markdown("**Tables available:**")
    st.markdown("- `clients` — 20 clients\n- `invoices` — 40 invoices\n- `invoice_line_items` — 96 items")
    st.divider()
    st.markdown(
        "**Example questions:**\n"
        "- List all clients with their industries\n"
        "- Which invoices are overdue?\n"
        "- What is the total billed amount for Acme Corp?\n"
        "- Top 3 services by revenue in 2024"
    )

# --- Initialize state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "engine" not in st.session_state:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("Please set OPENAI_API_KEY in your .env file or environment.")
        st.stop()
    st.session_state.engine = ChatEngine(model=model, api_key=api_key)

engine: ChatEngine = st.session_state.engine
if engine.model != model:
    engine.set_model(model)

# --- Title ---
st.title("📊 Aderant Data Chat")
st.caption("Ask questions about clients, invoices, and line items. Powered by OpenAI function calling.")

# --- Display chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sql_queries"):
            with st.expander("🔍 SQL Queries"):
                for q in msg["sql_queries"]:
                    st.code(q, language="sql")
        if msg.get("data_tables"):
            for table in msg["data_tables"]:
                if table.get("rows"):
                    df = pd.DataFrame(table["rows"], columns=table["columns"])
                    st.dataframe(df, use_container_width=True)

# --- Handle user input ---
if prompt := st.chat_input("Ask a question about the data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = engine.chat(prompt)

        if result.get("rewritten_query"):
            st.caption(f"_Interpreted as: {result['rewritten_query']}_")

        st.markdown(result["answer"])

        if result.get("sql_queries"):
            with st.expander("🔍 SQL Queries"):
                for q in result["sql_queries"]:
                    st.code(q, language="sql")

        if result.get("data_tables"):
            for table in result["data_tables"]:
                if table.get("rows"):
                    df = pd.DataFrame(table["rows"], columns=table["columns"])
                    st.dataframe(df, use_container_width=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sql_queries": result.get("sql_queries", []),
        "data_tables": result.get("data_tables", []),
    })
