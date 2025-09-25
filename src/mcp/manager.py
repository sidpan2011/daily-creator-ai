"""
MCP Integration Manager for Daily Creator AI
Coordinates all MCP server connections and operations
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx
import os
from ..models.trending import TrendingContext, TrendingItem, TrendingSource

class MCPManager:
    """Manages all MCP server connections and operations"""
    
    def __init__(self):
        self.base_url = os.getenv("MCP_BASE_URL", "http://localhost:3000")
        self.timeout = 30.0
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def gather_trending_context(self) -> TrendingContext:
        """Gather trending data from all sources in parallel"""
        tasks = [
            self._fetch_github_trending(),
            self._fetch_hackernews_top(),
            self._fetch_producthunt_featured(),
            self._fetch_reddit_hot(),
            self._fetch_twitter_trending()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return TrendingContext(
            github_trending=results[0] if not isinstance(results[0], Exception) else [],
            hackernews_top=results[1] if not isinstance(results[1], Exception) else [],
            producthunt_featured=results[2] if not isinstance(results[2], Exception) else [],
            reddit_hot=results[3] if not isinstance(results[3], Exception) else [],
            twitter_trending=results[4] if not isinstance(results[4], Exception) else [],
            fetched_at=datetime.utcnow()
        )
    
    async def _fetch_github_trending(self) -> List[TrendingItem]:
        """Fetch trending repositories from GitHub"""
        try:
            # For demo purposes, return mock data
            # In production, this would call the GitHub MCP server
            return [
                TrendingItem(
                    title="Claude 3.5 Sonnet API",
                    description="Advanced AI model for creative and analytical tasks",
                    url="https://github.com/anthropics/claude-api",
                    source=TrendingSource.GITHUB,
                    score=95.0,
                    tags=["ai", "api", "anthropic"],
                    language="Python",
                    stars=15000,
                    created_at=datetime.utcnow() - timedelta(days=1)
                ),
                TrendingItem(
                    title="Resend Python SDK",
                    description="Email API for developers",
                    url="https://github.com/resend/resend-python",
                    source=TrendingSource.GITHUB,
                    score=88.0,
                    tags=["email", "api", "python"],
                    language="Python",
                    stars=2500,
                    created_at=datetime.utcnow() - timedelta(days=2)
                )
            ]
        except Exception as e:
            print(f"Error fetching GitHub trending: {e}")
            return []
    
    async def _fetch_hackernews_top(self) -> List[TrendingItem]:
        """Fetch top stories from Hacker News"""
        try:
            return [
                TrendingItem(
                    title="Building AI-Powered Personal Assistants",
                    description="How to create intelligent agents that understand context",
                    url="https://news.ycombinator.com/item?id=123456",
                    source=TrendingSource.HACKERNEWS,
                    score=92.0,
                    tags=["ai", "assistant", "automation"],
                    created_at=datetime.utcnow() - timedelta(hours=3)
                ),
                TrendingItem(
                    title="The Future of Email APIs",
                    description="Modern approaches to transactional and marketing emails",
                    url="https://news.ycombinator.com/item?id=123457",
                    source=TrendingSource.HACKERNEWS,
                    score=85.0,
                    tags=["email", "api", "future"],
                    created_at=datetime.utcnow() - timedelta(hours=5)
                )
            ]
        except Exception as e:
            print(f"Error fetching Hacker News: {e}")
            return []
    
    async def _fetch_producthunt_featured(self) -> List[TrendingItem]:
        """Fetch featured products from Product Hunt"""
        try:
            return [
                TrendingItem(
                    title="Daily Creator AI",
                    description="AI-powered personal curator for creators",
                    url="https://producthunt.com/posts/daily-creator-ai",
                    source=TrendingSource.PRODUCTHUNT,
                    score=90.0,
                    tags=["ai", "creator", "productivity"],
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
            ]
        except Exception as e:
            print(f"Error fetching Product Hunt: {e}")
            return []
    
    async def _fetch_reddit_hot(self) -> List[TrendingItem]:
        """Fetch hot posts from relevant subreddits"""
        try:
            return [
                TrendingItem(
                    title="Best AI Tools for Developers in 2024",
                    description="Comprehensive list of AI development tools",
                    url="https://reddit.com/r/MachineLearning/comments/123456",
                    source=TrendingSource.REDDIT,
                    score=87.0,
                    tags=["ai", "tools", "development"],
                    created_at=datetime.utcnow() - timedelta(hours=2)
                )
            ]
        except Exception as e:
            print(f"Error fetching Reddit: {e}")
            return []
    
    async def _fetch_twitter_trending(self) -> List[TrendingItem]:
        """Fetch trending topics from Twitter"""
        try:
            return [
                TrendingItem(
                    title="#AIDevelopment",
                    description="Latest trends in AI development and tools",
                    url="https://twitter.com/hashtag/AIDevelopment",
                    source=TrendingSource.TWITTER,
                    score=82.0,
                    tags=["ai", "development", "trending"],
                    created_at=datetime.utcnow() - timedelta(hours=1)
                )
            ]
        except Exception as e:
            print(f"Error fetching Twitter: {e}")
            return []
    
    async def send_email(self, to_email: str, subject: str, html_content: str, 
                        text_content: str) -> Dict[str, Any]:
        """Send email via Resend MCP"""
        try:
            # For demo purposes, simulate email sending
            # In production, this would call the Resend MCP server
            print(f"📧 Email sent to {to_email}")
            print(f"📧 Subject: {subject}")
            print(f"📧 Content preview: {html_content[:100]}...")
            
            return {
                "success": True,
                "message_id": f"msg_{datetime.utcnow().timestamp()}",
                "to": to_email,
                "subject": subject
            }
        except Exception as e:
            print(f"Error sending email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_github_data(self, username: str) -> Dict[str, Any]:
        """Get GitHub user data via GitHub MCP"""
        try:
            # For demo purposes, return mock data
            return {
                "username": username,
                "name": "Demo User",
                "bio": "Passionate developer building amazing things",
                "public_repos": 25,
                "followers": 150,
                "following": 200,
                "recent_repos": [
                    {"name": "awesome-project", "stars": 50, "language": "Python"},
                    {"name": "cool-tool", "stars": 25, "language": "JavaScript"}
                ],
                "languages": ["Python", "JavaScript", "TypeScript", "Go"],
                "interests": ["web-development", "ai", "open-source"]
            }
        except Exception as e:
            print(f"Error fetching GitHub data: {e}")
            return {}
    
    async def scrape_web_content(self, url: str) -> Dict[str, Any]:
        """Scrape web content via Web Scraper MCP"""
        try:
            # For demo purposes, return mock data
            return {
                "url": url,
                "title": "Sample Article Title",
                "content": "This is sample content from the scraped article...",
                "summary": "Brief summary of the article content",
                "tags": ["sample", "article", "content"],
                "scraped_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error scraping web content: {e}")
            return {}
