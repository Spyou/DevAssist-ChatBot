from fastapi import FastAPI, WebSocket, UploadFile, File, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
import os
import json
from rag_engine import RAGEngine

load_dotenv()

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
rag_engine = RAGEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are DevAssist, an expert programming assistant. You help developers with coding questions, debugging, algorithms, system design, and software engineering concepts.

When the user provides context from uploaded documents, USE THAT INFORMATION to answer their questions. Reference the documentation directly and explain concepts based on what's in the provided context.

If asked about uploaded documentation:
- Summarize and explain what's in the documents
- Extract key information, functions, APIs, or concepts
- Answer questions based on the documentation content
- Quote relevant parts when helpful

For general programming questions without context, provide clear technical explanations with code examples when appropriate.

Always be concise, accurate, and helpful."""

@app.get("/")
async def root():
    return {"status": "running"}

@app.post("/clear")
async def clear_documents():
    """Clear all uploaded documents from RAG"""
    try:
        success = rag_engine.clear_documents()
        if success:
            return {"status": "success", "message": "All documents cleared"}
        else:
            return {"status": "error", "message": "Failed to clear documents"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(('.txt', '.md', '.pdf')):
            return {"status": "error", "message": "Invalid file type. Use .txt, .md, or .pdf"}
        
        content = await file.read()
        
        if len(content) > 5 * 1024 * 1024:
            return {"status": "error", "message": "File too large (max 5MB)"}
        
        chunks_processed = rag_engine.ingest_document(content, file.filename)
        
        return {
            "status": "success",
            "chunks_processed": chunks_processed,
            "filename": file.filename
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            # Retrieve relevant context from RAG
            context_chunks = rag_engine.search(user_message)
            
            # Build context-aware prompt
            if context_chunks:
                context_text = "\n\n--- CONTEXT FROM UPLOADED DOCUMENTS ---\n"
                for i, chunk in enumerate(context_chunks, 1):
                    context_text += f"\n[Document Section {i}]\n{chunk}\n"
                context_text += "\n--- END OF CONTEXT ---\n\nUse the above context to answer the user's question. Reference specific information from the documents when relevant."
                
                full_prompt = SYSTEM_PROMPT + context_text
            else:
                full_prompt = SYSTEM_PROMPT
            
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": full_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    stream=True,
                    temperature=0.7,
                    max_tokens=2048
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        await websocket.send_json({
                            "token": chunk.choices[0].delta.content,
                            "status": "streaming"
                        })
                
                await websocket.send_json({"status": "done"})
                
            except Exception as e:
                error_msg = str(e)
                
                # Handle rate limiting
                if "429" in error_msg or "rate_limit" in error_msg.lower():
                    await websocket.send_json({
                        "status": "error",
                        "message": "⏱️ Traffic is high. Please wait 10 seconds before asking again."
                    })
                # Handle other API errors
                elif "400" in error_msg or "401" in error_msg or "403" in error_msg:
                    await websocket.send_json({
                        "status": "error",
                        "message": f"API Error: {error_msg}"
                    })
                else:
                    await websocket.send_json({
                        "status": "error",
                        "message": f"Error: {error_msg}"
                    })
                    
    except WebSocketDisconnect:
        print("Client disconnected")
