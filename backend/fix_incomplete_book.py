"""
Script to complete an incomplete translation by uploading local files to Supabase
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Import after loading env
from services.database_service import get_database_service
from services.storage_service import get_storage_service

def complete_book(job_id: str):
    """Upload local files and mark book as completed"""
    
    db = get_database_service()
    storage = get_storage_service()
    
    # Check book exists
    book = db.get_book(job_id)
    if not book:
        print(f"❌ Book {job_id} not found")
        return
    
    print(f"📚 Found book: {book['title']}")
    print(f"   Current status: {book['status']}")
    
    # Check local files
    job_dir = Path(f"temp_jobs/{job_id}/output/final")
    
    html_path = job_dir / "result.html"
    epub_path = job_dir / "result.epub"
    cover_path = job_dir / "cover.png"
    pdf_path = job_dir / "translated.pdf"
    source_pdf = Path(f"temp_jobs/{job_id}/source.pdf")
    
    gcs_prefix = f"books/{job_id}/"
    
    # Upload files
    html_url = None
    epub_url = None
    cover_url = None
    pdf_url = None
    
    if html_path.exists():
        html_url = storage.upload_file(str(html_path), f"{gcs_prefix}result.html")
        print(f"✅ HTML uploaded: {html_url}")
    
    if epub_path.exists():
        epub_url = storage.upload_file(str(epub_path), f"{gcs_prefix}result.epub")
        print(f"✅ EPUB uploaded: {epub_url}")
    
    if cover_path.exists():
        cover_url = storage.upload_file(str(cover_path), f"{gcs_prefix}cover.png")
        print(f"✅ Cover uploaded: {cover_url}")
    
    if pdf_path.exists():
        pdf_url = storage.upload_file(str(pdf_path), f"{gcs_prefix}translated.pdf")
        print(f"✅ PDF uploaded: {pdf_url}")
    elif source_pdf.exists():
        pdf_url = storage.upload_file(str(source_pdf), f"{gcs_prefix}source.pdf")
        print(f"✅ Source PDF uploaded: {pdf_url}")
    
    # Upload images if exist
    images_dir = Path(f"temp_jobs/{job_id}/output/images")
    if images_dir.exists():
        storage.upload_directory(str(images_dir), f"{gcs_prefix}images/")
        print(f"✅ Images uploaded")
    
    # Update database
    db.save_book_urls(job_id, html_url=html_url, epub_url=epub_url, cover_url=cover_url, pdf_url=pdf_url)
    db.update_book_status(job_id, "completed")
    
    # Update pending book if linked
    pending_book_id = book.get('pending_book_id')
    if pending_book_id:
        db.supabase.table("pending_books").update({"status": "completed"}).eq("id", pending_book_id).execute()
        print(f"✅ Pending book {pending_book_id} marked as completed")
    
    print(f"\n🎉 Book {job_id} completed successfully!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
    else:
        job_id = "2c1893ac-8f18-4fdc-a36c-b6c028b78921"  # Default to current incomplete book
    
    complete_book(job_id)
