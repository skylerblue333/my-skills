"""Registry mapping MCP tool names to Stock Buddy skill scripts.

The MCP server exposes one tool per skill. Each entry records the skill folder,
its entry script, a short description (reused as the MCP tool description), and
the top-level input fields the skill reads (used to build a helpful inputSchema).

Skills live in ../skills relative to the repo root. SKILLS_DIR is resolved at
import time but can be overridden with the STOCK_BUDDY_SKILLS_DIR env var so the
server works regardless of where it is installed.
"""
from __future__ import annotations

import os
from pathlib import Path

# repo_root/mcp-server/stock_buddy_mcp/registry.py -> repo_root/skills
_DEFAULT_SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"
SKILLS_DIR = Path(os.environ.get("STOCK_BUDDY_SKILLS_DIR", _DEFAULT_SKILLS_DIR))

# tool_name -> spec
SKILLS = {
    "technical_analysis": {
        "skill": "technical-analysis", "script": "analyze.py",
        "description": "Run the DSE Technical Committee over OHLCV history; returns a weighted "
                       "technical score, rating, and reasoning (RSI/MACD/ADX/Bollinger/volume).",
        "reads": ["ohlcv", "mode", "microstructure", "ticker", "as_of"],
    },
    "momentum_screen": {
        "skill": "momentum-screen", "script": "screen.py",
        "description": "Score a stock against the 25-point momentum checklist (Minervini SEPA + "
                       "Driehaus) and return a Momentum Grade A+..F.",
        "reads": ["ohlcv", "fundamentals", "market_index", "ticker", "as_of"],
    },
    "fundamental_analysis": {
        "skill": "fundamental-analysis", "script": "analyze.py",
        "description": "Balance-sheet read, valuation (DCF/Graham/PE) fair-value range, and a "
                       "fundamental score with red flags.",
        "reads": ["fundamentals", "ticker", "as_of"],
    },
    "value_investment_checklist": {
        "skill": "value-investment-checklist", "script": "checklist.py",
        "description": "Score a stock against the 30-point Buffett/Graham/Lynch value checklist "
                       "and return an Investment Grade.",
        "reads": ["fundamentals", "ticker", "as_of"],
    },
    "smart_money_flow": {
        "skill": "smart-money-flow", "script": "analyze.py",
        "description": "Accumulation/distribution from public shareholding deltas and disclosed "
                       "fund moves (public data only).",
        "reads": ["shareholding", "funds", "ticker", "as_of"],
    },
    "sentiment_news": {
        "skill": "sentiment-news", "script": "sentiment.py",
        "description": "News sentiment with rumour-vs-fundamentals separation for a DSE ticker.",
        "reads": ["news", "mode", "ticker", "as_of"],
    },
    "macro_regime": {
        "skill": "macro-regime", "script": "regime.py",
        "description": "Assess Bangladesh market regime and emit a risk-appetite multiplier.",
        "reads": ["macro", "ticker", "as_of"],
    },
    "signal_synthesizer": {
        "skill": "signal-synthesizer", "script": "synthesize.py",
        "description": "Fuse per-agent sub-scores into dual-mode (Investment/Momentum) signals "
                       "with a 1-10 DSE Composite Score and confluence/stand-aside logic.",
        "reads": ["agents", "microstructure", "ticker", "as_of"],
    },
    "risk_manager": {
        "skill": "risk-manager", "script": "analyze.py",
        "description": "Convert a signal + price data into a risk-checked recommendation: ATR buy "
                       "zone, stop, target, position size in BDT, and pass/fail risk gates.",
        "reads": ["ohlcv", "account", "signal", "microstructure", "fundamentals", "portfolio"],
    },
    "stock_screener": {
        "skill": "stock-screener", "script": "screen.py",
        "description": "Screen a universe of DSE stocks by fundamental/technical filters, a named "
                       "template, or a natural-language query.",
        "reads": ["universe", "filters", "template", "query", "mode", "limit"],
    },
    "pattern_miner": {
        "skill": "pattern-miner", "script": "mine.py",
        "description": "Discover and validate recurring price patterns for one ticker with "
                       "anti-overfitting safeguards (train/holdout, min occurrences).",
        "reads": ["ohlcv", "params", "ticker", "as_of"],
    },
    "daily_briefing": {
        "skill": "daily-briefing", "script": "brief.py",
        "description": "Produce a pre-market briefing (levels, events, risk items) in conditional, "
                       "non-imperative language.",
        "reads": ["portfolio", "watchlist", "calendar", "overnight_news", "macro_regime", "as_of"],
    },
    "ticker_dossier": {
        "skill": "ticker-dossier", "script": "dossier.py",
        "description": "Consolidate analysis Thinking Cards into one Markdown dossier (PDF-ready).",
        "reads": ["cards", "data", "ticker", "as_of"],
    },
    "financial_terms_educator": {
        "skill": "financial-terms-educator", "script": "lookup.py",
        "description": "Explain financial terms bilingually (EN/BN) with dual-strategy impact; "
                       "look up a term, annotate metrics, or list all terms.",
        "reads": ["term", "terms", "metrics", "list"],
    },
}


def script_path(tool_name: str) -> Path:
    spec = SKILLS[tool_name]
    return SKILLS_DIR / spec["skill"] / "scripts" / spec["script"]


def input_schema(tool_name: str) -> dict:
    """Permissive object schema; skills validate their own required fields and
    return a structured {"error": ...} when inputs are insufficient."""
    reads = SKILLS[tool_name]["reads"]
    return {
        "type": "object",
        "description": "Stock Buddy shared data-contract object. Fields this skill reads: "
                       + ", ".join(reads) + ". See skills/README.md for the full contract.",
        "additionalProperties": True,
    }
