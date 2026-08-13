import streamlit as st
from src.research import ResearchEngine
from src.database import HistoryDatabase

st.set_page_config(page_title="AI Research Analyst", page_icon="📈", layout="wide")

db = HistoryDatabase()

st.sidebar.markdown("## Configuration")
persona_options = [
    "Senior Strategy Consultant",
    "Chief Financial Officer (CFO)",
    "Venture Capital Partner",
    "Supply Chain & Operations Director",
    "Chief Marketing Officer (CMO)"
]
selected_persona = st.sidebar.selectbox("Choose Analytical Persona:", persona_options)

st.sidebar.markdown("---")
st.sidebar.markdown("## Assessment History")

# Load history from Supabase if configured
history_items = db.load_history()
selected_query = None

if history_items:
    for item in history_items:
        label = f"{item['query'][:30]}... ({item['persona'].split()[0]})"
        if st.sidebar.button(label, key=f"hist_{item['id']}"):
            selected_query = item
else:
    st.sidebar.info("No past reports yet. Run an analysis to save history!")

st.title("📈 AI Research Analyst")
st.markdown("**Automated Market Intelligence & Strategic Assessment Platform**")

# If user clicked a history item, display it; otherwise show input
if selected_query:
    st.info(f"Loaded past report for query: **{selected_query['query']}** (Persona: {selected_query['persona']})")
    report = selected_query['report']
    
    st.subheader("Executive Summary")
    st.write(report.get("executive_summary"))
    
    st.subheader("Strategic Recommendation")
    st.write(report.get("recommendation"))
    
    if st.button("Clear View / New Search"):
        st.rerun()
else:
    query = st.text_input("Enter a strategic business question:", placeholder="e.g., Should an independent D2C brand expand into...")

    if st.button("Run Strategic Analysis", type="primary"):
        if not query.strip():
            st.warning("Please enter a valid strategic question.")
        else:
            with st.spinner(f"Running analysis with {selected_persona}..."):
                try:
                    engine = ResearchEngine()
                    result = engine.analyze_question(query, persona=selected_persona)
                    
                    # Save to Supabase
                    report_dict = result.model_dump()
                    db.save_report(query, selected_persona, report_dict)
                    
                    st.success("Analysis complete and saved to history!")
                    
                    st.subheader("Executive Summary")
                    st.write(result.executive_summary)
                    
                    st.subheader("Strategic Recommendation")
                    st.write(result.recommendation)
                    
                    for trend in result.market_trends:
                        st.write(f"- **{trend.year}**: {trend.market_size} ({trend.growth_rate})")
                        
                except Exception as e:
                    st.error(f"An error occurred during research: {e}")
