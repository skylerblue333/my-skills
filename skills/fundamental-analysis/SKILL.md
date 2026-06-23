---
name: fundamental-analysis
description: Balance-sheet read, multi-method fair-value range (DCF/Graham/PE), and a fundamental score with red flags for a DSE stock. Use when the user asks for fundamental analysis, intrinsic/fair value, DCF or Graham valuation, balance-sheet health, red flags, "is this stock cheap/overvalued", P/E, ROE, or whether a Dhaka Stock Exchange ticker is a good long-term buy.
license: Apache-2.0
compatibility: Prompt-first Agent Skill. Usable with the script absent. Script is Python 3.8+ stdlib-only, no network.
metadata:
  author: stock-buddy
  version: "0.2.0"
  prd_refs: ["PRD-001:REQ-003", "PRD-001:REQ-027"]
  mode: ["investment"]
---

# Fundamental Analysis

> **Prompt-first skill.** Follow the method with your own reasoning. `scripts/analyze.py`
> is OPTIONAL — run it for exact valuation math; the analysis is valid without it.

## Role & objective
You are a value analyst. Goal: read the balance sheet for red flags, estimate a fair-value
range by three methods, and synthesise a fundamental score (−1..+1), confidence and rating.

## When to use
"Is LHB undervalued?", "what's the fair value of GP?", "fundamental view", "P/E and ROE
read", "any balance-sheet red flags?". Feed the score into `signal-synthesizer`; pair with
`value-investment-checklist` for the long-form scorecard.

## Inputs you need
Gather via `dse-data-acquisition` → **`fundamentals`** (object). Used fields: `price` (or
last `ohlcv` close), `eps_ttm`, `eps_history[]`, `earnings_growth`, `book_value_per_share`,
`debt_to_equity`, `current_ratio`, `interest_coverage`, `free_cash_flow`, `profit_margin`,
`roe`, `pe`, `sector_median_pe`. Include what you have; flag what's missing — never invent.

## Method (follow in order)

**1. Balance-sheet red flags** — raise a flag for each: `debt_to_equity` > 1.0;
`free_cash_flow` ≤ 0; latest EPS < prior EPS (declining earnings); `current_ratio` < 1.0;
`interest_coverage` < 2.0; `profit_margin` < 0.

**2. Fair value — three methods (use what inputs allow)**
- Growth g = max(0, min(`earnings_growth`, 0.15)).
- **DCF (Graham growth):** `eps_ttm × (8.5 + 2·g·100)`.
- **Graham number:** `sqrt(22.5 × eps_ttm × book_value_per_share)`.
- **PE-based:** `eps_ttm × sector_median_pe` (default 15 if unknown).
- Fair value = {low, median, high} across the available method values.

**3. Synthesise three components**
- **Valuation gap** = (fair_median − price)/price; component = clamp(gap / 0.5).
- **Earnings trend** = average % change of `eps_history`; component = clamp(avg / 0.15).
- **Quality** = −0.2 per red flag (cap −0.8); if no flags, +0.10.

## Scoring rubric
`composite = 0.35·valuation_gap + 0.30·earnings_trend + 0.35·quality` (clamp −1..+1).

Rating: gap ≥ 0.30 and 0 flags → **strong_buy**; gap ≥ 0.10 and ≤1 flag → **buy**;
gap ≤ −0.15 or ≥3 flags → **sell**; else **hold**.

**Confidence** = clamp(0.5 + 0.25·disclosure − 0.07·(#flags) − 0.1 (if growth pinned at the
0.15 cap) − 0.15 (if no price/fair value), 0.1, 0.9), where disclosure = fraction of the 9
core fields present. Flag `limited_disclosure` if disclosure < 0.6.

Assumptions to state: discount rate 15% (DSE frontier premium), terminal growth 3%, growth
capped at 15%, sector P/E default 15.

## Output (emit this Thinking Card)
```json
{ "skill": "fundamental-analysis", "ticker": "..", "mode": "investment", "as_of": "..",
  "score": 0.0, "confidence": 0.0, "rating": "..",
  "key_metrics": { "fair_value_low": 0, "fair_value_median": 0, "fair_value_high": 0,
    "valuation_gap_pct": 0, "red_flags": [], "pe": 0, "roe": 0, "de": 0 },
  "reasoning": ["..."], "flags": ["..."],
  "disclaimer": "Educational analysis only. Not financial advice." }
```

## DSE pitfalls
- Few DSE names disclose every field — score on what's present and surface `limited_disclosure`
  rather than guessing.
- A high DCF-Graham value with a pinned 15% growth is aggressive — say so and cut confidence.
- Fair value is a range, not a price target; pair with technicals before acting.

## Optional precision helper
```bash
python3 scripts/analyze.py --input data.json --pretty
```
Returns the exact fair-value methods, gap %, red-flag list, score/confidence/rating. Use it to
check your arithmetic; trust the script if they differ.

## Worked example
LHB: price 54.3, eps_ttm 4.17, bvps 17.33, roe 0.241, d/e 0, fcf>0, sector P/E 15 →
PE-based 62.6, Graham 40.3, DCF-Graham 160.5 → median ≈ 62.6, gap +15% → component +0.30;
no red flags → quality +0.10 → composite ≈ 0.44 → **buy**.

## References
Valuation formulas and assumptions: [references/VALUATION.md](references/VALUATION.md).
Output is educational analysis only, never financial advice.
