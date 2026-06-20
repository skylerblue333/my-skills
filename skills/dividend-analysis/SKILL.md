# Dividend Analysis

Comprehensive dividend assessment for income-focused investors in DSE stocks.

## Overview

This skill analyzes dividend history, sustainability, and growth prospects for DSE stocks, calculating yield, payout ratios, and dividend growth rates. **NOT FINANCIAL ADVICE** - all analysis is for educational purposes only.

## Usage

Requires historical dividend data, earnings reports, and cash flow statements.

## Core Functions

### 1. Dividend Metrics
- **Current Yield**: Annual dividend / Current price
- **Forward Yield**: Expected dividend / Current price
- **Yield on Cost**: Dividend / Original purchase price
- **5-Year Average Yield**: Historical perspective

### 2. Sustainability Analysis
- Payout ratio (Dividends / Earnings)
- Free cash flow coverage
- Debt-to-equity impact
- Earnings stability score

### 3. Growth Analysis
- Dividend growth rate (1, 3, 5, 10 year)
- Dividend growth consistency
- Earnings growth correlation
- Future growth potential

### 4. Income Calculations
- Total return (price + dividends)
- Dividend reinvestment impact
- Tax-adjusted returns
- Income stream projections

### 5. Peer Comparison
- Sector yield comparison
- Dividend aristocrat criteria
- Relative dividend strength
- Industry benchmarking

## Output Format

```json
{
  "thinkingCard": {
    "currentMetrics": {
      "dividendYield": 0.045678,
      "annualDividend": 5.678901,
      "payoutRatio": 0.456789,
      "exDividendDate": "2024-03-15"
    },
    "sustainability": {
      "score": 0.823456,
      "fcfCoverage": 1.234567,
      "earningsStability": 0.890123,
      "debtImpact": "LOW"
    },
    "growthAnalysis": {
      "cagr5Year": 0.087654,
      "growthConsistency": 0.923456,
      "streakYears": 7,
      "projectedGrowth": 0.076543
    },
    "incomeProjection": {
      "year1Income": 567.890123,
      "year5Income": 789.012345,
      "totalReturn": 0.156789
    },
    "peerComparison": {
      "sectorAverage": 0.034567,
      "percentile": 75,
      "ranking": "TOP_QUARTILE"
    },
    "disclaimer": "NOT FINANCIAL ADVICE - Educational purposes only"
  }
}
```

## Implementation Notes

- Minimum 5 years history for trends
- Quarterly dividend tracking
- Special dividend handling
- All calculations use 6+ decimal precision