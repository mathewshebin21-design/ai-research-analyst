import os
import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

class DocumentRAGEngine:
    def __init__(self):
        gemini_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY is missing from secrets.")
        self.client = genai.Client(api_key=gemini_key)
        
        # Optional Supabase setup
        self.supabase = None
        supabase_url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
        
        if supabase_url and supabase_key:
            try:
                from supabase import create_client
                self.supabase = create_client(supabase_url, supabase_key)
            except Exception:
                self.supabase = None

    def extract_text_from_pdf(self, uploaded_file) -> str:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    def store_document_vectors(self, file_name: str, chunks: list[str]):
        if not self.supabase:
            return  # Skip vector db storage if Supabase isn't configured, use local memory
        try:
            self.supabase.table("document_vectors").delete().eq("file_name", file_name).execute()
            records = []
            for index, chunk in enumerate(chunks):
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
            self.supabase.table("document_vectors").insert(records).execute()
        except Exception:
            pass # Fall back safely if network call fails

    def query_document(self, document_text: str, chat_history: list, question: str) -> str:
        formatted_history = ""
        for message in chat_history:
            role = "User" if message["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {message['content']}\n"

        prompt = f"""
        You are an expert Document Intelligence Assistant. 
        Answer the user's question accurately using ONLY the provided document context and conversation history.

        <document_context>
        {document_text[:15000]}
        </document_context>

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
