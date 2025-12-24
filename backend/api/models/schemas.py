"""
Pydantic Models for API Request/Response
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class BookStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranslateRequest(BaseModel):
    """Request model for translation (used with form data)"""
    title: str = Field(..., description="Title of the book")
    target_language: str = Field(default="vi", description="Target language code")


class TranslateResponse(BaseModel):
    """Response after starting translation"""
    id: str
    status: BookStatus
    message: str


class TokenUsage(BaseModel):
    """Token usage statistics"""
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0


class BookResponse(BaseModel):
    """Full book response with URLs"""
    id: str
    title: str
    status: BookStatus
    source_format: str = "pdf"
    target_language: str = "vi"
    
    # Output URLs
    html_url: Optional[str] = None
    epub_url: Optional[str] = None
    pdf_url: Optional[str] = None
    
    # Token tracking
    token_usage: Optional[TokenUsage] = None
    
    # Metadata
    page_count: Optional[int] = None
    file_size_bytes: Optional[int] = None
    error_message: Optional[str] = None
    
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class BookListResponse(BaseModel):
    """Response for listing books"""
    books: list[BookResponse]
    total: int
