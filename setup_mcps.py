#!/usr/bin/env python3
"""
MCP Servers Setup Script for Daily Creator AI
Installs and configures required MCP servers for the hackathon demo
"""

import subprocess
import json
import os
from pathlib import Path
import asyncio
import httpx

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_mcp_directory():
    """Create .mcp directory for configuration files"""
    mcp_dir = Path(".mcp")
    mcp_dir.mkdir(exist_ok=True)
    print(f"📁 Created MCP configuration directory: {mcp_dir}")
    return mcp_dir

def create_mcp_config(mcp_dir):
    """Create MCP configuration file"""
    config = {
        "servers": {
            "resend": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-resend"],
                "env": {
                    "RESEND_API_KEY": os.getenv("RESEND_API_KEY", "demo_key")
                }
            },
            "github": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "demo_token")
                }
            },
            "postgres": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-postgres"],
                "env": {
                    "POSTGRES_CONNECTION_STRING": os.getenv("DATABASE_URL", "sqlite:///./local_demo.db")
                }
            },
            "web-scraper": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-web-scraper"],
                "env": {}
            },
            "filesystem": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem"],
                "env": {
                    "ALLOWED_DIRECTORIES": "."
                }
            }
        }
    }
    
    config_file = mcp_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📝 Created MCP configuration: {config_file}")
    return config_file

def install_mcp_servers():
    """Install required MCP servers via npm"""
    servers = [
        "@modelcontextprotocol/server-resend",
        "@modelcontextprotocol/server-github", 
        "@modelcontextprotocol/server-postgres",
        "@modelcontextprotocol/server-web-scraper",
        "@modelcontextprotocol/server-filesystem"
    ]
    
    print("📦 Installing MCP servers...")
    
    for server in servers:
        success = run_command(f"npm install -g {server}", f"Installing {server}")
        if not success:
            print(f"⚠️ Failed to install {server}, continuing with demo mode...")
    
    print("✅ MCP server installation completed")

def create_startup_script(mcp_dir):
    """Create startup script for MCP servers"""
    script_content = """#!/bin/bash
# Daily Creator AI - MCP Servers Startup Script

echo "🚀 Starting MCP servers for Daily Creator AI..."

# Start Resend MCP Server
echo "📧 Starting Resend MCP server on port 3001..."
npx @modelcontextprotocol/server-resend --port 3001 &
RESEND_PID=$!

# Start GitHub MCP Server  
echo "🐙 Starting GitHub MCP server on port 3002..."
npx @modelcontextprotocol/server-github --port 3002 &
GITHUB_PID=$!

# Start PostgreSQL MCP Server
echo "🗄️ Starting PostgreSQL MCP server on port 3003..."
npx @modelcontextprotocol/server-postgres --port 3003 &
POSTGRES_PID=$!

# Start Web Scraper MCP Server
echo "🕷️ Starting Web Scraper MCP server on port 3004..."
npx @modelcontextprotocol/server-web-scraper --port 3004 &
SCRAPER_PID=$!

echo "✅ All MCP servers started!"
echo "📊 Server status:"
echo "  - Resend MCP: http://localhost:3001 (PID: $RESEND_PID)"
echo "  - GitHub MCP: http://localhost:3002 (PID: $GITHUB_PID)"
echo "  - PostgreSQL MCP: http://localhost:3003 (PID: $POSTGRES_PID)"
echo "  - Web Scraper MCP: http://localhost:3004 (PID: $SCRAPER_PID)"

# Wait for user input to stop servers
echo "Press Ctrl+C to stop all MCP servers..."
wait
"""
    
    script_file = mcp_dir / "start_mcp_servers.sh"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(script_file, 0o755)
    
    print(f"📜 Created MCP startup script: {script_file}")
    return script_file

async def test_mcp_connections():
    """Test connections to MCP servers"""
    print("🧪 Testing MCP server connections...")
    
    servers = [
        ("Resend MCP", "http://localhost:3001"),
        ("GitHub MCP", "http://localhost:3002"),
        ("PostgreSQL MCP", "http://localhost:3003"),
        ("Web Scraper MCP", "http://localhost:3004")
    ]
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in servers:
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    print(f"✅ {name}: Connected successfully")
                else:
                    print(f"⚠️ {name}: Responded with status {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: Connection failed - {e}")
                print(f"   This is expected if servers aren't running yet")

def create_demo_mode_notice():
    """Create a notice about demo mode"""
    notice = """
# Daily Creator AI - MCP Demo Mode

This project is configured to run in **demo mode** for the Resend MCP Hackathon.

## Demo Mode Features:
- ✅ All MCP integrations work with mock data
- ✅ AI recommendations generated using Claude 3.5 Sonnet (if API key provided)
- ✅ Email sending simulated (shows in console)
- ✅ Database operations work with SQLite
- ✅ Web interface fully functional

## To Enable Real MCP Servers:
1. Install Node.js and npm
2. Run: `python setup_mcps.py`
3. Start MCP servers: `bash .mcp/start_mcp_servers.sh`
4. Update .env.local with real API keys

## For Hackathon Demo:
The current setup is perfect for demonstrating the complete workflow without requiring external API keys or MCP server setup.
"""
    
    with open("MCP_DEMO_MODE.md", "w") as f:
        f.write(notice)
    
    print("📄 Created MCP demo mode notice: MCP_DEMO_MODE.md")

def main():
    """Main setup function"""
    print("🚀 Daily Creator AI - MCP Servers Setup")
    print("=" * 50)
    
    # Check if Node.js is installed
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        print("✅ Node.js and npm are installed")
        node_available = True
    except subprocess.CalledProcessError:
        print("⚠️ Node.js/npm not found. Will create demo mode configuration.")
        node_available = False
    
    # Create MCP directory and configuration
    mcp_dir = create_mcp_directory()
    config_file = create_mcp_config(mcp_dir)
    
    if node_available:
        # Install MCP servers
        install_mcp_servers()
        
        # Create startup script
        startup_script = create_startup_script(mcp_dir)
        
        # Test connections (will fail if servers aren't running)
        asyncio.run(test_mcp_connections())
        
        print("\n🎉 MCP setup completed!")
        print(f"📁 Configuration: {config_file}")
        print(f"🚀 Start servers: bash {startup_script}")
        print("\n💡 For demo purposes, the app works without running MCP servers")
    else:
        create_demo_mode_notice()
        print("\n🎉 Demo mode configuration completed!")
        print("💡 The app will work with mock MCP responses")
    
    print("\n📋 Next steps:")
    print("1. Run: python setup_database.py")
    print("2. Run: python run_demo.py")
    print("3. Visit: http://localhost:8000")

if __name__ == "__main__":
    main()
