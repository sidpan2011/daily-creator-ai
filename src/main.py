#!/usr/bin/env python3
"""
Sparkflow - AI-Powered Personalized Newsletter
Main entry point for generating and sending recommendations
"""

import asyncio
import json
import time
from src.core.config import get_config
from src.mcp_orchestrator import MCPOrchestrator  
from src.ai_engine import AIEngine
from src.email_sender import EmailSender
from src.models import UserProfile

def load_users():
    """Load users from JSON file"""
    try:
        with open('data/users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No users.json found. Please run demo.py first to create sample data.")
        return {}

async def main():
    """Main function to generate recommendations for all users"""
    
    print("🚀 Starting Sparkflow Newsletter Generation...")
    
    # Initialize components
    config = get_config()
    config.validate()  # Validate API keys are present
    mcp_orchestrator = MCPOrchestrator(config)
    ai_engine = AIEngine(config)
    email_sender = EmailSender(config, mcp_orchestrator)
    
    # Start all MCP servers
    await mcp_orchestrator.start_all_servers()
    
    # Load users
    users = load_users()
    
    if not users:
        print("❌ No users found. Please run demo.py first to create sample data.")
        return
    
    for user_id, user_data in users.items():
        print(f"📧 Processing user: {user_data['name']}")
        
        try:
            # 1. Get trending data via MCP
            trending_data = await mcp_orchestrator.get_trending_data()
            
            # 2. Generate AI recommendations  
            recommendations = await ai_engine.generate_recommendations(
                user_data, trending_data
            )
            
            # 3. Send email
            await email_sender.send_newsletter(user_data, recommendations)
            
            print(f"✅ Sent newsletter to {user_data['name']}")
        except Exception as e:
            print(f"❌ Error processing {user_data['name']}: {e}")
        
        # Add small delay to avoid rate limiting
        await asyncio.sleep(1)
    
    # Stop all MCP servers
    await mcp_orchestrator.stop_all_servers()
    
    print("🎉 All newsletters sent!")

if __name__ == "__main__":
    asyncio.run(main())
