"""
Import crawled papers from arxiv to pending_books queue
"""

import json
from pathlib import Path
import os
import uuid
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def main():
    # Load crawled papers
    metadata_file = Path('crawler_output/papers_metadata.json')
    if not metadata_file.exists():
        print('❌ No crawled papers found at crawler_output/papers_metadata.json')
        return

    with open(metadata_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    print(f'📚 Found {len(papers)} crawled papers')

    # Connect to Supabase
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print('❌ SUPABASE_URL or SUPABASE_KEY not set')
        return
    
    supabase = create_client(url, key)

    # Add each paper to pending_books
    added = 0
    skipped = 0
    
    for paper_id, paper in papers.items():
        if not paper.get('pdf_url'):
            continue
        
        # Check if already in queue
        try:
            existing = supabase.table('pending_books').select('id').eq('source_id', paper_id).execute()
            if existing.data:
                print(f'⏭️  Skipped (exists): {paper["title"][:40]}...')
                skipped += 1
                continue
        except:
            pass
        
        data = {
            'id': str(uuid.uuid4()),
            'title': paper['title'][:200],
            'original_title': paper['title'][:200],
            'pdf_url': paper['pdf_url'],
            'source': 'arxiv',
            'source_id': paper_id,
            'category': 'ai_research',
            'priority': 0,
            'status': 'pending',
            'metadata': {
                'authors': paper.get('authors', [])[:5],
                'published': paper.get('published', ''),
            }
        }
        
        try:
            supabase.table('pending_books').insert(data).execute()
            added += 1
            print(f'✅ Added: {paper["title"][:50]}...')
        except Exception as e:
            print(f'❌ Error adding {paper_id}: {e}')

    print(f'\n{"="*50}')
    print(f'📊 Import complete!')
    print(f'   Added: {added}')
    print(f'   Skipped: {skipped}')
    print(f'{"="*50}')


if __name__ == '__main__':
    main()
