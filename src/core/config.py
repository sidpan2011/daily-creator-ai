"""
Configuration management for Daily Creator AI
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    def __init__(self):
        # Application
        self.app_name = "Daily Creator AI"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "True").lower() == "true"
        
        # AI Configuration
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Email Configuration
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "Daily Creator AI <noreply@dailycreator.ai>")
        
        # GitHub Integration
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./local_demo.db")
        
        # MCP Servers
        self.mcp_base_url = os.getenv("MCP_BASE_URL", "http://localhost:3000")
        self.resend_mcp_url = os.getenv("RESEND_MCP_URL", "http://localhost:3001")
        self.github_mcp_url = os.getenv("GITHUB_MCP_URL", "http://localhost:3002")
        self.postgres_mcp_url = os.getenv("POSTGRES_MCP_URL", "http://localhost:3003")
        self.web_scraper_mcp_url = os.getenv("WEB_SCRAPER_MCP_URL", "http://localhost:3004")
        
        # API Configuration
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        
        # Recommendation Settings
        self.max_recommendations_per_user = int(os.getenv("MAX_RECOMMENDATIONS", "3"))
        self.recommendation_cache_hours = int(os.getenv("RECOMMENDATION_CACHE_HOURS", "6"))
        
        # Email Settings
        self.email_timezone = os.getenv("EMAIL_TIMEZONE", "UTC")
        self.email_batch_size = int(os.getenv("EMAIL_BATCH_SIZE", "100"))

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings
