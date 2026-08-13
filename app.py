import streamlit as st
import plotly.express as px
import pandas as pd
from src.research import ResearchEngine
from rag import DocumentRAGEngine
from pdf_generator import PDFExporter

# 1. Define the dynamic theme injection function
def apply_theme(theme_name):
    if theme_name == "Modern Dark":
        st.markdown("""
            <style>
            .stApp { background-color: #0E1117; color: #FAFAFA; }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp { background-color: #FFFFFF; color: #31333F; }
            </style>
            """, unsafe_allow_html=True)

st.set_page_config(page_title="AI Research & Intelligence Hub", layout="wide")

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Hub Configuration")
    # 2. Get the selection
    theme_selection = st.radio("App Theme", ["Modern Dark", "Professional Light"])
    # 3. Apply it immediately
    apply_theme(theme_selection)
    
    st.divider()
    persona = st.selectbox("Analyst Persona", [
        "Senior Venture Capitalist", "Tech Industry Analyst", 
        "Global Supply Chain Expert", "Chief Technology Officer (CTO)",
        "ESG & Sustainability Director", "Macroeconomic Strategist"
    ])
    st.info("System Status: Operational")

st.title("🚀 AI Research & Intelligence Hub (v6.7)")

# ... [Keep the rest of your app logic as is] ...
# Make sure to include the tabs and main content here!
