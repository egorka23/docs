#!/usr/bin/env python3
"""
Production link audit script for Mintlify docs.
Crawls specified pages, extracts internal links, and checks for broken links.
"""

import re
import ssl
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from collections import defaultdict
from typing import List, Dict, Set, Tuple
import json
import sys

BASE_URL = "https://www.o1eb1.com"
DOCS_PREFIX = "/docs"

# Pages to audit
PAGES_TO_AUDIT = [
    "/docs/administrative-check/faq",
    "/docs/administrative-check/consulates",
    "/docs/administrative-check/timelines",
    "/docs/administrative-check/mandamus",
    "/docs/administrative-check/ds-5535",
    "/docs/administrative-check/tal-mantis",
    "/docs/administrative-check/expedite",
    "/docs/administrative-check/congressional-inquiry",
    "/docs/administrative-check/stem-publications",
    "/docs/success-stories",
    "/docs/success-stories/premium",
    "/docs/success-stories/cases-preview",
    "/docs/success-stories/self-prepared",
    "/docs/success-stories/with-rfe",
    "/docs/success-stories/by-center/nebraska",
    "/docs/success-stories/by-center/vermont",
    "/docs/success-stories/by-center/texas",
    "/docs/community",
]


class LinkExtractor(HTMLParser):
    """Extract href attributes from HTML."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value:
                    self.links.append(value)


def fetch_page(url: str) -> str:
    """Fetch HTML content from URL."""
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) LinkAudit/1.0'
        })
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return ""


def check_url_status(url: str) -> Tuple[int, str]:
    """Check HTTP status of URL. Returns (status_code, final_url)."""
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, method='HEAD', headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) LinkAudit/1.0'
        })
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            return resp.status, resp.url
    except urllib.error.HTTPError as e:
        return e.code, url
    except Exception as e:
        return -1, str(e)


def normalize_link(link: str, source_page: str) -> str:
    """Normalize a link to absolute URL."""
    # Skip external links, mailto, tel, anchors-only
    if link.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:')):
        if link.startswith(BASE_URL):
            return link
        return None  # External link

    if link.startswith('#'):
        return None  # Anchor only

    # Handle absolute paths starting with /docs/
    if link.startswith('/docs/'):
        return BASE_URL + link

    # Handle absolute paths starting with /
    if link.startswith('/'):
        return BASE_URL + link

    # Handle relative paths
    # Remove anchor from source page for path calculation
    source_path = source_page.split('#')[0]

    # Get directory of source page
    if not source_path.endswith('/'):
        source_dir = '/'.join(source_path.split('/')[:-1])
    else:
        source_dir = source_path.rstrip('/')

    # Resolve relative path
    full_path = urllib.parse.urljoin(source_dir + '/', link)

    # Ensure it starts with BASE_URL
    if not full_path.startswith('http'):
        full_path = BASE_URL + full_path

    return full_path


def is_internal_link(url: str) -> bool:
    """Check if URL is an internal docs link."""
    if not url:
        return False
    return url.startswith(BASE_URL + '/docs')


def detect_double_path(url: str) -> bool:
    """Detect if URL has double path like /administrative-check/administrative-check/."""
    patterns = [
        r'/administrative-check/administrative-check/',
        r'/success-stories/success-stories/',
        r'/by-center/by-center/',
    ]
    for pattern in patterns:
        if re.search(pattern, url):
            return True
    return False


def main():
    print("=" * 60)
    print("PRODUCTION LINK AUDIT")
    print("=" * 60)
    print()

    # Collect all links from all pages
    all_links: Dict[str, Set[str]] = defaultdict(set)  # link -> set of source pages
    broken_links: List[Dict] = []
    double_path_links: List[Dict] = []
    checked_urls: Dict[str, Tuple[int, str]] = {}  # url -> (status, final_url)

    print("Scanning pages for links...")
    print("-" * 40)

    for page_path in PAGES_TO_AUDIT:
        page_url = BASE_URL + page_path
        print(f"Scanning: {page_path}")

        html = fetch_page(page_url)
        if not html:
            print(f"  WARNING: Could not fetch page")
            continue

        # Extract links
        parser = LinkExtractor()
        parser.feed(html)

        for link in parser.links:
            normalized = normalize_link(link, page_url)
            if normalized and is_internal_link(normalized):
                all_links[normalized].add(page_path)

                # Check for double path issues
                if detect_double_path(normalized):
                    double_path_links.append({
                        'source': page_path,
                        'link': normalized,
                        'original': link,
                    })

    print()
    print(f"Found {len(all_links)} unique internal links")
    print()

    # Check all unique links
    print("Checking link status...")
    print("-" * 40)

    for url in sorted(all_links.keys()):
        if url in checked_urls:
            continue

        status, final_url = check_url_status(url)
        checked_urls[url] = (status, final_url)

        status_icon = "OK" if status == 200 else f"FAIL:{status}"

        if status not in (200, 301, 302, 303, 307, 308):
            print(f"  [{status_icon}] {url}")
            for source in all_links[url]:
                broken_links.append({
                    'source': source,
                    'link': url,
                    'status': status,
                })

    # Generate report
    print()
    print("=" * 60)
    print("AUDIT REPORT")
    print("=" * 60)
    print()

    # Summary
    print("SUMMARY")
    print("-" * 40)
    print(f"Pages audited: {len(PAGES_TO_AUDIT)}")
    print(f"Unique internal links found: {len(all_links)}")
    print(f"Broken links (4xx/5xx): {len(broken_links)}")
    print(f"Double-path links: {len(double_path_links)}")
    print()

    # Broken links detail
    if broken_links:
        print("BROKEN LINKS")
        print("-" * 40)
        for item in broken_links:
            print(f"Source: {item['source']}")
            print(f"  Link: {item['link']}")
            print(f"  Status: {item['status']}")
            print()
    else:
        print("No broken internal links found!")
        print()

    # Double path issues
    if double_path_links:
        print("DOUBLE-PATH LINKS (need source fix)")
        print("-" * 40)
        for item in double_path_links:
            print(f"Source: {item['source']}")
            print(f"  Original href: {item['original']}")
            print(f"  Resolved to: {item['link']}")
            print()
    else:
        print("No double-path links found!")
        print()

    # Top offenders
    if broken_links:
        print("TOP OFFENDERS (pages with most broken links)")
        print("-" * 40)
        offenders = defaultdict(int)
        for item in broken_links:
            offenders[item['source']] += 1
        for source, count in sorted(offenders.items(), key=lambda x: -x[1])[:10]:
            print(f"  {count} broken: {source}")
        print()

    # Return exit code
    total_issues = len(broken_links) + len(double_path_links)
    if total_issues > 0:
        print(f"AUDIT FAILED: {total_issues} issues found")
        return 1
    else:
        print("AUDIT PASSED: No issues found")
        return 0


if __name__ == "__main__":
    sys.exit(main())
