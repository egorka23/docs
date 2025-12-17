#!/usr/bin/env python3
"""
Update navigation labels in docs.json with case counts from data/cases.json.

Source of truth: data/cases.json

Counts:
  - premium_count: cases where premium == true
  - self_count: cases where prep == "self"
  - rfe_count: cases where rfe == true
  - vsc_count: cases where service_center == "VSC"
  - nsc_count: cases where service_center == "NSC"

Updates docs.json navigation:
  - "success-stories/premium" -> label "Premium (X)"
  - "success-stories/self-prepared" -> label "Самоподача (X)"
  - "success-stories/with-rfe" -> label "С RFE (X)"
  - "success-stories/by-center/vermont" -> label "Vermont (VSC) (X)"
  - "success-stories/by-center/nebraska" -> label "Nebraska (NSC) (X)"

Idempotent: re-running correctly updates numbers.

Usage:
  python3 scripts/update_success_stories_nav_counts.py
"""

import json
import re
from pathlib import Path


def load_cases(cases_path: Path) -> list[dict]:
    """Load cases from JSON file."""
    with open(cases_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('cases', [])


def count_cases(cases: list[dict]) -> dict[str, int]:
    """Count cases by different criteria."""
    counts = {
        'premium': 0,
        'self': 0,
        'rfe': 0,
        'vsc': 0,
        'nsc': 0,
    }

    for case in cases:
        if case.get('premium') is True:
            counts['premium'] += 1
        if case.get('prep') == 'self':
            counts['self'] += 1
        if case.get('rfe') is True:
            counts['rfe'] += 1
        if case.get('service_center') == 'VSC':
            counts['vsc'] += 1
        if case.get('service_center') == 'NSC':
            counts['nsc'] += 1

    return counts


def strip_count_suffix(label: str) -> str:
    """Remove existing count suffix like ' (12)' from label."""
    return re.sub(r'\s*\(\d+\)\s*$', '', label)


def update_navigation(docs: dict, counts: dict[str, int]) -> dict:
    """Update navigation labels with counts."""

    # Mapping: page path -> (base_label, count_key)
    page_config = {
        'success-stories/premium': ('Premium', 'premium'),
        'success-stories/self-prepared': ('Самоподача', 'self'),
        'success-stories/with-rfe': ('С RFE', 'rfe'),
        'success-stories/by-center/vermont': ('Vermont (VSC)', 'vsc'),
        'success-stories/by-center/nebraska': ('Nebraska (NSC)', 'nsc'),
    }

    def process_pages(pages: list) -> list:
        """Recursively process pages list."""
        result = []
        for item in pages:
            if isinstance(item, str):
                # Simple string page reference
                if item in page_config:
                    base_label, count_key = page_config[item]
                    result.append({
                        'page': item,
                        'title': f"{base_label} ({counts[count_key]})"
                    })
                else:
                    result.append(item)
            elif isinstance(item, dict):
                if 'page' in item:
                    # Page object - update title if needed
                    page_path = item['page']
                    if page_path in page_config:
                        base_label, count_key = page_config[page_path]
                        item = item.copy()
                        item['title'] = f"{base_label} ({counts[count_key]})"
                    result.append(item)
                elif 'group' in item:
                    # Nested group
                    new_item = item.copy()
                    if 'pages' in item:
                        new_item['pages'] = process_pages(item['pages'])
                    result.append(new_item)
                else:
                    result.append(item)
            else:
                result.append(item)
        return result

    # Process navigation structure
    if 'navigation' in docs:
        nav = docs['navigation']
        if 'tabs' in nav:
            for tab in nav['tabs']:
                if 'groups' in tab:
                    for group in tab['groups']:
                        if 'pages' in group:
                            group['pages'] = process_pages(group['pages'])

    return docs


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    cases_path = project_root / 'data' / 'cases.json'
    docs_path = project_root / 'docs.json'

    print("📊 Loading cases from data/cases.json...")
    cases = load_cases(cases_path)
    print(f"   Found {len(cases)} cases\n")

    print("🔢 Counting cases...")
    counts = count_cases(cases)
    for key, count in counts.items():
        print(f"   {key}: {count}")
    print()

    print("📝 Updating docs.json navigation...")
    with open(docs_path, 'r', encoding='utf-8') as f:
        docs = json.load(f)

    docs = update_navigation(docs, counts)

    with open(docs_path, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
        f.write('\n')

    print("✅ Updated docs.json with nav counts:")
    print(f"   - Premium ({counts['premium']})")
    print(f"   - Самоподача ({counts['self']})")
    print(f"   - С RFE ({counts['rfe']})")
    print(f"   - Vermont (VSC) ({counts['vsc']})")
    print(f"   - Nebraska (NSC) ({counts['nsc']})")


if __name__ == '__main__':
    main()
