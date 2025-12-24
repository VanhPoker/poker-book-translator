"""
Admin Authentication Module
Simple API key based authentication for admin endpoints
"""
import os
from fastapi import HTTPException, Header, Depends
from dotenv import load_dotenv

load_dotenv()

# Admin API key from environment
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-admin-key-change-in-production")


async def require_admin(x_api_key: str = Header(..., description="Admin API Key")):
    """
    Dependency to require admin authentication.
    Pass API key in X-API-Key header.
    """
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key. Admin access required."
        )
    return True


def get_admin_key():
    """Get the current admin API key (for testing)"""
    return ADMIN_API_KEY
