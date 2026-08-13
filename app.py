import streamlit as st
from src.research import ResearchEngine
from rag import DocumentRAGEngine
from pdf_generator import PDFExporter

st.set_page_config(page_title="AI Research & Document Intelligence Hub", layout="wide")

st.title("🚀 AI Research & Document Intelligence Hub (v6)")
st.write("Generate research, query documents via Supabase Vector DB with memory, and export findings as PDFs.")

tab1, tab2 = st.tabs(["📊 v2.0 Market Research Analyst", "📁 v6 Vector RAG (Supabase pgvector)"])

with tab1:
    st.header("Real-Time Market Research Engine")
    query = st.text_input("Enter research topic or market sector:", "Global Electric Vehicle Market Trends")
    persona = st.selectbox("Select Analyst Persona:", ["Senior Venture Capitalist", "Tech Industry Analyst", "Global Supply Chain Expert"])
    
    if st.button("Generate Research Report"):
        with st.spinner("Analyzing live web intelligence..."):
            try:
                engine = ResearchEngine()
                report = engine.generate_report(query, persona)
                
                st.subheader("Executive Summary")
                st.write(report.executive_summary)
                
                st.subheader("Market Size & Trends")
                st.write(report.market_size_and_trends)
                
                st.subheader("Key Competitors")
                for comp in report.key_competitors:
                    st.markdown(f"- {comp}")
                    
                st.subheader("Strategic Recommendations")
                for rec in report.strategic_recommendations:
                    st.markdown(f"- {rec}")
                    
                st.subheader("Verified Citations")
                for citation in report.citations:
                    st.markdown(f"- [{citation.source_title}]({citation.url})")

                content = [
                    {"header": "Executive Summary", "body": report.executive_summary},
                    {"header": "Market Size & Trends", "body": report.market_size_and_trends}
                ]
                pdf_file = PDFExporter.generate_report_pdf(f"Research Report: {query}", content)
                st.download_button("Download Report as PDF", pdf_file, file_name="research_report.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"An error occurred: {e}")

with tab2:
    st.header("Vector RAG Engine (Supabase pgvector)")
    uploaded_file = st.file_uploader("Upload a PDF document to store in Vector DB", type=["pdf"])
    
    if uploaded_file is not None:
        try:
            rag_engine = DocumentRAGEngine()
        except Exception as err:
            st.error(f"Initialization error: {err}. Check your SUPABASE_URL and SUPABASE_KEY in Secrets.")
            st.stop()
        
        # Cache & vectorize text in Supabase
        if st.session_state.get("current_file") != uploaded_file.name:
            with st.spinner("Chunking text, embedding vectors with Gemini, and indexing into Supabase..."):
                chunks = rag_engine.extract_and_chunk_pdf(uploaded_file)
                rag_engine.store_document_vectors(uploaded_file.name, chunks)
                st.session_state.current_file = uploaded_file.name
                st.session_state.messages = []
                st.success(f"Successfully vectorized and stored {uploaded_file.name} in Supabase!")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_question := st.chat_input("Ask a question about your document..."):
            st.session_state.messages.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                with st.spinner("Searching Supabase pgvector and generating response..."):
                    answer = rag_engine.query_document(
                        st.session_state.current_file, 
                        st.session_state.messages[:-1], 
                        user_question
                    )
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

        if st.session_state.messages:
            chat_content = [{"header": f"{m['role'].capitalize()}", "body": m['content']} for m in st.session_state.messages]
            pdf_file = PDFExporter.generate_report_pdf("Vector RAG Analysis Chat History", chat_content)
            st.download_button("Export Chat History as PDF", pdf_file, file_name="vector_chat_history.pdf", mime="application/pdf")
