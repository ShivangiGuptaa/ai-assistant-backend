from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from enhanced_ai_handler import EnhancedAIHandler
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Assistant API", version="2.0.0")

# CORS middleware to allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Enhanced AI Handler with action execution
ai_handler = EnhancedAIHandler()

class CommandRequest(BaseModel):
    command: str
    context: Optional[str] = None

class CommandResponse(BaseModel):
    success: bool
    response: str
    code: Optional[str] = None
    language: Optional[str] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AI Assistant API is running!",
        "version": "1.0.0"
    }

@app.post("/api/command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """
    Process user commands and return AI-generated responses
    """
    try:
        result = await ai_handler.process_command(request.command, request.context)
        return CommandResponse(
            success=True,
            response=result.get("response", ""),
            code=result.get("code"),
            language=result.get("language")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Check if AI service is properly configured"""
    is_configured = ai_handler.is_configured()
    return {
        "ai_configured": is_configured,
        "status": "ready" if is_configured else "needs_configuration"
    }

@app.get("/api/memory")
async def get_memory():
    """Get user memory summary"""
    try:
        summary = ai_handler.user_memory.get_memory_summary()
        profile = ai_handler.user_memory.get_profile()
        return {
            "success": True,
            "summary": summary,
            "profile": profile
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.delete("/api/memory")
async def clear_memory():
    """Clear all user memory"""
    try:
        ai_handler.user_memory.clear_memory()
        return {
            "success": True,
            "message": "Memory cleared successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"""
    ╔═══════════════════════════════════════════╗
    ║   AI Assistant Backend Server Started!    ║
    ╚═══════════════════════════════════════════╝
    
    🚀 Server running on: http://{host}:{port}
    📚 API Docs: http://{host}:{port}/docs
    🔧 Health Check: http://{host}:{port}/api/health
    
    Press CTRL+C to stop the server
    """)
    
    uvicorn.run(app, host=host, port=port)
