"""
Poker Content Crawler - Main Manager
Orchestrates all crawlers and integrates with translation pipeline
"""

import argparse
from pathlib import Path
import json
from typing import Optional

from crawler.arxiv_crawler import ArxivCrawler
from crawler.reddit_crawler import RedditPokerCrawler


class CrawlerManager:
    """Manages all content crawlers and translation integration"""
    
    def __init__(self, output_dir: str = "crawler_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.arxiv = ArxivCrawler(str(self.output_dir / "arxiv"))
        self.reddit = RedditPokerCrawler(str(self.output_dir / "reddit"))
    
    def crawl_all(self, sources: Optional[list] = None):
        """
        Crawl all sources or specific ones
        sources: list of ["arxiv", "reddit"] or None for all
        """
        print("=" * 70)
        print("🌐 POKER CONTENT CRAWLER")
        print("   Crawling legal, public poker research and articles")
        print("=" * 70)
        
        results = {}
        
        if sources is None or "arxiv" in sources:
            print("\n📚 ARXIV RESEARCH PAPERS")
            print("-" * 50)
            results["arxiv"] = self.arxiv.crawl_all(max_per_query=5, download_pdfs=True)
        
        if sources is None or "reddit" in sources:
            print("\n📱 REDDIT POSTS")
            print("-" * 50)
            results["reddit"] = self.reddit.crawl_all()
        
        self._print_summary(results)
        return results
    
    def _print_summary(self, results: dict):
        """Print crawl summary"""
        print("\n" + "=" * 70)
        print("📊 CRAWL SUMMARY")
        print("=" * 70)
        
        total = 0
        for source, items in results.items():
            count = len(items)
            total += count
            print(f"   {source.upper()}: {count} items")
        
        print(f"\n   TOTAL NEW CONTENT: {total}")
        print(f"   Output directory: {self.output_dir}")
    
    def get_pending_translations(self) -> dict:
        """Get all content that hasn't been translated yet"""
        pending = {
            "arxiv": [],
            "reddit": []
        }
        
        # arXiv papers with downloaded PDFs
        for paper_id, paper in self.arxiv.papers.items():
            if paper.get("local_pdf") and not paper.get("translated"):
                pending["arxiv"].append(paper)
        
        # Reddit posts that are exported
        for post_id, post in self.reddit.posts.items():
            if post.get("export_path") and not post.get("translated"):
                pending["reddit"].append(post)
        
        return pending
    
    def list_all(self):
        """List all crawled content"""
        print("\n📚 ARXIV PAPERS:")
        self.arxiv.list_papers()
        
        print("\n\n📱 REDDIT POSTS:")
        print(f"Total posts: {len(self.reddit.posts)}")
        for i, (post_id, post) in enumerate(list(self.reddit.posts.items())[:10], 1):
            print(f"{i}. [{post['score']}⬆] {post['title'][:60]}...")
        if len(self.reddit.posts) > 10:
            print(f"   ... and {len(self.reddit.posts) - 10} more")


def main():
    parser = argparse.ArgumentParser(description="Poker Content Crawler Manager")
    parser.add_argument("--output", "-o", default="crawler_output", help="Output directory")
    parser.add_argument("--source", "-s", choices=["arxiv", "reddit", "all"], default="all", 
                       help="Source to crawl")
    parser.add_argument("--list", "-l", action="store_true", help="List all content")
    parser.add_argument("--pending", "-p", action="store_true", help="Show pending translations")
    
    args = parser.parse_args()
    
    manager = CrawlerManager(output_dir=args.output)
    
    if args.list:
        manager.list_all()
    elif args.pending:
        pending = manager.get_pending_translations()
        print(f"Pending arXiv translations: {len(pending['arxiv'])}")
        print(f"Pending Reddit translations: {len(pending['reddit'])}")
    else:
        sources = None if args.source == "all" else [args.source]
        manager.crawl_all(sources=sources)


if __name__ == "__main__":
    main()
