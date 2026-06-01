"""
scorer.py - Scoring system for DesignPulse-Engine.

Computes weighted overall scores from individual dimension scores.
Generates optimization suggestions based on scoring results.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Scoring weights for each dimension
SCORING_WEIGHTS = {
    'color_harmony': 0.25,
    'contrast_accessibility': 0.20,
    'typography': 0.20,
    'layout_consistency': 0.15,
    'responsive_design': 0.10,
    'code_quality': 0.10,
}


def calculate_overall_score(dimension_scores):
    """
    Calculate the weighted overall design quality score.

    Args:
        dimension_scores: dict mapping dimension keys to score dicts
            e.g., {'color_harmony': {'score': 85}, 'typography': {'score': 72}, ...}

    Returns:
        dict with 'overall_score', 'dimension_scores', 'grade', and 'summary'
    """
    overall = 0
    detailed_scores = {}

    for dimension, weight in SCORING_WEIGHTS.items():
        dim_data = dimension_scores.get(dimension, {})
        score = dim_data.get('score', 0) if isinstance(dim_data, dict) else dim_data
        weighted = score * weight
        overall += weighted

        detailed_scores[dimension] = {
            'score': score,
            'weight': weight,
            'weighted_score': round(weighted, 1),
            'label': _dimension_label(dimension),
        }

    overall = round(overall)

    return {
        'overall_score': overall,
        'dimension_scores': detailed_scores,
        'grade': _score_to_grade(overall),
        'summary': _generate_summary(overall),
    }


def generate_suggestions(analysis_results):
    """
    Collect and prioritize suggestions from all analysis modules.
    Deduplicates and sorts by priority.

    Args:
        analysis_results: dict containing results from all analysis modules

    Returns:
        list of suggestion dicts sorted by priority (high first)
    """
    all_suggestions = []

    # Collect from each module
    modules = [
        'color_analysis',
        'typography_analysis',
        'layout_analysis',
        'accessibility_analysis',
        'responsive_analysis',
    ]

    for module in modules:
        module_data = analysis_results.get(module, {})
        suggestions = module_data.get('suggestions', [])
        all_suggestions.extend(suggestions)

    # Deduplicate by message
    seen = set()
    unique_suggestions = []
    for s in all_suggestions:
        msg = s.get('message', '')
        if msg and msg not in seen:
            seen.add(msg)
            unique_suggestions.append(s)

    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    unique_suggestions.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))

    return unique_suggestions


def _dimension_label(dimension):
    """Get human-readable label for a scoring dimension."""
    labels = {
        'color_harmony': 'Color Harmony',
        'contrast_accessibility': 'Contrast / Accessibility',
        'typography': 'Typography',
        'layout_consistency': 'Layout Consistency',
        'responsive_design': 'Responsive Design',
        'code_quality': 'Code Quality',
    }
    return labels.get(dimension, dimension)


def _score_to_grade(score):
    """Convert a 0-100 score to a letter grade."""
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'


def _generate_summary(score):
    """Generate a brief text summary for the overall score."""
    if score >= 90:
        return "Excellent design quality. Professional-grade implementation."
    elif score >= 80:
        return "Good design quality with minor areas for improvement."
    elif score >= 70:
        return "Acceptable design quality. Several areas need attention."
    elif score >= 60:
        return "Below average design quality. Significant improvements recommended."
    elif score >= 40:
        return "Poor design quality. Major improvements needed."
    else:
        return "Very poor design quality. Fundamental redesign recommended."
