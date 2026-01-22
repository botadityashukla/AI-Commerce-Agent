import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from langchain_core.messages import HumanMessage

from backend.config import get_settings
from backend.core.logger import setup_logger
from backend.rag.loader import load_knowledge_base
from backend.rag.vector_store import vector_store
from backend.core.router import graph, AgentState

settings = get_settings()
logger = setup_logger("app")

app = FastAPI(title="Multi-Agent Support AI")

# CORS
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    ticket: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup_event():
    logger.info("System starting up...")
    try:
        docs = load_knowledge_base(settings.KNOWLEDGE_BASE_PATH)
        vector_store.initialize_db(docs)
        logger.info("System initialized successfully.")
    except Exception as e:
        logger.critical(f"Startup failed: {e}")

@app.get("/health")
def health_check():
    return {
        "status": "active", 
        "llm_provider": settings.LLM_PROVIDER,
        "vector_db": "loaded" if vector_store.vector_db else "not_loaded"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Received message: {request.message}")
    
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "agent_used": "",
        "ticket": None
    }
    
    try:
        # Invoke the graph
        output = await graph.ainvoke(initial_state)
        
        # Parse output
        messages = output.get("messages", [])
        last_message = messages[-1] if messages else "No response generated."
        agent_used = output.get("agent_used", "Unknown")
        ticket = output.get("ticket")
        
        response_text = last_message if isinstance(last_message, str) else last_message.content
        
        return ChatResponse(
            response=response_text,
            agent_used=agent_used,
            ticket=ticket
        )
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
def get_logs():
    # In a real system, this would read from a DB or file.
    # For now, we return a mock or could implement a memory buffer handler in logger.
    return {"logs": ["Log retrieval not implemented in file mode yet."]}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
