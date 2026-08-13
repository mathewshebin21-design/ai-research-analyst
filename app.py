import streamlit as st
import plotly.express as px
import pandas as pd
from src.research import ResearchEngine
from rag import DocumentRAGEngine
from pdf_generator import PDFExporter

st.set_page_config(page_title="AI Research & Intelligence Hub", layout="wide")

st.title("🚀 AI Research & Intelligence Hub (v6)")
st.write("Real-time market research with SWOT Analysis, dynamic Plotly visualizations, multi-document comparison, automated summaries, and PDF export.")

tab1, tab2 = st.tabs(["📊 Market Research & SWOT", "📁 Multi-Document RAG & Summarizer"])

with tab1:
    st.header("Real-Time Market Research & SWOT Analysis")
    query = st.text_input("Enter research topic or market sector:", "Electric Vehicle Battery Recycling and Supply Chain Innovations")
    persona = st.selectbox("Select Analyst Persona:", ["Senior Venture Capitalist", "Tech Industry Analyst", "Global Supply Chain Expert"])
    
    if st.button("Generate Comprehensive Report & SWOT"):
        with st.spinner("Analyzing market intelligence and compiling SWOT analysis..."):
            try:
                engine = ResearchEngine()
                report = engine.generate_report(query, persona)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("Executive Summary")
                    st.write(report.executive_summary)
                    
                    st.subheader("Market Size & Trends")
                    st.write(report.market_size_and_trends)
                    
                with col2:
                    st.subheader("Interactive Growth Projections")
                    chart_data = pd.DataFrame({
                        "Year": ["2024", "2025", "2026 (Est.)", "2027 (Proj.)", "2028 (Proj.)"],
                        "Market Value ($B)": [120, 165, 220, 290, 380]
                    })
                    fig = px.bar(chart_data, x="Year", y="Market Value ($B)", title=f"Market Projection: {query}", color="Market Value ($B)", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")
                st.subheader("SWOT Matrix Analysis")
                s_col, w_col = st.columns(2)
                with s_col:
                    st.markdown("### 🟢 Strengths")
                    for item in report.swot_strengths:
                        st.markdown(f"- {item}")
                    st.markdown("### 🔵 Opportunities")
                    for item in report.swot_opportunities:
                        st.markdown(f"- {item}")
                with w_col:
                    st.markdown("### 🟠 Weaknesses")
                    for item in report.swot_weaknesses:
                        st.markdown(f"- {item}")
                    st.markdown("### 🔴 Threats")
                    for item in report.swot_threats:
                        st.markdown(f"- {item}")

                st.markdown("---")
                st.subheader("Key Competitors")
                for comp in report.key_competitors:
                    st.markdown(f"- {comp}")
                    
                st.subheader("Strategic Recommendations")
                for rec in report.strategic_recommendations:
                    st.markdown(f"- {rec}")

                content = [
                    {"header": "Executive Summary", "body": report.executive_summary},
                    {"header": "Market Size & Trends", "body": report.market_size_and_trends}
                ]
                pdf_file = PDFExporter.generate_report_pdf(f"Comprehensive Research Report: {query}", content)
                st.download_button("Download Full Report as PDF", pdf_file, file_name="comprehensive_research_report.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"An error occurred: {e}")

with tab2:
    st.header("Multi-Document RAG & Automated Summarizer")
    uploaded_files = st.file_uploader("Upload multiple PDF documents for comparative analysis", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        rag_engine = DocumentRAGEngine()
        
        file_names_key = "-".join([f.name for f in uploaded_files])
        if "multi_doc_text" not in st.session_state or st.session_state.get("current_files") != file_names_key:
            with st.spinner("Extracting text and running automated summarization..."):
                combined_text = ""
                for file in uploaded_files:
                    extracted = rag_engine.extract_text_from_pdf(file)
                    combined_text += f"\n\n--- START OF DOCUMENT: {file.name} ---\n\n{extracted}\n\n--- END OF DOCUMENT ---\n\n"
                
                st.session_state.multi_doc_text = combined_text
                st.session_state.current_files = file_names_key
                st.session_state.multi_messages = []
                
                summary_prompt = f"Provide a concise executive summary and list 3 key takeaways from these documents:\n{combined_text[:10000]}"
                st.session_state.auto_summary = rag_engine.query_document(combined_text, [], summary_prompt)
                st.success(f"Successfully loaded and summarized {len(uploaded_files)} documents!")

        if "auto_summary" in st.session_state:
            with st.expander("📋 Automated Document Summarizer & Key Takeaways", expanded=True):
                st.markdown(st.session_state.auto_summary)

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
