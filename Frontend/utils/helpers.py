import streamlit as st
import time

def load_css(file_path: str):
    """Loads custom CSS into the Streamlit app."""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def stream_text(text: str, delay: float = 0.015):
    """Simulates a typewriter effect for AI responses."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(delay)