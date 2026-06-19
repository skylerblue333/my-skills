"""
In-memory cache implementation

Simple TTL-based cache for reducing API calls.
"""

import time
import hashlib
import json
from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class MemoryCache:
    """In-memory cache with TTL support"""

    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache

        Args:
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create a deterministic string from args and kwargs
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry['expiry']:
                entry['hits'] += 1
                return entry['value']
            else:
                # Remove expired entry
                del self.cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expiry': time.time() + ttl,
            'created': datetime.now().isoformat(),
            'hits': 0
        }

    def delete(self, key: str) -> bool:
        """
        Delete entry from cache

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()

    def cleanup_expired(self) -> int:
        """
        Remove expired entries

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time >= entry['expiry']
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        total_entries = len(self.cache)
        current_time = time.time()

        expired = sum(
            1 for entry in self.cache.values()
            if current_time >= entry['expiry']
        )

        total_hits = sum(entry['hits'] for entry in self.cache.values())

        return {
            'total_entries': total_entries,
            'expired_entries': expired,
            'active_entries': total_entries - expired,
            'total_hits': total_hits,
            'cache_size_bytes': self._estimate_size()
        }

    def _estimate_size(self) -> int:
        """Estimate cache size in bytes"""
        try:
            return len(json.dumps(self.cache, default=str).encode())
        except:
            return 0


class CachedProvider:
    """Wrapper to add caching to any data provider"""

    def __init__(self, provider: Any, cache: Optional[MemoryCache] = None):
        """
        Initialize cached provider

        Args:
            provider: The underlying data provider
            cache: Cache instance (creates new if None)
        """
        self.provider = provider
        self.cache = cache or MemoryCache()

    async def get_ohlcv(self, ticker: str, start_date, end_date):
        """Get OHLCV with caching"""
        cache_key = self.cache._generate_key('ohlcv', ticker, start_date, end_date)

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        # Fetch from provider
        result = await self.provider.get_ohlcv(ticker, start_date, end_date)

        # Cache result (longer TTL for historical data)
        self.cache.set(cache_key, result, ttl=3600)  # 1 hour

        return result

    async def get_fundamentals(self, ticker: str):
        """Get fundamentals with caching"""
        cache_key = self.cache._generate_key('fundamentals', ticker)

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        result = await self.provider.get_fundamentals(ticker)
        self.cache.set(cache_key, result, ttl=1800)  # 30 minutes

        return result

    async def get_market_data(self, target_date):
        """Get market data with caching"""
        cache_key = self.cache._generate_key('market', target_date)

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        result = await self.provider.get_market_data(target_date)

        # Short TTL for current date, longer for historical
        ttl = 60 if target_date == datetime.now().date() else 3600
        self.cache.set(cache_key, result, ttl=ttl)

        return result

    async def get_sector_data(self, sector: str, target_date):
        """Get sector data with caching"""
        cache_key = self.cache._generate_key('sector', sector, target_date)

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        result = await self.provider.get_sector_data(sector, target_date)
        ttl = 60 if target_date == datetime.now().date() else 3600
        self.cache.set(cache_key, result, ttl=ttl)

        return result

    async def get_news(self, ticker=None, start_date=None, end_date=None, limit=10):
        """Get news with caching"""
        cache_key = self.cache._generate_key('news', ticker, start_date, end_date, limit)

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        result = await self.provider.get_news(ticker, start_date, end_date, limit)
        self.cache.set(cache_key, result, ttl=300)  # 5 minutes

        return result

    # Delegate other methods directly
    async def health_check(self):
        return await self.provider.health_check()

    def get_capabilities(self):
        capabilities = self.provider.get_capabilities()
        capabilities['cached'] = True
        return capabilities