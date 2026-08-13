import streamlit as st
from src.research import ResearchEngine

st.set_page_config(page_title="AI Research Hub", layout="wide")

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Hub Configuration")
    theme = st.radio("App Theme", ["Modern Dark", "Professional Light"])
    st.divider()
    persona = st.selectbox("Analyst Persona", [
        "Senior Venture Capitalist", "Tech Industry Analyst", 
        "Global Supply Chain Expert", "Chief Technology Officer (CTO)",
        "ESG & Sustainability Director", "Macroeconomic Strategist"
    ])
    st.info("System Status: Operational")

st.header("🚀 Enterprise Research Intelligence")

# Main logic
query = st.text_input("Enter research topic:")
if st.button("Generate Intelligence"):
    with st.spinner("Analyzing data..."):
        engine = ResearchEngine()
        report = engine.generate_report(query, persona, ["Market Size", "SWOT"])
        
        st.subheader("Executive Summary")
        st.write(report.executive_summary)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Strengths")
            for s in report.swot_strengths: st.write(f"- {s}")
        with col2:
            st.subheader("Weaknesses")
            for w in report.swot_weaknesses: st.write(f"- {w}")
