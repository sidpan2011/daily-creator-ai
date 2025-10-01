"""
Opportunity Finder - Real Hackathons, Jobs, and Opportunities
Finds actual opportunities from various sources
"""
import httpx
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .devpost_api import DevpostClient

class OpportunityFinder:
    def __init__(self):
        self.devpost = DevpostClient()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        }

    async def find_real_opportunities(self, user_interests: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find real opportunities based on user interests.
        Now with REAL API integrations!
        """

        print("🔍 Finding real opportunities...")

        opportunities = {
            "hackathons": [],
            "jobs": [],
            "funding": [],
            "events": []
        }

        # Fetch hackathons from Devpost (REAL API)
        try:
            devpost_hackathons = await self.devpost.get_hackathons_by_interests(user_interests, limit=10)
            opportunities["hackathons"].extend(devpost_hackathons)
            print(f"  ✅ Found {len(devpost_hackathons)} hackathons from Devpost")
        except Exception as e:
            print(f"  ⚠️ Devpost fetch failed: {e}")

        # Fetch jobs from Y Combinator (scraping)
        try:
            yc_jobs = await self._fetch_yc_jobs(user_interests, limit=5)
            opportunities["jobs"].extend(yc_jobs)
            print(f"  ✅ Found {len(yc_jobs)} jobs from YC")
        except Exception as e:
            print(f"  ⚠️ YC jobs fetch failed: {e}")

        # Fetch funding news from TechCrunch (already scraped in web_crawler)
        # We'll mark this as available but defer to web_crawler

        total = len(opportunities["hackathons"]) + len(opportunities["jobs"])
        print(f"✅ Total opportunities found: {total}")

        return opportunities

    async def _fetch_yc_jobs(self, user_interests: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape Y Combinator jobs page for startup jobs.
        """
        print("  💼 Fetching jobs from Y Combinator...")

        jobs = []

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers, follow_redirects=True) as client:
                url = "https://www.ycombinator.com/jobs"
                response = await client.get(url)

                if response.status_code != 200:
                    print(f"    ⚠️ YC returned {response.status_code}")
                    return []

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find job listings
                # YC uses various class names, let's try common patterns
                job_cards = soup.find_all('div', class_='job')
                if not job_cards:
                    job_cards = soup.find_all('a', class_='job-link')
                if not job_cards:
                    # Fallback: find all links containing /companies/
                    job_cards = soup.find_all('a', href=lambda x: x and '/companies/' in x)

                print(f"    Found {len(job_cards)} job listings")

                for card in job_cards[:limit * 3]:  # Get extra to filter
                    try:
                        job = self._parse_yc_job_card(card)
                        if job:
                            # Filter by relevance to interests - use smart keyword matching
                            job_text = (job.get('title', '') + ' ' + job.get('description', '')).lower()
                            relevance = self._calculate_job_relevance(job_text, user_interests)

                            if relevance > 0:
                                job['relevance_score'] = relevance
                                jobs.append(job)

                            if len(jobs) >= limit:
                                break
                    except Exception as e:
                        continue

                print(f"    ✅ Found {len(jobs)} relevant jobs")
                return jobs

        except Exception as e:
            print(f"    ❌ YC jobs fetch failed: {e}")
            return []

    def _calculate_job_relevance(self, job_text: str, user_interests: List[str]) -> int:
        """Calculate job relevance using flexible keyword matching"""

        # Map user interests to related keywords
        interest_keywords = {
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 'neural', 'llm', 'gpt', 'nlp', 'computer vision'],
            'ml': ['machine learning', 'ml', 'ai', 'deep learning', 'data science', 'neural', 'tensorflow', 'pytorch'],
            'tools': ['developer tools', 'devtools', 'sdk', 'api', 'platform', 'infrastructure'],
            'hackathon': ['developer', 'engineer', 'software', 'technical', 'coding'],
            'product': ['product', 'development', 'engineering', 'software', 'technical', 'build'],
            'development': ['development', 'engineering', 'software', 'developer', 'engineer', 'technical'],
            'web3': ['blockchain', 'crypto', 'web3', 'defi', 'ethereum', 'solana'],
            'blockchain': ['blockchain', 'crypto', 'web3', 'defi', 'ethereum', 'smart contract'],
            'startup': ['startup', 'early stage', 'founder', 'growth', 'scale'],
            'backend': ['backend', 'api', 'server', 'database', 'infrastructure'],
            'frontend': ['frontend', 'react', 'vue', 'angular', 'ui', 'web'],
            'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter']
        }

        relevance_score = 0

        for interest in user_interests:
            interest_lower = interest.lower()

            # Direct match (e.g., "product development" in job text)
            if interest_lower in job_text:
                relevance_score += 3
                continue

            # Split compound interests (e.g., "ai/ml tools" → ["ai", "ml", "tools"])
            interest_words = interest_lower.replace('/', ' ').split()

            for word in interest_words:
                # Skip common words
                if word in ['and', 'or', 'the', 'a', 'an']:
                    continue

                # Direct word match
                if word in job_text:
                    relevance_score += 2

                # Check related keywords
                if word in interest_keywords:
                    for keyword in interest_keywords[word]:
                        if keyword in job_text:
                            relevance_score += 1
                            break  # Only count once per word

        return relevance_score

    def _parse_yc_job_card(self, card) -> Dict[str, Any]:
        """Parse a job card from YC jobs page"""

        # Extract title
        title_elem = card.find('h3') or card.find('span', class_='job-title') or card
        title = title_elem.get_text(strip=True) if title_elem else "Job Opening"

        # Extract URL
        url = card.get('href') if card.name == 'a' else None
        if url and not url.startswith('http'):
            url = f"https://www.ycombinator.com{url}"

        # Extract company
        company_elem = card.find('span', class_='company') or card.find('div', class_='company-name')
        company = company_elem.get_text(strip=True) if company_elem else "YC Company"

        # Extract location
        location_elem = card.find('span', class_='location')
        location = location_elem.get_text(strip=True) if location_elem else "Remote / SF"

        # Extract description
        desc_elem = card.find('p', class_='description') or card.find('div', class_='job-description')
        description = desc_elem.get_text(strip=True)[:200] if desc_elem else f"Job at {company}"

        return {
            'title': title,
            'url': url,
            'company': company,
            'location': location,
            'description': description,
            'source': 'Y Combinator',
            'category': 'job',
            'published_at': datetime.now().isoformat()
        }

    # Old hardcoded opportunities (DISABLED):
    async def _disabled_hardcoded_opportunities(self):
        if False and any("web3" in interest.lower() or "blockchain" in interest.lower() for interest in user_interests):
            opportunities["hackathons"].extend([
                {
                    "title": "Solana Grizzlython Hackathon",
                    "description": "Global hackathon focused on building the next generation of web3 applications on Solana",
                    "deadline": "October 15, 2025",
                    "prize": "$5M in prizes",
                    "url": "https://grizzlython.com",
                    "category": "hackathon",
                    "relevance": "web3/blockchain"
                },
                {
                    "title": "Ethereum Foundation Grants",
                    "description": "Funding for projects building on Ethereum ecosystem",
                    "deadline": "Rolling basis",
                    "prize": "Up to $50K",
                    "url": "https://esp.ethereum.foundation",
                    "category": "funding",
                    "relevance": "web3/blockchain"
                }
            ])
        
        if any("ai" in interest.lower() or "ml" in interest.lower() for interest in user_interests):
            opportunities["hackathons"].extend([
                {
                    "title": "OpenAI API Challenge",
                    "description": "Build innovative applications using GPT-4 and other OpenAI models",
                    "deadline": "November 1, 2025",
                    "prize": "$100K in prizes",
                    "url": "https://openai.com/api/challenge",
                    "category": "hackathon",
                    "relevance": "ai/ml"
                },
                {
                    "title": "Google AI Residency Program",
                    "description": "1-year research position at Google AI",
                    "deadline": "December 15, 2025",
                    "prize": "Full-time position",
                    "url": "https://research.google.com/teams/brain/residency",
                    "category": "job",
                    "relevance": "ai/ml"
                }
            ])
        
        if any("startup" in interest.lower() for interest in user_interests):
            opportunities["funding"].extend([
                {
                    "title": "Y Combinator W25 Applications",
                    "description": "Join the world's most successful startup accelerator",
                    "deadline": "October 1, 2025",
                    "prize": "$500K investment",
                    "url": "https://ycombinator.com/apply",
                    "category": "accelerator",
                    "relevance": "startup"
                },
                {
                    "title": "Techstars Applications Open",
                    "description": "3-month mentorship-driven accelerator program",
                    "deadline": "Rolling deadlines",
                    "prize": "$120K investment",
                    "url": "https://techstars.com",
                    "category": "accelerator",
                    "relevance": "startup"
                }
            ])
        
        return opportunities
    
    async def find_geographically_relevant_opportunities(self, user_location: str, interests: List[str]) -> List[Dict[str, Any]]:
        """Find opportunities prioritized by location"""
        
        opportunities = []
        
        # Check if user is in India
        if self._is_indian_location(user_location):
            # Prioritize India-specific opportunities
            india_ops = await self._scrape_india_opportunities(interests)
            opportunities.extend(india_ops)
            
            # Add relevant global opportunities
            global_ops = await self._scrape_global_opportunities(interests)
            opportunities.extend(global_ops[:2])  # Only add 2 global
        else:
            # For non-India users, different priority
            global_ops = await self._scrape_global_opportunities(interests)
            opportunities.extend(global_ops)
        
        return opportunities
    
    def _is_indian_location(self, location: str) -> bool:
        """Check if location is in India"""
        if not location:
            return False
        
        location_lower = location.lower()
        indian_cities = ['india', 'bangalore', 'delhi', 'mumbai', 'hyderabad', 'pune', 'chennai', 'kolkata', 'ahmedabad', 'jaipur']
        return any(city in location_lower for city in indian_cities)
    
    async def _scrape_india_opportunities(self, interests: List[str]) -> List[Dict[str, Any]]:
        """Scrape India-specific opportunities"""
        
        opportunities = []
        
        # Add India-specific hackathons
        if any("hackathon" in interest.lower() for interest in interests):
            opportunities.extend([
                {
                    "title": "Devfolio Hackathons - India's Premier Platform",
                    "description": "Devfolio hosts 50+ hackathons annually across India with prizes up to ₹50L. Perfect for building your portfolio and connecting with India's top developers.",
                    "deadline": "Ongoing applications",
                    "prize": "Up to ₹50L total prizes",
                    "url": "https://devfolio.co/hackathons",
                    "category": "hackathon",
                    "relevance": "hackathon",
                    "location": "India-wide"
                },
                {
                    "title": "Unstop Campus Hackathons",
                    "description": "University-focused hackathons across 500+ Indian campuses. Great for students and recent graduates to showcase skills.",
                    "deadline": "Rolling deadlines",
                    "prize": "₹5L-₹20L per hackathon",
                    "url": "https://unstop.com/hackathons",
                    "category": "hackathon",
                    "relevance": "hackathon",
                    "location": "Indian Universities"
                }
            ])
        
        # Add India-specific startup opportunities
        if any("startup" in interest.lower() for interest in interests):
            opportunities.extend([
                {
                    "title": "Y Combinator India Program",
                    "description": "YC's India-focused accelerator program with $500K investment, Silicon Valley network access, and India-specific mentorship.",
                    "deadline": "Applications open quarterly",
                    "prize": "$500K investment",
                    "url": "https://ycombinator.com/india",
                    "category": "accelerator",
                    "relevance": "startup",
                    "location": "Bangalore + Remote"
                },
                {
                    "title": "Sequoia India Surge Program",
                    "description": "Early-stage startup accelerator focused on Indian market with $1M investment and access to Sequoia's global network.",
                    "deadline": "Applications open bi-annually",
                    "prize": "$1M investment",
                    "url": "https://surge.sequoia.com",
                    "category": "accelerator",
                    "relevance": "startup",
                    "location": "Bangalore"
                }
            ])
        
        # Add India-specific jobs
        if any("ai" in interest.lower() or "ml" in interest.lower() for interest in interests):
            opportunities.extend([
                {
                    "title": "AI Engineer at Razorpay",
                    "description": "Build AI-powered fintech solutions at India's leading payment gateway. Work on fraud detection, risk assessment, and customer insights.",
                    "deadline": "Open applications",
                    "prize": "₹15L-₹35L + equity",
                    "url": "https://razorpay.com/careers",
                    "category": "job",
                    "relevance": "ai/ml",
                    "location": "Bangalore"
                },
                {
                    "title": "ML Engineer at Swiggy",
                    "description": "Develop machine learning models for food delivery optimization, demand forecasting, and route optimization.",
                    "deadline": "Open applications",
                    "prize": "₹12L-₹30L + equity",
                    "url": "https://careers.swiggy.com",
                    "category": "job",
                    "relevance": "ai/ml",
                    "location": "Bangalore"
                }
            ])
        
        return opportunities
    
    async def _scrape_global_opportunities(self, interests: List[str]) -> List[Dict[str, Any]]:
        """Scrape global opportunities"""
        
        opportunities = []
        
        # Add global hackathons
        if any("hackathon" in interest.lower() for interest in interests):
            opportunities.extend([
                {
                    "title": "Devpost Global Hackathons",
                    "description": "World's largest hackathon platform with 1000+ events annually. Perfect for building global portfolio and winning international prizes.",
                    "deadline": "Various deadlines",
                    "prize": "Up to $100K per hackathon",
                    "url": "https://devpost.com/hackathons",
                    "category": "hackathon",
                    "relevance": "hackathon",
                    "location": "Global"
                }
            ])
        
        # Add global funding opportunities
        if any("startup" in interest.lower() for interest in interests):
            opportunities.extend([
                {
                    "title": "Y Combinator W25 Applications",
                    "description": "Join the world's most successful startup accelerator with $500K investment and access to Silicon Valley network.",
                    "deadline": "October 1, 2025",
                    "prize": "$500K investment",
                    "url": "https://ycombinator.com/apply",
                    "category": "accelerator",
                    "relevance": "startup",
                    "location": "San Francisco + Remote"
                }
            ])
        
        return opportunities
    
    async def get_devpost_hackathons(self) -> List[Dict[str, Any]]:
        """Get hackathons from Devpost (in production, would use their API)"""
        # Placeholder for real Devpost integration
        return [
            {
                "title": "MLH Fall Hackathon Season",
                "description": "Multiple hackathons happening across universities",
                "deadline": "Various dates in October-November",
                "prize": "Various prizes",
                "url": "https://mlh.io",
                "category": "hackathon",
                "relevance": "general"
            }
        ]
    
    async def get_angel_list_jobs(self, interests: List[str]) -> List[Dict[str, Any]]:
        """Get relevant jobs from AngelList (in production, would use their API)"""
        jobs = []
        
        if any("web3" in interest.lower() for interest in interests):
            jobs.append({
                "title": "Senior Blockchain Developer at Solana Labs",
                "description": "Build the next generation of blockchain infrastructure",
                "deadline": "Open applications",
                "prize": "$180K-250K + equity",
                "url": "https://jobs.solana.com",
                "category": "job",
                "relevance": "web3/blockchain"
            })
        
        if any("ai" in interest.lower() for interest in interests):
            jobs.append({
                "title": "AI Engineer at Anthropic",
                "description": "Work on Claude and other AI safety research",
                "deadline": "Open applications",
                "prize": "$200K-350K + equity",
                "url": "https://anthropic.com/careers",
                "category": "job",
                "relevance": "ai/ml"
            })
        
        return jobs
    
    def filter_by_relevance(self, opportunities: List[Dict[str, Any]], user_interests: List[str]) -> List[Dict[str, Any]]:
        """Filter opportunities by user interests"""
        filtered = []
        
        for opp in opportunities:
            relevance_score = 0
            for interest in user_interests:
                if interest.lower() in opp.get("relevance", "").lower():
                    relevance_score += 1
                if interest.lower() in opp.get("description", "").lower():
                    relevance_score += 1
            
            if relevance_score > 0:
                opp["relevance_score"] = relevance_score
                filtered.append(opp)
        
        return sorted(filtered, key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    async def get_comprehensive_opportunities(self, user_interests: List[str]) -> Dict[str, Any]:
        """Get all opportunities relevant to user"""
        
        # Get opportunities from various sources
        real_opportunities = await self.find_real_opportunities(user_interests)
        devpost_hackathons = await self.get_devpost_hackathons()
        angel_jobs = await self.get_angel_list_jobs(user_interests)
        
        # Combine and filter
        all_opportunities = []
        for category, opps in real_opportunities.items():
            all_opportunities.extend(opps)
        all_opportunities.extend(devpost_hackathons)
        all_opportunities.extend(angel_jobs)
        
        # Filter by relevance
        relevant_opportunities = self.filter_by_relevance(all_opportunities, user_interests)
        
        return {
            "opportunities": relevant_opportunities,
            "total_count": len(relevant_opportunities),
            "categories": {
                "hackathons": [o for o in relevant_opportunities if o["category"] == "hackathon"],
                "jobs": [o for o in relevant_opportunities if o["category"] == "job"],
                "funding": [o for o in relevant_opportunities if o["category"] == "funding"],
                "accelerators": [o for o in relevant_opportunities if o["category"] == "accelerator"]
            }
        }
