#!/usr/bin/env python3
"""
Daily Creator AI - Demo Runner Script
Complete setup and startup for hackathon demo
"""

import asyncio
import subprocess
import sys
import os
import json
import sqlite3
from pathlib import Path
import time

def print_banner():
    """Print demo banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🚀 Daily Creator AI - Resend MCP Hackathon Demo            ║
║                                                              ║
║  AI-powered personal curator for creators and developers    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Set up the database"""
    print("🗄️ Setting up database...")
    try:
        subprocess.run([sys.executable, "setup_database.py"], check=True, capture_output=True)
        print("✅ Database setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def load_demo_data():
    """Load demo data into database"""
    print("📊 Loading demo data...")
    try:
        db_path = Path("local_demo.db")
        if not db_path.exists():
            print("❌ Database not found. Run setup_database.py first.")
            return False
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Load demo users
        with open("demo/demo_users.json", "r") as f:
            demo_users = json.load(f)
        
        for i, user in enumerate(demo_users):
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (user["email"],))
            if cursor.fetchone():
                continue
            
            # Insert user with unique ID
            cursor.execute("""
                INSERT INTO users (id, name, email, skills, interests, goals, 
                                 github_username, email_time, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"demo_user_{i+1}_{int(time.time())}",
                user["name"],
                user["email"],
                json.dumps(user["skills"]),
                json.dumps(user["interests"]),
                json.dumps(user["goals"]),
                user["github_username"],
                user["email_time"],
                "2024-01-15T10:30:00Z",
                "2024-01-15T10:30:00Z"
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Loaded {len(demo_users)} demo users")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load demo data: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("🔧 Checking environment configuration...")
    
    env_file = Path(".env.local")
    if not env_file.exists():
        print("⚠️ .env.local not found, using default demo configuration")
        return True
    
    print("✅ Environment configuration found")
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Daily Creator AI server...")
    print("\n📋 Server Information:")
    print("  🌐 Web Interface: http://localhost:8000")
    print("  📚 API Documentation: http://localhost:8000/docs")
    print("  ❤️ Health Check: http://localhost:8000/health")
    print("  🎬 Demo Simulation: http://localhost:8000/api/demo/simulate")
    
    print("\n🎯 Demo Features:")
    print("  ✅ User registration with AI-powered recommendations")
    print("  ✅ Beautiful email templates (simulated sending)")
    print("  ✅ Trending data analysis from multiple sources")
    print("  ✅ GitHub profile enrichment")
    print("  ✅ Interactive web interface")
    print("  ✅ Complete MCP integration (demo mode)")
    
    print("\n💡 Tips for Demo:")
    print("  • Try the demo simulation first")
    print("  • Register a new user to see the full flow")
    print("  • Check the console for email simulation output")
    print("  • All MCP integrations work with mock data")
    
    print("\n" + "="*60)
    print("🎉 Daily Creator AI is ready for demo!")
    print("="*60)
    
    try:
        # Start the server
        subprocess.run([sys.executable, "-m", "uvicorn", "src.main:app", 
                       "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

def run_quick_test():
    """Run a quick test to verify everything works"""
    print("🧪 Running quick system test...")
    
    try:
        # Test imports
        from src.core.engine import DailyCreatorEngine
        from src.models.user import UserProfile
        from src.ai.processor import AIProcessor
        
        print("✅ Core modules imported successfully")
        
        # Test database connection
        db_path = Path("local_demo.db")
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            conn.close()
            print(f"✅ Database connection successful ({user_count} users)")
        else:
            print("⚠️ Database not found")
        
        # Test demo data
        demo_files = ["demo/demo_users.json", "demo/cached_trends.json", "demo/sample_recommendations.json"]
        for file in demo_files:
            if Path(file).exists():
                print(f"✅ {file} found")
            else:
                print(f"⚠️ {file} not found")
        
        print("✅ System test completed")
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main demo runner function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Demo setup failed at dependency installation")
        return
    
    # Check environment
    if not check_environment():
        print("❌ Demo setup failed at environment check")
        return
    
    # Setup database
    if not setup_database():
        print("❌ Demo setup failed at database setup")
        return
    
    # Load demo data
    if not load_demo_data():
        print("❌ Demo setup failed at demo data loading")
        return
    
    # Run quick test
    if not run_quick_test():
        print("❌ Demo setup failed at system test")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("🚀 Starting Daily Creator AI demo...")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
