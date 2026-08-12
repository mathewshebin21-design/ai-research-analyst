import streamlit as st
from src.research import ResearchEngine

st.set_page_config(page_title="AI Research Analyst", page_icon="📈", layout="wide")

st.title("📈 AI Research Analyst")
st.subheader("Automated Market Intelligence & Strategic Assessment Platform")

query = st.text_input(
    "Enter a strategic business question:",
    placeholder="e.g., Should a UK fashion company launch a premium technical outdoor-streetwear collection in 2027?"
)

if st.button("Run Strategic Analysis", type="primary"):
    if not query.strip():
        st.warning("Please enter a valid research question.")
    else:
        with st.spinner("Analyzing market dynamics, competition, and economics..."):
            try:
                engine = ResearchEngine()
                result = engine.analyze_question(query)

                st.divider()

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(
                        label="Overall Opportunity Score",
                        value=f"{result.matrix.overall_opportunity_score} / 100"
                    )

                    if result.recommendation == "ENTER":
                        st.success(f"### Recommendation: {result.recommendation}")
                    elif result.recommendation == "DO NOT ENTER":
                        st.error(f"### Recommendation: {result.recommendation}")
                    else:
                        st.warning(f"### Recommendation: {result.recommendation}")

                with col2:
                    st.markdown("### Executive Summary")
                    st.write(result.executive_summary)

                st.divider()

                st.markdown("### 📊 Market Factor Breakdown")
                matrix_data = {
                    "Factor": [
                        "Market Attractiveness",
                        "Customer Demand",
                        "Competitive Intensity",
                        "Pricing Opportunity",
                        "Entry Difficulty"
                    ],
                    "Score (0-100)": [
                        result.matrix.market_attractiveness,
                        result.matrix.customer_demand,
                        result.matrix.competitive_intensity,
                        result.matrix.pricing_opportunity,
                        result.matrix.entry_difficulty
                    ]
                }
                st.table(matrix_data)

                col3, col4 = st.columns(2)
                with col3:
                    st.markdown("### 🎯 Strategic Opportunity")
                    st.info(result.strategic_opportunity)

                    st.markdown("### 💡 Key Opportunities")
                    for opp in result.opportunities:
                        st.markdown(f"- {opp}")

                with col4:
                    st.markdown("### 🛠️ Suggested Strategy")
                    st.write(result.suggested_strategy)

                    st.markdown("### ⚠️ Key Risks")
                    for risk in result.key_risks:
                        st.markdown(f"- {risk}")

            except Exception as e:
                st.error(f"An error occurred during research: {str(e)}")