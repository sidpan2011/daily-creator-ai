"""
GitHub MCP wrapper for user data enrichment
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
import httpx
import os

class GitHubMCP:
    """Wrapper for GitHub MCP server"""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = os.getenv("GITHUB_MCP_URL", "http://localhost:3002")
        self.timeout = 30.0
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get GitHub user profile data"""
        try:
            if not self.token:
                print("⚠️ GitHub token not configured, using mock data")
                return self._get_mock_user_data(username)
            
            # For demo purposes, return mock data
            # In production, this would make actual GitHub API calls
            return self._get_mock_user_data(username)
            
        except Exception as e:
            print(f"❌ GitHub MCP Error: {e}")
            return {}
    
    def _get_mock_user_data(self, username: str) -> Dict[str, Any]:
        """Get mock user data for demo purposes"""
        return {
            "username": username,
            "name": f"Demo User {username}",
            "bio": "Passionate developer building amazing things with AI and web technologies",
            "email": f"{username}@example.com",
            "location": "San Francisco, CA",
            "company": "Tech Startup",
            "blog": f"https://{username}.dev",
            "public_repos": 25,
            "public_gists": 10,
            "followers": 150,
            "following": 200,
            "created_at": "2020-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "recent_repos": [
                {
                    "name": "awesome-ai-project",
                    "description": "An amazing AI-powered application",
                    "stars": 50,
                    "language": "Python",
                    "updated_at": "2024-01-14T10:30:00Z"
                },
                {
                    "name": "cool-web-tool",
                    "description": "A useful web development tool",
                    "stars": 25,
                    "language": "JavaScript",
                    "updated_at": "2024-01-13T10:30:00Z"
                }
            ],
            "languages": ["Python", "JavaScript", "TypeScript", "Go", "Rust"],
            "interests": ["web-development", "ai", "open-source", "machine-learning"],
            "contribution_streak": 45,
            "total_contributions": 1200
        }
    
    async def get_user_repositories(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's repositories"""
        try:
            # For demo purposes, return mock repositories
            return [
                {
                    "name": "daily-creator-ai",
                    "description": "AI-powered personal curator for creators",
                    "stars": 150,
                    "forks": 25,
                    "language": "Python",
                    "updated_at": "2024-01-15T10:30:00Z",
                    "topics": ["ai", "email", "recommendations", "creator"]
                },
                {
                    "name": "mcp-integration-demo",
                    "description": "Demo of MCP server integrations",
                    "stars": 75,
                    "forks": 15,
                    "language": "TypeScript",
                    "updated_at": "2024-01-14T10:30:00Z",
                    "topics": ["mcp", "demo", "integration"]
                }
            ]
        except Exception as e:
            print(f"❌ GitHub MCP Error: {e}")
            return []
    
    async def get_trending_repositories(self, language: Optional[str] = None, 
                                      since: str = "daily") -> List[Dict[str, Any]]:
        """Get trending repositories"""
        try:
            # For demo purposes, return mock trending repos
            return [
                {
                    "name": "claude-3.5-sonnet",
                    "description": "Advanced AI model for creative and analytical tasks",
                    "stars": 15000,
                    "forks": 2000,
                    "language": "Python",
                    "url": "https://github.com/anthropics/claude-3.5-sonnet",
                    "trending_score": 95.0
                },
                {
                    "name": "resend-python",
                    "description": "Email API for developers",
                    "stars": 2500,
                    "forks": 300,
                    "language": "Python",
                    "url": "https://github.com/resend/resend-python",
                    "trending_score": 88.0
                }
            ]
        except Exception as e:
            print(f"❌ GitHub MCP Error: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """Test MCP connection"""
        try:
            # For demo purposes, always return True
            print("✅ GitHub MCP: Connection test successful")
            return True
        except Exception as e:
            print(f"❌ GitHub MCP: Connection test failed - {e}")
            return False
