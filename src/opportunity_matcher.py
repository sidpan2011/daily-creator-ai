"""
Smart Opportunity Matcher
Matches user intent with 5 most relevant opportunities from research data
"""
import openai
import json
from typing import Dict, Any, List
from datetime import datetime

class OpportunityMatcher:
    def __init__(self, config):
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    async def find_daily_5(self, user_intent: dict, research_data: dict) -> List[Dict[str, Any]]:
        """Match user intent with 5 most relevant opportunities"""
        
        prompt = f"""
        You are creating a personalized Daily 5 for a developer with these specific interests:
        USER PROFILE: {json.dumps(user_intent, indent=2)}
        
        REAL GITHUB TRENDING: {json.dumps(research_data.get('trending_repos', [])[:15], indent=2)}
        REAL HACKERNEWS: {json.dumps(research_data.get('hackernews_stories', [])[:15], indent=2)}
        USER'S GITHUB ACTIVITY: {json.dumps(research_data.get('user_context', {}), indent=2)}
        
        Create 5 HIGHLY SPECIFIC opportunities that match their interests:
        
        MATCHING RULES:
        - If user likes "web3/blockchain" → find blockchain repos, DeFi projects, crypto hackathons
        - If user likes "ai/ml" → find AI repos, ML papers, AI hackathons, new models
        - If user likes "hackathon" → find ACTUAL hackathons with dates/prizes
        - If user likes "startup" → find funding news, YC companies, startup tools
        
        Categories:
        🎯 FOR YOU - Perfect match to their interests (web3 + AI + startup)
        ⚡ ACT NOW - Real hackathons, job applications, funding deadlines
        🧠 LEVEL UP - Advanced tutorials in their interest areas  
        💰 OPPORTUNITY - Real jobs, grants, accelerators in their field
        🔮 WHAT'S NEXT - Emerging trends in web3/AI/startup space
        
        For each item:
        1. Use REAL data from above sources
        2. Explain specific relevance to their interests
        3. Include actionable next steps with URLs
        4. Add relevant metrics (stars, funding amounts, dates)
        5. Make it feel personally curated
        
        Example for web3 interest:
        "Solana Foundation just announced a $50M hackathon focused on AI + DeFi. Given your background in both AI/ML and blockchain (evident from your PyTorch stars and Solana repos), this could be perfect. Applications close Oct 15."
        
        Return JSON array:
        [
            {{
                "category": "🎯 FOR YOU",
                "title": "Specific title from real data",
                "description": "Why this specifically matters to this user's interests and background",
                "action": "Exact next step with URL",
                "relevance_score": 9,
                "source": "GitHub/HackerNews",
                "meta_info": "Real metrics/dates",
                "image_query": "search term for relevant image"
            }}
        ]
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2500,
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a personalized opportunity curator. Always return valid JSON array with exactly 5 items."},
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            daily_5_data = json.loads(response.choices[0].message.content)
            return daily_5_data
        except Exception as e:
            print(f"⚠️ Daily 5 matching failed: {e}")
            return self._fallback_daily_5(user_intent, research_data)
    
    def _fallback_daily_5(self, user_intent: dict, research_data: dict) -> List[Dict[str, Any]]:
        """Fallback Daily 5 with smart matching when AI parsing fails"""
        
        trending_repos = research_data.get('trending_repos', [])[:10]
        hackernews_stories = research_data.get('hackernews_stories', [])[:10]
        user_interests = user_intent.get('tech_interests', ['technology'])
        github_context = research_data.get('user_context', {})
        
        # Smart matching based on user interests
        def matches_interests(text):
            if not text:
                return False
            text_lower = text.lower()
            interest_keywords = {
                'web3': ['blockchain', 'crypto', 'defi', 'solana', 'ethereum', 'web3'],
                'ai': ['ai', 'ml', 'machine learning', 'neural', 'gpt', 'llm', 'pytorch'],
                'startup': ['startup', 'funding', 'vc', 'accelerator', 'yc'],
                'hackathon': ['hackathon', 'competition', 'contest', 'prize']
            }
            
            for interest in user_interests:
                if any(keyword in text_lower for keyword in interest_keywords.get(interest.split('/')[0], [interest.lower()])):
                    return True
            return False
        
        daily_5 = []
        
        # Find most relevant repos
        relevant_repos = [repo for repo in trending_repos if matches_interests(repo.get('description', '') + ' ' + repo.get('name', ''))]
        if not relevant_repos:
            relevant_repos = trending_repos[:3]
        
        # Find most relevant HN stories
        relevant_stories = [story for story in hackernews_stories if matches_interests(story.get('title', ''))]
        if not relevant_stories:
            relevant_stories = hackernews_stories[:2]
        
        # FOR YOU - Best matching repo
        if relevant_repos:
            best_repo = relevant_repos[0]
            daily_5.append({
                "category": "🎯 FOR YOU",
                "title": best_repo.get('name', 'Trending Project'),
                "description": f"{best_repo.get('description', 'Trending repository')}. This matches your interests in {', '.join(user_interests[:2])} and could be valuable for your current projects.",
                "action": f"Explore the repository and consider contributing: {best_repo.get('html_url', 'GitHub')}",
                "relevance_score": 9,
                "source": "GitHub Trending",
                "meta_info": f"⭐ {best_repo.get('stargazers_count', 0)} stars • Language: {best_repo.get('language', 'N/A')}",
                "image_query": f"{best_repo.get('name', 'repository')} {best_repo.get('language', 'code')}"
            })
        
        # ACT NOW - Most relevant HN story
        if relevant_stories:
            urgent_story = relevant_stories[0]
            daily_5.append({
                "category": "⚡ ACT NOW",
                "title": urgent_story.get('title', 'Trending Discussion'),
                "description": f"Active discussion on HackerNews about {urgent_story.get('title', 'this topic')}. This is directly relevant to your interests and the community is actively engaging with it.",
                "action": f"Join the discussion and share your perspective: {urgent_story.get('url', 'HackerNews')}",
                "relevance_score": 8,
                "source": "HackerNews",
                "meta_info": f"💬 {urgent_story.get('descendants', 0)} comments • 📈 {urgent_story.get('score', 0)} points",
                "image_query": f"hackernews discussion {urgent_story.get('title', 'technology')[:30]}"
            })
        
        # LEVEL UP - Learning opportunity
        if len(relevant_repos) > 1:
            learning_repo = relevant_repos[1]
            daily_5.append({
                "category": "🧠 LEVEL UP",
                "title": learning_repo.get('name', 'Learning Resource'),
                "description": f"Advanced project: {learning_repo.get('description', 'Repository')}. Perfect for deepening your expertise in areas you're already exploring based on your GitHub activity.",
                "action": f"Study the implementation and architecture: {learning_repo.get('html_url', 'GitHub')}",
                "relevance_score": 7,
                "source": "GitHub",
                "meta_info": f"⭐ {learning_repo.get('stargazers_count', 0)} stars • Forks: {learning_repo.get('forks_count', 0)}",
                "image_query": f"{learning_repo.get('language', 'programming')} tutorial code"
            })
        
        # OPPORTUNITY - Career/business
        if len(relevant_stories) > 1:
            opp_story = relevant_stories[1]
            daily_5.append({
                "category": "💰 OPPORTUNITY",
                "title": opp_story.get('title', 'Industry Opportunity'),
                "description": f"Industry insight: {opp_story.get('title', 'Opportunity')}. This could reveal new opportunities in your field of interest or provide valuable market intelligence.",
                "action": f"Read and analyze for potential opportunities: {opp_story.get('url', 'HackerNews')}",
                "relevance_score": 8,
                "source": "HackerNews",
                "meta_info": f"💬 {opp_story.get('descendants', 0)} comments • Active discussion",
                "image_query": f"business opportunity {opp_story.get('title', 'startup')[:30]}"
            })
        
        # WHAT'S NEXT - Future trends
        if len(relevant_repos) > 2:
            future_repo = relevant_repos[2]
            daily_5.append({
                "category": "🔮 WHAT'S NEXT",
                "title": future_repo.get('name', 'Emerging Technology'),
                "description": f"Emerging trend: {future_repo.get('description', 'New technology')}. This represents the cutting edge of your field and could be important to track for future opportunities.",
                "action": f"Star and follow development: {future_repo.get('html_url', 'GitHub')}",
                "relevance_score": 7,
                "source": "GitHub",
                "meta_info": f"⭐ {future_repo.get('stargazers_count', 0)} stars • Recent activity",
                "image_query": f"future technology {future_repo.get('language', 'innovation')}"
            })
        
        return daily_5
    
    async def rank_opportunities(self, opportunities: List[Dict], user_intent: dict) -> List[Dict]:
        """Rank opportunities by relevance to user intent"""
        
        prompt = f"""
        Rank these opportunities by relevance to user intent:
        
        USER INTENT: {json.dumps(user_intent, indent=2)}
        OPPORTUNITIES: {json.dumps(opportunities, indent=2)}
        
        Rank each opportunity 1-10 based on:
        1. Perfect match to current intent
        2. Skill level appropriateness
        3. Time sensitivity
        4. Career/growth impact
        5. Learning value
        
        Return JSON with updated relevance scores and ranking.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            ranked_data = json.loads(response.choices[0].message.content)
            return ranked_data
        except:
            # Simple fallback ranking
            return sorted(opportunities, key=lambda x: x.get('relevance_score', 5), reverse=True)
    
    def format_opportunity_for_email(self, opportunity: Dict[str, Any]) -> Dict[str, str]:
        """Format opportunity for email display"""
        
        return {
            "category": opportunity.get('category', '📌 OPPORTUNITY'),
            "title": opportunity.get('title', 'Untitled Opportunity'),
            "description": opportunity.get('description', 'No description available'),
            "action": opportunity.get('action', 'Take action'),
            "timing": opportunity.get('timing', 'Time-sensitive'),
            "meta_info": opportunity.get('meta_info', ''),
            "source": opportunity.get('source', 'Unknown')
        }
    
    async def generate_opportunity_summary(self, daily_5: List[Dict], user_intent: dict) -> str:
        """Generate summary of why these 5 opportunities were selected"""
        
        prompt = f"""
        Generate a brief summary explaining why these 5 opportunities were selected:
        
        USER INTENT: {json.dumps(user_intent, indent=2)}
        SELECTED OPPORTUNITIES: {json.dumps(daily_5, indent=2)}
        
        Explain in 2-3 sentences why these specific opportunities match their current focus and goals.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            max_tokens=200,
            temperature=0.6,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content.strip()
