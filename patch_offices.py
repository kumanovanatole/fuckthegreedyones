#!/usr/bin/env python3
"""Replace office phone numbers with Contact us mailto buttons."""

from __future__ import annotations

import re
from pathlib import Path

SITE = Path(__file__).parent / "site/www.lunajets.com"
MAILTO = "mailto:charter@luna-jets.ch"

LOCALE_LABELS = {
    "en": "Contact us",
    "de": "Kontaktieren Sie uns",
    "fr": "Contactez-nous",
    "es": "Contáctenos",
    "it": "Contattaci",
    "ru": "Связаться с нами",
    "pl": "Kontakt",
    "hu": "Kapcsolat",
}

PHONE_WRAPPER_RE = re.compile(
    r'<div class="location_number_wrapper"><div class="icon-embed-xxxsmall w-embed"><svg.*?</svg></div>'
    r'<a href="tel:[^"]*" class="phone-footer">[^<]*</a></div>',
    re.DOTALL,
)

# JSON-LD telephone lines in office blocks
TELEPHONE_JSON_RE = re.compile(r'\s*"telephone":\s*"[^"]*",?\n?', re.MULTILINE)


def locale_from_path(path: Path) -> str:
    parts = path.parts
    for loc in LOCALE_LABELS:
        if loc in parts:
            return loc
    return "en"


def contact_button(label: str) -> str:
    return (
        f'<div class="location_number_wrapper">'
        f'<a href="{MAILTO}" class="button is-secondary is-stroke w-inline-block lj-office-contact">'
        f"<div>{label}</div></a></div>"
    )


def patch_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")
    if "phone-footer" not in html and "location_number_wrapper" not in html:
        return False

    label = LOCALE_LABELS.get(locale_from_path(path), "Contact us")
    new_html, n = PHONE_WRAPPER_RE.subn(contact_button(label), html)
    if n == 0 and "phone-footer" not in html:
        return False

    # Remove telephone from JSON-LD in footer locations section only
    if "section_locations" in new_html:
        loc_start = new_html.find("section_locations")
        loc_end = new_html.find("</footer>", loc_start)
        if loc_end == -1:
            loc_end = len(new_html)
        chunk = new_html[loc_start:loc_end]
        chunk = TELEPHONE_JSON_RE.sub("", chunk)
        new_html = new_html[:loc_start] + chunk + new_html[loc_end:]

    # Update main "Contact us" office card to mailto
    new_html = re.sub(
        r'(<div id="lj_locations_contact"[^>]*><a[^>]*href=")[^"]*(" class="location_item contact)',
        rf'\1{MAILTO}\2',
        new_html,
        count=1,
    )

    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for html in SITE.rglob("*.html"):
        if patch_file(html):
            changed += 1
    print(f"Patched {changed} HTML files")


if __name__ == "__main__":
    main()
