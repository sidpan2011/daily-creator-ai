"""
FastAPI routes for Daily Creator AI
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
import json

from ..models.user import UserProfile, User
from ..models.recommendation import Recommendation, RecommendationResponse
from ..core.engine import DailyCreatorEngine

router = APIRouter()

# Dependency to get engine instance
def get_engine() -> DailyCreatorEngine:
    return DailyCreatorEngine()

@router.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    try:
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>Daily Creator AI</title></head>
            <body>
                <h1>Daily Creator AI</h1>
                <p>AI-powered personal curator for creators</p>
                <p>Template file not found. Please run the demo setup.</p>
            </body>
        </html>
        """)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Daily Creator AI",
        "version": "1.0.0"
    }

@router.post("/api/users/register")
async def register_user(profile: UserProfile, engine: DailyCreatorEngine = Depends(get_engine)):
    """Register a new user"""
    try:
        user_id = await engine.process_user_registration(profile)
        return {
            "success": True,
            "user_id": user_id,
            "message": f"User {profile.name} registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/users/{user_id}")
async def get_user(user_id: str, engine: DailyCreatorEngine = Depends(get_engine)):
    """Get user profile"""
    try:
        user = await engine._get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/users/{user_id}/recommendations/generate")
async def generate_recommendations(user_id: str, engine: DailyCreatorEngine = Depends(get_engine)):
    """Generate daily recommendations for a user"""
    try:
        response = await engine.generate_daily_recommendations(user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/users/{user_id}/recommendations")
async def get_user_recommendations(user_id: str, limit: int = 10, 
                                 engine: DailyCreatorEngine = Depends(get_engine)):
    """Get user's recommendations"""
    try:
        recommendations = await engine.get_user_recommendations(user_id, limit)
        return {
            "recommendations": recommendations,
            "user_id": user_id,
            "total_count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/users/{user_id}/recommendations/{recommendation_id}/feedback")
async def submit_feedback(user_id: str, recommendation_id: str, 
                         feedback: Dict[str, str], 
                         engine: DailyCreatorEngine = Depends(get_engine)):
    """Submit feedback on a recommendation"""
    try:
        feedback_type = feedback.get("feedback", "like")
        success = await engine.record_user_feedback(user_id, recommendation_id, feedback_type)
        
        if success:
            return {"success": True, "message": "Feedback recorded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/demo/users")
async def get_demo_users():
    """Get demo users for testing"""
    try:
        with open("demo/demo_users.json", "r") as f:
            demo_users = json.load(f)
        return {"demo_users": demo_users}
    except FileNotFoundError:
        return {"demo_users": []}

@router.get("/api/demo/trends")
async def get_demo_trends():
    """Get demo trending data"""
    try:
        with open("demo/cached_trends.json", "r") as f:
            trends = json.load(f)
        return {"trends": trends}
    except FileNotFoundError:
        return {"trends": []}

@router.get("/api/demo/recommendations")
async def get_demo_recommendations():
    """Get demo recommendations"""
    try:
        with open("demo/sample_recommendations.json", "r") as f:
            recommendations = json.load(f)
        return {"recommendations": recommendations}
    except FileNotFoundError:
        return {"recommendations": []}

@router.post("/api/demo/simulate")
async def simulate_daily_flow(engine: DailyCreatorEngine = Depends(get_engine)):
    """Simulate the complete daily flow for demo purposes"""
    try:
        # Create a demo user
        demo_profile = UserProfile(
            name="Demo Creator",
            email="demo@dailycreator.ai",
            skills=["Python", "JavaScript", "AI"],
            interests=["Web Development", "AI", "Open Source"],
            goals=["Build a SaaS product", "Learn Rust", "Contribute to open source"],
            github_username="democreator",
            email_time="morning"
        )
        
        # Register user
        user_id = await engine.process_user_registration(demo_profile)
        
        # Generate recommendations
        recommendations_response = await engine.generate_daily_recommendations(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "recommendations": recommendations_response,
            "message": "Demo flow completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
