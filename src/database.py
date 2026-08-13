import os
import json
from supabase import create_client, Client
from src.analysis import StrategicAnalysis

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase credentials not found in environment variables.")
    return create_client(url, key)

def init_db():
    # Cloud tables are managed directly in Supabase Postgres schema
    pass

def save_report(query: str, persona: str, analysis_obj: StrategicAnalysis):
    try:
        supabase = get_supabase_client()
        analysis_json = analysis_obj.model_dump_json()
        supabase.table("reports").insert({
            "query": query,
            "persona": persona,
            "analysis_json": analysis_json
        }).execute()
    except Exception as e:
        print(f"Cloud DB save error (falling back/logging): {e}")

def load_reports():
    try:
        supabase = get_supabase_client()
        response = supabase.table("reports").select("*").order("timestamp", desc=True).execute()
        rows = response.data
        
        history = []
        for row in rows:
            analysis_obj = StrategicAnalysis.model_validate_json(row["analysis_json"])
            history.append({
                "query": row["query"],
                "persona": row["persona"],
                "analysis": analysis_obj,
                "timestamp": row["timestamp"]
            })
        return history
    except Exception as e:
        print(f"Cloud DB load error: {e}")
        return []

def clear_reports():
    try:
        supabase = get_supabase_client()
        supabase.table("reports").delete().neq("id", 0).execute()
    except Exception as e:
        print(f"Cloud DB clear error: {e}")
