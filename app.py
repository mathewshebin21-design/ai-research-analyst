import streamlit as st
from src.research import ResearchEngine
from rag import DocumentRAGEngine

st.set_page_config(page_title="AI Research & Document Intelligence Hub", layout="wide")

st.title("🚀 AI Research & Document Intelligence Hub (v3)")
st.write("Seamlessly generate real-time market research reports and query your documents using advanced AI.")

tab1, tab2 = st.tabs(["📊 v2.0 Market Research Analyst", "📁 v3 Document RAG Engine"])

with tab1:
    st.header("Real-Time Market Research Engine")
    query = st.text_input("Enter research topic or market sector:", "Global Electric Vehicle Market Trends")
    persona = st.selectbox("Select Analyst Persona:", ["Senior Venture Capitalist", "Tech Industry Analyst", "Global Supply Chain Expert"])
    
    if st.button("Generate Research Report"):
        with st.spinner("Analyzing live web intelligence and formatting structured report..."):
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
            except Exception as e:
                st.error(f"An error occurred: {e}")

with tab2:
    st.header("Multimodal Document RAG Engine")
    uploaded_file = st.file_uploader("Upload a PDF document for analysis", type=["pdf"])
    
    if uploaded_file is not None:
        rag_engine = DocumentRAGEngine()
        with st.spinner("Extracting text from document..."):
            doc_text = rag_engine.extract_text_from_pdf(uploaded_file)
            st.success(f"Successfully loaded document! Length: {len(doc_text)} characters.")
            
        user_question = st.text_input("Ask a question about your uploaded document:")
        if user_question and st.button("Query Document"):
            with st.spinner("Searching document context and generating answer..."):
                answer = rag_engine.query_document(doc_text, user_question)
                st.subheader("Answer")
                st.write(answer)
