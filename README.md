# 🚀 Transportation Spec AI Copilot

An AI-powered engineering assistant that enables conversational search over transportation and engineering specification documents using a Retrieval-Augmented Generation (RAG) architecture.

Built with **Python**, **FastAPI**, **Next.js**, **Qdrant**, **Ollama**, and **Llama 3.1**, the application provides grounded, context-aware answers while supporting multi-turn conversations similar to ChatGPT.

---

# 🖼️ Screenshots

## Home

![Home](screenshots/Home%20Screen.png)

---

## Conversation

![Conversation](screenshots/Conversation.png)

---

## Follow-up Questions

![Follow Up](screenshots/followup.png)

---

# ✨ Features

- 🤖 Conversational AI assistant for transportation engineering specifications
- 📚 Retrieval-Augmented Generation (RAG)
- 🔍 Hybrid Retrieval
  - BM25 keyword search
  - Semantic vector search
- ⚡ Reciprocal Rank Fusion (RRF)
- 🎯 Cross-Encoder Reranking (BGE Reranker)
- 🧠 Conversational Memory for follow-up questions
- 📄 Section-aware document chunking
- 📍 Metadata-aware citations
- 🔒 Fully Local LLM using Ollama
- 🌐 Modern web interface built with Next.js
- 🚀 FastAPI backend APIs

---

# 🏗️ Architecture

```
PDF
│
├── Parsing (PyMuPDF)
│
├── Cleaning
│
├── Section-aware Chunking
│
├── Metadata Extraction
│
├── BM25 Index
│
├── BGE Embeddings
│
├── Qdrant Vector Database
│
├── Hybrid Retrieval
│      ├── BM25
│      └── Vector Search
│
├── Reciprocal Rank Fusion
│
├── Cross Encoder Reranker
│
├── Prompt Grounding
│
├── Ollama (Llama 3.1)
│
└── Conversational Response
```

---

# 🛠️ Tech Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Backend

- FastAPI
- Python

## AI / ML

- Ollama
- Llama 3.1
- Retrieval-Augmented Generation (RAG)
- Sentence Transformers
- BAAI/bge-large-en-v1.5
- BAAI/bge-reranker-large

## Retrieval

- BM25
- Qdrant
- Hybrid Search
- Reciprocal Rank Fusion (RRF)

## Document Processing

- PyMuPDF

---

# 📂 Project Structure

```
transport-spec-rag-ai/

├── app/
│   ├── api.py
│   ├── ingest.py
│   ├── query.py
│   ├── prompts.py
│   ├── conversation.py
│   └── ...
│
├── transport-rag-ui/
│
├── screenshots/
│
├── data/
│
└── README.md
```

---

# ⚙️ Running the Project

## Backend

```bash
cd app

source ../venv/bin/activate

uvicorn api:app --reload
```

---

## Frontend

```bash
cd transport-rag-ui

npm install

npm run dev
```

---

## Ollama

```bash
ollama serve
```

Open:

```
http://localhost:3000
```

---

# 💬 Example Questions

- What are the curing requirements for concrete?
- Explain pull box installation requirements.
- What are the requirements for high mast luminaires?
- What are the cold weather curing requirements?
- Summarize Section 87.

---

# 🔮 Future Improvements

- Streaming responses
- PDF viewer with highlighted citations
- Multi-document search
- Authentication
- Chat history persistence
- Source highlighting
- Document upload support
- Evaluation framework for retrieval quality

---

# 📜 License

This project was developed for educational and portfolio purposes.