"""
Behavioral Intelligence Engine
Analyzes user behavior patterns to predict intent and needs
"""
import openai
import json
from typing import Dict, Any, List
from datetime import datetime

class BehaviorAnalyzer:
    def __init__(self, config):
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    async def analyze_user_intent(self, github_data: dict, user_profile: dict) -> Dict[str, Any]:
        """Analyze GitHub behavior to predict user intent and needs"""
        
        prompt = f"""
        Analyze this developer's profile and activity to create a detailed behavioral profile:
        
        USER PROFILE: {json.dumps(user_profile, indent=2)}
        GITHUB ACTIVITY: {json.dumps(github_data, indent=2)}
        
        Focus on these SPECIFIC interests from their profile:
        {user_profile.get('interests', [])}
        
        Analyze their GitHub activity patterns:
        
        RECENT PROJECTS: {json.dumps(github_data.get('recent_repos', [])[:5], indent=2)}
        STARRED REPOS: {json.dumps(github_data.get('interests_from_stars', [])[:5], indent=2)}
        
        Based on their stated interests and GitHub activity, determine:
        
        1. PRIMARY FOCUS AREAS (match their interests to their repos):
           - If they're interested in "web3/blockchain" → look for Solana, Ethereum, DeFi repos
           - If they're interested in "ai/ml" → look for PyTorch, ML, AI agent repos  
           - If they're interested in "startup" → look for SaaS, business tools, landing pages
           - If they're interested in "hackathon" → look for competition/contest activity
        
        2. CURRENT INTENT based on recent activity:
           - BUILDING: Active commits, new projects in their interest areas
           - EXPLORING: Starring repos outside current stack, research mode
           - LEARNING: Educational repos, tutorials in their interest areas
           - LAUNCHING: Marketing sites, documentation, deployment focus
        
        3. TECH STACK ANALYSIS:
           - Primary languages from their repos
           - Frameworks they're using (React, Next.js, etc.)
           - Tools they're interested in (based on stars)
        
        Return detailed JSON:
        {{
            "primary_intent": "building|exploring|learning|launching",
            "confidence": 0.9,
            "evidence": ["specific repo names and activities that show this intent"],
            "skill_context": "their expertise level in their stated interests",
            "tech_interests": ["specific technologies from their profile + GitHub activity"],
            "current_projects": ["actual project names from their recent repos"],
            "growth_areas": ["skills they're developing based on stars/repos"],
            "career_stage": "startup founder|developer|researcher based on activity",
            "opportunity_preferences": ["hackathons", "funding", "tools", "learning"],
            "specific_interests": {{
                "web3": "level of blockchain involvement",
                "ai": "level of AI/ML involvement", 
                "startup": "stage of startup journey",
                "hackathon": "competition activity level"
            }}
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1500,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "You are a developer behavior analyst. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            intent_data = json.loads(response.choices[0].message.content)
            return intent_data
        except Exception as e:
            print(f"⚠️ Intent analysis failed: {e}")
            # Fallback analysis based on GitHub data
            return self._fallback_intent_analysis(github_data, user_profile)
    
    def _fallback_intent_analysis(self, github_data: dict, user_profile: dict) -> Dict[str, Any]:
        """Fallback intent analysis when AI parsing fails"""
        
        # Analyze recent activity patterns
        recent_repos = github_data.get('recent_repos', [])
        starred_repos = github_data.get('interests_from_stars', [])
        repo_analysis = github_data.get('repo_analysis', {})
        
        # Determine primary intent based on activity patterns
        if len(recent_repos) > 5:
            primary_intent = "building"
        elif len(starred_repos) > 10:
            primary_intent = "exploring"
        else:
            primary_intent = "learning"
        
        # Extract tech interests
        top_languages = [lang[0] for lang in repo_analysis.get('top_languages', [])[:5]]
        tech_interests = list(set(top_languages + user_profile.get('interests', [])))
        
        return {
            "primary_intent": primary_intent,
            "confidence": 0.6,
            "evidence": [
                f"Recent activity: {len(recent_repos)} repositories",
                f"Starred repos: {len(starred_repos)} items",
                f"Top languages: {', '.join(top_languages[:3])}"
            ],
            "skill_context": "intermediate developer",
            "time_investment": "evening/weekend coding",
            "likely_next_actions": [
                "Continue current projects",
                "Explore new technologies",
                "Build portfolio projects"
            ],
            "pain_points": [
                "Time management",
                "Technology choice paralysis"
            ],
            "growth_areas": top_languages[:3],
            "current_projects": [repo.get('name', 'Unknown') for repo in recent_repos[:3]],
            "tech_interests": tech_interests,
            "career_stage": "mid-level"
        }
    
    async def analyze_engagement_patterns(self, github_data: dict) -> Dict[str, Any]:
        """Analyze engagement patterns for optimal content timing"""
        
        prompt = f"""
        Analyze GitHub engagement patterns to optimize content delivery:
        
        GITHUB DATA: {json.dumps(github_data, indent=2)}
        
        Determine:
        1. Optimal content timing (when they're most active)
        2. Preferred content depth (quick reads vs deep dives)
        3. Engagement style (hands-on vs theoretical)
        4. Learning preferences (tutorials vs examples vs documentation)
        5. Communication style (technical vs business-focused)
        
        Return JSON:
        {{
            "optimal_timing": "morning/afternoon/evening",
            "content_depth": "quick/medium/deep",
            "engagement_style": "hands-on/theoretical/mixed",
            "learning_preference": "tutorials/examples/docs",
            "communication_style": "technical/business/mixed",
            "attention_span": "short/medium/long",
            "interaction_preference": "read-only/hands-on/collaborative"
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            max_tokens=800,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            engagement_data = json.loads(response.choices[0].message.content)
            return engagement_data
        except:
            return {
                "optimal_timing": "evening",
                "content_depth": "medium",
                "engagement_style": "hands-on",
                "learning_preference": "examples",
                "communication_style": "technical",
                "attention_span": "medium",
                "interaction_preference": "hands-on"
            }
    
    def get_intent_based_subject_line(self, user_intent: dict, date: str) -> str:
        """Generate clean, simple subject lines"""
        return f"Update of the day: {date}"
    
    def get_personalization_note(self, user_intent: dict) -> str:
        """Generate personalization note for email"""
        
        intent_notes = {
            "exploring": "Based on your exploration focus",
            "building": "Based on your active development phase",
            "learning": "Based on your skill development journey",
            "launching": "Based on your launch preparation",
            "pivoting": "Based on your tech stack evolution",
            "scaling": "Based on your growth phase"
        }
        
        primary_intent = user_intent.get('primary_intent', 'exploring')
        return intent_notes.get(primary_intent, "Based on your current focus")
