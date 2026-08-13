import streamlit as st
from src.research import ResearchEngine
from rag import DocumentRAGEngine

st.set_page_config(page_title="AI Research & Document Intelligence Hub", layout="wide")

st.title("🚀 AI Research & Document Intelligence Hub (v4)")
st.write("Seamlessly generate real-time market research reports and query your documents with conversational memory.")

tab1, tab2 = st.tabs(["📊 v2.0 Market Research Analyst", "📁 v4 Document RAG with Memory"])

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
    st.header("Multimodal Document RAG Engine with Memory")
    uploaded_file = st.file_uploader("Upload a PDF document for analysis", type=["pdf"])
    
    if uploaded_file is not None:
        rag_engine = DocumentRAGEngine()
        
        # Cache extracted text in session state so it doesn't re-extract on every chat turn
        if "doc_text" not in st.session_state or st.session_state.get("current_file") != uploaded_file.name:
            with st.spinner("Extracting text from document..."):
                st.session_state.doc_text = rag_engine.extract_text_from_pdf(uploaded_file)
                st.session_state.current_file = uploaded_file.name
                st.session_state.messages = []
                st.success(f"Successfully loaded {uploaded_file.name}!")

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if user_question := st.chat_input("Ask a follow-up question about your document..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            # Generate response with memory
            with st.chat_message("assistant"):
                with st.spinner("Thinking through document context and history..."):
                    answer = rag_engine.query_document(
                        st.session_state.doc_text, 
                        st.session_state.messages[:-1], 
                        user_question
                    )
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
