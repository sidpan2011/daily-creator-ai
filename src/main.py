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
from src.system_prompts import LOCATION_RULES
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
        
        # 2. Generate Daily 5 using behavioral analysis with location rules
        print("🧠 Generating Daily 5 with behavioral intelligence...")
        location = user_profile.get('location', '')
        location_rule = LOCATION_RULES.get('India' if 'india' in location.lower() else 'default')
        
        try:
            daily_5_content = await ai_engine.generate_daily_5(
                user_profile, research_data, location_rule=location_rule
            )
            
            print(f"📰 Generated: \"{daily_5_content['headline']}\"")
            print(f"🎯 Subject: \"{daily_5_content['subject_line']}\"")
            # Handle user_intent being either dict or string
            user_intent = daily_5_content.get('user_intent', {})
            if isinstance(user_intent, dict):
                print(f"📊 Intent: {user_intent.get('primary_intent', 'exploring')}")
            else:
                print(f"📊 Intent: {user_intent}")
            
            # 3. Send Daily 5 newsletter
            print("📧 Sending Daily 5 newsletter...")
            success = await email_sender.send_daily_5_newsletter(user_profile, daily_5_content)
            
            if success:
                print(f"✅ Daily 5 sent to {user_profile['email']}")
                print(f"🎯 Check your inbox for personalized opportunities!")
            else:
                print("❌ Failed to send Daily 5")
                
        except Exception as generation_error:
            print(f"🚨 Content generation failed: {generation_error}")
            import traceback
            traceback.print_exc()
            print("📧 Sending graceful failure email instead...")
            
            # Send a simple email explaining the situation
            recent_repos = research_data.get('user_context', {}).get('recent_repos', [])
            repo_names = []
            for repo in recent_repos[:3]:
                if isinstance(repo, dict):
                    repo_names.append(repo.get('name', 'Unknown'))
                else:
                    repo_names.append(str(repo))
            
            failure_content = {
                "subject_line": f"Failed - {user_profile['name']}",
                "headline": "Quality Check in Progress",
                "personalization_note": f"Hi {user_profile['name']}, I tried to generate your personalized Daily 5 today, but I couldn't meet my quality standards. Rather than send you generic content, I'm skipping today.",
                "items": [
                    {
                        "title": "Your Recent GitHub Activity",
                        "content": f"Your repositories show active development: {', '.join(repo_names) if repo_names else 'Keep building!'}. Keep building!",
                        "category": "📊 UPDATE"
                    }
                ],
                "user_intent": {"primary_intent": "quality_focus"},
                "date": "Today",
                "summary": "I'll try again tomorrow with fresh data!"
            }
            
            success = await email_sender.send_daily_5_newsletter(user_profile, failure_content)
            if success:
                print(f"✅ Graceful failure email sent to {user_profile['email']}")
            else:
                print("❌ Failed to send failure email")
        
    except Exception as e:
        print(f"❌ System failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())