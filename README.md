# 🚀 Daily Creator AI - Resend MCP Hackathon

**AI-powered personal curator for creators and developers**

Daily Creator AI analyzes user profiles, fetches trending data via MCP servers, generates personalized recommendations using Claude 3.5 Sonnet, and sends beautiful emails via Resend MCP.

## 🎯 Project Overview

This project demonstrates a complete AI-powered recommendation system built for the Resend MCP Hackathon. It showcases:

- **AI-Powered Recommendations**: Claude 3.5 Sonnet generates personalized recommendations
- **MCP Integration**: Seamless integration with Resend, GitHub, PostgreSQL, and Web Scraper MCP servers
- **Beautiful Email Delivery**: Professional HTML email templates sent via Resend MCP
- **Trending Data Analysis**: Real-time data from GitHub, Hacker News, Product Hunt, and more
- **Interactive Web Interface**: Modern, responsive web application

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   FastAPI App   │    │   Core Engine   │
│   (HTML/CSS/JS) │◄──►│   (Routes)      │◄──►│   (Orchestrator)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 │                                 │
                       ▼                                 ▼                                 ▼
              ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
              │   MCP Manager   │              │  AI Processor   │              │   Database      │
              │                 │              │  (Claude 3.5)   │              │   (SQLite)      │
              └─────────────────┘              └─────────────────┘              └─────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Resend MCP  │ │ GitHub MCP  │ │Postgres MCP │ │Web Scraper  │
│             │ │             │ │             │ │    MCP      │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation & Demo

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd daily-creator-ai
   ```

2. **Run the complete demo**:
   ```bash
   python run_demo.py
   ```

3. **Access the application**:
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Manual Setup (Optional)

If you prefer manual setup:

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python setup_database.py

# Setup MCP servers (optional - demo works without)
python setup_mcps.py

# Start server
python -m uvicorn src.main:app --reload
```

## 🎬 Demo Features

### 1. User Registration
- Beautiful web form for user profile creation
- Skills, interests, and goals collection
- GitHub username integration
- Email time preferences

### 2. AI-Powered Recommendations
- Claude 3.5 Sonnet analyzes user profile
- Generates 3 personalized recommendations
- Connects recommendations to current trends
- Provides clear next steps and difficulty levels

### 3. Email Delivery
- Professional HTML email templates
- Personalized content for each user
- Feedback tracking URLs
- Responsive design for all devices

### 4. MCP Integration
- **Resend MCP**: Email delivery and management
- **GitHub MCP**: User profile enrichment and trending repos
- **PostgreSQL MCP**: Database operations
- **Web Scraper MCP**: Content extraction and trending data

### 5. Interactive Demo
- Try the demo simulation: `/api/demo/simulate`
- Register new users and see instant recommendations
- View demo data and sample recommendations

## 📊 Demo Data

The project includes comprehensive demo data:

- **5 Demo Users**: Different skill sets and interests
- **Trending Data**: GitHub, Hacker News, Product Hunt, Reddit, Twitter
- **Sample Recommendations**: Pre-generated examples
- **Cached Trends**: Realistic trending data for demo

## 🔧 Configuration

### Environment Variables

Create `.env.local` (or copy from `.env.example`):

```bash
# AI Configuration
ANTHROPIC_API_KEY=your_claude_api_key_here

# Email Configuration  
RESEND_API_KEY=your_resend_api_key_here

# GitHub Integration
GITHUB_TOKEN=your_github_token_here

# Database
DATABASE_URL=sqlite:///./local_demo.db

# Application
ENVIRONMENT=development
DEBUG=True
```

### Demo Mode

The application runs in **demo mode** by default, which means:
- ✅ All MCP integrations work with mock data
- ✅ AI recommendations generated (with Claude if API key provided)
- ✅ Email sending simulated (shows in console)
- ✅ Database operations work with SQLite
- ✅ Web interface fully functional

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/

# Run specific test modules
pytest tests/test_api.py
pytest tests/test_ai.py
pytest tests/test_mcp.py
```

## 📁 Project Structure

```
daily-creator-ai/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── engine.py           # Main orchestrator class
│   │   └── config.py           # Configuration management
│   ├── mcp/
│   │   ├── manager.py          # MCP integration manager
│   │   ├── resend_mcp.py       # Resend MCP wrapper
│   │   ├── github_mcp.py       # GitHub MCP wrapper
│   │   ├── postgres_mcp.py     # PostgreSQL MCP wrapper
│   │   └── web_scraper_mcp.py  # Web scraping MCP wrapper
│   ├── ai/
│   │   ├── processor.py        # AI recommendation engine
│   │   └── prompts.py          # Claude prompt templates
│   ├── models/
│   │   ├── user.py            # User data models
│   │   ├── recommendation.py   # Recommendation models
│   │   └── trending.py        # Trending data models
│   ├── api/
│   │   └── routes.py          # FastAPI routes
│   └── utils/
│       └── email_generator.py  # Email template rendering
├── templates/
│   ├── index.html             # Web interface
│   ├── email_template.html    # HTML email template
│   └── email_template.txt     # Text email fallback
├── static/
│   ├── style.css              # Styling
│   └── app.js                  # Frontend JavaScript
├── demo/
│   ├── demo_users.json        # Demo users
│   ├── cached_trends.json     # Cached trending data
│   └── sample_recommendations.json
├── tests/
│   ├── test_mcp.py
│   ├── test_ai.py
│   └── test_api.py
├── run_demo.py               # Demo startup script
├── setup_database.py         # Database setup
├── setup_mcps.py            # MCP server setup
└── requirements.txt          # Python dependencies
```

## 🎯 Key Features Demonstrated

### 1. **Resend MCP Integration**
- Email template rendering with Jinja2
- HTML and text email formats
- Feedback tracking URLs
- Professional email design

### 2. **Claude 3.5 Sonnet Integration**
- Sophisticated prompt engineering
- Personalized recommendation generation
- Trend-aware content creation
- Context-aware email personalization

### 3. **MCP Server Architecture**
- Modular MCP wrapper design
- Error handling and retry logic
- Mock data for demo purposes
- Real MCP server integration ready

### 4. **Modern Web Application**
- Responsive design
- Interactive JavaScript
- Real-time API integration
- Professional UI/UX

## 🏆 Hackathon Highlights

This project demonstrates:

- **Complete MCP Integration**: All required MCP servers integrated
- **AI-Powered Personalization**: Claude 3.5 Sonnet for intelligent recommendations
- **Professional Email Delivery**: Beautiful templates via Resend MCP
- **Production-Ready Architecture**: Clean, modular, testable code
- **Comprehensive Demo**: Ready-to-run demonstration with realistic data

## 📝 API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `POST /api/users/register` - User registration
- `POST /api/users/{user_id}/recommendations/generate` - Generate recommendations
- `GET /api/users/{user_id}/recommendations` - Get user recommendations
- `POST /api/users/{user_id}/recommendations/{rec_id}/feedback` - Submit feedback
- `POST /api/demo/simulate` - Run demo simulation
- `GET /api/demo/users` - Get demo users
- `GET /api/demo/trends` - Get demo trends

## 🤝 Contributing

This project was built for the Resend MCP Hackathon. For questions or feedback:

1. Check the demo simulation: `/api/demo/simulate`
2. Review the API documentation: `/docs`
3. Test the web interface: http://localhost:8000

## 📄 License

Built for the Resend MCP Hackathon. See hackathon guidelines for usage terms.

---

**🚀 Daily Creator AI - Your Personal Curator Powered by AI**
