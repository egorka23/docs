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
    'добрый день', 'доброе утро', 'моя очередь', 'делюсь', 'approval', 'approved',
    'апрув', 'одобрили', 'аппрув'
]

# Greeting patterns to remove from start
GREETING_PATTERNS = [
    r'^(всем\s+)?привет[!.\s]*',
    r'^ура[!,.\s]+',
    r'^здравствуйте[!.\s]*',
    r'^ребята[!,.\s]*',
    r'^(хочу\s+)?поделиться[!.\s]*',
    r'^добр(ый|ое)\s+(день|утро)[!.\s]*',
    r'^моя\s+очередь[!.\s]*',
    r'^делюсь[!.\s]*',
    r'^\*+\s*',
]

# Brand names to replace with [сервис]
BRAND_NAMES = [
    'passright', 'wegreened', 'idreem', 'prideimmigration', 'pride immigration',
    'immigrationhelp', 'usvisahelp', 'talentpetition', 'шамаев', 'greencard.pro',
    'lawfirm', 'visalaw'
]


def clean_text(text: str) -> str:
    """Clean text from markdown artifacts, hashtags, placeholders, brands."""
    if not text:
        return ""

    # Remove markdown artifacts
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'__+', '', text)

    # Remove hashtags at start or standalone
    text = re.sub(r'#\w+\s*', '', text)

    # Remove/replace placeholders
    text = re.sub(r'\[name\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[имя\]', '', text)
    text = re.sub(r'\[ссылка\]', '', text)
    text = re.sub(r'\[аккаунт\]', '', text)

    # Replace brand names with [сервис]
    for brand in BRAND_NAMES:
        text = re.sub(rf'\b{brand}\b', '[сервис]', text, flags=re.IGNORECASE)

    # Remove emoji spam
    text = re.sub(r'[☺️💫📖🃏📍😁🙂🥳🙏🎉✨💪🔥❤️]+', '', text)

    # Remove greetings from start
    for pattern in GREETING_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def is_title_garbage(title: str) -> bool:
    """Check if title is too generic or garbage."""
    title_lower = title.lower().strip()

    # Too short
    if len(title_lower) < 5:
        return True

    # Matches stop phrases
    for phrase in TITLE_STOP_PHRASES:
        if title_lower.startswith(phrase) or title_lower == phrase:
            return True

    # Just visa type
    if title_lower in ['eb-1a', 'eb-2 niw', 'eb-2', 'o-1', 'o-1a', 'o-1b', 'niw']:
        return True

    return False


def generate_title(case: dict) -> str:
    """Generate a proper title from case data."""
    visa = case.get('visa', 'EB-1A')
    field = case.get('field', '')
    rfe = case.get('rfe', False)
    premium = case.get('premium', False)
    service_center = case.get('service_center', '')

    parts = [visa]

    if field:
        parts.append(field)

    modifiers = []
    if premium:
        modifiers.append('premium')
    if rfe:
        modifiers.append('RFE')
    if service_center:
        modifiers.append(service_center)

    if modifiers:
        parts.append(', '.join(modifiers))

    title = ': '.join(parts[:2])
    if len(parts) > 2:
        title += f" ({parts[2]})"

    return title[:55]


def extract_summary(context: str, case: dict) -> str:
    """Extract a meaningful summary from context."""
    if not context:
        parts = []
        if case.get('premium'):
            parts.append('Premium processing')
        if case.get('rfe'):
            parts.append('RFE')
        if parts:
            return f"Одобрение. {', '.join(parts)}."
        return "Одобрение (по словам автора)."

    # Look for sentences with key info
    sentences = re.split(r'[.!?]+', context)

    keywords = ['одобр', 'апрув', 'аппрув', 'approved', 'rfe', 'noid',
                'premium', 'дней', 'месяц', 'nebraska', 'texas', 'небраска', 'техас']

    for sent in sentences:
        sent_lower = sent.lower()
        if any(kw in sent_lower for kw in keywords):
            summary = sent.strip()
            if len(summary) > 20:
                return summary[:100] + ('...' if len(summary) > 100 else '')

    # Fallback: first sentence if long enough
    if sentences and len(sentences[0].strip()) > 20:
        return sentences[0].strip()[:100]

    # Ultimate fallback
    parts = []
    if case.get('premium'):
        parts.append('Premium')
    if case.get('rfe'):
        parts.append('после RFE')
    if case.get('service_center'):
        parts.append(case['service_center'])

    if parts:
        return f"Одобрение. {', '.join(parts)}."
    return "Одобрение (по словам автора)."


def is_context_duplicate(summary: str, context: str) -> bool:
    """Check if context is essentially the same as summary."""
    if not context or not summary:
        return True

    # Normalize for comparison
    s1 = re.sub(r'\W+', '', summary.lower())
    s2 = re.sub(r'\W+', '', context.lower())

    # If one contains the other or they're very similar
    if s1 in s2 or s2 in s1:
        return True

    # Check similarity ratio
    if len(s1) < 30 and len(s2) < 30:
        return True

    return False


def is_card_garbage(case: dict) -> bool:
    """Check if the entire card has no useful content."""
    title = clean_text(case.get('title', ''))
    context = clean_text(case.get('context', ''))

    # Title is garbage
    title_bad = is_title_garbage(title)

    # Context too short
    context_bad = len(context) < 50

    # No useful metadata
    has_field = bool(case.get('field'))
    has_center = bool(case.get('service_center'))
    has_flags = case.get('rfe') or case.get('premium')

    # If title is bad AND context is bad AND no useful metadata
    if title_bad and context_bad and not has_field and not has_flags:
        return True

    return False


def process_case(case: dict) -> Optional[dict]:
    """Process a single case, returning cleaned version or None if garbage."""
    # Check if entire card is garbage
    if is_card_garbage(case):
        return None

    # Clean texts
    cleaned_title = clean_text(case.get('title', ''))
    cleaned_context = clean_text(case.get('context', ''))

    # Generate title if needed
    if is_title_garbage(cleaned_title):
        cleaned_title = generate_title(case)

    # Generate summary
    summary = extract_summary(cleaned_context, case)

    # Build cleaned case
    cleaned = case.copy()
    cleaned['title'] = cleaned_title
    cleaned['context'] = cleaned_context
    cleaned['summary'] = summary

    # Mark if context should be hidden
    cleaned['hide_context'] = (
        is_context_duplicate(summary, cleaned_context) or
        len(cleaned_context) < 30
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
