# Persnally - Personalized Tech Intelligence

> **Hackathon Project**: Built in 48 hours for the Resend MCP Hackathon. Core functionality works - it analyzes GitHub activity, curates fresh tech content, and delivers via email. Some features are still being refined (see Current Status below).

An AI-powered system that analyzes your GitHub activity and stated interests to deliver relevant tech intelligence via email.

## What It Does

**Persnally** generates personalized tech briefings by combining your interests with real-time content discovery:

- Analyzes your GitHub for technical context (skill level, tech stack)
- Gathers fresh content from GitHub trending, HackerNews, and news sources
- Uses Claude Sonnet 4 to match content to your interests
- Validates quality (real URLs, specific dates, no generic spam)
- Sends via Resend MCP integration

## Quick Start

### 1. Set Up Your Profile

Create `user_profile.json`:

```json
{
  "name": "Your Name",
  "email": "your-email@example.com",
  "github_username": "your-github-username",
  "location": "USA",
  "interests": ["ai/ml tools", "hackathons", "product development"],
  "experience_level": "intermediate_to_advanced",
  "preferences": {
    "content_style": "technical_with_business_context",
    "prioritize_local": true,
    "opportunity_types": ["hackathons", "jobs", "events"]
  }
}
```

### 2. Configure API Keys

Copy `env_template.txt` to `.env`:

```bash
cp env_template.txt .env
```

Required:
- **ANTHROPIC_API_KEY** - Get from [console.anthropic.com](https://console.anthropic.com)
- **RESEND_API_KEY** - Get from [resend.com](https://resend.com)

Optional:
- **GITHUB_TOKEN** - Get from [github.com/settings/tokens](https://github.com/settings/tokens)

### 3. Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Generate and send newsletter
python run.py

# Test without sending
python test_daily_5.py
```

## Current Status

**What Works:**
- GitHub activity analysis for technical context
- Multi-source content aggregation (GitHub trending, HackerNews, tech news)
- AI-powered content generation with Claude Sonnet 4
- Quality validation (URL verification, date checking, spam prevention)
- Email delivery via Resend MCP with professional templates
- Content diversity mechanisms (randomized source selection)

**Active Development:**
- Geographic content coverage (limited non-US sources currently)
- User profiling accuracy (balancing stated interests vs GitHub activity)
- Source reliability (some sources return limited results)
- Content diversity (randomized source selection per run)

**Known Limitations:**
- May generate 3-4 items instead of 5 if quality standards aren't met
- Geographic personalization works best for US content
- Some web crawling sources (Dev.to, Product Hunt) have limited results
- Content may repeat if run multiple times on same day (sources update daily)

This is a working proof of concept demonstrating personalized tech intelligence. Quality over quantity - better to send 4 verified items than 5 items with spam.

## How It Works

1. **Profile Analysis**: Reads your interests and analyzes GitHub for technical context
2. **Content Discovery**: Gathers fresh content (last 7-14 days) from multiple sources
3. **AI Curation**: Claude Sonnet 4 matches content to your profile
4. **Quality Validation**: Checks URLs, dates, specificity, and relevance
5. **Email Delivery**: Sends via Resend MCP with clean HTML template

The system uses your GitHub to understand skill level and tech stack, but recommends based on your stated interests. It's smart filtering, not surveillance.

## Features

### Data Sources

**Currently Working:**
- GitHub API (trending repos, releases, user activity)
- HackerNews API (top stories, discussions)
- Tech news sites (TechCrunch, The Verge, Wired via web scraping)
- Opportunity aggregation (hackathons, jobs from multiple sources)

**Partial Results:**
- Dev.to (limited article matches)
- Reddit (limited discussion matches)
- Product Hunt (limited product matches)

### Content Validation

- Real URL verification (broken links rejected)
- Specific date requirements (no vague "recently" or "this month")
- Spam phrase detection (rejects generic marketing language)
- Source diversity (each item from different source when possible)
- Freshness filtering (content from last 7-14 days)

### Email Features

- Clean, scannable HTML template
- Mobile-responsive design
- Source attribution
- Clickable real URLs
- Custom branding with Bebas Neue font

## Project Structure

```
persnally/
├── src/
│   ├── ai_engine.py           # Content generation orchestrator
│   ├── behavior_analyzer.py   # GitHub activity analysis
│   ├── content_curator.py     # Content generation & curation
│   ├── content_validator.py   # Quality validation
│   ├── email_sender.py        # Email generation & sending
│   └── config.py              # Configuration management
├── data_sources/
│   ├── github_api.py          # GitHub API client
│   ├── hackernews_api.py      # HackerNews API client
│   ├── opportunity_finder.py  # Hackathons + jobs aggregator
│   ├── realtime_web_crawler.py # Multi-source web crawler
│   └── web_research.py        # Research data aggregator
├── mcp_server/resend/         # Resend MCP integration
├── templates/
│   └── email.html             # Email template
├── user_profile.json          # User configuration
└── run.py                     # Main entry point
```

## Technical Stack

- **AI Model**: Claude Sonnet 4 (Anthropic API)
- **Email Delivery**: Resend MCP Server
- **GitHub Integration**: GitHub REST API
- **Web Scraping**: BeautifulSoup4 + httpx
- **Async Processing**: Concurrent data fetching

## Configuration

### User Profile Options

```json
{
  "interests": ["topic1", "topic2"],  // Your actual interests (most important)
  "experience_level": "beginner|intermediate|intermediate_to_advanced|expert",
  "preferences": {
    "content_style": "technical|technical_with_business_context|business_focused",
    "prioritize_local": true,  // Prefer local content when available
    "opportunity_types": ["hackathons", "jobs", "funding", "events"]
  }
}
```

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key
RESEND_API_KEY=your_resend_api_key

# Optional (prevents GitHub rate limiting)
GITHUB_TOKEN=your_github_token
```

## Testing

```bash
# Full system test (generates + sends email)
python run.py

# Test generation only (no email)
python test_daily_5.py
```

## Troubleshooting

**No relevant content found:**
- Make your interests more specific in `user_profile.json`
- Check that data sources are accessible (GitHub, HackerNews)
- Review console logs for API errors

**Email not received:**
- Verify RESEND_API_KEY is valid
- Check email address in user_profile.json
- Review Resend dashboard for delivery status

**Low geographic relevance:**
- US content is most abundant in current sources
- Geographic personalization being expanded

## Development Roadmap

**Immediate (Post-Hackathon):**
- Expand non-US content sources (India, Europe, Asia)
- Refine user profiling (better interest matching)
- Add content tracking to prevent repetition

**Future:**
- User feedback loops (thumbs up/down on items)
- Frequency controls (daily, weekly, activity-triggered)
- More data sources (newsletter APIs, conference listings)
- Analytics dashboard (engagement tracking)

## Built For

Resend MCP Hackathon - October 2025

**Key Technologies:**
- Anthropic Claude API for AI-powered curation
- Resend MCP for email delivery
- Multiple real-time data sources (GitHub, HackerNews, news APIs)

## License

MIT License

---

**Note**: This is a proof of concept demonstrating personalized tech intelligence. The core system works and sends quality content, but some features are still being refined based on real-world usage. Feedback welcome!
