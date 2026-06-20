"""
DSE Market Localization

Configuration and adaptations for Bangladesh market specifics.
"""

from typing import Dict, Any


class DSEConfig:
    """DSE-specific market configuration"""

    # Market hours (BST - Bangladesh Standard Time)
    MARKET_OPEN = "10:00"
    MARKET_CLOSE = "14:30"
    PRE_OPEN = "09:30"
    POST_CLOSE = "15:00"

    # DSE circuit breaker limits
    CIRCUIT_BREAKER_LIMITS = {
        'daily_upper': 0.10,  # 10% upper limit
        'daily_lower': -0.10,  # 10% lower limit
        'floor_price': 0.90,   # Floor at 90% of previous close
    }

    # Sector P/E benchmarks for DSE
    SECTOR_PE_BENCHMARKS = {
        'Banking': 8.5,
        'Financial Institutions': 12.0,
        'Insurance': 15.0,
        'Pharmaceuticals': 22.0,
        'Textile': 18.0,
        'Telecommunications': 15.0,
        'Engineering': 20.0,
        'Food & Allied': 25.0,
        'Cement': 16.0,
        'Power & Energy': 14.0,
        'IT': 28.0,
        'Services': 18.0
    }

    # DSE-specific metrics
    DSE_METRICS = {
        'min_lot_size': 10,  # Minimum trading lot
        'settlement_days': 2,  # T+2 settlement
        'currency': 'BDT',
        'tax_on_gain': 0.10,  # 10% capital gains tax
        'commission': 0.0050,  # 0.5% typical broker commission
    }

    # Bangladesh economic indicators
    MACRO_BENCHMARKS = {
        'gdp_growth': 0.065,  # 6.5% GDP growth
        'inflation': 0.060,    # 6% inflation
        'interest_rate': 0.075,  # 7.5% bank rate
        'market_cap_to_gdp': 0.30,  # Market cap as % of GDP
    }

    @classmethod
    def adapt_analysis(cls, analysis: Dict[str, Any], sector: str = None) -> Dict[str, Any]:
        """
        Adapt analysis to DSE context

        Args:
            analysis: Generic analysis results
            sector: Optional sector for specific adjustments

        Returns:
            DSE-adapted analysis
        """
        adapted = analysis.copy()

        # Add DSE context
        adapted['market'] = 'DSE'
        adapted['currency'] = cls.DSE_METRICS['currency']

        # Adjust P/E evaluation
        if 'pe_ratio' in adapted and sector:
            sector_pe = cls.SECTOR_PE_BENCHMARKS.get(sector, 15)
            pe = adapted['pe_ratio']

            if pe < sector_pe * 0.7:
                adapted['pe_assessment'] = 'undervalued'
            elif pe < sector_pe * 1.3:
                adapted['pe_assessment'] = 'fairly_valued'
            else:
                adapted['pe_assessment'] = 'overvalued'

            adapted['sector_pe_benchmark'] = sector_pe

        # Add circuit breaker warnings
        if 'price_change_pct' in adapted:
            change = adapted['price_change_pct']
            if change >= cls.CIRCUIT_BREAKER_LIMITS['daily_upper']:
                adapted['warnings'] = adapted.get('warnings', [])
                adapted['warnings'].append('At upper circuit limit')
            elif change <= cls.CIRCUIT_BREAKER_LIMITS['daily_lower']:
                adapted['warnings'] = adapted.get('warnings', [])
                adapted['warnings'].append('At lower circuit limit')

        # Add Bengali translations for key terms
        adapted['translations'] = cls._get_bengali_translations(adapted)

        return adapted

    @classmethod
    def _get_bengali_translations(cls, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Get Bengali translations for key terms"""
        translations = {
            'buy': 'ক্রয় (kroy)',
            'sell': 'বিক্রয় (bikroy)',
            'hold': 'ধরে রাখা (dhore rakha)',
            'bullish': 'ঊর্ধ্বমুখী (urdhomukhi)',
            'bearish': 'নিম্নমুখী (nimnomukhi)',
            'support': 'সমর্থন (somorthon)',
            'resistance': 'প্রতিরোধ (protirodh)',
        }

        # Add recommendation translation if present
        if 'recommendation' in analysis:
            rec = analysis['recommendation'].lower()
            if 'buy' in rec:
                translations['recommendation'] = 'ক্রয়ের সুপারিশ'
            elif 'sell' in rec:
                translations['recommendation'] = 'বিক্রয়ের সুপারিশ'
            else:
                translations['recommendation'] = 'ধরে রাখার সুপারিশ'

        return translations