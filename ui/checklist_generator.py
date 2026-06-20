"""
Interactive Checklist Generator

Generates HTML checklists with explanations for momentum and investment criteria.
"""

from typing import Dict, Any, List
import json
from datetime import datetime


class ChecklistGenerator:
    """Generate interactive HTML checklists"""

    @staticmethod
    def generate_momentum_checklist(data: Dict[str, Any]) -> str:
        """
        Generate 25-point momentum checklist HTML

        Args:
            data: Momentum screen results with criteria

        Returns:
            HTML string with interactive checklist
        """
        criteria = data.get('criteria', [])
        score = data.get('score', 0)
        ticker = data.get('ticker', 'Unknown')

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Momentum Checklist - {ticker}</title>
    <style>
        {ChecklistGenerator._get_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Momentum Trading Checklist</h1>
            <div class="ticker-info">
                <span class="ticker">{ticker}</span>
                <span class="score">Score: {score*100:.1f}%</span>
            </div>
        </header>

        <div class="checklist">
            {ChecklistGenerator._generate_criteria_items(criteria)}
        </div>

        <footer>
            <p class="disclaimer">Educational analysis only. Not financial advice.</p>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </footer>
    </div>

    <script>
        {ChecklistGenerator._get_javascript()}
    </script>
</body>
</html>
"""
        return html

    @staticmethod
    def generate_investment_checklist(data: Dict[str, Any]) -> str:
        """
        Generate 30-point investment checklist HTML

        Args:
            data: Value investment checklist results

        Returns:
            HTML string with interactive checklist
        """
        criteria = data.get('criteria', [])
        grade = data.get('grade', 'N/A')
        gpa = data.get('gpa', 0)
        ticker = data.get('ticker', 'Unknown')

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investment Checklist - {ticker}</title>
    <style>
        {ChecklistGenerator._get_css()}
        .grade-display {{
            font-size: 48px;
            font-weight: bold;
            color: {ChecklistGenerator._grade_color(grade)};
            text-align: center;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💰 Value Investment Checklist</h1>
            <div class="ticker-info">
                <span class="ticker">{ticker}</span>
                <div class="grade-display">{grade}</div>
                <span class="gpa">GPA: {gpa:.2f}/4.0</span>
            </div>
        </header>

        <div class="checklist">
            {ChecklistGenerator._generate_investment_criteria(criteria)}
        </div>

        <footer>
            <p class="disclaimer">Educational analysis only. Not financial advice.</p>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </footer>
    </div>

    <script>
        {ChecklistGenerator._get_javascript()}
    </script>
</body>
</html>
"""
        return html

    @staticmethod
    def _generate_criteria_items(criteria: List[Dict]) -> str:
        """Generate HTML for criteria items"""
        html = ""
        current_category = None

        for item in criteria:
            # Add category header if changed
            category = item.get('bucket', item.get('category', 'Other'))
            if category != current_category:
                if current_category is not None:
                    html += "</div>"
                html += f'<div class="category"><h2>{category.title()}</h2>'
                current_category = category

            # Add criterion item
            passed = item.get('passed')
            icon = "✅" if passed else "❌" if passed is False else "❓"
            css_class = "passed" if passed else "failed" if passed is False else "unknown"

            value = item.get('value', 'N/A')
            if isinstance(value, float):
                value = f"{value:.2f}"
            elif isinstance(value, dict):
                value = json.dumps(value, indent=2)

            html += f"""
            <div class="criterion {css_class}" onclick="toggleExplanation(this)">
                <div class="criterion-header">
                    <span class="icon">{icon}</span>
                    <span class="label">{item.get('label', 'Unknown')}</span>
                    <span class="value">{value}</span>
                </div>
                <div class="explanation" style="display:none;">
                    <p>{item.get('explanation', 'No explanation available.')}</p>
                </div>
            </div>
            """

        if current_category is not None:
            html += "</div>"

        return html

    @staticmethod
    def _generate_investment_criteria(criteria: List[Dict]) -> str:
        """Generate HTML for investment criteria grouped by methodology"""
        html = ""
        categories = {}

        # Group criteria by category
        for item in criteria:
            category = item.get('bucket', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)

        # Generate HTML for each category
        for category, items in categories.items():
            passed = sum(1 for i in items if i.get('passed'))
            total = len(items)

            html += f"""
            <div class="category">
                <h2>{category.title()} ({passed}/{total})</h2>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(passed/total*100) if total else 0}%"></div>
                </div>
            """

            for item in items:
                passed = item.get('passed')
                icon = "✅" if passed else "❌" if passed is False else "❓"
                css_class = "passed" if passed else "failed" if passed is False else "unknown"

                html += f"""
                <div class="criterion {css_class}" onclick="toggleExplanation(this)">
                    <div class="criterion-header">
                        <span class="icon">{icon}</span>
                        <span class="label">{item.get('label', 'Unknown')}</span>
                    </div>
                    <div class="explanation" style="display:none;">
                        <p>{item.get('explanation', 'No explanation available.')}</p>
                        <p class="value">Value: {item.get('value', 'N/A')}</p>
                    </div>
                </div>
                """

            html += "</div>"

        return html

    @staticmethod
    def _get_css() -> str:
        """Get CSS styles"""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 {
            margin: 0 0 20px 0;
            color: #333;
        }
        .ticker-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .ticker {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }
        .score {
            font-size: 24px;
            color: #333;
        }
        .gpa {
            font-size: 20px;
            color: #666;
        }
        .checklist {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .category {
            margin-bottom: 30px;
        }
        .category h2 {
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .criterion {
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 10px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .criterion:hover {
            transform: translateX(5px);
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        .criterion-header {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .icon {
            font-size: 20px;
        }
        .label {
            flex: 1;
            font-weight: 500;
        }
        .value {
            color: #666;
            font-family: monospace;
        }
        .explanation {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #dee2e6;
            color: #666;
            font-size: 14px;
        }
        .passed {
            border-left: 4px solid #28a745;
        }
        .failed {
            border-left: 4px solid #dc3545;
        }
        .unknown {
            border-left: 4px solid #ffc107;
        }
        .progress-bar {
            height: 10px;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        footer {
            text-align: center;
            color: white;
            margin-top: 30px;
        }
        .disclaimer {
            font-weight: bold;
            font-size: 14px;
        }
        .timestamp {
            font-size: 12px;
            opacity: 0.8;
        }
        """

    @staticmethod
    def _get_javascript() -> str:
        """Get JavaScript for interactivity"""
        return """
        function toggleExplanation(element) {
            const explanation = element.querySelector('.explanation');
            if (explanation) {
                if (explanation.style.display === 'none') {
                    explanation.style.display = 'block';
                } else {
                    explanation.style.display = 'none';
                }
            }
        }
        """

    @staticmethod
    def _grade_color(grade: str) -> str:
        """Get color for grade"""
        grade_colors = {
            'A+': '#28a745',
            'A': '#28a745',
            'B+': '#20c997',
            'B': '#17a2b8',
            'C': '#ffc107',
            'D': '#fd7e14',
            'F': '#dc3545'
        }
        return grade_colors.get(grade, '#6c757d')