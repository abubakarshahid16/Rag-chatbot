import os
import json
import shutil
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Resolve persisted FAISS index relative to this file
FAISS_INDEX_PATH = Path(__file__).resolve().parent / "faiss_index"


class RAGService:
    def __init__(self):
        # Embeddings loaded locally (free, fast, no API key needed)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None
        self.load_index()

    def load_index(self):
        """Loads the FAISS index from disk if it exists."""
        if FAISS_INDEX_PATH.exists():
            try:
                self.vectorstore = FAISS.load_local(
                    str(FAISS_INDEX_PATH),
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
            except Exception as e:
                print(f"Error loading FAISS index: {e}")
                self.vectorstore = None

    def reset_index(self):
        """Clears the in-memory vectorstore and deletes the persisted index on disk."""
        self.vectorstore = None
        if FAISS_INDEX_PATH.exists():
            shutil.rmtree(str(FAISS_INDEX_PATH))

    def get_indexed_documents(self) -> dict:
        """Returns a dictionary of filenames to their chunk counts currently indexed."""
        metadata_path = FAISS_INDEX_PATH / "indexed_files.json"
        if not FAISS_INDEX_PATH.exists() or not metadata_path.exists():
            return {}
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading indexed files metadata: {e}")
            return {}

    def _save_indexed_document(self, filename: str, chunk_count: int):
        """Saves a processed document metadata to disk."""
        FAISS_INDEX_PATH.mkdir(parents=True, exist_ok=True)
        metadata_path = FAISS_INDEX_PATH / "indexed_files.json"
        docs = self.get_indexed_documents()
        docs[filename] = chunk_count
        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(docs, f, indent=4)
        except Exception as e:
            print(f"Error saving indexed files metadata: {e}")

    def _get_llm(self, provider: str, model: str, temperature: float):
        """Dynamically instantiates and returns the selected LLM wrapper."""
        provider = provider.lower()
        
        if provider == "groq":
            key = os.getenv("GROQ_API_KEY")
            if not key:
                raise ValueError("Groq API Key (GROQ_API_KEY) is not set in backend environment.")
            return ChatGroq(temperature=temperature, model_name=model, groq_api_key=key)

        elif provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                raise ImportError(
                    "The 'langchain-openai' package is required for OpenAI models. "
                    "Please install it in the environment using: pip install langchain-openai"
                )
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("OpenAI API Key (OPENAI_API_KEY) is not set in backend environment.")
            return ChatOpenAI(temperature=temperature, model_name=model, api_key=key)

        elif provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
            except ImportError:
                raise ImportError(
                    "The 'langchain-anthropic' package is required for Anthropic models. "
                    "Please install it in the environment using: pip install langchain-anthropic"
                )
            key = os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise ValueError("Anthropic API Key (ANTHROPIC_API_KEY) is not set in backend environment.")
            return ChatAnthropic(temperature=temperature, model_name=model, api_key=key)

        elif provider == "together":
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                raise ImportError(
                    "The 'langchain-openai' package is required for Together AI. "
                    "Please install it in the environment using: pip install langchain-openai"
                )
            key = os.getenv("TOGETHER_API_KEY")
            if not key:
                raise ValueError("Together API Key (TOGETHER_API_KEY) is not set in backend environment.")
            return ChatOpenAI(
                temperature=temperature,
                model_name=model,
                api_key=key,
                base_url="https://api.together.xyz/v1"
            )

        elif provider == "huggingface":
            try:
                from langchain_huggingface import HuggingFaceEndpoint
            except ImportError:
                raise ImportError(
                    "The 'langchain-huggingface' package is required for Hugging Face models."
                )
            key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            if not key:
                raise ValueError("Hugging Face API Token (HUGGINGFACEHUB_API_TOKEN) is not set in backend environment.")
            return HuggingFaceEndpoint(
                repo_id=model,
                temperature=max(0.01, temperature),
                huggingfacehub_api_token=key
            )

        elif provider == "ollama":
            try:
                from langchain_community.chat_models import ChatOllama
            except ImportError:
                raise ImportError(
                    "The 'langchain-community' package is required for Ollama models."
                )
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return ChatOllama(temperature=temperature, model=model, base_url=base_url)

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def process_document(self, file_path: str, filename: str) -> int:
        ext = filename.rsplit(".", 1)[-1].lower()
        loader_map = {
            "pdf": PyPDFLoader,
            "docx": Docx2txtLoader,
            "txt": TextLoader,
        }
        if ext not in loader_map:
            raise ValueError(f"Unsupported file type: .{ext}")

        documents = loader_map[ext](file_path).load()
        splits = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        ).split_documents(documents)

        # Build or append FAISS index
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        else:
            self.vectorstore.add_documents(splits)

        self.vectorstore.save_local(str(FAISS_INDEX_PATH))
        self._save_indexed_document(filename, len(splits))
        return len(splits)

    def ask_question(self, question: str, history: list, config: dict = None) -> dict:
        if self.vectorstore is None:
            return {
                "answer": "No documents have been uploaded yet. Please upload a document in the sidebar first.",
                "sources": []
            }

        # Resolve model settings
        config = config or {}
        provider = config.get("provider", "groq")
        model = config.get("model", "llama-3.1-8b-instant")
        temperature = float(config.get("temperature", 0.0))

        try:
            llm = self._get_llm(provider, model, temperature)
        except Exception as e:
            return {
                "answer": f"⚠️ Configuration Error: {str(e)}",
                "sources": []
            }

        # Dynamically build historical chains with stable k=5
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Given a chat history and the latest user question which might reference "
             "context in the chat history, formulate a standalone question that can be "
             "understood without the chat history. Do NOT answer — just reformulate if "
             "needed, otherwise return it as is."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        # 🚀 1. SAFE DOCUMENT CHUNK TEMPLATE
        # This tags every chunk with its actual source file filepath so the LLM can identify it.
        document_prompt = PromptTemplate(
            input_variables=["page_content", "source"],
            template="Document Source Path: {source}\nContent:\n{page_content}\n"
        )

        # 🚀 2. UPDATED SYSTEM PROMPT
        # We explicitly tell the LLM to group chunks from the same file together.
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a helpful assistant for question-answering tasks.\n\n"
             "The retrieved context contains information from one or more uploaded documents. "
             "Each chunk is labeled with 'Document Source Path: [filepath]'. Use this filepath to know which document the text belongs to.\n"
             "If you see different file names in the filepaths, summarize/address each file individually. "
             "If multiple chunks belong to the same file path, group them together as a single document summary. Do not split them into multiple documents.\n\n"
             "Retrieved Context:\n{context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # 🚀 3. INJECT THE DOCUMENT PROMPT
        question_answer_chain = create_stuff_documents_chain(
            llm=llm, 
            prompt=qa_prompt,
            document_prompt=document_prompt # Safely inject file names!
        )
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        # Format memory
        formatted_history = [
            HumanMessage(content=m["content"]) if m["role"] == "user"
            else AIMessage(content=m["content"])
            for m in history
        ]

        # Extract source filenames from retrieval
        sources = []
        try:
            retrieved_docs = retriever.get_relevant_documents(question)
            for doc in retrieved_docs:
                src = doc.metadata.get('source', '')
                if src:
                    name = os.path.basename(src)
                    if name not in sources:
                        sources.append(name)
            
            # Print console debug details
            print("\n" + "="*50)
            print("🔍 [RAG SYSTEM DEBUG]")
            print(f"👉 USER QUESTION: '{question}'")
            print(f"👉 RETRIEVED {len(retrieved_docs)} CHUNKS FROM FAISS:")
            for i, doc in enumerate(retrieved_docs):
                src_file = os.path.basename(doc.metadata.get('source', 'Unknown'))
                print(f"  📍 Chunk {i+1} from Source File [{src_file}]:")
                print(f"     Text Preview: {doc.page_content[:150]}...")
            print("="*50 + "\n")
        except Exception as e:
            print(f"⚠️ [DEBUG ERROR] Could not log retrieval: {e}")

        # Run pipeline
        try:
            response = rag_chain.invoke({
                "input": question,
                "chat_history": formatted_history,
            })
            return {
                "answer": response["answer"],
                "sources": sources
            }
        except Exception as e:
            return {
                "answer": f"⚠️ Error running RAG pipeline: {str(e)}",
                "sources": []
            }