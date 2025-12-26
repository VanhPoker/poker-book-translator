"""
FastAPI Application - Book Translation API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import translate, queue

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Book Translation API starting...")
    yield
    # Shutdown
    print("👋 Book Translation API shutting down...")


app = FastAPI(
    title="Book Translation API",
    description="API để dịch sách từ PDF sang tiếng Việt",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(translate.router, prefix="/api/v1", tags=["Translation"])
app.include_router(queue.router, prefix="/api/v1", tags=["Translation Queue"])


@app.get("/")
async def root():
    return {
        "message": "Book Translation API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check if env vars are loaded (remove in production!)"""
    import os
    admin_key = os.getenv("ADMIN_API_KEY", "NOT_SET")
    return {
        "admin_key_first_4": admin_key[:4] if len(admin_key) >= 4 else admin_key,
        "admin_key_length": len(admin_key),
        "storage_provider": os.getenv("STORAGE_PROVIDER", "NOT_SET"),
        "supabase_url_set": bool(os.getenv("SUPABASE_URL")),
    }
