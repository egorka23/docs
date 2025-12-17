#!/usr/bin/env python3
"""
Regenerate cases-preview.mdx from data/cases.json.

Template (per enrichment pack rules):
1. Итог (1 sentence)
2. Контекст (if context exists)
3. Что заявляли / использовали в пакете (claimed_criteria, NOT "засчитали")
4. Хронология (if timeline data exists)

Rules:
- Do NOT say "засчитали критерии" - use "В истории упоминаются..."
- If service_center_uncertain=true, show as "по словам автора"
- If field is missing - hide the section
"""

import json
from pathlib import Path
from collections import defaultdict

CRITERIA_RU = {
    "awards": "Награды",
    "membership": "Членство",
    "press": "СМИ",
    "judging": "Судейство",
    "contributions": "Вклад",
    "critical_role": "Критическая роль",
    "salary": "Высокая ЗП",
    "authorship": "Авторство",
    "exhibitions": "Выставки",
}

ICONS = {
    "IT": "laptop-code",
    "Наука": "flask",
    "Бизнес": "briefcase",
    "Искусство": "palette",
    "Музыка": "music",
    "Маркетинг": "presentation",
    "Архитектура": "building",
    "Спорт": "person-running",
}


def get_icon(case):
    field = case.get("field")
    if field and field in ICONS:
        return ICONS[field]
    return "file"


def format_criteria(criteria_list):
    if not criteria_list:
        return None
    return ", ".join(CRITERIA_RU.get(c, c) for c in criteria_list)


def generate_tags(case):
    tags = []
    if case.get("visa"):
        tags.append(case["visa"])
    if case.get("field"):
        tags.append(case["field"])
    if case.get("premium") is True:
        tags.append("premium")

    # Service center with uncertainty handling
    sc = case.get("service_center")
    if sc and not case.get("service_center_uncertain"):
        tags.append(sc)

    prep = case.get("prep")
    if prep == "self":
        tags.append("самоподача")
    elif prep == "attorney":
        tags.append("с адвокатом")

    if case.get("rfe") is True:
        tags.append("RFE")
    elif case.get("rfe") is False:
        tags.append("без RFE")

    if case.get("noid") is True:
        tags.append("NOID")

    return tags


def generate_accordion(case):
    title = case.get("title", "Кейс")
    summary = case.get("summary", "")
    context = case.get("context")

    # Use claimed_criteria if available, otherwise fallback to criteria
    criteria = case.get("claimed_criteria") or case.get("criteria", [])

    icon = get_icon(case)

    lines = []
    lines.append(f'  <Accordion title="{title}" icon="{icon}">')

    # 1. Итог
    lines.append(f'    **Итог:** {summary}')
    lines.append('')

    # Tags
    tags = generate_tags(case)
    if tags:
        tag_codes = " ".join(f"<code>{t}</code>" for t in tags)
        lines.append(f"    <div style={{{{display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px'}}}}>")
        lines.append(f"      {tag_codes}")
        lines.append(f"    </div>")
        lines.append('')

    # 2. Контекст (only if exists and not empty/hashtag-only)
    if context and len(context) > 10 and not context.startswith('#'):
        lines.append('    ### Контекст')
        # Truncate long context
        if len(context) > 300:
            context = context[:297] + "..."
        lines.append(f'    {context}')
        lines.append('')

    # 3. Что заявляли / использовали в пакете
    criteria_str = format_criteria(criteria)
    has_package_info = criteria_str or case.get("attorney") or case.get("rec_letters")

    if has_package_info:
        lines.append('    ### Что заявляли / использовали в пакете')
        if criteria_str:
            lines.append(f'    В истории упоминаются: {criteria_str}')
        if case.get("attorney"):
            lines.append(f'    - Адвокат: {case["attorney"]}')
        if case.get("rec_letters"):
            lines.append(f'    - Рекомендательных писем: {case["rec_letters"]}')
        lines.append('')

    # 4. Хронология / Детали (only if has timeline data)
    details = []

    if case.get("timeline_days"):
        details.append(f"- Срок рассмотрения: ~{case['timeline_days']} дней")

    if case.get("consulate_city"):
        details.append(f"- Консульство: {case['consulate_city']}")

    # Service center with uncertainty
    sc = case.get("service_center")
    sc_note = case.get("service_center_note")
    if sc and not case.get("service_center_uncertain"):
        details.append(f"- Service Center: {sc}")
    elif sc_note:
        details.append(f"- Service Center: {sc_note}")

    if case.get("cost_usd"):
        details.append(f"- Расходы: ${case['cost_usd']:,}")

    if details:
        lines.append('    ### Хронология')
        lines.extend(f'    {d}' for d in details)
        lines.append('')

    lines.append('  </Accordion>')
    return '\n'.join(lines)


def group_cases_by_visa(cases):
    groups = defaultdict(list)
    visa_order = ["EB-1A", "EB-1", "EB-2 NIW", "O-1"]

    for case in cases:
        visa = case.get("visa", "Other")
        groups[visa].append(case)

    result = []
    for visa in visa_order:
        if visa in groups:
            result.append((visa, groups.pop(visa)))
    for visa, cases_list in groups.items():
        result.append((visa, cases_list))

    return result


def generate_mdx(cases):
    lines = []

    lines.append('---')
    lines.append('title: "Витрина кейсов"')
    lines.append('sidebarTitle: "Витрина (25 кейсов)"')
    lines.append('description: "Все 25 реальных кейсов из сообщества с контекстом и деталями."')
    lines.append('icon: "grid-2"')
    lines.append('---')
    lines.append('')
    lines.append('<Note>')
    lines.append('**25 кейсов** из Telegram-сообщества. Данные из оригинальных сообщений.')
    lines.append('</Note>')
    lines.append('')

    grouped = group_cases_by_visa(cases)

    for visa, visa_cases in grouped:
        lines.append(f'## {visa} ({len(visa_cases)} кейсов)')
        lines.append('')
        lines.append('<AccordionGroup>')
        for case in visa_cases:
            lines.append(generate_accordion(case))
        lines.append('</AccordionGroup>')
        lines.append('')

    lines.append('---')
    lines.append('')
    lines.append('<CardGroup cols={2}>')
    lines.append('  <Card title="Premium Processing" icon="bolt" href="/success-stories/premium">')
    lines.append('    Кейсы с ускоренным рассмотрением.')
    lines.append('  </Card>')
    lines.append('  <Card title="С RFE" icon="file-circle-question" href="/success-stories/with-rfe">')
    lines.append('    Кейсы с запросом доказательств.')
    lines.append('  </Card>')
    lines.append('</CardGroup>')
    lines.append('')

    return '\n'.join(lines)


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    cases_path = project_root / 'data' / 'cases.json'
    output_path = project_root / 'success-stories' / 'cases-preview.mdx'

    print("Loading cases...")
    with open(cases_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cases = data.get('cases', [])
    print(f"Found {len(cases)} cases")

    print("Generating MDX...")
    mdx = generate_mdx(cases)

    print(f"Writing {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(mdx)

    print("Done!")


if __name__ == '__main__':
    main()
