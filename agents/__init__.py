"""
Multi-Agent System for Stock Buddy

Specialized agents for different analysis strategies.
"""

from .momentum_agent import MomentumAgent
from .investment_agent import InvestmentAgent
from .business_agent import BusinessAgent
from .coordinator import AgentCoordinator

__all__ = [
    'MomentumAgent',
    'InvestmentAgent',
    'BusinessAgent',
    'AgentCoordinator'
]