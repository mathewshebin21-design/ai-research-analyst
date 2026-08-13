import streamlit as st

st.title("AI Research & Intelligence Platform")

st.sidebar.header("Controls")
uploaded_file = st.sidebar.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file is not None:
    if st.sidebar.button("Process & Index Document into Vector Store"):
        with st.spinner("Processing document..."):
            bytes_data = uploaded_file.read()
            with open("temp.pdf", "wb") as file_out:
                file_out.write(bytes_data)
            st.sidebar.success("Document indexed successfully!")

st.subheader("Document Intelligence & Search")
query = st.text_input("Ask anything about your uploaded document:")

if query:
    if "vector_store" in st.session_state:
        with st.spinner("Searching document..."):
            results = st.session_state.vector_store.similarity_search(query)
            st.write("### Results:")
            for res in results:
                st.write(res.page_content)
    else:
        st.warning("Please upload and click 'Process & Index Document into Vector Store' in the sidebar first.")

if uploaded_file is not None:
    with st.expander("View Uploaded Document Details"):
        st.write(f"Filename: {uploaded_file.name}")
        st.download_button(
            label="Download Uploaded PDF",
            data=uploaded_file,
            file_name=uploaded_file.name,
            mime="application/pdf"
        )
