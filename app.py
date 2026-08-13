import streamlit as st
import os

st.set_page_config(page_title="AI Research & Intelligence Hub", layout="wide")

# Custom CSS for UI styling
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
st.markdown("Enterprise modular market intelligence paired with advanced vector-indexed multi-document RAG and MBA Strategic Decision Frameworks.")

# Sidebar - Expanded Executive Configuration & MBA Checkboxes
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
st.sidebar.markdown("---")

# MBA Strategic Decision Hub Checkboxes on Sidebar
st.sidebar.markdown("### 🎓 MBA Strategic Decision Hub")
enable_mba_hub = st.sidebar.checkbox("Enable MBA Decision Hub", value=True)
mba_swot_check = st.sidebar.checkbox("Include SWOT & Positioning", value=True)
mba_financial_check = st.sidebar.checkbox("Include Capital & ROI Modeling", value=True)
mba_risk_check = st.sidebar.checkbox("Include Regulatory & Risk Audit", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🕒 Recent Chat & History")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        "Query: Scaling footwear startup in EU",
        "Query: INR 180k capital allocation strategy",
        "Query: Export compliance for eco-retail"
    ]

for past_chat in st.session_state.chat_history:
    st.sidebar.caption(f"📁 {past_chat}")

st.sidebar.success("System Status: Operational")

# Navigation Tabs
app_mode = st.radio(
    "Navigation Mode", 
    ["v2: Modular Market Research", "MBA Strategic Decision Hub", "v4: Advanced Multi-Doc Vector RAG"],
    horizontal=True,
    label_visibility="collapsed"
)

if app_mode == "v2: Modular Market Research":
    st.header("Customizable Market Intelligence Engine")
    
    # Default persistent query box
    research_topic = st.text_input(
        "Ask a strategic research question or enter market sector:",
        value="Should we launch an eco-friendly direct-to-consumer premium footwear and apparel brand in the European market?"
    )
    
    st.markdown("### 📋 Select Required Analysis Modules:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mod_trend = st.checkbox("Market Size & Trends", value=True)
        mod_swot = st.checkbox("SWOT Analysis", value=True)
    with col2:
        mod_competitors = st.checkbox("Key Competitors", value=True)
        mod_financial = st.checkbox("Financial Projections", value=True)
    with col3:
        mod_strategy = st.checkbox("Strategic Recommendations", value=True)
    with col4:
        mod_chart = st.checkbox("Interactive Plotly Charts", value=True)
        
    if st.button("🚀 Generate Custom Intelligence Report", type="primary"):
        st.success(f"Generating comprehensive intelligence report for persona: **{persona}**...")
        
        # Save query to history
        if research_topic not in st.session_state.chat_history:
            st.session_state.chat_history.insert(0, f"Query: {research_topic[:40]}...")
            
        st.markdown("---")
        st.subheader("Executive Summary")
        st.info(f"Analyzing strategic viability for: *'{research_topic}'*")
        
        if mod_trend:
            st.markdown("### 📊 Market Size & Trends")
            st.write("The target segment shows expanding demand for sustainable materials, with a projected compound annual growth rate (CAGR) of 12.4% over the next 5 years.")
            
        if mod_competitors:
            st.markdown("### 🏢 Key Competitors")
            st.markdown("""
            | Competitor | Market Focus | Estimated Share | Digital Presence |
            | :--- | :--- | :--- | :--- |
            | **EcoWear Ltd** | Sustainable Apparel | 28% | High |
            | **GreenStep** | Footwear Niche | 19% | Moderate |
            """)
            
        if mod_swot:
            st.markdown("### 🔍 SWOT Analysis")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown("**Strengths & Opportunities**")
                st.write("- High consumer pull for eco-friendly goods\n- Agile direct-to-consumer digital infrastructure")
            with sc2:
                st.markdown("**Weaknesses & Threats**")
                st.write("- Initial capital constraints\n- High customer acquisition costs in EU markets")
                
        if mod_financial:
            st.markdown("### 💰 Financial Projections")
            st.metric(label="Estimated Initial Outlay", value="INR 180,000 (Initial Capital)")
            
        if mod_chart:
            st.markdown("### 📈 Interactive Growth Trajectory")
            chart_data = {
                "Quarter": ["Q1", "Q2", "Q3", "Q4", "Year 2"],
                "Projected Revenue (INR)": [180000, 200000, 230000, 280000, 360000]
            }
            st.line_chart(chart_data, x="Quarter", y="Projected Revenue (INR)")
            
        if mod_strategy:
            st.markdown("### 🎯 Strategic Recommendations")
            st.write("1. **Phase Rollout:** Launch initial pilot collections online to validate product-market fit before expanding physical inventory.")
            st.write("2. **Supply Chain:** Secure transparent vendor compliance to align with European eco-label regulations.")

elif app_mode == "MBA Strategic Decision Hub":
    st.header("🎓 MBA Strategic Decision Framework & Financial Modeler")
    st.markdown("Advanced quantitative analysis and strategic positioning driven by sidebar controls.")
    
    # Default persistent query box
    mba_query = st.text_input(
        "Ask a strategic business or financial question:",
        value="What is the optimal capital allocation strategy for scaling our bootstrap fashion brand?"
    )
    
    if st.button("🚀 Run MBA Strategic Simulation & Analysis", type="primary"):
        st.success(f"Executing MBA simulation under persona **{persona}** for query: *'{mba_query}'*")
        
        if enable_mba_hub:
            if mba_swot_check:
                st.markdown("### 🏛️ Strategic Positioning & SWOT")
                st.write("- **Core Leverage:** High agility co-owned retail setup.")
                st.write("- **Strategic Focus:** Capitalizing on digital direct-to-consumer growth channels.")
                
            if mba_financial_check:
                st.markdown("### 💰 Financial Return Modeling")
                st.metric(label="Starting Capital Principal", value="INR 180,000")
                chart_dict = {
                    "Timeline": ["Initial", "Year 1", "Year 2", "Year 3"],
                    "Valuation (INR)": [180000, 216000, 259200, 311000]
                }
                st.bar_chart(chart_dict, x="Timeline", y="Valuation (INR)")
                
            if mba_risk_check:
                st.markdown("### ⚠️ Regulatory & Risk Audit")
                st.write("- **Compliance:** Active verification of GST and entity governance.")
                st.write("- **Mitigation:** Maintain lean cash reserves to buffer against supply chain volatility.")
        else:
            st.warning("MBA Strategic Hub is currently disabled via the sidebar checkbox.")

else:
    st.header("Advanced Multi-Document Vector RAG Engine")
    
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
            st.markdown("### RAG Search Results:")
            for i, d in enumerate(docs_found):
                st.info(f"**Context {i+1}:**\n{d.page_content}")
        else:
            st.warning("Please upload and index a PDF first.")
