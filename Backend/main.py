import os
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv

# Explicit import of the RAG class
from rag_service import RAGService

load_dotenv()

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

# Explicit instantiation of the service
rag_service = RAGService()

# Resolve directories relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent  
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


class ChatRequest(BaseModel):
    question: str
    chat_history: list = []  # Completely flexible list
    config: dict = None      # Added support for your advanced config payload!


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/documents")
def get_documents():
    """Returns the dictionary of currently indexed documents and chunk counts."""
    try:
        return {"documents": rag_service.get_indexed_documents()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_knowledge_base():
    """Resets the vector index and deletes the persisted metadata."""
    try:
        rag_service.reset_index()
        return {"message": "Knowledge base reset successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}."
        )

    file_path = UPLOADS_DIR / file.filename

    try:
        # Save uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks = rag_service.process_document(str(file_path), file.filename)

        return {
            "message": f"Successfully processed '{file.filename}' into {chunks} chunks.",
            "filename": file.filename,
            "chunks": chunks,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always clean up the temp file
        if file_path.exists():
            os.remove(file_path)


@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Pass question, history, and config payload to your advanced rag_service!
        result = rag_service.ask_question(
            request.question, 
            request.chat_history, 
            request.config
        )
        return result  # Returns {"answer": ..., "sources": ...}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))