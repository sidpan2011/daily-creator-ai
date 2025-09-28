"""
Real-Time Web Crawler
Actually crawls the web for fresh, current content instead of using fake data
"""
import httpx
import asyncio
import json
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin, urlparse

class RealTimeWebCrawler:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers=self.headers,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def get_fresh_tech_news(self, user_interests: List[str]) -> List[Dict[str, Any]]:
        """Get genuinely fresh tech news from RELIABLE sources only"""
        
        print("🌐 Crawling VERIFIED, reliable tech news sources...")
        
        all_articles = []
        
        # PRIORITY: Only use highly reliable, verified sources
        reliable_sources = [
            self._crawl_techcrunch(),        # Tier 1: Established tech journalism
            self._crawl_github_blog(),       # Tier 1: Official platform updates
            self._crawl_hacker_news_new(),   # Tier 1: Curated community
            self._crawl_openai_blog(),       # Tier 1: Official AI updates
            self._crawl_anthropic_blog(),    # Tier 1: Official AI research
            self._crawl_ethereum_blog(),     # Tier 1: Official blockchain updates
        ]
        
        results = await asyncio.gather(*reliable_sources, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                print(f"⚠️ Source failed: {result}")
        
        # Filter by user interests and recency
        relevant_articles = self._filter_by_interests(all_articles, user_interests)
        fresh_articles = self._filter_by_recency(relevant_articles, hours=72)  # Last 3 days
        
        # Sort by relevance and recency
        sorted_articles = sorted(
            fresh_articles, 
            key=lambda x: (x.get('relevance_score', 0), self._parse_date(x.get('published_at', ''))), 
            reverse=True
        )
        
        print(f"✅ Found {len(sorted_articles)} fresh, relevant articles")
        # Additional verification: Remove potentially unreliable sources
        verified_articles = []
        for article in sorted_articles:
            url = article.get('url', '')
            source = article.get('source', '')
            
            # Only include articles from verified domains
            trusted_domains = [
                'techcrunch.com', 'github.blog', 'news.ycombinator.com',
                'openai.com', 'anthropic.com', 'ethereum.org', 'blog.ethereum.org',
                'solana.com', 'polygon.technology', 'chainlink.com',
                'blog.google', 'engineering.fb.com', 'aws.amazon.com',
                'microsoft.com', 'apple.com', 'developer.apple.com'
            ]
            
            if any(domain in url for domain in trusted_domains) or source in ['HackerNews', 'GitHub Blog', 'TechCrunch', 'OpenAI Blog']:
                verified_articles.append(article)
        
        print(f"✅ Verified {len(verified_articles)} articles from trusted sources")
        return verified_articles[:15]  # Return top 15 verified articles
    
    async def _crawl_techcrunch(self) -> List[Dict[str, Any]]:
        """Crawl TechCrunch for latest tech news"""
        try:
            response = await self.session.get("https://techcrunch.com/feed/")
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                articles = []
                for entry in feed.entries[:10]:
                    published = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                    
                    articles.append({
                        'title': entry.title,
                        'description': self._clean_html(entry.get('summary', '')),
                        'url': entry.link,
                        'source': 'TechCrunch',
                        'published_at': published.isoformat(),
                        'category': 'tech_news',
                        'relevance_keywords': entry.title.lower()
                    })
                
                return articles
        except Exception as e:
            print(f"⚠️ TechCrunch crawl failed: {e}")
            return []
    
    async def _crawl_hacker_news_new(self) -> List[Dict[str, Any]]:
        """Get the newest stories from HackerNews (not just top stories)"""
        try:
            # Get newest stories instead of just top stories
            response = await self.session.get("https://hacker-news.firebaseio.com/v0/newstories.json")
            if response.status_code == 200:
                story_ids = response.json()[:20]  # Get 20 newest stories
                
                stories = []
                for story_id in story_ids:
                    try:
                        story_response = await self.session.get(
                            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                        )
                        
                        if story_response.status_code == 200:
                            story = story_response.json()
                            if story and story.get('title') and story.get('time'):
                                story_time = datetime.fromtimestamp(story['time'])
                                
                                # Only include stories from last 24 hours
                                if (datetime.now() - story_time).total_seconds() < 86400:  # 24 hours
                                    stories.append({
                                        'title': story['title'],
                                        'description': f"Fresh discussion on HackerNews with {story.get('descendants', 0)} comments",
                                        'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                                        'source': 'HackerNews',
                                        'published_at': story_time.isoformat(),
                                        'category': 'discussion',
                                        'relevance_keywords': story['title'].lower()
                                    })
                        
                        await asyncio.sleep(0.1)  # Rate limiting
                    except Exception:
                        continue
                
                return stories
        except Exception as e:
            print(f"⚠️ HackerNews crawl failed: {e}")
            return []
    
    async def _crawl_github_blog(self) -> List[Dict[str, Any]]:
        """Crawl GitHub's official blog for latest updates"""
        try:
            response = await self.session.get("https://github.blog/feed/")
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                articles = []
                for entry in feed.entries[:5]:
                    published = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                    
                    articles.append({
                        'title': f"GitHub: {entry.title}",
                        'description': self._clean_html(entry.get('summary', '')),
                        'url': entry.link,
                        'source': 'GitHub Blog',
                        'published_at': published.isoformat(),
                        'category': 'platform_update',
                        'relevance_keywords': f"github {entry.title.lower()}"
                    })
                
                return articles
        except Exception as e:
            print(f"⚠️ GitHub blog crawl failed: {e}")
            return []
    
    async def _crawl_openai_blog(self) -> List[Dict[str, Any]]:
        """Crawl OpenAI's blog for AI updates"""
        try:
            response = await self.session.get("https://openai.com/blog")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                articles = []
                # Look for blog post links (this is a simplified approach)
                blog_links = soup.find_all('a', href=re.compile(r'/blog/'))
                
                for link in blog_links[:5]:
                    title = link.get_text(strip=True)
                    if title and len(title) > 10:  # Filter out short/empty titles
                        articles.append({
                            'title': f"OpenAI: {title}",
                            'description': f"Latest update from OpenAI: {title}",
                            'url': urljoin("https://openai.com", link.get('href')),
                            'source': 'OpenAI Blog',
                            'published_at': datetime.now().isoformat(),  # We don't have exact dates from scraping
                            'category': 'ai_update',
                            'relevance_keywords': f"openai ai {title.lower()}"
                        })
                
                return articles
        except Exception as e:
            print(f"⚠️ OpenAI blog crawl failed: {e}")
            return []
    
    async def _crawl_ycombinator_news(self) -> List[Dict[str, Any]]:
        """Get latest from Y Combinator news/updates"""
        try:
            response = await self.session.get("https://www.ycombinator.com/blog")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                articles = []
                # Look for blog post titles (simplified scraping)
                post_titles = soup.find_all(['h1', 'h2', 'h3'], class_=re.compile(r'title|heading'))
                
                for title_elem in post_titles[:3]:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 10:
                        articles.append({
                            'title': f"YC: {title}",
                            'description': f"Latest from Y Combinator: {title}",
                            'url': "https://www.ycombinator.com/blog",
                            'source': 'Y Combinator',
                            'published_at': datetime.now().isoformat(),
                            'category': 'startup_news',
                            'relevance_keywords': f"yc startup {title.lower()}"
                        })
                
                return articles
        except Exception as e:
            print(f"⚠️ YC crawl failed: {e}")
            return []
    
    async def _crawl_dev_to_fresh(self) -> List[Dict[str, Any]]:
        """Get fresh articles from Dev.to"""
        try:
            response = await self.session.get("https://dev.to/api/articles?per_page=10&top=1")
            if response.status_code == 200:
                articles_data = response.json()
                
                articles = []
                for article in articles_data:
                    published = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
                    
                    # Only include articles from last 3 days
                    if (datetime.now(published.tzinfo) - published).days <= 3:
                        articles.append({
                            'title': article['title'],
                            'description': article.get('description', article['title']),
                            'url': article['url'],
                            'source': 'Dev.to',
                            'published_at': published.replace(tzinfo=None).isoformat(),
                            'category': 'tutorial',
                            'relevance_keywords': ' '.join(article.get('tag_list', []))
                        })
                
                return articles
        except Exception as e:
            print(f"⚠️ Dev.to crawl failed: {e}")
            return []
    
    async def _crawl_anthropic_blog(self) -> List[Dict[str, Any]]:
        """Crawl Anthropic's official blog for AI research updates"""
        try:
            response = await self.session.get("https://www.anthropic.com/news")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                articles = []
                # Look for blog post links (simplified approach)
                blog_links = soup.find_all('a', href=re.compile(r'/news/'))
                
                for link in blog_links[:3]:
                    title = link.get_text(strip=True)
                    if title and len(title) > 10:
                        articles.append({
                            'title': f"Anthropic Research: {title}",
                            'description': f"Latest AI research from Anthropic: {title}",
                            'url': urljoin("https://www.anthropic.com", link.get('href')),
                            'source': 'Anthropic',
                            'published_at': datetime.now().isoformat(),
                            'category': 'ai_research',
                            'relevance_keywords': f"anthropic ai research {title.lower()}"
                        })
                
                return articles
        except Exception as e:
            print(f"⚠️ Anthropic blog crawl failed: {e}")
            return []
    
    async def _crawl_ethereum_blog(self) -> List[Dict[str, Any]]:
        """Crawl Ethereum's official blog for blockchain updates"""
        try:
            response = await self.session.get("https://blog.ethereum.org/feed.xml")
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                articles = []
                for entry in feed.entries[:3]:
                    published = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                    
                    articles.append({
                        'title': f"Ethereum Foundation: {entry.title}",
                        'description': self._clean_html(entry.get('summary', '')),
                        'url': entry.link,
                        'source': 'Ethereum Foundation',
                        'published_at': published.isoformat(),
                        'category': 'blockchain_update',
                        'relevance_keywords': f"ethereum blockchain {entry.title.lower()}"
                    })
                
                return articles
        except Exception as e:
            print(f"⚠️ Ethereum blog crawl failed: {e}")
            return []
    
    def _clean_html(self, html_text: str) -> str:
        """Clean HTML tags and get plain text"""
        if not html_text:
            return ""
        
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text()
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:300]  # Limit length
    
    def _filter_by_interests(self, articles: List[Dict], user_interests: List[str]) -> List[Dict]:
        """Filter articles by user interests"""
        if not user_interests:
            return articles
        
        relevant_articles = []
        for article in articles:
            relevance_score = 0
            text_to_check = f"{article.get('title', '')} {article.get('description', '')} {article.get('relevance_keywords', '')}".lower()
            
            for interest in user_interests:
                interest_words = interest.lower().split()
                for word in interest_words:
                    if word in text_to_check:
                        relevance_score += 1
            
            # Include articles with any relevance or from high-quality sources
            if relevance_score > 0 or article.get('source') in ['GitHub Blog', 'OpenAI Blog', 'TechCrunch']:
                article['relevance_score'] = relevance_score
                relevant_articles.append(article)
        
        return relevant_articles
    
    def _filter_by_recency(self, articles: List[Dict], hours: int = 72) -> List[Dict]:
        """Filter articles by recency"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        fresh_articles = []
        for article in articles:
            try:
                published_at = self._parse_date(article.get('published_at', ''))
                if published_at and published_at >= cutoff_time:
                    fresh_articles.append(article)
            except Exception:
                # If we can't parse the date, include it anyway (might be very fresh)
                fresh_articles.append(article)
        
        return fresh_articles
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return datetime.now()
        
        try:
            # Handle ISO format
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            else:
                return datetime.fromisoformat(date_str)
        except Exception:
            return datetime.now()
    
    async def get_real_hackathons(self) -> List[Dict[str, Any]]:
        """Get real, current hackathons"""
        try:
            # Try to get hackathons from Devpost
            response = await self.session.get("https://devpost.com/hackathons")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                hackathons = []
                # Look for hackathon cards (simplified scraping)
                hackathon_cards = soup.find_all('div', class_=re.compile(r'hackathon|event'))
                
                for card in hackathon_cards[:5]:
                    title_elem = card.find(['h1', 'h2', 'h3', 'h4'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if 'hackathon' in title.lower() or 'competition' in title.lower():
                            hackathons.append({
                                'title': title,
                                'description': f"Active hackathon: {title}",
                                'url': 'https://devpost.com/hackathons',
                                'source': 'Devpost',
                                'published_at': datetime.now().isoformat(),
                                'category': 'hackathon',
                                'relevance_keywords': f"hackathon competition {title.lower()}"
                            })
                
                return hackathons
        except Exception as e:
            print(f"⚠️ Hackathon crawl failed: {e}")
            return []
