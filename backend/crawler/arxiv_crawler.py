"""
Poker Research Crawler
Crawls legal, public domain poker research from arXiv and other sources
"""

import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import time
import json
import os

# arXiv API base URL
ARXIV_API = "http://export.arxiv.org/api/query"

# Poker/Game Theory search queries
SEARCH_QUERIES = [
    "poker artificial intelligence",
    "poker game theory",
    "poker Nash equilibrium", 
    "Texas Holdem AI",
    "no-limit poker solver",
    "poker CFR counterfactual regret",
    "Libratus poker",
    "Pluribus poker",
    "DeepStack poker",
    "imperfect information games poker",
    "GTO poker strategy",
]

class ArxivCrawler:
    def __init__(self, output_dir: str = "crawler_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.papers_dir = self.output_dir / "papers"
        self.papers_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.output_dir / "papers_metadata.json"
        self.papers = self._load_metadata()
    
    def _load_metadata(self) -> dict:
        """Load existing metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.papers, f, indent=2, ensure_ascii=False)
    
    def search_arxiv(self, query: str, max_results: int = 10) -> list:
        """
        Search arXiv for papers matching the query
        """
        print(f"🔍 Searching arXiv for: {query}")
        
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        try:
            response = requests.get(ARXIV_API, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            papers = []
            for entry in root.findall("atom:entry", ns):
                paper = {
                    "id": entry.find("atom:id", ns).text.split("/abs/")[-1],
                    "title": entry.find("atom:title", ns).text.strip().replace("\n", " "),
                    "summary": entry.find("atom:summary", ns).text.strip(),
                    "authors": [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)],
                    "published": entry.find("atom:published", ns).text,
                    "updated": entry.find("atom:updated", ns).text,
                    "pdf_url": None,
                    "category": "ai_research",
                    "source": "arxiv"
                }
                
                # Get PDF link
                for link in entry.findall("atom:link", ns):
                    if link.get("title") == "pdf":
                        paper["pdf_url"] = link.get("href")
                        break
                
                papers.append(paper)
            
            print(f"   Found {len(papers)} papers")
            return papers
            
        except Exception as e:
            print(f"❌ Error searching arXiv: {e}")
            return []
    
    def download_paper(self, paper: dict) -> str | None:
        """
        Download PDF of a paper
        """
        if not paper.get("pdf_url"):
            print(f"⚠️ No PDF URL for: {paper['title'][:50]}...")
            return None
        
        paper_id = paper["id"].replace("/", "_")
        pdf_path = self.papers_dir / f"{paper_id}.pdf"
        
        # Skip if already downloaded
        if pdf_path.exists():
            print(f"⏭️ Already downloaded: {paper_id}")
            return str(pdf_path)
        
        print(f"📥 Downloading: {paper['title'][:50]}...")
        
        try:
            response = requests.get(paper["pdf_url"], timeout=60)
            response.raise_for_status()
            
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            
            print(f"   ✅ Saved: {pdf_path}")
            return str(pdf_path)
            
        except Exception as e:
            print(f"   ❌ Error downloading: {e}")
            return None
    
    def crawl_all(self, max_per_query: int = 5, download_pdfs: bool = True):
        """
        Crawl all queries and optionally download PDFs
        """
        print("=" * 60)
        print("🚀 Starting Poker Research Crawler")
        print("=" * 60)
        
        all_papers = []
        seen_ids = set(self.papers.keys())
        
        for query in SEARCH_QUERIES:
            papers = self.search_arxiv(query, max_results=max_per_query)
            
            for paper in papers:
                if paper["id"] not in seen_ids:
                    all_papers.append(paper)
                    seen_ids.add(paper["id"])
            
            # Respect arXiv rate limit (3 seconds between requests)
            time.sleep(3)
        
        print(f"\n📊 Found {len(all_papers)} unique new papers")
        
        # Download PDFs if requested
        downloaded = 0
        for paper in all_papers:
            if download_pdfs:
                pdf_path = self.download_paper(paper)
                if pdf_path:
                    paper["local_pdf"] = pdf_path
                    downloaded += 1
                time.sleep(1)  # Rate limit downloads
            
            # Save to metadata
            self.papers[paper["id"]] = paper
        
        self._save_metadata()
        
        print(f"\n✅ Crawl complete!")
        print(f"   Total papers in database: {len(self.papers)}")
        print(f"   PDFs downloaded this run: {downloaded}")
        print(f"   Metadata saved to: {self.metadata_file}")
        
        return all_papers
    
    def get_papers_for_translation(self) -> list:
        """
        Get papers that have been downloaded but not yet translated
        """
        papers_to_translate = []
        for paper_id, paper in self.papers.items():
            if paper.get("local_pdf") and not paper.get("translated"):
                papers_to_translate.append(paper)
        return papers_to_translate
    
    def list_papers(self):
        """Print list of all papers"""
        print(f"\n📚 Total papers: {len(self.papers)}")
        for i, (paper_id, paper) in enumerate(self.papers.items(), 1):
            status = "✅" if paper.get("local_pdf") else "❌"
            translated = "🌐" if paper.get("translated") else ""
            print(f"{i}. [{status}] {translated} {paper['title'][:60]}...")
            print(f"      Authors: {', '.join(paper['authors'][:3])}")


def main():
    """Main crawler function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Poker Research Crawler")
    parser.add_argument("--output", "-o", default="crawler_output", help="Output directory")
    parser.add_argument("--max", "-m", type=int, default=5, help="Max papers per query")
    parser.add_argument("--no-download", action="store_true", help="Don't download PDFs")
    parser.add_argument("--list", "-l", action="store_true", help="List all papers")
    
    args = parser.parse_args()
    
    crawler = ArxivCrawler(output_dir=args.output)
    
    if args.list:
        crawler.list_papers()
    else:
        crawler.crawl_all(
            max_per_query=args.max,
            download_pdfs=not args.no_download
        )


if __name__ == "__main__":
    main()
