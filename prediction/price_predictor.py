"""
Price Prediction Engine

Calculates specific buy/sell price targets with confidence scores.
Uses technical analysis, support/resistance, and statistical models.
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import date, timedelta
import math


class PricePredictor:
    """Price prediction engine for DSE stocks"""

    def __init__(self, currency: str = "BDT"):
        """
        Initialize price predictor

        Args:
            currency: Currency for price targets (default: BDT)
        """
        self.currency = currency

    def predict_targets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate price targets and confidence scores

        Args:
            data: Stock data with OHLCV, indicators, and fundamentals

        Returns:
            Price predictions with targets and confidence
        """
        ticker = data.get('ticker', 'Unknown')
        ohlcv = data.get('ohlcv', [])

        if not ohlcv:
            return self._no_data_response(ticker)

        # Current price
        current_price = float(ohlcv[-1]['close'])

        # Calculate support and resistance levels
        support_levels = self._calculate_support_levels(ohlcv)
        resistance_levels = self._calculate_resistance_levels(ohlcv)

        # Calculate technical targets
        technical_targets = self._calculate_technical_targets(
            current_price, ohlcv, support_levels, resistance_levels
        )

        # Calculate fundamental targets
        fundamental_targets = self._calculate_fundamental_targets(
            current_price, data.get('fundamentals', {})
        )

        # Generate buy/sell recommendations
        buy_zones = self._identify_buy_zones(
            current_price, support_levels, technical_targets
        )
        sell_targets = self._identify_sell_targets(
            current_price, resistance_levels, technical_targets
        )

        # Calculate stop loss
        stop_loss = self._calculate_stop_loss(current_price, support_levels)

        # Calculate confidence scores
        confidence = self._calculate_confidence(
            technical_targets, fundamental_targets, data
        )

        return {
            'ticker': ticker,
            'currency': self.currency,
            'current_price': current_price,
            'predictions': {
                'buy_zones': buy_zones,
                'sell_targets': sell_targets,
                'stop_loss': stop_loss,
                'technical_targets': technical_targets,
                'fundamental_targets': fundamental_targets
            },
            'levels': {
                'support': support_levels,
                'resistance': resistance_levels
            },
            'confidence': confidence,
            'horizon': '3-6 months',
            'disclaimer': 'Price predictions are estimates only. Not financial advice.'
        }

    def _calculate_support_levels(self, ohlcv: List[Dict]) -> List[float]:
        """Calculate support levels from price history"""
        if not ohlcv:
            return []

        lows = [float(bar['low']) for bar in ohlcv]
        closes = [float(bar['close']) for bar in ohlcv]

        # Method 1: Recent lows
        recent_lows = sorted(lows[-20:]) if len(lows) >= 20 else sorted(lows)
        support_1 = recent_lows[0] if recent_lows else 0

        # Method 2: Moving average support
        ma_20 = sum(closes[-20:]) / min(20, len(closes)) if closes else 0
        ma_50 = sum(closes[-50:]) / min(50, len(closes)) if len(closes) >= 50 else ma_20

        # Method 3: Fibonacci retracement
        high_52w = max(float(bar['high']) for bar in ohlcv[-252:]) if len(ohlcv) >= 252 else max(float(bar['high']) for bar in ohlcv)
        low_52w = min(float(bar['low']) for bar in ohlcv[-252:]) if len(ohlcv) >= 252 else min(float(bar['low']) for bar in ohlcv)

        fib_levels = []
        if high_52w > low_52w:
            diff = high_52w - low_52w
            fib_levels = [
                high_52w - 0.236 * diff,  # 23.6% retracement
                high_52w - 0.382 * diff,  # 38.2% retracement
                high_52w - 0.500 * diff,  # 50% retracement
                high_52w - 0.618 * diff,  # 61.8% retracement
            ]

        # Combine and sort unique levels
        all_supports = [support_1, ma_20, ma_50] + fib_levels
        unique_supports = sorted(set(s for s in all_supports if s > 0))

        return unique_supports[:5]  # Return top 5 support levels

    def _calculate_resistance_levels(self, ohlcv: List[Dict]) -> List[float]:
        """Calculate resistance levels from price history"""
        if not ohlcv:
            return []

        highs = [float(bar['high']) for bar in ohlcv]
        closes = [float(bar['close']) for bar in ohlcv]

        # Method 1: Recent highs
        recent_highs = sorted(highs[-20:], reverse=True) if len(highs) >= 20 else sorted(highs, reverse=True)
        resistance_1 = recent_highs[0] if recent_highs else 0

        # Method 2: Previous peaks
        peaks = self._find_peaks(highs)

        # Method 3: Round numbers
        current = closes[-1] if closes else 0
        round_levels = [
            math.ceil(current / 10) * 10,
            math.ceil(current / 25) * 25,
            math.ceil(current / 50) * 50,
            math.ceil(current / 100) * 100,
        ]

        # Combine and sort
        all_resistances = [resistance_1] + peaks + round_levels
        unique_resistances = sorted(set(r for r in all_resistances if r > current))

        return unique_resistances[:5]  # Return top 5 resistance levels

    def _calculate_technical_targets(
        self,
        current: float,
        ohlcv: List[Dict],
        support: List[float],
        resistance: List[float]
    ) -> Dict[str, float]:
        """Calculate technical price targets"""
        targets = {}

        # Short-term target (1 month)
        if resistance and len(resistance) > 0:
            targets['short_term'] = resistance[0]
        else:
            targets['short_term'] = current * 1.05

        # Medium-term target (3 months)
        if resistance and len(resistance) > 1:
            targets['medium_term'] = resistance[1]
        else:
            targets['medium_term'] = current * 1.15

        # Long-term target (6 months)
        if resistance and len(resistance) > 2:
            targets['long_term'] = resistance[2]
        else:
            # Use average historical return
            if len(ohlcv) >= 126:  # 6 months of data
                six_month_ago = float(ohlcv[-126]['close'])
                avg_return = (current - six_month_ago) / six_month_ago if six_month_ago > 0 else 0.1
                targets['long_term'] = current * (1 + max(avg_return, 0.1))
            else:
                targets['long_term'] = current * 1.25

        return targets

    def _calculate_fundamental_targets(
        self,
        current: float,
        fundamentals: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate fundamental value-based targets"""
        targets = {}

        # Intrinsic value target
        intrinsic = fundamentals.get('intrinsic_value')
        if intrinsic and intrinsic > 0:
            targets['intrinsic'] = float(intrinsic)

        # P/E based target
        pe = fundamentals.get('pe')
        eps = fundamentals.get('eps')
        sector_pe = fundamentals.get('sector_pe', 15)  # Default sector P/E

        if pe and eps and pe > 0 and eps > 0:
            # If P/E is below sector average, target sector P/E
            if pe < sector_pe:
                targets['pe_based'] = eps * sector_pe
            else:
                # Conservative target at current P/E
                targets['pe_based'] = eps * pe * 1.1

        # Book value based target
        book_value = fundamentals.get('book_value')
        if book_value and book_value > 0:
            # Target at 1.5x book value for growth stocks
            targets['book_value_based'] = book_value * 1.5

        return targets

    def _identify_buy_zones(
        self,
        current: float,
        support: List[float],
        targets: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify optimal buy zones"""
        buy_zones = []

        # Zone 1: Near strong support
        if support and len(support) > 0:
            strong_support = support[0]
            if current <= strong_support * 1.05:  # Within 5% of support
                buy_zones.append({
                    'price_range': f"{strong_support:.2f} - {strong_support * 1.02:.2f}",
                    'strength': 'strong',
                    'reason': 'Near strong support level'
                })

        # Zone 2: Value zone (below intrinsic value)
        intrinsic = targets.get('intrinsic')
        if intrinsic and current < intrinsic * 0.9:
            buy_zones.append({
                'price_range': f"{current * 0.98:.2f} - {current * 1.02:.2f}",
                'strength': 'strong',
                'reason': 'Trading below intrinsic value'
            })

        # Zone 3: Pullback zone
        if support and len(support) > 1:
            pullback_level = support[1]
            buy_zones.append({
                'price_range': f"{pullback_level:.2f} - {pullback_level * 1.03:.2f}",
                'strength': 'moderate',
                'reason': 'Pullback to secondary support'
            })

        return buy_zones

    def _identify_sell_targets(
        self,
        current: float,
        resistance: List[float],
        targets: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify sell targets"""
        sell_targets = []

        # Target 1: First resistance
        if resistance and len(resistance) > 0:
            sell_targets.append({
                'price': resistance[0],
                'gain_pct': ((resistance[0] - current) / current * 100),
                'timeframe': '1-2 weeks',
                'confidence': 'high'
            })

        # Target 2: Technical target
        tech_target = targets.get('medium_term')
        if tech_target:
            sell_targets.append({
                'price': tech_target,
                'gain_pct': ((tech_target - current) / current * 100),
                'timeframe': '1-3 months',
                'confidence': 'medium'
            })

        # Target 3: Intrinsic value
        intrinsic = targets.get('intrinsic')
        if intrinsic and intrinsic > current:
            sell_targets.append({
                'price': intrinsic,
                'gain_pct': ((intrinsic - current) / current * 100),
                'timeframe': '3-6 months',
                'confidence': 'medium'
            })

        # Sort by price
        sell_targets.sort(key=lambda x: x['price'])

        return sell_targets[:3]  # Return top 3 targets

    def _calculate_stop_loss(self, current: float, support: List[float]) -> Dict[str, Any]:
        """Calculate stop loss levels"""
        stop_loss = {}

        # Tight stop: 5% below current
        stop_loss['tight'] = {
            'price': current * 0.95,
            'risk_pct': 5.0
        }

        # Standard stop: Below nearest support
        if support and len(support) > 0:
            stop_loss['standard'] = {
                'price': support[0] * 0.98,
                'risk_pct': ((current - support[0] * 0.98) / current * 100)
            }

        # Wide stop: 10% below current or second support
        if support and len(support) > 1:
            wide_price = min(current * 0.90, support[1] * 0.98)
        else:
            wide_price = current * 0.90

        stop_loss['wide'] = {
            'price': wide_price,
            'risk_pct': ((current - wide_price) / current * 100)
        }

        return stop_loss

    def _calculate_confidence(
        self,
        technical: Dict[str, float],
        fundamental: Dict[str, float],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate confidence scores for predictions"""
        confidence = {
            'technical': 0.5,
            'fundamental': 0.5,
            'overall': 0.5
        }

        # Technical confidence based on data quality
        ohlcv = data.get('ohlcv', [])
        if len(ohlcv) >= 252:  # 1 year of data
            confidence['technical'] = 0.8
        elif len(ohlcv) >= 126:  # 6 months
            confidence['technical'] = 0.6
        elif len(ohlcv) >= 20:  # 1 month
            confidence['technical'] = 0.4

        # Fundamental confidence based on data availability
        fundamentals = data.get('fundamentals', {})
        if 'intrinsic_value' in fundamentals:
            confidence['fundamental'] = 0.7
        if 'pe' in fundamentals and 'eps' in fundamentals:
            confidence['fundamental'] = min(confidence['fundamental'] + 0.1, 0.9)
        if 'book_value' in fundamentals:
            confidence['fundamental'] = min(confidence['fundamental'] + 0.1, 0.9)

        # Overall confidence
        confidence['overall'] = (confidence['technical'] + confidence['fundamental']) / 2

        # Confidence level
        if confidence['overall'] >= 0.7:
            confidence['level'] = 'high'
        elif confidence['overall'] >= 0.5:
            confidence['level'] = 'medium'
        else:
            confidence['level'] = 'low'

        return confidence

    def _find_peaks(self, prices: List[float], window: int = 10) -> List[float]:
        """Find price peaks (local maxima)"""
        peaks = []
        for i in range(window, len(prices) - window):
            if all(prices[i] >= prices[j] for j in range(i - window, i + window + 1)):
                peaks.append(prices[i])

        return sorted(set(peaks), reverse=True)[:3]

    def _no_data_response(self, ticker: str) -> Dict[str, Any]:
        """Return response when no data available"""
        return {
            'ticker': ticker,
            'currency': self.currency,
            'error': 'Insufficient data for price prediction',
            'predictions': None,
            'confidence': {'overall': 0, 'level': 'none'}
        }