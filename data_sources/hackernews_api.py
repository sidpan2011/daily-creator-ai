"""
Real HackerNews API Client
Fetches live trending stories and discussions
"""
import asyncio
import httpx
from typing import List, Dict, Any
from datetime import datetime

class HackerNewsAPIClient:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
    
    async def get_trending_stories(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Get real trending HackerNews stories"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get top story IDs
                response = await client.get(f"{self.base_url}/topstories.json")
                
                if response.status_code != 200:
                    print(f"❌ Failed to get top stories: {response.status_code}")
                    return []
                
                story_ids = response.json()[:limit * 2]  # Get extra to filter quality
                
                stories = []
                for story_id in story_ids:
                    try:
                        story_response = await client.get(f"{self.base_url}/item/{story_id}.json")
                        
                        if story_response.status_code == 200:
                            story = story_response.json()
                            
                            if (story and 
                                story.get("title") and 
                                story.get("type") == "story" and
                                story.get("score", 0) > 30):  # Quality filter
                                
                                stories.append({
                                    "id": story_id,
                                    "title": story["title"],
                                    "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                                    "points": story.get("score", 0),
                                    "comments": story.get("descendants", 0),
                                    "time": story.get("time", 0),
                                    "author": story.get("by", "unknown"),
                                    "category": self._categorize_story(story["title"])
                                })
                        
                        # Rate limiting courtesy
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        print(f"⚠️ Failed to get story {story_id}: {e}")
                        continue
                    
                    if len(stories) >= limit:
                        break
                
                print(f"✅ Retrieved {len(stories)} HackerNews stories")
                return stories
                
        except Exception as e:
            print(f"❌ Failed to get HackerNews stories: {e}")
            return []
    
    def _categorize_story(self, title: str) -> str:
        """Categorize HN stories by topic"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['ai', 'gpt', 'llm', 'machine learning', 'neural', 'claude']):
            return 'ai'
        elif any(word in title_lower for word in ['startup', 'funding', 'vc', 'entrepreneur']):
            return 'startup'
        elif any(word in title_lower for word in ['python', 'javascript', 'react', 'code', 'programming', 'dev']):
            return 'programming'
        elif any(word in title_lower for word in ['show hn', 'ask hn']):
            return 'community'
        else:
            return 'general'
    
    async def get_stories_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get stories filtered by category"""
        all_stories = await self.get_trending_stories(limit * 3)
        return [story for story in all_stories if story["category"] == category][:limit]
