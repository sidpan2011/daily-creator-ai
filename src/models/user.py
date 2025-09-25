"""
User data models for Daily Creator AI
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

class UserProfile(BaseModel):
    """User profile for registration and recommendations"""
    name: str
    email: EmailStr
    skills: List[str]
    interests: List[str]
    goals: List[str]
    github_username: Optional[str] = None
    email_time: str = "morning"  # morning, afternoon, evening
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Alex Chen",
                "email": "alex@example.com",
                "skills": ["Python", "React", "Machine Learning"],
                "interests": ["AI", "Web Development", "Open Source"],
                "goals": ["Build a SaaS product", "Contribute to open source", "Learn Rust"],
                "github_username": "alexchen",
                "email_time": "morning"
            }
        }
    }

class User(BaseModel):
    """Complete user model with ID and timestamps"""
    id: str
    name: str
    email: EmailStr
    skills: List[str]
    interests: List[str]
    goals: List[str]
    github_username: Optional[str] = None
    email_time: str = "morning"
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_profile(cls, profile: UserProfile) -> "User":
        """Create User from UserProfile"""
        now = datetime.utcnow()
        return cls(
            id=str(uuid.uuid4()),
            name=profile.name,
            email=profile.email,
            skills=profile.skills,
            interests=profile.interests,
            goals=profile.goals,
            github_username=profile.github_username,
            email_time=profile.email_time,
            created_at=now,
            updated_at=now
        )

class UserUpdate(BaseModel):
    """Model for updating user profile"""
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    github_username: Optional[str] = None
    email_time: Optional[str] = None
