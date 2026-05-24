import streamlit as st
from components.uploader import render_uploader
from services.api import reset_backend_index

def render_sidebar():
    """Renders the left navigation sidebar with database control and LLM settings."""
    with st.sidebar:
        # App Branding
        st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🧠 Nexus AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8; margin-top: 0;'>Enterprise RAG Assistant</p>", unsafe_allow_html=True)
        
        st.write("")
        
        # New Chat Button
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        st.divider()
        
        # Upload Section
        st.markdown("#### 📁 Knowledge Base")
        render_uploader()
        
        # Display Indexed Files & Reset Button
        if st.session_state.uploaded_filenames:
            st.markdown("<p style='font-size: 0.9rem; color: #94A3B8; margin-top: 10px; margin-bottom: 5px;'>Active Documents:</p>", unsafe_allow_html=True)
            for f_name in st.session_state.uploaded_filenames:
                st.markdown(f"📄 `{f_name}`")
            
            st.write("")
            # 🗑️ RESET BUTTON: Deletes database completely
            if st.button("🗑️ Reset Knowledge Base", use_container_width=True, type="secondary"):
                with st.spinner("Deleting database..."):
                    res = reset_backend_index()
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.session_state.uploaded_filenames = []
                        st.session_state.messages = []
                        st.toast("Knowledge base deleted successfully! 🧹", icon="🗑️")
                        st.rerun()
        else:
            st.info("No documents uploaded yet.", icon="ℹ️")

        st.divider()
        
        # LLM Configurations Section
        st.markdown("#### ⚙️ Model Settings")
        
        # Provider Selector
        providers = ["Groq", "OpenAI", "Anthropic", "Together AI", "Hugging Face", "Ollama"]
        default_provider_idx = providers.index(st.session_state.llm_provider) if st.session_state.llm_provider in providers else 0
        provider = st.selectbox("LLM Provider", providers, index=default_provider_idx)
        st.session_state.llm_provider = provider
        
        # Models Map
        models_map = {
            "Groq": [
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "gemma2-9b-it",
                "mixtral-8x7b-32768"
            ],
            "OpenAI": [
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-3.5-turbo"
            ],
            "Anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229"
            ],
            "Together AI": [
                "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "mistralai/Mixtral-8x7B-Instruct-v0.1"
            ],
            "Hugging Face": [
                "meta-llama/Meta-Llama-3-8B-Instruct",
                "mistralai/Mistral-7B-Instruct-v0.2",
                "microsoft/Phi-3-mini-4k-instruct"
            ],
            "Ollama": [
                "llama3",
                "mistral",
                "phi3",
                "gemma2"
            ]
        }
        
        # Model Selection
        model_options = models_map.get(provider, ["llama-3.1-8b-instant"])
        current_model = st.session_state.llm_model
        default_model_idx = 0
        if current_model in model_options:
            default_model_idx = model_options.index(current_model)
            
        selected_model = st.selectbox("Model Name", model_options + ["Custom Model..."], index=default_model_idx)
        
        if selected_model == "Custom Model...":
            custom_model = st.text_input("Enter Custom Model ID", value=current_model if current_model not in model_options else "")
            st.session_state.llm_model = custom_model
        else:
            st.session_state.llm_model = selected_model
            
        # Temperature Slider
        temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=st.session_state.temperature, step=0.1)
        st.session_state.temperature = temp
        st.divider()
        
        # System Status Dashboard
        st.markdown("#### ⚙️ System Status")
        
        doc_count = len(st.session_state.uploaded_filenames)
        st.markdown("🟢 **API Status**: Connected")
        st.markdown(f"🧠 **Model**: `{st.session_state.llm_model}`")
        st.markdown(f"📁 **Indexed Files**: `{doc_count}` active")