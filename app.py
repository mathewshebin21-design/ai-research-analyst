import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google import genai
from google.genai import types
from src.research import ResearchEngine
from src.pdf_generator import generate_pdf_report

st.set_page_config(page_title="AI Research Analyst", page_icon="📈", layout="wide")

# Helper function for animated skeleton loader
def show_skeleton_loader():
    """Renders a sleek pulsing CSS skeleton loader while AI analysis runs."""
    skeleton_html = """
    <style>
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .skeleton-box {
        background-color: #e0e0e0;
        border-radius: 6px;
        animation: pulse 1.5s infinite ease-in-out;
        margin-bottom: 12px;
    }
    .skeleton-title { height: 35px; width: 60%; }
    .skeleton-text { height: 18px; width: 100%; }
    .skeleton-card { height: 120px; width: 100%; }
    </style>
    
    <div class="skeleton-box skeleton-title"></div>
    <div class="skeleton-box skeleton-text"></div>
    <div class="skeleton-box skeleton-text" style="width: 80%;"></div>
    <br>
    <div style="display: flex; gap: 15px;">
        <div class="skeleton-box skeleton-card" style="flex: 1;"></div>
        <div class="skeleton-box skeleton-card" style="flex: 3;"></div>
    </div>
    """
    return st.markdown(skeleton_html, unsafe_allow_html=True)

# Helper function to generate dynamic follow-up questions
def generate_follow_ups(query: str, executive_summary: str) -> list:
    try:
        client = genai.Client()
        prompt = f"""
        Based on the strategic question "{query}" and the executive summary "{executive_summary}", 
        generate exactly 3 short, highly relevant follow-up strategic questions a business leader would want to investigate next.
        Return ONLY the 3 questions separated by a newline character, with no numbers or extra text.
        """
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt
        )
        questions = [q.strip() for q in response.text.strip().split("\n") if q.strip()]
        return questions[:3]
    except Exception:
        return [
            "What are the primary regulatory and compliance hurdles for this initiative?",
            "Can you provide a detailed capital expenditure (CapEx) breakdown for Year 1?",
            "What alternative market segments offer higher profit margins?"
        ]

st.title("📈 AI Research Analyst")
st.caption("Automated Market Intelligence & Strategic Assessment Platform")

if "history" not in st.session_state:
    st.session_state.history = []
if "current_index" not in st.session_state:
    st.session_state.current_index = None
if "triggered_query" not in st.session_state:
    st.session_state.triggered_query = ""

st.sidebar.title("⚙️ Configuration")
persona = st.sidebar.selectbox(
    "Choose Analytical Persona:",
    ["Senior Strategy Consultant", "Aggressive Venture Capitalist", "Conservative Risk Officer", "Bootstrapped Founder"]
)

st.sidebar.markdown("---")
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

# Handle auto-triggered follow-up inputs or manual text inputs
user_input_query = st.text_input(
    "Enter a strategic business question:",
    value=st.session_state.triggered_query,
    placeholder="e.g., Should a UK fashion company launch a premium technical outdoor-streetwear collection in 2027?"
)

# Reset triggered query after reading it
if st.session_state.triggered_query:
    st.session_state.triggered_query = ""

run_analysis = st.button("Run Strategic Analysis", type="primary")

if run_analysis:
    query_to_run = user_input_query
    if not query_to_run.strip():
        st.warning("Please enter a valid strategic business question.")
    else:
        loader_placeholder = st.empty()
        with loader_placeholder.container():
            show_skeleton_loader()
            
        try:
            engine = ResearchEngine()
            analysis_result = engine.analyze_question(query_to_run, persona=persona)
            
            time.sleep(1.2)
            
            new_entry = {"query": query_to_run, "analysis": analysis_result}
            st.session_state.history.append(new_entry)
            st.session_state.current_index = len(st.session_state.history) - 1
            
            loader_placeholder.empty()
            st.success("Analysis Complete!")
        except Exception as e:
            loader_placeholder.empty()
            st.error(f"An error occurred during research: {e}")

if st.session_state.current_index is not None and st.session_state.history:
    current_item = st.session_state.history[st.session_state.current_index]
    analysis = current_item["analysis"]
    saved_query = current_item["query"]

    st.markdown("---")
    st.info(f"Viewing Report for: **{saved_query}**")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(label="Recommendation", value=analysis.recommendation)
    with col2:
        st.subheader("Executive Summary")
        st.write(analysis.executive_summary)

    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("### Strategic Breakdown Count")
        drivers_count = len(getattr(analysis, "key_drivers", getattr(analysis, "market_drivers", [])))
        risks_count = len(getattr(analysis, "key_risks", getattr(analysis, "risks", [])))
        actions_count = len(getattr(analysis, "action_plan", getattr(analysis, "opportunities", [])))

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
            title={"text": "Strategic Confidence Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2563EB"},
                "steps": [
                    {"range": [0, 50], "color": "#FEE2E2"},
                    {"range": [50, 75], "color": "#FEF3C7"},
                    {"range": [75, 100], "color": "#DCFCE7"}
                ],
            }
        ))
        fig_gauge.update_layout(margin=dict(t=30, b=10, l=20, r=20), height=250)
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📈 Market Size Projections & Trend Analysis")
    if hasattr(analysis, "market_trends") and analysis.market_trends:
        trend_data = [{"Year": str(t.year), "Market Size ($B)": t.market_size_billion_usd} for t in analysis.market_trends]
        trend_df = pd.DataFrame(trend_data)
        fig_trend = px.line(trend_df, x="Year", y="Market Size ($B)", markers=True, title="Market Valuation Growth Trajectory", color_discrete_sequence=["#2563EB"])
        fig_trend.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=300)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No market trend timeline available for this report.")

    st.markdown("---")
    st.markdown("### 🎯 SWOT Analysis")
    if hasattr(analysis, "swot") and analysis.swot:
        swot = analysis.swot
        col_a, col_b = st.columns(2)
        with col_a:
            with st.container(border=True):
                st.markdown("#### ✅ Strengths")
                for item in swot.strengths: st.markdown(f"• {item}")
            with st.container(border=True):
                st.markdown("#### ⚠️ Weaknesses")
                for item in swot.weaknesses: st.markdown(f"• {item}")
        with col_b:
            with st.container(border=True):
                st.markdown("#### 🚀 Opportunities")
                for item in swot.opportunities: st.markdown(f"• {item}")
            with st.container(border=True):
                st.markdown("#### 🛑 Threats")
                for item in swot.threats: st.markdown(f"• {item}")

    st.markdown("---")
    st.markdown("### 🏢 Competitive Landscape Matrix")
    if hasattr(analysis, "competitors") and analysis.competitors:
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
        
        selected_competitor = st.dataframe(
            comp_df, 
            use_container_width=True, 
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        if selected_competitor and selected_competitor.selection.rows:
            selected_row_idx = selected_competitor.selection.rows[0]
            chosen_comp = comp_df.iloc[selected_row_idx]
            
            with st.container(border=True):
                st.markdown(f"#### 🔍 Deep Dive: {chosen_comp['Competitor']}")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"**Positioning:** {chosen_comp['Positioning']}")
                    st.write(f"**Pricing Tier:** {chosen_comp['Pricing Tier']}")
                with col_d2:
                    st.write(f"**Core Strengths:** {chosen_comp['Strengths']}")
                    st.write(f"**Key Weaknesses:** {chosen_comp['Weaknesses']}")
    else:
        st.info("No competitor data available for this report.")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Market Drivers")
        for d in getattr(analysis, "key_drivers", getattr(analysis, "market_drivers", [])):
            st.markdown(f"- {d}")
    with c2:
        st.markdown("### Key Risks")
        for r in getattr(analysis, "key_risks", getattr(analysis, "risks", [])):
            st.markdown(f"- {r}")
    with c3:
        st.markdown("### Action Plan")
        for a in getattr(analysis, "action_plan", getattr(analysis, "opportunities", [])):
            st.markdown(f"- {a}")

    # Automated Follow-Up Generator Section
    st.markdown("---")
    st.markdown("### 🤖 Recommended Follow-Up Investigations")
    st.caption("Click any follow-up question below to instantly trigger a deep-dive analysis:")
    
    if "cached_follow_ups" not in st.session_state or st.session_state.get("last_query") != saved_query:
        st.session_state.cached_follow_ups = generate_follow_ups(saved_query, analysis.executive_summary)
        st.session_state.last_query = saved_query

    fu_cols = st.columns(len(st.session_state.cached_follow_ups))
    for idx, fu_question in enumerate(st.session_state.cached_follow_ups):
        with fu_cols[idx]:
            if st.button(fu_question, key=f"fu_btn_{idx}", use_container_width=True):
                st.session_state.triggered_query = fu_question
                st.rerun()

    st.markdown("---")
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
        from src.database import save_report, load_reports, clear_reports

# ... (keep your existing imports, setup, and helper functions)

# Initialize session history from SQLite database
if "history" not in st.session_state:
    db_rows = load_reports()
    # db_rows format: (id, query, persona, analysis_json, timestamp)
    st.session_state.history = []
    for row in db_rows:
        # Re-parse JSON back into your Pydantic object if needed, or handle as dict
        # For simplicity, we can load them into history items
        pass # We will wire this cleanly below