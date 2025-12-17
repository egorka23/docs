#!/usr/bin/env python3
"""
Update sidebar titles in success-stories MDX files with case counts.

Source of truth: data/cases.json

Counts:
  - premium_count: cases where premium == true
  - self_count: cases where prep == "self"
  - rfe_count: cases where rfe == true
  - vsc_count: cases where service_center == "VSC"
  - nsc_count: cases where service_center == "NSC"

Updates:
  - success-stories/premium.mdx: "Premium (X)"
  - success-stories/self-prepared.mdx: "Самоподача (X)"
  - success-stories/with-rfe.mdx: "С RFE (X)"
  - success-stories/by-center/vermont.mdx: "Vermont (X)"
  - success-stories/by-center/nebraska.mdx: "Nebraska (X)"
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
        # Premium: cases where premium == true
        if case.get('premium') is True:
            counts['premium'] += 1

        # Self-prepared: cases where prep == "self"
        if case.get('prep') == 'self':
            counts['self'] += 1

        # RFE: cases where rfe == true
        if case.get('rfe') is True:
            counts['rfe'] += 1

        # VSC: cases where service_center == "VSC"
        if case.get('service_center') == 'VSC':
            counts['vsc'] += 1

        # NSC: cases where service_center == "NSC"
        if case.get('service_center') == 'NSC':
            counts['nsc'] += 1

    return counts


def update_sidebar_title(file_path: Path, new_title: str) -> bool:
    """Update sidebarTitle in MDX frontmatter."""
    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False

    content = file_path.read_text(encoding='utf-8')

    # Match sidebarTitle in frontmatter
    pattern = r'^(sidebarTitle:\s*["\'])([^"\']+)(["\'])$'

    def replacer(match):
        quote_start = match.group(1)
        quote_end = match.group(3)
        return f'{quote_start}{new_title}{quote_end}'

    new_content, count = re.subn(pattern, replacer, content, flags=re.MULTILINE)

    if count == 0:
        print(f"  ⚠️  No sidebarTitle found in: {file_path}")
        return False

    file_path.write_text(new_content, encoding='utf-8')
    return True


def main():
    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    cases_path = project_root / 'data' / 'cases.json'

    # Define files to update with their new title templates
    files_config = {
        'premium': {
            'path': project_root / 'success-stories' / 'premium.mdx',
            'template': 'Premium ({count})',
        },
        'self': {
            'path': project_root / 'success-stories' / 'self-prepared.mdx',
            'template': 'Самоподача ({count})',
        },
        'rfe': {
            'path': project_root / 'success-stories' / 'with-rfe.mdx',
            'template': 'С RFE ({count})',
        },
        'vsc': {
            'path': project_root / 'success-stories' / 'by-center' / 'vermont.mdx',
            'template': 'Vermont ({count})',
        },
        'nsc': {
            'path': project_root / 'success-stories' / 'by-center' / 'nebraska.mdx',
            'template': 'Nebraska ({count})',
        },
    }

    print("📊 Loading cases from data/cases.json...")
    cases = load_cases(cases_path)
    print(f"   Found {len(cases)} cases\n")

    print("🔢 Counting cases...")
    counts = count_cases(cases)
    for key, count in counts.items():
        print(f"   {key}: {count}")
    print()

    print("📝 Updating sidebarTitles...")
    updated = 0
    for key, config in files_config.items():
        new_title = config['template'].format(count=counts[key])
        rel_path = config['path'].relative_to(project_root)
        print(f"   {rel_path}: \"{new_title}\"")
        if update_sidebar_title(config['path'], new_title):
            updated += 1

    print(f"\n✅ Updated {updated}/{len(files_config)} files")


if __name__ == '__main__':
    main()
