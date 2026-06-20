"""
Momentum Trading Agent

Specializes in technical momentum analysis using multiple indicators.
"""

import asyncio
from typing import Dict, Any
from .base_agent import BaseAgent


class MomentumAgent(BaseAgent):
    """Agent specialized in momentum trading strategies"""

    def __init__(self):
        super().__init__(
            name="MomentumAgent",
            skills=['momentum-screen', 'technical-analysis', 'pattern-miner']
        )

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze stock momentum

        Args:
            data: Stock data with OHLCV and indicators

        Returns:
            Momentum analysis with score and signals
        """
        results = {}
        scores = []

        # Run momentum screen
        momentum_result = self.run_skill('momentum-screen', data)
        if 'error' not in momentum_result:
            results['momentum_screen'] = momentum_result

            # Calculate momentum score from checklist
            if 'criteria' in momentum_result:
                passed = sum(1 for c in momentum_result['criteria'] if c.get('passed'))
                total = len(momentum_result['criteria'])
                momentum_score = passed / total if total > 0 else 0.5
                scores.append(momentum_score)

        # Run technical analysis
        tech_result = self.run_skill('technical-analysis', data)
        if 'error' not in tech_result:
            results['technical_analysis'] = tech_result

            # Extract technical score
            if 'score' in tech_result:
                scores.append(float(tech_result['score']))

        # Pattern detection
        pattern_result = self.run_skill('pattern-miner', data)
        if 'error' not in pattern_result:
            results['pattern_miner'] = pattern_result

            # Score based on bullish patterns
            if 'patterns' in pattern_result:
                bullish_patterns = [p for p in pattern_result['patterns']
                                  if p.get('sentiment') == 'bullish']
                pattern_score = min(len(bullish_patterns) * 0.2, 1.0)
                scores.append(pattern_score)

        # Aggregate scores
        final_score = self.aggregate_scores(scores)

        # Generate signals
        signals = self._generate_signals(results, final_score)

        # Create recommendation
        recommendation = self._generate_momentum_recommendation(final_score, signals)

        return {
            'agent': self.name,
            'score': final_score,
            'signals': signals,
            'recommendation': recommendation,
            'details': results,
            'ticker': data.get('ticker')
        }

    def _generate_signals(self, results: Dict[str, Any], score: float) -> Dict[str, Any]:
        """Generate trading signals from analysis"""
        signals = {
            'trend': 'neutral',
            'momentum': 'neutral',
            'entry': None,
            'stop_loss': None,
            'target': None
        }

        # Determine trend
        if score >= 0.7:
            signals['trend'] = 'bullish'
            signals['momentum'] = 'strong'
        elif score >= 0.5:
            signals['trend'] = 'bullish'
            signals['momentum'] = 'moderate'
        elif score >= 0.3:
            signals['trend'] = 'neutral'
            signals['momentum'] = 'weak'
        else:
            signals['trend'] = 'bearish'
            signals['momentum'] = 'negative'

        # Extract levels from technical analysis
        if 'technical_analysis' in results:
            tech = results['technical_analysis']
            if 'support' in tech:
                signals['stop_loss'] = tech['support']
            if 'resistance' in tech:
                signals['target'] = tech['resistance']

        return signals

    def _generate_momentum_recommendation(self, score: float, signals: Dict[str, Any]) -> str:
        """Generate momentum-specific recommendation"""
        trend = signals.get('trend', 'neutral')
        momentum = signals.get('momentum', 'neutral')

        if trend == 'bullish' and momentum == 'strong':
            rec = "Strong momentum detected. Consider entry on pullback to support."
        elif trend == 'bullish' and momentum == 'moderate':
            rec = "Positive momentum building. Wait for confirmation before entry."
        elif trend == 'neutral':
            rec = "Momentum is neutral. Monitor for directional breakout."
        else:
            rec = "Negative momentum. Avoid long positions."

        if signals.get('stop_loss'):
            rec += f" Stop loss: {signals['stop_loss']:.2f}"
        if signals.get('target'):
            rec += f" Target: {signals['target']:.2f}"

        return rec