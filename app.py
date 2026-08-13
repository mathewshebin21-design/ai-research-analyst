import streamlit as st
import os
import pandas as pd
from planner import AIResearchPlanner
from tavily_search import WebSearchModule
from rag import AdvancedRAGEngine
from scoring import StrategicScorer
from financials import FinancialScenarioModeler

st.set_page_config(page_title="AI Research & Intelligence Hub", layout="wide")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Research & Intelligence Hub")
st.markdown("Automated Market Intelligence & Strategic Decision Support Platform (MBA & AI Multi-Agent Architecture).")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        "Should we launch an eco-friendly direct-to-consumer premium footwear and apparel brand in the European market?",
        "What is the optimal capital allocation strategy for scaling our bootstrap fashion brand?",
        "Export compliance and trade regulations for international apparel retail"
    ]

if "active_query" not in st.session_state:
    st.session_state.active_query = st.session_state.chat_history[0]

# Sidebar - Executive Control Center & Interactive History
st.sidebar.markdown("### 🎛️ Executive Control Center")
persona_category = st.sidebar.radio("Select Persona Domain:", ["Financial & Strategy", "Technical & Supply Chain", "Executive Leadership"])

if persona_category == "Financial & Strategy":
    persona = st.sidebar.selectbox(
        "Choose Specialist:",
        ["General Market Analyst", "Financial Risk Expert", "Startup Strategist", "Macroeconomic Policy Advisor", "Venture Capital Partner"]
    )
elif persona_category == "Technical & Supply Chain":
    persona = st.sidebar.selectbox(
        "Choose Specialist:",
        ["Technical Due Diligence Agent", "Supply Chain & Export Specialist", "Operations Lead", "Global Trade Consultant"]
    )
else:
    persona = st.sidebar.selectbox(
        "Choose Specialist:",
        ["Chief Executive Officer", "Chief Technology Officer", "Chief Marketing Officer"]
    )

st.sidebar.markdown(f"**Active Persona:** `{persona}`")
st.sidebar.success("System Status: Operational")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🕒 Interactive Chat & History")
st.sidebar.caption("Click any past query to reload it:")

for i, past_query in enumerate(st.session_state.chat_history):
    display_label = past_query[:38] + "..." if len(past_query) > 38 else past_query
    if st.sidebar.button(f"📁 {display_label}", key=f"history_btn_{i}"):
        st.session_state.active_query = past_query
        st.rerun()

if st.sidebar.button("🗑️ Clear History"):
    st.session_state.chat_history = []
    st.session_state.active_query = ""
    st.rerun()

# Top Navigation Bar
app_mode = st.radio(
    "Navigation Bar", 
    ["v2: Modular Market Research", "MBA Strategic Decision Hub", "v4: Advanced Multi-Doc Vector RAG"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

if app_mode == "v2: Modular Market Research":
    st.header("Customizable Market Intelligence & AI Research Planner")
    
    research_topic = st.text_input(
        "Ask a strategic research question or enter market sector:",
        value=st.session_state.active_query
    )
    
    if research_topic != st.session_state.active_query:
        st.session_state.active_query = research_topic
    
    if research_topic:
        with st.expander("🧠 AI Research Planner Decomposition", expanded=True):
            plan = AIResearchPlanner.generate_plan(research_topic)
            st.write(f"**Objective:** {plan['objective']}")
            st.markdown("**Decomposed Research Tasks:**")
            for task in plan["research_tasks"]:
                st.markdown(f"- `[{task['category']}]` {task['task']}")
    
    st.markdown("### 📋 Select Required Analysis Modules:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mod_trend = st.checkbox("Market Size & Trends", value=True)
        mod_swot = st.checkbox("SWOT Analysis", value=True)
    with col2:
        mod_competitors = st.checkbox("Key Competitors", value=True)
        mod_financial = st.checkbox("Financial Projections & Scenarios", value=True)
    with col3:
        mod_strategy = st.checkbox("Strategic Recommendations", value=True)
    with col4:
        mod_chart = st.checkbox("Interactive Plotly Charts", value=True)
        
    if st.button("🚀 Generate Custom Intelligence Report", type="primary"):
        st.success(f"Executing multi-agent research plan and financial scenario modeling under persona: **{persona}**...")
        
        if research_topic and research_topic not in st.session_state.chat_history:
            st.session_state.chat_history.insert(0, research_topic)
            
        st.markdown("---")
        st.subheader("Executive Summary & Strategic Decision Intelligence")
        st.info(f"Analyzing strategic viability for: *'{research_topic}'*")
        
        # Display Quantitative Scoring Dials
        scores = StrategicScorer.calculate_scores(research_topic)
        st.markdown("### 📊 Quantitative Strategic Decision Scores")
        sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
        sc1.metric("Attractiveness", f"{scores['market_attractiveness']}/100")
        sc2.metric("Opportunity", f"{scores['opportunity_score']}/100")
        sc3.metric("Competition", f"{scores['competitive_intensity']}/100")
        sc4.metric("Difficulty", f"{scores['execution_difficulty']}/100")
        sc5.metric("Risk Score", f"{scores['risk_score']}/100")
        sc6.metric("Confidence", f"{scores['confidence_rating']}/100")
        
        # Display Traceable Evidence Model
        evidence_list = AdvancedRAGEngine.query_evidence_sources(research_topic)
        with st.expander("🔍 Traceable Evidence & Source Attribution Model", expanded=False):
            for idx, ev in enumerate(evidence_list, 1):
                st.markdown(f"**Source {idx}: [{ev['title']}]({ev['url']})**")
                st.caption(f"Publisher: {ev['publisher']} | Published: {ev['publication_date']} | Retrieved: {ev['retrieved_date']} | Relevance: {ev['relevance']}")
                st.info(f"**Supported Claim:** {ev['claim_supported']}")
        
        if mod_trend:
            st.markdown("### 📊 Market Size & Trends")
            st.write("European consumer demand for sustainable footwear and apparel is growing at a 12.4% CAGR.")
            
        if mod_competitors:
            st.markdown("### 🏢 Competitor Intelligence Matrix")
            st.markdown("""
            | Competitor | Market Focus | Estimated Share | Digital Presence | Competitive Advantage |
            | :--- | :--- | :--- | :--- | :--- |
            | **EcoWear Ltd** | Sustainable Apparel | 28% | High | Established European distribution |
            | **GreenStep** | Footwear Niche | 19% | Moderate | Proprietary eco-soles |
            | **Your Venture** | D2C Eco-Fashion | Emerging | High (Agile) | Co-owned agile bootstrap model (INR 180k capital) |
            """)
            
        if mod_swot:
            st.markdown("### 🔍 SWOT Intelligence Matrix")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown("**Strengths & Opportunities**")
                st.write("- High consumer pull for eco-friendly goods\n- Agile direct-to-consumer digital infrastructure\n- Low overhead bootstrap execution")
            with sc2:
                st.markdown("**Weaknesses & Threats**")
                st.write("- Initial capital constraints (INR 180,000 baseline)\n- High customer acquisition costs in EU markets\n- Regulatory compliance overhead")
                
        if mod_financial:
            st.markdown("### 💰 Financial Scenarios & What-If Modeler")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                cap_input = st.number_input("Initial Capital (INR)", value=180000.0, step=10000.0)
            with col_f2:
                growth_input = st.slider("Annual Growth Driver (%)", min_value=5.0, max_value=50.0, value=25.0, step=1.0) / 100.0
                
            scenarios = FinancialScenarioModeler.calculate_scenarios(cap_input, growth_input)
            df_scenarios = pd.DataFrame(scenarios).set_index("Timeline")
            
            st.markdown("**Projected Valuation Across Scenarios (INR):**")
            st.dataframe(df_scenarios, use_container_width=True)
            st.line_chart(df_scenarios)
            
        if mod_chart:
            st.markdown("### 📈 Interactive Growth Trajectory")
            chart_data = {
                "Quarter": ["Q1", "Q2", "Q3", "Q4", "Year 2"],
                "Projected Revenue (INR)": [180000, 200000, 230000, 280000, 360000]
            }
            st.line_chart(chart_data, x="Quarter", y="Projected Revenue (INR)")
            
        if mod_strategy:
            st.markdown("### 🎯 Strategic Recommendations")
            st.write("1. **Phase Rollout:** Cross-border D2C retail requires strict adherence to eco-label certifications and digital tax transparency.")
            st.write("2. **Supply Chain:** Secure transparent vendor compliance to align with European eco-label regulations.")

elif app_mode == "MBA Strategic Decision Hub":
    st.header("🎓 MBA Strategic Decision Framework & Financial Modeler")
    st.markdown("Advanced quantitative analysis and strategic positioning driven by navbar selection.")
    
    mba_query = st.text_input(
        "Ask a strategic business or financial question:",
        value=st.session_state.active_query
    )
    
    if mba_query != st.session_state.active_query:
        st.session_state.active_query = mba_query
    
    if st.button("🚀 Run MBA Strategic Simulation & Analysis", type="primary"):
        st.success(f"Executing MBA simulation under persona **{persona}** for query: *'{mba_query}'*")
        
        if mba_query and mba_query not in st.session_state.chat_history:
            st.session_state.chat_history.insert(0, mba_query)
            
        st.markdown("### 🏛️ Strategic Positioning & SWOT")
        st.write("- **Core Leverage:** High agility co-owned retail setup.")
        st.write("- **Strategic Focus:** Capitalizing on digital direct-to-consumer growth channels.")
        
        st.markdown("### 💰 Financial Return Modeling & Scenarios")
        mba_scenarios = FinancialScenarioModeler.calculate_scenarios(180000.0, 0.25)
        df_mba = pd.DataFrame(mba_scenarios).set_index("Timeline")
        st.dataframe(df_mba, use_container_width=True)
        st.bar_chart(df_mba)
        
        st.markdown("### ⚠️ Regulatory & Risk Audit")
        st.write("- **Compliance:** Active verification of GST and entity governance.")
        st.write("- **Mitigation:** Maintain lean cash reserves to buffer against supply chain volatility.")

else:
    st.header("Advanced Multi-Document Vector RAG Engine & Evidence Inspector")
    
    uploaded_file = st.file_uploader("Upload PDF documents for multi-doc RAG indexing", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Process & Index Document", type="primary"):
            with st.spinner("Indexing into vector store..."):
                bytes_data = uploaded_file.read()
                os.makedirs("data", exist_ok=True)
                file_path = os.path.join("data", uploaded_file.name)
                with open(file_path, "wb") as f_out:
                    f_out.write(bytes_data)
                
                try:
                    from langchain_community.document_loaders import PyPDFLoader
                    from langchain_text_splitters import RecursiveCharacterTextSplitter
                    from langchain_community.embeddings import HuggingFaceEmbeddings
                    from langchain_community.vectorstores import FAISS

                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                    splits = splitter.split_documents(docs)

                    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                    st.session_state.vector_store = FAISS.from_documents(splits, embeddings)
                    st.success("Documents successfully indexed!")
                except Exception as e:
                    st.error(f"Error: {e}")

    rag_prompt = st.text_input("Ask a question across your indexed documents:")
    if rag_prompt:
        if "vector_store" in st.session_state:
            docs_found = st.session_state.vector_store.similarity_search(rag_prompt, k=3)
            st.markdown("### Multi-Document RAG Evidence Results:")
            for i, d in enumerate(docs_found):
                st.info(f"**Evidence Chunk {i+1} (Source: {d.metadata.get('source', 'Uploaded PDF')})**:\n{d.page_content}")
        else:
            st.warning("Please upload and index a PDF first.")
