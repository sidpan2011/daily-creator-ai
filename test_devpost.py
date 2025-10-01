#!/usr/bin/env python3
"""
Quick test to verify Devpost API integration works
"""
import asyncio
from data_sources.devpost_api import DevpostClient

async def test_devpost():
    print("🧪 Testing Devpost API Integration\n")

    client = DevpostClient()

    # Test 1: Get active hackathons
    print("Test 1: Fetching active hackathons...")
    hackathons = await client.get_active_hackathons(limit=5)

    if hackathons:
        print(f"✅ Found {len(hackathons)} hackathons!\n")

        for i, hackathon in enumerate(hackathons[:3], 1):
            print(f"[{i}] {hackathon['title']}")
            print(f"    Prize: {hackathon.get('prize', 'N/A')}")
            print(f"    Deadline: {hackathon.get('deadline', 'N/A')}")
            print(f"    URL: {hackathon.get('url', 'N/A')}")
            print(f"    Status: {hackathon.get('status', 'N/A')}")
            print()
    else:
        print("❌ No hackathons found (might be a scraping issue)\n")

    # Test 2: Get hackathons by interests
    print("\nTest 2: Fetching hackathons for interests: ['ai/ml tools', 'hackathons']")
    relevant_hackathons = await client.get_hackathons_by_interests(
        ['ai/ml tools', 'hackathons', 'product development'],
        limit=3
    )

    if relevant_hackathons:
        print(f"✅ Found {len(relevant_hackathons)} relevant hackathons!\n")

        for i, hackathon in enumerate(relevant_hackathons, 1):
            print(f"[{i}] {hackathon['title']}")
            print(f"    Relevance Score: {hackathon.get('relevance_score', 0)}")
            print(f"    Themes: {', '.join(hackathon.get('themes', [])[:3])}")
            print()
    else:
        print("❌ No relevant hackathons found\n")

if __name__ == "__main__":
    asyncio.run(test_devpost())
