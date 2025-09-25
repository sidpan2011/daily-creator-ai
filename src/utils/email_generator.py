"""
Email template rendering utilities for Daily Creator AI
"""

from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from ..models.user import User
from ..models.recommendation import Recommendation

class EmailGenerator:
    """Email template rendering and generation"""
    
    def __init__(self):
        self.template_dir = Path("templates")
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
    
    def render_html_email(self, user: User, email_content: Dict[str, str], 
                         recommendations: List[Recommendation]) -> str:
        """Render HTML email template"""
        try:
            template = self.env.get_template("email_template.html")
            
            # Prepare template data
            template_data = {
                "subject": email_content.get("subject", "Your Daily Creator Recommendations"),
                "greeting": email_content.get("greeting", f"Hello {user.name}"),
                "intro": email_content.get("intro", "Here are your personalized recommendations"),
                "recommendations": recommendations,
                "closing": email_content.get("closing", "Happy creating!"),
                "feedback_urls": self._generate_feedback_urls(user.id, recommendations)
            }
            
            return template.render(**template_data)
            
        except Exception as e:
            print(f"❌ HTML email rendering error: {e}")
            return self._generate_fallback_html(user, email_content, recommendations)
    
    def render_text_email(self, user: User, email_content: Dict[str, str], 
                         recommendations: List[Recommendation]) -> str:
        """Render text email template"""
        try:
            template = self.env.get_template("email_template.txt")
            
            # Prepare template data
            template_data = {
                "subject": email_content.get("subject", "Your Daily Creator Recommendations"),
                "greeting": email_content.get("greeting", f"Hello {user.name}"),
                "intro": email_content.get("intro", "Here are your personalized recommendations"),
                "recommendations": recommendations,
                "closing": email_content.get("closing", "Happy creating!"),
                "feedback_urls": self._generate_feedback_urls(user.id, recommendations),
                "unsubscribe_url": f"https://dailycreator.ai/unsubscribe?user={user.id}"
            }
            
            return template.render(**template_data)
            
        except Exception as e:
            print(f"❌ Text email rendering error: {e}")
            return self._generate_fallback_text(user, email_content, recommendations)
    
    def _generate_feedback_urls(self, user_id: str, recommendations: List[Recommendation]) -> Dict[str, str]:
        """Generate feedback tracking URLs"""
        base_url = "https://dailycreator.ai/api/feedback"
        
        return {
            "like": f"{base_url}?user={user_id}&action=like&rec={recommendations[0].id if recommendations else 'none'}",
            "dislike": f"{base_url}?user={user_id}&action=dislike&rec={recommendations[0].id if recommendations else 'none'}",
            "clicked": f"{base_url}?user={user_id}&action=clicked&rec={recommendations[0].id if recommendations else 'none'}"
        }
    
    def _generate_fallback_html(self, user: User, email_content: Dict[str, str], 
                               recommendations: List[Recommendation]) -> str:
        """Generate fallback HTML email if template fails"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{email_content.get('subject', 'Your Daily Creator Recommendations')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .recommendation {{ background: #f8fafc; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Daily Creator AI</h1>
            </div>
            <div class="content">
                <h2>{email_content.get('greeting', f'Hello {user.name}')}</h2>
                <p>{email_content.get('intro', 'Here are your personalized recommendations')}</p>
                
                {self._render_recommendations_html(recommendations)}
                
                <p>{email_content.get('closing', 'Happy creating!')}</p>
            </div>
            <div class="footer">
                <p>Daily Creator AI • Powered by Claude 3.5 Sonnet & Resend</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_fallback_text(self, user: User, email_content: Dict[str, str], 
                               recommendations: List[Recommendation]) -> str:
        """Generate fallback text email if template fails"""
        text = f"""
🚀 Daily Creator AI - Your Personal Curator
===============================================

{email_content.get('greeting', f'Hello {user.name}')}

{email_content.get('intro', 'Here are your personalized recommendations')}

{self._render_recommendations_text(recommendations)}

{email_content.get('closing', 'Happy creating!')}

---
Daily Creator AI • Powered by Claude 3.5 Sonnet & Resend
Built for the Resend MCP Hackathon
        """
        return text.strip()
    
    def _render_recommendations_html(self, recommendations: List[Recommendation]) -> str:
        """Render recommendations as HTML"""
        html_parts = []
        for i, rec in enumerate(recommendations, 1):
            html_parts.append(f"""
                <div class="recommendation">
                    <h3>{i}. {rec.title}</h3>
                    <p>{rec.description}</p>
                    <p><strong>Category:</strong> {rec.category.value} | 
                       <strong>Difficulty:</strong> {rec.difficulty_level.value} | 
                       <strong>Score:</strong> {int(rec.score * 100)}%</p>
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        {''.join(f'<li>{step}</li>' for step in rec.next_steps)}
                    </ul>
                    {f'<p><em>📈 Trend Connection: {rec.trend_connection}</em></p>' if rec.trend_connection else ''}
                </div>
            """)
        return ''.join(html_parts)
    
    def _render_recommendations_text(self, recommendations: List[Recommendation]) -> str:
        """Render recommendations as text"""
        text_parts = []
        for i, rec in enumerate(recommendations, 1):
            text_parts.append(f"""
{i}. {rec.title}
   {rec.description}
   
   Category: {rec.category.value}
   Difficulty: {rec.difficulty_level.value}
   Score: {int(rec.score * 100)}%
   
   Next Steps:
   {chr(10).join(f'   - {step}' for step in rec.next_steps)}
   
   {f'📈 Trend Connection: {rec.trend_connection}' if rec.trend_connection else ''}
   
   ---
            """)
        return ''.join(text_parts)
