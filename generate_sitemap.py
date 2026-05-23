#!/usr/bin/env python3
"""Generate sitemap.xml for all mirrored pages on luna-jets.ch."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

SITE = Path(__file__).parent / "site/www.lunajets.com"
PRIMARY = "https://luna-jets.ch"
OUT = SITE / "sitemap.xml"

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ET.register_namespace("", NS)


def page_url(path: Path) -> str:
    rel = path.relative_to(SITE).as_posix()
    if rel == "index.html":
        return f"{PRIMARY}/"
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    return f"{PRIMARY}/{rel}"


def main() -> None:
    today = date.today().isoformat()
    urlset = ET.Element(f"{{{NS}}}urlset")

    pages = sorted(SITE.rglob("index.html"))
    for page in pages:
        url = ET.SubElement(urlset, f"{{{NS}}}url")
        loc = ET.SubElement(url, f"{{{NS}}}loc")
        loc.text = page_url(page)
        modified = ET.SubElement(url, f"{{{NS}}}lastmod")
        modified.text = today

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    tree.write(OUT, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {len(pages)} URLs to {OUT}")


if __name__ == "__main__":
    main()
