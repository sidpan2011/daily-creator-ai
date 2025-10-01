"""
Devpost API Client
Fetches real hackathons from Devpost
"""
import httpx
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup

class DevpostClient:
    def __init__(self):
        self.base_url = "https://devpost.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

    async def get_active_hackathons(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Fetch active hackathons from Devpost using their JSON API.
        """
        print("  🏆 Fetching hackathons from Devpost API...")

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers, follow_redirects=True) as client:
                # Use Devpost's JSON API
                url = f"{self.base_url}/api/hackathons"
                response = await client.get(url)

                if response.status_code != 200:
                    print(f"    ⚠️ Devpost API returned {response.status_code}")
                    return []

                data = response.json()
                hackathons_data = data.get('hackathons', [])

                print(f"    ✅ Found {len(hackathons_data)} hackathons from API")

                hackathons = []
                for hackathon_data in hackathons_data[:limit]:
                    try:
                        # Only include open hackathons
                        if hackathon_data.get('open_state') != 'open':
                            continue

                        hackathon = self._parse_api_hackathon(hackathon_data)
                        if hackathon:
                            hackathons.append(hackathon)
                    except Exception as e:
                        print(f"    ⚠️ Failed to parse hackathon: {e}")
                        continue

                print(f"    ✅ Parsed {len(hackathons)} open hackathons")
                return hackathons

        except httpx.TimeoutException:
            print("    ⚠️ Devpost request timed out")
            return []
        except Exception as e:
            print(f"    ❌ Devpost fetch failed: {e}")
            return []

    def _parse_api_hackathon(self, data: Dict) -> Dict[str, Any]:
        """Parse hackathon data from Devpost API JSON response"""

        try:
            # Extract themes
            themes = [theme.get('name') for theme in data.get('themes', [])]

            # Extract prize amount (remove HTML tags)
            prize_raw = data.get('prize_amount', 'Prizes available')
            # Parse prize from HTML span
            import re
            prize_match = re.search(r'(\d+(?:,\d+)*)', prize_raw)
            prize = f"${prize_match.group(1)}" if prize_match else "Prizes available"

            # Extract deadline info
            deadline = data.get('submission_period_dates', '')
            time_left = data.get('time_left_to_submission', '')

            # Build description
            registrations = data.get('registrations_count', 0)
            organizer = data.get('organization_name', 'Unknown')
            description = f"{organizer} hackathon with {prize} in prizes. {registrations:,} participants registered. Themes: {', '.join(themes[:3])}"

            return {
                'title': data.get('title', 'Untitled Hackathon'),
                'url': data.get('url', ''),
                'prize': prize,
                'deadline': deadline,
                'time_left': time_left,
                'organizer': organizer,
                'themes': themes,
                'status': 'open',
                'participants': f"{registrations:,} registered",
                'description': description,
                'source': 'Devpost',
                'category': 'hackathon',
                'published_at': datetime.now().isoformat(),
                'featured': data.get('featured', False),
                'registrations_count': registrations
            }
        except Exception as e:
            print(f"    ⚠️ Error parsing hackathon data: {e}")
            return None

    def _parse_hackathon_card(self, card) -> Dict[str, Any]:
        """Parse a hackathon card from Devpost HTML"""

        # Extract title and URL
        title_elem = card.find('h3') or card.find('a', class_='challenge-link')
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)
        url_elem = card.find('a', href=True)
        url = url_elem['href'] if url_elem else None

        # Make URL absolute
        if url and not url.startswith('http'):
            url = f"{self.base_url}{url}"

        # Extract prize/funding
        prize_elem = card.find('div', class_='prize-amount') or card.find('span', class_='prize')
        prize = prize_elem.get_text(strip=True) if prize_elem else "Prizes available"

        # Extract deadline
        deadline_elem = card.find('time') or card.find('div', class_='submission-period')
        deadline = None
        if deadline_elem:
            deadline_text = deadline_elem.get_text(strip=True)
            # Try to parse date
            try:
                if 'datetime' in deadline_elem.attrs:
                    deadline = deadline_elem['datetime']
                else:
                    deadline = deadline_text
            except:
                deadline = deadline_text

        # Extract themes/tags
        tags_elem = card.find_all('span', class_='tag') or card.find_all('div', class_='themes')
        themes = [tag.get_text(strip=True) for tag in tags_elem[:5]]

        # Extract organizer
        organizer_elem = card.find('div', class_='host-name') or card.find('span', class_='organizer')
        organizer = organizer_elem.get_text(strip=True) if organizer_elem else "Unknown"

        # Determine status (open/upcoming/ended)
        status = 'open'  # Devpost /hackathons page mostly shows open ones
        status_elem = card.find('span', class_='status')
        if status_elem:
            status_text = status_elem.get_text(strip=True).lower()
            if 'ended' in status_text or 'closed' in status_text:
                status = 'ended'
            elif 'upcoming' in status_text:
                status = 'upcoming'

        # Extract participants count if available
        participants_elem = card.find('div', class_='participants')
        participants = participants_elem.get_text(strip=True) if participants_elem else None

        # Extract description snippet
        description_elem = card.find('p', class_='challenge-description') or card.find('div', class_='description')
        description = description_elem.get_text(strip=True)[:200] if description_elem else f"Hackathon hosted by {organizer}"

        return {
            'title': title,
            'url': url,
            'prize': prize,
            'deadline': deadline,
            'organizer': organizer,
            'themes': themes,
            'status': status,
            'participants': participants,
            'description': description,
            'source': 'Devpost',
            'category': 'hackathon',
            'published_at': datetime.now().isoformat()  # Approximate
        }

    async def get_hackathons_by_theme(self, theme: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch hackathons filtered by theme (e.g., 'ai', 'web3', 'social-good')
        """
        print(f"  🏆 Fetching {theme} hackathons from Devpost...")

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=self.headers, follow_redirects=True) as client:
                # Devpost has theme-based filtering
                url = f"{self.base_url}/hackathons?themes[]={theme}"
                response = await client.get(url)

                if response.status_code != 200:
                    return []

                soup = BeautifulSoup(response.text, 'html.parser')
                hackathon_cards = soup.find_all('div', class_='challenge-listing')

                hackathons = []
                for card in hackathon_cards[:limit]:
                    try:
                        hackathon = self._parse_hackathon_card(card)
                        if hackathon:
                            hackathons.append(hackathon)
                    except:
                        continue

                return hackathons

        except Exception as e:
            print(f"    ❌ Theme-based fetch failed: {e}")
            return []

    async def get_hackathons_by_interests(self, interests: List[str], limit: int = 15) -> List[Dict[str, Any]]:
        """
        Fetch hackathons matching user interests.
        Maps user interests to Devpost themes.
        """

        # Map user interests to Devpost themes
        interest_to_theme = {
            'ai': 'machine-learning',
            'ml': 'machine-learning',
            'machine learning': 'machine-learning',
            'web3': 'blockchain',
            'blockchain': 'blockchain',
            'robotics': 'hardware',
            'iot': 'hardware',
            'social impact': 'social-good',
            'education': 'education',
            'health': 'health',
            'fintech': 'fintech',
            'gaming': 'gaming'
        }

        # Get all open hackathons first
        all_hackathons = await self.get_active_hackathons(limit=30)

        if not all_hackathons:
            return []

        # Filter by relevance to user interests
        relevant_hackathons = []

        for hackathon in all_hackathons:
            relevance_score = 0

            # Check themes
            hackathon_themes = [t.lower() for t in hackathon.get('themes', [])]
            hackathon_text = (
                hackathon.get('title', '') + ' ' +
                hackathon.get('description', '') + ' ' +
                ' '.join(hackathon_themes)
            ).lower()

            # Score by interest matching
            for interest in interests:
                interest_lower = interest.lower()

                # Direct keyword match
                if interest_lower in hackathon_text:
                    relevance_score += 3

                # Theme mapping match
                mapped_theme = interest_to_theme.get(interest_lower)
                if mapped_theme and mapped_theme in hackathon_themes:
                    relevance_score += 2

                # Partial match
                interest_words = interest_lower.split()
                for word in interest_words:
                    if len(word) > 3 and word in hackathon_text:
                        relevance_score += 1

            if relevance_score > 0:
                hackathon['relevance_score'] = relevance_score
                relevant_hackathons.append(hackathon)

        # Sort by relevance
        relevant_hackathons.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        print(f"    ✅ Found {len(relevant_hackathons)} relevant hackathons")
        return relevant_hackathons[:limit]
