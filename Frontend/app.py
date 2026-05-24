import streamlit as st
from components.sidebar import render_sidebar
from components.chat import render_empty_state, render_chat_history
from services.api import chat_with_backend, get_indexed_documents
from utils.helpers import load_css, stream_text

# 1. Page Configuration (Must be first)
st.set_page_config(
    page_title="RAG Chatbot | Enterprise RAG (FAISS + LangChain)",

    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_filenames" not in st.session_state:
    st.session_state.uploaded_filenames = []
if "active_prompt" not in st.session_state:
    st.session_state.active_prompt = None

# Model Configuration States
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "Groq"
if "llm_model" not in st.session_state:
    st.session_state.llm_model = "llama-3.1-8b-instant"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.0

# 3. Synchronize Indexed Files with Backend Database
try:
    backend_docs = get_indexed_documents()
    if isinstance(backend_docs, dict) and "error" not in backend_docs:
        st.session_state.uploaded_filenames = list(backend_docs.keys())
except Exception as e:
    st.sidebar.error(f"Backend Sync Failed: {e}")

# 4. Load UI Enhancements
load_css("assets/styles.css")

# 5. Mount Sidebar
render_sidebar()

# 6. Mount Main Chat Area
if not st.session_state.messages:
    render_empty_state()
else:
    render_chat_history()

# 7. Chat Input Logic
user_input = st.chat_input("Ask anything about your documents...") 
prompt = user_input or st.session_state.active_prompt

if prompt:
    # Reset active prompt if it was triggered by a suggested prompt button
    st.session_state.active_prompt = None
    
    # Render user message instantly
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exclude the current prompt from history payload to avoid duplicates
    history_payload = st.session_state.messages[:-1]
    
    # Resolve Model Config Payload
    provider_key = st.session_state.llm_provider.lower().replace(" ", "")
    
    config_payload = {
        "provider": provider_key,
        "model": st.session_state.llm_model,
        "temperature": st.session_state.temperature
    }
    
    # Call backend and render AI response
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Analyzing knowledge base..."):
            response = chat_with_backend(prompt, history_payload, config_payload)

        if "error" in response:

            st.error(response["error"])
        else:
            answer = response.get("answer", "No response generated.")
            sources = response.get("sources", [])
            
            # Typewriter text effect
            st.write_stream(stream_text(answer))
            
            # Render sources inline under the response
            if sources:
                sources_html = (
                    "<div class='sources-container'>"
                    "<span class='sources-label'>Retrieved Sources:</span> " +
                    " ".join([f"<span class='source-badge'>📄 {src}</span>" for src in sources]) +
                    "</div>"
                )
                st.markdown(sources_html, unsafe_allow_html=True)
                
            # Store assistant response with sources
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })
            st.rerun()