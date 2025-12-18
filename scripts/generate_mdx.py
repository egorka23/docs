#!/usr/bin/env python3
"""
Generate MDX pages for success stories with quality gate.
"""

import json
import re
from pathlib import Path
from clean_cases import clean_text, is_title_garbage, generate_title, extract_summary, is_context_duplicate

BASE_DIR = Path('/Users/aeb/mintlify-docs')
DATA_PATH = BASE_DIR / 'data' / 'cases.json'
STORIES_DIR = BASE_DIR / 'success-stories'


def get_icon(field: str, visa: str) -> str:
    """Get appropriate icon for case."""
    icons = {
        'IT': 'laptop-code',
        'Наука': 'flask',
        'Искусство': 'palette',
        'Бизнес': 'briefcase',
        'Музыка': 'music',
        'Спорт': 'person-running',
        'Мода': 'shirt',
        'Медицина': 'heart-pulse',
        'Маркетинг': 'chart-line',
        'Архитектура': 'building',
    }
    if field in icons:
        return icons[field]
    if 'O-1' in visa:
        return 'bolt'
    if visa == 'EB-2 NIW':
        return 'lightbulb'
    return 'star'


def make_accordion(case: dict) -> str:
    """Generate accordion MDX for a case."""
    visa = case.get('visa', 'EB-1A')
    field = case.get('field', '')

    # Clean and generate title
    title = clean_text(case.get('title', ''))
    if is_title_garbage(title):
        title = generate_title(case)
    title = title[:55]

    icon = get_icon(field, visa)

    # Clean context
    context = clean_text(case.get('context', ''))

    # Generate summary
    summary = extract_summary(context, case)

    # Build tags
    tags = [f'<code>{visa}</code>']
    if field:
        tags.append(f'<code>{field}</code>')
    if case.get('rfe'):
        tags.append('<code>RFE</code>')
    if case.get('premium'):
        tags.append('<code>premium</code>')
    if case.get('prep') == 'self':
        tags.append('<code>самоподача</code>')
    if case.get('service_center'):
        tags.append(f'<code>{case["service_center"]}</code>')

    # Check if context should be shown
    show_context = (
        context and
        len(context) >= 30 and
        not is_context_duplicate(summary, context)
    )

    # Build accordion
    accordion = f'''  <Accordion title="{title}" icon="{icon}">
    **Итог:** {summary}

    <div style={{{{display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px'}}}}>
      {' '.join(tags)}
    </div>
'''

    if show_context:
        accordion += f'''
    ### Контекст
    {context[:350]}
'''

    accordion += '\n  </Accordion>'
    return accordion


def generate_cases_preview(cases: list) -> str:
    """Generate cases-preview.mdx content."""
    eb1a = [c for c in cases if c.get('visa') == 'EB-1A']
    eb2 = [c for c in cases if c.get('visa') == 'EB-2 NIW']
    o1 = [c for c in cases if c.get('visa', '').startswith('O-1')]
    total = len(cases)

    output = f'''---
title: "Все истории успеха"
sidebarTitle: "Все истории ({total})"
description: "Все {total} реальных кейсов из сообщества."
icon: "grid-2"
---

<Note>
**{total} кейсов** из Telegram-сообщества. Данные из оригинальных сообщений.
</Note>

<CardGroup cols={{4}}>
  <Card title="EB-1A ({len(eb1a)})" icon="star" href="/success-stories/by-visa/eb-1a">
    Полный список
  </Card>
  <Card title="EB-2 NIW ({len(eb2)})" icon="lightbulb" href="/success-stories/by-visa/eb-2-niw">
    Полный список
  </Card>
  <Card title="O-1 ({len(o1)})" icon="bolt" href="/success-stories/by-visa/o-1">
    Полный список
  </Card>
</CardGroup>

---

## EB-1A ({len(eb1a)})

<AccordionGroup>
'''

    for case in eb1a:
        output += make_accordion(case) + '\n'

    output += f'''</AccordionGroup>

## EB-2 NIW ({len(eb2)})

<AccordionGroup>
'''

    for case in eb2:
        output += make_accordion(case) + '\n'

    output += f'''</AccordionGroup>

## O-1 ({len(o1)})

<AccordionGroup>
'''

    for case in o1:
        output += make_accordion(case) + '\n'

    output += '</AccordionGroup>\n'
    return output


def generate_filtered_page(cases: list, filter_fn, title: str, sidebar: str,
                           description: str, icon: str, heading: str) -> str:
    """Generate a filtered page (RFE, premium, etc.)."""
    filtered = [c for c in cases if filter_fn(c)]
    count = len(filtered)

    output = f'''---
title: "{title}"
sidebarTitle: "{sidebar} ({count})"
description: "{description}"
icon: "{icon}"
---

## {heading} ({count})

<AccordionGroup>
'''

    for case in filtered:
        output += make_accordion(case) + '\n'

    output += '</AccordionGroup>\n'
    return output


def generate_visa_page(cases: list, visa_filter: str, title: str, icon: str) -> str:
    """Generate a by-visa page."""
    if visa_filter.startswith('O-1'):
        filtered = [c for c in cases if c.get('visa', '').startswith('O-1')]
    else:
        filtered = [c for c in cases if c.get('visa') == visa_filter]

    count = len(filtered)

    output = f'''---
title: "Истории успеха: {visa_filter}"
sidebarTitle: "{visa_filter} ({count})"
description: "Реальные кейсы {visa_filter}."
icon: "{icon}"
---

## Кейсы {visa_filter} ({count})

<AccordionGroup>
'''

    for case in filtered:
        output += make_accordion(case) + '\n'

    output += '</AccordionGroup>\n'
    return output


def main():
    # Load cases
    with open(DATA_PATH) as f:
        data = json.load(f)
    cases = data['cases']

    print(f"Generating MDX from {len(cases)} cases...")

    # Generate cases-preview.mdx
    content = generate_cases_preview(cases)
    (STORIES_DIR / 'cases-preview.mdx').write_text(content)
    print("  - cases-preview.mdx")

    # Generate with-rfe.mdx
    content = generate_filtered_page(
        cases,
        lambda c: c.get('rfe'),
        "Кейсы с RFE (Request for Evidence)",
        "Одобрение через RFE",
        "Истории успеха, где USCIS запросил дополнительные доказательства.",
        "file-circle-question",
        "Кейсы с RFE"
    )
    (STORIES_DIR / 'with-rfe.mdx').write_text(content)
    print("  - with-rfe.mdx")

    # Generate premium.mdx
    content = generate_filtered_page(
        cases,
        lambda c: c.get('premium'),
        "Кейсы с Premium Processing",
        "Premium",
        "Истории успеха с ускоренным рассмотрением.",
        "bolt",
        "Кейсы с Premium"
    )
    (STORIES_DIR / 'premium.mdx').write_text(content)
    print("  - premium.mdx")

    # Generate self-prepared.mdx
    content = generate_filtered_page(
        cases,
        lambda c: c.get('prep') == 'self',
        "Самоподача без адвоката",
        "Самоподача",
        "Кейсы самостоятельной подготовки петиции.",
        "user",
        "Кейсы самоподачи"
    )
    (STORIES_DIR / 'self-prepared.mdx').write_text(content)
    print("  - self-prepared.mdx")

    # Generate by-visa pages
    visa_dir = STORIES_DIR / 'by-visa'
    visa_dir.mkdir(exist_ok=True)

    content = generate_visa_page(cases, 'EB-1A', "Истории успеха: EB-1A", "star")
    (visa_dir / 'eb-1a.mdx').write_text(content)
    print("  - by-visa/eb-1a.mdx")

    content = generate_visa_page(cases, 'EB-2 NIW', "Истории успеха: EB-2 NIW", "lightbulb")
    (visa_dir / 'eb-2-niw.mdx').write_text(content)
    print("  - by-visa/eb-2-niw.mdx")

    content = generate_visa_page(cases, 'O-1', "Истории успеха: O-1", "bolt")
    (visa_dir / 'o-1.mdx').write_text(content)
    print("  - by-visa/o-1.mdx")

    # Print stats
    eb1a = len([c for c in cases if c.get('visa') == 'EB-1A'])
    eb2 = len([c for c in cases if c.get('visa') == 'EB-2 NIW'])
    o1 = len([c for c in cases if c.get('visa', '').startswith('O-1')])
    rfe = len([c for c in cases if c.get('rfe')])
    premium = len([c for c in cases if c.get('premium')])
    self_prep = len([c for c in cases if c.get('prep') == 'self'])

    print(f"\nStats:")
    print(f"  Total: {len(cases)}")
    print(f"  EB-1A: {eb1a}")
    print(f"  EB-2 NIW: {eb2}")
    print(f"  O-1: {o1}")
    print(f"  RFE: {rfe}")
    print(f"  Premium: {premium}")
    print(f"  Self-prep: {self_prep}")


if __name__ == '__main__':
    main()
