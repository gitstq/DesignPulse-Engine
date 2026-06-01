"""
report.py - Report generation utility for DesignPulse-Engine.

Generates analysis reports in JSON and Markdown formats.
Provides formatted terminal output for CLI display.
"""

import json
import os


def format_terminal_report(analysis_result):
    """
    Format analysis results as a colored terminal-friendly string.
    Returns a multi-line string suitable for printing to stdout.
    """
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("  DesignPulse-Engine - Design Quality Analysis Report")
    lines.append("=" * 60)
    lines.append("")

    # File info
    file_info = analysis_result.get('file_info', {})
    if file_info.get('filename'):
        lines.append("  File: {}".format(file_info['filename']))
    if file_info.get('file_size'):
        size_kb = file_info['file_size'] / 1024
        lines.append("  Size: {:.1f} KB".format(size_kb))
    lines.append("")

    # Overall score
    overall = analysis_result.get('overall_score', 0)
    grade = _score_to_grade(overall)
    lines.append("  Overall Score: {} / 100  [{}]".format(overall, grade))
    lines.append("")

    # Dimension scores
    scores = analysis_result.get('dimension_scores', {})
    if scores:
        lines.append("  Dimension Scores:")
        lines.append("  " + "-" * 40)
        dimensions = [
            ('color_harmony', 'Color Harmony', 25),
            ('contrast_accessibility', 'Contrast / Accessibility', 20),
            ('typography', 'Typography', 20),
            ('layout_consistency', 'Layout Consistency', 15),
            ('responsive_design', 'Responsive Design', 10),
            ('code_quality', 'Code Quality', 10),
        ]
        for key, label, weight in dimensions:
            score = scores.get(key, {}).get('score', 0)
            bar = _score_bar(score)
            lines.append("  {:<28} {:>3}  {}".format(label, score, bar))
        lines.append("")

    # Color analysis summary
    color_info = analysis_result.get('color_analysis', {})
    if color_info:
        lines.append("  Color Analysis:")
        lines.append("  " + "-" * 40)
        unique_colors = color_info.get('unique_colors', 0)
        lines.append("  Unique colors detected:  {}".format(unique_colors))

        contrast_score = color_info.get('contrast_score', 0)
        lines.append("  Average contrast ratio:   {:.1f}:1".format(
            color_info.get('avg_contrast_ratio', 0)
        ))

        harmony_score = color_info.get('harmony_score', 0)
        lines.append("  Color harmony score:      {}".format(harmony_score))

        wcag_summary = color_info.get('wcag_summary', {})
        if wcag_summary:
            lines.append("  WCAG compliance:")
            for level, count in wcag_summary.items():
                lines.append("    {}: {} color pairs".format(level, count))
        lines.append("")

    # Typography summary
    typo_info = analysis_result.get('typography_analysis', {})
    if typo_info:
        lines.append("  Typography Analysis:")
        lines.append("  " + "-" * 40)
        font_families = typo_info.get('font_families', [])
        if font_families:
            lines.append("  Font families used:  {}".format(len(font_families)))
            for ff in font_families[:5]:
                lines.append("    - {}".format(ff))
        lines.append("  Font size range:     {}".format(typo_info.get('size_range', 'N/A')))
        lines.append("  Line height range:   {}".format(typo_info.get('line_height_range', 'N/A')))
        lines.append("  Typography score:    {}".format(typo_info.get('score', 0)))
        lines.append("")

    # Layout summary
    layout_info = analysis_result.get('layout_analysis', {})
    if layout_info:
        lines.append("  Layout Analysis:")
        lines.append("  " + "-" * 40)
        lines.append("  Semantic elements:    {}".format(layout_info.get('semantic_count', 0)))
        lines.append("  Layout consistency:  {}".format(layout_info.get('consistency_score', 0)))
        lines.append("")

    # Accessibility summary
    a11y_info = analysis_result.get('accessibility_analysis', {})
    if a11y_info:
        lines.append("  Accessibility Analysis:")
        lines.append("  " + "-" * 40)
        lines.append("  Accessibility score:  {}".format(a11y_info.get('score', 0)))
        issues = a11y_info.get('issues', [])
        if issues:
            lines.append("  Issues found:        {}".format(len(issues)))
            for issue in issues[:5]:
                lines.append("    ! {}".format(issue))
        lines.append("")

    # Responsive design summary
    resp_info = analysis_result.get('responsive_analysis', {})
    if resp_info:
        lines.append("  Responsive Design:")
        lines.append("  " + "-" * 40)
        lines.append("  Has viewport meta:    {}".format(
            "Yes" if resp_info.get('has_viewport') else "No"
        ))
        lines.append("  Media queries found:  {}".format(
            resp_info.get('media_query_count', 0)
        ))
        lines.append("  Responsive score:     {}".format(resp_info.get('score', 0)))
        lines.append("")

    # Optimization suggestions
    suggestions = analysis_result.get('suggestions', [])
    if suggestions:
        lines.append("  Optimization Suggestions:")
        lines.append("  " + "-" * 40)
        for i, suggestion in enumerate(suggestions[:10], 1):
            priority = suggestion.get('priority', 'medium')
            marker = _priority_marker(priority)
            lines.append("  {}{}. {}".format(marker, i, suggestion.get('message', '')))
        lines.append("")

    lines.append("=" * 60)
    lines.append("  Generated by DesignPulse-Engine")
    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)


def generate_json_report(analysis_result):
    """
    Generate a JSON format report string.
    """
    return json.dumps(analysis_result, indent=2, ensure_ascii=False, default=str)


def generate_markdown_report(analysis_result):
    """
    Generate a Markdown format report string.
    """
    lines = []

    lines.append("# DesignPulse-Engine Analysis Report")
    lines.append("")

    # File info
    file_info = analysis_result.get('file_info', {})
    if file_info.get('filename'):
        lines.append("**File:** {}".format(file_info['filename']))
    if file_info.get('file_size'):
        size_kb = file_info['file_size'] / 1024
        lines.append("**Size:** {:.1f} KB".format(size_kb))
    lines.append("")

    # Overall score
    overall = analysis_result.get('overall_score', 0)
    grade = _score_to_grade(overall)
    lines.append("## Overall Score: {} / 100 ({})".format(overall, grade))
    lines.append("")

    # Dimension scores
    scores = analysis_result.get('dimension_scores', {})
    if scores:
        lines.append("## Dimension Scores")
        lines.append("")
        lines.append("| Dimension | Score | Weight |")
        lines.append("|-----------|-------|--------|")

        dimensions = [
            ('color_harmony', 'Color Harmony', 25),
            ('contrast_accessibility', 'Contrast / Accessibility', 20),
            ('typography', 'Typography', 20),
            ('layout_consistency', 'Layout Consistency', 15),
            ('responsive_design', 'Responsive Design', 10),
            ('code_quality', 'Code Quality', 10),
        ]
        for key, label, weight in dimensions:
            score = scores.get(key, {}).get('score', 0)
            lines.append("| {} | {}/100 | {}% |".format(label, score, weight))
        lines.append("")

    # Color analysis
    color_info = analysis_result.get('color_analysis', {})
    if color_info:
        lines.append("## Color Analysis")
        lines.append("")
        lines.append("- **Unique colors:** {}".format(color_info.get('unique_colors', 0)))
        lines.append("- **Average contrast ratio:** {:.1f}:1".format(
            color_info.get('avg_contrast_ratio', 0)
        ))
        lines.append("- **Color harmony score:** {}".format(color_info.get('harmony_score', 0)))

        wcag_summary = color_info.get('wcag_summary', {})
        if wcag_summary:
            lines.append("- **WCAG compliance:**")
            for level, count in wcag_summary.items():
                lines.append("  - {}: {} pairs".format(level, count))
        lines.append("")

    # Typography
    typo_info = analysis_result.get('typography_analysis', {})
    if typo_info:
        lines.append("## Typography Analysis")
        lines.append("")
        font_families = typo_info.get('font_families', [])
        if font_families:
            lines.append("- **Font families:** {}".format(", ".join(font_families[:5])))
        lines.append("- **Font size range:** {}".format(typo_info.get('size_range', 'N/A')))
        lines.append("- **Line height range:** {}".format(typo_info.get('line_height_range', 'N/A')))
        lines.append("- **Score:** {}".format(typo_info.get('score', 0)))
        lines.append("")

    # Layout
    layout_info = analysis_result.get('layout_analysis', {})
    if layout_info:
        lines.append("## Layout Analysis")
        lines.append("")
        lines.append("- **Semantic elements:** {}".format(layout_info.get('semantic_count', 0)))
        lines.append("- **Consistency score:** {}".format(layout_info.get('consistency_score', 0)))
        lines.append("")

    # Accessibility
    a11y_info = analysis_result.get('accessibility_analysis', {})
    if a11y_info:
        lines.append("## Accessibility Analysis")
        lines.append("")
        lines.append("- **Score:** {}".format(a11y_info.get('score', 0)))
        issues = a11y_info.get('issues', [])
        if issues:
            lines.append("- **Issues:**")
            for issue in issues:
                lines.append("  - {}".format(issue))
        lines.append("")

    # Responsive
    resp_info = analysis_result.get('responsive_analysis', {})
    if resp_info:
        lines.append("## Responsive Design")
        lines.append("")
        lines.append("- **Viewport meta:** {}".format(
            "Yes" if resp_info.get('has_viewport') else "No"
        ))
        lines.append("- **Media queries:** {}".format(resp_info.get('media_query_count', 0)))
        lines.append("- **Score:** {}".format(resp_info.get('score', 0)))
        lines.append("")

    # Suggestions
    suggestions = analysis_result.get('suggestions', [])
    if suggestions:
        lines.append("## Optimization Suggestions")
        lines.append("")
        for i, suggestion in enumerate(suggestions, 1):
            priority = suggestion.get('priority', 'medium')
            lines.append("{}. **[{}]** {}".format(
                i, priority.upper(), suggestion.get('message', '')
            ))
        lines.append("")

    return "\n".join(lines)


def generate_batch_summary(batch_results):
    """
    Generate a summary report for batch analysis of multiple files.
    """
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("  DesignPulse-Engine - Batch Analysis Summary")
    lines.append("=" * 60)
    lines.append("")

    if not batch_results:
        lines.append("  No files analyzed.")
        lines.append("")
        return "\n".join(lines)

    total_files = len(batch_results)
    total_score = 0
    scores = []

    lines.append("  {:<40} {:>8}".format("File", "Score"))
    lines.append("  " + "-" * 50)

    for result in batch_results:
        filename = result.get('file_info', {}).get('filename', 'unknown')
        score = result.get('overall_score', 0)
        scores.append(score)
        total_score += score

        # Truncate long filenames
        display_name = filename if len(filename) <= 38 else "..." + filename[-35:]
        lines.append("  {:<40} {:>8}".format(display_name, score))

    lines.append("  " + "-" * 50)

    avg_score = total_score / total_files if total_files > 0 else 0
    lines.append("  {:<40} {:>8}".format("Average", int(avg_score)))
    lines.append("")

    if scores:
        lines.append("  Score Distribution:")
        lines.append("    Highest: {}".format(max(scores)))
        lines.append("    Lowest:  {}".format(min(scores)))
        lines.append("    Average: {}".format(int(avg_score)))
    lines.append("")

    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)


def save_report(content, filepath, fmt="json"):
    """
    Save report content to a file.
    Returns the filepath on success, None on failure.
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath
    except (IOError, OSError) as e:
        return None


def _score_to_grade(score):
    """Convert a 0-100 score to a letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def _score_bar(score, width=20):
    """Create a visual score bar using ASCII characters."""
    filled = int(score / 100 * width)
    empty = width - filled
    return "[" + "#" * filled + "-" * empty + "]"


def _priority_marker(priority):
    """Return a marker character for suggestion priority."""
    if priority == 'high':
        return "[!] "
    elif priority == 'medium':
        return "[~] "
    else:
        return "[.] "
