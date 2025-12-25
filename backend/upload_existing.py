"""
Script to upload existing translated files to Supabase Storage
Run after fixing RLS policies in Supabase
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Import services
from services.storage_service import get_storage_service
from services.database_service import get_database_service

def upload_existing_job(job_id: str, title: str = "Translated Book"):
    """Upload files from an existing translation job to Supabase Storage"""
    
    job_dir = Path(f"temp_jobs/{job_id}/output/final")
    
    if not job_dir.exists():
        print(f"❌ Job directory not found: {job_dir}")
        return
    
    storage = get_storage_service()
    db = get_database_service()
    
    print(f"📦 Storage provider: {storage.provider}")
    
    if storage.provider == "local":
        print("❌ No cloud storage configured. Check your .env file!")
        return
    
    # Create book record in database first
    print(f"📝 Creating database record...")
    try:
        db.create_book(job_id, title, source_format="pdf", target_language="vi")
        db.update_book_status(job_id, "processing")
    except Exception as e:
        print(f"⚠️ Database create error (may already exist): {e}")
    
    gcs_prefix = f"books/{job_id}/"
    html_url = None
    epub_url = None
    
    # Upload HTML
    html_path = job_dir / "result.html"
    if html_path.exists():
        print(f"⬆️ Uploading HTML...")
        html_url = storage.upload_file(str(html_path), f"{gcs_prefix}result.html")
        print(f"✅ HTML: {html_url}")
    
    # Upload EPUB
    epub_path = job_dir / "result.epub"
    if epub_path.exists():
        print(f"⬆️ Uploading EPUB...")
        epub_url = storage.upload_file(str(epub_path), f"{gcs_prefix}result.epub")
        print(f"✅ EPUB: {epub_url}")
    
    # Upload images if exist
    images_dir = Path(f"temp_jobs/{job_id}/output/images")
    if images_dir.exists():
        print(f"⬆️ Uploading images...")
        image_urls = storage.upload_directory(str(images_dir), f"{gcs_prefix}images/")
        print(f"✅ Uploaded {len(image_urls)} images")
    
    # Save URLs to database
    print(f"💾 Saving URLs to database...")
    try:
        db.save_book_urls(job_id, html_url=html_url, epub_url=epub_url)
        db.update_book_status(job_id, "completed")
        print(f"✅ Database updated!")
    except Exception as e:
        print(f"❌ Database save error: {e}")
    
    print(f"\n🎉 Upload complete!")
    print(f"   HTML: {html_url}")
    print(f"   EPUB: {epub_url}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
    else:
        # Default to the last job
        job_id = "5f1627fd-9450-4991-8a16-405d72abc71e"
    
    title = "The Theory of Poker"
    
    print(f"📤 Uploading job: {job_id}")
    upload_existing_job(job_id, title)
