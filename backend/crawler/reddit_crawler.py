"""
Reddit Poker Crawler
Crawls top posts and guides from r/poker subreddit
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import time


class RedditPokerCrawler:
    def __init__(self, output_dir: str = "crawler_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.output_dir / "reddit_posts.json"
        self.posts = self._load_metadata()
        
        # Reddit API endpoints (no auth required for public data)
        self.base_url = "https://www.reddit.com"
        self.headers = {
            "User-Agent": "PokerLibraryCrawler/1.0"
        }
    
    def _load_metadata(self) -> dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.posts, f, indent=2, ensure_ascii=False)
    
    def get_top_posts(self, subreddit: str = "poker", time_filter: str = "all", limit: int = 100) -> list:
        """
        Get top posts from a subreddit
        time_filter: hour, day, week, month, year, all
        """
        print(f"📥 Fetching top posts from r/{subreddit}...")
        
        url = f"{self.base_url}/r/{subreddit}/top.json"
        params = {
            "t": time_filter,
            "limit": min(limit, 100)  # Reddit caps at 100 per request
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for item in data["data"]["children"]:
                post = item["data"]
                
                # Only include text posts with significant content
                if post.get("is_self") and post.get("selftext") and len(post["selftext"]) > 500:
                    posts.append({
                        "id": post["id"],
                        "title": post["title"],
                        "content": post["selftext"],
                        "author": post["author"],
                        "score": post["score"],
                        "num_comments": post["num_comments"],
                        "url": f"https://reddit.com{post['permalink']}",
                        "created_utc": post["created_utc"],
                        "subreddit": subreddit,
                        "flair": post.get("link_flair_text"),
                        "category": "general",
                        "source": "reddit"
                    })
            
            print(f"   Found {len(posts)} quality posts")
            return posts
            
        except Exception as e:
            print(f"❌ Error fetching Reddit: {e}")
            return []
    
    def search_subreddit(self, subreddit: str, query: str, limit: int = 50) -> list:
        """Search subreddit for specific topics"""
        print(f"🔍 Searching r/{subreddit} for: {query}")
        
        url = f"{self.base_url}/r/{subreddit}/search.json"
        params = {
            "q": query,
            "restrict_sr": "true",
            "sort": "top",
            "limit": limit
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for item in data["data"]["children"]:
                post = item["data"]
                if post.get("is_self") and post.get("selftext") and len(post["selftext"]) > 300:
                    posts.append({
                        "id": post["id"],
                        "title": post["title"],
                        "content": post["selftext"],
                        "author": post["author"],
                        "score": post["score"],
                        "num_comments": post["num_comments"],
                        "url": f"https://reddit.com{post['permalink']}",
                        "created_utc": post["created_utc"],
                        "subreddit": subreddit,
                        "category": self._categorize_post(post["title"], query),
                        "source": "reddit"
                    })
            
            return posts
            
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return []
    
    def _categorize_post(self, title: str, query: str) -> str:
        """Auto-categorize post based on content"""
        title_lower = title.lower()
        
        if any(x in title_lower for x in ["gto", "solver", "pio", "optimal"]):
            return "ai_research"
        elif any(x in title_lower for x in ["nlh", "no limit", "holdem"]):
            return "nlh"
        elif "omaha" in title_lower:
            return "omaha"
        elif any(x in title_lower for x in ["tilt", "mental", "psychology", "emotion"]):
            return "psychology"
        else:
            return "general"
    
    def crawl_all(self):
        """Crawl all poker content from Reddit"""
        print("=" * 60)
        print("🚀 Starting Reddit Poker Crawler")
        print("=" * 60)
        
        subreddits = ["poker", "pokerstrategy"]
        search_terms = [
            "strategy guide",
            "beginner tips",
            "GTO",
            "hand analysis",
            "mental game",
            "bankroll management",
            "tournament strategy",
            "cash game strategy"
        ]
        
        all_posts = []
        seen_ids = set(self.posts.keys())
        
        # Get top posts from each subreddit
        for sub in subreddits:
            posts = self.get_top_posts(sub, time_filter="all", limit=100)
            for post in posts:
                if post["id"] not in seen_ids:
                    all_posts.append(post)
                    seen_ids.add(post["id"])
            time.sleep(2)  # Rate limit
        
        # Search for specific topics
        for term in search_terms:
            posts = self.search_subreddit("poker", term, limit=25)
            for post in posts:
                if post["id"] not in seen_ids:
                    all_posts.append(post)
                    seen_ids.add(post["id"])
            time.sleep(2)  # Rate limit
        
        # Save all new posts
        for post in all_posts:
            self.posts[post["id"]] = post
        
        self._save_metadata()
        
        print(f"\n✅ Crawl complete!")
        print(f"   New posts found: {len(all_posts)}")
        print(f"   Total posts in database: {len(self.posts)}")
        
        return all_posts
    
    def export_for_translation(self) -> list:
        """Export posts as markdown files for translation"""
        export_dir = self.output_dir / "reddit_articles"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        exported = []
        for post_id, post in self.posts.items():
            if post.get("exported"):
                continue
            
            md_content = f"""# {post['title']}

**Author:** u/{post['author']}  
**Score:** {post['score']} upvotes  
**Source:** [Reddit]({post['url']})

---

{post['content']}
"""
            
            filename = f"{post_id}_{post['title'][:40].replace(' ', '_')}.md"
            filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            
            filepath = export_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            post["exported"] = True
            post["export_path"] = str(filepath)
            exported.append(post)
        
        self._save_metadata()
        print(f"📁 Exported {len(exported)} posts to {export_dir}")
        return exported


def main():
    crawler = RedditPokerCrawler()
    crawler.crawl_all()


if __name__ == "__main__":
    main()
