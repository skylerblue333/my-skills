"""
Mock Data Provider

Returns predictable test data for unit testing.
"""

from typing import Dict, List, Optional, Any
from datetime import date, timedelta

from ..interface import DataProvider


class MockProvider(DataProvider):
    """Mock provider for testing"""

    async def get_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Return mock OHLCV data"""
        ohlcv = []
        current = start_date
        price = 100.0

        while current <= end_date:
            if current.weekday() < 5:  # Weekdays only
                ohlcv.append({
                    'date': current.isoformat(),
                    'open': price,
                    'high': price * 1.02,
                    'low': price * 0.98,
                    'close': price * 1.01,
                    'volume': 1000000
                })
                price *= 1.01

            current += timedelta(days=1)

        return ohlcv

    async def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Return mock fundamentals"""
        return {
            'ticker': ticker,
            'market_cap': 1000000000,
            'pe_ratio': 15.0,
            'eps': 10.0,
            'dividend_yield': 0.03,
            'book_value': 100.0,
            'debt_to_equity': 0.5,
            'roe': 0.15,
            'revenue': 500000000,
            'profit_margin': 0.10,
            'mock': True
        }

    async def get_market_data(self, target_date: date) -> Dict[str, Any]:
        """Return mock market data"""
        return {
            'dse_index': 5500.0,
            'dse30_index': 2100.0,
            'total_volume': 1000000000,
            'total_trades': 50000,
            'total_value': 5000000000,
            'advances': 150,
            'declines': 100,
            'unchanged': 50,
            'date': target_date.isoformat(),
            'mock': True
        }

    async def get_sector_data(self, sector: str, target_date: date) -> Dict[str, Any]:
        """Return mock sector data"""
        return {
            'sector': sector,
            'index': 1500.0,
            'change_pct': 1.5,
            'volume': 500000000,
            'trades': 10000,
            'date': target_date.isoformat(),
            'top_gainers': [
                {'ticker': 'MOCK1', 'change_pct': 5.0},
                {'ticker': 'MOCK2', 'change_pct': 3.0}
            ],
            'top_losers': [
                {'ticker': 'MOCK3', 'change_pct': -4.0},
                {'ticker': 'MOCK4', 'change_pct': -2.0}
            ],
            'mock': True
        }

    async def get_news(
        self,
        ticker: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Return mock news"""
        news = []
        for i in range(min(limit, 5)):
            news.append({
                'date': date.today().isoformat(),
                'ticker': ticker or f'MOCK{i}',
                'headline': f'Mock news item {i+1}',
                'source': 'Mock Source',
                'category': 'test',
                'mock': True
            })
        return news