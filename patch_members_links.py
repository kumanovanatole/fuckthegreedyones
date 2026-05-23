#!/usr/bin/env python3
"""Point members portal links to the mirrored /members path on this deployment."""

from __future__ import annotations

from pathlib import Path

SITE = Path(__file__).parent / "site/www.lunajets.com"
OLD = "https://www.members.lunajets.com"
NEW = "/members"


def main() -> None:
    changed = 0
    for path in SITE.rglob("*.html"):
        try:
            if path.relative_to(SITE).parts[0] == "members":
                continue
        except ValueError:
            pass
        html = path.read_text(encoding="utf-8", errors="replace")
        if OLD not in html:
            continue
        path.write_text(html.replace(OLD, NEW), encoding="utf-8")
        changed += 1
    print(f"Patched {changed} HTML files (members links -> {NEW})")


if __name__ == "__main__":
    main()
