#!/usr/bin/env python3
"""Point all WhatsApp links to a fixed international number."""

from __future__ import annotations

import re
from pathlib import Path

SITE = Path(__file__).parent / "site"

OLD_PHONE = "34628329945"
NEW_PHONE = "359894314827"  # +359 89 431 48 27

API_FETCH_RE = re.compile(
    r'try\{let r=await fetch\("https://www\.members\.lunajets\.com/api/manager"\);'
    r"if\(!r\.ok\)throw Error\(`HTTP error! status: \$\{r\.status\}`\);"
    r"let o=await r\.json\(\),s=o\.number;if\(s\)\{"
    r"let i=`https://api\.whatsapp\.com/send\?phone=\$\{s\}&text=\$\{n\}`;"
    r'e\.href=i,e\.setAttribute\("target","_blank"\),e\.setAttribute\("rel","noopener noreferrer"\)\}'
    r'\}catch\(C\)\{console\.error\("Failed to load the dynamic WhatsApp number:",C\)\}'
)

FIXED_LINK = (
    f'try{{let s="{NEW_PHONE}",i=`https://api.whatsapp.com/send?phone=${{s}}&text=${{n}}`;'
    'e.href=i,e.setAttribute("target","_blank"),e.setAttribute("rel","noopener noreferrer")}'
    'catch(C){console.error("Failed to set WhatsApp link:",C)}'
)


def patch_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")
    new_html = html.replace(OLD_PHONE, NEW_PHONE)
    new_html, api_n = API_FETCH_RE.subn(FIXED_LINK, new_html)
    if new_html == html:
        return False
    path.write_text(new_html, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for html in SITE.rglob("*.html"):
        if patch_file(html):
            changed += 1
    print(f"Patched {changed} HTML files (WhatsApp -> +359 89 431 48 27)")


if __name__ == "__main__":
    main()
