"""
Tests for API routes and functionality
"""

import pytest
import json
from fastapi.testclient import TestClient
from src.main import app
from src.models.user import UserProfile

client = TestClient(app)

class TestAPIRoutes:
    """Test API route functionality"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Daily Creator AI"
        assert "version" in data
    
    def test_register_user(self):
        """Test user registration endpoint"""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "skills": ["Python", "JavaScript"],
            "interests": ["AI", "Web Development"],
            "goals": ["Build a SaaS", "Learn Rust"],
            "github_username": "testuser",
            "email_time": "morning"
        }
        
        response = client.post("/api/users/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data
        assert "message" in data
    
    def test_register_user_invalid_data(self):
        """Test user registration with invalid data"""
        invalid_data = {
            "name": "Test User",
            "email": "invalid-email",  # Invalid email format
            "skills": ["Python"],
            "interests": ["AI"],
            "goals": ["Build a SaaS"]
        }
        
        response = client.post("/api/users/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_demo_users(self):
        """Test demo users endpoint"""
        response = client.get("/api/demo/users")
        assert response.status_code == 200
        
        data = response.json()
        assert "demo_users" in data
        assert isinstance(data["demo_users"], list)
    
    def test_get_demo_trends(self):
        """Test demo trends endpoint"""
        response = client.get("/api/demo/trends")
        assert response.status_code == 200
        
        data = response.json()
        assert "trends" in data
    
    def test_get_demo_recommendations(self):
        """Test demo recommendations endpoint"""
        response = client.get("/api/demo/recommendations")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommendations" in data
    
    def test_demo_simulation(self):
        """Test demo simulation endpoint"""
        response = client.post("/api/demo/simulate")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data
        assert "recommendations" in data
        assert "message" in data
    
    def test_get_user_not_found(self):
        """Test getting non-existent user"""
        response = client.get("/api/users/non_existent_user")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_generate_recommendations(self):
        """Test recommendation generation endpoint"""
        # First register a user
        user_data = {
            "name": "Test User",
            "email": "test2@example.com",
            "skills": ["Python", "JavaScript"],
            "interests": ["AI", "Web Development"],
            "goals": ["Build a SaaS", "Learn Rust"],
            "github_username": "testuser2",
            "email_time": "morning"
        }
        
        register_response = client.post("/api/users/register", json=user_data)
        assert register_response.status_code == 200
        
        user_id = register_response.json()["user_id"]
        
        # Generate recommendations
        response = client.post(f"/api/users/{user_id}/recommendations/generate")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommendations" in data
        assert "user_id" in data
        assert "generated_at" in data
        assert "total_count" in data
        assert data["total_count"] == 3
    
    def test_get_user_recommendations(self):
        """Test getting user recommendations"""
        # First register a user and generate recommendations
        user_data = {
            "name": "Test User",
            "email": "test3@example.com",
            "skills": ["Python", "JavaScript"],
            "interests": ["AI", "Web Development"],
            "goals": ["Build a SaaS", "Learn Rust"],
            "github_username": "testuser3",
            "email_time": "morning"
        }
        
        register_response = client.post("/api/users/register", json=user_data)
        user_id = register_response.json()["user_id"]
        
        # Generate recommendations
        client.post(f"/api/users/{user_id}/recommendations/generate")
        
        # Get recommendations
        response = client.get(f"/api/users/{user_id}/recommendations")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommendations" in data
        assert "user_id" in data
        assert "total_count" in data
        assert data["user_id"] == user_id
    
    def test_submit_feedback(self):
        """Test feedback submission"""
        # First register a user and generate recommendations
        user_data = {
            "name": "Test User",
            "email": "test4@example.com",
            "skills": ["Python", "JavaScript"],
            "interests": ["AI", "Web Development"],
            "goals": ["Build a SaaS", "Learn Rust"],
            "github_username": "testuser4",
            "email_time": "morning"
        }
        
        register_response = client.post("/api/users/register", json=user_data)
        user_id = register_response.json()["user_id"]
        
        # Generate recommendations
        rec_response = client.post(f"/api/users/{user_id}/recommendations/generate")
        recommendations = rec_response.json()["recommendations"]
        recommendation_id = recommendations[0]["id"]
        
        # Submit feedback
        feedback_data = {"feedback": "like"}
        response = client.post(
            f"/api/users/{user_id}/recommendations/{recommendation_id}/feedback",
            json=feedback_data
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data
