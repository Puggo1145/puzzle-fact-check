"""API module for the Puzzle Fact Check system"""
from .app import app
from .service import agent_service

__all__ = [
    "app",
    "agent_service"
]
