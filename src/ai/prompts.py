"""
Prompt templates for Claude 3.5 Sonnet AI recommendations
"""

from typing import List, Dict, Any
from ..models.user import User
from ..models.trending import TrendingContext
from ..models.recommendation import RecommendationCategory, DifficultyLevel

class PromptTemplates:
    """Collection of prompt templates for different AI tasks"""
    
    @staticmethod
    def get_recommendation_prompt(user: User, trending_data: TrendingContext, 
                                feedback_history: List[Dict[str, Any]] = None) -> str:
        """Generate personalized recommendations prompt"""
        
        feedback_context = ""
        if feedback_history:
            feedback_context = f"""
            
            Previous Feedback Analysis:
            {_format_feedback_history(feedback_history)}
            """
        
        return f"""You are Daily Creator AI, an expert personal curator for creators and developers. 
        Your task is to generate 3 highly personalized, actionable recommendations for a user based on their profile and current trends.

        USER PROFILE:
        Name: {user.name}
        Skills: {', '.join(user.skills)}
        Interests: {', '.join(user.interests)}
        Goals: {', '.join(user.goals)}
        GitHub: {user.github_username or 'Not provided'}
        Preferred email time: {user.email_time}
        {feedback_context}

        CURRENT TRENDING DATA:
        {_format_trending_data(trending_data)}

        REQUIREMENTS:
        1. Generate exactly 3 recommendations
        2. Each recommendation must be actionable and specific
        3. Connect recommendations to current trends when relevant
        4. Vary difficulty levels (beginner, intermediate, advanced)
        5. Include diverse categories (BUILD, WRITE, LEARN, COLLABORATE)
        6. Provide clear next steps for each recommendation
        7. Score each recommendation (0.0-1.0) based on relevance and potential impact

        OUTPUT FORMAT (JSON):
        {{
            "recommendations": [
                {{
                    "category": "BUILD|WRITE|LEARN|COLLABORATE",
                    "title": "Compelling title (max 60 chars)",
                    "description": "Detailed description (2-3 sentences)",
                    "next_steps": ["Step 1", "Step 2", "Step 3"],
                    "trend_connection": "How this connects to current trends",
                    "difficulty_level": "beginner|intermediate|advanced",
                    "score": 0.85
                }}
            ]
        }}

        Focus on recommendations that will genuinely help this user achieve their goals while leveraging current trends and opportunities."""

    @staticmethod
    def get_email_personalization_prompt(user: User, recommendations: List[Dict[str, Any]]) -> str:
        """Generate personalized email content"""
        
        return f"""You are Daily Creator AI writing a personalized daily email for {user.name}.

        USER CONTEXT:
        - Skills: {', '.join(user.skills)}
        - Interests: {', '.join(user.interests)}
        - Goals: {', '.join(user.goals)}
        - Email time preference: {user.email_time}

        RECOMMENDATIONS TO INCLUDE:
        {_format_recommendations_for_email(recommendations)}

        REQUIREMENTS:
        1. Write a warm, personal greeting
        2. Create an engaging subject line (max 50 chars)
        3. Write a brief intro paragraph connecting to their goals
        4. Present each recommendation as an exciting opportunity
        5. Include a motivational closing
        6. Keep tone professional but friendly
        7. Make it feel like it was written specifically for them

        OUTPUT FORMAT (JSON):
        {{
            "subject": "Email subject line",
            "greeting": "Personal greeting",
            "intro": "Introductory paragraph",
            "recommendations_text": "Formatted recommendations text",
            "closing": "Motivational closing paragraph"
        }}"""

    @staticmethod
    def get_trend_analysis_prompt(trending_data: TrendingContext) -> str:
        """Analyze trending data for insights"""
        
        return f"""Analyze the following trending data and extract key insights for creators and developers:

        {_format_trending_data(trending_data)}

        Provide insights on:
        1. Emerging technologies and tools
        2. Popular programming languages and frameworks
        3. Trending topics in AI and development
        4. Opportunities for creators
        5. Skills in high demand

        Format as a brief analysis (2-3 paragraphs) highlighting the most relevant trends."""

def _format_feedback_history(feedback_history: List[Dict[str, Any]]) -> str:
    """Format feedback history for prompt"""
    if not feedback_history:
        return "No previous feedback available"
    
    formatted = []
    for feedback in feedback_history[-5:]:  # Last 5 feedback items
        formatted.append(f"- {feedback.get('feedback', 'unknown')} on '{feedback.get('title', 'unknown')}'")
    
    return "\n".join(formatted)

def _format_trending_data(trending_data: TrendingContext) -> str:
    """Format trending data for prompt"""
    sections = []
    
    if trending_data.github_trending:
        sections.append("GitHub Trending:")
        for item in trending_data.github_trending[:3]:
            sections.append(f"- {item.title}: {item.description}")
    
    if trending_data.hackernews_top:
        sections.append("\nHacker News Top:")
        for item in trending_data.hackernews_top[:3]:
            sections.append(f"- {item.title}: {item.description}")
    
    if trending_data.producthunt_featured:
        sections.append("\nProduct Hunt Featured:")
        for item in trending_data.producthunt_featured[:3]:
            sections.append(f"- {item.title}: {item.description}")
    
    return "\n".join(sections)

def _format_recommendations_for_email(recommendations: List[Dict[str, Any]]) -> str:
    """Format recommendations for email prompt"""
    formatted = []
    for i, rec in enumerate(recommendations, 1):
        formatted.append(f"{i}. {rec.get('title', 'Unknown')}")
        formatted.append(f"   {rec.get('description', 'No description')}")
        formatted.append(f"   Category: {rec.get('category', 'Unknown')}")
        formatted.append(f"   Difficulty: {rec.get('difficulty_level', 'Unknown')}")
        formatted.append("")
    
    return "\n".join(formatted)
