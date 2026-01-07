from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
from dotenv import load_dotenv

from .config.database import connect_db, get_database
from .config.redis_config import connect_redis, get_redis
from .services.auth_service import verify_token
from .routers import documents, chat, content, inventory

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AutomateIQ AI Engine",
    description="AI-powered microservices for business automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    # await connect_db()
    # await connect_redis()
    print("🤖 AI Engine started successfully")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-engine",
        "version": "1.0.0"
    }

# Authentication dependency (optional for now)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user info"""
    try:
        # TODO: Implement actual token verification
        # user_info = await verify_token(credentials.credentials)
        # return user_info
        return {"user_id": "test_user", "organization_id": "test_org"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Include routers
app.include_router(
    documents.router,
    prefix="/api/documents",
    tags=["documents"],
    # dependencies=[Depends(get_current_user)]  # Commented out for testing
)

app.include_router(
    chat.router,
    prefix="/api/chat",
    tags=["chat"],
    # dependencies=[Depends(get_current_user)]  # Commented out for testing
)

app.include_router(
    content.router,
    prefix="/api/content",
    tags=["content"],
    # dependencies=[Depends(get_current_user)]  # Commented out for testing
)

app.include_router(
    inventory.router,
    prefix="/api/inventory",
    tags=["inventory"],
    # dependencies=[Depends(get_current_user)]  # Commented out for testing
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AutomateIQ AI Engine",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )