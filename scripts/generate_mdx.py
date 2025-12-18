#!/usr/bin/env python3
"""
Generate MDX pages for success stories with quality gate.
"""

import json
import re
from pathlib import Path
from clean_cases import (
    clean_text_light, clean_text_for_title, is_title_garbage,
    generate_title, extract_summary, is_context_duplicate, expand_context
)

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

    # Get or generate title
    title = case.get('title', '')
    if not title or is_title_garbage(title):
        title = generate_title(case)
    title = clean_text_for_title(title)[:55]

    icon = get_icon(field, visa)

    # Get context (use raw from case, clean lightly)
    raw_context = case.get('context', '')
    context = clean_text_light(raw_context)

    # Get or generate summary
    summary = case.get('summary', '')
    if not summary:
        summary = extract_summary(raw_context, case)
    summary = clean_text_for_title(summary)[:200]

    # Build tags
    tags = [f'<code>{visa}</code>']
    if field:
        tags.append(f'<code>{field}</code>')
    if case.get('rfe'):
        tags.append('<code>RFE</code>')
    if case.get('noid'):
        tags.append('<code>NOID</code>')
    if case.get('premium'):
        tags.append('<code>premium</code>')
    if case.get('prep') == 'self':
        tags.append('<code>самоподача</code>')
    if case.get('service_center'):
        tags.append(f'<code>{case["service_center"]}</code>')
    if case.get('consulate_city'):
        tags.append(f'<code>{case["consulate_city"]}</code>')

    # Determine if we should show context section
    # Show context if:
    # 1. Context is long enough (> 80 chars)
    # 2. Context is not just a repeat of summary
    # 3. Context has meaningful additional info
    show_context = True

    if not context or len(context) < 50:
        show_context = False
    elif is_context_duplicate(summary, context) and len(context) < len(summary) * 1.5:
        # Try to expand context
        expanded = expand_context(raw_context, summary)
        if expanded and len(expanded) > len(summary) * 1.3:
            context = expanded
        else:
            show_context = False

    # Build accordion
    accordion = f'''  <Accordion title="{title}" icon="{icon}">
    **Итог:** {summary}

    <div style={{{{display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px'}}}}>
      {' '.join(tags)}
    </div>
'''

    if show_context:
        # Truncate context to reasonable length
        display_context = context[:400]
        if len(context) > 400:
            # Try to cut at sentence boundary
            last_period = display_context.rfind('.')
            if last_period > 200:
                display_context = display_context[:last_period + 1]

        accordion += f'''
    ### Контекст
    {display_context}
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
                           description: str, icon: str, heading: str, note: str = None) -> str:
    """Generate a filtered page (RFE, premium, etc.)."""
    filtered = [c for c in cases if filter_fn(c)]
    count = len(filtered)

    output = f'''---
title: "{title}"
sidebarTitle: "{sidebar} ({count})"
description: "{description}"
icon: "{icon}"
---
'''

    if note:
        output += f'''
<Note>
{note}
</Note>
'''

    output += f'''
## {heading} ({count})

<AccordionGroup>
'''

    for case in filtered:
        output += make_accordion(case) + '\n'

    output += '</AccordionGroup>\n'
    return output


def generate_visa_page(cases: list, visa_filter: str, title: str, icon: str, note: str = None) -> str:
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
'''

    if note:
        output += f'''
<Note>
{note}
</Note>
'''

    output += f'''
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
        "Кейсы с RFE",
        note="**RFE** - запрос дополнительных доказательств. Не отказ, а возможность усилить кейс."
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
        "Кейсы с Premium",
        note="**Premium Processing** - ускоренное рассмотрение за $2,805 (I-140). USCIS дает ответ в течение 15 рабочих дней."
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
        "Кейсы самоподачи",
        note="**Самоподача** - подготовка петиции без адвоката. Экономия $5,000-15,000."
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

    # O-1 page with helpful note
    o1_note = """**O-1** имеет две подкатегории:
- **O-1A** — для бизнеса, науки, образования, спорта
- **O-1B** — для искусства, кино, ТВ"""
    content = generate_visa_page(cases, 'O-1', "Истории успеха: O-1", "bolt", note=o1_note)
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
