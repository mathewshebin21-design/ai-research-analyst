import streamlit as st
from src.research import ResearchEngine
from src.pdf_generator import generate_pdf_report

st.set_page_config(page_title="AI Research Analyst", page_icon="📈", layout="wide")

st.title("📈 AI Research Analyst")
st.caption("Automated Market Intelligence & Strategic Assessment Platform")

query = st.text_input(
    "Enter a strategic business question:",
    value="Should a UK fashion company launch a premium technical outdoor-streetwear collection in 2027?"
)

if st.button("Run Strategic Analysis", type="primary"):
    with st.spinner("Analyzing opportunity with Gemini..."):
        try:
            engine = ResearchEngine()
            analysis = engine.analyze_question(query)

            st.success("Analysis Complete!")

            # Metric / Executive Summary Display
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
                for d in analysis.market_drivers:
                    st.markdown(f"- {d}")
            
            with c2:
                st.markdown("### Key Risks")
                for r in analysis.key_risks:
                    st.markdown(f"- {r}")

            with c3:
                st.markdown("### Action Plan")
                for a in analysis.action_plan:
                    st.markdown(f"- {a}")

            st.markdown("---")

            # PDF Download Button
            pdf_bytes = generate_pdf_report(analysis, query)
            st.download_button(
                label="📄 Download Strategic Report (PDF)",
                data=pdf_bytes,
                file_name="Strategic_Market_Assessment.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"An error occurred during research: {e}")