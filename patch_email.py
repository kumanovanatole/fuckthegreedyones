#!/usr/bin/env python3
"""Replace LunaJets contact emails with a single sales address."""

from __future__ import annotations

import re
from pathlib import Path

SITE = Path(__file__).parent / "site/www.lunajets.com"
NEW_EMAIL = "sales@luna-jets.ch"

# Only @lunajets.com addresses (avoids false positives like jquery@4.0.0 in asset paths).
LUNAJETS_EMAIL_RE = re.compile(r"[a-zA-Z0-9._+-]+@lunajets\.com")


def main() -> None:
    changed = 0
    replacements = 0
    for path in SITE.rglob("*.html"):
        before = path.read_text(encoding="utf-8", errors="replace")
        new_html, n = LUNAJETS_EMAIL_RE.subn(NEW_EMAIL, before)
        if n:
            path.write_text(new_html, encoding="utf-8")
            changed += 1
            replacements += n
    print(f"Patched {changed} HTML files ({replacements} replacements -> {NEW_EMAIL})")


if __name__ == "__main__":
    main()
