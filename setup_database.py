#!/usr/bin/env python3
"""
Database setup script for Daily Creator AI
Creates SQLite database with required schema for local demo
"""

import sqlite3
import os
from pathlib import Path

def create_database():
    """Create SQLite database with schema"""
    db_path = Path("local_demo.db")
    
    # Remove existing database if it exists
    if db_path.exists():
        db_path.unlink()
        print(f"Removed existing database: {db_path}")
    
    # Create new database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            skills TEXT NOT NULL,      -- JSON array
            interests TEXT NOT NULL,   -- JSON array  
            goals TEXT NOT NULL,       -- JSON array
            github_username TEXT,
            email_time TEXT DEFAULT 'morning',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Recommendations table  
    cursor.execute("""
        CREATE TABLE recommendations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            category TEXT NOT NULL,    -- BUILD, WRITE, LEARN, COLLABORATE
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            next_steps TEXT NOT NULL,  -- JSON array
            trend_connection TEXT,
            difficulty_level TEXT,
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # User feedback table
    cursor.execute("""
        CREATE TABLE user_feedback (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            recommendation_id TEXT,
            feedback TEXT NOT NULL,    -- 'like', 'dislike', 'clicked'
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (recommendation_id) REFERENCES recommendations (id)
        )
    """)
    
    # Trending cache table
    cursor.execute("""
        CREATE TABLE trending_cache (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,      -- 'github', 'hackernews', 'producthunt'
            data TEXT NOT NULL,        -- JSON data
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX idx_recommendations_user_id ON recommendations(user_id)")
    cursor.execute("CREATE INDEX idx_recommendations_category ON recommendations(category)")
    cursor.execute("CREATE INDEX idx_feedback_user_id ON user_feedback(user_id)")
    cursor.execute("CREATE INDEX idx_trending_source ON trending_cache(source)")
    cursor.execute("CREATE INDEX idx_trending_expires ON trending_cache(expires_at)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully: {db_path}")
    print("📊 Tables created:")
    print("  - users")
    print("  - recommendations") 
    print("  - user_feedback")
    print("  - trending_cache")
    print("🔍 Indexes created for optimal performance")

if __name__ == "__main__":
    create_database()
