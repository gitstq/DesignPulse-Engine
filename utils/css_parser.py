"""
css_parser.py - CSS parser utility for DesignPulse-Engine.

Parses CSS from inline styles and <style> tags using regex.
Extracts selectors, properties, and values into structured data.
"""

import re


def parse_inline_style(style_str):
    """
    Parse an inline style attribute string into a dictionary.
    Example: "color: red; font-size: 16px;" -> {"color": "red", "font-size": "16px"}
    """
    if not style_str:
        return {}

    props = {}
    # Split by semicolon, then by colon
    declarations = style_str.split(';')
    for decl in declarations:
        decl = decl.strip()
        if ':' in decl:
            prop, _, value = decl.partition(':')
            prop = prop.strip().lower()
            value = value.strip()
            if prop and value:
                props[prop] = value

    return props


def parse_style_tags(html_content):
    """
    Extract all CSS content from <style> tags in HTML.
    Returns a list of CSS text strings.
    """
    style_pattern = re.compile(
        r'<style[^>]*>(.*?)</style>',
        re.DOTALL | re.IGNORECASE
    )
    matches = style_pattern.findall(html_content)
    return matches


def parse_css_rules(css_text):
    """
    Parse CSS text into a list of rule dictionaries.
    Each rule has 'selector' and 'declarations' (dict of property -> value).

    Handles simple CSS rules. Does not fully support:
    - @media queries (extracted but nested rules not parsed)
    - @keyframes
    - Complex selectors with combinators (stored as-is)
    """
    if not css_text:
        return []

    rules = []

    # Remove comments
    css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)

    # Remove @import and @charset directives
    css_text = re.sub(r'@import[^;]+;', '', css_text)
    css_text = re.sub(r'@charset[^;]+;', '', css_text)

    # Extract @media queries for responsive analysis
    media_queries = re.findall(
        r'@media\s*([^{]+)\{([^@]+)\}',
        css_text,
        re.DOTALL
    )

    # Parse rules outside of @media blocks
    # Remove @media blocks from the main CSS for separate parsing
    css_without_media = re.sub(r'@media\s*[^{]+\{[^@]+\}', '', css_text, flags=re.DOTALL)

    # Parse regular rules
    rule_pattern = re.compile(
        r'([^{}]+)\{([^{}]*)\}',
        re.DOTALL
    )
    matches = rule_pattern.findall(css_without_media)

    for selector_str, declarations_str in matches:
        selector = selector_str.strip()
        declarations = parse_declarations(declarations_str)
        if selector and declarations:
            rules.append({
                'selector': selector,
                'declarations': declarations,
                'type': 'regular'
            })

    # Parse @media query rules
    for media_condition, media_body in media_queries:
        media_rules = rule_pattern.findall(media_body)
        for selector_str, declarations_str in media_rules:
            selector = selector_str.strip()
            declarations = parse_declarations(declarations_str)
            if selector and declarations:
                rules.append({
                    'selector': selector,
                    'declarations': declarations,
                    'type': 'media',
                    'condition': media_condition.strip()
                })

    return rules


def parse_declarations(declarations_str):
    """
    Parse a CSS declarations block into a dictionary.
    Handles multiple values for the same property by keeping the last one.
    """
    props = {}
    declarations = declarations_str.split(';')
    for decl in declarations:
        decl = decl.strip()
        if ':' in decl:
            prop, _, value = decl.partition(':')
            prop = prop.strip().lower()
            value = value.strip()
            if prop and value:
                # Remove !important for analysis purposes
                value = re.sub(r'!\s*important', '', value, flags=re.IGNORECASE).strip()
                props[prop] = value

    return props


def extract_all_styles(html_content):
    """
    Extract all styles from an HTML document.
    Returns a dict with:
      - 'inline': list of (element_tag, style_dict) tuples
      - 'style_tags': list of CSS rule dicts
      - 'raw_css': list of raw CSS text strings
    """
    result = {
        'inline': [],
        'style_tags': [],
        'raw_css': []
    }

    # Extract inline styles
    inline_pattern = re.compile(
        r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*style\s*=\s*["\']([^"\']*)["\'][^>]*>',
        re.IGNORECASE
    )
    for match in inline_pattern.finditer(html_content):
        tag = match.group(1).lower()
        style_str = match.group(2)
        style_dict = parse_inline_style(style_str)
        if style_dict:
            result['inline'].append((tag, style_dict))

    # Extract <style> tag content
    raw_css_list = parse_style_tags(html_content)
    result['raw_css'] = raw_css_list

    # Parse CSS rules from style tags
    for css_text in raw_css_list:
        rules = parse_css_rules(css_text)
        result['style_tags'].extend(rules)

    return result


def get_property_values(all_styles, property_name):
    """
    Get all values for a specific CSS property across all styles.
    Returns a list of (selector_or_tag, value) tuples.
    """
    values = []

    for tag, style_dict in all_styles.get('inline', []):
        if property_name in style_dict:
            values.append((tag, style_dict[property_name]))

    for rule in all_styles.get('style_tags', []):
        if property_name in rule.get('declarations', {}):
            values.append((rule.get('selector', ''), rule['declarations'][property_name]))

    return values


def get_media_queries(all_styles):
    """
    Extract all @media query conditions from parsed styles.
    Returns a list of media condition strings.
    """
    queries = []
    for rule in all_styles.get('style_tags', []):
        if rule.get('type') == 'media':
            queries.append(rule.get('condition', ''))

    return queries


def count_selectors(all_styles):
    """
    Count the number of unique CSS selectors used.
    Returns: (total_selectors, unique_selectors, inline_count)
    """
    selectors = set()
    inline_count = len(all_styles.get('inline', []))

    for rule in all_styles.get('style_tags', []):
        sel = rule.get('selector', '')
        if sel:
            selectors.add(sel)

    total = inline_count + len(selectors)
    return (total, len(selectors), inline_count)
