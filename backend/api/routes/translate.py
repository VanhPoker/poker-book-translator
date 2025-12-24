"""
Translation API Routes
"""
import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from typing import Optional

from api.models.schemas import (
    TranslateResponse, 
    BookResponse, 
    BookStatus,
    TokenUsage
)
from api.auth import require_admin

router = APIRouter()

# Temporary storage for job status (will be replaced with Supabase)
jobs_store: dict = {}


@router.post("/translate", response_model=TranslateResponse)
async def translate_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file to translate"),
    title: str = Form(..., description="Book title"),
    target_language: str = Form(default="vi", description="Target language"),
    _admin = Depends(require_admin)
):
    """
    Upload a PDF and start translation process.
    Returns immediately with job ID for polling.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create temp directory for this job
    job_dir = Path(f"temp_jobs/{job_id}")
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    input_path = job_dir / "source.pdf"
    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Store job info
    jobs_store[job_id] = {
        "id": job_id,
        "title": title,
        "status": BookStatus.PENDING,
        "target_language": target_language,
        "file_size_bytes": len(content),
        "input_path": str(input_path),
        "output_dir": str(job_dir / "output"),
    }
    
    # Start background translation
    background_tasks.add_task(
        run_translation_job,
        job_id=job_id,
        input_path=str(input_path),
        output_dir=str(job_dir / "output"),
        target_language=target_language
    )
    
    return TranslateResponse(
        id=job_id,
        status=BookStatus.PENDING,
        message="Translation started. Poll /books/{id} for status."
    )


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str):
    """Get book translation status and URLs"""
    if book_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Book not found")
    
    job = jobs_store[book_id]
    
    return BookResponse(
        id=job["id"],
        title=job["title"],
        status=job["status"],
        target_language=job.get("target_language", "vi"),
        html_url=job.get("html_url"),
        epub_url=job.get("epub_url"),
        pdf_url=job.get("pdf_url"),
        token_usage=job.get("token_usage"),
        file_size_bytes=job.get("file_size_bytes"),
        error_message=job.get("error_message"),
    )


@router.get("/books", response_model=dict)
async def list_books():
    """List all translated books"""
    books = [
        BookResponse(
            id=job["id"],
            title=job["title"],
            status=job["status"],
            html_url=job.get("html_url"),
            epub_url=job.get("epub_url"),
        )
        for job in jobs_store.values()
    ]
    return {"books": books, "total": len(books)}


async def run_translation_job(
    job_id: str, 
    input_path: str, 
    output_dir: str, 
    target_language: str
):
    """Background task to run the translation pipeline"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "translator"))
    
    # Import services
    from services.storage_service import get_storage_service
    from services.database_service import get_database_service
    
    storage = get_storage_service()
    db = get_database_service()
    
    try:
        jobs_store[job_id]["status"] = BookStatus.PROCESSING
        db.update_book_status(job_id, "processing")
        
        # Import translator modules
        from translator.extractor import extract_pdf_to_markdown
        from translator.ai_translator import translate_markdown
        from translator.builder import build_epub, build_html
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Step 1: Extract PDF to Markdown
        md_content = extract_pdf_to_markdown(input_path, output_dir)
        
        # Step 2: Translate Markdown
        translated_content = translate_markdown(md_content, output_dir=output_dir)
        
        # Step 3: Build outputs
        translated_md_path = Path(output_dir) / "temp_md" / "translated.md"
        final_dir = Path(output_dir) / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        
        epub_path = str(final_dir / "result.epub")
        html_path = str(final_dir / "result.html")
        
        build_epub(str(translated_md_path), epub_path, output_dir + "/")
        build_html(str(translated_md_path), html_path, output_dir + "/")
        
        # Step 4: Upload to GCS
        gcs_prefix = f"books/{job_id}/"
        
        html_url = storage.upload_file(html_path, f"{gcs_prefix}result.html")
        epub_url = storage.upload_file(epub_path, f"{gcs_prefix}result.epub")
        
        # Also upload images directory if exists
        images_dir = Path(output_dir) / "images"
        if images_dir.exists():
            storage.upload_directory(str(images_dir), f"{gcs_prefix}images/")
        
        # Step 5: Save to database
        db.save_book_urls(job_id, html_url=html_url, epub_url=epub_url)
        db.update_book_status(job_id, "completed")
        
        # Update local store
        jobs_store[job_id].update({
            "status": BookStatus.COMPLETED,
            "html_url": html_url,
            "epub_url": epub_url,
            "token_usage": TokenUsage(
                input_tokens=0,  # TODO: Get from translator
                output_tokens=0,
                estimated_cost=0.0
            )
        })
        
    except Exception as e:
        jobs_store[job_id].update({
            "status": BookStatus.FAILED,
            "error_message": str(e)
        })
        db.update_book_status(job_id, "failed", error_message=str(e))
