import sqlite3
from src.analysis import StrategicAnalysis

DB_NAME = "reports.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            persona TEXT,
            analysis_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_report(query: str, persona: str, analysis_obj: StrategicAnalysis):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    analysis_json = analysis_obj.model_dump_json()
    cursor.execute(
        "INSERT INTO reports (query, persona, analysis_json) VALUES (?, ?, ?)",
        (query, persona, analysis_json)
    )
    conn.commit()
    conn.close()

def load_reports():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, query, persona, analysis_json, timestamp FROM reports ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # Reconstruct history items with parsed Pydantic objects
    history = []
    for row in rows:
        report_id, query, persona, analysis_json, timestamp = row
        analysis_obj = StrategicAnalysis.model_validate_json(analysis_json)
        history.append({
            "query": query,
            "persona": persona,
            "analysis": analysis_obj,
            "timestamp": timestamp
        })
    return history

def clear_reports():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports")
    conn.commit()
    conn.close()