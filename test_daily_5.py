#!/usr/bin/env python3
"""
Test script for the new Behavioral Intelligence Daily 5 system
"""
import asyncio
import json
from src.config import get_config
from src.ai_engine import AIEditorialEngine
from data_sources.web_research import WebResearchAggregator

async def test_daily_5():
    """Test the Daily 5 generation system"""
    
    print("🧠 Testing Behavioral Intelligence Daily 5 System")
    print("=" * 60)
    
    # Load user profile
    try:
        with open('user_profile.json', 'r') as f:
            user_profile = json.load(f)
        print(f"✅ Loaded profile for: {user_profile['name']}")
    except FileNotFoundError:
        print("❌ user_profile.json not found. Please create your profile first.")
        return
    
    # Initialize components
    config = get_config()
    ai_engine = AIEditorialEngine(config)
    web_research = WebResearchAggregator(config.GITHUB_TOKEN)
    
    try:
        # 1. Gather research data
        print("\n📊 Gathering research data...")
        research_data = await web_research.gather_comprehensive_research(user_profile)
        
        if not research_data:
            print("❌ Failed to gather research data")
            return
        
        print(f"✅ Gathered data: {len(research_data.get('trending_repos', []))} trending repos, {len(research_data.get('hackernews_stories', []))} HN stories")
        
        # 2. Generate Daily 5
        print("\n🧠 Generating Daily 5 with behavioral analysis...")
        daily_5_content = await ai_engine.generate_daily_5(user_profile, research_data)
        
        # 3. Display results
        print("\n" + "=" * 60)
        print("📰 DAILY 5 RESULTS")
        print("=" * 60)
        
        print(f"📧 Subject: {daily_5_content['subject_line']}")
        print(f"🎯 Headline: {daily_5_content['headline']}")
        print(f"📊 Personalization: {daily_5_content['personalization_note']}")
        print(f"🧠 Detected Intent: {daily_5_content['user_intent'].get('primary_intent', 'unknown')}")
        print(f"🎯 Confidence: {daily_5_content['user_intent'].get('confidence', 0):.1f}")
        
        print(f"\n📋 DAILY 5 ITEMS:")
        for i, item in enumerate(daily_5_content['items'], 1):
            print(f"\n{i}. {item['category']}")
            print(f"   Title: {item['title']}")
            print(f"   Action: {item['action']}")
            print(f"   Meta: {item.get('meta_info', 'N/A')}")
        
        print(f"\n📝 Summary: {daily_5_content.get('summary', 'No summary available')}")
        
        print("\n✅ Daily 5 generation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_daily_5())
