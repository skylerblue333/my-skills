#!/usr/bin/env python3
"""
Test the data adapter implementation
"""

import asyncio
from datetime import date, timedelta
from data_adapter.rate_limiter import create_provider


async def test_data_adapter():
    """Test data adapter functionality"""
    print("Testing Data Adapter Layer")
    print("=" * 50)

    # Create a file provider with cache and rate limiting
    provider = create_provider(
        provider_type='file',
        with_cache=True,
        with_rate_limit=True,
        config={'fixtures_path': 'skills/_fixtures'}
    )

    # Test 1: Get OHLCV data
    print("\n1. Testing OHLCV data retrieval...")
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()

    ohlcv = await provider.get_ohlcv('GP', start_date, end_date)
    print(f"   Retrieved {len(ohlcv)} OHLCV records")
    if ohlcv:
        print(f"   Sample: {ohlcv[0]}")

    # Test 2: Get fundamentals
    print("\n2. Testing fundamentals retrieval...")
    fundamentals = await provider.get_fundamentals('GP')
    print(f"   Market Cap: {fundamentals.get('market_cap', 'N/A')}")
    print(f"   P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}")

    # Test 3: Get market data
    print("\n3. Testing market data retrieval...")
    market_data = await provider.get_market_data(date.today())
    print(f"   DSE Index: {market_data.get('dse_index', 'N/A')}")
    print(f"   Total Volume: {market_data.get('total_volume', 'N/A')}")

    # Test 4: Get sector data
    print("\n4. Testing sector data retrieval...")
    sector_data = await provider.get_sector_data('Banking', date.today())
    print(f"   Sector Index: {sector_data.get('index', 'N/A')}")
    print(f"   Change %: {sector_data.get('change_pct', 'N/A')}")

    # Test 5: Get news
    print("\n5. Testing news retrieval...")
    news = await provider.get_news(ticker='GP', limit=5)
    print(f"   Retrieved {len(news)} news items")
    if news:
        print(f"   Latest: {news[0].get('headline', 'N/A')}")

    # Test 6: Test caching
    print("\n6. Testing cache...")
    print("   Fetching same OHLCV data (should be cached)...")
    cached_ohlcv = await provider.get_ohlcv('GP', start_date, end_date)
    # Cache stats available through the wrapped provider if it has cache
    if hasattr(provider, 'provider') and hasattr(provider.provider, 'cache'):
        print(f"   Cache stats: {provider.provider.cache.get_stats()}")
    else:
        print("   Cache is enabled (stats not directly accessible)")

    # Test 7: Test provider capabilities
    print("\n7. Provider capabilities:")
    capabilities = provider.get_capabilities()
    for key, value in capabilities.items():
        if key != 'rate_limit':
            print(f"   {key}: {value}")

    print("\n" + "=" * 50)
    print("✅ Data Adapter Tests Complete!")


async def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\nTesting Rate Limiting")
    print("=" * 50)

    # Create provider with strict rate limiting (2 requests per second)
    provider = create_provider(
        provider_type='mock',
        with_cache=False,
        with_rate_limit=True,
        config={'rate_limit': 2, 'rate_period': 1.0}
    )

    print("Rate limit: 2 requests per second")
    print("Making 5 rapid requests...")

    start_time = asyncio.get_event_loop().time()
    for i in range(5):
        request_start = asyncio.get_event_loop().time()
        await provider.get_fundamentals(f'TEST{i}')
        elapsed = asyncio.get_event_loop().time() - request_start
        print(f"   Request {i+1}: {elapsed:.2f}s")

    total_time = asyncio.get_event_loop().time() - start_time
    print(f"Total time for 5 requests: {total_time:.2f}s")
    print(f"Rate limit stats: {provider.rate_limiter.get_stats()}")


async def main():
    """Run all tests"""
    await test_data_adapter()
    await test_rate_limiting()


if __name__ == '__main__':
    asyncio.run(main())