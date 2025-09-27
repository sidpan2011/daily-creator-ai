# Sparkflow - Simplified AI Newsletter

A simple, focused Python project for an AI-powered personalized newsletter called "Sparkflow". This is a minimal but production-ready implementation that analyzes user profiles, fetches trending data, uses Claude AI to generate personalized recommendations, and sends them via email.

## 🎯 Core Concept

Sparkflow analyzes user profiles, fetches trending data via MCP servers, uses Claude AI to generate personalized recommendations, and sends them via email using Resend.

## 📁 Project Structure

```
sparkflow/
├── src/
│   ├── __init__.py
│   ├── main.py              # Single entry point script
│   ├── models.py            # Data classes
│   ├── mcp_orchestrator.py  # MCP coordination hub
│   ├── ai_engine.py         # Claude AI integration
│   ├── email_sender.py      # Email generation & sending
│   ├── core/
│   │   └── config.py        # Configuration
│   ├── mcp_clients/         # MCP client implementations
│   │   ├── __init__.py
│   │   ├── base_client.py   # Base class for MCP clients
│   │   ├── resend_client.py # Resend email MCP client
│   │   └── README.md        # MCP clients documentation
│   └── models/              # Data models
│       ├── __init__.py
│       ├── user.py
│       ├── recommendation.py
│       └── trending.py
├── templates/
│   └── email.html           # Single email template
├── data/
│   ├── users.json           # Simple JSON file for users
│   └── trends_cache.json    # Cached trending data
├── mcp_server/              # MCP servers
│   └── resend/              # Resend MCP server
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
├── README.md               # Documentation
└── demo.py                 # Demo runner script
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file with:

```env
ANTHROPIC_API_KEY=your_claude_key_here
RESEND_API_KEY=your_resend_key_here
GITHUB_TOKEN=your_github_token_here
```

### 3. Run Demo

```bash
python demo.py
```

This will:
- Create sample user data
- Generate AI recommendations
- Send personalized emails

## 📦 Dependencies

- **python-dotenv**: Environment variable management
- **anthropic**: Claude AI integration
- **httpx**: HTTP requests for APIs
- **jinja2**: Email templating
- **pydantic**: Data validation

## 🔧 Core Components

### 1. `src/main.py` - Entry Point
Single script that orchestrates the entire process:
- Loads users from JSON
- Gets trending data via MCP
- Generates AI recommendations
- Sends personalized emails

### 2. `src/ai_engine.py` - Claude Integration
Handles AI recommendation generation:
- Creates prompts based on user profile and trends
- Calls Claude 3.5 Sonnet API
- Parses responses into structured recommendations
- Falls back to mock data if AI fails

### 3. `src/email_sender.py` - Email Generation
Creates and sends beautiful emails:
- Uses Jinja2 templates for HTML emails
- Sends via Resend API
- Handles errors gracefully

### 4. `src/mcp_client.py` - MCP Integration
Simplified MCP client:
- Loads trending data from cache files
- Ready for real MCP server integration
- Handles missing data gracefully

## 📧 Email Template

The email template (`templates/email.html`) includes:
- Beautiful, responsive design
- Personalized recommendations
- Clear call-to-actions
- Trend connections

## 🗄 Data Storage

Uses simple JSON files instead of databases:
- `data/users.json`: User profiles
- `data/trends_cache.json`: Cached trending data

## 🎬 Demo Features

The demo includes:
- 3 sample users with different profiles
- Trending GitHub repositories
- HackerNews topics
- AI-generated recommendations
- Email sending simulation

## 🔄 Next Steps

1. **Test basic functionality** - Run `python demo.py`
2. **Add real MCP integration** - One server at a time
3. **Improve AI prompts** - Make recommendations more impressive
4. **Polish email template** - Make it even more beautiful
5. **Add real MCP servers** - GitHub, Resend, Web Scraper

## 🛠 Development

### Running the Main Script

```bash
python src/main.py
```

### Adding New Users

Edit `data/users.json` to add new users with their profiles.

### Customizing Recommendations

Modify the prompt in `src/ai_engine.py` to change how recommendations are generated.

### Styling Emails

Update `templates/email.html` to customize the email appearance.

## 📝 Notes

- This is a simplified version focused on core functionality
- MCP integration is prepared but uses cached data initially
- Error handling is included for production readiness
- The structure is designed to be easily extensible

## 🎯 What This Creates

After running this setup:
- ✅ Simple Python project with clear structure
- ✅ Claude AI integration for recommendations  
- ✅ Email generation with Jinja2 templates
- ✅ JSON-based user/data storage
- ✅ Demo script that works immediately
- ✅ Foundation to add MCP servers gradually

Keep it simple, understand each part, then gradually enhance! This approach will help you learn MCP while building something that actually works.
