"""
Business Analysis Agent

Specializes in company business model and competitive position analysis.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class BusinessAgent(BaseAgent):
    """Agent specialized in business model analysis"""

    def __init__(self):
        super().__init__(
            name="BusinessAgent",
            skills=['fundamental-analysis', 'risk-manager']
        )

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze business model and competitive position

        Args:
            data: Company data with fundamentals and market info

        Returns:
            Business analysis with viability assessment
        """
        results = {}
        scores = []

        # Run fundamental analysis for business metrics
        fundamental_result = self.run_skill('fundamental-analysis', data)
        if 'error' not in fundamental_result:
            results['fundamentals'] = fundamental_result
            if 'score' in fundamental_result:
                scores.append(float(fundamental_result['score']))

        # Run risk analysis
        risk_result = self.run_skill('risk-manager', data)
        if 'error' not in risk_result:
            results['risk_assessment'] = risk_result
            # Invert risk score (low risk = high score)
            if 'risk_level' in risk_result:
                risk_map = {'low': 0.8, 'medium': 0.5, 'high': 0.2, 'extreme': 0.0}
                risk_score = risk_map.get(risk_result['risk_level'], 0.5)
                scores.append(risk_score)

        # Aggregate scores
        final_score = self.aggregate_scores(scores)

        # Analyze business model
        business_analysis = self._analyze_business_model(data, results)

        # Assess competitive position
        competitive_position = self._assess_competitive_position(data, results)

        # Generate business outlook
        outlook = self._generate_business_outlook(final_score, business_analysis, competitive_position)

        return {
            'agent': self.name,
            'score': final_score,
            'business_model': business_analysis,
            'competitive_position': competitive_position,
            'outlook': outlook,
            'details': results,
            'ticker': data.get('ticker')
        }

    def _analyze_business_model(self, data: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the business model"""
        analysis = {
            'revenue_stability': 'unknown',
            'margin_trend': 'unknown',
            'capital_efficiency': 'unknown',
            'growth_sustainability': 'unknown'
        }

        fundamentals = data.get('fundamentals', {})

        # Revenue stability
        revenue_growth = fundamentals.get('revenue_growth', 0)
        if revenue_growth > 0.15:
            analysis['revenue_stability'] = 'strong growth'
        elif revenue_growth > 0.05:
            analysis['revenue_stability'] = 'steady growth'
        elif revenue_growth > -0.05:
            analysis['revenue_stability'] = 'stable'
        else:
            analysis['revenue_stability'] = 'declining'

        # Margin trend
        profit_margin = fundamentals.get('profit_margin', 0)
        if profit_margin > 0.20:
            analysis['margin_trend'] = 'excellent'
        elif profit_margin > 0.10:
            analysis['margin_trend'] = 'healthy'
        elif profit_margin > 0.05:
            analysis['margin_trend'] = 'thin'
        else:
            analysis['margin_trend'] = 'poor'

        # Capital efficiency
        roe = fundamentals.get('roe', 0)
        asset_turnover = fundamentals.get('asset_turnover', 0)
        if roe > 0.20 and asset_turnover > 1.0:
            analysis['capital_efficiency'] = 'highly efficient'
        elif roe > 0.15:
            analysis['capital_efficiency'] = 'efficient'
        elif roe > 0.10:
            analysis['capital_efficiency'] = 'moderate'
        else:
            analysis['capital_efficiency'] = 'inefficient'

        # Growth sustainability
        debt_to_equity = fundamentals.get('debt_to_equity', 0)
        fcf = fundamentals.get('free_cash_flow', 0)
        if fcf > 0 and debt_to_equity < 0.5:
            analysis['growth_sustainability'] = 'highly sustainable'
        elif fcf > 0:
            analysis['growth_sustainability'] = 'sustainable'
        elif debt_to_equity < 1.0:
            analysis['growth_sustainability'] = 'moderate'
        else:
            analysis['growth_sustainability'] = 'at risk'

        return analysis

    def _assess_competitive_position(self, data: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess competitive position"""
        position = {
            'market_share': 'unknown',
            'moat_strength': 'none',
            'industry_position': 'follower',
            'competitive_advantages': []
        }

        fundamentals = data.get('fundamentals', {})

        # Moat strength
        moat = fundamentals.get('moat')
        if moat:
            position['moat_strength'] = 'strong'
            position['competitive_advantages'].append('Economic moat')

        # Industry position based on margins and ROE
        profit_margin = fundamentals.get('profit_margin', 0)
        roe = fundamentals.get('roe', 0)

        if profit_margin > 0.20 and roe > 0.20:
            position['industry_position'] = 'leader'
            position['competitive_advantages'].append('Superior profitability')
        elif profit_margin > 0.15 or roe > 0.15:
            position['industry_position'] = 'strong player'
        else:
            position['industry_position'] = 'follower'

        # Additional competitive advantages
        if fundamentals.get('revenue_growth', 0) > 0.20:
            position['competitive_advantages'].append('High growth')

        if fundamentals.get('debt_to_equity', 1.0) < 0.3:
            position['competitive_advantages'].append('Strong balance sheet')

        return position

    def _generate_business_outlook(
        self,
        score: float,
        business_analysis: Dict[str, Any],
        competitive_position: Dict[str, Any]
    ) -> str:
        """Generate business outlook"""
        if score >= 0.7:
            outlook = "Strong business with favorable long-term prospects."
        elif score >= 0.5:
            outlook = "Solid business with moderate growth potential."
        elif score >= 0.3:
            outlook = "Challenged business facing headwinds."
        else:
            outlook = "Weak business model with significant risks."

        # Add specific insights
        if business_analysis['revenue_stability'] == 'strong growth':
            outlook += " Revenue growing rapidly."

        if business_analysis['capital_efficiency'] == 'highly efficient':
            outlook += " Excellent capital allocation."

        if competitive_position['industry_position'] == 'leader':
            outlook += " Market leadership position."

        if len(competitive_position['competitive_advantages']) > 2:
            outlook += f" Multiple competitive advantages: {', '.join(competitive_position['competitive_advantages'][:2])}."

        return outlook