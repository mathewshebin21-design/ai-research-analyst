# auth.py
import streamlit as st
from supabase import create_client

def get_supabase_client():
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")
    return create_client(url, key)

def login_form():
    st.subheader("🔒 Secure Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            supabase = get_supabase_client()
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = user.user
            st.rerun()
        except Exception:
            st.error("Login failed. Please check your credentials.")