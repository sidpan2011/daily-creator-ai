"""
Image Fetcher for Daily 5 Content
Fetches relevant images for each news/article item
"""
import httpx
import json
from typing import Optional

class ImageFetcher:
    def __init__(self):
        self.unsplash_access_key = None  # We'll use placeholder images for now
    
    async def get_relevant_image(self, query: str, category: str) -> Optional[str]:
        """Get relevant image URL for the given query and category"""
        
        # For now, use placeholder images with relevant themes
        # In production, you could integrate with Unsplash API or other image services
        
        category_images = {
            "🎯": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop",  # Target/focus
            "⚡": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=200&fit=crop",  # Lightning/urgent
            "🧠": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=200&fit=crop",  # Brain/learning
            "💰": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=200&fit=crop",  # Money/opportunity
            "🔮": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=200&fit=crop",  # Future/crystal ball
        }
        
        # Get category emoji from category string
        category_emoji = category.split()[0] if category else "🎯"
        
        # Use specific images based on query keywords
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['blockchain', 'crypto', 'web3', 'bitcoin', 'ethereum']):
            return "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400&h=200&fit=crop"
        elif any(word in query_lower for word in ['ai', 'machine learning', 'neural', 'gpt', 'ml']):
            return "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=200&fit=crop"
        elif any(word in query_lower for word in ['startup', 'funding', 'venture', 'accelerator']):
            return "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&h=200&fit=crop"
        elif any(word in query_lower for word in ['hackathon', 'competition', 'coding', 'programming']):
            return "https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?w=400&h=200&fit=crop"
        elif any(word in query_lower for word in ['github', 'repository', 'code', 'development']):
            return "https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400&h=200&fit=crop"
        else:
            # Fallback to category-based image
            return category_images.get(category_emoji, category_images["🎯"])
    
    def get_placeholder_image(self, width: int = 400, height: int = 200, text: str = "News") -> str:
        """Get a placeholder image with text"""
        # Using placeholder.com service
        return f"https://via.placeholder.com/{width}x{height}/667eea/ffffff?text={text.replace(' ', '+')}"
    
    async def fetch_unsplash_image(self, query: str) -> Optional[str]:
        """Fetch image from Unsplash API (requires API key)"""
        if not self.unsplash_access_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={
                        "query": query,
                        "per_page": 1,
                        "orientation": "landscape"
                    },
                    headers={
                        "Authorization": f"Client-ID {self.unsplash_access_key}"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["results"]:
                        return data["results"][0]["urls"]["small"]
        except Exception as e:
            print(f"⚠️ Failed to fetch Unsplash image: {e}")
        
        return None
