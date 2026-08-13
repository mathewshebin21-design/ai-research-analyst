import streamlit as st
import os

st.set_page_config(page_title="AI Research & Intelligence Platform", layout="wide")

st.title("AI Research & Intelligence Platform")

# Sidebar Controls & Personas
st.sidebar.header("Controls & Configuration")
persona = st.sidebar.selectbox(
    "Select Analyst Persona",
    ["General Market Analyst", "Financial Risk Expert", "Technical Due Diligence Agent", "Startup Strategist"]
)

uploaded_file = st.sidebar.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file is not None:
    if st.sidebar.button("Process & Index Document into Vector Store"):
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
                
                st.sidebar.success("Document indexed successfully!")
            except Exception as e:
                st.sidebar.error(f"Error indexing document: {e}")

# Main Content Layout with Persona Mode
st.markdown(f"**Active Persona:** `{persona}`")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Document Intelligence & Search")
    query = st.text_input("Ask anything about your uploaded document:")

    if query:
        if "vector_store" in st.session_state:
            with st.spinner("Searching document..."):
                docs_found = st.session_state.vector_store.similarity_search(query, k=3)
                st.write("### Search Results:")
                for i, doc in enumerate(docs_found):
                    st.info(f"**Result {i+1}:**\n{doc.page_content}")
        else:
            st.warning("Please upload a PDF and click 'Process & Index Document into Vector Store' in the sidebar first.")

with col2:
    st.subheader("Document Info")
    if uploaded_file is not None:
        st.write(f"**Filename:** {uploaded_file.name}")
        st.download_button(
            label="Download Uploaded PDF",
            data=uploaded_file,
            file_name=uploaded_file.name,
            mime="application/pdf"
        )
    else:
        st.info("No document uploaded yet.")
