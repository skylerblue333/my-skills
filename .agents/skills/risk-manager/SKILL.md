---
compatibility: Python 3.8+, standard library only. No network. No third-party packages.
description: Converts a raw DSE trade signal plus OHLCV price data into a risk-checked recommendation with concrete BDT numbers — ATR-based buy zone, stop-loss, target, risk:reward, Kelly/percent position sizing, and pass/fail risk gates (liquidity, sector concentration, portfolio heat, circuit-breaker suppression). Use when the user asks "how many shares should I buy", "where's my stop", "what's the position size", "is this trade safe", "set my risk", or needs the risk gatekeeper for a Dhaka Stock Exchange ticker.
license: Apache-2.0
metadata:
    author: stock-buddy
    github-path: skills/risk-manager
    github-pinned: main
    github-ref: refs/heads/main
    github-repo: https://github.com/kuntal-r-d/my-skills
    github-tree-sha: 16dbdae4c9187cc5a99a50cb2b1bed76de9995a9
    mode:
        - investment
        - momentum
    prd_refs:
        - PRD-002:REQ-108
        - PRD-002:REQ-097
        - PRD-001:REQ-004
        - PRD-001:REQ-005
        - PRD-001:REQ-029
        - PRD-001:REQ-053
    version: 0.1.0
name: risk-manager
---
# Risk Manager

## When to use

Activate when a signal exists and the user wants the *trade mechanics and risk gate*:
"how many shares of GP should I buy", "where do I put my stop", "what's my position size",
"is this trade within my risk", "size this for a 1% risk". This skill is the Risk Manager
gatekeeper (PRD-002 REQ-108): it turns a directional view into concrete BDT levels and
**approves, reduces, rejects, or suppresses** the trade against hard risk rules.

## What it does

From `ohlcv`, an `account`, and an optional `signal`, it computes (PRD-001 REQ-004/005/029):

1. **ATR(14)** and the working entry (`signal.entry` or last close).
2. **Buy zone** near support: `entry - 0.25×ATR` to `entry` (a range, not a point).
3. **Stop-loss** `entry - 2×ATR` and **target** `entry + 3×ATR`, with the **risk:reward**.
4. **Position size**: `risk_amount = capital × risk_per_trade_pct/100`;
   `shares = risk_amount / (entry - stop)`; capped by a **Kelly 25%** ceiling and a
   **5% per-position** cap (take the min); **halved** if ATR/price > 6% (volatility scaling).

Then it runs four **risk gates** (REQ-053), each pass/fail and explained:

- **Liquidity** — `avg_daily_value_bdt` must exceed **BDT 10,000,000 (1 crore)** or the trade
  is **rejected**.
- **Sector concentration** — existing sector exposure + this position must stay **≤ 30%** of
  portfolio value.
- **Portfolio heat** — summed per-position risk (1% proxy where unknown) + this trade's risk
  must stay **≤ 6%**.
- **Circuit/floor (REQ-097)** — at a circuit limit, on a floor price, or halted, a momentum
  recommendation is **suppressed** (price discovery interrupted).

## How to run

```bash
python3 scripts/analyze.py --input data.json --pretty
cat data.json | python3 scripts/analyze.py
```

Input shape (uses the suite data contract):

```json
{
  "ticker": "GP", "as_of": "2026-06-19", "ohlcv": [ ... ≥15 bars ... ],
  "account": {"capital_bdt": 1000000, "risk_per_trade_pct": 1.0},
  "signal": {"entry": 304.0, "mode": "momentum"},
  "microstructure": {"circuit_state": "normal", "floor_price": null, "halted": false,
                     "avg_daily_value_bdt": 25000000},
  "fundamentals": {"sector": "Telecom"},
  "portfolio": {"total_value_bdt": 5000000,
                "positions": [{"ticker": "ROBI", "sector": "Telecom", "value_bdt": 800000}]}
}
```

Reads `ohlcv` (required, ≥15 bars for ATR(14)) and `account` (required). `signal`,
`microstructure`, `fundamentals.sector`, and `portfolio` are optional.

## Interpreting output

- `rating`: `approved`, `reduced` (a gate trimmed size), `rejected` (a hard gate failed),
  or `suppressed` (circuit/floor/halt).
- `key_metrics` carry every BDT number (buy zone, stop, target, shares, position value,
  % of capital, risk:reward). `gates` shows each gate's pass/fail and why.
- `score` reflects setup confidence; `flags` carry penalties and are never silently dropped.

## Notes

ATR math lives in `scripts/indicators.py` (copied verbatim from the suite). Stop/target/Kelly
rules, the 5%/30%/6% caps, the liquidity floor, and the sizing formula are documented in
[references/RISK.md](references/RISK.md). Output is educational analysis only, never financial
advice.
