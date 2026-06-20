# Price Action Analysis

Pure price movement analysis without indicators, focusing on candlestick patterns and market structure.

## Overview

This skill analyzes raw price action, candlestick patterns, and market structure for DSE stocks to identify high-probability trading setups. **NOT FINANCIAL ADVICE** - all analysis is for educational purposes only.

## Usage

Requires detailed OHLC data with sufficient history for pattern recognition.

## Core Functions

### 1. Candlestick Patterns
- **Reversal Patterns**: Hammer, shooting star, engulfing
- **Continuation Patterns**: Three white soldiers, three black crows
- **Indecision Patterns**: Doji, spinning top, harami
- **Complex Patterns**: Morning/evening star, three inside

### 2. Market Structure
- Swing highs and lows
- Market phases (trending/ranging)
- Support/resistance from structure
- Price action zones

### 3. Bar Analysis
- Inside bars and outside bars
- Pin bars and rejection candles
- Momentum bars
- Exhaustion bars

### 4. Pattern Context
- Location relative to support/resistance
- Trend context validation
- Volume confirmation
- Multiple timeframe alignment

### 5. Entry/Exit Signals
- Pattern completion points
- Stop loss placement
- Risk/reward ratios
- Trade management levels

## Output Format

```json
{
  "thinkingCard": {
    "candlestickPatterns": [
      {
        "pattern": "Bullish Engulfing",
        "timestamp": "2024-01-15",
        "reliability": 0.789012,
        "location": "support"
      }
    ],
    "marketStructure": {
      "phase": "UPTREND",
      "lastSwingHigh": 112.345678,
      "lastSwingLow": 98.765432,
      "structureIntact": true
    },
    "priceActionSignals": {
      "pinBarDetected": true,
      "insideBarBreakout": false,
      "momentumShift": true
    },
    "tradingSetup": {
      "signal": "BUY",
      "entry": 105.678901,
      "stopLoss": 102.345678,
      "target": 115.234567,
      "riskReward": 3.456789
    },
    "confidence": 0.823456,
    "disclaimer": "NOT FINANCIAL ADVICE - Educational purposes only"
  }
}
```

## Implementation Notes

- Pattern validation requires 3+ candles
- Context weighs 60% of signal strength
- False signal filtering via multi-timeframe
- All prices use 6+ decimal precision