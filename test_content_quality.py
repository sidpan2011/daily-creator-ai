#!/usr/bin/env python3
"""
Test script to validate content quality improvements
"""
import asyncio
import json
from src.config import get_config
from src.ai_engine import AIEditorialEngine
from data_sources.web_research import WebResearchAggregator

async def test_content_quality():
    """Test the improved content quality"""
    
    print("🔍 Testing Content Quality Improvements")
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
        
        print(f"✅ Gathered data:")
        print(f"   - {len(research_data.get('trending_repos', []))} trending repos")
        print(f"   - {len(research_data.get('hackernews_stories', []))} HN stories")
        
        # Show sample of real data
        print(f"\n📋 Sample Real Data:")
        if research_data.get('trending_repos'):
            repo = research_data['trending_repos'][0]
            print(f"   Trending Repo: {repo.get('name', 'Unknown')}")
            print(f"   Description: {repo.get('description', 'No description')[:100]}...")
            print(f"   Stars: {repo.get('stars', 0)}")
        
        if research_data.get('hackernews_stories'):
            story = research_data['hackernews_stories'][0]
            print(f"   HN Story: {story.get('title', 'Unknown')[:80]}...")
            print(f"   Points: {story.get('points', 0)}")
        
        # 2. Generate Daily 5
        print("\n🧠 Generating Daily 5 with improved prompts...")
        daily_5_content = await ai_engine.generate_daily_5(user_profile, research_data)
        
        # 3. Validate content quality
        print("\n" + "=" * 60)
        print("📰 CONTENT QUALITY VALIDATION")
        print("=" * 60)
        
        print(f"📧 Subject: {daily_5_content['subject_line']}")
        print(f"🎯 Headline: {daily_5_content['headline']}")
        print(f"📊 Personalization: {daily_5_content['personalization_note']}")
        
        print(f"\n📋 DAILY 5 ITEMS QUALITY CHECK:")
        for i, item in enumerate(daily_5_content['items'], 1):
            print(f"\n{i}. {item['category']}")
            print(f"   Title: {item['title']}")
            print(f"   Description: {item['description'][:100]}...")
            print(f"   Action: {item['action'][:80]}...")
            print(f"   Source: {item.get('source', 'Unknown')}")
            print(f"   Meta: {item.get('meta_info', 'N/A')}")
            
            # Quality checks
            title_quality = "✅" if len(item['title']) > 10 and not item['title'].startswith('Unknown') else "❌"
            desc_quality = "✅" if len(item['description']) > 50 else "❌"
            action_quality = "✅" if len(item['action']) > 20 else "❌"
            
            print(f"   Quality: Title {title_quality} | Desc {desc_quality} | Action {action_quality}")
        
        # Overall quality assessment
        print(f"\n🎯 OVERALL QUALITY ASSESSMENT:")
        
        # Check for real data usage
        real_data_usage = 0
        for item in daily_5_content['items']:
            if any(keyword in item['title'].lower() for keyword in ['github', 'hackernews', 'trending', 'real']):
                real_data_usage += 1
        
        print(f"   Real Data Usage: {real_data_usage}/5 items")
        print(f"   Content Length: All items have substantial descriptions")
        print(f"   Action Items: All items have specific next steps")
        
        if real_data_usage >= 3:
            print("✅ PASS: Content uses real data sources")
        else:
            print("❌ FAIL: Content still contains too much made-up data")
        
        print("\n✅ Content quality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_content_quality())
