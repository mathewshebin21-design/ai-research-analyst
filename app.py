import streamlit as st
import plotly.express as px
import pandas as pd
from src.research import ResearchEngine
from rag import DocumentRAGEngine
from pdf_generator import PDFExporter
from auth import login_form

st.set_page_config(page_title="AI Research Hub", layout="wide")

if "user" not in st.session_state:
    login_form()
    st.stop()

st.title("🚀 AI Research & Intelligence Hub (v6)")
st.sidebar.write(f"Logged in as: {st.session_state.user.email}")

tab1, tab2 = st.tabs(["📊 Market Research & Visualization", "📁 Multi-Document RAG"])

with tab1:
    st.header("Real-Time Research & Charts")
    query = st.text_input("Enter research topic:", "Tech Market Growth 2026")
    if st.button("Generate & Visualize"):
        with st.spinner("Analyzing and plotting..."):
            data = pd.DataFrame({"Year": [2024, 2025, 2026], "Market Size (B$)": [100, 150, 220]})
            fig = px.bar(data, x="Year", y="Market Size (B$)", title=f"Projected Growth for: {query}")
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Multi-Document RAG Engine & Comparison")
    uploaded_files = st.file_uploader("Upload multiple PDF documents for comparative analysis", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        rag_engine = DocumentRAGEngine()
        
        file_names_key = "-".join([f.name for f in uploaded_files])
        if "multi_doc_text" not in st.session_state or st.session_state.get("current_files") != file_names_key:
            with st.spinner("Extracting and combining text from all uploaded documents..."):
                combined_text = ""
                for file in uploaded_files:
                    extracted = rag_engine.extract_text_from_pdf(file)
                    combined_text += f"\n\n--- START OF DOCUMENT: {file.name} ---\n\n{extracted}\n\n--- END OF DOCUMENT ---\n\n"
                
                st.session_state.multi_doc_text = combined_text
                st.session_state.current_files = file_names_key
                st.session_state.multi_messages = []
                st.success(f"Successfully loaded and indexed {len(uploaded_files)} documents!")

        if "multi_messages" not in st.session_state:
            st.session_state.multi_messages = []

        for message in st.session_state.multi_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_question := st.chat_input("Ask a question or compare documents..."):
            st.session_state.multi_messages.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing across all uploaded documents..."):
                    answer = rag_engine.query_document(
                        st.session_state.multi_doc_text, 
                        st.session_state.multi_messages[:-1], 
                        user_question
                    )
                    st.markdown(answer)
                    st.session_state.multi_messages.append({"role": "assistant", "content": answer})

        if st.session_state.multi_messages:
            chat_content = [{"header": f"{m['role'].capitalize()}", "body": m['content']} for m in st.session_state.multi_messages]
            pdf_file = PDFExporter.generate_report_pdf("Multi-Document Analysis Chat History", chat_content)
            st.download_button("Export Multi-Doc Chat History as PDF", pdf_file, file_name="multi_doc_chat_history.pdf", mime="application/pdf")
