# Sector Comparison

Compare stocks across and within sectors to identify relative strength and opportunities.

## Overview

This skill performs comprehensive sector analysis for DSE stocks, comparing performance, valuations, and fundamentals across sectors and within peer groups. **NOT FINANCIAL ADVICE** - all analysis is for educational purposes only.

## Usage

Requires sector classification data, peer group metrics, and market-wide statistics.

## Core Functions

### 1. Sector Performance
- Sector rotation analysis
- Relative strength ranking
- Performance attribution
- Momentum scoring

### 2. Peer Group Analysis
- Company vs peer metrics
- Percentile rankings
- Competitive positioning
- Market share analysis

### 3. Valuation Comparison
- P/E relative to sector
- P/B, P/S, EV/EBITDA comparisons
- PEG ratio analysis
- Sector premium/discount

### 4. Fundamental Comparison
- ROE, ROA, ROIC rankings
- Margin comparisons
- Growth rate analysis
- Efficiency metrics

### 5. Sector Trends
- Money flow analysis
- Institutional positioning
- Analyst sentiment
- Regulatory impacts

## Output Format

```json
{
  "thinkingCard": {
    "sectorOverview": {
      "sectorName": "Banking",
      "sectorPerformance": 0.123456,
      "marketPerformance": 0.098765,
      "relativeStrength": 1.254789
    },
    "peerComparison": {
      "stockRank": 3,
      "totalPeers": 15,
      "percentile": 80,
      "topMetrics": ["ROE", "NetMargin"]
    },
    "valuationMetrics": {
      "stockPE": 12.345678,
      "sectorPE": 15.678901,
      "discount": 0.212345,
      "valuation": "UNDERVALUED"
    },
    "fundamentalRanking": {
      "roe": {"value": 0.156789, "rank": 2},
      "netMargin": {"value": 0.234567, "rank": 1},
      "debtToEquity": {"value": 0.456789, "rank": 5}
    },
    "sectorTrends": {
      "momentum": "IMPROVING",
      "moneyFlow": "POSITIVE",
      "institutionalInterest": "INCREASING"
    },
    "recommendation": {
      "position": "OVERWEIGHT",
      "confidence": 0.789012
    },
    "disclaimer": "NOT FINANCIAL ADVICE - Educational purposes only"
  }
}
```

## Implementation Notes

- Update sector classifications quarterly
- Use market-cap weighted averages
- Include at least 5 peers for comparison
- All calculations use 6+ decimal precision