#!/usr/bin/env python3
"""
Demo runner - loads sample data and runs the newsletter generation
"""
import asyncio
import json
import os
from src.main import main

def setup_demo_data():
    """Create sample users and trends data"""
    
    print("🔧 Setting up demo data...")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    demo_users = {
        "alex": {
            "name": "Alex Chen", 
            "email": "sidh.pan98@gmail.com",
            "skills": ["React", "Node.js", "Python"],
            "interests": ["AI", "productivity", "startups"],
            "goals": ["build SaaS", "learn ML"]
        }
    }
    
    demo_trends = {
        "github_trending": [
            {
                "name": "microsoft/autogen",
                "description": "Multi-agent AI framework for building conversational AI applications",
                "stars": 28000
            },
            {
                "name": "claude-ai/claude-3.5-sonnet",
                "description": "Latest Claude AI model for advanced reasoning and coding",
                "stars": 15000
            },
            {
                "name": "vercel/next.js",
                "description": "The React framework for production",
                "stars": 120000
            },
            {
                "name": "openai/openai-python",
                "description": "The official Python library for the OpenAI API",
                "stars": 45000
            }
        ],
        "hackernews": [
            {
                "title": "Show HN: AI coding assistant that understands context",
                "points": 245,
                "url": "https://example.com"
            },
            {
                "title": "Ask HN: Best practices for AI integration in web apps",
                "points": 189,
                "url": "https://example.com"
            },
            {
                "title": "The future of AI in software development",
                "points": 312,
                "url": "https://example.com"
            }
        ],
        "last_updated": "2024-10-15T10:00:00Z"
    }
    
    # Save demo data
    with open('data/users.json', 'w') as f:
        json.dump(demo_users, f, indent=2)
    
    with open('data/trends_cache.json', 'w') as f:
        json.dump(demo_trends, f, indent=2)
    
    print("✅ Demo data created!")
    print(f"   - {len(demo_users)} users created")
    print(f"   - {len(demo_trends['github_trending'])} trending repos")
    print(f"   - {len(demo_trends['hackernews'])} HN topics")

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment...")
    
    required_vars = ["ANTHROPIC_API_KEY", "RESEND_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please create a .env file with:")
        print("ANTHROPIC_API_KEY=your_claude_key_here")
        print("RESEND_API_KEY=your_resend_key_here")
        return False
    
    print("✅ Environment variables found")
    return True

async def run_demo():
    """Run the complete demo"""
    print("🚀 Starting Sparkflow Demo...")
    print("=" * 50)
    
    # Setup demo data
    setup_demo_data()
    
    # Check environment
    if not check_environment():
        print("\n❌ Demo cannot run without required environment variables")
        return
    
    print("\n" + "=" * 50)
    print("🎬 Running newsletter generation...")
    print("=" * 50)
    
    # Run the main newsletter generation
    await main()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(run_demo())
