"""
User data models for Sparkflow
"""

from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

@dataclass
class UserProfile:
    """User profile for recommendations"""
    name: str
    email: str
    skills: List[str]
    interests: List[str]
    goals: List[str]

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
            github_username=None,
            email_time="morning",
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
