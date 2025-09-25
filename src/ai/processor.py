"""
AI Recommendation Engine using Claude 3.5 Sonnet
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
import anthropic
import os
from datetime import datetime

from ..models.user import User
from ..models.recommendation import Recommendation, RecommendationCategory, DifficultyLevel
from ..models.trending import TrendingContext
from .prompts import PromptTemplates

class AIProcessor:
    """AI recommendation engine powered by Claude 3.5 Sonnet"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("⚠️ ANTHROPIC_API_KEY not configured, using mock responses")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 4000
        self.temperature = 0.7
    
    async def generate_recommendations(self, user: User, trending_data: TrendingContext, 
                                    feedback_history: List[Dict[str, Any]] = None) -> List[Recommendation]:
        """Generate personalized recommendations using Claude 3.5 Sonnet"""
        try:
            if not self.client:
                return self._get_mock_recommendations(user)
            
            prompt = PromptTemplates.get_recommendation_prompt(user, trending_data, feedback_history)
            
            # Call Claude API
            response = await self._call_claude_api(prompt)
            
            if response:
                recommendations_data = json.loads(response)
                recommendations = []
                
                for rec_data in recommendations_data.get("recommendations", []):
                    recommendation = Recommendation.create_new(
                        user_id=user.id,
                        category=RecommendationCategory(rec_data.get("category", "LEARN")),
                        title=rec_data.get("title", "Untitled Recommendation"),
                        description=rec_data.get("description", "No description provided"),
                        next_steps=rec_data.get("next_steps", []),
                        trend_connection=rec_data.get("trend_connection"),
                        difficulty_level=DifficultyLevel(rec_data.get("difficulty_level", "intermediate")),
                        score=float(rec_data.get("score", 0.8))
                    )
                    recommendations.append(recommendation)
                
                return recommendations
            else:
                return self._get_mock_recommendations(user)
                
        except Exception as e:
            print(f"❌ AI Processor Error: {e}")
            return self._get_mock_recommendations(user)
    
    async def generate_email_content(self, user: User, recommendations: List[Recommendation]) -> Dict[str, str]:
        """Generate personalized email content"""
        try:
            if not self.client:
                return self._get_mock_email_content(user, recommendations)
            
            # Convert recommendations to dict format for prompt
            recs_data = []
            for rec in recommendations:
                recs_data.append({
                    "title": rec.title,
                    "description": rec.description,
                    "category": rec.category.value,
                    "difficulty_level": rec.difficulty_level.value,
                    "next_steps": rec.next_steps
                })
            
            prompt = PromptTemplates.get_email_personalization_prompt(user, recs_data)
            
            response = await self._call_claude_api(prompt)
            
            if response:
                return json.loads(response)
            else:
                return self._get_mock_email_content(user, recommendations)
                
        except Exception as e:
            print(f"❌ AI Email Generation Error: {e}")
            return self._get_mock_email_content(user, recommendations)
    
    async def analyze_trends(self, trending_data: TrendingContext) -> str:
        """Analyze trending data for insights"""
        try:
            if not self.client:
                return self._get_mock_trend_analysis()
            
            prompt = PromptTemplates.get_trend_analysis_prompt(trending_data)
            
            response = await self._call_claude_api(prompt)
            
            if response:
                return response
            else:
                return self._get_mock_trend_analysis()
                
        except Exception as e:
            print(f"❌ AI Trend Analysis Error: {e}")
            return self._get_mock_trend_analysis()
    
    async def _call_claude_api(self, prompt: str) -> Optional[str]:
        """Call Claude API with error handling"""
        try:
            # Run the synchronous API call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"❌ Claude API Error: {e}")
            return None
    
    def _get_mock_recommendations(self, user: User) -> List[Recommendation]:
        """Generate mock recommendations for demo purposes"""
        return [
            Recommendation.create_new(
                user_id=user.id,
                category=RecommendationCategory.BUILD,
                title="Build an AI-Powered Email Service",
                description="Create a personalized email recommendation service using Claude 3.5 Sonnet and Resend API. This project combines trending AI technologies with practical email automation.",
                next_steps=[
                    "Set up Resend API account and get API key",
                    "Integrate Claude 3.5 Sonnet for content generation",
                    "Create email templates with Jinja2",
                    "Build user profile management system",
                    "Implement recommendation scoring algorithm"
                ],
                trend_connection="AI email automation is trending with 95% score on GitHub",
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                score=0.92
            ),
            Recommendation.create_new(
                user_id=user.id,
                category=RecommendationCategory.LEARN,
                title="Master MCP Server Integration",
                description="Learn how to build and integrate MCP (Model Context Protocol) servers for seamless AI tool connections. This skill is becoming essential for modern AI applications.",
                next_steps=[
                    "Study MCP protocol documentation",
                    "Build a simple MCP server in Python",
                    "Integrate with Claude API using MCP",
                    "Create custom tools for your use case",
                    "Share your MCP server on GitHub"
                ],
                trend_connection="MCP servers are trending in AI development community",
                difficulty_level=DifficultyLevel.ADVANCED,
                score=0.88
            ),
            Recommendation.create_new(
                user_id=user.id,
                category=RecommendationCategory.COLLABORATE,
                title="Contribute to Open Source AI Projects",
                description="Join the growing community of AI developers by contributing to popular open source projects. This will help you learn from experts and build your reputation.",
                next_steps=[
                    "Find AI projects that match your interests",
                    "Start with documentation improvements",
                    "Fix small bugs and submit PRs",
                    "Engage with the community on Discord/Slack",
                    "Build your own AI project and open source it"
                ],
                trend_connection="Open source AI projects are gaining massive traction",
                difficulty_level=DifficultyLevel.BEGINNER,
                score=0.85
            )
        ]
    
    def _get_mock_email_content(self, user: User, recommendations: List[Recommendation]) -> Dict[str, str]:
        """Generate mock email content for demo purposes"""
        return {
            "subject": f"Your Daily Creator Recommendations, {user.name}! 🚀",
            "greeting": f"Good {user.email_time}, {user.name}!",
            "intro": f"I've analyzed the latest trends in {', '.join(user.interests[:2])} and found some exciting opportunities that align perfectly with your goals of {user.goals[0] if user.goals else 'building amazing things'}.",
            "recommendations_text": f"""
Here are your personalized recommendations for today:

🎯 {recommendations[0].title}
{recommendations[0].description}
Difficulty: {recommendations[0].difficulty_level.value.title()}

🚀 {recommendations[1].title}
{recommendations[1].description}
Difficulty: {recommendations[1].difficulty_level.value.title()}

🤝 {recommendations[2].title}
{recommendations[2].description}
Difficulty: {recommendations[2].difficulty_level.value.title()}
            """.strip(),
            "closing": "These recommendations are tailored specifically for your skills and interests. Pick one that excites you most and start building! Remember, every expert was once a beginner. 🎉"
        }
    
    def _get_mock_trend_analysis(self) -> str:
        """Generate mock trend analysis for demo purposes"""
        return """
        Current AI Development Trends Analysis:
        
        The AI development landscape is experiencing unprecedented growth, with several key trends emerging. Claude 3.5 Sonnet is leading the charge in advanced language models, offering superior reasoning capabilities for complex development tasks. Email automation APIs like Resend are becoming essential infrastructure for modern applications.
        
        MCP (Model Context Protocol) servers are revolutionizing how AI tools integrate, enabling seamless connections between different services. This trend is particularly strong in the developer community, with GitHub trending repositories showing increased activity in AI-powered development tools.
        
        The demand for AI-skilled developers continues to rise, with Python, TypeScript, and Rust being the most sought-after languages for AI projects. Open source contributions in AI are at an all-time high, presenting excellent opportunities for developers to build their reputation and skills.
        """
