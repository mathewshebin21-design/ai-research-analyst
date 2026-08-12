import streamlit as st
from src.research import ResearchEngine
from src.pdf_generator import generate_pdf_report

st.set_page_config(page_title="AI Research Analyst", page_icon="📈", layout="wide")

st.title("📈 AI Research Analyst")
st.caption("Automated Market Intelligence & Strategic Assessment Platform")

# Initialize session state for analysis results
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
            # Store results into session state so it survives script reruns
            st.session_state.analysis = engine.analyze_question(query)
            st.session_state.last_query = query
            st.success("Analysis Complete!")
        except Exception as e:
            st.error(f"An error occurred during research: {e}")

# Display results if available in session_state
if st.session_state.analysis is not None:
    analysis = st.session_state.analysis
    saved_query = st.session_state.last_query

    st.markdown("---")

    # Executive Summary Section
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(label="Recommendation", value=analysis.recommendation)
    with col2:
        st.subheader("Executive Summary")
        st.write(analysis.executive_summary)

    st.markdown("---")

    # Structured Breakdown
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Market Drivers")
        drivers = getattr(analysis, 'key_drivers', getattr(analysis, 'market_drivers', []))
        for d in drivers:
            st.markdown(f"- {d}")

    with c2:
        st.markdown("### Key Risks")
        risks = getattr(analysis, 'key_risks', getattr(analysis, 'risks', []))
        for r in risks:
            st.markdown(f"- {r}")

    with c3:
        st.markdown("### Action Plan")
        actions = getattr(analysis, 'action_plan', getattr(analysis, 'opportunities', []))
        for a in actions:
            st.markdown(f"- {a}")

    st.markdown("---")

    # Generate PDF bytes in memory
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