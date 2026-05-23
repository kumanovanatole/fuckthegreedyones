#!/usr/bin/env python3
"""Point SEO metadata to luna-jets.ch (primary domain for the rebrand)."""

from __future__ import annotations

from pathlib import Path

SITE = Path(__file__).parent / "site/www.lunajets.com"
PRIMARY = "https://luna-jets.ch"

# Order: longer / more specific first.
REPLACEMENTS = (
    ("https://www.lunajets.com", PRIMARY),
    ("http://www.lunajets.com", PRIMARY),
    ("https://lunajets.com", PRIMARY),
    ("http://lunajets.com", PRIMARY),
    ('"www.lunajets.com"', '"luna-jets.ch"'),
    ('data-wf-domain="www.lunajets.com"', 'data-wf-domain="luna-jets.ch"'),
)


def main() -> None:
    changed = 0
    total = 0
    for path in SITE.rglob("*.html"):
        html = path.read_text(encoding="utf-8", errors="replace")
        new_html = html
        file_n = 0
        for old, new in REPLACEMENTS:
            c = new_html.count(old)
            if c:
                new_html = new_html.replace(old, new)
                file_n += c
        if file_n:
            path.write_text(new_html, encoding="utf-8")
            changed += 1
            total += file_n
    print(f"Patched {changed} HTML files ({total} replacements -> {PRIMARY})")


if __name__ == "__main__":
    main()
