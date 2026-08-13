import os
import streamlit as st
from supabase import create_client, Client

class HistoryDatabase:
    def __init__(self):
        url = (
            st.secrets.get("SUPABASE_URL") or 
            os.environ.get("SUPABASE_URL")
        )
        key = (
            st.secrets.get("SUPABASE_KEY") or 
            st.secrets.get("SUPABASE_ANON_KEY") or 
            os.environ.get("SUPABASE_KEY")
        )
        
        if not url or not key:
            raise ValueError("Supabase URL or Key not found in Streamlit secrets or environment variables.")
        
        self.supabase: Client = create_client(url, key)

    def save_report(self, query: str, persona: str, report_dict: dict):
        try:
            self.supabase.table("history").insert({
                "query": query,
                "persona": persona,
                "report": report_dict
            }).execute()
        except Exception as e:
            print(f"Error saving to Supabase: {e}")

    def get_history(self):
        try:
            response = self.supabase.table("history").select("*").order("id", desc=True).execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching from Supabase: {e}")
            return []

    def load_history(self):
        return self.get_history()
