#!/usr/bin/env python3
"""
Quality gate for success stories cases.
Cleans text, generates proper titles/summaries, filters garbage.
"""

import json
import re
from pathlib import Path
from typing import Optional

# Stop phrases for titles
TITLE_STOP_PHRASES = [
    'eb-1a кейс', 'eb-2 niw кейс', 'niw кейс', 'o-1 кейс', 'o-1a кейс', 'o-1b кейс',
    'привет', 'всем привет', 'ура', 'здравствуйте', 'ребята', 'хочу поделиться',
    'добрый день', 'доброе утро', 'моя очередь', 'делюсь', 'наконец', 'появилось время',
]

# Greeting patterns to remove from START only
GREETING_START_PATTERNS = [
    r'^(всем\s+)?привет[!.\s,]*',
    r'^ура[!,.\s]+',
    r'^здравствуйте[!.\s]*',
    r'^ребята[!,.\s]*',
    r'^добр(ый|ое)\s+(день|утро)[!.\s]*',
    r'^наконец[\s-]*(то)?\s+появилось время[^.]*[.,!]?\s*',
    r'^наконец[\s-]*(то)?\s+',
    r'^появилось время[^.]*[.,!]?\s*',
    r'^делюсь информацией[^.]*[.,!]?\s*',
    r'^хочу поделиться[^.]*[.,!]?\s*',
    r'^\*+\s*',
    r'^,\s*',  # Leading comma
    r'^\(после\s+-\s*а\)\s*',  # (после -а) artifact
]

# Full greeting sentences to skip entirely
GARBAGE_SENTENCES = [
    'всем привет',
    'наконец то появилось время все расписать',
    'делюсь информацией',
    'хочу поделиться',
    'появилось время',
    'моя очередь делиться',
    'мой черед',
]

# Brand names to replace with [сервис]
BRAND_NAMES = [
    'passright', 'wegreened', 'idreem', 'prideimmigration', 'pride immigration',
    'immigrationhelp', 'usvisahelp', 'talentpetition', 'шамаев', 'greencard.pro',
    'lawfirm', 'visalaw', 'муверт', 'muvert', 'аронова', 'aronova', 'поляков'
]

# Keywords indicating approval
APPROVAL_KEYWORDS = [
    'одобрили', 'одобрение', 'одобрен', 'аппрув', 'апрув', 'approved', 'approval',
    'visa issued', 'issued', 'case approved', 'получил', 'получила', 'пришел аппрув',
    'пришло одобрение', 'has approved'
]


def clean_text_light(text: str) -> str:
    """Light cleaning - remove only garbage, keep emotions and narrative."""
    if not text:
        return ""

    # Remove markdown artifacts
    text = re.sub(r'\*\*+', '', text)
    text = re.sub(r'__+', '', text)

    # Remove hashtags
    text = re.sub(r'#\w+\s*', '', text)

    # Remove/replace placeholders
    text = re.sub(r'\[name\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[имя\]', '', text)
    text = re.sub(r'\[ссылка\]', '', text)
    text = re.sub(r'\[аккаунт\]', '', text)

    # Replace brand names with [сервис]
    for brand in BRAND_NAMES:
        text = re.sub(rf'\b{brand}\b', '[сервис]', text, flags=re.IGNORECASE)

    # Clean excessive whitespace but keep single newlines
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    text = text.strip()

    return text


def clean_text_for_title(text: str) -> str:
    """Clean text for use in title - more aggressive cleaning."""
    text = clean_text_light(text)

    # Remove greetings from start
    for pattern in GREETING_START_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Remove emoji
    text = re.sub(r'[☺️💫📖🃏📍😁🙂🥳🙏🎉✨💪🔥❤️🇺🇸🕺😏]+', '', text)

    return text.strip()


def is_garbage_sentence(sent: str) -> bool:
    """Check if a sentence is just greeting/filler."""
    sent_lower = sent.lower().strip()

    # Check against known garbage sentences
    for garbage in GARBAGE_SENTENCES:
        if garbage in sent_lower:
            return True

    # Check greeting patterns
    if any(g in sent_lower for g in ['привет', 'делюсь', 'расскажу', 'появилось время', 'наконец то', 'хочу поделиться']):
        return True

    # Too short to be meaningful
    if len(sent_lower) < 15:
        return True

    return False


def find_approval_sentence(text: str) -> Optional[str]:
    """Find a sentence that describes the approval result."""
    if not text:
        return None

    # Clean text first
    text = clean_text_for_title(text)

    # Split into sentences
    sentences = re.split(r'[.!?]+', text)

    # First pass: look for clear approval statements
    for sent in sentences:
        sent_lower = sent.lower()
        if is_garbage_sentence(sent):
            continue
        # Look for approval keywords
        if any(kw in sent_lower for kw in APPROVAL_KEYWORDS):
            clean_sent = sent.strip()
            if len(clean_sent) > 15:
                return clean_sent[:150]

    # Second pass: look for RFE/NOID with result
    for sent in sentences:
        sent_lower = sent.lower()
        if is_garbage_sentence(sent):
            continue
        if ('rfe' in sent_lower or 'noid' in sent_lower) and any(kw in sent_lower for kw in ['апрув', 'одобр', 'approved']):
            clean_sent = sent.strip()
            if len(clean_sent) > 15:
                return clean_sent[:150]

    # Third pass: look for timeline info
    for sent in sentences:
        sent_lower = sent.lower()
        if is_garbage_sentence(sent):
            continue
        if any(kw in sent_lower for kw in ['дней', 'недел', 'месяц', 'premium', 'премиум', 'небраска', 'техас', 'вермонт', 'калифорни']):
            if any(kw in sent_lower for kw in ['рассмотр', 'получ', 'пришел', 'пришло', 'ждал', 'через']):
                clean_sent = sent.strip()
                if len(clean_sent) > 15:
                    return clean_sent[:150]

    # Fourth pass: look for case details (visa type, criteria, petitioner info)
    for sent in sentences:
        sent_lower = sent.lower()
        if is_garbage_sentence(sent):
            continue
        # Case details keywords
        if any(kw in sent_lower for kw in ['подавал', 'подавала', 'критери', 'петиц', 'интервью', 'консульство', 'visa', 'виза']):
            clean_sent = sent.strip()
            if len(clean_sent) > 20:
                return clean_sent[:150]

    # Fifth pass: first non-garbage sentence
    for sent in sentences:
        if is_garbage_sentence(sent):
            continue
        clean_sent = sent.strip()
        if len(clean_sent) > 20:
            return clean_sent[:150]

    return None


def extract_key_details(case: dict) -> dict:
    """Extract key details from case for title generation."""
    context = case.get('context', '')
    context_lower = context.lower()

    details = {
        'has_interview': False,
        'interview_city': case.get('consulate_city'),
        'has_rfe': case.get('rfe', False),
        'has_noid': case.get('noid', False),
        'has_premium': case.get('premium', False),
        'service_center': case.get('service_center'),
        'timeline': None,
        'profession': None,
    }

    # Look for interview mentions
    interview_patterns = [
        r'интервью\s+в\s+(\w+)',
        r'собеседование\s+в\s+(\w+)',
        r'консульство\s+в\s+(\w+)',
    ]
    for pattern in interview_patterns:
        match = re.search(pattern, context_lower)
        if match:
            details['has_interview'] = True
            if not details['interview_city']:
                details['interview_city'] = match.group(1).capitalize()

    # Look for timeline
    timeline_match = re.search(r'за\s+(\d+)\s*(дн|недел|месяц)', context_lower)
    if timeline_match:
        num = timeline_match.group(1)
        unit = timeline_match.group(2)
        if 'дн' in unit:
            details['timeline'] = f"{num} дней"
        elif 'недел' in unit:
            details['timeline'] = f"{num} нед."
        elif 'месяц' in unit:
            details['timeline'] = f"{num} мес."

    # Look for profession
    professions = {
        'программист': 'Программист',
        'software': 'Software Engineer',
        'developer': 'Developer',
        'дизайнер': 'Дизайнер',
        'маркетолог': 'Маркетолог',
        'фотограф': 'Фотограф',
        'актер': 'Актер',
        'актриса': 'Актриса',
        'танц': 'Танцор',
        'модел': 'Модель',
        'журналист': 'Журналист',
        'инженер': 'Инженер',
        'architect': 'Архитектор',
        'product': 'Product Manager',
        'entrepreneur': 'Предприниматель',
        'звукорежис': 'Звукорежиссер',
        'педагог': 'Педагог',
    }
    for key, val in professions.items():
        if key in context_lower:
            details['profession'] = val
            break

    return details


def generate_title(case: dict) -> str:
    """Generate an informative title from case data."""
    visa = case.get('visa', 'EB-1A')
    field = case.get('field', '')
    details = extract_key_details(case)

    parts = [visa]

    # Add profession or field
    if details['profession']:
        parts.append(details['profession'])
    elif field:
        parts.append(field)

    # Build modifiers
    modifiers = []
    if details['has_premium']:
        modifiers.append('premium')
    if details['has_rfe']:
        modifiers.append('RFE')
    if details['has_noid']:
        modifiers.append('NOID')
    if details['interview_city']:
        modifiers.append(details['interview_city'])
    elif details['service_center']:
        modifiers.append(details['service_center'])
    if details['timeline'] and len(modifiers) < 2:
        modifiers.append(details['timeline'])

    # Construct title
    if len(parts) > 1:
        title = f"{parts[0]}: {parts[1]}"
    else:
        title = parts[0]

    if modifiers:
        title += f" ({', '.join(modifiers[:3])})"

    return title[:60]


def is_title_garbage(title: str) -> bool:
    """Check if title is too generic or garbage."""
    title_lower = title.lower().strip()

    # Too short
    if len(title_lower) < 8:
        return True

    # Matches stop phrases
    for phrase in TITLE_STOP_PHRASES:
        if title_lower.startswith(phrase) or title_lower == phrase:
            return True

    # Just visa type
    if title_lower in ['eb-1a', 'eb-2 niw', 'eb-2', 'o-1', 'o-1a', 'o-1b', 'niw', 'approval']:
        return True

    # Starts with greeting
    if re.match(r'^(привет|ура|ребята|делюсь|наконец)', title_lower):
        return True

    return False


def extract_summary(context: str, case: dict) -> str:
    """Extract a meaningful summary from context."""
    if not context:
        return build_fallback_summary(case)

    # Try to find approval sentence
    approval_sent = find_approval_sentence(context)
    if approval_sent:
        return approval_sent

    # If no approval sentence, try first informative sentence
    cleaned_context = clean_text_for_title(context)
    sentences = re.split(r'[.!?]+', cleaned_context)
    for sent in sentences:
        if is_garbage_sentence(sent):
            continue
        sent_clean = sent.strip()
        if len(sent_clean) > 20:
            return sent_clean[:150]

    return build_fallback_summary(case)


def build_fallback_summary(case: dict) -> str:
    """Build summary from case metadata when no good text found."""
    visa = case.get('visa', '')
    field = case.get('field', '')
    parts = []

    # Start with visa and field info
    if field:
        parts.append(f"Кейс в сфере {field}")
    elif visa:
        parts.append(f"Кейс {visa}")

    modifiers = []
    if case.get('premium'):
        modifiers.append('premium processing')
    if case.get('rfe'):
        modifiers.append('после RFE')
    if case.get('noid'):
        modifiers.append('после NOID')
    if case.get('service_center'):
        modifiers.append(case['service_center'])
    if case.get('consulate_city'):
        modifiers.append(f"интервью {case['consulate_city']}")

    if parts and modifiers:
        return f"{parts[0]}, {', '.join(modifiers)}. Одобрен."
    elif modifiers:
        return f"Одобрение: {', '.join(modifiers)}."
    elif parts:
        return f"{parts[0]}. Одобрен."

    # Only use generic fallback if we truly have nothing
    return "Успешный кейс."


def is_context_duplicate(summary: str, context: str) -> bool:
    """Check if context is essentially the same as summary."""
    if not context or not summary:
        return True

    # Normalize for comparison
    s1 = re.sub(r'\W+', '', summary.lower())[:100]
    s2 = re.sub(r'\W+', '', context.lower())[:100]

    # If very short context, it's likely duplicate
    if len(s2) < 50:
        return True

    # Check if one contains the other
    if len(s1) > 20 and len(s2) > 20:
        if s1 in s2 or s2 in s1:
            # Only mark as duplicate if context doesn't have much more
            if len(s2) < len(s1) * 1.5:
                return True

    return False


def expand_context(context: str, summary: str) -> str:
    """If context is too short or same as summary, try to expand it."""
    if not context:
        return ""

    # If context is same as summary, try to get more
    sentences = re.split(r'[.!?]+', context)
    if len(sentences) > 1:
        # Skip first sentence if it's the summary, take next ones
        expanded = []
        for i, sent in enumerate(sentences):
            sent_clean = sent.strip()
            if len(sent_clean) < 15:
                continue
            # Skip if it's essentially the summary
            if summary and re.sub(r'\W+', '', sent_clean.lower()) in re.sub(r'\W+', '', summary.lower()):
                continue
            expanded.append(sent_clean)
            if len(' '.join(expanded)) > 200:
                break

        if expanded:
            return '. '.join(expanded) + '.'

    return context


def is_card_garbage(case: dict) -> bool:
    """Check if the entire card has no useful content."""
    title = clean_text_for_title(case.get('title', ''))
    context = clean_text_light(case.get('context', ''))

    # Title is garbage
    title_bad = is_title_garbage(title)

    # Context too short
    context_bad = len(context) < 40

    # No useful metadata
    has_field = bool(case.get('field'))
    has_center = bool(case.get('service_center'))
    has_consulate = bool(case.get('consulate_city'))
    has_flags = case.get('rfe') or case.get('premium') or case.get('noid')

    # If title is bad AND context is bad AND no useful metadata
    if title_bad and context_bad and not has_field and not has_flags and not has_center and not has_consulate:
        return True

    return False


def process_case(case: dict) -> Optional[dict]:
    """Process a single case, returning cleaned version or None if garbage."""
    # Check if entire card is garbage
    if is_card_garbage(case):
        return None

    # Clean texts
    cleaned_title = clean_text_for_title(case.get('title', ''))
    cleaned_context = clean_text_light(case.get('context', ''))

    # Generate title if needed
    if is_title_garbage(cleaned_title):
        cleaned_title = generate_title(case)

    # Generate summary
    summary = extract_summary(cleaned_context, case)

    # Expand context if it's same as summary
    if is_context_duplicate(summary, cleaned_context):
        cleaned_context = expand_context(case.get('context', ''), summary)

    # Build cleaned case
    cleaned = case.copy()
    cleaned['title'] = cleaned_title
    cleaned['context'] = cleaned_context
    cleaned['summary'] = summary

    # Mark if context should be hidden (only if truly no extra info)
    cleaned['hide_context'] = (
        is_context_duplicate(summary, cleaned_context) and
        len(cleaned_context) < 60
    )

    return cleaned


def process_all_cases(input_path: str, output_path: str = None):
    """Process all cases and save cleaned version."""
    with open(input_path) as f:
        data = json.load(f)

    original_count = len(data['cases'])
    cleaned_cases = []
    removed_ids = []

    for case in data['cases']:
        cleaned = process_case(case)
        if cleaned:
            cleaned_cases.append(cleaned)
        else:
            removed_ids.append(case.get('id', 'unknown'))

    data['cases'] = cleaned_cases

    output = output_path or input_path
    with open(output, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Processed {original_count} cases")
    print(f"Kept: {len(cleaned_cases)}")
    print(f"Removed: {len(removed_ids)}")
    if removed_ids:
        print(f"Removed IDs: {removed_ids}")

    return data


if __name__ == '__main__':
    import sys
    input_path = sys.argv[1] if len(sys.argv) > 1 else '/Users/aeb/mintlify-docs/data/cases.json'
    process_all_cases(input_path)
