"""
Simple data models for Sparkflow
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class UserProfile:
    """User profile for recommendations"""
    name: str
    email: str
    skills: List[str]
    interests: List[str]
    goals: List[str]

@dataclass 
class Recommendation:
    """AI-generated recommendation"""
    category: str  # BUILD, WRITE, LEARN
    title: str
    description: str
    next_steps: List[str]
    trend_connection: str

@dataclass
class TrendingData:
    """Trending data from various sources"""
    github_repos: List[Dict[str, Any]]
    hackernews_topics: List[Dict[str, Any]]
    timestamp: str
