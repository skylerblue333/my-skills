# Support and Resistance Analysis

Identify key price levels where buying or selling pressure historically emerges.

## Overview

This skill detects support and resistance levels using price history, volume profiles, and psychological levels for DSE stocks. **NOT FINANCIAL ADVICE** - all analysis is for educational purposes only.

## Usage

Requires comprehensive price and volume history to identify significant levels.

## Core Functions

### 1. Level Identification
- **Historical Pivots**: Previous highs/lows
- **Volume Profile**: High volume nodes
- **Psychological Levels**: Round numbers
- **Fibonacci Retracements**: Key percentage levels

### 2. Level Strength Analysis
- Touch count validation
- Volume at level
- Time spent at level
- Bounce magnitude

### 3. Dynamic Levels
- Moving average support/resistance
- Trend line boundaries
- Bollinger Band extremes
- VWAP levels

### 4. Zone Analysis
- Support/resistance zones vs lines
- Confluence areas
- Level clustering
- Zone width calculation

### 5. Breakout Detection
- Volume confirmation
- Retest validation
- False breakout identification
- Breakout targets

## Output Format

```json
{
  "thinkingCard": {
    "supportLevels": [
      {"price": 98.765432, "strength": 0.876543, "touches": 5}
    ],
    "resistanceLevels": [
      {"price": 112.345678, "strength": 0.923456, "touches": 4}
    ],
    "currentPosition": {
      "price": 105.678901,
      "nearestSupport": 98.765432,
      "nearestResistance": 112.345678
    },
    "dynamicLevels": {
      "ema50": 101.234567,
      "vwap": 104.567890,
      "upperBB": 115.678901
    },
    "breakoutAnalysis": {
      "potentialBreakout": 112.345678,
      "target": 125.678901,
      "volumeRequired": 1500000
    },
    "disclaimer": "NOT FINANCIAL ADVICE - Educational purposes only"
  }
}
```

## Implementation Notes

- Minimum 100 periods for reliable levels
- Zone tolerance: 2-3% of price
- Volume weighted calculations
- All values use 6+ decimal precision