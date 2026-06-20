# Earnings Forecast

Analyze and project earnings using historical trends and analyst estimates.

## Overview

This skill forecasts earnings for DSE stocks using trend analysis, seasonal patterns, and growth models to project future financial performance. **NOT FINANCIAL ADVICE** - all analysis is for educational purposes only.

## Usage

Requires historical earnings data, revenue trends, and industry growth rates.

## Core Functions

### 1. Historical Analysis
- Earnings trend analysis
- Growth rate calculation
- Seasonal adjustments
- Cyclical pattern detection

### 2. Forecasting Models
- Linear regression projection
- Exponential smoothing
- ARIMA modeling
- Monte Carlo simulation

### 3. Earnings Quality
- Accrual analysis
- One-time item adjustments
- Core earnings calculation
- Quality score assessment

### 4. Growth Drivers
- Revenue growth analysis
- Margin expansion/contraction
- Operating leverage
- Market share dynamics

### 5. Estimate Analysis
- Consensus tracking
- Revision trends
- Surprise history
- Whisper numbers

## Output Format

```json
{
  "thinkingCard": {
    "currentEarnings": {
      "ttmEPS": 8.765432,
      "lastQuarter": 2.234567,
      "yoyGrowth": 0.156789
    },
    "forecast": {
      "nextQuarter": 2.456789,
      "nextYear": 10.234567,
      "growthRate": 0.167890,
      "confidence": 0.756789
    },
    "earningsQuality": {
      "score": 0.823456,
      "accrualRatio": 0.045678,
      "coreEarnings": 8.345678,
      "adjustments": -0.419754
    },
    "growthDrivers": {
      "revenueGrowth": 0.123456,
      "marginExpansion": 0.023456,
      "operatingLeverage": 1.234567
    },
    "estimates": {
      "consensus": 2.345678,
      "highEstimate": 2.567890,
      "lowEstimate": 2.123456,
      "revisionTrend": "UPWARD"
    },
    "surpriseAnalysis": {
      "avgSurprise": 0.034567,
      "beatRate": 0.750000,
      "lastSurprise": 0.045678
    },
    "disclaimer": "NOT FINANCIAL ADVICE - Educational purposes only"
  }
}
```

## Implementation Notes

- Minimum 12 quarters for reliable forecast
- Adjust for seasonality and one-time items
- Weight recent quarters more heavily
- All calculations use 6+ decimal precision