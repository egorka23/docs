#!/usr/bin/env python3
"""
QA lint script for success stories cases.
Fails if cases contain garbage patterns.
"""

import json
import re
import sys
from pathlib import Path

# Patterns that should FAIL the lint
FAIL_PATTERNS = [
    r'\[name\]',           # Placeholder
    r'\*\*',               # Markdown bold
    r'^#\w+',              # Hashtag at start
]

# Titles that should FAIL
FAIL_TITLES = [
    'eb-1a кейс',
    'eb-2 niw кейс',
    'niw кейс',
    'o-1 кейс',
    'o-1a кейс',
    'o-1b кейс',
    'eb-1a',
    'eb-2 niw',
    'o-1',
]

# Patterns that trigger WARNING
WARN_PATTERNS = [
    r'^\s*(привет|ура|здравствуй)',
    r'\[имя\]',
    r'\[ссылка\]',
]


def lint_case(case: dict) -> tuple[list, list]:
    """Lint a single case. Returns (errors, warnings)."""
    errors = []
    warnings = []

    case_id = case.get('id', 'unknown')
    title = case.get('title', '')
    context = case.get('context', '')
    summary = case.get('summary', '')

    # Check FAIL patterns in all text fields
    for field_name, field_value in [('title', title), ('context', context), ('summary', summary)]:
        for pattern in FAIL_PATTERNS:
            if re.search(pattern, field_value, re.IGNORECASE):
                errors.append(f"{case_id}: {field_name} contains '{pattern}'")

    # Check FAIL titles
    title_lower = title.lower().strip()
    if title_lower in FAIL_TITLES:
        errors.append(f"{case_id}: title is generic stop-phrase '{title}'")

    # Check WARNING patterns
    for field_name, field_value in [('title', title), ('context', context)]:
        for pattern in WARN_PATTERNS:
            if re.search(pattern, field_value, re.IGNORECASE):
                warnings.append(f"{case_id}: {field_name} matches warning pattern '{pattern}'")

    # Check if summary == context (too similar)
    if summary and context:
        s1 = re.sub(r'\W+', '', summary.lower())
        s2 = re.sub(r'\W+', '', context.lower())
        if s1 == s2 or (len(s1) > 10 and s1 in s2):
            warnings.append(f"{case_id}: summary equals context")

    # Check empty/very short content
    if len(context.strip()) < 20:
        warnings.append(f"{case_id}: context too short ({len(context)} chars)")

    if len(title.strip()) < 5:
        errors.append(f"{case_id}: title too short ({len(title)} chars)")

    return errors, warnings


def lint_all_cases(input_path: str) -> tuple[list, list]:
    """Lint all cases. Returns (all_errors, all_warnings)."""
    with open(input_path) as f:
        data = json.load(f)

    all_errors = []
    all_warnings = []

    for case in data['cases']:
        errors, warnings = lint_case(case)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    return all_errors, all_warnings


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else '/Users/aeb/mintlify-docs/data/cases.json'

    print(f"Linting {input_path}...")
    errors, warnings = lint_all_cases(input_path)

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        print(f"\nLint FAILED with {len(errors)} errors")
        sys.exit(1)
    else:
        print(f"\n✅ Lint passed! ({len(warnings)} warnings)")
        sys.exit(0)


if __name__ == '__main__':
    main()
