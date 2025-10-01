"""
Web Research Aggregator
Combines data from GitHub, HackerNews, and enhanced web crawling for comprehensive research
"""
from typing import Dict, Any, List
from .github_api import GitHubAPIClient
from .hackernews_api import HackerNewsAPIClient
from .enhanced_crawler import EnhancedWebCrawler
from .opportunity_finder import OpportunityFinder

class WebResearchAggregator:
    def __init__(self, github_token: str = None):
        self.github_client = GitHubAPIClient(github_token)
        self.hn_client = HackerNewsAPIClient()
        self.enhanced_crawler = EnhancedWebCrawler()
        self.opportunity_finder = OpportunityFinder()
    
    async def gather_comprehensive_research(self, user_profile: dict) -> Dict[str, Any]:
        """Gather comprehensive research data for editorial content"""
        print("🔍 Gathering comprehensive research data...")
        
        # Extract user context
        github_username = user_profile.get("github_username")
        
        research_data = {}
        
        try:
            # 1. Get GitHub user context if username provided
            if github_username:
                print(f"  👤 Analyzing GitHub profile: {github_username}")
                user_context = await self.github_client.get_user_context(github_username)
                research_data["user_context"] = user_context
            
            # 2. Get trending repositories (fresh data)
            print("  📈 Fetching fresh trending repositories...")
            trending_repos = await self.github_client.get_trending_repositories(days_back=3, limit=25)
            research_data["trending_repos"] = trending_repos
            
            # 3. Get language-specific trends (inferred from user's repos)
            if github_username and research_data.get("user_context", {}).get("repo_analysis"):
                inferred_languages = [lang[0] for lang in research_data["user_context"]["repo_analysis"].get("top_languages", [])[:3]]
                if inferred_languages:
                    print(f"  💻 Analyzing trends for inferred languages: {', '.join(inferred_languages)}")
                    language_trends = await self.github_client.get_language_trends(inferred_languages)
                    research_data["language_trends"] = language_trends
            
            # 4. Get HackerNews stories
            print("  📰 Fetching HackerNews stories...")
            hn_stories = await self.hn_client.get_trending_stories()
            research_data["hackernews_stories"] = hn_stories
            
            # 5. Get categorized HN stories
            ai_stories = await self.hn_client.get_stories_by_category("ai")
            programming_stories = await self.hn_client.get_stories_by_category("programming")
            startup_stories = await self.hn_client.get_stories_by_category("startup")
            
            research_data["categorized_stories"] = {
                "ai": ai_stories,
                "programming": programming_stories,
                "startup": startup_stories
            }
            
            # 6. Enhanced web crawling for niche content
            print("  🕷️ Enhanced web crawling for niche content...")
            user_interests = user_profile.get('interests', [])
            crawled_data = await self.enhanced_crawler.crawl_comprehensive_content(user_interests)
            research_data.update(crawled_data)
            
            print(f"✅ Research complete: {len(trending_repos)} repos, {len(hn_stories)} stories, {len(crawled_data.get('fresh_updates', []))} web updates")
            return research_data
            
        except Exception as e:
            print(f"❌ Research aggregation failed: {e}")
            return {}
    
    def analyze_research_relevance(self, research_data: dict, user_interests: List[str]) -> Dict[str, Any]:
        """Analyze research data relevance to user interests"""
        relevant_data = {
            "high_relevance": [],
            "medium_relevance": [],
            "trending_topics": [],
            "interest_matches": {}
        }
        
        try:
            # Analyze repo relevance
            for repo in research_data.get("trending_repos", []):
                relevance_score = self._calculate_relevance(repo, user_interests)
                if relevance_score > 0.7:
                    relevant_data["high_relevance"].append(repo)
                elif relevance_score > 0.4:
                    relevant_data["medium_relevance"].append(repo)
            
            # Extract trending topics
            all_topics = []
            for repo in research_data.get("trending_repos", []):
                all_topics.extend(repo.get("topics", []))
            
            # Count topic frequency
            topic_counts = {}
            for topic in all_topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Get most trending topics
            relevant_data["trending_topics"] = sorted(
                topic_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            return relevant_data
            
        except Exception as e:
            print(f"⚠️ Relevance analysis failed: {e}")
            return relevant_data
    
    def _calculate_relevance(self, item: dict, user_interests: List[str]) -> float:
        """Calculate relevance score for research item"""
        score = 0.0
        
        # Check description and topics
        text_to_check = f"{item.get('description', '')} {' '.join(item.get('topics', []))}"
        text_lower = text_to_check.lower()
        
        for interest in user_interests:
            if interest.lower() in text_lower:
                score += 0.3
        
        # Language match
        if item.get("language") and item["language"].lower() in [i.lower() for i in user_interests]:
            score += 0.4
        
        return min(score, 1.0)
    
    async def gather_comprehensive_research_with_opportunities(self, user_profile: dict) -> Dict[str, Any]:
        """Enhanced version with real opportunities (hackathons, jobs)"""

        # Get the standard research data
        research_data = await self.gather_comprehensive_research(user_profile)

        # Add real opportunities from Devpost + YC Jobs
        print("  🎯 Finding real opportunities (hackathons + jobs)...")
        try:
            opportunities = await self.opportunity_finder.find_real_opportunities(
                user_profile.get('interests', [])
            )

            # Add opportunities to research data
            research_data["opportunities"] = opportunities

            # Log what we found
            hackathon_count = len(opportunities.get('hackathons', []))
            job_count = len(opportunities.get('jobs', []))
            print(f"  ✅ Opportunities: {hackathon_count} hackathons, {job_count} jobs")

        except Exception as e:
            print(f"  ⚠️ Opportunity finding failed: {e}")
            research_data["opportunities"] = {"hackathons": [], "jobs": [], "funding": [], "events": []}

        return research_data
