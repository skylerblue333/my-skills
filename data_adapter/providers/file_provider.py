"""
File-based Data Provider

Reads data from JSON fixture files for testing and development.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import date, datetime
from pathlib import Path

from ..interface import DataProvider


class FileProvider(DataProvider):
    """Provider that reads data from JSON fixture files"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize file provider

        Args:
            config: Configuration with 'fixtures_path' key
        """
        super().__init__(config)
        self.fixtures_path = Path(
            config.get('fixtures_path', 'skills/_fixtures') if config else 'skills/_fixtures'
        )

    def _load_fixture(self, filename: str) -> Dict[str, Any]:
        """Load data from a fixture file"""
        filepath = self.fixtures_path / filename
        if not filepath.exists():
            # Try alternative path
            filepath = Path('skills/_fixtures') / filename

        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)

        # Return sample data if fixture not found
        return {}

    async def get_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Get OHLCV data from fixtures"""
        # Load sample input which contains OHLCV data
        data = self._load_fixture('sample_input.json')

        if 'ohlcv' in data:
            # Filter by date range
            ohlcv = []
            for record in data['ohlcv']:
                record_date = datetime.strptime(record['date'], '%Y-%m-%d').date()
                if start_date <= record_date <= end_date:
                    ohlcv.append(record)
            return ohlcv

        # Return synthetic data if no fixture
        return self._generate_synthetic_ohlcv(ticker, start_date, end_date)

    async def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Get fundamental data from fixtures"""
        data = self._load_fixture('sample_input.json')

        if 'fundamentals' in data:
            return data['fundamentals']

        # Return sample fundamentals
        return {
            'market_cap': 10000000000,  # 10B BDT
            'pe_ratio': 15.5,
            'eps': 12.50,
            'dividend_yield': 0.045,
            'book_value': 150.0,
            'debt_to_equity': 0.35,
            'roe': 0.18,
            'revenue': 5000000000,  # 5B BDT
            'profit_margin': 0.12,
            'beta': 1.1,
            'shares_outstanding': 80000000
        }

    async def get_market_data(self, target_date: date) -> Dict[str, Any]:
        """Get market data from fixtures"""
        data = self._load_fixture('sample_input.json')

        if 'market' in data:
            return data['market']

        # Return sample market data
        return {
            'dse_index': 5523.45,
            'dse30_index': 2156.78,
            'total_volume': 1234567890,
            'total_trades': 52341,
            'total_value': 9876543210,
            'advances': 142,
            'declines': 98,
            'unchanged': 47,
            'date': target_date.isoformat()
        }

    async def get_sector_data(self, sector: str, target_date: date) -> Dict[str, Any]:
        """Get sector data from fixtures"""
        # Sample sector data
        sectors = {
            'Banking': {
                'index': 1523.45,
                'change_pct': 1.25,
                'volume': 450000000,
                'trades': 12500
            },
            'Pharmaceuticals': {
                'index': 3421.56,
                'change_pct': -0.75,
                'volume': 280000000,
                'trades': 8900
            },
            'Textile': {
                'index': 892.34,
                'change_pct': 0.45,
                'volume': 150000000,
                'trades': 5600
            }
        }

        sector_data = sectors.get(sector, {
            'index': 1000.0,
            'change_pct': 0.0,
            'volume': 100000000,
            'trades': 5000
        })

        return {
            'sector': sector,
            'date': target_date.isoformat(),
            **sector_data,
            'top_gainers': [
                {'ticker': f'{sector[:3]}1', 'change_pct': 5.2},
                {'ticker': f'{sector[:3]}2', 'change_pct': 3.8}
            ],
            'top_losers': [
                {'ticker': f'{sector[:3]}3', 'change_pct': -4.1},
                {'ticker': f'{sector[:3]}4', 'change_pct': -2.9}
            ]
        }

    async def get_news(
        self,
        ticker: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get news from fixtures"""
        data = self._load_fixture('sample_input.json')

        news = []
        if 'overnight_news' in data:
            for item in data['overnight_news'][:limit]:
                news_item = {
                    'date': item.get('date', date.today().isoformat()),
                    'ticker': item.get('ticker'),
                    'headline': item.get('headline'),
                    'source': item.get('source', 'DSE'),
                    'category': 'news'
                }

                # Filter by ticker if specified
                if ticker and news_item['ticker'] != ticker:
                    continue

                news.append(news_item)

        # Add sample news if needed
        if len(news) < 3:
            news.extend([
                {
                    'date': date.today().isoformat(),
                    'ticker': ticker or 'GP',
                    'headline': 'Q3 earnings exceed expectations',
                    'source': 'DSE',
                    'category': 'disclosure'
                },
                {
                    'date': date.today().isoformat(),
                    'ticker': ticker or 'BATBC',
                    'headline': 'Dividend announcement for FY2024',
                    'source': 'Company',
                    'category': 'dividend'
                }
            ])

        return news[:limit]

    def _generate_synthetic_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Generate synthetic OHLCV data for testing"""
        import random
        from datetime import timedelta

        ohlcv = []
        current_date = start_date
        base_price = 200.0

        while current_date <= end_date:
            # Skip weekends (simplified)
            if current_date.weekday() < 5:
                variation = random.uniform(-0.03, 0.03)  # ±3% daily variation
                close = base_price * (1 + variation)
                high = close * random.uniform(1.0, 1.02)
                low = close * random.uniform(0.98, 1.0)
                open_price = base_price

                ohlcv.append({
                    'date': current_date.isoformat(),
                    'open': round(open_price, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'close': round(close, 2),
                    'volume': random.randint(500000, 2000000)
                })

                base_price = close

            current_date += timedelta(days=1)

        return ohlcv

    def get_capabilities(self) -> Dict[str, bool]:
        """Get provider capabilities"""
        return {
            'realtime': False,
            'historical': True,
            'fundamentals': True,
            'news': True,
            'sectors': True,
            'fixture_based': True
        }