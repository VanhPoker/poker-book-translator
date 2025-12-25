"""
Supabase Database Service
Handles book records in Supabase PostgreSQL
"""
import os
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Try to import supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ supabase not installed. Using in-memory storage fallback.")


class DatabaseService:
    """Service for handling database operations (Supabase or in-memory fallback)"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.in_memory_store: dict = {}
        
        if SUPABASE_AVAILABLE:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            
            if url and key:
                try:
                    self.supabase = create_client(url, key)
                    print(f"✅ Connected to Supabase")
                except Exception as e:
                    print(f"⚠️ Could not connect to Supabase: {e}")
                    print("   Using in-memory storage fallback.")
    
    def create_book(
        self,
        id: str,
        title: str,
        source_format: str = "pdf",
        target_language: str = "vi",
        file_size_bytes: int = 0
    ) -> dict:
        """Create a new book record"""
        book = {
            "id": id,
            "title": title,
            "status": "pending",
            "source_format": source_format,
            "target_language": target_language,
            "file_size_bytes": file_size_bytes,
            "created_at": datetime.now().isoformat()
        }
        
        if self.supabase:
            try:
                print(f"📝 Creating book record: {id}")
                result = self.supabase.table("translated_books").insert(book).execute()
                print(f"✅ Book created successfully: {result.data}")
                return result.data[0] if result.data else book
            except Exception as e:
                print(f"❌ Failed to create book in Supabase: {e}")
                print(f"   Book data: {book}")
                # Fall back to in-memory
                self.in_memory_store[id] = book
                return book
        else:
            self.in_memory_store[id] = book
            return book
    
    def update_book_status(
        self, 
        id: str, 
        status: str,
        error_message: Optional[str] = None
    ) -> dict:
        """Update book status"""
        update_data = {"status": status}
        
        if error_message:
            update_data["error_message"] = error_message
        
        if status == "completed":
            update_data["completed_at"] = datetime.now().isoformat()
        
        if self.supabase:
            try:
                print(f"📝 Updating book status: {id} -> {status}")
                result = self.supabase.table("translated_books").update(update_data).eq("id", id).execute()
                print(f"✅ Status updated: {result.data}")
                return result.data[0] if result.data else {}
            except Exception as e:
                print(f"❌ Failed to update status in Supabase: {e}")
                return {}
        else:
            if id in self.in_memory_store:
                self.in_memory_store[id].update(update_data)
                return self.in_memory_store[id]
            return {}
    
    def save_book_urls(
        self,
        id: str,
        html_url: Optional[str] = None,
        epub_url: Optional[str] = None,
        pdf_url: Optional[str] = None
    ) -> dict:
        """Save output URLs for a book"""
        update_data = {}
        if html_url:
            update_data["html_url"] = html_url
        if epub_url:
            update_data["epub_url"] = epub_url
        if pdf_url:
            update_data["pdf_url"] = pdf_url
        
        if self.supabase:
            try:
                print(f"📝 Saving URLs for book: {id}")
                print(f"   URLs: {update_data}")
                result = self.supabase.table("translated_books").update(update_data).eq("id", id).execute()
                print(f"✅ URLs saved: {result.data}")
                return result.data[0] if result.data else {}
            except Exception as e:
                print(f"❌ Failed to save URLs in Supabase: {e}")
                return {}
        else:
            if id in self.in_memory_store:
                self.in_memory_store[id].update(update_data)
                return self.in_memory_store[id]
            return {}
    
    def save_token_usage(
        self,
        id: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float
    ) -> dict:
        """Save token usage for a book"""
        update_data = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": estimated_cost
        }
        
        if self.supabase:
            result = self.supabase.table("translated_books").update(update_data).eq("id", id).execute()
            return result.data[0] if result.data else {}
        else:
            if id in self.in_memory_store:
                self.in_memory_store[id].update(update_data)
                return self.in_memory_store[id]
            return {}
    
    def get_book(self, id: str) -> Optional[dict]:
        """Get a book by ID"""
        if self.supabase:
            result = self.supabase.table("translated_books").select("*").eq("id", id).execute()
            return result.data[0] if result.data else None
        else:
            return self.in_memory_store.get(id)
    
    def list_books(self, limit: int = 50) -> List[dict]:
        """List all books"""
        if self.supabase:
            result = self.supabase.table("translated_books").select("*").order("created_at", desc=True).limit(limit).execute()
            return result.data or []
        else:
            return list(self.in_memory_store.values())


# Singleton instance
_db_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Get or create database service instance"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
