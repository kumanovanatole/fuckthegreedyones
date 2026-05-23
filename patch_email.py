#!/usr/bin/env python3
"""Replace contact emails with the unified Luna Jets inbox."""

from __future__ import annotations

import re
from pathlib import Path

SITE = Path(__file__).parent / "site/www.lunajets.com"
NEW_EMAIL = "luna-jets@luna-jets.ch"

LUNAJETS_EMAIL_RE = re.compile(r"[a-zA-Z0-9._+-]+@lunajets\.com")
SALES_CH_RE = re.compile(r"sales@luna-jets\.ch", re.I)


def main() -> None:
    changed = 0
    replacements = 0
    for path in SITE.rglob("*.html"):
        html = path.read_text(encoding="utf-8", errors="replace")
        new_html, n1 = LUNAJETS_EMAIL_RE.subn(NEW_EMAIL, html)
        new_html, n2 = SALES_CH_RE.subn(NEW_EMAIL, new_html)
        n = n1 + n2
        if n:
            path.write_text(new_html, encoding="utf-8")
            changed += 1
            replacements += n
    print(f"Patched {changed} HTML files ({replacements} replacements -> {NEW_EMAIL})")


if __name__ == "__main__":
    main()
