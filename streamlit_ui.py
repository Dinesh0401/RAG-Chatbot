import streamlit as st
import requests
from typing import List
import os

# Use environment variable or default to localhost for development
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/chat")

st.title("RAG Chatbot Demo")

st.markdown("Upload one or more PDFs and ask a question. The backend is the FastAPI RAG service.")

uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
question = st.text_input("Question")

if st.button("Ask"):
    if not question.strip():
        st.error("Please enter a question.")
    else:
        files = {}
        for i, f in enumerate(uploaded_files or []):
            files[f"files"] = (f.name, f.getvalue(), "application/pdf")

        # Use requests to POST multipart form
        try:
            if uploaded_files:
                # build multipart for multiple files
                multipart = [("question", (None, question))]
                for f in uploaded_files:
                    multipart.append(("files", (f.name, f.getvalue(), "application/pdf")))
                resp = requests.post(API_URL, files=multipart)
            else:
                resp = requests.post(API_URL, data={"question": question})

            resp.raise_for_status()
        except Exception as e:
            st.error(f"Request failed: {e}")
        else:
            data = resp.json()
            st.subheader("Answer")
            st.write(data.get("answer"))
            st.subheader("Sources")
            for s in data.get("sources", []):
                st.write(f"- {s.get('source')} (page {s.get('page')})")
