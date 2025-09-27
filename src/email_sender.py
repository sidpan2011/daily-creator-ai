"""
Email Sender - generates beautiful emails and sends via Resend MCP
"""
from jinja2 import Template
from typing import List
from src.models import Recommendation

class EmailSender:
    """Email sender for Sparkflow using MCP"""
    
    def __init__(self, config, mcp_orchestrator=None):
        self.config = config
        self.mcp_orchestrator = mcp_orchestrator
    
    async def send_newsletter(self, user_data: dict, recommendations: List[Recommendation]):
        """Generate and send the newsletter email via MCP"""
        
        if not self.mcp_orchestrator:
            raise Exception("MCP orchestrator not provided")
        
        # Get the Resend MCP client from orchestrator
        resend_client = self.mcp_orchestrator.get_client('resend')
        if not resend_client:
            raise Exception("Resend MCP client not available")
        
        # Send via MCP Resend client
        await resend_client.send_newsletter(user_data, recommendations)
