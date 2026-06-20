# Portfolio Optimization

Optimize portfolio allocation using Modern Portfolio Theory and risk-adjusted metrics.

## Overview

This skill analyzes a portfolio of DSE stocks to optimize allocation based on risk-return trade-offs, implementing Markowitz efficient frontier, Sharpe ratio optimization, and Kelly Criterion for position sizing. **NOT FINANCIAL ADVICE** - all recommendations are for educational purposes only.

## Usage

The skill expects client-provided portfolio data including:
- Current holdings with quantities and prices
- Historical price data for correlation analysis
- Risk-free rate for Sharpe ratio calculations
- Investment constraints (min/max allocations)

## Core Functions

### 1. Efficient Frontier Analysis
- Calculate expected returns and covariance matrix
- Generate efficient frontier curve
- Identify optimal portfolios for different risk levels

### 2. Risk-Adjusted Metrics
- **Sharpe Ratio**: (Return - Risk-free rate) / Standard deviation
- **Sortino Ratio**: Focus on downside deviation
- **Calmar Ratio**: Return / Maximum drawdown
- **Information Ratio**: Active return / Tracking error

### 3. Optimization Strategies
- **Maximum Sharpe Ratio**: Best risk-adjusted returns
- **Minimum Variance**: Lowest portfolio volatility
- **Risk Parity**: Equal risk contribution
- **Kelly Criterion**: Optimal position sizing

### 4. Correlation Analysis
- Asset correlation matrix
- Diversification ratio
- Principal component analysis
- Cluster identification

### 5. Rebalancing Recommendations
- Target vs current allocation gaps
- Transaction cost optimization
- Tax-aware rebalancing
- Periodic vs threshold rebalancing

## Output Format

```json
{
  "thinkingCard": {
    "portfolioStats": {
      "expectedReturn": 0.156789,
      "annualizedVolatility": 0.234567,
      "sharpeRatio": 0.567890,
      "maxDrawdown": -0.123456,
      "diversificationRatio": 1.456789
    },
    "optimalAllocation": {
      "SYMBOL1": 0.234567,
      "SYMBOL2": 0.345678,
      "SYMBOL3": 0.419755
    },
    "efficientFrontier": [
      {"risk": 0.123456, "return": 0.098765},
      {"risk": 0.234567, "return": 0.156789}
    ],
    "rebalancingActions": [
      {"symbol": "SYMBOL1", "action": "BUY", "quantity": 100, "targetWeight": 0.234567}
    ],
    "riskAnalysis": {
      "valueAtRisk95": -0.045678,
      "conditionalVaR95": -0.067890,
      "betaToMarket": 0.987654
    },
    "disclaimer": "NOT FINANCIAL ADVICE - Educational purposes only"
  }
}
```

## Implementation Notes

- All calculations use 6+ decimal precision
- Historical data minimum: 252 trading days
- Correlation window: 60-day rolling
- Rebalancing frequency: Quarterly recommended
- Transaction costs: Include in optimization
- Tax considerations: Track holding periods

## Dependencies

Requires client to provide:
- Portfolio holdings data
- Historical price series
- Risk-free rate
- Investment constraints
- Transaction cost model