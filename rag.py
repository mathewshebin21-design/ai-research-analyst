import os
from google import genai

class DocumentRAGEngine:
    def __init__(self):
        self.client = genai.Client()

    def extract_text_from_pdf(self, uploaded_file) -> str:
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text

    def query_document(self, combined_text: str, chat_history: list, user_question: str) -> str:
        history_str = ""
        for msg in chat_history:
            history_str += f"{msg['role']}: {msg['content']}\n"
            
        prompt = f"""You are an expert document analysis assistant. Use the provided document contents and chat history to answer accurately.

Documents Content:
{combined_text}

Chat History:
{history_str}

Current Question: {user_question}
"""
        response = self.client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt
        )
        return response.text
