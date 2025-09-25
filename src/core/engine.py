"""
Main orchestrator engine for Daily Creator AI
Coordinates all components to deliver personalized recommendations
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

from ..models.user import User, UserProfile
from ..models.recommendation import Recommendation, RecommendationResponse
from ..models.trending import TrendingContext
from ..mcp.manager import MCPManager
from ..ai.processor import AIProcessor
from .config import get_settings

class DailyCreatorEngine:
    """Main orchestrator for the Daily Creator AI system"""
    
    def __init__(self):
        self.settings = get_settings()
        self.mcp_manager = MCPManager()
        self.ai_processor = AIProcessor()
        self.db_path = Path("local_demo.db")
        
    async def process_user_registration(self, profile: UserProfile) -> str:
        """Process new user registration and return user ID"""
        try:
            # Create user from profile
            user = User.from_profile(profile)
            
            # Enrich with GitHub data if username provided
            if profile.github_username:
                github_data = await self.mcp_manager.get_user_github_data(profile.github_username)
                if github_data:
                    # Update user with GitHub insights
                    user.skills.extend(github_data.get("languages", []))
                    user.interests.extend(github_data.get("interests", []))
            
            # Store user in database
            await self._store_user(user)
            
            print(f"✅ User registered: {user.name} ({user.email})")
            return user.id
            
        except Exception as e:
            print(f"❌ User registration error: {e}")
            raise
    
    async def generate_daily_recommendations(self, user_id: str) -> RecommendationResponse:
        """Generate daily recommendations for a user"""
        try:
            # Get user profile
            user = await self._get_user(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Get trending data
            trending_data = await self.mcp_manager.gather_trending_context()
            
            # Get user feedback history
            feedback_history = await self._get_user_feedback(user_id)
            
            # Generate AI recommendations
            recommendations = await self.ai_processor.generate_recommendations(
                user, trending_data, feedback_history
            )
            
            # Store recommendations
            for rec in recommendations:
                await self._store_recommendation(rec)
            
            # Generate email content
            email_content = await self.ai_processor.generate_email_content(user, recommendations)
            
            # Send email
            await self._send_recommendation_email(user, email_content, recommendations)
            
            print(f"✅ Generated {len(recommendations)} recommendations for {user.name}")
            
            return RecommendationResponse(
                recommendations=recommendations,
                user_id=user_id,
                generated_at=datetime.utcnow(),
                total_count=len(recommendations)
            )
            
        except Exception as e:
            print(f"❌ Recommendation generation error: {e}")
            raise
    
    async def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[Recommendation]:
        """Get user's recent recommendations"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            query = """
                SELECT id, user_id, category, title, description, next_steps,
                       trend_connection, difficulty_level, score, created_at, sent_at
                FROM recommendations 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """
            
            cursor.execute(query, (user_id, limit))
            rows = cursor.fetchall()
            
            recommendations = []
            for row in rows:
                rec = Recommendation(
                    id=row[0],
                    user_id=row[1],
                    category=row[2],
                    title=row[3],
                    description=row[4],
                    next_steps=json.loads(row[5]) if row[5] else [],
                    trend_connection=row[6],
                    difficulty_level=row[7],
                    score=row[8],
                    created_at=datetime.fromisoformat(row[9]),
                    sent_at=datetime.fromisoformat(row[10]) if row[10] else None
                )
                recommendations.append(rec)
            
            conn.close()
            return recommendations
            
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}")
            return []
    
    async def record_user_feedback(self, user_id: str, recommendation_id: str, 
                                 feedback: str) -> bool:
        """Record user feedback on a recommendation"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            query = """
                INSERT INTO user_feedback (id, user_id, recommendation_id, feedback, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                f"feedback_{datetime.utcnow().timestamp()}",
                user_id,
                recommendation_id,
                feedback,
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Feedback recorded: {feedback} for recommendation {recommendation_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error recording feedback: {e}")
            return False
    
    async def _store_user(self, user: User) -> None:
        """Store user in database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = """
            INSERT INTO users (id, name, email, skills, interests, goals, 
                             github_username, email_time, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (
            user.id,
            user.name,
            user.email,
            json.dumps(user.skills),
            json.dumps(user.interests),
            json.dumps(user.goals),
            user.github_username,
            user.email_time,
            user.created_at.isoformat(),
            user.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def _get_user(self, user_id: str) -> Optional[User]:
        """Get user from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return User(
                id=row[0],
                name=row[1],
                email=row[2],
                skills=json.loads(row[3]),
                interests=json.loads(row[4]),
                goals=json.loads(row[5]),
                github_username=row[6],
                email_time=row[7],
                created_at=datetime.fromisoformat(row[8]),
                updated_at=datetime.fromisoformat(row[9])
            )
        
        return None
    
    async def _store_recommendation(self, recommendation: Recommendation) -> None:
        """Store recommendation in database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = """
            INSERT INTO recommendations (id, user_id, category, title, description,
                                       next_steps, trend_connection, difficulty_level,
                                       score, created_at, sent_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (
            recommendation.id,
            recommendation.user_id,
            recommendation.category.value,
            recommendation.title,
            recommendation.description,
            json.dumps(recommendation.next_steps),
            recommendation.trend_connection,
            recommendation.difficulty_level.value,
            recommendation.score,
            recommendation.created_at.isoformat(),
            recommendation.sent_at.isoformat() if recommendation.sent_at else None
        ))
        
        conn.commit()
        conn.close()
    
    async def _get_user_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user feedback history"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = """
            SELECT f.feedback, r.title
            FROM user_feedback f
            JOIN recommendations r ON f.recommendation_id = r.id
            WHERE f.user_id = ?
            ORDER BY f.timestamp DESC
            LIMIT 10
        """
        
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        
        conn.close()
        
        return [{"feedback": row[0], "title": row[1]} for row in rows]
    
    async def _send_recommendation_email(self, user: User, email_content: Dict[str, str], 
                                       recommendations: List[Recommendation]) -> None:
        """Send recommendation email to user"""
        try:
            # Generate HTML email content
            html_content = await self._generate_email_html(user, email_content, recommendations)
            
            # Generate text fallback
            text_content = await self._generate_email_text(user, email_content, recommendations)
            
            # Send via Resend MCP
            result = await self.mcp_manager.send_email(
                to_email=user.email,
                subject=email_content.get("subject", "Your Daily Creator Recommendations"),
                html_content=html_content,
                text_content=text_content
            )
            
            if result.get("success"):
                print(f"📧 Email sent successfully to {user.email}")
                
                # Update recommendation sent_at timestamp
                await self._update_recommendations_sent_at([r.id for r in recommendations])
            else:
                print(f"❌ Failed to send email: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Email sending error: {e}")
    
    async def _generate_email_html(self, user: User, email_content: Dict[str, str], 
                                 recommendations: List[Recommendation]) -> str:
        """Generate HTML email content"""
        # This will be implemented with Jinja2 templates
        return f"""
        <html>
        <body>
            <h1>{email_content.get('greeting', 'Hello')}</h1>
            <p>{email_content.get('intro', 'Here are your recommendations')}</p>
            {email_content.get('recommendations_text', '')}
            <p>{email_content.get('closing', 'Happy creating!')}</p>
        </body>
        </html>
        """
    
    async def _generate_email_text(self, user: User, email_content: Dict[str, str], 
                                 recommendations: List[Recommendation]) -> str:
        """Generate text email content"""
        return f"""
        {email_content.get('greeting', 'Hello')}
        
        {email_content.get('intro', 'Here are your recommendations')}
        
        {email_content.get('recommendations_text', '')}
        
        {email_content.get('closing', 'Happy creating!')}
        """
    
    async def _update_recommendations_sent_at(self, recommendation_ids: List[str]) -> None:
        """Update sent_at timestamp for recommendations"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        placeholders = ",".join("?" * len(recommendation_ids))
        query = f"UPDATE recommendations SET sent_at = ? WHERE id IN ({placeholders})"
        
        cursor.execute(query, [datetime.utcnow().isoformat()] + recommendation_ids)
        
        conn.commit()
        conn.close()
