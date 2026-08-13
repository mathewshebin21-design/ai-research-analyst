import streamlit as st
import plotly.express as px
import pandas as pd
from src.research import ResearchEngine
from rag import DocumentRAGEngine
from pdf_generator import PDFExporter

st.set_page_config(page_title="AI Research & Intelligence Hub", layout="wide")

# Sidebar Global Settings Configuration
with st.sidebar:
    st.title("⚙️ Hub Configuration")
    theme = st.radio("App Theme", ["Modern Dark", "Professional Light"])
    st.divider()
    
    persona = st.selectbox(
        "Default Analyst Persona:", 
        [
            "Senior Venture Capitalist", 
            "Tech Industry Analyst", 
            "Global Supply Chain Expert",
            "Chief Technology Officer (CTO)",
            "ESG & Sustainability Director",
            "Macroeconomic Strategist",
            "Growth Marketing & Brand Director",
            "Cybersecurity & Compliance Officer"
        ]
    )
    st.divider()
    st.info("System Status: Operational (Fail-safe Enabled)")

st.title("🚀 AI Research & Intelligence Hub (v6.6)")
st.write("Enterprise modular market intelligence with fail-safe simulation mode, expert personas, and multi-document RAG.")

tab1, tab2 = st.tabs(["📊 Modular Market Research", "📁 Multi-Document RAG & Summarizer"])

with tab1:
    st.header("Customizable Market Intelligence Engine")
    query = st.text_input("Enter research topic or market sector:", "Electric Vehicle Battery Recycling and Supply Chain Innovations")
    
    st.markdown("### 📋 Select Required Analysis Modules:")
    col_cb1, col_cb2, col_cb3, col_cb4 = st.columns(4)
    with col_cb1:
        include_market = st.checkbox("Market Size & Trends", value=True)
        include_swot = st.checkbox("SWOT Analysis", value=True)
    with col_cb2:
        include_competitors = st.checkbox("Key Competitors", value=True)
        include_financials = st.checkbox("Financial Projections", value=True)
    with col_cb3:
        include_recommendations = st.checkbox("Strategic Recommendations", value=True)
    with col_cb4:
        include_charts = st.checkbox("Interactive Plotly Charts", value=True)

    if st.button("Generate Custom Intelligence Report"):
        selected_sections = []
        if include_market: selected_sections.append("Market Size and Trends")
        if include_swot: selected_sections.append("SWOT Analysis")
        if include_competitors: selected_sections.append("Key Competitors")
        if include_financials: selected_sections.append("Financial Projections")
        if include_recommendations: selected_sections.append("Strategic Recommendations")

        if not selected_sections:
            st.warning("Please select at least one analysis module.")
        else:
            with st.spinner(f"Compiling custom research modules from the perspective of a {persona}..."):
                try:
                    engine = ResearchEngine()
                    report = engine.generate_report(query, persona, selected_sections)
                    
                    st.subheader("Executive Summary")
                    st.write(report.executive_summary)
                    
                    col_main1, col_main2 = st.columns([1, 1])
                    
                    with col_main1:
                        if include_market and report.market_size_and_trends:
                            st.subheader("Market Size & Trends")
                            st.write(report.market_size_and_trends)
                            
                        if include_competitors and report.key_competitors:
                            st.subheader("Key Competitors")
                            for comp in report.key_competitors:
                                st.markdown(f"- {comp}")
                                
                    with col_main2:
                        if include_charts:
                            st.subheader("Interactive Growth Projections")
                            chart_data = pd.DataFrame({
                                "Year": ["2024", "2025", "2026 (Est.)", "2027 (Proj.)", "2028 (Proj.)"],
                                "Market Value ($B)": [120, 165, 220, 290, 380]
                            })
                            fig = px.bar(chart_data, x="Year", y="Market Value ($B)", title=f"Market Projection: {query}", color="Market Value ($B)", template="plotly_dark")
                            st.plotly_chart(fig, use_container_width=True)

                    if include_swot and report.swot_strengths:
                        st.markdown("---")
                        st.subheader("SWOT Matrix Analysis")
                        s_col, w_col = st.columns(2)
                        with s_col:
                            st.markdown("### 🟢 Strengths")
                            for item in report.swot_strengths: st.markdown(f"- {item}")
                            st.markdown("### 🔵 Opportunities")
                            for item in report.swot_opportunities: st.markdown(f"- {item}")
                        with w_col:
                            st.markdown("### 🟠 Weaknesses")
                            for item in report.swot_weaknesses: st.markdown(f"- {item}")
                            st.markdown("### 🔴 Threats")
                            for item in report.swot_threats: st.markdown(f"- {item}")

                    if include_recommendations and report.strategic_recommendations:
                        st.markdown("---")
                        st.subheader("Strategic Recommendations")
                        for rec in report.strategic_recommendations:
                            st.markdown(f"- {rec}")

                    content = [{"header": "Executive Summary", "body": report.executive_summary}]
                    if include_market and report.market_size_and_trends:
                        content.append({"header": "Market Size & Trends", "body": report.market_size_and_trends})
                        
                    pdf_file = PDFExporter.generate_report_pdf(f"Custom Research Report: {query}", content)
                    st.download_button("Download Custom Report as PDF", pdf_file, file_name="custom_research_report.pdf", mime="application/pdf")

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
                
                followup_prompt = f"Based on these documents, suggest 3 short, high-value follow-up questions a user could ask. Return them as a comma-separated list of strings without numbers:\n{combined_text[:5000]}"
                followups_raw = rag_engine.query_document(combined_text, [], followup_prompt)
                st.session_state.suggested_followups = [f.strip() for f in followups_raw.split(",") if f.strip()][:3]
                
                st.success(f"Successfully loaded and summarized {len(uploaded_files)} documents!")

        if "auto_summary" in st.session_state:
            with st.expander("📋 Automated Document Summarizer & Key Takeaways", expanded=True):
                st.markdown(st.session_state.auto_summary)

        if "multi_messages" not in st.session_state:
            st.session_state.multi_messages = []

        for message in st.session_state.multi_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if "suggested_followups" in st.session_state and st.session_state.suggested_followups:
            st.markdown("**💡 Suggested Follow-up Questions:**")
            cols = st.columns(len(st.session_state.suggested_followups))
            for idx, suggestion in enumerate(st.session_state.suggested_followups):
                with cols[idx]:
                    if st.button(suggestion, key=f"followup_btn_{idx}_{suggestion[:10]}"):
                        st.session_state.multi_messages.append({"role": "user", "content": suggestion})
                        with st.chat_message("user"):
                            st.markdown(suggestion)
                        with st.chat_message("assistant"):
                            with st.spinner("Analyzing across all uploaded documents..."):
                                answer = rag_engine.query_document(
                                    st.session_state.multi_doc_text, 
                                    st.session_state.multi_messages[:-1], 
                                    suggestion
                                )
                                st.markdown(answer)
                                st.session_state.multi_messages.append({"role": "assistant", "content": answer})
                        st.rerun()

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
            st.rerun()

        if st.session_state.multi_messages:
            chat_content = [{"header": f"{m['role'].capitalize()}", "body": m['content']} for m in st.session_state.multi_messages]
            pdf_file = PDFExporter.generate_report_pdf("Multi-Document Analysis Chat History", chat_content)
            st.download_button("Export Multi-Doc Chat History as PDF", pdf_file, file_name="multi_doc_chat_history.pdf", mime="application/pdf")
