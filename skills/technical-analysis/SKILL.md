---
name: technical-analysis
description: Runs a DSE Technical Analysis Committee over a stock's OHLCV history and returns a weighted technical score, rating, and reasoning. Use when the user asks for technical analysis, momentum/trend read, chart signal, RSI/MACD/ADX/Bollinger/volume analysis, or "is this stock technically bullish/bearish" for a Dhaka Stock Exchange ticker.
license: Apache-2.0
compatibility: Prompt-first Agent Skill. Usable with the script absent. Script is Python 3.8+ stdlib-only, no network.
metadata:
  author: stock-buddy
  version: "0.2.0"
  prd_refs: ["PRD-001:REQ-001", "PRD-001:REQ-027"]
  mode: ["momentum", "investment"]
---

# Technical Analysis

> **Prompt-first skill.** Follow the method below with your own reasoning to produce
> the Thinking Card. `scripts/analyze.py` is OPTIONAL — run it for exact indicator
> math, but the analysis is valid without it. The script implements exactly this method.

## Role & objective
You are the **Chair of a six-member DSE Technical Committee**. Goal: turn a daily price
history into one weighted technical score (−1..+1), a rating, and clear reasoning.

## When to use
"Analyze the chart for GP", "is BEXIMCO technically bullish?", "what do RSI and MACD
say?", "run technical analysis", "momentum/trend read". Pair with `momentum-screen` for
trade setups, or feed the score into `signal-synthesizer`.

## Inputs you need
Gather via the `dse-data-acquisition` skill:
- **`ohlcv`** — daily bars, oldest-first. **Need ≥30** bars; **≥200** for the full
  moving-average stack (else flag `limited_history_<200_bars`).
- *(optional)* **`microstructure`** — `circuit_state` (`limit_up`/`limit_down`), `floor_price`.

If fewer than 30 bars are available, stop and say so — do not analyse a stub series.

## Method — score each member in −1..+1, then weight

**1. Trend (weight 0.25)**
- Price **above** 200-day SMA → +0.3; below → −0.3.
- MA stack **50 > 150 > 200** → +0.3.
- **ADX(14) ≥ 25** → +0.4 if +DI ≥ −DI, else −0.4. ADX < 25 → weak/no trend (0).

**2. Momentum & oscillators (weight 0.22)**
- **RSI(14)** 40–70 → +0.25; >70 → −0.15; <40 → −0.2.
- **MACD** line above signal → +0.25; below → −0.2.
- **ROC(12)** > 0 → +0.2; ≤ 0 → −0.2.
- **MFI(14)** within 20–80 → +0.1.

**3. Volume & flow (weight 0.20)**
- **OBV** slope rising (last ~10 bars) → +0.3; falling → −0.2.
- **Relative volume** vs 20-day avg ≥ 1.5× → +0.3; < 0.7× → −0.1.

**4. Levels (weight 0.13)**
- Distance to 60-bar **support** < 8% above → +0.3.
- Within 3% of 60-bar **resistance** → −0.2.

**5. Chart pattern (weight 0.12)**
- Price ≥ 40-bar high → +0.5 (breakout); range ratio < 0.12 → +0.1 (tight coil);
  price ≤ 40-bar low → −0.5.

**6. Candlestick — latest bar (weight 0.08)**
- Hammer (lower wick > 2× body, up bar) → +0.4; shooting star → −0.4; bullish engulfing → +0.3.

Clamp every member to [−1, +1].

## Scoring rubric
`composite = 0.25·trend + 0.22·momentum + 0.20·volume + 0.13·levels + 0.12·pattern + 0.08·candlestick`

Rating: **≥0.5** strong_bullish · **≥0.15** bullish · **−0.15..0.15** neutral ·
**≤−0.15** bearish · **≤−0.5** strong_bearish.

**Chair (agreement vs conflict):** members >0.15 are "bulls", <−0.15 "bears". Both present →
conflict_penalty 0.2 (stand-aside, not a weak buy); none decisive → 0.1; one-sided → 0.

**Confidence** = clamp(0.55 + 0.4·|composite| − conflict_penalty − (0.15 if <200 bars), 0.1, 0.95).

## Output (emit this Thinking Card)
```json
{ "skill": "technical-analysis", "ticker": "..", "mode": "momentum", "as_of": "..",
  "score": 0.0, "confidence": 0.0, "rating": "..",
  "sub_scores": { "trend": 0.0, "momentum_oscillator": 0.0, "chart_pattern": 0.0,
                  "candlestick": 0.0, "levels": 0.0, "volume_flow": 0.0 },
  "chair_note": "..", "key_metrics": { "rsi_14": 0, "adx_14": 0, "macd_hist": 0 },
  "reasoning": ["..."], "flags": ["..."],
  "disclaimer": "Educational analysis only. Not financial advice." }
```

## DSE pitfalls
- **Circuit / floor price:** if `microstructure.circuit_state` is limit_up/limit_down or
  `floor_price` is set, add flag `microstructure_circuit_or_floor` and treat momentum as unreliable.
- **<200 bars:** flag `limited_history_<200_bars` and cut confidence (−0.15).
- **Thin liquidity:** low relative volume weakens any breakout — don't over-weight it.

## Optional precision helper
```bash
python3 scripts/analyze.py --input data.json --pretty
python3 scripts/analyze.py --input ../_fixtures/sample_input.json --pretty
```
Returns the same Thinking Card with exact `sub_scores` and `key_metrics`. Use it to verify
your hand computation; if they disagree, trust the script's math and explain the gap.

## Worked example
250 bars, price above a rising 50>150>200 stack, ADX 27 (+DI leading), RSI 58, MACD line >
signal, OBV rising, volume 1.6× the 20-day average → trend ≈ +1.0, momentum ≈ +0.7,
volume ≈ +0.6 → composite ≈ +0.55 → **strong_bullish**, confidence ≈ 0.77.

## References
Formulas and DSE caveats: [references/INDICATORS.md](references/INDICATORS.md).
Output is educational analysis only, never financial advice.
