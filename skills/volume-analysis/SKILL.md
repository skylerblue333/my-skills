# Volume Analysis

Analyze trading volume patterns to confirm price movements and identify accumulation/distribution.

## Overview

This skill analyzes volume patterns, on-balance volume, and volume-price relationships for DSE stocks to validate trends and identify institutional activity. **NOT FINANCIAL ADVICE** - all analysis is for educational purposes only.

## Usage

Requires tick-level or high-frequency volume data for accurate analysis.

## Core Functions

### 1. Volume Pattern Recognition
- **Volume Spikes**: Abnormal activity detection
- **Volume Trends**: Increasing/decreasing patterns
- **Volume Divergence**: Price-volume conflicts
- **Volume Clusters**: Accumulation zones

### 2. Volume Indicators
- **OBV (On-Balance Volume)**: Cumulative buying/selling
- **Volume RSI**: Momentum of volume
- **Chaikin Money Flow**: Accumulation/distribution
- **VWAP**: Volume-weighted average price

### 3. Institutional Activity
- Block trade detection
- Smart money accumulation
- Distribution patterns
- Volume footprint analysis

### 4. Volume Profile Analysis
- Point of control (POC)
- Value area (70% volume)
- High volume nodes (HVN)
- Low volume nodes (LVN)

### 5. Volume Confirmation
- Breakout validation
- Trend confirmation
- Reversal signals
- Exhaustion patterns

## Output Format

```json
{
  "thinkingCard": {
    "volumeMetrics": {
      "averageVolume": 2345678.901234,
      "currentVolume": 3456789.012345,
      "volumeRatio": 1.473456,
      "obv": 45678901.234567
    },
    "volumeProfile": {
      "pointOfControl": 105.678901,
      "valueAreaHigh": 108.234567,
      "valueAreaLow": 103.456789
    },
    "institutionalActivity": {
      "accumulation": true,
      "smartMoneyFlow": 0.678901,
      "blockTradesDetected": 3
    },
    "volumeSignals": {
      "breakoutConfirmed": true,
      "divergenceDetected": false,
      "exhaustionPattern": false
    },
    "interpretation": {
      "signal": "BULLISH",
      "confidence": 0.823456,
      "recommendation": "Volume confirms uptrend"
    },
    "disclaimer": "NOT FINANCIAL ADVICE - Educational purposes only"
  }
}
```

## Implementation Notes

- 20-day average for baseline
- Spike threshold: 2.5x average
- Block trade: >10,000 shares
- All calculations use 6+ decimal precision