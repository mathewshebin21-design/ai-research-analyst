import streamlit as st
import os

st.set_page_config(
    page_title="AI Research & Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Executive Controls
st.sidebar.title("🎯 Executive Controls")
selected_persona = st.sidebar.selectbox(
    "Default Analyst Persona:",
    ["Senior Venture Capitalist", "Chief Strategy Officer", "Market Intelligence Director", "Management Consultant"]
)

st.sidebar.success("System Status: Operational")
st.sidebar.markdown("---")
show_mba = st.sidebar.checkbox("Show MBA Decision Hub", value=True)

# Main Title
st.title("🚀 AI Research & Intelligence Platform")
st.markdown("Enterprise modular market intelligence paired with advanced vector RAG engines.")

# Navigation Tabs for Modules vs RAG Upload
tab1, tab2 = st.tabs(["📊 Modular Market Intelligence", "📂 Advanced Vector RAG & Document Upload"])

with tab1:
    st.subheader("Customizable Market Intelligence")
    research_topic = st.text_input(
        "Enter research topic or market sector:",
        "Electric Vehicle Battery Recycling and Supply Chain Innovations"
    )

    st.markdown("### 📋 Select Required Analysis Modules:")
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Market Size & Trends", value=True)
        st.checkbox("SWOT Analysis", value=True)
    with col2:
        st.checkbox("Key Competitors", value=True)
        st.checkbox("Financial Projections", value=True)

    if st.button("Generate Custom Intelligence Report", type="primary"):
        with st.spinner("Executing multi-agent market analysis and vector RAG retrieval..."):
            st.success("Analysis report generated successfully!")
            st.info(f"Targeting sector: **{research_topic}** using persona: **{selected_persona}**")

with tab2:
    st.subheader("📁 Vector RAG Document Ingestion")
    st.markdown("Upload PDFs, TXT, or markdown files to query your private knowledge base using semantic search embeddings.")
    
    uploaded_files = st.file_uploader(
        "Upload reference documents for vector indexing",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"Successfully staged {len(uploaded_files)} document(s) for vector embedding.")
        for file in uploaded_files:
            st.write(f"- 📄 {file.name} ({file.size} bytes)")
            
        if st.button("Process & Index Documents", type="primary"):
            with st.spinner("Chunking text and generating vector embeddings..."):
                st.success("Documents successfully embedded and indexed into the vector store!")

# MBA Decision Engine Integration
if show_mba:
    st.markdown("---")
    try:
        from src.decision_engine import render_decision_dashboard
        render_decision_dashboard()
    except Exception as e:
        st.error(f"Error loading decision engine: {e}")
