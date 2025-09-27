"""
Base MCP Client - template for all MCP clients
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseMCPClient(ABC):
    """Base class for all MCP clients"""
    
    def __init__(self, config):
        self.config = config
        self.mcp_process = None
    
    @abstractmethod
    async def start_mcp_server(self):
        """Start the MCP server for this client"""
        pass
    
    @abstractmethod
    async def stop_mcp_server(self):
        """Stop the MCP server for this client"""
        pass
    
    @abstractmethod
    async def send_request(self, method: str, params: Dict[str, Any]):
        """Send a request to the MCP server"""
        pass
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text (simple implementation)"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
