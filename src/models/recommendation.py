"""
Recommendation data models for Sparkflow
"""

from dataclasses import dataclass
from typing import List

@dataclass
class Recommendation:
    """AI-generated recommendation"""
    category: str  # BUILD, WRITE, LEARN
    title: str
    description: str
    next_steps: List[str]
    trend_connection: str
