"""
typography.py - Typography analysis module for DesignPulse-Engine.

Analyzes font usage, size hierarchy, line height, letter spacing,
and overall typographic quality.
"""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.css_parser import get_property_values


def analyze_typography(all_styles, html_info=None):
    """
    Perform comprehensive typography analysis.

    Args:
        all_styles: dict from css_parser.extract_all_styles()
        html_info: dict from html_parser.parse_html()

    Returns:
        dict with typography analysis results.
    """
    result = {
        'font_families': [],
        'font_sizes': [],
        'line_heights': [],
        'letter_spacings': [],
        'size_range': 'N/A',
        'line_height_range': 'N/A',
        'score': 0,
        'suggestions': [],
    }

    # Extract font-family values
    font_family_values = get_property_values(all_styles, 'font-family')
    font_families = set()
    for selector, value in font_family_values:
        # Clean up font-family value
        families = _parse_font_families(value)
        font_families.update(families)

    result['font_families'] = sorted(font_families)

    # Extract font-size values
    font_size_values = get_property_values(all_styles, 'font-size')
    font_sizes = []
    for selector, value in font_size_values:
        px_size = _parse_size_to_px(value)
        if px_size is not None:
            font_sizes.append({
                'selector': selector,
                'raw': value,
                'px': px_size
            })

    result['font_sizes'] = font_sizes

    # Extract line-height values
    line_height_values = get_property_values(all_styles, 'line-height')
    line_heights = []
    for selector, value in line_height_values:
        lh = _parse_line_height(value)
        if lh is not None:
            line_heights.append({
                'selector': selector,
                'raw': value,
                'value': lh
            })

    result['line_heights'] = line_heights

    # Extract letter-spacing values
    letter_spacing_values = get_property_values(all_styles, 'letter-spacing')
    letter_spacings = []
    for selector, value in letter_spacing_values:
        ls = _parse_letter_spacing(value)
        if ls is not None:
            letter_spacings.append({
                'selector': selector,
                'raw': value,
                'px': ls
            })

    result['letter_spacings'] = letter_spacings

    # Calculate ranges
    if font_sizes:
        px_values = [fs['px'] for fs in font_sizes]
        result['size_range'] = "{}px - {}px".format(
            min(px_values), max(px_values)
        )

    if line_heights:
        lh_values = [lh['value'] for lh in line_heights]
        result['line_height_range'] = "{} - {}".format(
            min(lh_values), max(lh_values)
        )

    # Score typography
    score = _score_typography(result, html_info)
    result['score'] = score['score']
    result['suggestions'].extend(score['suggestions'])

    return result


def _parse_font_families(value):
    """
    Parse a CSS font-family value into a list of family names.
    Handles quotes, commas, and generic family names.
    """
    families = []

    # Remove !important
    value = re.sub(r'!\s*important', '', value, flags=re.IGNORECASE).strip()

    # Split by comma, handling quoted values
    pattern = r'"([^"]+)"|\'([^\']+)\'|([^,]+)'
    for match in re.finditer(pattern, value):
        if match.group(1):
            families.append(match.group(1).strip())
        elif match.group(2):
            families.append(match.group(2).strip())
        elif match.group(3):
            name = match.group(3).strip()
            if name:
                families.append(name)

    return families


def _parse_size_to_px(value):
    """
    Convert a CSS size value to pixels.
    Supports: px, em, rem, pt, %, vw, vh, and unitless values.
    Returns float pixels or None if unparseable.
    """
    if not value:
        return None

    value = value.strip().lower()
    value = re.sub(r'!\s*important', '', value, flags=re.IGNORECASE).strip()

    # Extract numeric value
    num_match = re.match(r'([+-]?\d*\.?\d+)', value)
    if not num_match:
        return None

    num = float(num_match.group(1))

    if 'px' in value:
        return num
    elif 'em' in value or 'rem' in value:
        return num * 16  # Assume 16px base
    elif 'pt' in value:
        return num * 1.333  # 1pt = 1.333px
    elif '%' in value:
        return num * 16 / 100  # Assume percentage of 16px base
    elif 'vw' in value:
        return num * 19.2  # Assume 1920px viewport
    elif 'vh' in value:
        return num * 10.8  # Assume 1080px viewport
    else:
        # Unitless (treated as em for line-height, px for font-size)
        return num


def _parse_line_height(value):
    """
    Parse a CSS line-height value.
    Returns a numeric value (unitless ratio or pixels).
    """
    if not value:
        return None

    value = value.strip().lower()
    value = re.sub(r'!\s*important', '', value, flags=re.IGNORECASE).strip()

    num_match = re.match(r'([+-]?\d*\.?\d+)', value)
    if not num_match:
        return None

    num = float(num_match.group(1))

    if 'px' in value:
        return num
    elif 'em' in value or 'rem' in value:
        return num
    elif '%' in value:
        return num / 100.0
    else:
        return num  # Unitless


def _parse_letter_spacing(value):
    """
    Parse a CSS letter-spacing value to pixels.
    """
    if not value:
        return None

    value = value.strip().lower()
    value = re.sub(r'!\s*important', '', value, flags=re.IGNORECASE).strip()

    if value == 'normal':
        return 0.0

    num_match = re.match(r'([+-]?\d*\.?\d+)', value)
    if not num_match:
        return None

    num = float(num_match.group(1))

    if 'px' in value:
        return num
    elif 'em' in value or 'rem' in value:
        return num * 16
    else:
        return num


def _score_typography(typo_result, html_info=None):
    """
    Score typography quality based on multiple factors.
    Returns dict with 'score' and 'suggestions'.
    """
    score = 0
    suggestions = []

    font_families = typo_result.get('font_families', [])
    font_sizes = typo_result.get('font_sizes', [])
    line_heights = typo_result.get('line_heights', [])

    # 1. Font family count (1-3 is ideal)
    if len(font_families) == 0:
        score += 10  # Using browser defaults
        suggestions.append({
            'message': 'No custom font-family defined. Consider specifying fonts for better typography control.',
            'priority': 'low',
            'category': 'typography'
        })
    elif 1 <= len(font_families) <= 3:
        score += 25
    elif 4 <= len(font_families) <= 6:
        score += 15
        suggestions.append({
            'message': 'Many font families used ({}). Consider reducing to 2-3 for consistency.'.format(
                len(font_families)
            ),
            'priority': 'low',
            'category': 'typography'
        })
    else:
        score += 5
        suggestions.append({
            'message': 'Too many font families ({}). Limit to 2-3 for a cohesive design.'.format(
                len(font_families)
            ),
            'priority': 'medium',
            'category': 'typography'
        })

    # 2. Font size hierarchy
    if font_sizes:
        px_values = sorted(set(fs['px'] for fs in font_sizes))
        size_range = max(px_values) - min(px_values)

        # Good typography has a clear hierarchy (range >= 12px)
        if size_range >= 24:
            score += 25
        elif size_range >= 12:
            score += 20
        elif size_range >= 6:
            score += 10
            suggestions.append({
                'message': 'Font size range is narrow ({}px). Use more variation for visual hierarchy.'.format(
                    int(size_range)
                ),
                'priority': 'medium',
                'category': 'typography'
            })
        else:
            score += 5
            suggestions.append({
                'message': 'Very little font size variation ({}px). Create a clear typographic hierarchy.'.format(
                    int(size_range)
                ),
                'priority': 'high',
                'category': 'typography'
            })

        # Check for modular scale (sizes follow a ratio)
        if len(px_values) >= 3:
            has_scale = _check_modular_scale(px_values)
            if has_scale:
                score += 10
            else:
                suggestions.append({
                    'message': 'Font sizes do not follow a clear modular scale. '
                               'Consider using a consistent ratio (e.g., 1.25, 1.333, 1.5).',
                    'priority': 'low',
                    'category': 'typography'
                })

        # Check for reasonable base font size (14-18px)
        has_reasonable_base = any(14 <= fs['px'] <= 18 for fs in font_sizes)
        if has_reasonable_base:
            score += 10
        else:
            suggestions.append({
                'message': 'No font size in the recommended 14-18px range for body text.',
                'priority': 'medium',
                'category': 'typography'
            })

        # Check for very small text (< 10px)
        very_small = [fs for fs in font_sizes if fs['px'] < 10]
        if very_small:
            score -= 5
            suggestions.append({
                'message': 'Very small font sizes detected ({}px). Minimum recommended size is 10px.'.format(
                    min(fs['px'] for fs in very_small)
                ),
                'priority': 'high',
                'category': 'typography'
            })
    else:
        score += 10  # No font sizes defined, using defaults

    # 3. Line height analysis
    if line_heights:
        lh_values = [lh['value'] for lh in line_heights]

        # Check for reasonable line heights (1.4 - 1.8 is ideal for body text)
        reasonable_lh = [lh for lh in lh_values if 1.2 <= lh <= 2.5]
        if reasonable_lh:
            ratio = len(reasonable_lh) / len(lh_values)
            if ratio >= 0.8:
                score += 15
            elif ratio >= 0.5:
                score += 10
            else:
                score += 5
                suggestions.append({
                    'message': 'Some line-height values are outside the recommended 1.4-1.8 range.',
                    'priority': 'low',
                    'category': 'typography'
                })
        else:
            score += 5
            suggestions.append({
                'message': 'Line-height values are outside normal range. Recommended: 1.4-1.8 for body text.',
                'priority': 'medium',
                'category': 'typography'
            })

        # Check for tight line heights (< 1.2)
        tight = [lh for lh in lh_values if lh < 1.2]
        if tight:
            suggestions.append({
                'message': 'Tight line-height detected ({}). Lines may overlap and reduce readability.'.format(
                    min(lh_values)
                ),
                'priority': 'high',
                'category': 'typography'
            })
    else:
        score += 10  # Using browser defaults

    # 4. Check for font-weight usage (via CSS)
    # This is handled implicitly through heading hierarchy

    # 5. Check heading hierarchy from HTML
    if html_info:
        headings = html_info.get('headings', [])
        heading_levels = set(h[0] for h in headings)

        # Check for proper hierarchy (h1 exists, levels don't skip)
        if 1 in heading_levels:
            score += 5
        else:
            suggestions.append({
                'message': 'No <h1> heading found. Every page should have a primary heading.',
                'priority': 'medium',
                'category': 'typography'
            })

        # Check for skipped levels (e.g., h1 -> h3 without h2)
        if heading_levels:
            sorted_levels = sorted(heading_levels)
            for i in range(len(sorted_levels) - 1):
                if sorted_levels[i + 1] - sorted_levels[i] > 1:
                    suggestions.append({
                        'message': 'Heading levels skip from h{} to h{}. Use sequential heading levels.'.format(
                            sorted_levels[i], sorted_levels[i + 1]
                        ),
                        'priority': 'medium',
                        'category': 'typography'
                    })
                    break

    return {
        'score': max(0, min(100, score)),
        'suggestions': suggestions
    }


def _check_modular_scale(sizes):
    """
    Check if font sizes roughly follow a modular scale.
    Tests common ratios: 1.067 (minor second), 1.125 (major second),
    1.2 (minor third), 1.25 (major third), 1.333 (perfect fourth),
    1.414 (augmented fourth), 1.5 (perfect fifth), 1.618 (golden ratio).
    """
    if len(sizes) < 3:
        return True  # Not enough data to evaluate

    common_ratios = [1.067, 1.125, 1.2, 1.25, 1.333, 1.414, 1.5, 1.618, 2.0]

    # Sort sizes
    sorted_sizes = sorted(sizes)
    if sorted_sizes[0] == 0:
        return False

    # Check if ratios between consecutive sizes match any common ratio
    for ratio in common_ratios:
        matches = 0
        for i in range(len(sorted_sizes) - 1):
            if sorted_sizes[i] > 0:
                actual_ratio = sorted_sizes[i + 1] / sorted_sizes[i]
                if abs(actual_ratio - ratio) < 0.15 or abs(actual_ratio - ratio * 2) < 0.3:
                    matches += 1
        if matches >= len(sorted_sizes) - 2:
            return True

    return False
