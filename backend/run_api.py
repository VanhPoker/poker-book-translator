"""
Run the FastAPI server
Usage: python run_api.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
