"""
color_utils.py - Color utility functions for DesignPulse-Engine.

Provides color parsing, conversion, and calculation utilities.
Supports hex, rgb, rgba, hsl, hsla, and named CSS colors.
Uses only Python standard library (colorsys, re).
"""

import colorsys
import re


# Standard CSS named colors mapped to RGB tuples
NAMED_COLORS = {
    "aliceblue": (240, 248, 255), "antiquewhite": (250, 235, 215),
    "aqua": (0, 255, 255), "aquamarine": (127, 255, 212),
    "azure": (240, 255, 255), "beige": (245, 245, 220),
    "bisque": (255, 228, 196), "black": (0, 0, 0),
    "blanchedalmond": (255, 235, 205), "blue": (0, 0, 255),
    "blueviolet": (138, 43, 226), "brown": (165, 42, 42),
    "burlywood": (222, 184, 135), "cadetblue": (95, 158, 160),
    "chartreuse": (127, 255, 0), "chocolate": (210, 105, 30),
    "coral": (255, 127, 80), "cornflowerblue": (100, 149, 237),
    "cornsilk": (255, 248, 220), "crimson": (220, 20, 60),
    "cyan": (0, 255, 255), "darkblue": (0, 0, 139),
    "darkcyan": (0, 139, 139), "darkgoldenrod": (184, 134, 11),
    "darkgray": (169, 169, 169), "darkgreen": (0, 100, 0),
    "darkgrey": (169, 169, 169), "darkkhaki": (189, 183, 107),
    "darkmagenta": (139, 0, 139), "darkolivegreen": (85, 107, 47),
    "darkorange": (255, 140, 0), "darkorchid": (153, 50, 204),
    "darkred": (139, 0, 0), "darksalmon": (233, 150, 122),
    "darkseagreen": (143, 188, 143), "darkslateblue": (72, 61, 139),
    "darkslategray": (47, 79, 79), "darkslategrey": (47, 79, 79),
    "darkturquoise": (0, 206, 209), "darkviolet": (148, 0, 211),
    "deeppink": (255, 20, 147), "deepskyblue": (0, 191, 255),
    "dimgray": (105, 105, 105), "dimgrey": (105, 105, 105),
    "dodgerblue": (30, 144, 255), "firebrick": (178, 34, 34),
    "floralwhite": (255, 250, 240), "forestgreen": (34, 139, 34),
    "fuchsia": (255, 0, 255), "gainsboro": (220, 220, 220),
    "ghostwhite": (248, 248, 255), "gold": (255, 215, 0),
    "goldenrod": (218, 165, 32), "gray": (128, 128, 128),
    "green": (0, 128, 0), "greenyellow": (173, 255, 47),
    "grey": (128, 128, 128), "honeydew": (240, 255, 240),
    "hotpink": (255, 105, 180), "indianred": (205, 92, 92),
    "indigo": (75, 0, 130), "ivory": (255, 255, 240),
    "khaki": (240, 230, 140), "lavender": (230, 230, 250),
    "lavenderblush": (255, 240, 245), "lawngreen": (124, 252, 0),
    "lemonchiffon": (255, 250, 205), "lightblue": (173, 216, 230),
    "lightcoral": (240, 128, 128), "lightcyan": (224, 255, 255),
    "lightgoldenrodyellow": (250, 250, 210), "lightgray": (211, 211, 211),
    "lightgreen": (144, 238, 144), "lightgrey": (211, 211, 211),
    "lightpink": (255, 182, 193), "lightsalmon": (255, 160, 122),
    "lightseagreen": (32, 178, 170), "lightskyblue": (135, 206, 250),
    "lightslategray": (119, 136, 153), "lightslategrey": (119, 136, 153),
    "lightsteelblue": (176, 196, 222), "lightyellow": (255, 255, 224),
    "lime": (0, 255, 0), "limegreen": (50, 205, 50),
    "linen": (250, 240, 230), "magenta": (255, 0, 255),
    "maroon": (128, 0, 0), "mediumaquamarine": (102, 205, 170),
    "mediumblue": (0, 0, 205), "mediumorchid": (186, 85, 211),
    "mediumpurple": (147, 111, 219), "mediumseagreen": (60, 179, 113),
    "mediumslateblue": (123, 104, 238), "mediumspringgreen": (0, 250, 154),
    "mediumturquoise": (72, 209, 204), "mediumvioletred": (199, 21, 133),
    "midnightblue": (25, 25, 112), "mintcream": (245, 255, 250),
    "mistyrose": (255, 228, 225), "moccasin": (255, 228, 181),
    "navajowhite": (255, 222, 173), "navy": (0, 0, 128),
    "oldlace": (253, 245, 230), "olive": (128, 128, 0),
    "olivedrab": (107, 142, 35), "orange": (255, 165, 0),
    "orangered": (255, 69, 0), "orchid": (218, 112, 214),
    "palegoldenrod": (238, 232, 170), "palegreen": (152, 251, 152),
    "paleturquoise": (175, 238, 238), "palevioletred": (219, 112, 147),
    "papayawhip": (255, 239, 213), "peachpuff": (255, 218, 185),
    "peru": (205, 133, 63), "pink": (255, 192, 203),
    "plum": (221, 160, 221), "powderblue": (176, 224, 230),
    "purple": (128, 0, 128), "rebeccapurple": (102, 51, 153),
    "red": (255, 0, 0), "rosybrown": (188, 143, 143),
    "royalblue": (65, 105, 225), "saddlebrown": (139, 69, 19),
    "salmon": (250, 128, 114), "sandybrown": (244, 164, 96),
    "seagreen": (46, 139, 87), "seashell": (255, 245, 238),
    "sienna": (160, 82, 45), "silver": (192, 192, 192),
    "skyblue": (135, 206, 235), "slateblue": (106, 90, 205),
    "slategray": (112, 128, 144), "slategrey": (112, 128, 144),
    "snow": (255, 250, 250), "springgreen": (0, 255, 127),
    "steelblue": (70, 130, 180), "tan": (210, 180, 140),
    "teal": (0, 128, 128), "thistle": (216, 191, 216),
    "tomato": (255, 99, 71), "turquoise": (64, 224, 208),
    "violet": (238, 130, 238), "wheat": (245, 222, 179),
    "white": (255, 255, 255), "whitesmoke": (245, 245, 245),
    "yellow": (255, 255, 0), "yellowgreen": (154, 205, 50),
    # Transparent keyword
    "transparent": (0, 0, 0),
    # Common aliases
    "initial": (0, 0, 0), "inherit": (0, 0, 0), "currentcolor": (0, 0, 0),
    "none": (0, 0, 0),
}


def parse_color(color_str):
    """
    Parse a CSS color string and return an (R, G, B) tuple with values 0-255.
    Supports hex (#RGB, #RRGGBB), rgb(), rgba(), hsl(), hsla(), and named colors.
    Returns None if the color cannot be parsed.
    """
    if not color_str or not isinstance(color_str, str):
        return None

    color_str = color_str.strip().lower()

    # Handle named colors
    if color_str in NAMED_COLORS:
        return NAMED_COLORS[color_str]

    # Handle hex colors: #RGB or #RRGGBB
    hex_match = re.match(r'^#([0-9a-f]{3,8})$', color_str)
    if hex_match:
        hex_val = hex_match.group(1)
        if len(hex_val) == 3:
            r = int(hex_val[0] * 2, 16)
            g = int(hex_val[1] * 2, 16)
            b = int(hex_val[2] * 2, 16)
            return (r, g, b)
        elif len(hex_val) == 6:
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
            return (r, g, b)
        elif len(hex_val) == 8:
            # #RRGGBBAA - ignore alpha for basic operations
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
            return (r, g, b)
        return None

    # Handle rgba() function
    rgba_match = re.match(
        r'rgba?\s*\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*(?:,\s*([\d.]+%?))?\s*\)',
        color_str
    )
    if rgba_match:
        r = _parse_color_component(rgba_match.group(1))
        g = _parse_color_component(rgba_match.group(2))
        b = _parse_color_component(rgba_match.group(3))
        if r is not None and g is not None and b is not None:
            return (r, g, b)

    # Handle hsl() / hsla() function
    hsl_match = re.match(
        r'hsla?\s*\(\s*(\d+\.?\d*)\s*,\s*(\d+\.?\d*)%?\s*,\s*(\d+\.?\d*)%?\s*(?:,\s*([\d.]+%?))?\s*\)',
        color_str
    )
    if hsl_match:
        h = float(hsl_match.group(1)) / 360.0
        s = float(hsl_match.group(2)) / 100.0
        l = float(hsl_match.group(3)) / 100.0
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))

    return None


def _parse_color_component(value):
    """Parse a single color component (supports percentage and absolute values)."""
    value = value.strip()
    if value.endswith('%'):
        return int(float(value[:-1]) * 255 / 100)
    else:
        return int(value)


def relative_luminance(rgb):
    """
    Calculate the relative luminance of a color per WCAG 2.0 specification.
    Input: (R, G, B) tuple with values 0-255.
    Returns: float luminance value.
    """
    if rgb is None:
        return 0.0

    r, g, b = [c / 255.0 for c in rgb]

    # Apply linearization for sRGB
    def linearize(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    r_lin = linearize(r)
    g_lin = linearize(g)
    b_lin = linearize(b)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(color1, color2):
    """
    Calculate the contrast ratio between two colors per WCAG 2.0.
    Input: two (R, G, B) tuples with values 0-255.
    Returns: contrast ratio (1:1 to 21:1).
    """
    lum1 = relative_luminance(color1)
    lum2 = relative_luminance(color2)

    if lum1 is None or lum2 is None:
        return 1.0

    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    if darker == 0:
        return (lighter + 0.05) / 0.05

    return (lighter + 0.05) / (darker + 0.05)


def wcag_level(ratio, size="normal"):
    """
    Determine WCAG compliance level for a given contrast ratio.
    size: "normal" for normal text, "large" for large text (18pt+ or 14pt bold+).
    Returns: "AAA", "AA", "A", or "Fail".
    """
    if size == "large":
        if ratio >= 7.0:
            return "AAA"
        elif ratio >= 4.5:
            return "AA"
        elif ratio >= 3.0:
            return "A"
    else:
        if ratio >= 7.0:
            return "AAA"
        elif ratio >= 4.5:
            return "AA"
        elif ratio >= 3.0:
            return "A"
    return "Fail"


def rgb_to_hsl(rgb):
    """
    Convert an (R, G, B) tuple to (H, S, L) values.
    Returns: (hue: 0-360, saturation: 0-100, lightness: 0-100).
    """
    if rgb is None:
        return (0, 0, 0)

    r, g, b = [c / 255.0 for c in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s * 100, l * 100)


def color_temperature(rgb):
    """
    Estimate the color temperature category of a color.
    Returns: "warm", "cool", "neutral", or "unknown".
    """
    if rgb is None:
        return "unknown"

    h, s, l = rgb_to_hsl(rgb)

    # Low saturation colors are neutral
    if s < 10:
        return "neutral"

    # Warm hues: reds, oranges, yellows (0-60, 300-360)
    if h <= 60 or h >= 300:
        return "warm"

    # Cool hues: blues, greens, purples (60-300)
    return "cool"


def color_distance(color1, color2):
    """
    Calculate the Euclidean distance between two colors in RGB space.
    Returns: float distance (0 = identical, ~441 = max distance).
    """
    if color1 is None or color2 is None:
        return 0.0

    return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5


def is_light_color(rgb):
    """
    Determine if a color is light (suitable for dark text overlay).
    Uses relative luminance threshold of 0.179 (approx #777).
    """
    if rgb is None:
        return True
    return relative_luminance(rgb) > 0.179


def is_dark_color(rgb):
    """Determine if a color is dark (suitable for light text overlay)."""
    if rgb is None:
        return False
    return relative_luminance(rgb) <= 0.179


def extract_colors_from_css(css_text):
    """
    Extract all color values from a CSS text string.
    Returns a list of (R, G, B) tuples.
    """
    colors = []

    # Match color properties
    color_props = re.findall(
        r'(?:color|background(?:-color)?|border-color|outline-color)\s*:\s*([^;}{]+)',
        css_text,
        re.IGNORECASE
    )

    # Also match shorthand background with color values
    bg_shorthand = re.findall(
        r'background\s*:\s*([^;}{]+)',
        css_text,
        re.IGNORECASE
    )

    all_values = color_props + bg_shorthand

    for value in all_values:
        # Try to extract color from the value (may contain other properties)
        # Look for hex colors
        hex_colors = re.findall(r'#[0-9a-fA-F]{3,8}', value)
        for hc in hex_colors:
            parsed = parse_color(hc)
            if parsed:
                colors.append(parsed)

        # Look for rgb/rgba
        rgb_colors = re.findall(
            r'rgba?\s*\([^)]+\)',
            value,
            re.IGNORECASE
        )
        for rc in rgb_colors:
            parsed = parse_color(rc)
            if parsed:
                colors.append(parsed)

        # Look for hsl/hsla
        hsl_colors = re.findall(
            r'hsla?\s*\([^)]+\)',
            value,
            re.IGNORECASE
        )
        for hc in hsl_colors:
            parsed = parse_color(hc)
            if parsed:
                colors.append(parsed)

        # Look for named colors (only if no other color found in this value)
        if not hex_colors and not rgb_colors and not hsl_colors:
            words = re.findall(r'[a-zA-Z]+', value)
            for word in words:
                parsed = parse_color(word)
                if parsed:
                    colors.append(parsed)

    return colors
