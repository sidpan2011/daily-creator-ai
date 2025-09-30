"""
Email Sender - Premium Editorial Email Delivery
"""
from jinja2 import Template, Environment, FileSystemLoader
from datetime import datetime
from typing import Dict, Any
from .image_fetcher import ImageFetcher
from .content_formatter import ContentFormatter
import re

class PremiumEmailSender:
    def __init__(self, config, mcp_orchestrator):
        self.config = config
        self.mcp_orchestrator = mcp_orchestrator
        self.image_fetcher = ImageFetcher()
        self.content_formatter = ContentFormatter()
    
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
        """Create personalized subject lines based on intent and location"""
        
        current_date = datetime.now()
        date = current_date.strftime("%A, %B %d, %Y")
        location = user_data.get('location', '').split(',')[0]  # Get city
        
        # Intent-based subject lines
        intent_subjects = {
            'building': f"Daily update by persnally: {date}",
            'exploring': f"Daily update by persnally: {date}",
            'learning': f"Daily update by persnally: {date}",
            'launching': f"Daily update by persnally: {date}"
        }
        
        # Add location hint if there's local content
        primary_intent = editorial_content.get('user_intent', {}).get('primary_intent', 'exploring')
        subject = intent_subjects.get(primary_intent, f"Daily update by persnally: {date}")
        
        # Add location hint if there's local content
        if location and user_data.get('preferences', {}).get('prioritize_local'):
            subject = f"{location} " + subject
        
        return subject
    
    def _generate_daily_5_email_html(self, user_data: dict, daily_5_content: Dict[str, Any]) -> str:
        """Generate Daily 5 HTML email with visual formatting"""

        with open('templates/email.html', 'r') as f:
            template_content = f.read()

        # Format items with visual highlighting
        formatted_items = []

        # Defensive: Get user_intent safely
        user_intent = daily_5_content.get('user_intent', {})
        if isinstance(user_intent, dict):
            active_repos = user_intent.get('evidence', {}).get('active_repos', [])
        else:
            # user_intent is not a dict (might be a string), use empty list
            active_repos = []

        for item in daily_5_content.get('items', []):
            formatted_item = item.copy()

            # Apply visual formatting to content
            content = item.get('content', '')
            formatted_content = self.content_formatter.format_content(content, active_repos)

            # Add source attribution if available
            source = item.get('source', '')
            source_url = item.get('source_url', '')
            if source:
                formatted_content = self.content_formatter.add_source_attribution(
                    formatted_content,
                    source,
                    source_url
                )

            formatted_item['content'] = formatted_content
            formatted_items.append(formatted_item)

        # Create Jinja2 environment with custom markdown filter
        env = Environment()
        env.filters['markdown_to_html'] = self._markdown_to_html
        template = env.from_string(template_content)

        return template.render(
            user_name=user_data['name'],
            headline=daily_5_content['headline'],
            personalization_note=daily_5_content.get('personalization_note', ''),
            items=formatted_items,  # Use formatted items
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
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML for email rendering"""
        if not markdown_text:
            return ""
        
        # Convert markdown to HTML
        html = markdown_text
        
        # Convert markdown links [text](url) to HTML <a href="url">text</a>
        # This must be done FIRST before other conversions to preserve URLs
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2" style="color: #2563eb; text-decoration: none; font-weight: normal;">\1</a>', html)
        
        # Convert **bold** to <strong> with simple styling
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Convert *italic* to <em>
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Convert line breaks to <br> and paragraphs
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        
        # Wrap in paragraph tags if not already wrapped
        if not html.startswith('<p>'):
            html = f'<p>{html}</p>'
        
        # Convert bullet points (- item) to <ul><li>
        lines = html.split('<br>')
        converted_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                if not in_list:
                    converted_lines.append('<ul>')
                    in_list = True
                converted_lines.append(f'<li>{line[2:]}</li>')
            else:
                if in_list:
                    converted_lines.append('</ul>')
                    in_list = False
                converted_lines.append(line)
        
        if in_list:
            converted_lines.append('</ul>')
        
        html = '<br>'.join(converted_lines)
        
        # Convert numbered lists (1. item) to <ol><li>
        html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        if '<li>' in html and '<ul>' not in html:
            html = html.replace('<li>', '<ol><li>', 1)
            html = html.replace('</li>', '</li></ol>', 1)
        
        return html
    
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
