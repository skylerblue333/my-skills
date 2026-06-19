"""
Data Adapter Layer for Stock Buddy Skills Suite

Provides pluggable data sources with caching and rate limiting.
"""

from .interface import DataProvider
from .providers import FileProvider, DSEProvider, MockProvider
from .cache import MemoryCache
from .rate_limiter import RateLimiter

__all__ = [
    'DataProvider',
    'FileProvider',
    'DSEProvider',
    'MockProvider',
    'MemoryCache',
    'RateLimiter'
]

__version__ = '1.0.0'