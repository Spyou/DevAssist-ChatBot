from fastapi import FastAPI, WebSocket, UploadFile, File, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
from groq import Groq as GroqClient
from dotenv import load_dotenv
from mcp_client import MCPClient
from datetime import datetime
from uuid import uuid4
import os
import json
from pathlib import Path
from rag_engine import RAGEngine
from memory_manager import MemoryManager
from auth import verify_token, AuthManager
from web_research import WebResearchService
from qwen_service import QwenService

load_dotenv()

app = FastAPI(docs_url="/api/docs", redoc_url="/api/redoc")
client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))
rag_engine = RAGEngine()
memory = MemoryManager()
auth_manager = AuthManager()
web_research = WebResearchService()
qwen_service = QwenService()
mcp_client = MCPClient()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost", 
        "http://localhost:80", 
        "http://localhost:8888", 
        "http://devassist.local"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are DevAssist, a programming-focused AI assistant. You EXCLUSIVELY help with software development.

ALLOWED TOPICS ONLY:
- Code, algorithms, data structures
- Debugging, errors, exceptions
- Programming languages (Python, JavaScript, Java, C++, Go, Rust, etc.)
- Frameworks and libraries
- Databases and SQL
- APIs and web development
- System design and architecture
- DevOps and deployment
- Git and version control
- Testing and CI/CD

FORBIDDEN - NEVER respond to:
- Jokes, humor, entertainment
- Stories, creative writing
- General knowledge questions
- Non-technical casual conversation
- Personal advice
- Current events, news, weather
- Any topic unrelated to programming

RESPONSE RULES:
1. If the question is NOT about programming, respond EXACTLY: "I only assist with programming questions. Please ask about code, algorithms, debugging, or system design."

2. Do NOT be conversational or friendly beyond technical assistance.

3. Do NOT apologize excessively or over-explain why you can't help.

4. Keep responses technical, direct, and code-focused.

5. When documents are uploaded, extract technical information only (APIs, functions, code snippets, architecture).

Stay laser-focused on software engineering ONLY."""

active_sessions = {}

class AuthRequest(BaseModel):
    email: str
    password: str
    name: str = None

@app.post("/api/signup")
async def signup_endpoint(req: AuthRequest):
    return await auth_manager.signup(req.email, req.password, req.name)

@app.post("/api/login")
async def login_endpoint(req: AuthRequest):
    return await auth_manager.login(req.email, req.password)

@app.get("/api/health")
async def health():
    return {"status": "running"}

@app.get("/api/history/{user_id}")
async def get_chat_history(user_id: str):
    try:
        response = memory.supabase.table('chat_history')\
            .select('id, session_id, role, content, created_at')\
            .eq('user_id', user_id)\
            .order('created_at', desc=False)\
            .limit(200)\
            .execute()
        
        all_messages = response.data
        
        if not all_messages:
            return {"status": "success", "conversations": []}
        
        sessions = {}
        for msg in all_messages:
            session_id = msg.get('session_id', 'default')
            if session_id not in sessions:
                sessions[session_id] = []
            sessions[session_id].append(msg)
        
        conversations = []
        for session_id, msgs in sessions.items():
            if msgs:
                first_msg = msgs[0]['content']
                last_msg_time = msgs[-1]['created_at']
                
                conversations.append({
                    'id': session_id,
                    'title': first_msg[:50] + ('...' if len(first_msg) > 50 else ''),
                    'preview': first_msg[:100],
                    'timestamp': last_msg_time,
                    'messages': [{'role': m['role'], 'content': m['content']} for m in msgs]
                })
        
        conversations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            "status": "success",
            "conversations": conversations
        }
    except Exception as e:
        print(f"Error getting history: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/clear")
async def clear_documents():
    try:
        success = rag_engine.clear_documents()
        if success:
            return {"status": "success", "message": "All documents cleared"}
        return {"status": "error", "message": "Failed to clear documents"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/clear-memory")
async def clear_memory_endpoint(user_id: str):
    try:
        success = memory.clear_history(user_id)
        if success:
            return {"status": "success", "message": "Memory cleared"}
        return {"status": "error", "message": "Failed to clear memory"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/upload")
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
    
@app.get("/api/mcp/tools")
async def get_mcp_tools():
    return {
        "status": "success",
        "tools": mcp_client.list_tools()
    }

@app.post("/api/mcp/test")
async def test_mcp_tool(query: str):
    result = await mcp_client.call_tool(
        "queryProgrammingWeb",
        {"query": query, "max_results": 3}
    )
    return result

@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    user_id = None
    session_id = None

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            user_id = message_data.get("user_id", "anonymous")
            session_id = message_data.get("session_id")
            web_search_enabled = message_data.get("web_search_enabled", False)
            qwen_enabled = message_data.get("qwen_enabled", False)

            print(f"📨 Message: {user_message}")
            print(f"🔍 Web Search Enabled: {web_search_enabled}")
            print(f"🤖 Qwen Enabled: {qwen_enabled}")

            if not session_id:
                session_id = str(uuid4())
                active_sessions[user_id] = session_id

            memory.add_message(user_id, "user", user_message, session_id)

            # ===== QWEN MODE: Stream direct response (bypass LLM) =====
            if qwen_enabled:
                await websocket.send_json({
                    "status": "qwen_processing",
                    "message": "🤖 Querying Qwen AI..."
                })

                qwen_result = await qwen_service.query_qwen(user_message)
                
                if qwen_result and qwen_result.get('content'):
                    # Stream Qwen response DIRECTLY to frontend
                    qwen_response = qwen_result['content']
                    
                    print(f"✅ Streaming Qwen response ({len(qwen_response)} chars) directly to client...")
                    
                    for char in qwen_response:
                        await websocket.send_json({
                            "token": char,
                            "status": "streaming",
                            "session_id": session_id
                        })
                    
                    # Save to memory
                    memory.add_message(user_id, "assistant", qwen_response, session_id)
                    
                    # Send done signal
                    await websocket.send_json({
                        "status": "done",
                        "session_id": session_id,
                        "mcp_used": False,
                        "sources_count": 0,
                        "qwen_used": True
                    })
                    
                    print("✅ Qwen response streaming complete")
                    continue  # Skip LLM processing completely
                else:
                    # Qwen failed
                    await websocket.send_json({
                        "status": "error",
                        "message": "⚠️ Qwen failed to respond"
                    })
                    continue

            # ===== NORMAL MODE (Web Search + Your LLM) =====
            web_results = []
            context_text = ""

            # WEB SEARCH
            if web_search_enabled and web_research.is_programming_query(user_message):
                await websocket.send_json({
                    "status": "searching",
                    "message": "🔍 Using MCP Web Research Tool..."
                })

                mcp_response = await mcp_client.call_tool(
                    "queryProgrammingWeb", {"query": user_message, "max_results": 5}
                )

                if "results" in mcp_response and mcp_response["results"]:
                    web_results = mcp_response["results"]

                    context_text += "\n\n=== WEB RESEARCH RESULTS (from Bing) ===\n"
                    context_text += f"Query: {mcp_response['query']}\n"
                    context_text += f"Found {mcp_response['count']} web results:\n\n"
                    for i, result in enumerate(web_results, 1):
                        context_text += (f"[Source {i}]\n"
                                         f"Title: {result['title']}\n"
                                         f"URL: {result['url']}\n"
                                         f"Content: {result['snippet']}\n\n")
                    context_text += "=== END WEB RESEARCH ===\n\n"
                    context_text += (
                        "INSTRUCTIONS:\n"
                        "If any of the web research results above directly answer the user's question, "
                        "use ONLY those and cite [Source N] for every fact. "
                        "If not found in the web results, you MAY use your own up-to-date programming knowledge as fallback.\n\n"
                    )

            # RAG context
            context_chunks = rag_engine.search(user_message)
            if context_chunks:
                context_text += "\n\n--- UPLOADED DOCUMENTS ---\n"
                for i, chunk in enumerate(context_chunks, 1):
                    context_text += f"\n[Document {i}]\n{chunk}\n"
                context_text += "\n--- END DOCUMENTS ---\n"

            full_prompt = SYSTEM_PROMPT + context_text

            recent_history = memory.get_session_history(user_id, session_id, limit=10)
            messages = [{"role": "system", "content": full_prompt}]
            if len(recent_history) > 1:
                messages.extend(recent_history[:-1])
            messages.append({"role": "user", "content": user_message})

            print("="*30, "LLM CONTEXT", "="*30)
            print(full_prompt[:800])
            print("="*70)

            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    stream=True,
                    temperature=0.7,
                    max_tokens=2048
                )
                assistant_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        assistant_response += token
                        await websocket.send_json({
                            "token": token,
                            "status": "streaming",
                            "session_id": session_id
                        })

                if web_results:
                    sources_text = "\n\n**Sources (Web Research):**\n"
                    for i, result in enumerate(web_results, 1):
                        sources_text += f"{i}. [{result['title']}]({result['url']})\n"
                    for char in sources_text:
                        await websocket.send_json({
                            "token": char,
                            "status": "streaming",
                            "session_id": session_id
                        })
                    assistant_response += sources_text

                memory.add_message(user_id, "assistant", assistant_response, session_id)

                await websocket.send_json({
                    "status": "done",
                    "session_id": session_id,
                    "mcp_used": len(web_results) > 0,
                    "sources_count": len(web_results),
                    "qwen_used": False
                })

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "rate_limit" in error_msg.lower():
                    await websocket.send_json({
                        "status": "error",
                        "message": "⏱️ Traffic is high. Please wait 10 seconds."
                    })
                else:
                    await websocket.send_json({
                        "status": "error",
                        "message": f"Error: {error_msg}"
                    })

    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
        if user_id in active_sessions:
            del active_sessions[user_id]


# Static files
static_dir = Path(__file__).parent.parent / "frontend" / "dist"

if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(static_dir / "index.html"))
else:
    print(f"⚠️  Frontend not found at: {static_dir}")
    print("    Run 'npm run build' in frontend folder")
