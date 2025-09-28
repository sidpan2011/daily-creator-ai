#!/usr/bin/env python3
"""
Persnally - Simple Runner
Clean entry point for real data editorial generation
"""
import asyncio
from src.main import main

if __name__ == "__main__":
    print("⚡ Starting Persnally Editorial Generation")
    asyncio.run(main())
