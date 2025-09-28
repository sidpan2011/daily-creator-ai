#!/usr/bin/env python3
"""
Persnally - Behavioral Intelligence "Daily 5"
Production version with behavioral analysis and smart opportunity matching
"""
import asyncio
import json
from pathlib import Path
from src.config import get_config
from src.mcp_orchestrator import MCPOrchestrator
from src.ai_engine import AIEditorialEngine
from src.email_sender import PremiumEmailSender
from data_sources.web_research import WebResearchAggregator

def load_user_profile() -> dict:
    """Load real user profile"""
    try:
        with open('user_profile.json', 'r') as f:
            profile = json.load(f)
            print(f"✅ Loaded profile for: {profile['name']}")
            return profile
    except FileNotFoundError:
        print("❌ user_profile.json not found. Please create your profile first.")
        return {}
    except Exception as e:
        print(f"❌ Error loading profile: {e}")
        return {}

async def main():
    """Generate behavioral intelligence Daily 5 with real data"""
    
    print("🧠 Persnally - Behavioral Intelligence Daily 5")
    print("=" * 50)
    
    # Load real user profile
    user_profile = load_user_profile()
    if not user_profile:
        print("❌ No user profile found. Exiting.")
        return
    
    # Initialize components
    config = get_config()
    mcp_orchestrator = MCPOrchestrator(config)
    ai_engine = AIEditorialEngine(config)
    email_sender = PremiumEmailSender(config, mcp_orchestrator)
    web_research = WebResearchAggregator(config.GITHUB_TOKEN)
    
    # Initialize MCP services
    await mcp_orchestrator.initialize_all_clients()
    
    print(f"🔄 Generating Daily 5 for: {user_profile['name']}")
    print("=" * 50)
    
    try:
        # 1. Gather real research data with opportunities
        print("📊 Gathering real-time research data...")
        research_data = await web_research.gather_comprehensive_research_with_opportunities(user_profile)
        
        if not research_data:
            print("❌ Failed to gather research data. Exiting.")
            return
        
        # 2. Generate Daily 5 using behavioral analysis
        print("🧠 Generating Daily 5 with behavioral intelligence...")
        daily_5_content = await ai_engine.generate_daily_5(
            user_profile, research_data
        )
        
        print(f"📰 Generated: \"{daily_5_content['headline']}\"")
        print(f"🎯 Subject: \"{daily_5_content['subject_line']}\"")
        print(f"📊 Intent: {daily_5_content['user_intent'].get('primary_intent', 'exploring')}")
        
        # 3. Send Daily 5 newsletter
        print("📧 Sending Daily 5 newsletter...")
        success = await email_sender.send_daily_5_newsletter(user_profile, daily_5_content)
        
        if success:
            print(f"✅ Daily 5 sent to {user_profile['email']}")
            print(f"🎯 Check your inbox for personalized opportunities!")
        else:
            print("❌ Failed to send Daily 5")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())