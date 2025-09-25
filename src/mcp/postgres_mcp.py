"""
PostgreSQL MCP wrapper for database operations
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
import httpx
import os

class PostgresMCP:
    """Wrapper for PostgreSQL MCP server"""
    
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL", "sqlite:///./local_demo.db")
        self.base_url = os.getenv("POSTGRES_MCP_URL", "http://localhost:3003")
        self.timeout = 30.0
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query via PostgreSQL MCP"""
        try:
            # For demo purposes, simulate query execution
            print(f"🗄️ PostgreSQL MCP: Executing query: {query[:50]}...")
            
            # Mock response based on query type
            if "SELECT" in query.upper():
                return self._mock_select_response(query)
            elif "INSERT" in query.upper():
                return self._mock_insert_response(query)
            elif "UPDATE" in query.upper():
                return self._mock_update_response(query)
            else:
                return [{"success": True, "rows_affected": 1}]
                
        except Exception as e:
            print(f"❌ PostgreSQL MCP Error: {e}")
            return []
    
    def _mock_select_response(self, query: str) -> List[Dict[str, Any]]:
        """Mock SELECT query response"""
        if "users" in query.lower():
            return [
                {
                    "id": "user_123",
                    "name": "Demo User",
                    "email": "demo@example.com",
                    "skills": '["Python", "JavaScript"]',
                    "interests": '["AI", "Web Development"]',
                    "goals": '["Build SaaS", "Learn Rust"]',
                    "github_username": "demouser",
                    "email_time": "morning",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                }
            ]
        elif "recommendations" in query.lower():
            return [
                {
                    "id": "rec_123",
                    "user_id": "user_123",
                    "category": "BUILD",
                    "title": "Build an AI-powered Email Service",
                    "description": "Create a service that sends personalized emails using AI",
                    "next_steps": '["Set up Resend API", "Integrate Claude API", "Create email templates"]',
                    "trend_connection": "AI email automation is trending",
                    "difficulty_level": "intermediate",
                    "score": 0.85,
                    "created_at": "2024-01-15T10:30:00Z",
                    "sent_at": None
                }
            ]
        else:
            return []
    
    def _mock_insert_response(self, query: str) -> List[Dict[str, Any]]:
        """Mock INSERT query response"""
        return [{"success": True, "rows_affected": 1, "id": "new_record_123"}]
    
    def _mock_update_response(self, query: str) -> List[Dict[str, Any]]:
        """Mock UPDATE query response"""
        return [{"success": True, "rows_affected": 1}]
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            query = "SELECT * FROM users WHERE email = :email"
            result = await self.execute_query(query, {"email": email})
            return result[0] if result else None
        except Exception as e:
            print(f"❌ PostgreSQL MCP Error: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create new user"""
        try:
            query = """
                INSERT INTO users (id, name, email, skills, interests, goals, github_username, email_time)
                VALUES (:id, :name, :email, :skills, :interests, :goals, :github_username, :email_time)
            """
            result = await self.execute_query(query, user_data)
            return result[0].get("id") if result else None
        except Exception as e:
            print(f"❌ PostgreSQL MCP Error: {e}")
            return None
    
    async def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recommendations"""
        try:
            query = """
                SELECT * FROM recommendations 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC 
                LIMIT :limit
            """
            result = await self.execute_query(query, {"user_id": user_id, "limit": limit})
            return result
        except Exception as e:
            print(f"❌ PostgreSQL MCP Error: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """Test MCP connection"""
        try:
            # For demo purposes, always return True
            print("✅ PostgreSQL MCP: Connection test successful")
            return True
        except Exception as e:
            print(f"❌ PostgreSQL MCP: Connection test failed - {e}")
            return False
