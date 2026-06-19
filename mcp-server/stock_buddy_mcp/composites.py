"""Composite tools that orchestrate the skill pipeline server-side (TAD ADR-007).

analyze_ticker: leaf skills -> signal-synthesizer -> risk-manager, in one call.
screen_market:  thin wrapper over stock-screener.

Each composite degrades gracefully: if a leaf errors, it records the failing
stage in `stages` and continues, rather than dropping the result silently.
"""
from __future__ import annotations

from typing import Any, Dict

from .dispatch import run_skill, SkillError

# leaf tool -> agent key consumed by signal_synthesizer
_LEAVES = {
    "technical_analysis": "technical",
    "fundamental_analysis": "fundamental",
    "smart_money_flow": "smart_money",
    "sentiment_news": "sentiment",
    "macro_regime": "macro",
}


def _score_conf(card: Dict[str, Any]) -> Dict[str, float]:
    return {
        "score": float(card.get("score", 0.0) or 0.0),
        "confidence": float(card.get("confidence", 0.5) or 0.5),
    }


def analyze_ticker(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run the full pipeline for one ticker.

    `payload` is the shared data-contract object (ohlcv, fundamentals,
    shareholding, news, macro, microstructure, account, ...).
    """
    ticker = payload.get("ticker")
    stages: Dict[str, str] = {}
    agents: Dict[str, Dict[str, float]] = {}
    cards: Dict[str, Any] = {}

    for tool, agent_key in _LEAVES.items():
        try:
            card = run_skill(tool, payload)
            if "error" in card:
                stages[tool] = f"skipped: {card['error']}"
                continue
            cards[agent_key] = card
            agents[agent_key] = _score_conf(card)
            stages[tool] = "ok"
        except SkillError as e:
            stages[tool] = f"error: {e}"

    if not agents:
        return {"skill": "analyze_ticker", "ticker": ticker,
                "error": "no leaf analyses succeeded", "stages": stages}

    # Synthesize dual-mode signal.
    syn_payload = {"ticker": ticker, "as_of": payload.get("as_of"),
                   "agents": agents, "microstructure": payload.get("microstructure")}
    try:
        synthesis = run_skill("signal_synthesizer", syn_payload)
        stages["signal_synthesizer"] = "ok" if "error" not in synthesis else f"error: {synthesis['error']}"
    except SkillError as e:
        synthesis = {"error": str(e)}
        stages["signal_synthesizer"] = f"error: {e}"

    # Risk-check (uses ohlcv + account from the original payload).
    try:
        risk = run_skill("risk_manager", payload)
        stages["risk_manager"] = "ok" if "error" not in risk else f"error: {risk['error']}"
    except SkillError as e:
        risk = {"error": str(e)}
        stages["risk_manager"] = f"error: {e}"

    return {
        "skill": "analyze_ticker",
        "ticker": ticker,
        "as_of": payload.get("as_of"),
        "synthesis": synthesis,
        "risk": risk,
        "agent_cards": cards,
        "stages": stages,
        "disclaimer": "Educational analysis only. Not financial advice.",
    }


def screen_market(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Thin wrapper over stock-screener (kept as a composite for a stable name)."""
    return run_skill("stock_screener", payload)


COMPOSITES = {
    "analyze_ticker": {
        "fn": analyze_ticker,
        "description": "End-to-end: run technical, fundamental, smart-money, sentiment and macro "
                       "analyses, fuse them via signal-synthesizer (dual-mode 1-10 composite), and "
                       "risk-check via risk-manager. One call, full pipeline, for a DSE ticker.",
        "reads": ["ticker", "ohlcv", "fundamentals", "shareholding", "news", "macro",
                  "microstructure", "account", "market_index", "as_of"],
    },
    "screen_market": {
        "fn": screen_market,
        "description": "Scan a universe of DSE stocks for Investment or Momentum candidates via "
                       "filters, a named template, or a natural-language query.",
        "reads": ["universe", "filters", "template", "query", "mode", "limit"],
    },
}
