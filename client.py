import os
import streamlit as st
import openai

CURRENT_MODEL = "gpt-4o-mini"

def get_openai_client():
    try:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", None)
        except Exception:
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key not found. Put it in .streamlit/secrets.toml or environment.")
            return None
        return openai.OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {e}")
        return None
