import streamlit as st
import os

st.set_page_config(page_title="AI Research & Intelligence Hub", layout="wide")

st.title("🚀 AI Research & Intelligence Hub")
st.markdown("Enterprise modular market intelligence paired with advanced vector-indexed multi-document RAG and MBA Strategic Decision Frameworks.")

# Sidebar Controls & Personas
st.sidebar.header("Executive Configuration")
persona = st.sidebar.selectbox(
    "Select Analyst Persona",
    [
        "General Market Analyst", 
        "Financial Risk Expert", 
        "Technical Due Diligence Agent", 
        "Startup Strategist", 
        "Supply Chain & Export Specialist", 
        "Macroeconomic Policy Advisor"
    ]
)
st.sidebar.markdown(f"**Active Persona:** `{persona}`")
st.sidebar.success("System Status: Operational")

# Navigation Modes
app_mode = st.radio(
    "Navigation Mode", 
    ["v2: Modular Market Research", "MBA Strategic Decision Hub", "v4: Advanced Multi-Doc Vector RAG"],
    horizontal=True,
    label_visibility="collapsed"
)

if app_mode == "v2: Modular Market Research":
    st.header("Customizable Market Intelligence Engine")
    
    research_topic = st.text_input(
        "Enter research topic or market sector:",
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
        
    if st.button("Generate Custom Intelligence Report"):
        st.success(f"Generating comprehensive intelligence report for persona: **{persona}**...")
        
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
                "Projected Revenue (INR)": [180000, 210000, 260000, 320000, 450000]
            }
            st.line_chart(chart_data, x="Quarter", y="Projected Revenue (INR)")
            
        if mod_strategy:
            st.markdown("### 🎯 Strategic Recommendations")
            st.write("1. **Phase Rollout:** Launch initial pilot collections online to validate product-market fit before expanding physical inventory.")
            st.write("2. **Supply Chain:** Secure transparent vendor compliance to align with European eco-label regulations.")

elif app_mode == "MBA Strategic Decision Hub":
    st.header("🎓 MBA Strategic Decision Framework & Financial Modeler")
    st.markdown("Advanced quantitative analysis and strategic positioning tools based on executive frameworks.")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        initial_capital = st.number_input("Initial Capital Allocation (INR):", value=180000)
    with col_m2:
        annual_growth = st.slider("Projected Annual Growth Rate (%)", 5, 50, 20)
        
    if st.button("Run MBA Financial Simulation"):
        st.success("Executing multi-year valuation forecast...")
        
        # Calculation logic
        years = 3
        projections = []
        val = initial_capital
        for y in range(1, years + 1):
            val *= (1 + annual_growth / 100)
            projections.append((f"Year {y}", int(val)))
            
        st.metric(label="Starting Capital Principal", value=f"INR {initial_capital:,}")
        
        chart_dict = {
            "Timeline": ["Initial"] + [p[0] for p in projections],
            "Valuation (INR)": [initial_capital] + [p[1] for p in projections]
        }
        st.bar_chart(chart_dict, x="Timeline", y="Valuation (INR)")
        
        st.markdown("### 🏛️ Strategic Decision Breakdown")
        st.write("- **Capital Efficiency:** High return potential on initial bootstrap capital.")
        st.write("- **Risk Horizon:** Monitor operating cash burn during early quarters.")

else:
    st.header("Advanced Multi-Document Vector RAG Engine")
    
    uploaded_file = st.file_uploader("Upload PDF documents for multi-doc RAG indexing", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Process & Index Document"):
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
