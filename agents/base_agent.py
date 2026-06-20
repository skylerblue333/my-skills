"""
Base Agent Class

Abstract base class for all specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import subprocess
import sys


class BaseAgent(ABC):
    """Abstract base class for analysis agents"""

    def __init__(self, name: str, skills: List[str]):
        """
        Initialize agent

        Args:
            name: Agent name
            skills: List of skills this agent uses
        """
        self.name = name
        self.skills = skills
        self.results = {}

    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform analysis

        Args:
            data: Input data matching skill requirements

        Returns:
            Analysis results with score and recommendations
        """
        pass

    def run_skill(self, skill_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a skill synchronously

        Args:
            skill_name: Name of the skill to run
            data: Input data for the skill

        Returns:
            Skill output
        """
        try:
            # Find the skill script
            skill_path = f"skills/{skill_name.replace('_', '-')}/scripts"

            # Determine which script to run
            script_map = {
                'momentum-screen': 'screen.py',
                'value-investment-checklist': 'checklist.py',
                'fundamental-analysis': 'analyze.py',
                'technical-analysis': 'analyze.py',
                'risk-manager': 'analyze.py',
                'signal-synthesizer': 'synthesize.py'
            }

            script = script_map.get(skill_name.replace('_', '-'), 'analyze.py')
            script_path = f"{skill_path}/{script}"

            # Run the skill
            result = subprocess.run(
                [sys.executable, script_path],
                input=json.dumps(data),
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {
                    'error': f'Skill {skill_name} failed',
                    'stderr': result.stderr
                }

            return json.loads(result.stdout)

        except Exception as e:
            return {
                'error': f'Failed to run skill {skill_name}: {str(e)}'
            }

    def aggregate_scores(self, scores: List[float], weights: Optional[List[float]] = None) -> float:
        """
        Aggregate multiple scores

        Args:
            scores: List of scores (0-1 range)
            weights: Optional weights for each score

        Returns:
            Weighted average score
        """
        if not scores:
            return 0.5

        if weights is None:
            weights = [1.0] * len(scores)

        if len(weights) != len(scores):
            raise ValueError("Weights and scores must have same length")

        total_weight = sum(weights)
        if total_weight == 0:
            return 0.5

        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        return weighted_sum / total_weight

    def generate_recommendation(self, score: float, analysis: Dict[str, Any]) -> str:
        """
        Generate recommendation based on score

        Args:
            score: Overall score (0-1)
            analysis: Detailed analysis data

        Returns:
            Recommendation text
        """
        if score >= 0.8:
            strength = "Strong"
            action = "Consider for immediate analysis"
        elif score >= 0.6:
            strength = "Moderate"
            action = "Monitor closely"
        elif score >= 0.4:
            strength = "Weak"
            action = "Wait for better conditions"
        else:
            strength = "Poor"
            action = "Avoid at current levels"

        return f"{strength} signal (score: {score:.2f}). {action}."