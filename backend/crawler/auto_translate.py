"""
Auto-translate crawled papers
Integrates crawler with translation pipeline and uploads to database
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from translator.extractor import extract_pdf_to_markdown
from translator.ai_translator import translate_markdown
from translator.builder import build_html, build_epub
from services.database_service import DatabaseService
from services.storage_service import StorageService


class AutoTranslator:
    """Auto-translate crawled papers and upload to library"""
    
    def __init__(self, crawler_output: str = "crawler_output"):
        self.crawler_output = Path(crawler_output)
        self.arxiv_dir = self.crawler_output / "arxiv"
        self.metadata_file = self.arxiv_dir / "papers_metadata.json"
        
        self.db = DatabaseService()
        self.storage = StorageService()
        
        self.papers = self._load_metadata()
    
    def _load_metadata(self) -> dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.papers, f, indent=2, ensure_ascii=False)
    
    def get_pending_papers(self) -> list:
        """Get papers that have PDFs but haven't been translated"""
        pending = []
        for paper_id, paper in self.papers.items():
            if paper.get("local_pdf") and not paper.get("translated"):
                pending.append(paper)
        return pending
    
    async def translate_paper(self, paper: dict) -> bool:
        """
        Translate a single paper and upload to library
        """
        paper_id = paper["id"].replace("/", "_")
        pdf_path = paper.get("local_pdf")
        
        if not pdf_path or not Path(pdf_path).exists():
            print(f"❌ PDF not found: {pdf_path}")
            return False
        
        print(f"\n{'=' * 60}")
        print(f"📄 Translating: {paper['title'][:60]}...")
        print(f"   Authors: {', '.join(paper['authors'][:3])}")
        print(f"{'=' * 60}")
        
        # Create job directory
        job_id = f"arxiv_{paper_id}_{uuid.uuid4().hex[:8]}"
        output_dir = Path("temp_jobs") / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Step 1: Extract PDF to Markdown
            print("📖 Extracting PDF to Markdown...")
            markdown_content = extract_pdf_to_markdown(pdf_path)
            
            if not markdown_content or len(markdown_content) < 100:
                print("❌ Failed to extract content from PDF")
                return False
            
            # Save original markdown
            md_path = output_dir / "original.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"   ✅ Extracted {len(markdown_content)} characters")
            
            # Step 2: Translate with AI
            print("🌐 Translating to Vietnamese...")
            translated_content = await translate_markdown(markdown_content, target_language="vi")
            
            if not translated_content:
                print("❌ Translation failed")
                return False
            
            # Save translated markdown
            translated_md_path = output_dir / "translated.md"
            with open(translated_md_path, "w", encoding="utf-8") as f:
                f.write(translated_content)
            print(f"   ✅ Translated {len(translated_content)} characters")
            
            # Step 3: Build HTML
            print("🔨 Building HTML...")
            html_path = output_dir / "translated.html"
            build_html(translated_content, str(html_path), paper["title"])
            
            # Step 4: Build EPUB
            print("📚 Building EPUB...")
            epub_path = output_dir / "translated.epub"
            build_epub(translated_content, str(epub_path), paper["title"])
            
            # Step 5: Create book in database
            print("💾 Saving to database...")
            book_id = job_id
            
            self.db.create_book(
                book_id=book_id,
                title=f"[Research] {paper['title']}",
                source_format="pdf",
                target_language="vi",
                file_size=Path(pdf_path).stat().st_size,
                category=paper.get("category", "ai_research")
            )
            
            # Step 6: Upload files to storage
            print("☁️ Uploading to storage...")
            
            # Upload HTML
            if html_path.exists():
                html_url = self.storage.upload_file(
                    str(html_path),
                    f"books/{book_id}/translated.html"
                )
                print(f"   HTML: {html_url}")
            
            # Upload EPUB
            if epub_path.exists():
                epub_url = self.storage.upload_file(
                    str(epub_path),
                    f"books/{book_id}/translated.epub"
                )
                print(f"   EPUB: {epub_url}")
            
            # Upload original PDF
            pdf_url = self.storage.upload_file(
                pdf_path,
                f"books/{book_id}/original.pdf"
            )
            print(f"   PDF: {pdf_url}")
            
            # Step 7: Update book record
            self.db.save_book_urls(
                book_id=book_id,
                html_url=html_url if html_path.exists() else None,
                epub_url=epub_url if epub_path.exists() else None,
                pdf_url=pdf_url
            )
            
            self.db.update_book_status(book_id, "completed")
            
            # Mark as translated in metadata
            paper["translated"] = True
            paper["translated_at"] = datetime.now().isoformat()
            paper["book_id"] = book_id
            self._save_metadata()
            
            print(f"✅ Successfully translated and uploaded!")
            return True
            
        except Exception as e:
            print(f"❌ Error translating paper: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def translate_all(self, limit: int = None):
        """Translate all pending papers"""
        pending = self.get_pending_papers()
        
        if limit:
            pending = pending[:limit]
        
        print(f"\n🚀 Starting auto-translation of {len(pending)} papers")
        
        success = 0
        failed = 0
        
        for paper in pending:
            try:
                result = await self.translate_paper(paper)
                if result:
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Error: {e}")
                failed += 1
        
        print(f"\n{'=' * 60}")
        print(f"📊 TRANSLATION COMPLETE")
        print(f"   Success: {success}")
        print(f"   Failed: {failed}")
        print(f"{'=' * 60}")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-translate crawled papers")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of papers to translate")
    parser.add_argument("--list", action="store_true", help="List pending papers")
    
    args = parser.parse_args()
    
    translator = AutoTranslator()
    
    if args.list:
        pending = translator.get_pending_papers()
        print(f"\n📋 Pending translations: {len(pending)}")
        for i, paper in enumerate(pending, 1):
            print(f"{i}. {paper['title'][:60]}...")
    else:
        await translator.translate_all(limit=args.limit)


if __name__ == "__main__":
    asyncio.run(main())
