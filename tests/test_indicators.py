"""Test suite for momentum indicators"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skills', 'momentum-screen', 'scripts'))

import pytest
from indicators import sma, ema, rsi, macd, roc, mfi, atr


class TestIndicators:
    """Test technical indicators"""

    def test_sma(self):
        """Test Simple Moving Average"""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = sma(values, 3)

        # First two should be None (not enough data)
        assert result[0] is None
        assert result[1] is None

        # Third should be average of first 3
        assert result[2] == 2.0  # (1+2+3)/3
        assert result[3] == 3.0  # (2+3+4)/3
        assert result[9] == 9.0  # (8+9+10)/3

    def test_rsi(self):
        """Test Relative Strength Index"""
        # Create test data with known pattern
        closes = [44, 44.25, 44.5, 43.75, 44.65, 45.12, 45.84, 46.08, 45.89, 46.03,
                  45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64]

        result = rsi(closes, 14)

        # First 14 values should be None
        for i in range(14):
            assert result[i] is None

        # RSI should be calculated from index 14 onwards
        assert result[14] is not None
        assert 0 <= result[14] <= 100

    def test_macd(self):
        """Test MACD indicator"""
        closes = [float(i) for i in range(1, 51)]  # 50 data points

        result = macd(closes, fast=12, slow=26, signal=9)

        assert 'macd' in result
        assert 'signal' in result
        assert 'hist' in result

        # Should have same length as input
        assert len(result['macd']) == 50
        assert len(result['signal']) == 50
        assert len(result['hist']) == 50

    def test_roc(self):
        """Test Rate of Change"""
        closes = [100, 102, 101, 103, 105, 104, 106, 108, 107, 110, 112, 111, 113, 115]

        result = roc(closes, period=5)

        # First 5 should be None
        for i in range(5):
            assert result[i] is None

        # ROC at index 5: (104 - 100) / 100 * 100 = 4%
        assert result[5] == 4.0

    def test_mfi(self):
        """Test Money Flow Index"""
        highs = [10, 11, 12, 11, 13, 14, 13, 12, 14, 15]
        lows = [8, 9, 10, 9, 11, 12, 11, 10, 12, 13]
        closes = [9, 10, 11, 10, 12, 13, 12, 11, 13, 14]
        volumes = [1000] * 10

        result = mfi(highs, lows, closes, volumes, period=3)

        # First 3 should be None
        for i in range(3):
            assert result[i] is None

        # MFI should be between 0 and 100
        for i in range(3, len(result)):
            if result[i] is not None:
                assert 0 <= result[i] <= 100

    def test_atr(self):
        """Test Average True Range"""
        highs = [10, 11, 12, 11, 13, 14, 13, 12, 14, 15] * 3  # Need more data
        lows = [8, 9, 10, 9, 11, 12, 11, 10, 12, 13] * 3
        closes = [9, 10, 11, 10, 12, 13, 12, 11, 13, 14] * 3

        result = atr(highs, lows, closes, period=14)

        # Should have same length as input
        assert len(result) == len(closes)

        # ATR values should be positive where calculated
        for val in result:
            if val is not None:
                assert val >= 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_data(self):
        """Test with empty data"""
        assert sma([], 5) == []
        assert rsi([], 14) == []

    def test_insufficient_data(self):
        """Test with insufficient data"""
        values = [1, 2, 3]
        result = sma(values, 5)
        assert all(x is None for x in result)

    def test_negative_period(self):
        """Test with negative period"""
        values = [1, 2, 3, 4, 5]
        result = sma(values, -1)
        assert all(x is None for x in result)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])