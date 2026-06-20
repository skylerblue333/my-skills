"""Test suite for data adapter"""

import pytest
import asyncio
from datetime import date, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_adapter import DataProvider, FileProvider, MockProvider
from data_adapter.cache import MemoryCache
from data_adapter.rate_limiter import RateLimiter, create_provider


class TestDataProvider:
    """Test data provider interface"""

    @pytest.mark.asyncio
    async def test_file_provider(self):
        """Test file provider loads fixture data"""
        provider = FileProvider({'fixtures_path': 'skills/_fixtures'})

        # Test OHLCV
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        ohlcv = await provider.get_ohlcv('GP', start_date, end_date)
        assert isinstance(ohlcv, list)

        # Test fundamentals
        fundamentals = await provider.get_fundamentals('GP')
        assert isinstance(fundamentals, dict)
        assert 'market_cap' in fundamentals

        # Test market data
        market = await provider.get_market_data(date.today())
        assert isinstance(market, dict)
        assert 'dse_index' in market

    @pytest.mark.asyncio
    async def test_mock_provider(self):
        """Test mock provider returns predictable data"""
        provider = MockProvider()

        ohlcv = await provider.get_ohlcv('TEST', date.today(), date.today())
        assert len(ohlcv) == 1
        assert ohlcv[0]['volume'] == 1000000

        fundamentals = await provider.get_fundamentals('TEST')
        assert fundamentals['pe_ratio'] == 15.0
        assert fundamentals['mock'] is True


class TestCache:
    """Test caching functionality"""

    def test_memory_cache(self):
        """Test memory cache operations"""
        cache = MemoryCache(default_ttl=5)

        # Test set and get
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'

        # Test expiry
        cache.set('key2', 'value2', ttl=0)
        assert cache.get('key2') is None

        # Test delete
        cache.set('key3', 'value3')
        assert cache.delete('key3') is True
        assert cache.get('key3') is None

        # Test stats
        stats = cache.get_stats()
        assert 'total_entries' in stats
        assert 'cache_size_bytes' in stats

    @pytest.mark.asyncio
    async def test_cached_provider(self):
        """Test caching wrapper for providers"""
        from data_adapter.cache.memory_cache import CachedProvider

        mock_provider = MockProvider()
        cache = MemoryCache()
        cached_provider = CachedProvider(mock_provider, cache)

        # First call should hit provider
        data1 = await cached_provider.get_fundamentals('TEST')

        # Second call should hit cache
        data2 = await cached_provider.get_fundamentals('TEST')

        assert data1 == data2
        assert cache.get_stats()['total_hits'] > 0


class TestRateLimiter:
    """Test rate limiting functionality"""

    @pytest.mark.asyncio
    async def test_rate_limiter(self):
        """Test rate limiter enforces limits"""
        limiter = RateLimiter(rate=2, per=1.0)  # 2 requests per second

        start = asyncio.get_event_loop().time()
        for i in range(3):
            await limiter.acquire()

        elapsed = asyncio.get_event_loop().time() - start

        # Third request should have waited
        assert elapsed >= 0.5  # Should take at least 0.5 seconds

    def test_rate_limiter_stats(self):
        """Test rate limiter statistics"""
        limiter = RateLimiter(rate=10, per=1.0)

        assert limiter.can_proceed(1) is True
        assert limiter.can_proceed(100) is False

        stats = limiter.get_stats()
        assert stats['rate'] == '10 per 1.0s'
        assert stats['total_requests'] == 0

    @pytest.mark.asyncio
    async def test_create_provider(self):
        """Test factory function creates configured provider"""
        provider = create_provider(
            provider_type='mock',
            with_cache=True,
            with_rate_limit=True,
            config={'rate_limit': 5}
        )

        # Should be able to use it
        data = await provider.get_fundamentals('TEST')
        assert data is not None

        # Check capabilities
        caps = provider.get_capabilities()
        assert caps['cached'] is True
        assert caps['rate_limited'] is True


class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test complete data pipeline"""
        provider = create_provider(
            provider_type='file',
            with_cache=True,
            with_rate_limit=True
        )

        # Should handle multiple requests
        tasks = [
            provider.get_fundamentals('GP'),
            provider.get_market_data(date.today()),
            provider.get_news(limit=5)
        ]

        results = await asyncio.gather(*tasks)

        assert all(r is not None for r in results)
        assert len(results) == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])