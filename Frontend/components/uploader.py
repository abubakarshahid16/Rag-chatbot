import streamlit as st
from services.api import upload_file_to_backend

def render_uploader():
    """Renders the drag-and-drop uploader in the sidebar."""
    uploaded_files = st.file_uploader(
        "Upload context documents", 
        type=['pdf', 'docx', 'txt'], 
        accept_multiple_files=True, 
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        if st.button("Process Documents", use_container_width=True, type="primary"):
            new_files_added = False
            
            with st.status("Indexing documents...", expanded=True) as status:
                for file in uploaded_files:
                    if file.name not in st.session_state.uploaded_filenames:
                        st.write(f"Analyzing `{file.name}`...")
                        res = upload_file_to_backend(file)
                        
                        if "error" in res:
                            status.update(label=f"Failed to process {file.name}", state="error")
                            st.error(res["error"])
                            return
                        else:
                            st.session_state.uploaded_filenames.append(file.name)
                            new_files_added = True
                
                status.update(label="Knowledge base updated!", state="complete", expanded=False)
            
            # 🧹 AUTO-CLEAR LOGIC: If a new file was successfully added to the knowledge base,
            # we wipe the chat history to prevent context contamination from older files.
            if new_files_added:
                st.session_state.messages = [] 
                st.toast("New files indexed! Chat cleared to prevent context confusion. 🧹", icon="🧠")
                st.rerun()