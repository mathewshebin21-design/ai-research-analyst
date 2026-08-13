import streamlit as st
import os

st.set_page_config(page_title="AI Research & Intelligence Platform", layout="wide")

st.title("AI Research & Intelligence Platform")

# Sidebar - Expanded Expert Personas & Global Controls
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
st.sidebar.markdown("---")
st.sidebar.info("Use Tab 1 for multi-module market intelligence and Tab 2 for RAG document querying.")

# Create Two Main Tabs
tab1, tab2 = st.tabs(["📊 AI Data Analyzer & Modular Research", "📁 Document RAG & File Viewer"])

with tab1:
    st.header("Modular Market Research & AI Analysis")
    
    # Advanced Analysis Module Selection
    analysis_type = st.radio(
        "Select Advanced Analysis Module:", 
        [
            "SWOT Matrix", 
            "Competitor Landscape", 
            "Financial Projections & Capital Allocation", 
            "Market Entry & Regulatory Risk Assessment",
            "Export/Import Supply Chain Optimization"
        ],
        horizontal=True
    )
    
    st.markdown("---")

    if analysis_type == "SWOT Matrix":
        st.subheader("SWOT Matrix Generator")
        query_input = st.text_input("Enter company, brand, or market topic for SWOT analysis:")
        if st.button("Run Comprehensive SWOT"):
            if query_input:
                st.success(f"Executing SWOT analysis for **{query_input}** under persona **{persona}**...")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("### Strengths")
                    st.write("- Core market positioning\n- Proprietary operational setup")
                    st.markdown("### Opportunities")
                    st.write("- Emerging digital scale\n- Untapped export corridors")
                with col_b:
                    st.markdown("### Weaknesses")
                    st.write("- Initial capital constraints\n- Supply chain dependencies")
                    st.markdown("### Threats")
                    st.write("- Competitive saturation\n- Regulatory fluctuations")
            else:
                st.warning("Please enter a valid topic.")

    elif analysis_type == "Competitor Landscape":
        st.subheader("Competitor Landscape Mapping")
        industry_input = st.text_input("Enter industry niche or sector:")
        if st.button("Generate Competitor Matrix"):
            if industry_input:
                st.success(f"Mapping competitor ecosystem for **{industry_input}**...")
                st.markdown("""
                | Competitor | Market Share | Core Advantage | Strategic Vulnerability |
                | :--- | :--- | :--- | :--- |
                | **Alpha Corp** | 35% | Established distribution | High overhead costs |
                | **Beta Retail** | 22% | Niche product focus | Limited scale capability |
                | **Gamma Tech** | 18% | Disruptive pricing model | Lower brand loyalty |
                """)
            else:
                st.warning("Please provide an industry niche.")

    elif analysis_type == "Financial Projections & Capital Allocation":
        st.subheader("Financial Projections & Capital Allocation")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            capital = st.number_input("Total Capital Allocation (INR):", value=180000)
        with col_f2:
            growth_rate = st.slider("Projected Annual Growth Rate (%)", 5, 50, 15)
            
        if st.button("Calculate Financial Forecasts"):
            st.success("Evaluating capital deployment and cash flow trajectory...")
            st.metric(label="Initial Principal", value=f"INR {capital:,}")
            st.metric(label="Estimated Year 1 Return (at {growth_rate}%)", value=f"INR {int(capital * (1 + growth_rate/100)):,}")

    elif analysis_type == "Market Entry & Regulatory Risk Assessment":
        st.subheader("Market Entry & Regulatory Compliance")
        target_market = st.text_input("Enter target geographic market or business entity type:")
        if st.button("Evaluate Regulatory Risks"):
            if target_market:
                st.info(f"Assessing compliance protocols and entry friction for **{target_market}**...")
                st.write("1. **Entity Registration & Licensing:** Verify mandatory GST/Udyam or regional requirements.")
                st.write("2. **Taxation & Compliance:** Review domestic and international withholding guidelines.")
                st.write("3. **Risk Mitigation:** Implement robust contract structures.")
            else:
                st.warning("Please specify a target market or setup type.")

    else:
        st.subheader("Supply Chain & Export Strategy")
        product_category = st.text_input("Enter product category for trade analysis:")
        if st.button("Analyze Trade & Logistics"):
            if product_category:
                st.info(f"Analyzing export procedures, logistics, and buyer acquisition for **{product_category}**...")
                st.write("- **Logistics Hubs:** Primary freight routing and local fulfillment centers.")
                st.write("- **Documentation:** Importer-Exporter Code (IEC) and shipping manifests.")
            else:
                st.warning("Please enter a product category.")

with tab2:
    st.header("Document RAG & Multi-Document Search")
    
    uploaded_file = st.file_uploader("Upload a PDF document for analysis", type=["pdf"], key="tab2_upload")

    if uploaded_file is not None:
        if st.button("Process & Index Document into Vector Store"):
            with st.spinner("Processing and indexing document..."):
                bytes_data = uploaded_file.read()
                os.makedirs("data", exist_ok=True)
                file_path = os.path.join("data", uploaded_file.name)
                with open(file_path, "wb") as file_out:
                    file_out.write(bytes_data)
                
                try:
                    from langchain_community.document_loaders import PyPDFLoader
                    from langchain_text_splitters import RecursiveCharacterTextSplitter
                    from langchain_community.embeddings import HuggingFaceEmbeddings
                    from langchain_community.vectorstores import FAISS

                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                    splits = text_splitter.split_documents(docs)

                    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                    st.session_state.vector_store = FAISS.from_documents(splits, embeddings)
                    
                    st.success("Document indexed successfully into Vector Store!")
                except Exception as e:
                    st.error(f"Error indexing document: {e}")

    st.subheader("Search Uploaded Documents")
    rag_query = st.text_input("Ask anything about your uploaded document:")

    if rag_query:
        if "vector_store" in st.session_state:
            with st.spinner("Searching document context..."):
                docs_found = st.session_state.vector_store.similarity_search(rag_query, k=3)
                st.write("### Search Results:")
                for i, doc in enumerate(docs_found):
                    st.info(f"**Result {i+1}:**\n{doc.page_content}")
        else:
            st.warning("Please upload a PDF and click 'Process & Index Document into Vector Store' above first.")

    if uploaded_file is not None:
        with st.expander("View Uploaded Document Details"):
            st.write(f"Filename: {uploaded_file.name}")
            st.download_button(
                label="Download Uploaded PDF",
                data=uploaded_file,
                file_name=uploaded_file.name,
                mime="application/pdf"
            )
