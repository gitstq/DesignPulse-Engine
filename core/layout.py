"""
layout.py - Layout analysis module for DesignPulse-Engine.

Analyzes layout consistency, spacing, semantic structure,
and overall layout quality.
"""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.css_parser import get_property_values, count_selectors, get_media_queries


def analyze_layout(all_styles, html_info=None):
    """
    Perform comprehensive layout analysis.

    Args:
        all_styles: dict from css_parser.extract_all_styles()
        html_info: dict from html_parser.parse_html()

    Returns:
        dict with layout analysis results.
    """
    result = {
        'consistency_score': 0,
        'spacing_score': 0,
        'semantic_count': 0,
        'semantic_ratio': 0,
        'total_selectors': 0,
        'unique_selectors': 0,
        'inline_style_count': 0,
        'has_grid': False,
        'has_flexbox': False,
        'score': 0,
        'suggestions': [],
    }

    # Semantic HTML analysis
    if html_info:
        semantic_count = html_info.get('semantic_count', 0)
        total_tags = html_info.get('total_tags', 1)
        result['semantic_count'] = semantic_count
        result['semantic_ratio'] = round(semantic_count / max(total_tags, 1) * 100, 1)

    # Selector statistics
    total, unique, inline = count_selectors(all_styles)
    result['total_selectors'] = total
    result['unique_selectors'] = unique
    result['inline_style_count'] = inline

    # Check for modern layout techniques
    result['has_flexbox'] = _detect_flexbox(all_styles)
    result['has_grid'] = _detect_grid(all_styles)

    # Spacing consistency analysis
    spacing_result = _analyze_spacing(all_styles)
    result['spacing_score'] = spacing_result['score']
    result['suggestions'].extend(spacing_result['suggestions'])

    # Score layout
    layout_score = _score_layout(result, html_info)
    result['consistency_score'] = layout_score['score']
    result['suggestions'].extend(layout_score['suggestions'])

    # Overall layout score is the consistency score
    result['score'] = result['consistency_score']

    return result


def _detect_flexbox(all_styles):
    """Check if flexbox layout is used."""
    display_values = get_property_values(all_styles, 'display')
    for selector, value in display_values:
        if 'flex' in value.lower():
            return True

    # Also check for flex-specific properties
    flex_props = ['flex-direction', 'flex-wrap', 'justify-content',
                  'align-items', 'align-self', 'flex-grow', 'flex-shrink', 'flex-basis']
    for prop in flex_props:
        values = get_property_values(all_styles, prop)
        if values:
            return True

    return False


def _detect_grid(all_styles):
    """Check if CSS Grid layout is used."""
    display_values = get_property_values(all_styles, 'display')
    for selector, value in display_values:
        if 'grid' in value.lower():
            return True

    # Also check for grid-specific properties
    grid_props = ['grid-template-columns', 'grid-template-rows',
                  'grid-gap', 'gap', 'grid-column', 'grid-row',
                  'grid-area', 'grid-template-areas']
    for prop in grid_props:
        values = get_property_values(all_styles, prop)
        if values:
            return True

    return False


def _analyze_spacing(all_styles):
    """
    Analyze spacing consistency across the stylesheet.
    Checks margin and padding values for consistent patterns.
    """
    result = {
        'score': 0,
        'suggestions': []
    }

    # Collect all margin and padding values
    spacing_values = []

    spacing_props = [
        'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
        'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
        'gap', 'row-gap', 'column-gap'
    ]

    for prop in spacing_props:
        values = get_property_values(all_styles, prop)
        for selector, value in values:
            px = _parse_spacing_value(value)
            if px is not None and px != 0:
                spacing_values.append({
                    'property': prop,
                    'selector': selector,
                    'value': value,
                    'px': px
                })

    if not spacing_values:
        result['score'] = 50
        return result

    # Check for spacing scale consistency
    px_values = [sv['px'] for sv in spacing_values]
    unique_px = sorted(set(px_values))

    # A good spacing system uses values from a consistent scale
    # Common scales: 4, 8, 12, 16, 24, 32, 48, 64 (4px base)
    # Or: 5, 10, 15, 20, 30, 40, 60, 80 (5px base)

    score = 50  # Base score

    # Check 4px base scale
    scale_4 = all(v % 4 == 0 for v in px_values)
    # Check 8px base scale
    scale_8 = all(v % 8 == 0 for v in px_values)

    if scale_8:
        score += 25
    elif scale_4:
        score += 20
    else:
        # Check how many values deviate from 4px grid
        on_grid = sum(1 for v in px_values if v % 4 == 0)
        grid_ratio = on_grid / len(px_values)
        if grid_ratio >= 0.8:
            score += 15
        elif grid_ratio >= 0.6:
            score += 10
        else:
            score += 0
            result['suggestions'].append({
                'message': 'Spacing values are inconsistent. Consider using a 4px or 8px base grid system.',
                'priority': 'medium',
                'category': 'layout'
            })

    # Check for too many unique spacing values
    if len(unique_px) > 10:
        score -= 10
        result['suggestions'].append({
            'message': 'Too many unique spacing values ({}). Simplify to a consistent spacing scale.'.format(
                len(unique_px)
            ),
            'priority': 'low',
            'category': 'layout'
        })

    result['score'] = max(0, min(100, score))
    return result


def _parse_spacing_value(value):
    """
    Parse a CSS spacing value to pixels.
    """
    if not value:
        return None

    value = value.strip().lower()
    value = re.sub(r'!\s*important', '', value, flags=re.IGNORECASE).strip()

    if value in ('auto', 'inherit', 'initial', 'normal', 'unset'):
        return None

    # Handle shorthand with multiple values (take the first)
    if ' ' in value:
        parts = value.split()
        value = parts[0]

    num_match = re.match(r'([+-]?\d*\.?\d+)', value)
    if not num_match:
        return None

    num = float(num_match.group(1))

    if 'px' in value:
        return num
    elif 'em' in value or 'rem' in value:
        return num * 16
    elif '%' in value:
        return num * 16 / 100
    elif 'vw' in value:
        return num * 19.2
    else:
        return num


def _score_layout(layout_result, html_info=None):
    """
    Score overall layout quality.
    """
    score = 0
    suggestions = []

    # 1. Semantic HTML usage
    semantic_count = layout_result.get('semantic_count', 0)
    if semantic_count >= 5:
        score += 20
    elif semantic_count >= 3:
        score += 15
    elif semantic_count >= 1:
        score += 10
        suggestions.append({
            'message': 'Few semantic HTML elements used. Consider using <header>, <main>, <nav>, <footer>, etc.',
            'priority': 'medium',
            'category': 'layout'
        })
    else:
        score += 0
        suggestions.append({
            'message': 'No semantic HTML5 elements detected. Use <header>, <main>, <nav>, <section>, <footer> for better structure.',
            'priority': 'high',
            'category': 'layout'
        })

    # 2. Modern layout techniques
    has_flex = layout_result.get('has_flexbox', False)
    has_grid = layout_result.get('has_grid', False)

    if has_grid and has_flex:
        score += 20
    elif has_flex:
        score += 15
    elif has_grid:
        score += 15
    else:
        score += 5
        suggestions.append({
            'message': 'No Flexbox or CSS Grid detected. Modern layout techniques improve responsiveness and maintainability.',
            'priority': 'low',
            'category': 'layout'
        })

    # 3. Inline style ratio (lower is better)
    total_selectors = layout_result.get('total_selectors', 0)
    inline_count = layout_result.get('inline_style_count', 0)

    if total_selectors > 0:
        inline_ratio = inline_count / total_selectors
        if inline_ratio <= 0.1:
            score += 15
        elif inline_ratio <= 0.3:
            score += 10
        elif inline_ratio <= 0.5:
            score += 5
            suggestions.append({
                'message': 'High ratio of inline styles ({}%). Move styles to external/internal CSS for better maintainability.'.format(
                    int(inline_ratio * 100)
                ),
                'priority': 'medium',
                'category': 'layout'
            })
        else:
            score += 0
            suggestions.append({
                'message': 'Very high inline style usage ({}%). Externalize CSS for better maintainability and performance.'.format(
                    int(inline_ratio * 100)
                ),
                'priority': 'high',
                'category': 'layout'
            })

    # 4. DOCTYPE declaration
    if html_info and html_info.get('has_doctype'):
        score += 5
    else:
        suggestions.append({
            'message': 'No DOCTYPE declaration found. Add <!DOCTYPE html> for standards compliance.',
            'priority': 'low',
            'category': 'layout'
        })

    # 5. Viewport meta tag (part of responsive, but relevant here)
    if html_info and html_info.get('meta_viewport'):
        score += 5

    # 6. Image alt text
    if html_info:
        images = html_info.get('images', [])
        if images:
            alt_count = sum(1 for src, alt in images if alt)
            alt_ratio = alt_count / len(images)
            if alt_ratio >= 0.9:
                score += 10
            elif alt_ratio >= 0.5:
                score += 5
                suggestions.append({
                    'message': 'Some images are missing alt text ({} of {}). Add alt attributes for accessibility.'.format(
                        len(images) - alt_count, len(images)
                    ),
                    'priority': 'medium',
                    'category': 'layout'
                })
            else:
                suggestions.append({
                    'message': 'Most images lack alt text ({} of {}). Alt text is essential for accessibility.'.format(
                        alt_count, len(images)
                    ),
                    'priority': 'high',
                    'category': 'layout'
                })

    return {
        'score': max(0, min(100, score)),
        'suggestions': suggestions
    }
