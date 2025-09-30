"""
Content Deduplication System
Prevents sending the same content multiple times within 7 days
"""
import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class ContentCache:
    def __init__(self, cache_file: str = "content_history.json"):
        """Initialize content cache"""
        self.cache_file = cache_file
        self.cache_data = self._load_cache()
        self.cache_days = 3  # Reduced from 7 to 3 days for more variety

    def _load_cache(self) -> Dict:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load content cache: {e}")
                return {}
        return {}

    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save content cache: {e}")

    def _generate_content_hash(self, title: str, url: str) -> str:
        """Generate unique hash for content item"""
        content_str = f"{title.lower().strip()}|{url.lower().strip()}"
        return hashlib.md5(content_str.encode()).hexdigest()

    def _clean_old_entries(self, user_email: str):
        """Remove entries older than cache_days"""
        if user_email not in self.cache_data:
            return

        cutoff_date = datetime.now() - timedelta(days=self.cache_days)

        old_count = len(self.cache_data[user_email].get('content_hashes', []))

        self.cache_data[user_email]['content_hashes'] = [
            entry for entry in self.cache_data[user_email].get('content_hashes', [])
            if datetime.fromisoformat(entry['sent_date']) >= cutoff_date
        ]

        new_count = len(self.cache_data[user_email]['content_hashes'])

        if old_count != new_count:
            print(f"  🧹 Cleaned {old_count - new_count} old cache entries (older than {self.cache_days} days)")

    def check_duplicate(self, user_email: str, title: str, url: str) -> bool:
        """
        Check if content was recently sent to user

        Returns:
            True if duplicate (already sent), False if new
        """
        content_hash = self._generate_content_hash(title, url)

        if user_email not in self.cache_data:
            return False  # New user, no duplicates

        # Check if this hash exists in recent sends
        for entry in self.cache_data[user_email].get('content_hashes', []):
            if entry['hash'] == content_hash:
                # Found duplicate
                sent_date = datetime.fromisoformat(entry['sent_date'])
                days_ago = (datetime.now() - sent_date).days
                print(f"  ⚠️ Duplicate found: '{title}' (sent {days_ago} days ago)")
                return True

        return False  # Not a duplicate

    def add_sent_content(self, user_email: str, items: List[Dict[str, Any]]):
        """
        Add sent content items to cache

        Args:
            user_email: User's email address
            items: List of content items that were sent
        """
        if user_email not in self.cache_data:
            self.cache_data[user_email] = {
                'content_hashes': []
            }

        # Clean old entries before adding new ones
        self._clean_old_entries(user_email)

        current_date = datetime.now().isoformat()

        for item in items:
            title = item.get('title', '')
            url = item.get('url', '')

            if title and url:
                content_hash = self._generate_content_hash(title, url)

                self.cache_data[user_email]['content_hashes'].append({
                    'hash': content_hash,
                    'sent_date': current_date,
                    'title': title[:100],  # Store truncated title for reference
                    'url': url
                })

        # Save updated cache
        self._save_cache()
        print(f"  ✅ Added {len(items)} items to content cache for {user_email}")

    def filter_duplicates(self, user_email: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out duplicate items from a list

        Args:
            user_email: User's email address
            items: List of potential content items

        Returns:
            List of items that are NOT duplicates
        """
        print(f"\n🔍 Checking for duplicate content...")
        print(f"  Checking {len(items)} items against cache")

        # Clean old entries first
        self._clean_old_entries(user_email)

        non_duplicates = []
        duplicate_count = 0

        for item in items:
            title = item.get('title', '')
            url = item.get('url', '')

            if not self.check_duplicate(user_email, title, url):
                non_duplicates.append(item)
            else:
                duplicate_count += 1

        print(f"  ✅ Found {len(non_duplicates)} new items ({duplicate_count} duplicates removed)")

        return non_duplicates

    def get_cache_stats(self, user_email: str) -> Dict[str, Any]:
        """Get statistics about user's cache"""
        if user_email not in self.cache_data:
            return {
                'total_cached': 0,
                'oldest_date': None,
                'newest_date': None
            }

        entries = self.cache_data[user_email].get('content_hashes', [])

        if not entries:
            return {
                'total_cached': 0,
                'oldest_date': None,
                'newest_date': None
            }

        dates = [datetime.fromisoformat(e['sent_date']) for e in entries]

        return {
            'total_cached': len(entries),
            'oldest_date': min(dates).isoformat(),
            'newest_date': max(dates).isoformat()
        }