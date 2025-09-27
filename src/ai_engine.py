"""
AI Engine - handles OpenAI GPT-4o-mini integration for recommendation generation
"""
import openai
import json
from typing import List
from src.models import UserProfile, Recommendation, TrendingData

class AIEngine:
    """Simple AI engine for Sparkflow"""
    
    def __init__(self, config):
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    async def generate_recommendations(
        self, 
        user_data: dict, 
        trending_data: TrendingData
    ) -> List[Recommendation]:
        """Generate personalized recommendations using GPT-4o-mini"""
        
        prompt = self._create_prompt(user_data, trending_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse GPT's response into Recommendation objects
            return self._parse_recommendations(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            # Return mock data if AI fails
            return self._get_mock_recommendations()
    
    def _create_prompt(self, user_data: dict, trending_data: TrendingData) -> str:
        """Create the prompt for GPT-4o-mini"""
        return f"""
        Generate 3 personalized recommendations for this creator:
        
        Profile:
        - Skills: {', '.join(user_data['skills'])}
        - Interests: {', '.join(user_data['interests'])}
        - Goals: {', '.join(user_data['goals'])}
        
        Current Trends:
        - GitHub trending: {trending_data.github_repos[:3]}
        
        Create 3 specific, actionable recommendations in these categories:
        1. BUILD (a specific project to build)
        2. WRITE (a topic to write about)  
        3. LEARN (a skill to learn next)
        
        Make each recommendation specific, not generic. Connect their skills with trends.
        
        Return as JSON array with: category, title, description, next_steps (array), trend_connection
        """
    
    def _parse_recommendations(self, ai_response: str) -> List[Recommendation]:
        """Parse Claude's JSON response into Recommendation objects"""
        try:
            # Try to extract JSON from the response
            json_start = ai_response.find('[')
            json_end = ai_response.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                data = json.loads(json_str)
                
                recommendations = []
                for item in data:
                    recommendations.append(Recommendation(
                        category=item.get('category', 'BUILD'),
                        title=item.get('title', 'Untitled'),
                        description=item.get('description', 'No description'),
                        next_steps=item.get('next_steps', []),
                        trend_connection=item.get('trend_connection', 'No trend connection')
                    ))
                return recommendations
        except Exception as e:
            print(f"Error parsing AI response: {e}")
        
        # Fallback to mock data
        return self._get_mock_recommendations()
    
    def _get_mock_recommendations(self) -> List[Recommendation]:
        """Return mock recommendations if AI fails"""
        return [
            Recommendation(
                category="BUILD",
                title="AI-Powered Code Review Tool",
                description="Build a tool that uses AI to review code automatically and provide suggestions",
                next_steps=["Set up React project", "Integrate Claude API", "Design UI", "Deploy to Vercel"],
                trend_connection="AI coding tools are trending on GitHub"
            ),
            Recommendation(
                category="WRITE",
                title="Building with Claude: A Developer's Guide",
                description="Write a comprehensive guide about integrating Claude AI into development workflows",
                next_steps=["Research current AI tools", "Create outline", "Write first draft", "Get feedback"],
                trend_connection="AI development content is highly searched"
            ),
            Recommendation(
                category="LEARN",
                title="Advanced Python for AI",
                description="Master advanced Python concepts specifically for AI and machine learning applications",
                next_steps=["Take online course", "Build practice projects", "Join AI community", "Contribute to open source"],
                trend_connection="Python AI skills are in high demand"
            )
        ]
