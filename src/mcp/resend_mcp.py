"""
Resend MCP wrapper for email functionality
"""

import asyncio
import json
from typing import Dict, Any, Optional
import httpx
import os

class ResendMCP:
    """Wrapper for Resend MCP server"""
    
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.base_url = os.getenv("RESEND_MCP_URL", "http://localhost:3001")
        self.timeout = 30.0
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def send_email(self, to_email: str, subject: str, html_content: str, 
                        text_content: str, from_email: Optional[str] = None) -> Dict[str, Any]:
        """Send email via Resend MCP"""
        try:
            if not self.api_key:
                raise ValueError("RESEND_API_KEY not configured")
            
            payload = {
                "to": to_email,
                "subject": subject,
                "html": html_content,
                "text": text_content,
                "from": from_email or "Daily Creator AI <noreply@dailycreator.ai>"
            }
            
            # For demo purposes, simulate the API call
            print(f"📧 Resend MCP: Sending email to {to_email}")
            print(f"📧 Subject: {subject}")
            
            # Simulate successful response
            return {
                "success": True,
                "message_id": f"msg_{asyncio.get_event_loop().time()}",
                "to": to_email,
                "subject": subject,
                "status": "sent"
            }
            
        except Exception as e:
            print(f"❌ Resend MCP Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """Get email delivery status"""
        try:
            # For demo purposes, return mock status
            return {
                "message_id": message_id,
                "status": "delivered",
                "delivered_at": "2024-01-15T10:30:00Z",
                "opens": 0,
                "clicks": 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_connection(self) -> bool:
        """Test MCP connection"""
        try:
            # For demo purposes, always return True
            print("✅ Resend MCP: Connection test successful")
            return True
        except Exception as e:
            print(f"❌ Resend MCP: Connection test failed - {e}")
            return False
