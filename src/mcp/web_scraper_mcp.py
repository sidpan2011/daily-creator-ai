"""
Web Scraper MCP wrapper for content extraction
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
import httpx
import os

class WebScraperMCP:
    """Wrapper for Web Scraper MCP server"""
    
    def __init__(self):
        self.base_url = os.getenv("WEB_SCRAPER_MCP_URL", "http://localhost:3004")
        self.timeout = 30.0
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def scrape_url(self, url: str, extract_text: bool = True, 
                        extract_links: bool = False) -> Dict[str, Any]:
        """Scrape content from URL"""
        try:
            print(f"🕷️ Web Scraper MCP: Scraping {url}")
            
            # For demo purposes, return mock scraped data
            return self._get_mock_scraped_data(url)
            
        except Exception as e:
            print(f"❌ Web Scraper MCP Error: {e}")
            return {}
    
    def _get_mock_scraped_data(self, url: str) -> Dict[str, Any]:
        """Get mock scraped data for demo purposes"""
        return {
            "url": url,
            "title": "Sample Article: The Future of AI Development",
            "content": """
            Artificial Intelligence is revolutionizing the way we build software. 
            From automated code generation to intelligent debugging, AI tools are 
            becoming essential for modern developers. This article explores the 
            latest trends in AI development and how they're changing the industry.
            
            Key topics covered:
            - Claude 3.5 Sonnet capabilities
            - Resend API for email automation
            - MCP server integrations
            - Best practices for AI-powered development
            """,
            "summary": "AI is transforming software development with tools like Claude 3.5 Sonnet and automated email services",
            "tags": ["ai", "development", "automation", "claude", "resend"],
            "links": [
                "https://anthropic.com/claude",
                "https://resend.com",
                "https://github.com/anthropics/claude-api"
            ],
            "images": [
                "https://example.com/ai-diagram.png",
                "https://example.com/development-flow.png"
            ],
            "scraped_at": "2024-01-15T10:30:00Z",
            "word_count": 150,
            "reading_time": "1 min"
        }
    
    async def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs in parallel"""
        try:
            tasks = [self.scrape_url(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return successful results
            successful_results = []
            for result in results:
                if not isinstance(result, Exception) and result:
                    successful_results.append(result)
            
            return successful_results
            
        except Exception as e:
            print(f"❌ Web Scraper MCP Error: {e}")
            return []
    
    async def extract_trending_topics(self, source: str = "hackernews") -> List[Dict[str, Any]]:
        """Extract trending topics from various sources"""
        try:
            # For demo purposes, return mock trending topics
            if source == "hackernews":
                return [
                    {
                        "title": "Building AI-Powered Personal Assistants",
                        "url": "https://news.ycombinator.com/item?id=123456",
                        "score": 92,
                        "comments": 45,
                        "source": "hackernews"
                    },
                    {
                        "title": "The Future of Email APIs",
                        "url": "https://news.ycombinator.com/item?id=123457",
                        "score": 85,
                        "comments": 32,
                        "source": "hackernews"
                    }
                ]
            elif source == "reddit":
                return [
                    {
                        "title": "Best AI Tools for Developers in 2024",
                        "url": "https://reddit.com/r/MachineLearning/comments/123456",
                        "score": 87,
                        "comments": 120,
                        "source": "reddit"
                    }
                ]
            else:
                return []
                
        except Exception as e:
            print(f"❌ Web Scraper MCP Error: {e}")
            return []
    
    async def get_article_summary(self, url: str) -> Dict[str, Any]:
        """Get article summary and key points"""
        try:
            scraped_data = await self.scrape_url(url)
            
            return {
                "url": url,
                "title": scraped_data.get("title", ""),
                "summary": scraped_data.get("summary", ""),
                "key_points": [
                    "AI is revolutionizing software development",
                    "Claude 3.5 Sonnet offers advanced capabilities",
                    "Email automation is becoming essential",
                    "MCP servers enable seamless integrations"
                ],
                "tags": scraped_data.get("tags", []),
                "reading_time": scraped_data.get("reading_time", "1 min"),
                "scraped_at": scraped_data.get("scraped_at", "")
            }
            
        except Exception as e:
            print(f"❌ Web Scraper MCP Error: {e}")
            return {}
    
    async def test_connection(self) -> bool:
        """Test MCP connection"""
        try:
            # For demo purposes, always return True
            print("✅ Web Scraper MCP: Connection test successful")
            return True
        except Exception as e:
            print(f"❌ Web Scraper MCP: Connection test failed - {e}")
            return False
