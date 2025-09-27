"""
MCP Orchestrator - coordinates all MCP clients and servers
Central hub for managing MCP communications
"""
import json
from typing import Dict, Any, List
from src.models import TrendingData
from src.mcp_clients import MCPResendClient

class MCPOrchestrator:
    """Orchestrates all MCP clients and servers for Sparkflow"""
    
    def __init__(self, config):
        self.config = config
        self.clients = {}
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize all MCP clients"""
        self.clients = {
            'resend': MCPResendClient(self.config),
            # Future MCP clients will be added here
            # 'github': MCPGitHubClient(self.config),
            # 'web_scraper': MCPWebScraperClient(self.config),
        }
    
    async def start_all_servers(self):
        """Start all MCP servers"""
        print("🔌 Starting all MCP servers...")
        
        for name, client in self.clients.items():
            if hasattr(client, 'start_mcp_server'):
                try:
                    await client.start_mcp_server()
                    print(f"✅ {name.title()} MCP server started")
                except Exception as e:
                    print(f"❌ Failed to start {name} MCP server: {e}")
    
    async def stop_all_servers(self):
        """Stop all MCP servers"""
        print("🔌 Stopping all MCP servers...")
        
        for name, client in self.clients.items():
            if hasattr(client, 'stop_mcp_server'):
                try:
                    await client.stop_mcp_server()
                    print(f"✅ {name.title()} MCP server stopped")
                except Exception as e:
                    print(f"❌ Failed to stop {name} MCP server: {e}")
    
    async def get_trending_data(self) -> TrendingData:
        """Get trending data from multiple sources via MCP"""
        
        # For now, load from cache file (we'll add real MCP later)
        try:
            with open('data/trends_cache.json', 'r') as f:
                cached_data = json.load(f)
        except FileNotFoundError:
            # Return empty data if cache doesn't exist
            cached_data = {
                'github_trending': [],
                'hackernews': [],
                'last_updated': ''
            }
            
        # TODO: Replace with real MCP calls
        # - GitHub MCP for trending repos
        # - Web scraper MCP for HackerNews
        
        return TrendingData(
            github_repos=cached_data.get('github_trending', []),
            hackernews_topics=cached_data.get('hackernews', []),
            timestamp=cached_data.get('last_updated', '')
        )
    
    def get_client(self, client_name: str):
        """Get a specific MCP client by name"""
        return self.clients.get(client_name)
    
    def list_available_clients(self) -> List[str]:
        """List all available MCP clients"""
        return list(self.clients.keys())
