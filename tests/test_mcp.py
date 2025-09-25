"""
Tests for MCP integration modules
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.mcp.manager import MCPManager
from src.mcp.resend_mcp import ResendMCP
from src.mcp.github_mcp import GitHubMCP
from src.mcp.postgres_mcp import PostgresMCP
from src.mcp.web_scraper_mcp import WebScraperMCP

class TestMCPManager:
    """Test MCP Manager functionality"""
    
    @pytest.mark.asyncio
    async def test_gather_trending_context(self):
        """Test gathering trending context from all sources"""
        manager = MCPManager()
        
        trending_data = await manager.gather_trending_context()
        
        assert trending_data is not None
        assert hasattr(trending_data, 'github_trending')
        assert hasattr(trending_data, 'hackernews_top')
        assert hasattr(trending_data, 'producthunt_featured')
        assert hasattr(trending_data, 'reddit_hot')
        assert hasattr(trending_data, 'twitter_trending')
    
    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test email sending functionality"""
        manager = MCPManager()
        
        result = await manager.send_email(
            to_email="test@example.com",
            subject="Test Email",
            html_content="<h1>Test</h1>",
            text_content="Test"
        )
        
        assert result is not None
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_get_user_github_data(self):
        """Test GitHub user data retrieval"""
        manager = MCPManager()
        
        github_data = await manager.get_user_github_data("testuser")
        
        assert github_data is not None
        assert "username" in github_data

class TestResendMCP:
    """Test Resend MCP functionality"""
    
    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test email sending via Resend MCP"""
        resend = ResendMCP()
        
        result = await resend.send_email(
            to_email="test@example.com",
            subject="Test Email",
            html_content="<h1>Test</h1>",
            text_content="Test"
        )
        
        assert result is not None
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_test_connection(self):
        """Test MCP connection"""
        resend = ResendMCP()
        
        result = await resend.test_connection()
        assert result is True

class TestGitHubMCP:
    """Test GitHub MCP functionality"""
    
    @pytest.mark.asyncio
    async def test_get_user_profile(self):
        """Test GitHub user profile retrieval"""
        github = GitHubMCP()
        
        profile = await github.get_user_profile("testuser")
        
        assert profile is not None
        assert "username" in profile
    
    @pytest.mark.asyncio
    async def test_get_trending_repositories(self):
        """Test trending repositories retrieval"""
        github = GitHubMCP()
        
        repos = await github.get_trending_repositories()
        
        assert isinstance(repos, list)
        if repos:
            assert "name" in repos[0]

class TestPostgresMCP:
    """Test PostgreSQL MCP functionality"""
    
    @pytest.mark.asyncio
    async def test_execute_query(self):
        """Test SQL query execution"""
        postgres = PostgresMCP()
        
        result = await postgres.execute_query("SELECT 1 as test")
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self):
        """Test user retrieval by email"""
        postgres = PostgresMCP()
        
        user = await postgres.get_user_by_email("test@example.com")
        
        # Should return None for non-existent user
        assert user is None or isinstance(user, dict)

class TestWebScraperMCP:
    """Test Web Scraper MCP functionality"""
    
    @pytest.mark.asyncio
    async def test_scrape_url(self):
        """Test URL scraping functionality"""
        scraper = WebScraperMCP()
        
        result = await scraper.scrape_url("https://example.com")
        
        assert result is not None
        assert "url" in result
    
    @pytest.mark.asyncio
    async def test_extract_trending_topics(self):
        """Test trending topics extraction"""
        scraper = WebScraperMCP()
        
        topics = await scraper.extract_trending_topics("hackernews")
        
        assert isinstance(topics, list)
