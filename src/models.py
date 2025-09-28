"""
Clean Data Models for Real Data Processing
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class UserProfile:
    name: str
    email: str
    github_username: Optional[str]
    skills: List[str]
    interests: List[str]
    goals: List[str]
    experience_level: str
    content_preferences: Dict[str, str]

@dataclass
class ResearchData:
    trending_repos: List[Dict[str, Any]]
    hackernews_stories: List[Dict[str, Any]]
    user_context: Dict[str, Any]
    language_trends: Dict[str, List[Dict[str, Any]]]
    timestamp: str

@dataclass
class EditorialContent:
    headline: str
    content: str
    key_insights: List[str]
    date: str
    data_sources: List[str]

@dataclass
class TopicSelection:
    selected_topic: str
    angle: str
    supporting_data: List[str]
    why_now: str
    personal_relevance: str