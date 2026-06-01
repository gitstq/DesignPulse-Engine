"""
accessibility.py - Accessibility analysis module for DesignPulse-Engine.

Analyzes WCAG compliance, ARIA usage, semantic structure,
and overall accessibility quality.
"""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.color_utils import parse_color, contrast_ratio, wcag_level
from utils.css_parser import get_property_values


def analyze_accessibility(all_styles, html_info=None, html_content=None):
    """
    Perform comprehensive accessibility analysis.

    Args:
        all_styles: dict from css_parser.extract_all_styles()
        html_info: dict from html_parser.parse_html()
        html_content: raw HTML string for additional checks

    Returns:
        dict with accessibility analysis results.
    """
    result = {
        'score': 0,
        'issues': [],
        'warnings': [],
        'passes': [],
        'contrast_issues': [],
        'aria_usage': {},
        'suggestions': [],
    }

    issues = []

    # 1. Language attribute
    if html_content:
        has_lang = bool(re.search(r'<html[^>]*\slang\s*=\s*["\'][^"\']+["\']', html_content, re.IGNORECASE))
        if has_lang:
            result['passes'].append('HTML lang attribute present')
        else:
            issues.append('Missing lang attribute on <html> element')

    # 2. Document title
    if html_info:
        title = html_info.get('title', '')
        if title:
            result['passes'].append('Document has a title')
        else:
            issues.append('Missing document <title>')

    # 3. Heading hierarchy
    if html_info:
        headings = html_info.get('headings', [])
        heading_levels = [h[0] for h in headings]

        if not heading_levels:
            issues.append('No headings found. Use headings to create a hierarchical document structure.')
        else:
            if 1 not in heading_levels:
                issues.append('No <h1> heading found. Each page should have exactly one <h1>.')

            # Check for multiple h1
            h1_count = heading_levels.count(1)
            if h1_count > 1:
                issues.append('Multiple <h1> headings found ({}). Use only one <h1> per page.'.format(h1_count))

            # Check for skipped levels
            sorted_levels = sorted(set(heading_levels))
            for i in range(len(sorted_levels) - 1):
                if sorted_levels[i + 1] - sorted_levels[i] > 1:
                    issues.append('Heading level skipped: h{} to h{}. Use sequential heading levels.'.format(
                        sorted_levels[i], sorted_levels[i + 1]
                    ))
                    break

    # 4. Image alt text
    if html_info:
        images = html_info.get('images', [])
        if images:
            missing_alt = []
            for src, alt in images:
                if not alt:
                    missing_alt.append(src)

            if missing_alt:
                issues.append('{} of {} images missing alt text'.format(
                    len(missing_alt), len(images)
                ))
            else:
                result['passes'].append('All images have alt text')

    # 5. Link text quality
    if html_info:
        links = html_info.get('links', [])
        empty_links = sum(1 for link in links if not link.strip())
        generic_links = sum(1 for link in links if link.strip().lower() in (
            'click here', 'here', 'read more', 'more', 'link', '#'
        ))

        if empty_links > 0:
            issues.append('{} empty link(s) found'.format(empty_links))
        if generic_links > 0:
            issues.append('{} generic link text(s) found (e.g., "click here", "read more")'.format(
                generic_links
            ))

    # 6. Contrast analysis
    contrast_issues = _check_text_contrast(all_styles)
    result['contrast_issues'] = contrast_issues
    for ci in contrast_issues:
        issues.append(ci['message'])

    # 7. ARIA analysis
    if html_content:
        aria_result = _analyze_aria(html_content)
        result['aria_usage'] = aria_result
        if aria_result.get('missing_labels'):
            issues.append('Interactive elements without accessible labels: {}'.format(
                len(aria_result['missing_labels'])
            ))

    # 8. Form accessibility
    if html_info:
        forms = html_info.get('forms', [])
        if forms:
            if html_content:
                # Check for labels associated with inputs
                inputs = re.findall(r'<input[^>]+>', html_content, re.IGNORECASE)
                inputs_without_label = 0
                for inp in inputs:
                    inp_lower = inp.lower()
                    has_id = 'id=' in inp_lower
                    has_aria_label = 'aria-label' in inp_lower or 'aria-labelledby' in inp_lower
                    has_placeholder = 'placeholder=' in inp_lower
                    has_type_hidden = 'type="hidden"' in inp_lower or "type='hidden'" in inp_lower

                    if not has_type_hidden and not has_aria_label and not has_placeholder:
                        inputs_without_label += 1

                if inputs_without_label > 0:
                    issues.append('{} input(s) without labels or accessible names'.format(
                        inputs_without_label
                    ))

    # 9. Meta viewport (affects accessibility on mobile)
    if html_info:
        viewport = html_info.get('meta_viewport', '')
        if not viewport:
            issues.append('Missing viewport meta tag. Add <meta name="viewport" content="width=device-width, initial-scale=1.0">')

    # 10. Charset
    if html_info:
        charset = html_info.get('meta_charset', '')
        if not charset:
            issues.append('Missing charset declaration. Add <meta charset="UTF-8">')

    # Calculate score
    total_checks = len(result['passes']) + len(issues)
    if total_checks > 0:
        pass_ratio = len(result['passes']) / total_checks
        score = int(pass_ratio * 100)
    else:
        score = 50  # Neutral if nothing to check

    # Adjust for contrast issues severity
    if contrast_issues:
        fail_count = sum(1 for ci in contrast_issues if ci.get('wcag_level') == 'Fail')
        if fail_count > 3:
            score = max(0, score - 20)
        elif fail_count > 0:
            score = max(0, score - 10)

    result['score'] = max(0, min(100, score))
    result['issues'] = issues

    # Generate suggestions from issues
    for issue in issues:
        result['suggestions'].append({
            'message': issue,
            'priority': 'high' if any(kw in issue.lower() for kw in ['missing', 'fail', 'without']) else 'medium',
            'category': 'accessibility'
        })

    return result


def _check_text_contrast(all_styles):
    """
    Check text-to-background contrast ratios.
    Returns list of contrast issue dicts.
    """
    issues = []

    # Get color and background-color pairs
    color_values = get_property_values(all_styles, 'color')
    bg_values = get_property_values(all_styles, 'background-color')
    bg_shorthand = get_property_values(all_styles, 'background')

    fg_colors = []
    bg_colors = []

    for selector, value in color_values:
        parsed = parse_color(value)
        if parsed:
            fg_colors.append((selector, parsed))

    for selector, value in bg_values:
        parsed = parse_color(value)
        if parsed:
            bg_colors.append((selector, parsed))

    for selector, value in bg_shorthand:
        parsed = parse_color(value)
        if parsed:
            bg_colors.append((selector, parsed))

    if fg_colors and bg_colors:
        for fg_sel, fg_rgb in fg_colors:
            for bg_sel, bg_rgb in bg_colors:
                ratio = contrast_ratio(fg_rgb, bg_rgb)
                level = wcag_level(ratio)

                if level == 'Fail':
                    issues.append({
                        'selector': fg_sel,
                        'foreground': fg_rgb,
                        'background': bg_rgb,
                        'ratio': round(ratio, 2),
                        'wcag_level': level,
                        'message': 'Low contrast ({:.1f}:1) for "{}" text on background. '
                                   'WCAG AA requires 4.5:1 for normal text.'.format(ratio, fg_sel)
                    })
                elif level == 'A':
                    issues.append({
                        'selector': fg_sel,
                        'foreground': fg_rgb,
                        'background': bg_rgb,
                        'ratio': round(ratio, 2),
                        'wcag_level': level,
                        'message': 'Borderline contrast ({:.1f}:1) for "{}" text. '
                                   'Consider increasing for better readability.'.format(ratio, fg_sel)
                    })

    return issues


def _analyze_aria(html_content):
    """
    Analyze ARIA attribute usage in the HTML.
    Returns dict with ARIA statistics.
    """
    result = {
        'aria_labels': 0,
        'aria_labelledby': 0,
        'aria_describedby': 0,
        'aria_roles': 0,
        'aria_hidden': 0,
        'missing_labels': [],
    }

    # Count ARIA attributes
    result['aria_labels'] = len(re.findall(r'aria-label\s*=', html_content, re.IGNORECASE))
    result['aria_labelledby'] = len(re.findall(r'aria-labelledby\s*=', html_content, re.IGNORECASE))
    result['aria_describedby'] = len(re.findall(r'aria-describedby\s*=', html_content, re.IGNORECASE))
    result['aria_roles'] = len(re.findall(r'role\s*=', html_content, re.IGNORECASE))
    result['aria_hidden'] = len(re.findall(r'aria-hidden\s*=', html_content, re.IGNORECASE))

    # Check for interactive elements without labels
    # Buttons without text content or aria-label
    button_pattern = re.compile(r'<button[^>]*>(.*?)</button>', re.DOTALL | re.IGNORECASE)
    for match in button_pattern.finditer(html_content):
        button_tag = match.group(0)
        inner_text = match.group(1).strip()
        if not inner_text and 'aria-label' not in button_tag.lower():
            result['missing_labels'].append('button without label')

    # Check for <a> tags with empty text and no aria-label
    link_pattern = re.compile(r'<a\s+[^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
    for match in link_pattern.finditer(html_content):
        link_tag = match.group(0)
        inner_text = match.group(1).strip()
        href = re.search(r'href\s*=\s*["\']([^"\']+)["\']', link_tag, re.IGNORECASE)
        if href and href.group(1) != '#' and not inner_text and 'aria-label' not in link_tag.lower():
            result['missing_labels'].append('link without label')

    return result
