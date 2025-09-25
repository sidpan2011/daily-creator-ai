"""
Recommendation data models for Daily Creator AI
"""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid

class RecommendationCategory(str, Enum):
    """Categories for recommendations"""
    BUILD = "BUILD"
    WRITE = "WRITE" 
    LEARN = "LEARN"
    COLLABORATE = "COLLABORATE"

class DifficultyLevel(str, Enum):
    """Difficulty levels for recommendations"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Recommendation(BaseModel):
    """Individual recommendation model"""
    id: str
    user_id: str
    category: RecommendationCategory
    title: str
    description: str
    next_steps: List[str]
    trend_connection: Optional[str] = None
    difficulty_level: DifficultyLevel
    score: float  # 0.0 to 1.0
    created_at: datetime
    sent_at: Optional[datetime] = None
    
    @classmethod
    def create_new(cls, user_id: str, category: RecommendationCategory, 
                   title: str, description: str, next_steps: List[str],
                   trend_connection: Optional[str] = None,
                   difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
                   score: float = 0.8) -> "Recommendation":
        """Create a new recommendation"""
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            category=category,
            title=title,
            description=description,
            next_steps=next_steps,
            trend_connection=trend_connection,
            difficulty_level=difficulty_level,
            score=score,
            created_at=datetime.utcnow()
        )

class RecommendationResponse(BaseModel):
    """Response model for recommendation API"""
    recommendations: List[Recommendation]
    user_id: str
    generated_at: datetime
    total_count: int

class UserFeedback(BaseModel):
    """User feedback on recommendations"""
    id: str
    user_id: str
    recommendation_id: str
    feedback: str  # 'like', 'dislike', 'clicked'
    timestamp: datetime
    
    @classmethod
    def create(cls, user_id: str, recommendation_id: str, feedback: str) -> "UserFeedback":
        """Create new feedback"""
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            recommendation_id=recommendation_id,
            feedback=feedback,
            timestamp=datetime.utcnow()
        )
