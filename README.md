# LunaJets site mirror

Static 1:1 mirror of [lunajets.com](https://www.lunajets.com) recovered from the live Webflow site (sitemap + assets).

## Contents

- `site/` — mirrored HTML, CSS, JS, images (path mirrors `www.lunajets.com/...`)
- `mirror.py` — download script (re-run to refresh)

## Local preview

```bash
cd site/www.lunajets.com/en
python3 -m http.server 8080
```

Open http://localhost:8080

## Re-mirror

```bash
pip3 install -r requirements.txt
python3 mirror.py
```
