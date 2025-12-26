"""
Translation Queue API Routes
Manage pending PDFs and trigger translations
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import uuid
import os
from datetime import datetime

from services.database_service import DatabaseService
from services.storage_service import StorageService

router = APIRouter(prefix="/queue", tags=["Translation Queue"])

db = DatabaseService()
storage = StorageService()


class PendingBookCreate(BaseModel):
    title: str
    original_title: Optional[str] = None
    category: str = "general"
    priority: int = 0
    source: str = "upload"
    metadata: dict = {}


class PendingBookUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None


@router.get("/pending")
async def get_pending_books(status: Optional[str] = None, source: Optional[str] = None):
    """Get all pending books in queue"""
    import time
    start = time.time()
    
    try:
        query = db.supabase.table("pending_books").select("*")
        
        if status:
            query = query.eq("status", status)
        
        if source:
            query = query.eq("source", source)
        
        result = query.order("priority", desc=True).order("created_at", desc=True).limit(100).execute()
        
        elapsed = time.time() - start
        print(f"📊 Queue pending loaded {len(result.data)} books in {elapsed:.2f}s")
        
        return {"books": result.data, "count": len(result.data)}
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Queue pending failed after {elapsed:.2f}s: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending/{book_id}")
async def get_pending_book(book_id: str):
    """Get a specific pending book"""
    try:
        result = db.supabase.table("pending_books").select("*").eq("id", book_id).single().execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Book not found")


@router.post("/pending")
async def create_pending_book(book: PendingBookCreate, pdf_url: str):
    """Add a new book to the translation queue"""
    try:
        book_id = str(uuid.uuid4())
        
        data = {
            "id": book_id,
            "title": book.title,
            "original_title": book.original_title,
            "pdf_url": pdf_url,
            "category": book.category,
            "priority": book.priority,
            "source": book.source,
            "status": "pending",
            "metadata": book.metadata
        }
        
        result = db.supabase.table("pending_books").insert(data).execute()
        return {"id": book_id, "message": "Book added to queue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_pdf_to_queue(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    category: str = "general",
    priority: int = 0,
    source: str = "upload",
    note: Optional[str] = None
):
    """Upload a PDF and add to translation queue"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Generate unique ID
        book_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Upload to storage
        storage_path = f"pending/{book_id}/{file.filename}"
        
        # Save temporarily then upload
        temp_path = f"temp_jobs/{book_id}.pdf"
        os.makedirs("temp_jobs", exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        pdf_url = storage.upload_file(temp_path, storage_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Extract title from filename if not provided
        if not title:
            title = file.filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        
        # Build metadata
        metadata = {"file_size": file_size}
        if note:
            metadata["note"] = note
        
        # Add to pending_books table
        data = {
            "id": book_id,
            "title": title,
            "original_title": file.filename,
            "pdf_url": pdf_url,
            "category": category,
            "priority": priority,
            "source": source,
            "status": "pending",
            "metadata": metadata
        }
        
        db.supabase.table("pending_books").insert(data).execute()
        
        return {
            "id": book_id,
            "title": title,
            "pdf_url": pdf_url,
            "source": source,
            "message": "PDF uploaded and added to queue"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/pending/{book_id}")
async def update_pending_book(book_id: str, update: PendingBookUpdate):
    """Update a pending book"""
    try:
        update_data = {k: v for k, v in update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        result = db.supabase.table("pending_books").update(update_data).eq("id", book_id).execute()
        return {"message": "Updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/pending/{book_id}")
async def delete_pending_book(book_id: str):
    """Delete a pending book from queue"""
    try:
        db.supabase.table("pending_books").delete().eq("id", book_id).execute()
        return {"message": "Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate/{book_id}")
async def trigger_translation(book_id: str, background_tasks: BackgroundTasks):
    """
    Trigger translation for a pending book.
    This calls the main /translate API with pdf_url and pending_book_id.
    """
    print(f"🔄 Starting translation for pending book: {book_id}")
    
    try:
        # Get pending book
        result = db.supabase.table("pending_books").select("*").eq("id", book_id).single().execute()
        pending_book = result.data
        
        if not pending_book:
            raise HTTPException(status_code=404, detail="Pending book not found")
        
        if pending_book["status"] == "translating":
            raise HTTPException(status_code=400, detail="Book is already being translated")
        
        if pending_book["status"] == "completed":
            raise HTTPException(status_code=400, detail="Book is already translated")
        
        print(f"📚 Book found: {pending_book['title'][:50]}...")
        
        # Import and call the translate API directly
        from api.routes.translate import translate_book
        
        # Create a MockUploadFile since we're using URL instead
        class MockUploadFile:
            filename = None
        
        # Call translate_book with pdf_url instead of file
        response = await translate_book(
            background_tasks=background_tasks,
            file=None,  # No file upload
            pdf_url=pending_book["pdf_url"],  # Use URL
            title=pending_book["title"],
            target_language="vi",
            category=pending_book.get("category"),
            pending_book_id=book_id,  # Link to pending book
            _admin=None  # Skip admin check (internal call)
        )
        
        return {
            "message": "Translation started",
            "translated_book_id": response.id,
            "pending_book_id": book_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in trigger_translation: {e}")
        import traceback
        traceback.print_exc()
        # Reset status on error
        try:
            db.supabase.table("pending_books").update({"status": "pending"}).eq("id", book_id).execute()
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))


async def run_translation_job_with_pending_update(
    translated_id: str,
    pending_id: str,
    input_path: str,
    output_dir: str,
    target_language: str
):
    """Wrapper that runs translation and updates pending_book status"""
    from api.routes.translate import run_translation_job
    
    print(f"🚀 Starting translation job: {translated_id}")
    
    try:
        # Run the actual translation
        await run_translation_job(
            job_id=translated_id,
            input_path=input_path,
            output_dir=output_dir,
            target_language=target_language
        )
        
        # Update pending book status to completed
        db.supabase.table("pending_books").update({"status": "completed"}).eq("id", pending_id).execute()
        print(f"✅ Translation complete! Pending book {pending_id} marked as completed")
        
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Update pending book status to failed
        db.supabase.table("pending_books").update({"status": "failed"}).eq("id", pending_id).execute()


async def run_translation_from_queue(translated_id: str, pending_id: str, pdf_url: str, title: str):
    """Background task to run translation from queue"""
    import requests
    from pathlib import Path
    
    from translator.extractor import extract_pdf_to_markdown, extract_cover_image
    from translator.ai_translator import translate_markdown
    from translator.builder import build_html, build_epub, build_pdf
    
    try:
        # Create output directory
        output_dir = Path(f"temp_jobs/{translated_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Download PDF
        print(f"📥 Downloading PDF: {pdf_url}")
        response = requests.get(pdf_url, timeout=120)
        pdf_path = output_dir / "original.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        
        # Extract markdown
        print("📖 Extracting PDF to markdown...")
        db.update_book_status(translated_id, "processing")
        markdown_content = extract_pdf_to_markdown(str(pdf_path))
        
        # Extract cover
        cover_path = output_dir / "cover.png"
        extract_cover_image(str(pdf_path), str(cover_path))
        
        # Translate
        print("🌐 Translating...")
        translated_content = await translate_markdown(markdown_content, target_language="vi")
        
        # Build outputs
        print("🔨 Building outputs...")
        html_path = output_dir / "translated.html"
        epub_path = output_dir / "translated.epub"
        
        build_html(translated_content, str(html_path), title)
        build_epub(translated_content, str(epub_path), title)
        
        # Try to build PDF (may fail without LaTeX)
        try:
            pdf_output_path = output_dir / "translated.pdf"
            build_pdf(translated_content, str(pdf_output_path), title)
        except:
            pdf_output_path = None
        
        # Upload to storage
        print("☁️ Uploading to storage...")
        
        html_url = storage.upload_file(str(html_path), f"books/{translated_id}/translated.html")
        epub_url = storage.upload_file(str(epub_path), f"books/{translated_id}/translated.epub")
        
        cover_url = None
        if cover_path.exists():
            cover_url = storage.upload_file(str(cover_path), f"books/{translated_id}/cover.png")
        
        translated_pdf_url = None
        if pdf_output_path and pdf_output_path.exists():
            translated_pdf_url = storage.upload_file(str(pdf_output_path), f"books/{translated_id}/translated.pdf")
        
        # Update database
        db.save_book_urls(
            book_id=translated_id,
            html_url=html_url,
            epub_url=epub_url,
            pdf_url=translated_pdf_url or pdf_url,
            cover_url=cover_url
        )
        
        db.update_book_status(translated_id, "completed")
        
        # Update pending book status
        db.supabase.table("pending_books").update({"status": "completed"}).eq("id", pending_id).execute()
        
        print(f"✅ Translation complete: {translated_id}")
        
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        import traceback
        traceback.print_exc()
        
        db.update_book_status(translated_id, "failed")
        db.supabase.table("pending_books").update({"status": "failed"}).eq("id", pending_id).execute()
