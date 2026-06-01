#!/usr/bin/env python3
"""
DesignPulse-Engine - Design Pulse Engine

A lightweight zero-dependency terminal AI content design quality
detection and optimization engine.

Usage:
    python designpulse.py analyze <file>
    python designpulse.py batch <directory>
    python designpulse.py score <file>
    python designpulse.py report <file> --format json|markdown
    python designpulse.py colors <file>
    python designpulse.py typography <file>
    python designpulse.py accessibility <file>
"""

import argparse
import os
import sys

# Ensure the project root is in the Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from core.analyzer import (
    analyze_file,
    analyze_content,
    analyze_colors_only,
    analyze_typography_only,
    analyze_accessibility_only,
)
from utils.report import (
    format_terminal_report,
    generate_json_report,
    generate_markdown_report,
    generate_batch_summary,
    save_report,
)


def cmd_analyze(args):
    """Handle the 'analyze' command - full analysis of a single file."""
    filepath = args.file

    if not os.path.isfile(filepath):
        print("Error: File not found: {}".format(filepath))
        sys.exit(1)

    result = analyze_file(filepath)

    if 'error' in result:
        print("Error: {}".format(result['error']))
        sys.exit(1)

    # Print terminal report
    report = format_terminal_report(result)
    print(report)

    return result


def cmd_batch(args):
    """Handle the 'batch' command - analyze all HTML files in a directory."""
    directory = args.directory

    if not os.path.isdir(directory):
        print("Error: Directory not found: {}".format(directory))
        sys.exit(1)

    # Find all HTML files
    html_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.html', '.htm')):
            html_files.append(os.path.join(directory, filename))

    if not html_files:
        print("No HTML files found in: {}".format(directory))
        sys.exit(1)

    html_files.sort()

    # Analyze each file
    results = []
    for filepath in html_files:
        result = analyze_file(filepath)
        if 'error' not in result:
            results.append(result)

    # Print batch summary
    summary = generate_batch_summary(results)
    print(summary)

    # Optionally save individual reports
    if args.output:
        for result in results:
            filename = result.get('file_info', {}).get('filename', 'unknown')
            report_filename = filename.rsplit('.', 1)[0] + '_report.json'
            report_path = os.path.join(args.output, report_filename)
            json_report = generate_json_report(result)
            save_report(json_report, report_path)

        print("  Individual reports saved to: {}".format(args.output))

    return results


def cmd_score(args):
    """Handle the 'score' command - quick scoring of a single file."""
    filepath = args.file

    if not os.path.isfile(filepath):
        print("Error: File not found: {}".format(filepath))
        sys.exit(1)

    result = analyze_file(filepath)

    if 'error' in result:
        print("Error: {}".format(result['error']))
        sys.exit(1)

    # Print only the score
    score = result.get('overall_score', 0)
    grade = result.get('grade', 'N/A')
    filename = result.get('file_info', {}).get('filename', 'unknown')

    print("DesignPulse Score: {} / 100 [{}] - {}".format(score, grade, filename))

    return result


def cmd_report(args):
    """Handle the 'report' command - generate a detailed report file."""
    filepath = args.file
    fmt = args.format.lower()

    if not os.path.isfile(filepath):
        print("Error: File not found: {}".format(filepath))
        sys.exit(1)

    result = analyze_file(filepath)

    if 'error' in result:
        print("Error: {}".format(result['error']))
        sys.exit(1)

    # Generate report in requested format
    if fmt == 'json':
        report_content = generate_json_report(result)
        ext = '.json'
    elif fmt == 'markdown' or fmt == 'md':
        report_content = generate_markdown_report(result)
        ext = '.md'
    else:
        print("Error: Unsupported format '{}'. Use 'json' or 'markdown'.".format(fmt))
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        basename = os.path.basename(filepath).rsplit('.', 1)[0]
        output_path = os.path.join(os.path.dirname(filepath) or '.', basename + '_report' + ext)

    # Save report
    saved_path = save_report(report_content, output_path)
    if saved_path:
        print("Report saved to: {}".format(saved_path))
    else:
        print("Error: Failed to save report to: {}".format(output_path))
        sys.exit(1)

    # Also print terminal summary
    print("")
    terminal_report = format_terminal_report(result)
    print(terminal_report)

    return result


def cmd_colors(args):
    """Handle the 'colors' command - analyze color scheme only."""
    filepath = args.file

    if not os.path.isfile(filepath):
        print("Error: File not found: {}".format(filepath))
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    result = analyze_colors_only(html_content, filepath)

    # Print color analysis
    print("")
    print("=" * 60)
    print("  DesignPulse-Engine - Color Scheme Analysis")
    print("=" * 60)
    print("")

    print("  Unique colors: {}".format(result.get('unique_color_count', 0)))
    print("  Harmony score: {}/100".format(result.get('harmony_score', 0)))
    print("  Contrast score: {}/100".format(result.get('contrast_score', 0)))
    print("  Avg contrast ratio: {:.1f}:1".format(result.get('avg_contrast_ratio', 0)))
    print("")

    wcag = result.get('wcag_summary', {})
    if wcag:
        print("  WCAG Compliance:")
        for level, count in wcag.items():
            print("    {}: {} pairs".format(level, count))
        print("")

    suggestions = result.get('suggestions', [])
    if suggestions:
        print("  Suggestions:")
        for s in suggestions:
            print("    - {}".format(s.get('message', '')))
        print("")

    print("=" * 60)
    print("")

    return result


def cmd_typography(args):
    """Handle the 'typography' command - analyze typography only."""
    filepath = args.file

    if not os.path.isfile(filepath):
        print("Error: File not found: {}".format(filepath))
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    result = analyze_typography_only(html_content, filepath)

    print("")
    print("=" * 60)
    print("  DesignPulse-Engine - Typography Analysis")
    print("=" * 60)
    print("")

    font_families = result.get('font_families', [])
    print("  Font families ({}):".format(len(font_families)))
    for ff in font_families[:10]:
        print("    - {}".format(ff))
    print("")

    print("  Font size range: {}".format(result.get('size_range', 'N/A')))
    print("  Line height range: {}".format(result.get('line_height_range', 'N/A')))
    print("  Typography score: {}/100".format(result.get('score', 0)))
    print("")

    suggestions = result.get('suggestions', [])
    if suggestions:
        print("  Suggestions:")
        for s in suggestions:
            print("    - {}".format(s.get('message', '')))
        print("")

    print("=" * 60)
    print("")

    return result


def cmd_accessibility(args):
    """Handle the 'accessibility' command - analyze accessibility only."""
    filepath = args.file

    if not os.path.isfile(filepath):
        print("Error: File not found: {}".format(filepath))
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    result = analyze_accessibility_only(html_content, filepath)

    print("")
    print("=" * 60)
    print("  DesignPulse-Engine - Accessibility Analysis")
    print("=" * 60)
    print("")

    print("  Accessibility score: {}/100".format(result.get('score', 0)))
    print("")

    passes = result.get('passes', [])
    if passes:
        print("  Passes:")
        for p in passes:
            print("    [OK] {}".format(p))
        print("")

    issues = result.get('issues', [])
    if issues:
        print("  Issues ({}):".format(len(issues)))
        for issue in issues:
            print("    [!] {}".format(issue))
        print("")

    contrast_issues = result.get('contrast_issues', [])
    if contrast_issues:
        print("  Contrast Issues ({}):".format(len(contrast_issues)))
        for ci in contrast_issues[:5]:
            print("    [!] Ratio {:.1f}:1 ({}) - {}".format(
                ci.get('ratio', 0), ci.get('wcag_level', ''), ci.get('selector', '')
            ))
        print("")

    print("=" * 60)
    print("")

    return result


def main():
    """Main entry point for the DesignPulse-Engine CLI."""
    parser = argparse.ArgumentParser(
        prog='designpulse',
        description='DesignPulse-Engine - Lightweight terminal AI content design quality detection and optimization engine.',
        epilog='Example: python designpulse.py analyze index.html'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # analyze command
    parser_analyze = subparsers.add_parser('analyze', help='Full design quality analysis of an HTML file')
    parser_analyze.add_argument('file', help='Path to HTML file')
    parser_analyze.set_defaults(func=cmd_analyze)

    # batch command
    parser_batch = subparsers.add_parser('batch', help='Batch analyze all HTML files in a directory')
    parser_batch.add_argument('directory', help='Path to directory containing HTML files')
    parser_batch.add_argument('-o', '--output', help='Output directory for individual reports')
    parser_batch.set_defaults(func=cmd_batch)

    # score command
    parser_score = subparsers.add_parser('score', help='Quick scoring of an HTML file')
    parser_score.add_argument('file', help='Path to HTML file')
    parser_score.set_defaults(func=cmd_score)

    # report command
    parser_report = subparsers.add_parser('report', help='Generate a detailed report file')
    parser_report.add_argument('file', help='Path to HTML file')
    parser_report.add_argument('-f', '--format', choices=['json', 'markdown'], default='json',
                               help='Report format (default: json)')
    parser_report.add_argument('-o', '--output', help='Output file path')
    parser_report.set_defaults(func=cmd_report)

    # colors command
    parser_colors = subparsers.add_parser('colors', help='Analyze color scheme only')
    parser_colors.add_argument('file', help='Path to HTML file')
    parser_colors.set_defaults(func=cmd_colors)

    # typography command
    parser_typography = subparsers.add_parser('typography', help='Analyze typography only')
    parser_typography.add_argument('file', help='Path to HTML file')
    parser_typography.set_defaults(func=cmd_typography)

    # accessibility command
    parser_a11y = subparsers.add_parser('accessibility', help='Analyze accessibility only')
    parser_a11y.add_argument('file', help='Path to HTML file')
    parser_a11y.set_defaults(func=cmd_accessibility)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
