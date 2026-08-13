import streamlit as st

st.set_page_config(page_title="AI Research & Intelligence Platform", layout="wide")

st.sidebar.title("🎯 Executive Controls")
show_mba = st.sidebar.checkbox("Show MBA Decision Hub", value=True)

st.title("🚀 AI Research & Intelligence Platform")
st.markdown("Enterprise modular market intelligence paired with advanced vector RAG engines.")

if show_mba:
    st.markdown("---")
    try:
        from src.decision_engine import render_decision_dashboard
        render_decision_dashboard()
    except Exception as e:
        st.error(f"Error loading decision engine: {e}")
