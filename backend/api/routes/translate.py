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
from services.database_service import get_database_service

router = APIRouter()

# Temporary storage for job status (will be replaced with Supabase)
jobs_store: dict = {}


def translate_title(title: str, target_language: str = "vi") -> str:
    """
    Translate book title to target language and return bilingual title.
    Example: "Theory of Poker" -> "Theory of Poker - Lý thuyết Poker"
    """
    import os
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return title
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = f"""Translate this book title to Vietnamese. 
Return ONLY the Vietnamese translation, nothing else.
Keep poker terminology in English (Poker, Bluff, Fold, etc).

Title: {title}
Vietnamese:"""
        
        response = model.generate_content(prompt)
        vietnamese_title = response.text.strip()
        
        # Combine: "English Title - Vietnamese Title"
        bilingual_title = f"{title} - {vietnamese_title}"
        print(f"📚 Title translated: {bilingual_title}")
        
        return bilingual_title
    except Exception as e:
        print(f"⚠️ Could not translate title: {e}")
        return title


def auto_classify_book(title: str) -> str:
    """
    Auto-classify book into a category based on title using Gemini AI.
    Categories: shortdeck, omaha, nlh, ai_research, general
    """
    import os
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "general"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = f"""Classify this poker book into ONE of these categories based on its title:
- shortdeck: Books about Short Deck poker (6+, Triton)
- omaha: Books about Omaha poker (PLO, PLO5, PLO Hi-Lo)
- nlh: Books about No-Limit Hold'em (Texas Holdem, NLH, NLHE)
- ai_research: Books about AI, GTO, solvers, game theory, machine learning in poker
- psychology: Books about poker psychology, mental game, tilt control, mindset
- general: General poker strategy, mixed games, or unclear

Title: {title}

Return ONLY the category name (shortdeck, omaha, nlh, ai_research, psychology, or general), nothing else."""
        
        response = model.generate_content(prompt)
        category = response.text.strip().lower()
        
        # Validate category
        valid_categories = ['shortdeck', 'omaha', 'nlh', 'ai_research', 'psychology', 'general']
        if category not in valid_categories:
            category = 'general'
        
        print(f"📂 Category classified: {category}")
        return category
    except Exception as e:
        print(f"⚠️ Could not classify book: {e}")
        return "general"


@router.post("/translate", response_model=TranslateResponse)
async def translate_book(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(default=None, description="PDF file to translate"),
    pdf_url: Optional[str] = Form(default=None, description="URL to PDF file (alternative to file upload)"),
    title: Optional[str] = Form(default=None, description="Book title (optional, auto-extracted)"),
    target_language: str = Form(default="vi", description="Target language"),
    category: Optional[str] = Form(default=None, description="Book category (optional, auto-classified)"),
    pending_book_id: Optional[str] = Form(default=None, description="ID of pending book (for queue integration)"),
    _admin = Depends(require_admin)
):
    """
    Translate a PDF to target language.
    
    Accepts either:
    - file: Upload a PDF file directly
    - pdf_url: URL to a PDF file (e.g., arXiv, Supabase storage)
    
    Optionally link to a pending_book_id for queue integration.
    """
    import requests
    
    # Validate: must have either file or pdf_url
    if not file and not pdf_url:
        raise HTTPException(status_code=400, detail="Either 'file' or 'pdf_url' must be provided")
    
    if file and pdf_url:
        raise HTTPException(status_code=400, detail="Provide either 'file' or 'pdf_url', not both")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create temp directory for this job
    job_dir = Path(f"temp_jobs/{job_id}")
    job_dir.mkdir(parents=True, exist_ok=True)
    input_path = job_dir / "source.pdf"
    
    # Get PDF content - either from upload or URL
    if file:
        # File upload
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        
        # Extract title from filename if not provided
        if not title:
            title = file.filename.rsplit('.', 1)[0]
            title = title.replace('_', ' ').replace('-', ' ')
            title = ' '.join(title.split())
        
        print(f"📤 Received file upload: {file.filename} ({len(content)} bytes)")
        
    else:
        # Download from URL
        print(f"📥 Downloading PDF from: {pdf_url}")
        try:
            response = requests.get(pdf_url, timeout=120)
            response.raise_for_status()
            content = response.content
            
            with open(input_path, "wb") as f:
                f.write(content)
            
            print(f"   ✅ Downloaded {len(content)} bytes")
            
            # Extract title from URL if not provided
            if not title:
                title = pdf_url.split('/')[-1].replace('.pdf', '').replace('_', ' ')
            
        except Exception as e:
            print(f"❌ Failed to download PDF: {e}")
            # If linked to pending book, mark as failed
            if pending_book_id:
                try:
                    db = get_database_service()
                    db.supabase.table("pending_books").update({"status": "failed"}).eq("id", pending_book_id).execute()
                except:
                    pass
            raise HTTPException(status_code=500, detail=f"Failed to download PDF: {e}")
    
    file_size = len(content)
    
    # Translate title to Vietnamese using Gemini
    bilingual_title = translate_title(title, target_language)
    
    # Auto-classify book category if not provided
    if not category:
        category = auto_classify_book(title)
    
    # Create book record in database
    db = get_database_service()
    book_data = {
        "id": job_id,
        "title": bilingual_title,
        "source_format": "pdf",
        "target_language": target_language,
        "file_size_bytes": file_size,
        "category": category
    }
    
    # Link to pending book if provided
    if pending_book_id:
        book_data["pending_book_id"] = pending_book_id
        # Update pending book status to translating
        db.supabase.table("pending_books").update({"status": "translating"}).eq("id", pending_book_id).execute()
        print(f"🔗 Linked to pending book: {pending_book_id}")
    
    db.create_book(**book_data)
    
    # Store job info in memory (for quick access)
    jobs_store[job_id] = {
        "id": job_id,
        "title": bilingual_title,
        "status": BookStatus.PENDING,
        "target_language": target_language,
        "file_size_bytes": file_size,
        "input_path": str(input_path),
        "output_dir": str(job_dir / "output"),
        "pending_book_id": pending_book_id,
    }
    
    # Start background translation
    background_tasks.add_task(
        run_translation_job,
        job_id=job_id,
        input_path=str(input_path),
        output_dir=str(job_dir / "output"),
        target_language=target_language,
        pending_book_id=pending_book_id  # Pass pending_book_id for status update
    )
    
    return TranslateResponse(
        id=job_id,
        status=BookStatus.PENDING,
        message=f"Translation started for '{bilingual_title}'. Poll /books/{{id}} for status."
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


@router.delete("/books/{book_id}")
async def delete_book(book_id: str, _admin = Depends(require_admin)):
    """Soft delete a book (admin only)"""
    from services.database_service import get_database_service
    db = get_database_service()
    
    result = db.soft_delete_book(book_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Also remove from in-memory store if exists
    if book_id in jobs_store:
        jobs_store[book_id]["is_deleted"] = True
    
    return {"message": f"Book {book_id} deleted successfully", "data": result}


@router.post("/books/{book_id}/restore")
async def restore_book(book_id: str, _admin = Depends(require_admin)):
    """Restore a soft-deleted book (admin only)"""
    from services.database_service import get_database_service
    db = get_database_service()
    
    result = db.restore_book(book_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Also restore in in-memory store if exists
    if book_id in jobs_store:
        jobs_store[book_id]["is_deleted"] = False
    
    return {"message": f"Book {book_id} restored successfully", "data": result}


async def run_translation_job(
    job_id: str, 
    input_path: str, 
    output_dir: str, 
    target_language: str,
    pending_book_id: Optional[str] = None
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
        from translator.extractor import extract_pdf_to_markdown, extract_cover_image
        from translator.ai_translator import translate_markdown
        from translator.builder import build_epub, build_html, build_pdf
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Step 1: Extract PDF to Markdown
        md_content = extract_pdf_to_markdown(input_path, output_dir)
        
        # Step 1.5: Extract cover image from first page
        final_dir = Path(output_dir) / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        cover_path = str(final_dir / "cover.png")
        extract_cover_image(input_path, cover_path)
        
        # Step 2: Translate Markdown
        translated_content = translate_markdown(md_content, output_dir=output_dir)
        
        # Step 3: Build outputs
        translated_md_path = Path(output_dir) / "temp_md" / "translated.md"
        
        epub_path = str(final_dir / "result.epub")
        html_path = str(final_dir / "result.html")
        translated_pdf_path = str(final_dir / "translated.pdf")
        
        build_epub(str(translated_md_path), epub_path, output_dir + "/")
        build_html(str(translated_md_path), html_path, output_dir + "/")
        
        
        # PDF build disabled - too slow and often fails due to LaTeX requirements
        # EPUB and HTML are sufficient for reading
        translated_pdf_path = None
        print("📄 PDF generation skipped (disabled for performance)")
        
        # Step 4: Upload cover and images first
        gcs_prefix = f"books/{job_id}/"
        
        # Upload original PDF source
        pdf_url = None
        if Path(input_path).exists():
            pdf_url = storage.upload_file(input_path, f"{gcs_prefix}source.pdf")
            print(f"📄 Original PDF uploaded: {pdf_url}")
        
        # Upload cover image
        cover_url = None
        if Path(cover_path).exists():
            cover_url = storage.upload_file(cover_path, f"{gcs_prefix}cover.png")
            print(f"📕 Cover uploaded: {cover_url}")
        
        # Upload images directory if exists
        images_dir = Path(output_dir) / "images"
        if images_dir.exists():
            storage.upload_directory(str(images_dir), f"{gcs_prefix}images/")
        
        # Get Supabase base URL for images
        supabase_images_base = storage.get_public_url(f"{gcs_prefix}images/")
        
        # Fix image paths in HTML before uploading
        import re
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Replace various image path patterns with Supabase URLs
        # Pattern 1: src="images/xxx.png"
        html_content = re.sub(
            r'src="\.?/?images/',
            f'src="{supabase_images_base}',
            html_content
        )
        # Pattern 2: src="./images/xxx.png"
        html_content = re.sub(
            r'src="\./images/',
            f'src="{supabase_images_base}',
            html_content
        )
        # Pattern 3: Absolute local paths
        html_content = re.sub(
            r'src="[^"]*[/\\]images[/\\]',
            f'src="{supabase_images_base}',
            html_content
        )
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"🖼️ Fixed image paths in HTML with base: {supabase_images_base}")
        
        # Step 5: Upload HTML, EPUB and translated PDF
        html_url = storage.upload_file(html_path, f"{gcs_prefix}result.html")
        epub_url = storage.upload_file(epub_path, f"{gcs_prefix}result.epub")
        
        # Upload translated PDF if generated successfully
        translated_pdf_url = None
        if translated_pdf_path and Path(translated_pdf_path).exists():
            translated_pdf_url = storage.upload_file(translated_pdf_path, f"{gcs_prefix}translated.pdf")
            print(f"📄 Translated PDF uploaded: {translated_pdf_url}")
        
        # Step 6: Save to database (use translated_pdf_url if available, fallback to source pdf_url)
        final_pdf_url = translated_pdf_url if translated_pdf_url else pdf_url
        db.save_book_urls(job_id, html_url=html_url, epub_url=epub_url, cover_url=cover_url, pdf_url=final_pdf_url)
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
        
        # Update pending book status if linked
        if pending_book_id:
            db.supabase.table("pending_books").update({"status": "completed"}).eq("id", pending_book_id).execute()
            print(f"✅ Pending book {pending_book_id} marked as completed")
        
        print(f"✅ Translation complete for job {job_id}")
        
    except Exception as e:
        print(f"❌ Translation failed for job {job_id}: {e}")
        import traceback
        traceback.print_exc()
        
        jobs_store[job_id].update({
            "status": BookStatus.FAILED,
            "error_message": str(e)
        })
        db.update_book_status(job_id, "failed", error_message=str(e))
        
        # Update pending book status if linked
        if pending_book_id:
            db.supabase.table("pending_books").update({"status": "failed"}).eq("id", pending_book_id).execute()
            print(f"❌ Pending book {pending_book_id} marked as failed")
