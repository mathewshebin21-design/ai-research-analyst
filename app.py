import streamlit as st
from src.research import ResearchEngine

st.set_page_config(page_title="AI Research Analyst", page_icon="📈", layout="wide")

st.sidebar.markdown("## Configuration")

# Expanded list of analytical personas
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
st.sidebar.info("Past reports session storage is active.")

st.title("📈 AI Research Analyst")
st.markdown("**Automated Market Intelligence & Strategic Assessment Platform**")

query = st.text_input("Enter a strategic business question:", placeholder="e.g., Should an independent D2C brand expand into...")

if st.button("Run Strategic Analysis", type="primary"):
    if not query.strip():
        st.warning("Please enter a valid strategic question.")
    else:
        with st.spinner(f"Running analysis with {selected_persona}..."):
            try:
                engine = ResearchEngine()
                result = engine.analyze_question(query, persona=selected_persona)
                
                st.success("Analysis complete!")
                
                # Display Executive Summary
                st.subheader("Executive Summary")
                st.write(result.executive_summary)
                
                # Display Recommendation
                st.subheader("Strategic Recommendation")
                st.write(result.recommendation)
                
                # Display Market Trends / Size
                st.subheader("Market Trend Projections")
                for trend in result.market_trends:
                    st.write(f"- **{trend.year}**: {trend.market_size} ({trend.growth_rate})")
                    
            except Exception as e:
                st.error(f"An error occurred during research: {e}")
