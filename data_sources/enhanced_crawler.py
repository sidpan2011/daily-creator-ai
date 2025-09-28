"""
Enhanced Web Crawler for Niche, Specific Content
Fetches current, relevant content from multiple sources
"""
import asyncio
import httpx
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
import re

class EnhancedWebCrawler:
    def __init__(self):
        self.sources = {
            "github_trending": "https://github.com/trending",
            "product_hunt": "https://www.producthunt.com/",
            "dev_to": "https://dev.to/api/articles",
            "reddit_programming": "https://www.reddit.com/r/programming/hot.json",
            "reddit_machinelearning": "https://www.reddit.com/r/MachineLearning/hot.json",
            "reddit_webdev": "https://www.reddit.com/r/webdev/hot.json",
            "reddit_startups": "https://www.reddit.com/r/startups/hot.json"
        }
    
    async def crawl_comprehensive_content(self, user_interests: List[str]) -> Dict[str, Any]:
        """Crawl multiple sources for comprehensive, current content"""
        print("🕷️ Enhanced web crawling for niche content...")
        
        crawled_data = {
            "timestamp": datetime.now().isoformat(),
            "sources_crawled": [],
            "content_by_interest": {},
            "fresh_updates": []
        }
        
        try:
            # Crawl each source
            tasks = [
                self._crawl_dev_to(user_interests),
                self._crawl_reddit_sources(user_interests),
                self._crawl_product_hunt(user_interests)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"⚠️ Crawling task {i} failed: {result}")
                else:
                    crawled_data.update(result)
            
            # Filter for freshness (last 7 days)
            crawled_data["fresh_updates"] = self._filter_fresh_content(crawled_data.get("fresh_updates", []))
            
            print(f"✅ Crawled {len(crawled_data['fresh_updates'])} fresh updates from {len(crawled_data['sources_crawled'])} sources")
            return crawled_data
            
        except Exception as e:
            print(f"❌ Enhanced crawling failed: {e}")
            return crawled_data
    
    async def _crawl_dev_to(self, user_interests: List[str]) -> Dict[str, Any]:
        """Crawl Dev.to for current articles"""
        try:
            print("  📝 Crawling Dev.to for current articles...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get recent articles
                response = await client.get(
                    "https://dev.to/api/articles",
                    params={
                        "per_page": 30,
                        "top": 7  # Last 7 days
                    }
                )
                
                if response.status_code == 200:
                    articles = response.json()
                    relevant_articles = []
                    
                    for article in articles:
                        # Check relevance to user interests
                        relevance_score = self._calculate_relevance(article, user_interests)
                        if relevance_score > 0.3:
                            relevant_articles.append({
                                "title": article["title"],
                                "description": article["description"],
                                "url": article["url"],
                                "published_at": article["published_at"],
                                "tags": article.get("tag_list", []),
                                "relevance_score": relevance_score,
                                "source": "dev.to",
                                "author": article["user"]["name"]
                            })
                    
                    print(f"    ✅ Found {len(relevant_articles)} relevant Dev.to articles")
                    return {
                        "sources_crawled": ["dev.to"],
                        "fresh_updates": relevant_articles
                    }
                    
        except Exception as e:
            print(f"    ❌ Dev.to crawling failed: {e}")
            return {}
    
    async def _crawl_reddit_sources(self, user_interests: List[str]) -> Dict[str, Any]:
        """Crawl Reddit sources for current discussions"""
        try:
            print("  🔴 Crawling Reddit for current discussions...")
            
            reddit_sources = [
                ("programming", "https://www.reddit.com/r/programming/hot.json"),
                ("MachineLearning", "https://www.reddit.com/r/MachineLearning/hot.json"),
                ("webdev", "https://www.reddit.com/r/webdev/hot.json"),
                ("startups", "https://www.reddit.com/r/startups/hot.json"),
                ("web3", "https://www.reddit.com/r/web3/hot.json")
            ]
            
            all_posts = []
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for subreddit, url in reddit_sources:
                    try:
                        response = await client.get(url, headers={"User-Agent": "Persnally-Crawler/1.0"})
                        
                        if response.status_code == 200:
                            data = response.json()
                            posts = data.get("data", {}).get("children", [])
                            
                            for post in posts[:10]:  # Top 10 from each
                                post_data = post["data"]
                                relevance_score = self._calculate_relevance(post_data, user_interests)
                                
                                if relevance_score > 0.4:
                                    all_posts.append({
                                        "title": post_data["title"],
                                        "description": post_data.get("selftext", "")[:500],
                                        "url": f"https://reddit.com{post_data['permalink']}",
                                        "created_utc": post_data["created_utc"],
                                        "score": post_data["score"],
                                        "num_comments": post_data["num_comments"],
                                        "relevance_score": relevance_score,
                                        "source": f"reddit/r/{subreddit}",
                                        "subreddit": subreddit
                                    })
                        
                        await asyncio.sleep(0.5)  # Rate limiting
                        
                    except Exception as e:
                        print(f"    ⚠️ Reddit r/{subreddit} failed: {e}")
                        continue
            
            print(f"    ✅ Found {len(all_posts)} relevant Reddit posts")
            return {
                "sources_crawled": ["reddit"],
                "fresh_updates": all_posts
            }
            
        except Exception as e:
            print(f"    ❌ Reddit crawling failed: {e}")
            return {}
    
    async def _crawl_product_hunt(self, user_interests: List[str]) -> Dict[str, Any]:
        """Crawl Product Hunt for new tools and products"""
        try:
            print("  🚀 Crawling Product Hunt for new tools...")
            
            # Note: Product Hunt doesn't have a public API, so we'll simulate
            # In a real implementation, you'd use their API or scrape carefully
            
            # For now, return empty - in production you'd implement proper scraping
            return {
                "sources_crawled": ["product_hunt"],
                "fresh_updates": []
            }
            
        except Exception as e:
            print(f"    ❌ Product Hunt crawling failed: {e}")
            return {}
    
    def _calculate_relevance(self, content: Dict[str, Any], user_interests: List[str]) -> float:
        """Calculate relevance score for content based on user interests"""
        score = 0.0
        
        # Check title and description
        text_to_check = f"{content.get('title', '')} {content.get('description', '')} {content.get('selftext', '')}"
        text_lower = text_to_check.lower()
        
        # Check tags
        tags = content.get('tag_list', []) or content.get('tags', [])
        if isinstance(tags, list):
            text_lower += " " + " ".join(tags).lower()
        
        # Score based on interest matches
        for interest in user_interests:
            interest_lower = interest.lower()
            if interest_lower in text_lower:
                score += 0.3
            
            # Check for related keywords
            related_keywords = self._get_related_keywords(interest_lower)
            for keyword in related_keywords:
                if keyword in text_lower:
                    score += 0.1
        
        return min(score, 1.0)
    
    def _get_related_keywords(self, interest: str) -> List[str]:
        """Get related keywords for an interest"""
        keyword_map = {
            "ai/ml development": ["ai", "ml", "machine learning", "artificial intelligence", "deep learning", "neural network"],
            "web3 and blockchain": ["web3", "blockchain", "crypto", "defi", "nft", "ethereum", "smart contract"],
            "developer productivity tools": ["productivity", "tools", "automation", "workflow", "efficiency", "dev tools"],
            "startup building": ["startup", "entrepreneur", "founder", "funding", "vc", "business", "launch"],
            "open source projects": ["open source", "oss", "github", "contribute", "community", "free software"],
            "technical writing": ["writing", "blog", "documentation", "tutorial", "guide", "article"],
            "indie hacking": ["indie", "hacker", "maker", "side project", "bootstrapping", "solo"],
            "saas development": ["saas", "software as a service", "subscription", "recurring revenue", "mrr"]
        }
        
        return keyword_map.get(interest, [])
    
    def _filter_fresh_content(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter content to only include items from last 7 days"""
        fresh_content = []
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for item in content_list:
            try:
                # Handle different date formats
                if "published_at" in item:
                    published_date = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
                elif "created_utc" in item:
                    published_date = datetime.fromtimestamp(item["created_utc"])
                else:
                    continue
                
                if published_date >= cutoff_date:
                    fresh_content.append(item)
                    
            except Exception as e:
                print(f"⚠️ Date parsing failed for item: {e}")
                continue
        
        # Sort by relevance score
        fresh_content.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        print(f"🕒 Filtered to {len(fresh_content)} fresh updates from last 7 days")
        return fresh_content
