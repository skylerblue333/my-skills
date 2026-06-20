"""
Investment Analysis Agent

Specializes in fundamental value investment analysis.
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class InvestmentAgent(BaseAgent):
    """Agent specialized in value investment strategies"""

    def __init__(self):
        super().__init__(
            name="InvestmentAgent",
            skills=['value-investment-checklist', 'fundamental-analysis']
        )

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze investment value

        Args:
            data: Stock data with fundamentals

        Returns:
            Investment analysis with grade and criteria
        """
        results = {}
        scores = []

        # Run value investment checklist
        value_result = self.run_skill('value-investment-checklist', data)
        if 'error' not in value_result:
            results['value_checklist'] = value_result

            # Extract investment grade
            if 'gpa' in value_result:
                # Convert 4.0 GPA to 0-1 score
                scores.append(value_result['gpa'] / 4.0)

        # Run fundamental analysis
        fundamental_result = self.run_skill('fundamental-analysis', data)
        if 'error' not in fundamental_result:
            results['fundamental_analysis'] = fundamental_result

            # Extract fundamental score
            if 'score' in fundamental_result:
                scores.append(float(fundamental_result['score']))

        # Aggregate scores
        final_score = self.aggregate_scores(scores, weights=[0.6, 0.4])

        # Extract key metrics
        metrics = self._extract_key_metrics(results)

        # Generate investment thesis
        thesis = self._generate_investment_thesis(final_score, metrics)

        return {
            'agent': self.name,
            'score': final_score,
            'grade': self._score_to_grade(final_score),
            'metrics': metrics,
            'thesis': thesis,
            'details': results,
            'ticker': data.get('ticker')
        }

    def _extract_key_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key investment metrics"""
        metrics = {
            'pe_ratio': None,
            'roe': None,
            'debt_to_equity': None,
            'profit_margin': None,
            'moat': None,
            'intrinsic_value': None
        }

        # From value checklist
        if 'value_checklist' in results:
            checklist = results['value_checklist']
            if 'criteria' in checklist:
                for criterion in checklist['criteria']:
                    if 'ROE' in criterion.get('label', ''):
                        metrics['roe'] = criterion.get('value')
                    elif 'Debt/Equity' in criterion.get('label', ''):
                        metrics['debt_to_equity'] = criterion.get('value')
                    elif 'moat' in criterion.get('label', '').lower():
                        metrics['moat'] = criterion.get('value')

        # From fundamental analysis
        if 'fundamental_analysis' in results:
            fundamental = results['fundamental_analysis']
            if 'metrics' in fundamental:
                metrics.update(fundamental['metrics'])

        return metrics

    def _generate_investment_thesis(self, score: float, metrics: Dict[str, Any]) -> str:
        """Generate investment thesis"""
        if score >= 0.8:
            thesis = "Exceptional investment opportunity with strong fundamentals."
        elif score >= 0.6:
            thesis = "Good investment candidate with solid value characteristics."
        elif score >= 0.4:
            thesis = "Fair investment with mixed signals. Further research needed."
        else:
            thesis = "Weak investment case. Significant concerns present."

        # Add specific insights
        if metrics.get('moat'):
            thesis += " Economic moat provides competitive advantage."

        if metrics.get('roe') and metrics['roe'] > 0.15:
            thesis += f" High ROE of {metrics['roe']*100:.1f}% indicates efficient capital use."

        if metrics.get('debt_to_equity') and metrics['debt_to_equity'] < 0.5:
            thesis += " Low debt provides financial stability."

        return thesis

    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B+'
        elif score >= 0.6:
            return 'B'
        elif score >= 0.5:
            return 'C'
        elif score >= 0.4:
            return 'D'
        else:
            return 'F'