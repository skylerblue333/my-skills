# Trend Detection

Identify and analyze market trends using multiple technical indicators and timeframes.

## Overview

This skill detects trend direction, strength, and potential reversals in DSE stocks using moving averages, trend lines, and momentum indicators. **NOT FINANCIAL ADVICE** - all analysis is for educational purposes only.

## Usage

Requires client-provided OHLCV data across multiple timeframes for comprehensive trend analysis.

## Core Functions

### 1. Trend Identification
- **Moving Average Analysis**: SMA, EMA, WMA crossovers
- **Trend Line Detection**: Support/resistance trend lines
- **Higher Highs/Lower Lows**: Price structure analysis
- **ADX Indicator**: Trend strength measurement

### 2. Multi-Timeframe Analysis
- Daily, weekly, monthly trend alignment
- Timeframe confluence zones
- Dominant trend identification
- Trend conflict resolution

### 3. Trend Strength Metrics
- ADX value and direction
- Trend duration analysis
- Volume confirmation
- Momentum alignment

### 4. Reversal Detection
- Divergence analysis (price vs indicators)
- Chart pattern recognition
- Volume climax identification
- Sentiment extremes

### 5. Trend Projection
- Fibonacci extensions
- Measured moves
- Channel projections
- Time cycle analysis

## Output Format

```json
{
  "thinkingCard": {
    "primaryTrend": {
      "direction": "UPTREND",
      "strength": 0.789012,
      "duration": 45,
      "adxValue": 34.567890
    },
    "timeframeAnalysis": {
      "daily": "UPTREND",
      "weekly": "UPTREND",
      "monthly": "SIDEWAYS"
    },
    "trendLines": [
      {"type": "support", "slope": 0.023456, "touches": 4}
    ],
    "reversalSignals": {
      "divergence": false,
      "patternDetected": null,
      "volumeClimactic": false
    },
    "projection": {
      "targetPrice": 125.678901,
      "supportLevel": 98.765432,
      "timeframe": "2-3 weeks"
    },
    "disclaimer": "NOT FINANCIAL ADVICE - Educational purposes only"
  }
}
```

## Implementation Notes

- Minimum 50 data points for reliable trends
- Use log scale for long-term trends
- Validate with volume confirmation
- All calculations use 6+ decimal precision