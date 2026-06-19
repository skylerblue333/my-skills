"""
Data Provider Interface

Defines the contract for all data providers in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import date, datetime


class DataProvider(ABC):
    """Abstract base class for data providers"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize provider with optional configuration

        Args:
            config: Provider-specific configuration
        """
        self.config = config or {}

    @abstractmethod
    async def get_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data for a ticker

        Args:
            ticker: Stock ticker symbol
            start_date: Start date for data
            end_date: End date for data

        Returns:
            List of OHLCV records with format:
            [{
                'date': '2024-01-01',
                'open': 100.0,
                'high': 105.0,
                'low': 99.0,
                'close': 103.0,
                'volume': 1000000
            }]
        """
        pass

    @abstractmethod
    async def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """
        Get company fundamental data

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with fundamental metrics:
            {
                'market_cap': 1000000000,
                'pe_ratio': 15.5,
                'eps': 2.50,
                'dividend_yield': 0.03,
                'book_value': 50.0,
                'debt_to_equity': 0.5,
                'roe': 0.15,
                'revenue': 500000000,
                'profit_margin': 0.10
            }
        """
        pass

    @abstractmethod
    async def get_market_data(self, target_date: date) -> Dict[str, Any]:
        """
        Get market indices and statistics

        Args:
            target_date: Date for market data

        Returns:
            Dictionary with market data:
            {
                'dse_index': 5500.0,
                'dse30_index': 2100.0,
                'total_volume': 1000000000,
                'total_trades': 50000,
                'advances': 150,
                'declines': 100,
                'unchanged': 50
            }
        """
        pass

    @abstractmethod
    async def get_sector_data(self, sector: str, target_date: date) -> Dict[str, Any]:
        """
        Get sector-specific data

        Args:
            sector: Sector name (e.g., 'Banking', 'Pharmaceuticals')
            target_date: Date for sector data

        Returns:
            Dictionary with sector metrics:
            {
                'sector': 'Banking',
                'index': 1500.0,
                'change_pct': 1.5,
                'volume': 500000000,
                'top_gainers': [...],
                'top_losers': [...]
            }
        """
        pass

    @abstractmethod
    async def get_news(
        self,
        ticker: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get news and disclosures

        Args:
            ticker: Optional ticker to filter news
            start_date: Optional start date
            end_date: Optional end date
            limit: Maximum number of items to return

        Returns:
            List of news items:
            [{
                'date': '2024-01-01',
                'ticker': 'GP',
                'headline': 'Company announces dividend',
                'source': 'DSE',
                'category': 'disclosure',
                'url': 'https://...'
            }]
        """
        pass

    async def health_check(self) -> Dict[str, Any]:
        """
        Check provider health and connectivity

        Returns:
            Health status dictionary
        """
        return {
            'provider': self.__class__.__name__,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }

    def get_capabilities(self) -> Dict[str, bool]:
        """
        Get provider capabilities

        Returns:
            Dictionary of supported features
        """
        return {
            'realtime': False,
            'historical': True,
            'fundamentals': True,
            'news': True,
            'sectors': True
        }