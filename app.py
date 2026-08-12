import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.research import ResearchEngine
from src.pdf_generator import generate_pdf_report

st.set_page_config(page_title="AI Research Analyst", page_icon="📈", layout="wide")

st.title("📈 AI Research Analyst")
st.caption("Automated Market Intelligence & Strategic Assessment Platform")

# Initialize session state
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

query = st.text_input(
    "Enter a strategic business question:",
    value="Should a UK fashion company launch a premium technical outdoor-streetwear collection in 2027?"
)

if st.button("Run Strategic Analysis", type="primary"):
    with st.spinner("Analyzing opportunity with Gemini..."):
        try:
            engine = ResearchEngine()
            st.session_state.analysis = engine.analyze_question(query)
            st.session_state.last_query = query
            st.success("Analysis Complete!")
        except Exception as e:
            st.error(f"An error occurred during research: {e}")

# Display results if available
if st.session_state.analysis is not None:
    analysis = st.session_state.analysis
    saved_query = st.session_state.last_query

    st.markdown("---")

    # Executive Summary & Recommendation Card
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(label="Recommendation", value=analysis.recommendation)
    with col2:
        st.subheader("Executive Summary")
        st.write(analysis.executive_summary)

    st.markdown("---")

    # Interactive Charts Section using Plotly
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
        # Example dynamic confidence gauge based on recommendation weight
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