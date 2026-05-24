<p align="center">
  <img src="assets/banner.png" alt="Nexus AI RAG Chatbot Banner" width="100%" />
</p>

<h1 align="center">🧠 Nexus AI — Enterprise RAG Chatbot (FAISS + LangChain)</h1>

<p align="center">
  <a href="https://github.com/abubakarshahid16/Rag-chatbot/stargazers"><img src="https://img.shields.io/github/stars/abubakarshahid16/Rag-chatbot?style=for-the-badge&color=ffd700" alt="GitHub Stars"></a>
  <a href="https://github.com/abubakarshahid16/Rag-chatbot/network/members"><img src="https://img.shields.io/github/forks/abubakarshahid16/Rag-chatbot?style=for-the-badge&color=8a2be2" alt="GitHub Forks"></a>
  <a href="https://github.com/abubakarshahid16/Rag-chatbot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/abubakarshahid16/Rag-chatbot?style=for-the-badge&color=brightgreen" alt="MIT License"></a>
  <br>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue?style=for-the-badge&logo=python" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B?style=for-the-badge&logo=streamlit" alt="Streamlit">
</p>

<p align="center">
  <strong>The ultimate open-source Enterprise Retrieval-Augmented Generation (RAG) chatbot pipeline.</strong> Upload documents, index them into a secure local vector store, and perform conversations with full source citations using LangChain, FAISS, and dynamic LLM configurations.
</p>

---

## 📺 Video Demo & Walkthrough

We have included a full setup and feature walkthrough video inside this repository.

*   **Local Video File**: Located at [assets/rag_chatbot.mp4](assets/rag_chatbot.mp4) (gitignored locally to prevent size bloat).
*   **YouTube Demo Video**: [Watch the Walkthrough Demo on YouTube](https://www.youtube.com) *(Insert your uploaded YouTube link here)*.
*   **Interactive Streamlit UI Demo**: Upload documents $\rightarrow$ Ask questions $\rightarrow$ Review sources badges!

---

## 🖥️ User Interface Preview

Here is a preview of the interactive Streamlit user interface where you can upload your knowledge base and query it in real-time:

<p align="center">
  <img src="assets/screenshot.png" alt="Nexus AI Chatbot Interface Preview" width="90%" />
</p>

---


## ⚡ Core Features

-   **📁 Multi-Format Document Ingestion**: Upload and process `.pdf`, `.docx`, and `.txt` files on the fly.
-   **⚡ Local Vector Indexing**: Auto-chunking (`RecursiveCharacterTextSplitter`) and vector storage utilizing **FAISS** with local **HuggingFace** embeddings (`all-MiniLM-L6-v2`)—no embedding API key required!
-   **💬 Conversational History-Aware Retrieval**: Reformulates multi-turn conversation questions into standalone queries for highly accurate context retrieval.
-   **⚙️ Dynamic LLM Provider Hot-Swapping**: Switch models in real-time in the UI:
    -   **Groq** (Llama 3/3.3, Gemma 2, Mixtral)
    -   **OpenAI** (GPT-4o, GPT-4o-mini, GPT-3.5)
    -   **Anthropic** (Claude 3.5 Sonnet/Haiku, Claude 3 Opus)
    -   **Together AI** (Open-source instruction models)
    -   **Hugging Face Hub** (Inference APIs)
    -   **Ollama** (Completely local/offline LLM pipelines)
-   **🔍 Context Citation Badges**: The UI marks answers with direct citations, listing exactly which documents were used to build the answer.
-   **🗑️ Database Reset System**: Easily clean up and start fresh with a single click.

---

## 🏗️ System Architecture

```
                    ┌────────────────────────┐
                    │  User Documents        │
                    │  (PDF, DOCX, TXT)      │
                    └───────────┬────────────┘
                                │ (Upload API)
                                ▼
         ┌─────────────────────────────────────────────┐
         │ FastAPI Backend (main.py)                   │
         │  1. Chunking: RecursiveCharacterTextSplitter │
         │  2. Embedding: HuggingFace (all-MiniLM-L6-v2)│
         └──────────────────────┬──────────────────────┘
                                │ (Persist Index)
                                ▼
                      ┌───────────────────┐
                      │ FAISS Vector DB   │
                      │ (Local Directory) │
                      └─────────┬─────────┘
                                │ (Retrieve Top 5 Chunks)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ LangChain Conversational Retrieval Chain                    │
 │  1. History-Aware Contextualizing Chain                     │
 │  2. LLM Selection (Groq, OpenAI, Claude, Ollama, Together)  │
 └──────────────────────────────┬──────────────────────────────┘
                                │ (Formatted Answer + Citations)
                                ▼
                     ┌─────────────────────┐
                     │ Streamlit UI        │
                     │ (app.py Dashboard)  │
                     └─────────────────────┘
```

---

## 🚀 Setup & Installation Instructions

Follow these steps to run the RAG Chatbot on your local machine.

### 1. Prerequisites
-   Python 3.9 or higher installed on your system.
-   API Keys for your preferred LLM provider (e.g., Groq API key, OpenAI API key, Anthropic API key).

### 2. Clone the Repository
```bash
git clone https://github.com/abubakarshahid16/Rag-chatbot.git
cd Rag-chatbot
```

### 3. Configure Environment Variables
Create a file named `.env` in the `Backend/` directory and populate it with your keys:
```bash
# Backend/.env
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=sk_your_openai_api_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here
TOGETHER_API_KEY=your_together_api_key_here
HUGGINGFACEHUB_API_TOKEN=hf_your_token_here
OLLAMA_BASE_URL=http://localhost:11434
```

### 4. Setup & Start Backend Server
Open a terminal window and run:
```bash
cd Backend
python -m venv venv

# Activate Virtual Environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Start Server (Uvicorn)
uvicorn main:app --reload --port 8000
```
The FastAPI API documentation will be available at: http://localhost:8000/docs

### 5. Setup & Start Streamlit Frontend UI
Open a second terminal window and run:
```bash
cd Frontend
python -m venv venv

# Activate Virtual Environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Start Streamlit App
streamlit run app.py
```
Open your browser to http://localhost:8501 to use the dashboard!

---

## 🌐 Deployment Guide

This project can be deployed easily to the cloud using the following setups.

### Option 1: Hugging Face Spaces (One-Click, Docker-based, Free)
We have included a root-level [Dockerfile](Dockerfile) that runs both the FastAPI backend and the Streamlit frontend concurrently in the same container.
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces).
2. Choose **Docker** as the SDK and select **Blank** template.
3. Push this repository's code to your Hugging Face Space remote.
4. Hugging Face will automatically build and run the Docker container. Your app will be live instantly!

### Option 2: Separate UI & API (Streamlit Cloud + Render)
1. **Backend**: Deploy the `Backend/` directory to [Render](https://render.com) or [Railway](https://railway.app) as a Python Web Service. Set the startup command to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
2. **Frontend**: Deploy to [Streamlit Community Cloud](https://streamlit.io/cloud) by connecting your GitHub repo and selecting `Frontend/app.py` as the entrypoint.
3. **Link them**: In your Streamlit Cloud Advanced Settings, add the environment variable `API_URL` and set it to your backend service's URL (e.g., `https://your-backend.onrender.com`).

---

## 📽️ Hosting the 185 MB Demo Video

Since your walkthrough video `rag_chatbot.mp4` is larger than the 100 MB GitHub limit, follow this developer trick to embed it directly in your README:
1. Go to your repository on GitHub.
2. Click on **Releases** on the right side and click **Create a new release**.
3. Create a draft release tag (e.g., `v1.0.0-assets`).
4. Drag and drop `assets/rag_chatbot.mp4` into the release binaries box (GitHub supports files up to 2GB in releases).
5. Once uploaded, publish the release, right-click on the download link for the video, and copy the link address.
6. Replace the placeholder video link in [README.md](README.md) with your copied direct download URL:
   ```html
   <video src="https://github.com/abubakarshahid16/Rag-chatbot/releases/download/v1.0.0-assets/rag_chatbot.mp4" width="100%" controls></video>
   ```

---


## 📡 API Endpoints Reference

The backend API exposes the following REST endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Verify if the API is active and running. |
| `GET` | `/documents` | Fetch a dictionary of all indexed documents and their chunk counts. |
| `POST` | `/upload` | Upload a document, chunk it, embed it, and add it to the FAISS index. |
| `POST` | `/chat` | Submit a prompt with conversational history and model configurations. |
| `POST` | `/reset` | Purge the FAISS vector database and clear indexed file metadata. |

---

## 🧠 Answer Engine Optimization (AEO) & AI Discovery (GEO)

This repository is optimized for **AEO (Answer Engine Optimization)** and **GEO (Generative Engine Optimization)**. It features:
*   [llms.txt](llms.txt): A structured high-level summary optimized for search crawlers like GPTBot, ClaudeBot, and Perplexity.
*   [llms-full.txt](llms-full.txt): Detailed developer schemas and API specs designed to feed LLM context windows, helping AI systems write accurate implementations for users.
*   Structured documentation hierarchy (`H1` to `H4` headers) mapped to high-volume user search queries.

---

## ❓ FAQ & Troubleshooting

### Q: Why do I get a "Dangerous Deserialization" error?
**A**: When loading FAISS indexes from disk, LangChain enables strict checks. The RAG service sets `allow_dangerous_deserialization=True` because the files are generated and loaded locally in your workspace. Ensure you do not load untrusted FAISS indices from other sources.

### Q: Can I run this offline?
**A**: Yes! Select **Ollama** as the provider and ensure you have Ollama running locally (e.g. `ollama run llama3`). The HuggingFace embedding model (`all-MiniLM-L6-v2`) downloads automatically and runs entirely locally.

### Q: How do I change the chunk sizes?
**A**: You can customize chunking settings directly in [Backend/rag_service.py](Backend/rag_service.py) under the `process_document` method by tweaking the `chunk_size` and `chunk_overlap` variables.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
