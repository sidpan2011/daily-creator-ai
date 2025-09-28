"""
Email Sender - Premium Editorial Email Delivery
"""
from jinja2 import Template
from datetime import datetime
from typing import Dict, Any
from .image_fetcher import ImageFetcher

class PremiumEmailSender:
    def __init__(self, config, mcp_orchestrator):
        self.config = config
        self.mcp_orchestrator = mcp_orchestrator
        self.image_fetcher = ImageFetcher()
    
    async def send_daily_5_newsletter(self, user_data: dict, daily_5_content: Dict[str, Any]):
        """Send Daily 5 newsletter with behavioral intelligence"""
        
        # Skip image processing since we removed images from template
        
        # Generate Daily 5 email content
        html_content = self._generate_daily_5_email_html(user_data, daily_5_content)
        
        # Use the subject line from behavioral analysis
        subject = daily_5_content['subject_line']
        
        # Send via MCP orchestrator
        success = await self.mcp_orchestrator.send_email(
            user_data['email'],
            subject,
            html_content
        )
        
        if success:
            print(f"✅ Daily 5 sent to {user_data['name']}")
        else:
            print(f"❌ Failed to send Daily 5 to {user_data['name']}")
        
        return success
    
    async def send_editorial_newsletter(self, user_data: dict, editorial_content: Dict[str, str]):
        """Send premium editorial newsletter (legacy method)"""
        
        # Generate premium email content
        html_content = self._generate_premium_email_html(user_data, editorial_content)
        
        # Create engaging subject line
        subject = self._create_premium_subject_line(user_data, editorial_content)
        
        # Send via MCP orchestrator
        success = await self.mcp_orchestrator.send_email(
            user_data['email'],
            subject,
            html_content
        )
        
        if success:
            print(f"✅ Premium editorial sent to {user_data['name']}")
        else:
            print(f"❌ Failed to send editorial to {user_data['name']}")
        
        return success
    
    def _create_premium_subject_line(self, user_data: dict, editorial_content: Dict[str, str]) -> str:
        """Create premium, engaging subject lines"""
        
        current_date = datetime.now()
        date_formats = [
            current_date.strftime("%B %d"),  # "October 15"
            current_date.strftime("%b %d"),   # "Oct 15"
        ]
        
        subject_templates = [
            f"Your update: {date_formats[0]}",
            f"Persnally: {date_formats[0]}",
            f"Today's insights: {date_formats[0]}",
            f"Your briefing: {date_formats[0]}",
            f"Persnally curated: {date_formats[0]}",
        ]
        
        # Select based on user preferences or rotate
        selected_subject = subject_templates[0]  # Use first for consistency
        
        return selected_subject
    
    def _generate_daily_5_email_html(self, user_data: dict, daily_5_content: Dict[str, Any]) -> str:
        """Generate Daily 5 HTML email"""
        
        with open('templates/email.html', 'r') as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        return template.render(
            user_name=user_data['name'],
            headline=daily_5_content['headline'],
            personalization_note=daily_5_content.get('personalization_note', ''),
            items=daily_5_content.get('items', []),
            key_insights=daily_5_content.get('key_insights', []),
            date=daily_5_content['date']
        )
    
    def _generate_premium_email_html(self, user_data: dict, editorial_content: Dict[str, str]) -> str:
        """Generate premium HTML email (legacy method)"""
        
        with open('templates/email.html', 'r') as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        return template.render(
            user_name=user_data['name'],
            headline=editorial_content['headline'],
            intro=editorial_content.get('intro', ''),
            updates=editorial_content.get('updates', []),
            content=self._format_content_for_email(editorial_content.get('content', '')),
            key_insights=editorial_content.get('key_insights', []),
            date=editorial_content['date']
        )
    
    def _format_content_for_email(self, content: str) -> str:
        """Format content for email HTML"""
        # Split into paragraphs and wrap in <p> tags
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            if para.strip():
                # Handle basic formatting
                formatted_para = para.strip()
                
                # Add paragraph tags
                formatted_paragraphs.append(f"<p>{formatted_para}</p>")
        
        return '\n'.join(formatted_paragraphs)
    
    async def _add_images_to_items(self, items):
        """Add relevant images to each item"""
        items_with_images = []
        
        for item in items:
            # Get image based on the image_query if available, otherwise use title
            query = item.get('image_query', item.get('title', 'news'))
            category = item.get('category', '🎯')
            
            # Get relevant image
            image_url = await self.image_fetcher.get_relevant_image(query, category)
            
            # Add image to item
            item_with_image = item.copy()
            item_with_image['image'] = image_url
            items_with_images.append(item_with_image)
        
        return items_with_images
