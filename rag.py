import os
import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader
from supabase import create_client, Client

class DocumentRAGEngine:
    def __init__(self):
        gemini_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        supabase_url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

        if not gemini_key:
            raise ValueError("GEMINI_API_KEY is missing from secrets.")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing from secrets.")

        self.client = genai.Client(api_key=gemini_key)
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def extract_and_chunk_pdf(self, uploaded_file, chunk_size=1000, overlap=100) -> list[str]:
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                full_text += extracted + "\n"

        chunks = []
        start = 0
        while start < len(full_text):
            end = start + chunk_size
            chunks.append(full_text[start:end])
            start += (chunk_size - overlap)
        return chunks

    def store_document_vectors(self, file_name: str, chunks: list[str]):
        # Delete old vectors for this file if re-uploaded
        self.supabase.table("document_vectors").delete().eq("file_name", file_name).execute()

        records = []
        for index, chunk in enumerate(chunks):
            # Generate vector embedding for chunk using Gemini
            emb_res = self.client.models.embed_content(
                model="text-embedding-004",
                contents=chunk
            )
            embedding_vector = emb_res.embeddings[0].values

            records.append({
                "file_name": file_name,
                "chunk_index": index,
                "content": chunk,
                "embedding": embedding_vector
            })

        # Insert batch into Supabase
        self.supabase.table("document_vectors").insert(records).execute()

    def query_document(self, file_name: str, chat_history: list, question: str) -> str:
        # 1. Embed current query
        q_emb_res = self.client.models.embed_content(
            model="text-embedding-004",
            contents=question
        )
        query_vector = q_emb_res.embeddings[0].values

        # 2. Vector search in Supabase using match_document_vectors function
        search_res = self.supabase.rpc(
            "match_document_vectors",
            {
                "query_embedding": query_vector,
                "match_threshold": 0.2,
                "match_count": 5,
                "filter_file_name": file_name
            }
        ).execute()

        retrieved_chunks = [item["content"] for item in search_res.data] if search_res.data else []
        retrieved_context = "\n---\n".join(retrieved_chunks)

        # 3. Format chat history
        formatted_history = ""
        for message in chat_history:
            role = "User" if message["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {message['content']}\n"

        prompt = f"""
        You are an expert Document Intelligence Assistant. 
        Answer the user's question accurately using ONLY the vector-retrieved context chunks and conversation history below.

        <retrieved_context>
        {retrieved_context if retrieved_context else "No relevant context found in vector storage."}
        </retrieved_context>

        <conversation_history>
        {formatted_history}
        </conversation_history>

        Current User Question: {question}
        """

        response = self.client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
            ),
        )
        return response.text
