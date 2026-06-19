"""
Rate Limiter

Implements token bucket algorithm for API rate limiting.
"""

import time
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, rate: int = 10, per: float = 1.0):
        """
        Initialize rate limiter

        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.updated_at = time.time()
        self.lock = asyncio.Lock()

        # Statistics
        self.total_requests = 0
        self.blocked_requests = 0
        self.wait_times = []

    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens, waiting if necessary

        Args:
            tokens: Number of tokens to acquire

        Returns:
            Wait time in seconds (0 if no wait)
        """
        async with self.lock:
            wait_time = await self._acquire_internal(tokens)
            self.total_requests += 1
            if wait_time > 0:
                self.blocked_requests += 1
                self.wait_times.append(wait_time)
            return wait_time

    async def _acquire_internal(self, tokens: int) -> float:
        """Internal acquire logic"""
        while True:
            now = time.time()

            # Add tokens based on elapsed time
            elapsed = now - self.updated_at
            self.tokens = min(
                self.rate,
                self.tokens + elapsed * (self.rate / self.per)
            )
            self.updated_at = now

            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0.0

            # Calculate wait time
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed * (self.per / self.rate)

            # Wait for tokens to replenish
            await asyncio.sleep(wait_time)
            return wait_time

    def can_proceed(self, tokens: int = 1) -> bool:
        """
        Check if request can proceed without waiting

        Args:
            tokens: Number of tokens needed

        Returns:
            True if tokens available, False otherwise
        """
        now = time.time()
        elapsed = now - self.updated_at

        available = min(
            self.rate,
            self.tokens + elapsed * (self.rate / self.per)
        )

        return available >= tokens

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        return {
            'rate': f'{self.rate} per {self.per}s',
            'available_tokens': self.tokens,
            'total_requests': self.total_requests,
            'blocked_requests': self.blocked_requests,
            'block_rate': (
                self.blocked_requests / self.total_requests
                if self.total_requests > 0 else 0
            ),
            'avg_wait_time': (
                sum(self.wait_times) / len(self.wait_times)
                if self.wait_times else 0
            )
        }

    def reset(self) -> None:
        """Reset rate limiter to full capacity"""
        self.tokens = self.rate
        self.updated_at = time.time()


class RateLimitedProvider:
    """Wrapper to add rate limiting to any data provider"""

    def __init__(
        self,
        provider: Any,
        rate_limiter: Optional[RateLimiter] = None
    ):
        """
        Initialize rate-limited provider

        Args:
            provider: The underlying data provider
            rate_limiter: Rate limiter instance
        """
        self.provider = provider
        self.rate_limiter = rate_limiter or RateLimiter(rate=10, per=1.0)

    async def get_ohlcv(self, ticker: str, start_date, end_date):
        """Get OHLCV with rate limiting"""
        await self.rate_limiter.acquire()
        return await self.provider.get_ohlcv(ticker, start_date, end_date)

    async def get_fundamentals(self, ticker: str):
        """Get fundamentals with rate limiting"""
        await self.rate_limiter.acquire()
        return await self.provider.get_fundamentals(ticker)

    async def get_market_data(self, target_date):
        """Get market data with rate limiting"""
        await self.rate_limiter.acquire()
        return await self.provider.get_market_data(target_date)

    async def get_sector_data(self, sector: str, target_date):
        """Get sector data with rate limiting"""
        await self.rate_limiter.acquire()
        return await self.provider.get_sector_data(sector, target_date)

    async def get_news(self, ticker=None, start_date=None, end_date=None, limit=10):
        """Get news with rate limiting"""
        await self.rate_limiter.acquire()
        return await self.provider.get_news(ticker, start_date, end_date, limit)

    async def health_check(self):
        """Health check doesn't consume rate limit"""
        return await self.provider.health_check()

    def get_capabilities(self):
        """Get capabilities with rate limit info"""
        capabilities = self.provider.get_capabilities()
        capabilities['rate_limited'] = True
        capabilities['rate_limit'] = self.rate_limiter.get_stats()
        return capabilities


def create_provider(
    provider_type: str = 'file',
    with_cache: bool = True,
    with_rate_limit: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Factory function to create configured data provider

    Args:
        provider_type: Type of provider ('file', 'dse', 'mock')
        with_cache: Enable caching
        with_rate_limit: Enable rate limiting
        config: Provider configuration

    Returns:
        Configured provider instance
    """
    from .providers import FileProvider, DSEProvider, MockProvider
    from .cache import MemoryCache

    # Create base provider
    if provider_type == 'file':
        provider = FileProvider(config)
    elif provider_type == 'dse':
        provider = DSEProvider(config)
    elif provider_type == 'mock':
        provider = MockProvider(config)
    else:
        raise ValueError(f'Unknown provider type: {provider_type}')

    # Add caching
    if with_cache:
        from .cache.memory_cache import CachedProvider
        cache = MemoryCache()
        provider = CachedProvider(provider, cache)

    # Add rate limiting
    if with_rate_limit:
        rate_limiter = RateLimiter(
            rate=config.get('rate_limit', 10) if config else 10,
            per=config.get('rate_period', 1.0) if config else 1.0
        )
        provider = RateLimitedProvider(provider, rate_limiter)

    return provider