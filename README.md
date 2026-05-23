# Luna Jets web (rebrand)

Static site for **https://luna-jets.ch** (~11k pages, 8 locales). Built from the Webflow export/mirror workflow.

## Primary domain

- **Production:** `luna-jets.ch` (canonical, sitemap, hreflang)
- **Forward only:** `lunajets.ch` → 301 to `luna-jets.ch` (configure in DNS/Vercel)
- **Contact:** `luna-jets@luna-jets.ch` · WhatsApp +359 89 431 48 27

## After re-mirroring from lunajets.com

```bash
pip3 install -r requirements.txt
python3 mirror.py
python3 patch_whatsapp.py
python3 patch_email.py
python3 patch_seo.py
python3 patch_members_links.py
python3 mirror_members_login.py
python3 generate_sitemap.py
```

## Deploy (Vercel)

- `outputDirectory`: `site/www.lunajets.com`
- Attach custom domain **luna-jets.ch**
- Submit `https://luna-jets.ch/sitemap.xml` in Google Search Console

## Contents

- `site/www.lunajets.com/` — HTML + `robots.txt` + `sitemap.xml`
- `mirror.py` — refresh pages from live sitemap
- `patch_*.py` — contact, SEO domain, WhatsApp, members login
