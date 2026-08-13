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

    def extract_text_from_pdf(self, uploaded_file) -> str:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    def query_document(self, document_text: str, question: str) -> str:
        prompt = f"""
        You are an expert Document Intelligence Assistant. 
        Answer the user's question accurately using ONLY the provided document context below. If the answer cannot be found in the context, state that clearly.

        <document_context>
        {document_text[:15000]} 
        </document_context>

        User Question: {question}
        """

        response = self.client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
            ),
        )
        return response.text
