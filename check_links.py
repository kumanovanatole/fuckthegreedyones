#!/usr/bin/env python3
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

base = Path(__file__).parent / "site/www.lunajets.com"
link_re = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.I)
found: set[str] = set()

for html in base.rglob("index.html"):
    text = html.read_text(errors="replace")
    rel = html.relative_to(base)
    page_path = "/" + str(rel.parent).replace("\\", "/")
    if page_path.endswith("/."):
        page_path = "/"
    page_url = f"https://www.lunajets.com{page_path if page_path != '/' else ''}"
    for m in link_re.finditer(text):
        href = m.group(1)
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urljoin(page_url + "/", href)
        p = urlparse(full)
        if p.netloc in ("www.lunajets.com", "lunajets.com"):
            path = p.path.rstrip("/") or "/"
            found.add(path)

existing: set[str] = set()
for html in base.rglob("index.html"):
    rel = html.relative_to(base)
    if str(rel) == "index.html":
        existing.add("/")
    else:
        existing.add("/" + str(rel.parent).replace("\\", "/"))

missing = sorted(found - existing)
print(f"internal links: {len(found)}")
print(f"existing pages: {len(existing)}")
print(f"linked but missing: {len(missing)}")
for m in missing[:50]:
    print(m)
