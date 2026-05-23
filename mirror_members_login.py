#!/usr/bin/env python3
"""Download and patch members.lunajets.com login pages for local hosting."""

from __future__ import annotations

import re
from pathlib import Path

import requests

BASE = "https://www.members.lunajets.com"
LOCALES = ("en", "de", "fr", "es", "it", "ru", "pl", "hu")
OUT = Path(__file__).parent / "site/www.lunajets.com/members"
NEW_PHONE = "359894314827"

SESSION = requests.Session()
SESSION.headers["User-Agent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

WHATSAPP_HREF_RE = re.compile(
    r'https://api\.whatsapp\.com/send\?phone=[^"\'<]+',
    re.I,
)
OLD_NUMBERS_RE = re.compile(
    r"447407092176|\+44\s*7407\s*092\s*176|\+447407092176",
    re.I,
)


def patch_html(html: str) -> str:
    html = WHATSAPP_HREF_RE.sub(
        f"https://wa.me/{NEW_PHONE}?text=Dear%20LunaJets%2C%0APlease%20get%20back%20to%20me%20regarding%20...%0A",
        html,
    )
    html = OLD_NUMBERS_RE.sub(NEW_PHONE, html)
    return html


def main() -> None:
    for loc in LOCALES:
        url = f"{BASE}/{loc}/login"
        dest = OUT / loc / "login" / "index.html"
        print(f"Fetching {url} ...")
        r = SESSION.get(url, timeout=60)
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(patch_html(r.text), encoding="utf-8")
        print(f"  -> {dest}")
    print("Done.")


if __name__ == "__main__":
    main()
