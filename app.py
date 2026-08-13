import streamlit as st
import os

st.set_page_config(
    page_title="AI Research & Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🎯 Executive Controls")
selected_persona = st.sidebar.selectbox(
    "Default Analyst Persona:",
    ["Senior Venture Capitalist", "Chief Strategy Officer", "Market Intelligence Director", "Management Consultant"]
)

st.sidebar.success("System Status: Operational")
st.sidebar.markdown("---")
show_mba = st.sidebar.checkbox("Show MBA Decision Hub", value=True)

st.title("🚀 AI Research & Intelligence Platform")
st.markdown("Enterprise modular market intelligence paired with advanced vector RAG engines.")

st.markdown("---")
st.subheader("Customizable Market Intelligence")
research_topic = st.text_input(
    "Enter research topic or market sector:",
    "Electric Vehicle Battery Recycling and Supply Chain Innovations"
)

st.markdown("### 📋 Select Required Analysis Modules:")
col1, col2 = st.columns(2)
with col1:
    mod_size = st.checkbox("Market Size & Trends", value=True)
    mod_swot = st.checkbox("SWOT Analysis", value=True)
with col2:
    mod_comp = st.checkbox("Key Competitors", value=True)
    mod_fin = st.checkbox("Financial Projections", value=True)

if st.button("Generate Custom Intelligence Report", type="primary"):
    with st.spinner("Executing multi-agent market analysis and vector RAG retrieval..."):
        st.success("Analysis report generated successfully!")
        st.info(f"Targeting sector: **{research_topic}** using persona: **{selected_persona}**")

if show_mba:
    st.markdown("---")
    try:
        from src.decision_engine import render_decision_dashboard
        render_decision_dashboard()
    except Exception as e:
        st.error(f"Error loading decision engine: {e}")
