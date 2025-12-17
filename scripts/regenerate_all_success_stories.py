#!/usr/bin/env python3
"""
Regenerate all success-stories MDX pages from data/cases.json.

Pages generated:
- cases-preview.mdx (all cases)
- premium.mdx (premium=True)
- with-rfe.mdx (rfe=True)
- self-prepared.mdx (prep="self")
- by-center/nebraska.mdx (service_center="NSC")
- by-center/vermont.mdx (service_center="VSC")
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
    criteria = case.get("claimed_criteria") or case.get("criteria", [])
    icon = get_icon(case)

    lines = []
    lines.append(f'  <Accordion title="{title}" icon="{icon}">')
    lines.append(f'    **Итог:** {summary}')
    lines.append('')

    tags = generate_tags(case)
    if tags:
        tag_codes = " ".join(f"<code>{t}</code>" for t in tags)
        lines.append(f"    <div style={{{{display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px'}}}}>")
        lines.append(f"      {tag_codes}")
        lines.append(f"    </div>")
        lines.append('')

    if context and len(context) > 10 and not context.startswith('#'):
        lines.append('    ### Контекст')
        if len(context) > 300:
            context = context[:297] + "..."
        lines.append(f'    {context}')
        lines.append('')

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

    details = []
    if case.get("timeline_days"):
        details.append(f"- Срок рассмотрения: ~{case['timeline_days']} дней")
    if case.get("consulate_city"):
        details.append(f"- Консульство: {case['consulate_city']}")
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


def generate_premium_mdx(cases):
    premium_cases = [c for c in cases if c.get("premium") is True]

    lines = []
    lines.append('---')
    lines.append('title: "Кейсы с Premium Processing"')
    lines.append('sidebarTitle: "Premium"')
    lines.append('description: "Подборка историй с ускоренным рассмотрением. Таймлайны, когда стоит платить."')
    lines.append('icon: "bolt"')
    lines.append('---')
    lines.append('')
    lines.append('<Note>')
    lines.append(f'**Premium Processing** - ускоренное рассмотрение за $2,805 (I-140). USCIS дает ответ в течение 15 рабочих дней.')
    lines.append('</Note>')
    lines.append('')
    lines.append(f'## Кейсы с Premium ({len(premium_cases)} из 25)')
    lines.append('')
    lines.append('<AccordionGroup>')
    for case in premium_cases:
        lines.append(generate_accordion(case))
    lines.append('</AccordionGroup>')
    lines.append('')

    return '\n'.join(lines)


def generate_rfe_mdx(cases):
    rfe_cases = [c for c in cases if c.get("rfe") is True]

    lines = []
    lines.append('---')
    lines.append('title: "Кейсы с RFE (Request for Evidence)"')
    lines.append('sidebarTitle: "С RFE"')
    lines.append('description: "Истории успеха, где USCIS запросил дополнительные доказательства."')
    lines.append('icon: "file-circle-question"')
    lines.append('---')
    lines.append('')
    lines.append('<Note>')
    lines.append('**RFE** - запрос дополнительных доказательств. Не отказ, а возможность усилить кейс.')
    lines.append('</Note>')
    lines.append('')
    lines.append(f'## Кейсы с RFE ({len(rfe_cases)} из 25)')
    lines.append('')
    lines.append('<AccordionGroup>')
    for case in rfe_cases:
        lines.append(generate_accordion(case))
    lines.append('</AccordionGroup>')
    lines.append('')

    return '\n'.join(lines)


def generate_self_mdx(cases):
    self_cases = [c for c in cases if c.get("prep") == "self"]

    lines = []
    lines.append('---')
    lines.append('title: "Самоподача без адвоката"')
    lines.append('sidebarTitle: "Самоподача"')
    lines.append('description: "Кейсы самостоятельной подготовки петиции. Экономия, риски, что нужно знать."')
    lines.append('icon: "user"')
    lines.append('---')
    lines.append('')
    lines.append('<Note>')
    lines.append('**Самоподача** - подготовка петиции без адвоката. Экономия $5,000-15,000.')
    lines.append('</Note>')
    lines.append('')
    lines.append(f'## Кейсы самоподачи ({len(self_cases)})')
    lines.append('')
    lines.append('<AccordionGroup>')
    for case in self_cases:
        lines.append(generate_accordion(case))
    lines.append('</AccordionGroup>')
    lines.append('')

    return '\n'.join(lines)


def generate_nebraska_mdx(cases):
    nsc_cases = [c for c in cases if c.get("service_center") == "NSC"]

    lines = []
    lines.append('---')
    lines.append('title: "Кейсы Nebraska Service Center (NSC)"')
    lines.append('sidebarTitle: "Nebraska (NSC)"')
    lines.append('description: "Подборка историй с рассмотрением в Nebraska Service Center."')
    lines.append('icon: "building-columns"')
    lines.append('---')
    lines.append('')
    lines.append('<Note>')
    lines.append('**Nebraska Service Center (NSC)** обрабатывает петиции EB-1A, EB-2 NIW и O-1.')
    lines.append('</Note>')
    lines.append('')
    lines.append(f'## Подтвержденные кейсы NSC ({len(nsc_cases)})')
    lines.append('')
    lines.append('<AccordionGroup>')
    for case in nsc_cases:
        lines.append(generate_accordion(case))
    lines.append('</AccordionGroup>')
    lines.append('')

    return '\n'.join(lines)


def generate_vermont_mdx(cases):
    vsc_cases = [c for c in cases if c.get("service_center") == "VSC"]

    lines = []
    lines.append('---')
    lines.append('title: "Кейсы Vermont Service Center (VSC)"')
    lines.append('sidebarTitle: "Vermont (VSC)"')
    lines.append('description: "Истории успеха с рассмотрением в Vermont Service Center."')
    lines.append('icon: "building-columns"')
    lines.append('---')
    lines.append('')
    lines.append('<Note>')
    lines.append('**Vermont Service Center (VSC)** обрабатывает петиции O-1.')
    lines.append('</Note>')
    lines.append('')
    lines.append(f'## Подтвержденные кейсы VSC ({len(vsc_cases)})')
    lines.append('')
    lines.append('<AccordionGroup>')
    for case in vsc_cases:
        lines.append(generate_accordion(case))
    lines.append('</AccordionGroup>')
    lines.append('')

    return '\n'.join(lines)


def group_cases_by_visa(cases):
    groups = defaultdict(list)
    visa_order = ["EB-1A", "EB-2 NIW", "O-1"]

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


def generate_preview_mdx(cases):
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
    ss_dir = project_root / 'success-stories'

    print("Loading cases...")
    with open(cases_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cases = data.get('cases', [])
    print(f"Found {len(cases)} cases")

    pages = [
        ('cases-preview.mdx', generate_preview_mdx(cases)),
        ('premium.mdx', generate_premium_mdx(cases)),
        ('with-rfe.mdx', generate_rfe_mdx(cases)),
        ('self-prepared.mdx', generate_self_mdx(cases)),
        ('by-center/nebraska.mdx', generate_nebraska_mdx(cases)),
        ('by-center/vermont.mdx', generate_vermont_mdx(cases)),
    ]

    for filename, content in pages:
        path = ss_dir / filename
        print(f"Writing {path}...")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    print("Done!")


if __name__ == '__main__':
    main()
