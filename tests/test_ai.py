"""
Tests for AI processing modules
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from src.ai.processor import AIProcessor
from src.models.user import User
from src.models.trending import TrendingContext, TrendingItem, TrendingSource
from datetime import datetime

class TestAIProcessor:
    """Test AI Processor functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = AIProcessor()
        self.test_user = User(
            id="test_user_123",
            name="Test User",
            email="test@example.com",
            skills=["Python", "JavaScript"],
            interests=["AI", "Web Development"],
            goals=["Build a SaaS", "Learn Rust"],
            github_username="testuser",
            email_time="morning",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.test_trending_data = TrendingContext(
            github_trending=[
                TrendingItem(
                    title="Test Repo",
                    description="Test description",
                    url="https://github.com/test/repo",
                    source=TrendingSource.GITHUB,
                    score=90.0,
                    tags=["test", "demo"],
                    created_at=datetime.utcnow()
                )
            ],
            hackernews_top=[],
            producthunt_featured=[],
            reddit_hot=[],
            twitter_trending=[],
            fetched_at=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_mock(self):
        """Test recommendation generation with mock data"""
        recommendations = await self.processor.generate_recommendations(
            self.test_user, 
            self.test_trending_data
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 3  # Should generate exactly 3 recommendations
        
        for rec in recommendations:
            assert rec.user_id == self.test_user.id
            assert rec.title is not None
            assert rec.description is not None
            assert len(rec.next_steps) > 0
            assert 0.0 <= rec.score <= 1.0
    
    @pytest.mark.asyncio
    async def test_generate_email_content(self):
        """Test email content generation"""
        recommendations = await self.processor.generate_recommendations(
            self.test_user, 
            self.test_trending_data
        )
        
        email_content = await self.processor.generate_email_content(
            self.test_user, 
            recommendations
        )
        
        assert isinstance(email_content, dict)
        assert "subject" in email_content
        assert "greeting" in email_content
        assert "intro" in email_content
        assert "recommendations_text" in email_content
        assert "closing" in email_content
    
    @pytest.mark.asyncio
    async def test_analyze_trends(self):
        """Test trend analysis functionality"""
        analysis = await self.processor.analyze_trends(self.test_trending_data)
        
        assert isinstance(analysis, str)
        assert len(analysis) > 0
    
    def test_mock_recommendations(self):
        """Test mock recommendation generation"""
        recommendations = self.processor._get_mock_recommendations(self.test_user)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 3
        
        for rec in recommendations:
            assert rec.user_id == self.test_user.id
            assert rec.title is not None
            assert rec.description is not None
            assert len(rec.next_steps) > 0
            assert 0.0 <= rec.score <= 1.0
    
    def test_mock_email_content(self):
        """Test mock email content generation"""
        recommendations = self.processor._get_mock_recommendations(self.test_user)
        
        email_content = self.processor._get_mock_email_content(
            self.test_user, 
            recommendations
        )
        
        assert isinstance(email_content, dict)
        assert "subject" in email_content
        assert "greeting" in email_content
        assert "intro" in email_content
        assert "recommendations_text" in email_content
        assert "closing" in email_content
    
    def test_mock_trend_analysis(self):
        """Test mock trend analysis"""
        analysis = self.processor._get_mock_trend_analysis()
        
        assert isinstance(analysis, str)
        assert len(analysis) > 0
        assert "AI Development" in analysis
