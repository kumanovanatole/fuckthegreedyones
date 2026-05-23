#!/usr/bin/env python3
"""Point all WhatsApp links to a fixed number and open app/web on click."""

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

LEGACY_FIXED_RE = re.compile(
    r'try\{let s="' + NEW_PHONE + r'",i=`https://api\.whatsapp\.com/send\?phone=\$\{s\}&text=\$\{n\}`;'
    r'e\.href=i,e\.setAttribute\("target","_blank"\),e\.setAttribute\("rel","noopener noreferrer"\)\}'
    r'catch\(C\)\{console\.error\("Failed to set WhatsApp link:",C\)\}'
)

# Mobile: whatsapp:// (app). Desktop: web.whatsapp.com. Fallback: wa.me.
OPEN_WHATSAPP_JS = (
    f'try{{let s="{NEW_PHONE}",m=/android|iphone|ipad|ipod|mobile/i.test(navigator.userAgent),'
    f"d=`https://web.whatsapp.com/send?phone=${{s}}&text=${{n}}`,"
    f"a=`whatsapp://send?phone=${{s}}&text=${{n}}`,w=`https://wa.me/${{s}}?text=${{n}}`;"
    f"e.href=w,e.removeAttribute(\"target\"),e.addEventListener(\"click\",function(ev){{"
    f"ev.preventDefault();if(m){{location.href=a;setTimeout(function(){{location.href=w}},900)}}"
    f'else{{var o=window.open(d,"_blank","noopener,noreferrer");'
    f'o||window.open(w,"_blank","noopener,noreferrer")}}}})'
    f'}}catch(C){{console.error("Failed to set WhatsApp link:",C)}}'
)

API_HREF_RE = re.compile(
    rf"https://api\.whatsapp\.com/send\?phone=(?:{OLD_PHONE}|{NEW_PHONE})&amp;text="
)


def patch_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")
    new_html = html.replace(OLD_PHONE, NEW_PHONE)
    new_html = API_HREF_RE.sub(f"https://wa.me/{NEW_PHONE}?text=", new_html)
    new_html, _ = API_FETCH_RE.subn(OPEN_WHATSAPP_JS, new_html)
    new_html, _ = LEGACY_FIXED_RE.subn(OPEN_WHATSAPP_JS, new_html)
    if new_html == html:
        return False
    path.write_text(new_html, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for html in SITE.rglob("*.html"):
        if patch_file(html):
            changed += 1
    print(f"Patched {changed} HTML files (WhatsApp -> +359 89 431 48 27, app/web open)")


if __name__ == "__main__":
    main()
