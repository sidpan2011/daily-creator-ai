"""
MCP Resend Client - handles email sending via Resend MCP server
"""
import asyncio
import subprocess
import json
import httpx
from typing import Dict, Any, List
from src.models import Recommendation

class MCPResendClient:
    """MCP client for Resend email sending"""
    
    def __init__(self, config):
        self.config = config
        self.mcp_server_path = "mcp_server/resend/mcp-send-email/build/index.js"
        self.mcp_process = None
    
    async def start_mcp_server(self):
        """Start the Resend MCP server"""
        try:
            # Start the MCP server process
            self.mcp_process = await asyncio.create_subprocess_exec(
                "node", self.mcp_server_path,
                "--key", self.config.RESEND_API_KEY,
                "--sender", "onboarding@resend.dev",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print("✅ Resend MCP server started")
            return True
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
    
    async def stop_mcp_server(self):
        """Stop the Resend MCP server"""
        if self.mcp_process:
            self.mcp_process.terminate()
            await self.mcp_process.wait()
            print("✅ Resend MCP server stopped")
    
    async def send_email_via_mcp(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email via MCP server"""
        if not self.mcp_process:
            print("❌ MCP server not started, falling back to HTTP")
            return await self._send_via_http(to_email, subject, html_content, text_content)
        
        # Create the MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "send-email",
                "arguments": {
                    "to": to_email,
                    "subject": subject,
                    "text": text_content or self._html_to_text(html_content),
                    "html": html_content,
                    "from": "onboarding@resend.dev"
                }
            }
        }
        
        print(f"📤 Sending MCP request: {json.dumps(mcp_request, indent=2)}")
        
        try:
            # Send request to MCP server
            request_json = json.dumps(mcp_request) + "\n"
            self.mcp_process.stdin.write(request_json.encode())
            await self.mcp_process.stdin.drain()
            
            # Read response
            response_line = await self.mcp_process.stdout.readline()
            response = json.loads(response_line.decode().strip())
            
            print(f"📥 MCP response: {json.dumps(response, indent=2)}")
            
            if "error" in response:
                raise Exception(f"MCP Error: {response['error']}")
            
            # Check if the result indicates an error (like Resend 403)
            result = response.get("result", {})
            if result.get("isError", False):
                error_content = result.get("content", [{}])[0].get("text", "")
                if "403" in error_content or "You can only send testing emails" in error_content:
                    print("🔄 Resend test domain restriction detected, falling back to HTTP...")
                    return await self._send_via_http(to_email, subject, html_content, text_content)
                else:
                    raise Exception(f"MCP Server Error: {error_content}")
            
            return result
            
        except Exception as e:
            print(f"❌ MCP email sending failed: {e}")
            # Fallback to direct HTTP call
            print("🔄 Falling back to direct HTTP call...")
            return await self._send_via_http(to_email, subject, html_content, text_content)
    
    async def _send_via_http(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Fallback: Send email via direct HTTP call"""
        headers = {
            "Authorization": f"Bearer {self.config.RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": "onboarding@resend.dev",
            "to": [to_email],  # Send to actual user email
            "subject": subject,
            "html": html_content,
            "text": text_content or self._html_to_text(html_content)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.resend.com/emails", headers=headers, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Email sent successfully via HTTP fallback")
                return {"success": True}
            else:
                print(f"❌ HTTP fallback failed: {response.text}")
                return {"success": False, "error": response.text}
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text (simple implementation)"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    async def send_newsletter(self, user_data: dict, recommendations: List[Recommendation]):
        """Send newsletter via MCP"""
        print(f"📧 Sending newsletter to {user_data['email']} via MCP...")
        
        # Generate email content
        html_content = self._generate_email_html(user_data, recommendations)
        text_content = self._generate_text_content(user_data, recommendations)
        
        # Send via MCP
        result = await self.send_email_via_mcp(
            to_email=user_data['email'],
            subject="Your Daily Sparkflow ⚡",
            html_content=html_content,
            text_content=text_content
        )
        
        print(f"📧 MCP result: {result}")
    
    def _generate_email_html(self, user_data: dict, recommendations: List[Recommendation]) -> str:
        """Generate HTML email using Jinja2 template"""
        from jinja2 import Template
        
        try:
            with open('templates/email.html', 'r') as f:
                template_content = f.read()
            
            template = Template(template_content)
            
            return template.render(
                user_name=user_data['name'],
                recommendations=recommendations
            )
        except FileNotFoundError:
            # Fallback to simple HTML if template not found
            return self._generate_simple_html(user_data, recommendations)
    
    def _generate_simple_html(self, user_data: dict, recommendations: List[Recommendation]) -> str:
        """Generate simple HTML email as fallback"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Your Daily Sparkflow</title>
            <style>
                body {{ font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; }}
                .header {{ text-align: center; padding: 20px; background: #f8f9fa; }}
                .recommendation {{ background: white; margin: 20px 0; padding: 20px; border-left: 4px solid #007bff; }}
                .category {{ background: #007bff; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚡ Your Daily Sparkflow</h1>
                <p>Hi {user_data['name']}! Here are today's personalized recommendations:</p>
            </div>
        """
        
        for rec in recommendations:
            html += f"""
            <div class="recommendation">
                <span class="category">{rec.category}</span>
                <h2>{rec.title}</h2>
                <p>{rec.description}</p>
                <p><strong>Next steps:</strong></p>
                <ul>
            """
            for step in rec.next_steps:
                html += f"<li>{step}</li>"
            
            html += f"""
                </ul>
                <p><em>Why now:</em> {rec.trend_connection}</p>
            </div>
            """
        
        html += """
            <div style="text-align: center; padding: 20px; color: #666;">
                <p>Made personally for you by Sparkflow AI</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_text_content(self, user_data: dict, recommendations: List[Recommendation]) -> str:
        """Generate plain text email content"""
        text = f"""
⚡ Your Daily Sparkflow

Hi {user_data['name']}! Here are today's personalized recommendations:

"""
        
        for i, rec in enumerate(recommendations, 1):
            text += f"""
{i}. {rec.category}: {rec.title}
   {rec.description}
   
   Next steps:
"""
            for step in rec.next_steps:
                text += f"   - {step}\n"
            
            text += f"   Why now: {rec.trend_connection}\n\n"
        
        text += """
Made personally for you by Sparkflow AI
"""
        
        return text
