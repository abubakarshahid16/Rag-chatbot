import requests
import streamlit as st

# Point this to your existing FastAPI backend
API_URL = "http://127.0.0.1:8000"

def upload_file_to_backend(file):
    """Sends a single file to the FastAPI backend."""
    files = {"file": (file.name, file.getvalue(), file.type)}
    try:
        response = requests.post(f"{API_URL}/upload", files=files, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection failed: {str(e)}"}

def chat_with_backend(question: str, history: list, config: dict = None):

    """Sends question, context history, and model config to FastAPI backend with active debugging."""

    
    # Clean history defensively to only send text fields
    cleaned_history = []
    for msg in history:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            cleaned_history.append({
                "role": str(msg["role"]),
                "content": str(msg["content"])
            })

    payload = {
        "question": question,
        "chat_history": cleaned_history,
        "config": config,
    }

    
    # 🔍 FRONTEND PAYLOAD DEBUGGER
    print("\n" + "="*50)
    print("🤖 [FRONTEND API DEBUG] SENDING PAYLOAD:")
    print(payload)
    print("="*50 + "\n")
    
    try:
        response = requests.post(f"{API_URL}/chat", json=payload, timeout=60)
        
        # 🔍 FRONTEND 422 ERROR LOGGER
        if response.status_code == 422:
            print("\n" + "❌"*10)
            print("❌ [FRONTEND API DEBUG] FASTAPI REJECTED VALIDATION (422):")
            print(response.json())
            print("❌"*10 + "\n")
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API Error: {str(e)}"}

def reset_backend_index():
    """Requests the FastAPI backend to delete the FAISS index."""
    try:
        response = requests.post(f"{API_URL}/reset", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to reset database: {str(e)}"}

def get_indexed_documents():
    """Fetches the list of currently indexed documents from the backend."""
    try:
        response = requests.get(f"{API_URL}/documents", timeout=10)
        response.raise_for_status()
        res = response.json()
        
        # Flexibly handle both list and dict outputs from backend
        if isinstance(res, list):
            return res
        elif isinstance(res, dict) and "documents" in res:
            return res["documents"]
        return []
    except Exception:
        return []