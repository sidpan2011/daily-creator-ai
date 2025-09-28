"""
Clean MCP Orchestrator - Resend Only
Simplified for real data integration
"""
import asyncio
from src.mcp_clients.resend_client import MCPResendClient

class MCPOrchestrator:
    """
    Simplified orchestrator focusing on Resend MCP integration
    """
    
    def __init__(self, config):
        self.config = config
        self.resend_client = MCPResendClient(config)
    
    async def initialize_all_clients(self):
        """Initialize Resend MCP client"""
        print("🔧 Initializing MCP services...")
        
        try:
            await self.resend_client.start_mcp_server()
            print("✅ Resend MCP initialized successfully")
        except Exception as e:
            print(f"❌ Resend MCP initialization failed: {e}")
            raise
    
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via Resend MCP"""
        return await self.resend_client.send_email_via_mcp(to_email, subject, html_content)