# DevAssist Chatbot

DevAssist is an AI-powered programming assistant built with FastAPI, Vue.js, and the Groq API. It supports document uploads and uses a Retrieval-Augmented Generation (RAG) engine to provide context-aware answers for technical queries.

## Features

* Programming-focused AI assistant using Groq Llama 3.3 70B
* Document upload support (.txt, .md, .pdf)
* Context-aware answers through RAG (ChromaDB + Sentence Transformers)
* Real-time streaming responses via WebSocket
* Modern dark UI built with Vue 3 and Tailwind CSS
* Automatic rate-limit handling and error management
* Fully local embeddings and vector search

## Tech Stack

### Frontend

* Vue.js 3 (Composition API)
* Tailwind CSS
* Vite
* Marked (Markdown rendering)

### Backend

* FastAPI (Python)
* Groq API for LLM inference
* ChromaDB for vector storage
* Sentence Transformers for embeddings
* WebSockets for streaming responses

## Setup

### Prerequisites

* Python 3.11 or higher
* Node.js 18 or higher
* Groq API key

### Backend Setup

```
cd backend
pip3 install -r requirements.txt
echo 'GROQ_API_KEY=your_api_key_here' > .env
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173]

## Usage

1. Upload documents using the left sidebar
2. Ask programming-related questions in the chat
3. If documents are uploaded, the model uses them as context through RAG
4. Use the Clear Documents option when switching topics

## API Endpoints

* GET / — Health check
* POST /upload — Upload document for RAG
* POST /clear — Clear all indexed documents
* WebSocket /ws/chat — Real-time streaming chat interface

## Configuration

### Environment Variables (backend .env)

```
GROQ_API_KEY=your_groq_api_key
```

### Model (main.py)

llama-3.3-70b-versatile

### RAG Settings (rag_engine.py)

* Chunk size: 500 characters
* Overlap: 50 characters
* Top-k retrieval: 3

## Notes

* Chat history is session-based and resets on page refresh
* RAG is optional; the assistant works normally without uploaded documents
* Vector data is stored in memory only
