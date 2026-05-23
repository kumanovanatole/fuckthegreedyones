#!/usr/bin/env python3
"""Mirror lunajets.com from sitemap + asset harvesting."""

from __future__ import annotations

import os
import re
import threading
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import requests

BASE = "https://www.lunajets.com"
SITEMAP = f"{BASE}/sitemap.xml"
OUT = Path(__file__).resolve().parent / "site"

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
)

ALLOWED_HOSTS = {
    "www.lunajets.com",
    "lunajets.com",
    "cdn.prod.website-files.com",
    "media.lunajets.com",
    "code-components.website-files.com",
    "cdn.jsdelivr.net",
}

ASSET_RE = re.compile(
    r"""(?:src|href|srcset|poster)\s*=\s*["']([^"']+)["']"""
    r"""|url\(\s*['"]?([^'")\s]+)['"]?\s*\)""",
    re.I,
)

lock = threading.Lock()
downloaded: set[str] = set()
failed: list[tuple[str, str]] = []
pending_assets: set[str] = set()


def url_to_path(url: str) -> Path:
    p = urlparse(url)
    host = p.netloc
    path = p.path or "/"
    if path.endswith("/"):
        path = path + "index.html"
    elif not Path(path).suffix:
        path = path + "/index.html"
    return OUT / host / path.lstrip("/")


def save_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def normalize_url(url: str, base: str | None = None) -> str | None:
    if not url or url.startswith(("data:", "javascript:", "mailto:", "tel:", "#")):
        return None
    full = urljoin(base or BASE, url.strip())
    p = urlparse(full)
    if p.scheme not in ("http", "https"):
        return None
    if p.hostname not in ALLOWED_HOSTS:
        return None
    return urlunparse((p.scheme, p.hostname, p.path or "/", "", "", ""))


def harvest_assets(html: str, page_url: str) -> set[str]:
    found: set[str] = set()
    for m in ASSET_RE.finditer(html):
        raw = m.group(1) or m.group(2)
        if not raw:
            continue
        for part in raw.split(","):
            part = part.strip().split()[0] if " " in part.strip() else part.strip()
            u = normalize_url(part, page_url)
            if u:
                found.add(u)
    return found


def download_one(url: str) -> str:
    with lock:
        if url in downloaded:
            return "skip"
        downloaded.add(url)

    try:
        r = SESSION.get(url, timeout=90, allow_redirects=True)
        r.raise_for_status()
        path = url_to_path(r.url)
        save_bytes(path, r.content)

        ctype = (r.headers.get("content-type") or "").lower()
        if "html" in ctype or path.suffix == ".html":
            text = r.content.decode("utf-8", errors="replace")
            assets = harvest_assets(text, r.url)
            with lock:
                pending_assets.update(assets - downloaded)
        return "ok"
    except Exception as e:
        with lock:
            failed.append((url, str(e)))
        return "fail"


def load_sitemap_urls() -> list[str]:
    print(f"Fetching sitemap {SITEMAP}...")
    r = SESSION.get(SITEMAP, timeout=120)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls: list[str] = []
    for loc in root.findall(".//sm:loc", ns):
        if loc.text:
            u = normalize_url(loc.text.strip())
            if u:
                urls.append(u)
    return sorted(set(urls))


def run_pool(urls: list[str], workers: int, label: str) -> None:
    if not urls:
        return
    done = 0
    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(download_one, u) for u in urls]
        for fut in as_completed(futures):
            done += 1
            if done % 500 == 0:
                print(f"  [{label}] {done}/{len(urls)} ({time.time() - start:.0f}s)")
            fut.result()
    print(f"  [{label}] done {len(urls)} in {time.time() - start:.0f}s")


def main() -> None:
    workers = int(os.environ.get("MIRROR_WORKERS", "32"))
    pages = load_sitemap_urls()
    print(f"Sitemap: {len(pages)} pages")

    run_pool(pages, workers, "pages")

    asset_round = 0
    while pending_assets:
        asset_round += 1
        with lock:
            batch = sorted(pending_assets - downloaded)
            pending_assets.clear()
        print(f"Asset round {asset_round}: {len(batch)} URLs")
        run_pool(batch, workers, f"assets-{asset_round}")

    print(f"Unique downloads: {len(downloaded)}")
    print(f"Failed: {len(failed)}")
    if failed[:10]:
        for u, e in failed[:10]:
            print(f"  FAIL {u}: {e}")


if __name__ == "__main__":
    main()
