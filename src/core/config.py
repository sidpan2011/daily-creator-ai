"""
Configuration management for Sparkflow
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Simple configuration for Sparkflow"""
    
    def __init__(self):
        # AI Configuration
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        # Email Configuration
        self.RESEND_API_KEY = os.getenv("RESEND_API_KEY")
        
        # MCP Configuration
        self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    def validate(self):
        """Validate that required API keys are present"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not self.RESEND_API_KEY:
            raise ValueError("RESEND_API_KEY is required")

# Global config instance
config = Config()

def get_config() -> Config:
    """Get application configuration"""
    return config
