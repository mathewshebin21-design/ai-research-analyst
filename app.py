import streamlit as st
import os

st.set_page_config(page_title="AI Research & Intelligence Platform", layout="wide")

st.title("AI Research & Intelligence Platform")

# Create Two Main Tabs
tab1, tab2 = st.tabs(["📊 AI Data Analyzer & Modular Research", "📁 Document RAG & File Viewer"])

with tab1:
    st.header("Modular Market Research & AI Analysis")
    
    # Sidebar Controls & Personas specific to Tab 1 / General workspace
    persona = st.selectbox(
        "Select Analyst Persona",
        ["General Market Analyst", "Financial Risk Expert", "Technical Due Diligence Agent", "Startup Strategist"],
        key="persona_select"
    )
    
    st.markdown(f"**Active Executive Persona:** `{persona}`")
    
    # Modular Market Analysis Section
    analysis_type = st.radio("Select Analysis Module:", ["SWOT Matrix", "Competitor Landscape", "Financial Projections & Capital Allocation"])
    
    if analysis_type == "SWOT Matrix":
        st.subheader("SWOT Matrix Generator")
        query_input = st.text_input("Enter company or market topic for SWOT analysis:")
        if st.button("Run SWOT Analysis"):
            st.info(f"Generating comprehensive SWOT framework for: {query_input} under persona {persona}...")
            # Placeholder for SWOT logic
    elif analysis_type == "Competitor Landscape":
        st.subheader("Competitor Landscape Mapping")
        st.text_input("Enter industry niche:")
        if st.button("Analyze Competitors"):
            st.success("Analyzing top market competitors...")
    else:
        st.subheader("Financial Projections & Capital Allocation")
        st.number_input("Capital amount (INR):", value=180000)
        if st.button("Calculate Projections"):
            st.success("Evaluating financial allocation strategy...")

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
                    
                    st.success("Document indexed successfully!")
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
