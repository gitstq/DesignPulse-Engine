"""
color.py - Color scheme analysis module for DesignPulse-Engine.

Analyzes color harmony, contrast ratios, WCAG compliance,
and overall color scheme quality.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.color_utils import (
    parse_color, contrast_ratio, wcag_level, rgb_to_hsl,
    color_temperature, color_distance, is_light_color, is_dark_color,
    extract_colors_from_css
)
from utils.css_parser import get_property_values


def analyze_colors(all_styles, html_info=None):
    """
    Perform comprehensive color analysis.

    Args:
        all_styles: dict from css_parser.extract_all_styles()
        html_info: dict from html_parser.parse_html()

    Returns:
        dict with color analysis results including:
        - unique_colors: list of unique (R,G,B) tuples
        - harmony_score: 0-100 color harmony score
        - contrast_score: 0-100 contrast quality score
        - wcag_summary: dict of WCAG level counts
        - avg_contrast_ratio: average contrast ratio
        - suggestions: list of improvement suggestions
    """
    result = {
        'unique_colors': [],
        'unique_color_count': 0,
        'harmony_score': 0,
        'contrast_score': 0,
        'wcag_summary': {},
        'avg_contrast_ratio': 0,
        'color_pairs': [],
        'suggestions': [],
    }

    # Extract all colors from CSS
    all_colors = []

    # Colors from style tags
    for css_text in all_styles.get('raw_css', []):
        colors = extract_colors_from_css(css_text)
        all_colors.extend(colors)

    # Colors from inline styles
    for tag, style_dict in all_styles.get('inline', []):
        for prop, value in style_dict.items():
            if any(c in prop for c in ['color', 'background', 'border']):
                parsed = parse_color(value)
                if parsed:
                    all_colors.append(parsed)

    # Deduplicate colors
    unique_colors = list(set(all_colors))
    result['unique_colors'] = unique_colors
    result['unique_color_count'] = len(unique_colors)

    if not unique_colors:
        result['harmony_score'] = 50  # Neutral score if no colors found
        result['contrast_score'] = 50
        result['suggestions'].append({
            'message': 'No explicit colors found in styles. Consider defining a clear color palette.',
            'priority': 'medium',
            'category': 'color'
        })
        return result

    # Analyze color harmony
    harmony_result = _analyze_harmony(unique_colors)
    result['harmony_score'] = harmony_result['score']
    result['suggestions'].extend(harmony_result['suggestions'])

    # Analyze contrast between foreground/background pairs
    contrast_result = _analyze_contrast(all_styles, unique_colors)
    result['contrast_score'] = contrast_result['score']
    result['wcag_summary'] = contrast_result['wcag_summary']
    result['avg_contrast_ratio'] = contrast_result['avg_ratio']
    result['color_pairs'] = contrast_result['pairs']
    result['suggestions'].extend(contrast_result['suggestions'])

    return result


def _analyze_harmony(colors):
    """
    Analyze color harmony based on color theory principles.
    Evaluates: analogous, complementary, triadic, and monochromatic schemes.
    """
    result = {
        'score': 0,
        'suggestions': []
    }

    if len(colors) < 2:
        result['score'] = 70  # Single color is fine
        return result

    # Convert all colors to HSL
    hsl_colors = [rgb_to_hsl(c) for c in colors]

    # Calculate hue distribution
    hues = [h for h, s, l in hsl_colors if s > 5]  # Only consider saturated colors
    saturations = [s for h, s, l in hsl_colors]
    lightnesses = [l for h, s, l in hsl_colors]

    score = 50  # Base score

    # 1. Color count evaluation (5-8 colors is ideal for a palette)
    color_count = len(colors)
    if 3 <= color_count <= 8:
        score += 15
    elif color_count > 8 and color_count <= 12:
        score += 5
    elif color_count > 12:
        score -= 10
        result['suggestions'].append({
            'message': 'Too many unique colors ({}). Consider reducing to 5-8 for a cohesive palette.'.format(
                color_count
            ),
            'priority': 'medium',
            'category': 'color'
        })
    elif color_count < 3:
        score += 5  # Minimal palette is acceptable

    # 2. Saturation consistency
    if saturations:
        avg_sat = sum(saturations) / len(saturations)
        sat_variance = sum((s - avg_sat) ** 2 for s in saturations) / len(saturations)
        if sat_variance < 200:
            score += 10  # Consistent saturation
        elif sat_variance > 800:
            score -= 5
            result['suggestions'].append({
                'message': 'Inconsistent saturation levels across colors. Consider harmonizing saturation values.',
                'priority': 'low',
                'category': 'color'
            })

    # 3. Lightness distribution (good designs have a range of lightness values)
    if lightnesses:
        min_l = min(lightnesses)
        max_l = max(lightnesses)
        l_range = max_l - min_l
        if 30 <= l_range <= 70:
            score += 10  # Good lightness range
        elif l_range < 20:
            score -= 5
            result['suggestions'].append({
                'message': 'Colors have very similar lightness. Add contrast with darker and lighter shades.',
                'priority': 'medium',
                'category': 'color'
            })

    # 4. Hue harmony analysis
    if len(hues) >= 2:
        hue_score = _evaluate_hue_harmony(hues)
        score += hue_score
        if hue_score < 10:
            result['suggestions'].append({
                'message': 'Color hues lack clear harmonic relationship. Consider using analogous, complementary, or triadic schemes.',
                'priority': 'low',
                'category': 'color'
            })

    # 5. Temperature balance
    warm_count = sum(1 for c in colors if color_temperature(c) == 'warm')
    cool_count = sum(1 for c in colors if color_temperature(c) == 'cool')
    total_colored = warm_count + cool_count

    if total_colored > 0:
        warm_ratio = warm_count / total_colored
        if 0.3 <= warm_ratio <= 0.7:
            score += 5  # Balanced temperature
        # Extreme temperature is also fine if intentional (monochrome warm/cool)

    # Clamp score
    result['score'] = max(0, min(100, score))
    return result


def _evaluate_hue_harmony(hues):
    """
    Evaluate how well hues follow color harmony principles.
    Returns a score contribution (0-20).
    """
    if len(hues) < 2:
        return 10

    score = 0
    sorted_hues = sorted(hues)

    # Check for analogous scheme (hues within 30 degrees of each other)
    max_hue_diff = max(
        min(abs(a - b), 360 - abs(a - b))
        for i, a in enumerate(sorted_hues)
        for b in sorted_hues[i + 1:]
    )

    if max_hue_diff <= 30:
        score += 15  # Analogous
    elif max_hue_diff <= 60:
        score += 12  # Near-analogous

    # Check for complementary pairs (180 degrees apart, +/- 15)
    has_complementary = False
    for i, a in enumerate(sorted_hues):
        for b in sorted_hues[i + 1:]:
            diff = abs(a - b)
            diff = min(diff, 360 - diff)
            if 165 <= diff <= 195:
                has_complementary = True
                break
        if has_complementary:
            break

    if has_complementary:
        score += 10

    # Check for triadic (120 degrees apart)
    if len(sorted_hues) >= 3:
        has_triadic = False
        for i, a in enumerate(sorted_hues):
            for j, b in enumerate(sorted_hues):
                if i == j:
                    continue
                for k, c in enumerate(sorted_hues):
                    if k == i or k == j:
                        continue
                    diff_ab = min(abs(a - b), 360 - abs(a - b))
                    diff_bc = min(abs(b - c), 360 - abs(b - c))
                    diff_ca = min(abs(c - a), 360 - abs(c - a))
                    if (abs(diff_ab - 120) <= 15 and
                            abs(diff_bc - 120) <= 15 and
                            abs(diff_ca - 120) <= 15):
                        has_triadic = True
                        break
                if has_triadic:
                    break
            if has_triadic:
                break
        if has_triadic:
            score += 10

    # Check for split-complementary
    if not has_complementary and len(sorted_hues) >= 3:
        score += 5  # Some structure

    return min(20, score)


def _analyze_contrast(all_styles, unique_colors):
    """
    Analyze contrast ratios between foreground and background color pairs.
    """
    result = {
        'score': 0,
        'wcag_summary': {},
        'avg_ratio': 0,
        'pairs': [],
        'suggestions': []
    }

    # Collect foreground/background color pairs
    fg_colors = []
    bg_colors = []

    # Extract color and background-color properties
    color_values = get_property_values(all_styles, 'color')
    bg_values = get_property_values(all_styles, 'background-color')
    bg_shorthand = get_property_values(all_styles, 'background')

    for selector, value in color_values:
        parsed = parse_color(value)
        if parsed:
            fg_colors.append(parsed)

    for selector, value in bg_values:
        parsed = parse_color(value)
        if parsed:
            bg_colors.append(parsed)

    for selector, value in bg_shorthand:
        parsed = parse_color(value)
        if parsed:
            bg_colors.append(parsed)

    # Calculate contrast ratios for all pairs
    ratios = []
    wcag_counts = {'AAA': 0, 'AA': 0, 'A': 0, 'Fail': 0}

    if fg_colors and bg_colors:
        for fg in fg_colors:
            for bg in bg_colors:
                ratio = contrast_ratio(fg, bg)
                level = wcag_level(ratio)
                ratios.append(ratio)
                wcag_counts[level] = wcag_counts.get(level, 0) + 1
                result['pairs'].append({
                    'foreground': fg,
                    'background': bg,
                    'ratio': round(ratio, 2),
                    'wcag_level': level
                })
    elif unique_colors:
        # If no explicit fg/bg pairs, evaluate all color pairs
        for i, c1 in enumerate(unique_colors):
            for c2 in unique_colors[i + 1:]:
                ratio = contrast_ratio(c1, c2)
                level = wcag_level(ratio)
                ratios.append(ratio)
                wcag_counts[level] = wcag_counts.get(level, 0) + 1

    result['wcag_summary'] = wcag_counts

    if ratios:
        avg_ratio = sum(ratios) / len(ratios)
        result['avg_ratio'] = round(avg_ratio, 2)

        # Score based on average contrast ratio
        if avg_ratio >= 7.0:
            score = 95
        elif avg_ratio >= 4.5:
            score = 80
        elif avg_ratio >= 3.0:
            score = 60
        elif avg_ratio >= 2.0:
            score = 40
        else:
            score = 20

        # Bonus for high AAA compliance rate
        total_pairs = sum(wcag_counts.values())
        if total_pairs > 0:
            aaa_rate = wcag_counts.get('AAA', 0) / total_pairs
            aa_rate = (wcag_counts.get('AAA', 0) + wcag_counts.get('AA', 0)) / total_pairs

            if aa_rate >= 0.8:
                score = min(100, score + 10)
            elif aa_rate < 0.5:
                score = max(0, score - 10)

            if wcag_counts.get('Fail', 0) > total_pairs * 0.5:
                result['suggestions'].append({
                    'message': 'More than half of color pairs fail WCAG contrast requirements. '
                               'Increase contrast between text and background colors.',
                    'priority': 'high',
                    'category': 'contrast'
                })
    else:
        score = 50  # No pairs to evaluate
        result['suggestions'].append({
            'message': 'No foreground/background color pairs found. '
                       'Ensure both color and background-color are defined for text elements.',
            'priority': 'medium',
            'category': 'contrast'
        })

    result['score'] = max(0, min(100, score))
    return result
