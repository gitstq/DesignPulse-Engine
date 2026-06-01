"""
analyzer.py - Core analysis engine for DesignPulse-Engine.

Orchestrates all analysis modules and produces a comprehensive
design quality report.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.css_parser import extract_all_styles, get_media_queries
from utils.html_parser import parse_html
from core.color import analyze_colors
from core.typography import analyze_typography
from core.layout import analyze_layout
from core.accessibility import analyze_accessibility
from core.scorer import calculate_overall_score, generate_suggestions, SCORING_WEIGHTS


def analyze_file(filepath):
    """
    Analyze a single HTML file and return comprehensive results.

    Args:
        filepath: path to the HTML file

    Returns:
        dict with complete analysis results
    """
    # Read file content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except (IOError, OSError) as e:
        return {
            'error': 'Failed to read file: {}'.format(str(e)),
            'file_info': {'filename': filepath}
        }

    return analyze_content(html_content, filepath)


def analyze_content(html_content, source_name="inline"):
    """
    Analyze HTML content string and return comprehensive results.

    Args:
        html_content: HTML content string
        source_name: name/identifier for the source

    Returns:
        dict with complete analysis results
    """
    # File info
    file_info = {
        'filename': os.path.basename(source_name) if source_name else 'unknown',
        'filepath': source_name if source_name else '',
        'file_size': len(html_content.encode('utf-8')),
    }

    # Parse HTML structure
    html_info = parse_html(html_content)

    # Extract all styles
    all_styles = extract_all_styles(html_content)

    # Run analysis modules
    color_analysis = analyze_colors(all_styles, html_info)
    typography_analysis = analyze_typography(all_styles, html_info)
    layout_analysis = analyze_layout(all_styles, html_info)
    accessibility_analysis = analyze_accessibility(all_styles, html_info, html_content)
    responsive_analysis = _analyze_responsive(all_styles, html_info)
    code_quality_analysis = _analyze_code_quality(html_content, all_styles, html_info)

    # Calculate dimension scores
    dimension_scores = {
        'color_harmony': {
            'score': color_analysis.get('harmony_score', 0),
        },
        'contrast_accessibility': {
            'score': _avg_scores(
                color_analysis.get('contrast_score', 0),
                accessibility_analysis.get('score', 0)
            ),
        },
        'typography': {
            'score': typography_analysis.get('score', 0),
        },
        'layout_consistency': {
            'score': layout_analysis.get('consistency_score', 0),
        },
        'responsive_design': {
            'score': responsive_analysis.get('score', 0),
        },
        'code_quality': {
            'score': code_quality_analysis.get('score', 0),
        },
    }

    # Calculate overall score
    scoring_result = calculate_overall_score(dimension_scores)

    # Generate suggestions
    all_results = {
        'color_analysis': color_analysis,
        'typography_analysis': typography_analysis,
        'layout_analysis': layout_analysis,
        'accessibility_analysis': accessibility_analysis,
        'responsive_analysis': responsive_analysis,
        'code_quality': code_quality_analysis,
    }
    suggestions = generate_suggestions(all_results)

    # Assemble final result
    result = {
        'file_info': file_info,
        'overall_score': scoring_result['overall_score'],
        'grade': scoring_result['grade'],
        'summary': scoring_result['summary'],
        'dimension_scores': scoring_result['dimension_scores'],
        'color_analysis': color_analysis,
        'typography_analysis': typography_analysis,
        'layout_analysis': layout_analysis,
        'accessibility_analysis': accessibility_analysis,
        'responsive_analysis': responsive_analysis,
        'code_quality': code_quality_analysis,
        'suggestions': suggestions,
    }

    return result


def analyze_colors_only(html_content, source_name="inline"):
    """Analyze only the color scheme of the HTML content."""
    all_styles = extract_all_styles(html_content)
    html_info = parse_html(html_content)
    return analyze_colors(all_styles, html_info)


def analyze_typography_only(html_content, source_name="inline"):
    """Analyze only the typography of the HTML content."""
    all_styles = extract_all_styles(html_content)
    html_info = parse_html(html_content)
    return analyze_typography(all_styles, html_info)


def analyze_accessibility_only(html_content, source_name="inline"):
    """Analyze only the accessibility of the HTML content."""
    all_styles = extract_all_styles(html_content)
    html_info = parse_html(html_content)
    return analyze_accessibility(all_styles, html_info, html_content)


def _analyze_responsive(all_styles, html_info):
    """
    Analyze responsive design quality.
    """
    result = {
        'has_viewport': False,
        'media_query_count': 0,
        'media_queries': [],
        'score': 0,
        'suggestions': [],
    }

    # Check viewport meta tag
    result['has_viewport'] = bool(html_info.get('meta_viewport', ''))

    # Check media queries
    media_queries = get_media_queries(all_styles)
    result['media_query_count'] = len(media_queries)
    result['media_queries'] = media_queries

    score = 0

    # Viewport meta (essential for responsive)
    if result['has_viewport']:
        score += 30
    else:
        result['suggestions'].append({
            'message': 'Missing viewport meta tag. Add <meta name="viewport" content="width=device-width, initial-scale=1.0"> for responsive design.',
            'priority': 'high',
            'category': 'responsive'
        })

    # Media queries
    mq_count = result['media_query_count']
    if mq_count >= 4:
        score += 40
    elif mq_count >= 2:
        score += 30
    elif mq_count >= 1:
        score += 15
        result['suggestions'].append({
            'message': 'Only {} media query found. Consider adding breakpoints for tablet and mobile devices.'.format(
                mq_count
            ),
            'priority': 'medium',
            'category': 'responsive'
        })
    else:
        result['suggestions'].append({
            'message': 'No media queries found. Add responsive breakpoints for different screen sizes.',
            'priority': 'high',
            'category': 'responsive'
        })

    # Check for responsive units (%, em, rem, vw, vh)
    import re
    responsive_units = re.findall(
        r'(?:width|height|max-width|min-width|margin|padding|font-size)\s*:\s*[^;]*?(%|em|rem|vw|vh)',
        str(all_styles.get('style_tags', [])),
        re.IGNORECASE
    )
    if len(responsive_units) >= 5:
        score += 20
    elif len(responsive_units) >= 2:
        score += 10
    else:
        result['suggestions'].append({
            'message': 'Few responsive units (em, rem, %, vw, vh) detected. Use relative units for better scalability.',
            'priority': 'low',
            'category': 'responsive'
        })

    # Check for max-width on containers (common responsive pattern)
    max_width_values = []
    for rule in all_styles.get('style_tags', []):
        decls = rule.get('declarations', {})
        if 'max-width' in decls:
            max_width_values.append(decls['max-width'])

    if max_width_values:
        score += 10

    result['score'] = max(0, min(100, score))
    return result


def _analyze_code_quality(html_content, all_styles, html_info):
    """
    Analyze HTML/CSS code quality.
    """
    result = {
        'score': 0,
        'suggestions': [],
    }

    score = 50  # Base score

    # 1. Check for DOCTYPE
    if html_info.get('has_doctype'):
        score += 10
    else:
        result['suggestions'].append({
            'message': 'Missing DOCTYPE declaration. Start the document with <!DOCTYPE html>.',
            'priority': 'medium',
            'category': 'code_quality'
        })

    # 2. Check for charset
    if html_info.get('meta_charset'):
        score += 5
    else:
        result['suggestions'].append({
            'message': 'Missing character encoding declaration. Add <meta charset="UTF-8">.',
            'priority': 'medium',
            'category': 'code_quality'
        })

    # 3. Check CSS organization (comments, structure)
    import re
    css_comments = re.findall(r'/\*.*?\*/', ''.join(all_styles.get('raw_css', [])), re.DOTALL)
    if css_comments:
        score += 5

    # 4. Check for !important usage
    important_count = 0
    for css_text in all_styles.get('raw_css', []):
        important_count += len(re.findall(r'!\s*important', css_text, re.IGNORECASE))

    for tag, style_dict in all_styles.get('inline', []):
        for prop, value in style_dict.items():
            if '!important' in value.lower():
                important_count += 1

    if important_count == 0:
        score += 10
    elif important_count <= 2:
        score += 5
    else:
        score -= min(10, important_count * 2)
        result['suggestions'].append({
            'message': 'Excessive use of !important ({} times). Avoid !important; increase CSS specificity instead.'.format(
                important_count
            ),
            'priority': 'medium',
            'category': 'code_quality'
        })

    # 5. Check for inline styles ratio
    total_selectors = html_info.get('total_tags', 0)
    inline_count = len(all_styles.get('inline', []))
    style_tag_count = len(all_styles.get('style_tags', []))

    if style_tag_count > 0 or inline_count > 0:
        total_styles = inline_count + style_tag_count
        if total_styles > 0:
            inline_ratio = inline_count / total_styles
            if inline_ratio <= 0.2:
                score += 10
            elif inline_ratio > 0.6:
                score -= 10
                result['suggestions'].append({
                    'message': 'Heavy use of inline styles ({}% of all styles). Move to <style> tags or external CSS.'.format(
                        int(inline_ratio * 100)
                    ),
                    'priority': 'medium',
                    'category': 'code_quality'
                })

    # 6. Check for deprecated elements
    deprecated = re.findall(
        r'<(font|center|b|i|strike|s|u|big|small|tt|frame|frameset)[\s>]',
        html_content,
        re.IGNORECASE
    )
    if deprecated:
        score -= len(deprecated) * 3
        result['suggestions'].append({
            'message': 'Deprecated HTML elements found: {}. Use CSS for styling instead.'.format(
                ', '.join(set(d.lower() for d in deprecated))
            ),
            'priority': 'low',
            'category': 'code_quality'
        })

    # 7. Check for proper HTML structure
    if html_info.get('title'):
        score += 5

    result['score'] = max(0, min(100, score))
    return result


def _avg_scores(*scores):
    """Calculate the average of multiple scores."""
    valid = [s for s in scores if s is not None]
    return int(sum(valid) / len(valid)) if valid else 0
