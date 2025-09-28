"""
Real-Time Data Sources
Fresh, up-to-date content from multiple reliable sources
"""
import httpx
import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
import feedparser
import re

class RealTimeDataAggregator:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                'User-Agent': 'Persnally/1.0 (Content Aggregator)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def get_fresh_content(self, user_interests: List[str]) -> Dict[str, Any]:
        """Get genuinely fresh content from multiple real-time sources"""
        
        print("🚀 Fetching REAL-TIME content from multiple sources...")
        
        # Get content from all sources in parallel
        results = await asyncio.gather(
            self._get_github_releases(),
            self._get_producthunt_launches(),
            self._get_dev_to_articles(),
            self._get_hackernews_fresh(),
            self._get_reddit_programming(),
            self._get_twitter_tech_trends(),
            return_exceptions=True
        )
        
        github_releases, ph_launches, dev_articles, hn_fresh, reddit_posts, twitter_trends = results
        
        # Filter and combine results
        all_content = []
        
        # Add GitHub releases (these are always fresh)
        if isinstance(github_releases, list):
            all_content.extend(github_releases)
        
        # Add ProductHunt launches (daily fresh content)
        if isinstance(ph_launches, list):
            all_content.extend(ph_launches)
        
        # Add Dev.to articles (recent technical content)
        if isinstance(dev_articles, list):
            all_content.extend(dev_articles)
        
        # Add fresh HackerNews (last 24 hours)
        if isinstance(hn_fresh, list):
            all_content.extend(hn_fresh)
        
        # Add Reddit programming discussions
        if isinstance(reddit_posts, list):
            all_content.extend(reddit_posts)
        
        # Filter by user interests and recency
        relevant_content = self._filter_by_interests(all_content, user_interests)
        fresh_content = self._filter_by_recency(relevant_content, hours=48)  # Last 48 hours
        
        print(f"✅ Found {len(fresh_content)} pieces of fresh, relevant content")
        
        return {
            'fresh_content': fresh_content,
            'total_sources': 6,
            'content_count': len(fresh_content),
            'last_updated': datetime.now().isoformat()
        }
    
    async def _get_github_releases(self) -> List[Dict[str, Any]]:
        """Get latest GitHub releases from popular repositories"""
        try:
            # Popular repos in different categories
            popular_repos = [
                'microsoft/vscode',
                'facebook/react',
                'vercel/next.js',
                'openai/openai-python',
                'solana-labs/solana',
                'ethereum/go-ethereum',
                'pytorch/pytorch',
                'tensorflow/tensorflow'
            ]
            
            releases = []
            for repo in popular_repos[:4]:  # Limit to avoid rate limits
                try:
                    response = await self.session.get(
                        f"https://api.github.com/repos/{repo}/releases/latest"
                    )
                    if response.status_code == 200:
                        release = response.json()
                        published = datetime.fromisoformat(release['published_at'].replace('Z', '+00:00'))
                        
                        # Only include releases from last 30 days
                        if (datetime.now(published.tzinfo) - published).days <= 30:
                            releases.append({
                                'title': f"{repo} {release['tag_name']} Released",
                                'description': release.get('body', 'New release available')[:300],
                                'url': release['html_url'],
                                'published_at': release['published_at'],
                                'source': 'GitHub Releases',
                                'category': 'release',
                                'relevance_keywords': repo.split('/')[1]
                            })
                    
                    await asyncio.sleep(0.2)  # Rate limiting
                except Exception as e:
                    continue
            
            return releases
        except Exception as e:
            print(f"⚠️ GitHub releases failed: {e}")
            return []
    
    async def _get_producthunt_launches(self) -> List[Dict[str, Any]]:
        """Get today's ProductHunt launches"""
        try:
            # ProductHunt RSS feed for today's launches
            today = datetime.now().strftime('%Y/%m/%d')
            
            # Use RSS feed as it's publicly available
            response = await self.session.get("https://www.producthunt.com/feed")
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                launches = []
                for entry in feed.entries[:10]:  # Top 10 launches
                    published = datetime(*entry.published_parsed[:6])
                    
                    # Only today's launches
                    if (datetime.now() - published).days == 0:
                        launches.append({
                            'title': f"🚀 {entry.title}",
                            'description': entry.summary[:300],
                            'url': entry.link,
                            'published_at': published.isoformat(),
                            'source': 'ProductHunt',
                            'category': 'launch',
                            'relevance_keywords': 'startup product launch'
                        })
                
                return launches
        except Exception as e:
            print(f"⚠️ ProductHunt failed: {e}")
            return []
    
    async def _get_dev_to_articles(self) -> List[Dict[str, Any]]:
        """Get latest Dev.to articles"""
        try:
            response = await self.session.get(
                "https://dev.to/api/articles?per_page=20&top=1"  # Top articles from last day
            )
            
            if response.status_code == 200:
                articles = response.json()
                
                fresh_articles = []
                for article in articles:
                    published = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
                    
                    # Only articles from last 3 days
                    if (datetime.now(published.tzinfo) - published).days <= 3:
                        fresh_articles.append({
                            'title': article['title'],
                            'description': article['description'][:300],
                            'url': article['url'],
                            'published_at': article['published_at'],
                            'source': 'Dev.to',
                            'category': 'article',
                            'relevance_keywords': ' '.join(article.get('tag_list', []))
                        })
                
                return fresh_articles
        except Exception as e:
            print(f"⚠️ Dev.to failed: {e}")
            return []
    
    async def _get_hackernews_fresh(self) -> List[Dict[str, Any]]:
        """Get fresh HackerNews stories from last 24 hours"""
        try:
            # Get top stories
            response = await self.session.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            if response.status_code == 200:
                story_ids = response.json()[:30]  # Top 30 stories
                
                stories = []
                for story_id in story_ids[:15]:  # Check first 15
                    try:
                        story_response = await self.session.get(
                            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                        )
                        
                        if story_response.status_code == 200:
                            story = story_response.json()
                            if story and 'time' in story:
                                story_time = datetime.fromtimestamp(story['time'])
                                
                                # Only stories from last 24 hours
                                if (datetime.now() - story_time).hours <= 24:
                                    stories.append({
                                        'title': story.get('title', 'HN Story'),
                                        'description': f"HackerNews discussion with {story.get('descendants', 0)} comments and {story.get('score', 0)} points",
                                        'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                                        'published_at': story_time.isoformat(),
                                        'source': 'HackerNews',
                                        'category': 'discussion',
                                        'relevance_keywords': story.get('title', '').lower()
                                    })
                        
                        await asyncio.sleep(0.1)  # Rate limiting
                    except Exception:
                        continue
                
                return stories
        except Exception as e:
            print(f"⚠️ HackerNews failed: {e}")
            return []
    
    async def _get_reddit_programming(self) -> List[Dict[str, Any]]:
        """Get hot posts from programming subreddits"""
        try:
            subreddits = ['programming', 'webdev', 'MachineLearning', 'crypto', 'startups']
            all_posts = []
            
            for subreddit in subreddits[:3]:  # Limit to avoid rate limits
                try:
                    response = await self.session.get(
                        f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10",
                        headers={'User-Agent': 'Persnally/1.0'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post.get('data', {})
                            created = datetime.fromtimestamp(post_data.get('created_utc', 0))
                            
                            # Only posts from last 2 days
                            if (datetime.now() - created).days <= 2:
                                all_posts.append({
                                    'title': f"r/{subreddit}: {post_data.get('title', 'Reddit Post')}",
                                    'description': post_data.get('selftext', 'Discussion on Reddit')[:300],
                                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                    'published_at': created.isoformat(),
                                    'source': 'Reddit',
                                    'category': 'discussion',
                                    'relevance_keywords': f"{subreddit} {post_data.get('title', '').lower()}"
                                })
                    
                    await asyncio.sleep(0.5)  # Reddit rate limiting
                except Exception:
                    continue
            
            return all_posts
        except Exception as e:
            print(f"⚠️ Reddit failed: {e}")
            return []
    
    async def _get_twitter_tech_trends(self) -> List[Dict[str, Any]]:
        """Get tech trends from Twitter-like sources"""
        # For now, return empty as Twitter API requires special access
        # In production, you'd integrate with Twitter API v2 or similar
        return []
    
    def _filter_by_interests(self, content: List[Dict], user_interests: List[str]) -> List[Dict]:
        """Filter content by user interests"""
        if not user_interests:
            return content
        
        relevant_content = []
        for item in content:
            relevance_score = 0
            text_to_check = f"{item.get('title', '')} {item.get('description', '')} {item.get('relevance_keywords', '')}".lower()
            
            for interest in user_interests:
                if interest.lower() in text_to_check:
                    relevance_score += 1
            
            # Include items with any relevance or high-quality sources
            if relevance_score > 0 or item.get('source') in ['GitHub Releases', 'ProductHunt']:
                item['relevance_score'] = relevance_score
                relevant_content.append(item)
        
        return sorted(relevant_content, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def _filter_by_recency(self, content: List[Dict], hours: int = 48) -> List[Dict]:
        """Filter content by recency"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        fresh_content = []
        for item in content:
            try:
                published_str = item.get('published_at', '')
                if published_str:
                    # Handle different date formats
                    if 'T' in published_str:
                        published = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                    else:
                        published = datetime.fromisoformat(published_str)
                    
                    # Remove timezone info for comparison
                    if published.tzinfo:
                        published = published.replace(tzinfo=None)
                    
                    if published >= cutoff_time:
                        fresh_content.append(item)
            except Exception:
                # If we can't parse the date, include it anyway
                fresh_content.append(item)
        
        return fresh_content
