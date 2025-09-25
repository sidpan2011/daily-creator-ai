"""
FastAPI application entry point for Daily Creator AI
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os
from pathlib import Path

from .api.routes import router
from .core.config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="Daily Creator AI",
    description="AI-powered personal curator for creators",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    try:
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Creator AI</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2563eb; text-align: center; }
                .status { background: #fef3c7; padding: 20px; border-radius: 5px; margin: 20px 0; }
                .api-link { display: inline-block; margin: 10px; padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; }
                .api-link:hover { background: #1d4ed8; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Daily Creator AI</h1>
                <p style="text-align: center; font-size: 18px; color: #666;">
                    AI-powered personal curator for creators and developers
                </p>
                
                <div class="status">
                    <h3>📋 Setup Status</h3>
                    <p>✅ FastAPI server is running</p>
                    <p>⚠️ Template files not found - please run demo setup</p>
                    <p>🔧 Run <code>python run_demo.py</code> to complete setup</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="/docs" class="api-link">📚 API Documentation</a>
                    <a href="/health" class="api-link">❤️ Health Check</a>
                    <a href="/api/demo/simulate" class="api-link">🎬 Demo Simulation</a>
                </div>
                
                <h3>🎯 Features</h3>
                <ul>
                    <li>🤖 AI-powered recommendations using Claude 3.5 Sonnet</li>
                    <li>📧 Beautiful email delivery via Resend MCP</li>
                    <li>📊 Trending data analysis from multiple sources</li>
                    <li>👤 Personalized user profiles with GitHub integration</li>
                    <li>🔄 Real-time feedback and learning</li>
                </ul>
                
                <h3>🚀 Quick Start</h3>
                <ol>
                    <li>Run <code>python setup_database.py</code> to create the database</li>
                    <li>Run <code>python run_demo.py</code> to start the complete demo</li>
                    <li>Visit <code>http://localhost:8000</code> to see the interface</li>
                    <li>Try the demo simulation at <code>/api/demo/simulate</code></li>
                </ol>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Daily Creator AI",
        "version": "1.0.0",
        "environment": settings.environment
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )
