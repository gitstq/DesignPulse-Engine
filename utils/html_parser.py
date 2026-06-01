"""
html_parser.py - HTML parser utility for DesignPulse-Engine.

Parses HTML content using the standard library html.parser.
Extracts structural information, text content, and metadata.
"""

import re
from html.parser import HTMLParser


class DesignHTMLParser(HTMLParser):
    """
    Custom HTML parser that extracts structural information
    relevant to design quality analysis.
    """

    def __init__(self):
        super().__init__()
        # Document metadata
        self.title = ""
        self.meta_charset = ""
        self.meta_viewport = ""
        self.meta_description = ""
        self.has_doctype = False

        # Structural elements
        self.headings = []       # [(level, text), ...]
        self.paragraphs = []     # [text, ...]
        self.links = []          # [href, ...]
        self.images = []         # [(src, alt), ...]
        self.forms = []          # list of form dicts
        self.tables = []         # count of tables
        self.lists = []          # [(type, count), ...]

        # Element counts
        self.tag_counts = {}     # tag -> count
        self.total_tags = 0

        # Semantic elements
        self.semantic_elements = set()

        # Current state
        self._current_heading_level = 0
        self._current_heading_text = ""
        self._in_heading = False
        self._in_title = False
        self._in_style = False
        self._style_content = ""
        self._in_script = False
        self._current_list_type = None
        self._current_list_depth = 0
        self._list_stack = []

        # Semantic HTML5 tags
        self._semantic_tags = {
            'header', 'nav', 'main', 'article', 'section', 'aside',
            'footer', 'figure', 'figcaption', 'details', 'summary',
            'mark', 'time', 'progress', 'meter', 'dialog',
            'address', 'hgroup', 'search'
        }

    def handle_decl(self, decl):
        """Handle DOCTYPE declarations."""
        if 'DOCTYPE' in decl.upper() or 'html' in decl.lower():
            self.has_doctype = True

    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        tag = tag.lower()
        self.tag_counts[tag] = self.tag_counts.get(tag, 0) + 1
        self.total_tags += 1

        # Track semantic elements
        if tag in self._semantic_tags:
            self.semantic_elements.add(tag)

        # Handle <title>
        if tag == 'title':
            self._in_title = True

        # Handle headings
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._in_heading = True
            self._current_heading_level = int(tag[1])
            self._current_heading_text = ""

        # Handle <style>
        if tag == 'style':
            self._in_style = True
            self._style_content = ""

        # Handle <script>
        if tag == 'script':
            self._in_script = True

        # Handle <a>
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href:
                self.links.append(href)

        # Handle <img>
        if tag == 'img':
            attr_dict = dict(attrs)
            src = attr_dict.get('src', '')
            alt = attr_dict.get('alt', '')
            self.images.append((src, alt))

        # Handle <form>
        if tag == 'form':
            attr_dict = dict(attrs)
            self.forms.append({
                'action': attr_dict.get('action', ''),
                'method': attr_dict.get('method', 'get').upper()
            })

        # Handle <table>
        if tag == 'table':
            self.tables.append(1)

        # Handle <meta>
        if tag == 'meta':
            attr_dict = dict(attrs)
            charset = attr_dict.get('charset', '')
            if charset:
                self.meta_charset = charset
            name = attr_dict.get('name', '').lower()
            content = attr_dict.get('content', '')
            if name == 'viewport':
                self.meta_viewport = content
            elif name == 'description':
                self.meta_description = content

        # Handle lists
        if tag in ('ul', 'ol'):
            self._list_stack.append(tag)

    def handle_endtag(self, tag):
        """Handle closing tags."""
        tag = tag.lower()

        if tag == 'title':
            self._in_title = False

        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._in_heading = False
            text = self._current_heading_text.strip()
            if text:
                self.headings.append((self._current_heading_level, text))

        if tag == 'style':
            self._in_style = False

        if tag == 'script':
            self._in_script = False

        if tag in ('ul', 'ol'):
            if self._list_stack:
                list_type = self._list_stack.pop()
                self.lists.append(list_type)

    def handle_data(self, data):
        """Handle text data."""
        if self._in_title:
            self.title += data

        if self._in_heading:
            self._current_heading_text += data

        if self._in_style:
            self._style_content += data

        # Collect paragraph text (rough heuristic: text in <p> tags)
        # We handle this via starttag detection

    def handle_startendtag(self, tag, attrs):
        """Handle self-closing tags (XHTML style)."""
        self.handle_starttag(tag, attrs)

    def error(self, message):
        """Handle parse errors gracefully."""
        pass  # Silently ignore parse errors


def parse_html(html_content):
    """
    Parse HTML content and return a structured analysis result.
    Returns a dictionary with document structure information.
    """
    parser = DesignHTMLParser()

    try:
        parser.feed(html_content)
    except Exception:
        pass  # Gracefully handle any parsing errors

    return {
        'title': parser.title.strip(),
        'has_doctype': parser.has_doctype,
        'meta_charset': parser.meta_charset,
        'meta_viewport': parser.meta_viewport,
        'meta_description': parser.meta_description,
        'headings': parser.headings,
        'heading_count': len(parser.headings),
        'links': parser.links,
        'link_count': len(parser.links),
        'images': parser.images,
        'image_count': len(parser.images),
        'forms': parser.forms,
        'form_count': len(parser.forms),
        'table_count': len(parser.tables),
        'lists': parser.lists,
        'list_count': len(parser.lists),
        'tag_counts': parser.tag_counts,
        'total_tags': parser.total_tags,
        'semantic_elements': parser.semantic_elements,
        'semantic_count': len(parser.semantic_elements),
    }


def extract_text_content(html_content):
    """
    Extract visible text content from HTML (strip all tags).
    Returns cleaned text string.
    """
    # Remove script and style content first
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode common HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def count_text_elements(html_content):
    """
    Count various text-containing elements in the HTML.
    Returns dict with counts of p, span, div, li, td, th, label, button, etc.
    """
    text_tags = ['p', 'span', 'div', 'li', 'td', 'th', 'label',
                 'button', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                 'blockquote', 'pre', 'code', 'strong', 'em', 'b', 'i',
                 'figcaption', 'caption', 'dt', 'dd']

    counts = {}
    for tag in text_tags:
        pattern = re.compile(r'<{}[\s>]'.format(tag), re.IGNORECASE)
        counts[tag] = len(pattern.findall(html_content))

    return counts
