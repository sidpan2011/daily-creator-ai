"""
Real GitHub API Client
Fetches live trending repositories and user data
"""
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class GitHubAPIClient:
    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Persnally-Newsletter/1.0"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    async def get_user_context(self, username: str) -> Dict[str, Any]:
        """Get comprehensive user's GitHub context including private repos"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get user info
                user_response = await client.get(
                    f"{self.base_url}/users/{username}",
                    headers=self.headers
                )
                
                # Get ALL user's repositories (including private if token is provided)
                repos_response = await client.get(
                    f"{self.base_url}/user/repos" if self.token else f"{self.base_url}/users/{username}/repos",
                    params={"sort": "updated", "per_page": 30, "visibility": "all"},
                    headers=self.headers
                )
                
                # Get user's starred repos for interest analysis
                starred_response = await client.get(
                    f"{self.base_url}/users/{username}/starred",
                    params={"per_page": 30},
                    headers=self.headers
                )
                
                # Get user's README content for deeper analysis
                readme_content = await self._get_user_readme(client, username)
                
                if all(r.status_code == 200 for r in [user_response, repos_response, starred_response]):
                    user_data = user_response.json()
                    repos = repos_response.json()
                    starred = starred_response.json()
                    
                    # Log GitHub data for transparency
                    print(f"    📊 GitHub Data Retrieved:")
                    print(f"      - User: {user_data.get('name', 'N/A')} ({user_data.get('public_repos', 0)} public repos)")
                    print(f"      - Recent Repos: {len(repos)} repos analyzed")
                    print(f"      - Starred Repos: {len(starred)} starred repos")
                    
                    # Log specific repos for transparency
                    print(f"    🔍 Recent Repositories:")
                    for i, repo in enumerate(repos[:5], 1):
                        repo_desc = repo.get('description') or 'No description'
                        print(f"      {i}. {repo['name']} ({repo.get('language', 'Unknown')}) - {repo_desc[:50]}...")
                    
                    print(f"    ⭐ Top Starred Repositories:")
                    for i, repo in enumerate(starred[:5], 1):
                        repo_desc = repo.get('description') or 'No description'
                        print(f"      {i}. {repo['full_name']} ({repo.get('language', 'Unknown')}) - {repo_desc[:50]}...")
                    
                    # Analyze repository patterns
                    repo_analysis = self._analyze_repository_patterns(repos)
                    
                    return {
                        "user_info": {
                            "name": user_data.get("name"),
                            "bio": user_data.get("bio"),
                            "public_repos": user_data.get("public_repos"),
                            "followers": user_data.get("followers"),
                            "location": user_data.get("location"),
                            "created_at": user_data.get("created_at"),
                            "updated_at": user_data.get("updated_at")
                        },
                        "recent_repos": [
                            {
                                "name": repo["name"],
                                "full_name": repo["full_name"],
                                "description": repo["description"],
                                "language": repo["language"],
                                "stars": repo["stargazers_count"],
                                "updated_at": repo["updated_at"],
                                "created_at": repo["created_at"],
                                "topics": repo.get("topics", []),
                                "private": repo.get("private", False),
                                "fork": repo.get("fork", False)
                            }
                            for repo in repos[:15]
                        ],
                        "interests_from_stars": [
                            {
                                "name": repo["full_name"],
                                "description": repo["description"],
                                "language": repo["language"],
                                "topics": repo.get("topics", []),
                                "stars": repo["stargazers_count"]
                            }
                            for repo in starred[:15]
                        ],
                        "readme_content": readme_content,
                        "repo_analysis": repo_analysis
                    }
                
        except Exception as e:
            print(f"❌ Failed to get user context: {e}")
            return {}
    
    async def _get_user_readme(self, client: httpx.AsyncClient, username: str) -> str:
        """Get user's README content from their profile"""
        try:
            # Try to get README from user's profile
            readme_response = await client.get(
                f"{self.base_url}/repos/{username}/{username}/readme",
                headers=self.headers
            )
            
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                import base64
                content = base64.b64decode(readme_data["content"]).decode("utf-8")
                return content[:2000]  # Limit size
        except:
            pass
        
        return ""
    
    def _analyze_repository_patterns(self, repos: list) -> Dict[str, Any]:
        """Analyze repository patterns to infer user's skills and interests"""
        languages = {}
        topics = {}
        recent_activity = []
        
        for repo in repos:
            # Language analysis
            if repo.get("language"):
                languages[repo["language"]] = languages.get(repo["language"], 0) + 1
            
            # Topic analysis
            for topic in repo.get("topics", []):
                topics[topic] = topics.get(topic, 0) + 1
            
            # Recent activity analysis
            if repo.get("updated_at"):
                recent_activity.append({
                    "name": repo["name"],
                    "updated_at": repo["updated_at"],
                    "language": repo.get("language"),
                    "description": repo.get("description")
                })
        
        # Sort by frequency
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "top_languages": top_languages,
            "top_topics": top_topics,
            "recent_activity": sorted(recent_activity, key=lambda x: x["updated_at"], reverse=True)[:5],
            "total_repos": len(repos),
            "private_repos": len([r for r in repos if r.get("private", False)])
        }
    
    async def get_trending_repositories(self, days_back: int = 3, limit: int = 25) -> List[Dict[str, Any]]:
        """Get real trending repositories with better freshness"""
        try:
            # Calculate date for trending search - shorter window for fresher data
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            # More diverse and current search queries
            search_queries = [
                f"created:>{since_date} stars:>20",  # New repos with decent traction
                f"pushed:>{since_date} stars:>50",   # Recently updated popular repos
                f"language:Python created:>{since_date} stars:>10",
                f"language:JavaScript created:>{since_date} stars:>10", 
                f"language:TypeScript created:>{since_date} stars:>10",
                f"language:Rust created:>{since_date} stars:>5",
                f"topic:ai created:>{since_date} stars:>15",
                f"topic:developer-tools created:>{since_date} stars:>10",
                f"topic:machine-learning created:>{since_date} stars:>10",
                f"topic:web3 created:>{since_date} stars:>5",
                f"topic:automation created:>{since_date} stars:>5"
            ]
            
            all_repos = []
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for query in search_queries:
                    try:
                        response = await client.get(
                            f"{self.base_url}/search/repositories",
                            params={
                                "q": query,
                                "sort": "stars",
                                "order": "desc",
                                "per_page": 3  # Fewer per query, more queries
                            },
                            headers=self.headers
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            for repo in data.get("items", []):
                                # Calculate freshness score
                                created_date = datetime.fromisoformat(repo["created_at"].replace("Z", "+00:00"))
                                days_old = (datetime.now(created_date.tzinfo) - created_date).days
                                freshness_score = max(0, 10 - days_old)  # Higher score for newer repos
                                
                                all_repos.append({
                                    "name": repo["full_name"],
                                    "description": repo["description"] or "No description",
                                    "stars": repo["stargazers_count"],
                                    "language": repo["language"] or "Unknown",
                                    "url": repo["html_url"],
                                    "topics": repo.get("topics", []),
                                    "created_at": repo["created_at"],
                                    "updated_at": repo["updated_at"],
                                    "forks": repo["forks_count"],
                                    "open_issues": repo["open_issues_count"],
                                    "freshness_score": freshness_score,
                                    "days_old": days_old
                                })
                        
                        # Rate limiting courtesy
                        await asyncio.sleep(0.3)
                        
                    except Exception as e:
                        print(f"⚠️ Query failed: {query} - {e}")
                        continue
            
            # Remove duplicates and sort by freshness + stars
            unique_repos = {repo["name"]: repo for repo in all_repos}
            sorted_repos = sorted(
                unique_repos.values(), 
                key=lambda x: (x["freshness_score"], x["stars"]), 
                reverse=True
            )
            
            print(f"✅ Retrieved {len(sorted_repos)} trending repositories (freshness-focused)")
            return sorted_repos[:limit]
            
        except Exception as e:
            print(f"❌ Failed to get trending repositories: {e}")
            return []
    
    async def get_language_trends(self, languages: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Get trending repos for specific languages"""
        try:
            trends_by_language = {}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for language in languages:
                    try:
                        response = await client.get(
                            f"{self.base_url}/search/repositories",
                            params={
                                "q": f"language:{language} created:>2024-09-01 stars:>20",
                                "sort": "stars",
                                "order": "desc", 
                                "per_page": 5
                            },
                            headers=self.headers
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            trends_by_language[language] = [
                                {
                                    "name": repo["full_name"],
                                    "description": repo["description"] or "No description",
                                    "stars": repo["stargazers_count"],
                                    "url": repo["html_url"]
                                }
                                for repo in data.get("items", [])
                            ]
                        
                        await asyncio.sleep(0.5)  # Rate limiting
                        
                    except Exception as e:
                        print(f"⚠️ Language trend failed for {language}: {e}")
                        trends_by_language[language] = []
            
            return trends_by_language
            
        except Exception as e:
            print(f"❌ Failed to get language trends: {e}")
            return {}
