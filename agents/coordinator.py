"""
Agent Coordinator

Coordinates multiple specialized agents and synthesizes their insights.
"""

import asyncio
from typing import Dict, Any, List, Optional
from .momentum_agent import MomentumAgent
from .investment_agent import InvestmentAgent
from .business_agent import BusinessAgent


class AgentCoordinator:
    """Coordinates multiple analysis agents"""

    def __init__(self):
        """Initialize coordinator with all agents"""
        self.agents = {
            'momentum': MomentumAgent(),
            'investment': InvestmentAgent(),
            'business': BusinessAgent()
        }

    async def analyze_comprehensive(
        self,
        data: Dict[str, Any],
        agents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive analysis using multiple agents

        Args:
            data: Input data for analysis
            agents: Optional list of specific agents to use

        Returns:
            Comprehensive analysis with synthesis
        """
        # Determine which agents to use
        if agents is None:
            agents = list(self.agents.keys())

        # Run agents in parallel
        tasks = []
        for agent_name in agents:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                tasks.append(agent.analyze(data))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        agent_results = {}
        scores = []
        for agent_name, result in zip(agents, results):
            if isinstance(result, Exception):
                agent_results[agent_name] = {
                    'error': str(result),
                    'agent': agent_name
                }
            else:
                agent_results[agent_name] = result
                if 'score' in result:
                    scores.append(result['score'])

        # Synthesize insights
        synthesis = self._synthesize_insights(agent_results)

        # Calculate consensus score
        consensus_score = sum(scores) / len(scores) if scores else 0.5

        # Generate final recommendation
        recommendation = self._generate_final_recommendation(
            consensus_score,
            agent_results,
            synthesis
        )

        return {
            'ticker': data.get('ticker'),
            'consensus_score': consensus_score,
            'agents': agent_results,
            'synthesis': synthesis,
            'recommendation': recommendation,
            'timestamp': data.get('as_of')
        }

    def _synthesize_insights(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize insights from multiple agents"""
        synthesis = {
            'agreement_level': 'none',
            'key_strengths': [],
            'key_concerns': [],
            'divergences': []
        }

        scores = []
        recommendations = []

        # Extract scores and recommendations
        for agent_name, result in agent_results.items():
            if 'error' not in result:
                if 'score' in result:
                    scores.append(result['score'])
                if 'recommendation' in result:
                    recommendations.append({
                        'agent': agent_name,
                        'text': result['recommendation']
                    })

        # Calculate agreement level
        if scores:
            score_variance = self._calculate_variance(scores)
            if score_variance < 0.1:
                synthesis['agreement_level'] = 'strong'
            elif score_variance < 0.2:
                synthesis['agreement_level'] = 'moderate'
            else:
                synthesis['agreement_level'] = 'weak'

        # Extract key insights
        self._extract_key_insights(agent_results, synthesis)

        return synthesis

    def _extract_key_insights(
        self,
        agent_results: Dict[str, Any],
        synthesis: Dict[str, Any]
    ) -> None:
        """Extract key insights from agent results"""
        # From momentum agent
        if 'momentum' in agent_results and 'error' not in agent_results['momentum']:
            momentum = agent_results['momentum']
            if momentum.get('score', 0) > 0.7:
                synthesis['key_strengths'].append('Strong technical momentum')
            elif momentum.get('score', 0) < 0.3:
                synthesis['key_concerns'].append('Weak technical momentum')

            signals = momentum.get('signals', {})
            if signals.get('trend') == 'bullish':
                synthesis['key_strengths'].append('Bullish trend confirmed')

        # From investment agent
        if 'investment' in agent_results and 'error' not in agent_results['investment']:
            investment = agent_results['investment']
            if investment.get('grade') in ['A+', 'A', 'B+']:
                synthesis['key_strengths'].append(f"Investment grade: {investment['grade']}")
            elif investment.get('grade') in ['D', 'F']:
                synthesis['key_concerns'].append(f"Poor investment grade: {investment['grade']}")

            metrics = investment.get('metrics', {})
            if metrics.get('moat'):
                synthesis['key_strengths'].append('Economic moat present')

        # From business agent
        if 'business' in agent_results and 'error' not in agent_results['business']:
            business = agent_results['business']
            position = business.get('competitive_position', {})

            if position.get('industry_position') == 'leader':
                synthesis['key_strengths'].append('Industry leader')

            advantages = position.get('competitive_advantages', [])
            if advantages:
                synthesis['key_strengths'].extend(advantages[:2])

            model = business.get('business_model', {})
            if model.get('growth_sustainability') == 'at risk':
                synthesis['key_concerns'].append('Growth sustainability at risk')

        # Identify divergences
        if 'momentum' in agent_results and 'investment' in agent_results:
            mom_score = agent_results['momentum'].get('score', 0.5)
            inv_score = agent_results['investment'].get('score', 0.5)

            if abs(mom_score - inv_score) > 0.3:
                if mom_score > inv_score:
                    synthesis['divergences'].append('Technical signals stronger than fundamentals')
                else:
                    synthesis['divergences'].append('Fundamentals stronger than technicals')

    def _generate_final_recommendation(
        self,
        consensus_score: float,
        agent_results: Dict[str, Any],
        synthesis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final coordinated recommendation"""
        # Determine overall stance
        if consensus_score >= 0.7:
            stance = 'bullish'
            action = 'Consider for investment'
        elif consensus_score >= 0.5:
            stance = 'neutral-positive'
            action = 'Monitor for entry opportunity'
        elif consensus_score >= 0.3:
            stance = 'neutral-negative'
            action = 'Wait for improvement'
        else:
            stance = 'bearish'
            action = 'Avoid'

        # Build narrative
        narrative = f"{action}. "

        if synthesis['agreement_level'] == 'strong':
            narrative += "All agents agree on the assessment. "
        elif synthesis['agreement_level'] == 'weak':
            narrative += "Mixed signals from different perspectives. "

        if synthesis['key_strengths']:
            narrative += f"Strengths: {', '.join(synthesis['key_strengths'][:2])}. "

        if synthesis['key_concerns']:
            narrative += f"Concerns: {', '.join(synthesis['key_concerns'][:2])}. "

        if synthesis['divergences']:
            narrative += f"Note: {synthesis['divergences'][0]}. "

        return {
            'stance': stance,
            'action': action,
            'narrative': narrative,
            'confidence': self._calculate_confidence(synthesis['agreement_level'])
        }

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

    def _calculate_confidence(self, agreement_level: str) -> str:
        """Calculate confidence based on agreement"""
        confidence_map = {
            'strong': 'high',
            'moderate': 'medium',
            'weak': 'low',
            'none': 'very low'
        }
        return confidence_map.get(agreement_level, 'medium')