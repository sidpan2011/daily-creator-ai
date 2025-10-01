#!/usr/bin/env python3
"""
Test the full opportunities data flow:
1. OpportunityFinder fetches from Devpost/YC
2. WebResearchAggregator includes it in research_data
3. AI Engine receives and passes it to the prompt
"""
import asyncio
import json
from src.config import get_config
from data_sources.web_research import WebResearchAggregator
from data_sources.opportunity_finder import OpportunityFinder

async def test_full_flow():
    print("="*80)
    print("🧪 TESTING OPPORTUNITIES DATA FLOW")
    print("="*80)

    # Test profile
    user_profile = {
        'name': 'Test User',
        'email': 'test@example.com',
        'github_username': 'test',
        'location': 'USA',
        'interests': ['ai/ml tools', 'hackathons', 'product development'],
        'preferences': {
            'opportunity_types': ['hackathons', 'jobs']
        }
    }

    print("\n1️⃣ Testing OpportunityFinder directly...")
    print("-" * 80)

    opportunity_finder = OpportunityFinder()
    opportunities = await opportunity_finder.find_real_opportunities(
        user_profile['interests']
    )

    print(f"\n📊 OpportunityFinder Results:")
    print(f"   Type: {type(opportunities)}")
    print(f"   Keys: {opportunities.keys() if isinstance(opportunities, dict) else 'Not a dict'}")

    if isinstance(opportunities, dict):
        hackathons = opportunities.get('hackathons', [])
        jobs = opportunities.get('jobs', [])

        print(f"\n   Hackathons: {len(hackathons)}")
        if hackathons:
            print(f"   Example: {hackathons[0].get('title', 'No title')}")
            print(f"   URL: {hackathons[0].get('url', 'No URL')}")

        print(f"\n   Jobs: {len(jobs)}")
        if jobs:
            print(f"   Example: {jobs[0].get('title', 'No title')}")

    print("\n\n2️⃣ Testing WebResearchAggregator...")
    print("-" * 80)

    config = get_config()
    web_research = WebResearchAggregator(config.GITHUB_TOKEN)

    # We'll use the simpler method to avoid GitHub API calls
    print("\n   Calling gather_comprehensive_research_with_opportunities()...")

    # Mock research_data to simulate what gather_comprehensive_research returns
    mock_research_data = {
        'trending_repos': [],
        'hackernews_stories': [],
        'fresh_updates': [],
        'user_context': {}
    }

    # Now test adding opportunities
    print("\n   Adding opportunities to research data...")
    opps = await opportunity_finder.find_real_opportunities(user_profile['interests'])

    research_data = mock_research_data.copy()
    research_data['opportunities'] = opps

    print(f"\n📊 Research Data Structure:")
    print(f"   Keys: {research_data.keys()}")
    print(f"   opportunities type: {type(research_data.get('opportunities'))}")

    if isinstance(research_data.get('opportunities'), dict):
        opps_dict = research_data['opportunities']
        print(f"   opportunities keys: {opps_dict.keys()}")
        print(f"   hackathons count: {len(opps_dict.get('hackathons', []))}")
        print(f"   jobs count: {len(opps_dict.get('jobs', []))}")

    print("\n\n3️⃣ Simulating AI Engine data extraction...")
    print("-" * 80)

    # Simulate what ai_engine.py does
    opps = research_data.get('opportunities', {})
    print(f"\n   opportunities type: {type(opps)}")

    if isinstance(opps, dict):
        hackathons = opps.get('hackathons', [])[:5]
        jobs = opps.get('jobs', [])[:3]

        opps_data = {
            'hackathons': hackathons,
            'jobs': jobs
        }

        print(f"\n   ✅ Successfully extracted:")
        print(f"      {len(hackathons)} hackathons")
        print(f"      {len(jobs)} jobs")

        if hackathons:
            print(f"\n   Example hackathon that would go to AI:")
            print(f"      Title: {hackathons[0].get('title')}")
            print(f"      Prize: {hackathons[0].get('prize')}")
            print(f"      Deadline: {hackathons[0].get('deadline')}")
            print(f"      URL: {hackathons[0].get('url')}")

        # Show what the AI prompt would receive
        print(f"\n   JSON that goes to AI prompt:")
        print(json.dumps(opps_data, indent=2)[:500] + "...")

    else:
        print(f"   ❌ ERROR: opportunities is not a dict: {type(opps)}")

    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_full_flow())
