"""
Trending data models for Daily Creator AI
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid

class TrendingSource(str, Enum):
    """Sources for trending data"""
    GITHUB = "github"
    HACKERNEWS = "hackernews"
    PRODUCTHUNT = "producthunt"
    REDDIT = "reddit"
    TWITTER = "twitter"

class TrendingItem(BaseModel):
    """Individual trending item"""
    title: str
    description: str
    url: str
    source: TrendingSource
    score: float  # Trending score/rank
    tags: List[str]
    language: Optional[str] = None
    stars: Optional[int] = None
    created_at: datetime

class TrendingContext(BaseModel):
    """Complete trending context for AI processing"""
    github_trending: List[TrendingItem]
    hackernews_top: List[TrendingItem]
    producthunt_featured: List[TrendingItem]
    reddit_hot: List[TrendingItem]
    twitter_trending: List[TrendingItem]
    fetched_at: datetime
    
    def get_all_items(self) -> List[TrendingItem]:
        """Get all trending items from all sources"""
        all_items = []
        all_items.extend(self.github_trending)
        all_items.extend(self.hackernews_top)
        all_items.extend(self.producthunt_featured)
        all_items.extend(self.reddit_hot)
        all_items.extend(self.twitter_trending)
        return all_items
    
    def get_by_source(self, source: TrendingSource) -> List[TrendingItem]:
        """Get trending items by source"""
        source_map = {
            TrendingSource.GITHUB: self.github_trending,
            TrendingSource.HACKERNEWS: self.hackernews_top,
            TrendingSource.PRODUCTHUNT: self.producthunt_featured,
            TrendingSource.REDDIT: self.reddit_hot,
            TrendingSource.TWITTER: self.twitter_trending
        }
        return source_map.get(source, [])

class TrendingCache(BaseModel):
    """Cached trending data"""
    id: str
    source: TrendingSource
    data: Dict[str, Any]
    cached_at: datetime
    expires_at: datetime
    
    @classmethod
    def create(cls, source: TrendingSource, data: Dict[str, Any], 
               expires_in_hours: int = 6) -> "TrendingCache":
        """Create new cache entry"""
        now = datetime.utcnow()
        return cls(
            id=str(uuid.uuid4()),
            source=source,
            data=data,
            cached_at=now,
            expires_at=now.replace(hour=now.hour + expires_in_hours)
        )
    
    def is_expired(self) -> bool:
        """Check if cache is expired"""
        return datetime.utcnow() > self.expires_at
