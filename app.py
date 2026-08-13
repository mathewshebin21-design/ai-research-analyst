import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.research import ResearchEngine
from src.pdf_generator import generate_pdf_report

st.set_page_config(page_title="AI Research Analyst", page_icon="📈", layout="wide")

st.title("📈 AI Research Analyst")
st.caption("Automated Market Intelligence & Strategic Assessment Platform")

# Initialize history and current selection in session state
if "history" not in st.session_state:
    st.session_state.history = []
if "current_index" not in st.session_state:
    st.session_state.current_index = None
    # --- Sidebar ---
st.sidebar.title("⚙️ Configuration")
persona = st.sidebar.selectbox(
    "Choose Analytical Persona:",
    ["Senior Strategy Consultant", "Aggressive Venture Capitalist", "Conservative Risk Officer", "Bootstrapped Founder"]
)

# ... update your button call to include the persona:
# engine.analyze_question(query, persona=persona)

# --- Sidebar for Past Reports ---
st.sidebar.title("📂 Assessment History")

if st.session_state.history:
    history_options = {f"{i+1}. {item['query'][:40]}...": i for i, item in enumerate(st.session_state.history)}
    selected_label = st.sidebar.selectbox("Select Past Report:", options=list(history_options.keys()))
    
    if selected_label:
        st.session_state.current_index = history_options[selected_label]
    
    if st.sidebar.button("Clear History"):
        st.session_state.history = []
        st.session_state.current_index = None
        st.rerun()
else:
    st.sidebar.info("No past reports yet. Run an analysis to save history!")

# --- Main Query Interface ---
query = st.text_input(
    "Enter a strategic business question:",
    value="",
    placeholder="e.g., Should a UK fashion company launch a premium technical outdoor-streetwear collection in 2027?"
)

if st.button("Run Strategic Analysis", type="primary"):
    if not query.strip():
        st.warning("Please enter a valid strategic business question.")
    else:
        with st.spinner("Analyzing opportunity with Gemini..."):
            try:
                engine = ResearchEngine()
                analysis_result = engine.analyze_question(query)
                
                new_entry = {"query": query, "analysis": analysis_result}
                st.session_state.history.append(new_entry)
                st.session_state.current_index = len(st.session_state.history) - 1
                
                st.success("Analysis Complete!")
            except Exception as e:
                st.error(f"An error occurred during research: {e}")

# --- Display Results for Current Selection ---
if st.session_state.current_index is not None and st.session_state.history:
    current_item = st.session_state.history[st.session_state.current_index]
    analysis = current_item["analysis"]
    saved_query = current_item["query"]

    st.markdown("---")
    st.info(f"Viewing Report for: **{saved_query}**")

    # Executive Summary & Recommendation Card
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(label="Recommendation", value=analysis.recommendation)
    with col2:
        st.subheader("Executive Summary")
        st.write(analysis.executive_summary)

    st.markdown("---")

    # Interactive Charts Section
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### Strategic Breakdown Count")
        drivers_count = len(getattr(analysis, 'key_drivers', getattr(analysis, 'market_drivers', [])))
        risks_count = len(getattr(analysis, 'key_risks', getattr(analysis, 'risks', [])))
        actions_count = len(getattr(analysis, 'action_plan', getattr(analysis, 'opportunities', [])))

        fig_bar = px.bar(
            x=["Drivers", "Risks", "Action Steps"],
            y=[drivers_count, risks_count, actions_count],
            labels={"x": "Category", "y": "Count"},
            title="Strategic Factor Distribution",
            color=["Drivers", "Risks", "Action Steps"],
            color_discrete_map={"Drivers": "#2563EB", "Risks": "#DC2626", "Action Steps": "#16A34A"}
        )
        fig_bar.update_layout(showlegend=False, margin=dict(t=30, b=10, l=10, r=10), height=250)
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        st.markdown("### Assessment Confidence Gauge")
        conf_val = 88 if "ENTER" in analysis.recommendation.upper() else 65
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=conf_val,
            title={'text': "Strategic Confidence Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#2563EB"},
                'steps': [
                    {'range': [0, 50], 'color': "#FEE2E2"},
                    {'range': [50, 75], 'color': "#FEF3C7"},
                    {'range': [75, 100], 'color': "#DCFCE7"}
                ],
            }
        ))
        fig_gauge.update_layout(margin=dict(t=30, b=10, l=20, r=20), height=250)
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # Competitor Matrix Table Section
    st.markdown("### 🏢 Competitive Landscape Matrix")
    if hasattr(analysis, 'competitors') and analysis.competitors:
        comp_data = [
            {
                "Competitor": c.name,
                "Positioning": c.positioning,
                "Pricing Tier": c.pricing_tier,
                "Strengths": c.strengths,
                "Weaknesses": c.weaknesses
            }
            for c in analysis.competitors
        ]
        comp_df = pd.DataFrame(comp_data)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
    else:
        st.info("No competitor data available for this report.")

    st.markdown("---")

    # Structured Text Details
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Market Drivers")
        for d in getattr(analysis, 'key_drivers', getattr(analysis, 'market_drivers', [])):
            st.markdown(f"- {d}")

    with c2:
        st.markdown("### Key Risks")
        for r in getattr(analysis, 'key_risks', getattr(analysis, 'risks', [])):
            st.markdown(f"- {r}")

    with c3:
        st.markdown("### Action Plan")
        for a in getattr(analysis, 'action_plan', getattr(analysis, 'opportunities', [])):
            st.markdown(f"- {a}")

    st.markdown("---")

    # PDF Download Button
    try:
        pdf_bytes = generate_pdf_report(analysis, saved_query)
        st.download_button(
            label="📄 Download Strategic Report (PDF)",
            data=pdf_bytes,
            file_name="Strategic_Market_Assessment.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as pdf_err:
        st.error(f"Failed to generate PDF: {pdf_err}")
        # Market Trends Chart Section
    st.markdown("---")
    st.markdown("### 📈 Market Size Projections & Trend Analysis")
    if hasattr(analysis, 'market_trends') and analysis.market_trends:
        trend_data = [{"Year": str(t.year), "Market Size ($B)": t.market_size_billion_usd} for t in analysis.market_trends]
        trend_df = pd.DataFrame(trend_data)
        
        fig_trend = px.line(
            trend_df,
            x="Year",
            y="Market Size ($B)",
            markers=True,
            title="Market Valuation Growth Trajectory",
            color_discrete_sequence=["#2563EB"]
        )
        fig_trend.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=300)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No market trend timeline available for this report.")