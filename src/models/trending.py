"""
Trending data models for Sparkflow
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class TrendingData:
    """Trending data from various sources"""
    github_repos: List[Dict[str, Any]]
    hackernews_topics: List[Dict[str, Any]]
    timestamp: str
