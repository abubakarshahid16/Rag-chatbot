import streamlit as st

def render_empty_state():
    """Displays a welcome screen when chat history is empty."""
    st.markdown("""
        <div style='text-align: center; margin-top: 8vh; margin-bottom: 5vh;'>
            <h1 style='font-size: 2.5rem; font-weight: 600;'>How can I help you today?</h1>
            <p style='color: #94A3B8; font-size: 1.1rem;'>Upload documents in the sidebar, then ask me anything.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Suggested Prompts Row
    cols = st.columns(3)
    prompts = [
        "Summarize the main points of the uploaded document.",
        "What are the key technical skills listed?",
        "Extract actionable insights from this text."
    ]
    
    for i, col in enumerate(cols):
        if col.button(prompts[i], use_container_width=True):
            st.session_state.active_prompt = prompts[i]
            st.rerun()

def render_chat_history():
    """Loops through and displays previous messages with source attribution badges."""
    for msg in st.session_state.messages:
        avatar = "✨" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            
            # Render source attribution badges for AI responses
            if msg["role"] == "assistant" and msg.get("sources"):
                sources_html = (
                    "<div class='sources-container'>"
                    "<span class='sources-label'>Retrieved Sources:</span> " +
                    " ".join([f"<span class='source-badge'>📄 {src}</span>" for src in msg["sources"]]) +
                    "</div>"
                )
                st.markdown(sources_html, unsafe_allow_html=True)